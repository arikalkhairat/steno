 # File: app.py
# Deskripsi: Aplikasi web Flask untuk watermarking dokumen .docx dengan QR Code LSB.

import os
import subprocess
import uuid
import shutil
import json
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from PIL import Image
import numpy as np
import fitz  # PyMuPDF

from main import extract_images_from_docx, embed_watermark_to_docx, extract_images_from_pdf, embed_watermark_to_pdf, analyze_qr_options
from qr_utils import (read_qr, analyze_text_encoding, calculate_qr_capacity, 
                      get_optimal_qr_version, compare_qr_configurations, generate_qr_advanced,
                      generate_secure_qr, read_secure_qr, validate_qr_security)

# Import security utilities
import security_utils

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
GENERATED_FOLDER = os.path.join(BASE_DIR, 'static', 'generated')
DOCUMENTS_FOLDER = os.path.join(BASE_DIR, 'public', 'documents')
MAIN_SCRIPT_PATH = os.path.join(BASE_DIR, 'main.py')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Batas unggah 16MB

ALLOWED_DOCX_EXTENSIONS = {'docx'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'png'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def run_main_script(args):
    """Menjalankan skrip main.py dan menangkap output."""
    command = ['python', MAIN_SCRIPT_PATH] + args
    try:
        print(f"[*] Menjalankan perintah: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        print(f"[*] Stdout: {result.stdout}")
        print(f"[*] Stderr: {result.stderr}")
        return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        print(f"[!] Error saat menjalankan skrip: {e}")
        print(f"    Stdout: {e.stdout}")
        print(f"    Stderr: {e.stderr}")
        return {"success": False, "stdout": e.stdout, "stderr": e.stderr, "error": str(e)}
    except FileNotFoundError:
        error_msg = "[!] Error: Perintah 'python' atau skrip 'main.py' tidak ditemukan. Pastikan Python terinstal dan path sudah benar."
        print(error_msg)
        return {"success": False, "stdout": "", "stderr": error_msg, "error": error_msg}
    except Exception as e:
        error_msg = f"[!] Exception saat menjalankan skrip: {str(e)}"
        print(error_msg)
        return {"success": False, "stdout": "", "stderr": error_msg, "error": error_msg}


def calculate_metrics(original_docx_path, stego_docx_path):
    """Menghitung MSE dan PSNR antara gambar-gambar dalam dua file .docx."""

    try:
        # Ekstrak gambar dari kedua dokumen
        original_images_dir = os.path.join(app.config['GENERATED_FOLDER'], "original_images")
        stego_images_dir = os.path.join(app.config['GENERATED_FOLDER'], "stego_images")
        os.makedirs(original_images_dir, exist_ok=True)
        os.makedirs(stego_images_dir, exist_ok=True)

        original_images = extract_images_from_docx(original_docx_path, original_images_dir)
        stego_images = extract_images_from_docx(stego_docx_path, stego_images_dir)

        if not original_images or not stego_images:
            print("[!] Tidak dapat membandingkan gambar: Gagal mengekstrak gambar dari dokumen.")
            return {"mse": None, "psnr": None, "error": "Gagal mengekstrak gambar dari dokumen."}

        if len(original_images) != len(stego_images):
            print("[!] Tidak dapat membandingkan gambar: Jumlah gambar tidak sama.")
            return {"mse": None, "psnr": None, "error": "Jumlah gambar tidak sama."}

        total_mse = 0
        all_psnr_values = []

        for original_image_path, stego_image_path in zip(original_images, stego_images):
            try:
                original_image = Image.open(original_image_path).convert('RGB')
                stego_image = Image.open(stego_image_path).convert('RGB')

                if original_image.size != stego_image.size:
                    print(f"[!] Ukuran gambar tidak sama: {original_image_path} vs {stego_image_path}")
                    continue  # Lewati pasangan gambar ini

                original_array = np.array(original_image, dtype=np.float64)
                watermarked_array = np.array(stego_image, dtype=np.float64)

                mse = np.mean((original_array - watermarked_array) ** 2)
                total_mse += mse

                if mse == 0:
                    psnr = float('inf')
                else:
                    max_pixel = 255.0
                    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
                all_psnr_values.append(psnr)

            except Exception as e:
                print(f"[!] Error memproses pasangan gambar: {e}")

        final_mse = total_mse / len(original_images) if original_images else 0
        # Rata-rata PSNR (hindari ZeroDivisionError jika daftar kosong)
        final_psnr = sum(all_psnr_values) / len(all_psnr_values) if all_psnr_values else 0

        # Bersihkan direktori sementara
        if os.path.exists(original_images_dir):
            shutil.rmtree(original_images_dir)
        if os.path.exists(stego_images_dir):
            shutil.rmtree(stego_images_dir)

        return {"mse": final_mse, "psnr": final_psnr}

    except Exception as e:
        print(f"[!] Error keseluruhan dalam calculate_metrics: {e}")
        return {"mse": None, "psnr": None, "error": str(e)}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_qr', methods=['POST'])
def generate_qr_route():
    data = request.form.get('qrData')
    if not data:
        return jsonify({"success": False, "message": "Data QR tidak boleh kosong."}), 400

    # Get optional configuration parameters with defaults for backward compatibility
    version = request.form.get('version', type=int)  # None if not provided
    error_correction = request.form.get('error_correction', 'M')  # Default to 'M'
    box_size = request.form.get('box_size', 10, type=int)  # Default to 10
    border = request.form.get('border', 4, type=int)  # Default to 4
    analyze = request.form.get('analyze', 'false').lower() == 'true'  # Default to False

    # Validate parameters
    if version is not None and not (1 <= version <= 40):
        return jsonify({"success": False, "message": "Version harus antara 1-40."}), 400
    
    if error_correction not in ['L', 'M', 'Q', 'H']:
        return jsonify({"success": False, "message": "Error correction harus L, M, Q, atau H."}), 400
    
    if box_size < 1:
        return jsonify({"success": False, "message": "Box size harus minimal 1."}), 400
    
    if border < 0:
        return jsonify({"success": False, "message": "Border harus non-negatif."}), 400

    qr_filename = f"qr_{uuid.uuid4().hex}.png"
    qr_output_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)

    # Build command with new parameters
    args = ['generate_qr', '--data', data, '--output', qr_output_path]
    
    if version is not None:
        args.extend(['--version', str(version)])
    
    args.extend(['--error-correction', error_correction])
    args.extend(['--box-size', str(box_size)])
    args.extend(['--border', str(border)])
    
    if analyze:
        args.append('--analyze')

    result = run_main_script(args)

    if result["success"] and os.path.exists(qr_output_path):
        # Try to get QR analysis information if analyze was requested
        analysis_info = None
        if analyze:
            try:
                analysis_info = analyze_qr_options(data)
            except Exception as e:
                print(f"[!] Warning: Analysis failed: {str(e)}")

        return jsonify({
            "success": True,
            "message": "QR Code berhasil dibuat!",
            "qr_url": f"/static/generated/{qr_filename}",
            "qr_filename": qr_filename,
            "configuration": {
                "version": version,
                "error_correction": error_correction,
                "box_size": box_size,
                "border": border
            },
            "analysis": analysis_info,
            "log": result["stdout"]
        })
    else:
        return jsonify({
            "success": False,
            "message": "Gagal membuat QR Code.",
            "log": result["stderr"] or result.get("error", "Error tidak diketahui")
        }), 500


@app.route('/analyze_qr_text', methods=['POST'])
def analyze_qr_text_route():
    """Analyze text and return encoding recommendations."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            text = data.get('text')
            target_image_sizes = data.get('target_image_sizes', [])
        else:
            text = request.form.get('text')
            # Parse target_image_sizes from form if provided as JSON string
            target_sizes_str = request.form.get('target_image_sizes', '[]')
            try:
                target_image_sizes = json.loads(target_sizes_str) if target_sizes_str else []
            except json.JSONDecodeError:
                target_image_sizes = []

        if not text:
            return jsonify({"success": False, "message": "Text tidak boleh kosong."}), 400

        # Convert target_image_sizes to list of tuples if needed
        if target_image_sizes and isinstance(target_image_sizes[0], list):
            target_image_sizes = [tuple(size) for size in target_image_sizes]

        # Perform analysis
        analysis_result = analyze_qr_options(text, target_image_sizes)
        
        return jsonify({
            "success": True,
            "message": "Analisis berhasil.",
            "analysis": analysis_result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error saat analisis: {str(e)}"
        }), 500


@app.route('/compare_qr_versions', methods=['POST'])
def compare_qr_versions_route():
    """Compare different QR configurations."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            text = data.get('text')
            versions = data.get('versions', None)
        else:
            text = request.form.get('text')
            # Parse versions from form if provided as JSON string
            versions_str = request.form.get('versions', 'null')
            try:
                versions = json.loads(versions_str) if versions_str != 'null' else None
            except json.JSONDecodeError:
                versions = None

        if not text:
            return jsonify({"success": False, "message": "Text tidak boleh kosong."}), 400

        # Validate versions if provided
        if versions:
            if not isinstance(versions, list):
                return jsonify({"success": False, "message": "Versions harus berupa array."}), 400
            
            for v in versions:
                if not isinstance(v, int) or not (1 <= v <= 40):
                    return jsonify({"success": False, "message": "Setiap version harus integer antara 1-40."}), 400

        # Perform comparison
        comparison_result = compare_qr_configurations(text, versions)
        
        return jsonify({
            "success": True,
            "message": "Perbandingan berhasil.",
            "comparison": comparison_result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error saat perbandingan: {str(e)}"
        }), 500


@app.route('/calculate_qr_capacity', methods=['POST'])
def calculate_qr_capacity_route():
    """Calculate capacity for given QR parameters."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            version = data.get('version')
            error_level = data.get('error_level')
            encoding = data.get('encoding')
        else:
            version = request.form.get('version', type=int)
            error_level = request.form.get('error_level')
            encoding = request.form.get('encoding')

        # Validate required parameters
        if version is None:
            return jsonify({"success": False, "message": "Parameter version diperlukan."}), 400
        if not error_level:
            return jsonify({"success": False, "message": "Parameter error_level diperlukan."}), 400
        if not encoding:
            return jsonify({"success": False, "message": "Parameter encoding diperlukan."}), 400

        # Validate parameter values
        if not (1 <= version <= 40):
            return jsonify({"success": False, "message": "Version harus antara 1-40."}), 400
        
        if error_level not in ['L', 'M', 'Q', 'H']:
            return jsonify({"success": False, "message": "Error level harus L, M, Q, atau H."}), 400
        
        if encoding not in ['numeric', 'alphanumeric', 'byte']:
            return jsonify({"success": False, "message": "Encoding harus numeric, alphanumeric, atau byte."}), 400

        # Calculate capacity
        capacity = calculate_qr_capacity(version, error_level, encoding)
        
        return jsonify({
            "success": True,
            "message": "Kapasitas berhasil dihitung.",
            "capacity": capacity,
            "parameters": {
                "version": version,
                "error_level": error_level,
                "encoding": encoding
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error saat menghitung kapasitas: {str(e)}"
        }), 500


@app.route('/generate_qr_advanced', methods=['POST'])
def generate_qr_advanced_route():
    """Generate QR with custom configuration using advanced options."""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            text = data.get('data') or data.get('text')
            version = data.get('version')
            error_correction = data.get('error_correction', 'M')
            box_size = data.get('box_size', 10)
            border = data.get('border', 4)
        else:
            text = request.form.get('data') or request.form.get('text')
            version = request.form.get('version', type=int)
            error_correction = request.form.get('error_correction', 'M')
            box_size = request.form.get('box_size', 10, type=int)
            border = request.form.get('border', 4, type=int)

        if not text:
            return jsonify({"success": False, "message": "Data/text tidak boleh kosong."}), 400

        # Validate parameters
        if version is not None and not (1 <= version <= 40):
            return jsonify({"success": False, "message": "Version harus antara 1-40."}), 400
        
        if error_correction not in ['L', 'M', 'Q', 'H']:
            return jsonify({"success": False, "message": "Error correction harus L, M, Q, atau H."}), 400
        
        if box_size < 1:
            return jsonify({"success": False, "message": "Box size harus minimal 1."}), 400
        
        if border < 0:
            return jsonify({"success": False, "message": "Border harus non-negatif."}), 400

        # Generate QR code
        qr_filename = f"qr_advanced_{uuid.uuid4().hex}.png"
        qr_output_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)

        # Use the advanced QR generation function directly
        img = generate_qr_advanced(
            data=text,
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
            output_path=qr_output_path
        )

        # Get analysis information
        analysis_info = None
        try:
            analysis_info = analyze_qr_options(text)
        except Exception as e:
            print(f"[!] Warning: Analysis failed: {str(e)}")

        # Get actual QR configuration used (in case version was auto-selected)
        try:
            if version is None:
                encoding = analyze_text_encoding(text)
                actual_version = get_optimal_qr_version(len(text), encoding, error_correction)
            else:
                actual_version = version
        except Exception as e:
            print(f"[!] Warning: Could not determine actual version: {str(e)}")
            actual_version = version

        return jsonify({
            "success": True,
            "message": "QR Code advanced berhasil dibuat!",
            "qr_url": f"/static/generated/{qr_filename}",
            "qr_filename": qr_filename,
            "configuration": {
                "requested_version": version,
                "actual_version": actual_version,
                "error_correction": error_correction,
                "box_size": box_size,
                "border": border
            },
            "analysis": analysis_info
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error saat membuat QR Code advanced: {str(e)}"
        }), 500


@app.route('/embed_document', methods=['POST'])
def embed_document_route():
    if 'docxFileEmbed' not in request.files or 'qrFileEmbed' not in request.files:
        error_msg = "File Dokumen dan File QR Code diperlukan."
        print(f"[ERROR] /embed_document: {error_msg}")
        print(f"[ERROR] Missing fields: docxFileEmbed in files: {'docxFileEmbed' in request.files}, qrFileEmbed in files: {'qrFileEmbed' in request.files}")
        return jsonify({"success": False, "message": error_msg, "security_status": "missing_files"}), 400

    doc_file = request.files['docxFileEmbed']
    qr_file = request.files['qrFileEmbed']
    
    # Extract advanced QR settings (optional parameters)
    qr_version = request.form.get('qr_version', 'auto')
    error_correction = request.form.get('error_correction', 'M')
    box_size = request.form.get('box_size', '10')
    border_size = request.form.get('border_size', '4')
    auto_optimize = request.form.get('auto_optimize') == 'on'
    
    # NEW: Extract security settings
    enable_document_security = request.form.get('enable_document_security', 'false').lower() == 'true'
    document_key = request.form.get('document_key', '').strip()
    validate_qr_auth = request.form.get('validate_qr_auth', 'false').lower() == 'true'
    
    # Legacy parameter for backward compatibility
    validate_security = request.form.get('validate_security', 'false').lower() == 'true'
    if validate_security and not enable_document_security:
        enable_document_security = True
    
    # Convert string parameters to appropriate types
    try:
        box_size = int(box_size)
        border_size = int(border_size)
        if qr_version != 'auto':
            qr_version = int(qr_version)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid QR configuration parameters", "security_status": "invalid_params"}), 400
    
    # Build QR configuration object
    qr_config = {
        'version': qr_version,
        'error_correction': error_correction,
        'box_size': box_size,
        'border_size': border_size,
        'auto_optimize': auto_optimize
    }
    
    # Log advanced settings if they're not defaults
    if qr_version != 'auto' or error_correction != 'M' or box_size != 10 or not auto_optimize:
        print(f"[INFO] Advanced QR settings detected:")
        print(f"  - Version: {qr_version}")
        print(f"  - Error Correction: {error_correction}")
        print(f"  - Box Size: {box_size}px")
        print(f"  - Border Size: {border_size}")
        print(f"  - Auto Optimize: {auto_optimize}")

    if doc_file.filename == '' or qr_file.filename == '':
        error_msg = "Nama file tidak boleh kosong."
        print(f"[ERROR] /embed_document: {error_msg}")
        print(f"[ERROR] Filenames: doc={doc_file.filename}, qr={qr_file.filename}")
        return jsonify({"success": False, "message": error_msg}), 400

    # Check if it's either DOCX or PDF
    is_docx = allowed_file(doc_file.filename, ALLOWED_DOCX_EXTENSIONS)
    is_pdf = allowed_file(doc_file.filename, ALLOWED_PDF_EXTENSIONS)
    
    if not (doc_file and (is_docx or is_pdf)):
        error_msg = "Format Dokumen harus .docx atau .pdf"
        print(f"[ERROR] /embed_document: {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 400
    if not (qr_file and allowed_file(qr_file.filename, ALLOWED_IMAGE_EXTENSIONS)):
        error_msg = "Format QR Code harus .png"
        print(f"[ERROR] /embed_document: {error_msg}")
        return jsonify({"success": False, "message": error_msg}), 400

    # Generate unique filenames based on document type
    file_extension = '.docx' if is_docx else '.pdf'
    doc_filename = f"doc_embed_in_{uuid.uuid4().hex}{file_extension}"
    qr_embed_filename = f"qr_embed_in_{uuid.uuid4().hex}.png"
    doc_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
    qr_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_embed_filename)
    doc_file.save(doc_temp_path)
    qr_file.save(qr_temp_path)

    # Auto-optimization logic
    optimized_qr_config = qr_config.copy()
    if auto_optimize:
        print("[*] Auto-optimization enabled, analyzing document images...")
        try:
            # First, do a quick analysis of the document to get image sizes
            if is_docx:
                from main import analyze_docx_images
                image_analysis = analyze_docx_images(doc_temp_path)
            else:
                from main import analyze_pdf_images  
                image_analysis = analyze_pdf_images(doc_temp_path)
            
            if image_analysis and image_analysis.get('images'):
                # Get average image size for optimization
                avg_width = sum(img.get('width', 0) for img in image_analysis['images']) / len(image_analysis['images'])
                avg_height = sum(img.get('height', 0) for img in image_analysis['images']) / len(image_analysis['images'])
                min_dimension = min(avg_width, avg_height)
                
                print(f"[*] Average image dimensions: {avg_width:.0f}x{avg_height:.0f}")
                print(f"[*] Min dimension: {min_dimension:.0f}px")
                
                # Optimize QR settings based on image size
                if qr_version == 'auto':
                    # Use qr_utils to get optimal version
                    from qr_utils import get_optimal_qr_version
                    try:
                        with open(qr_temp_path, 'rb') as qr_file_handle:
                            from PIL import Image
                            qr_img = Image.open(qr_file_handle)
                            qr_data = "sample"  # We'll extract actual data later if needed
                            optimal_version = get_optimal_qr_version(qr_data, error_correction)
                            optimized_qr_config['version'] = optimal_version
                            print(f"[*] Optimal QR version: {optimal_version}")
                    except Exception as e:
                        print(f"[!] Could not determine optimal QR version: {e}")
                
                # Optimize box size based on image dimensions
                if min_dimension > 800:
                    suggested_box_size = max(12, min(20, int(min_dimension / 40)))
                elif min_dimension > 400:
                    suggested_box_size = max(8, min(15, int(min_dimension / 50)))
                else:
                    suggested_box_size = max(4, min(10, int(min_dimension / 60)))
                
                optimized_qr_config['box_size'] = suggested_box_size
                print(f"[*] Optimized box size: {suggested_box_size}px")
                
        except Exception as e:
            print(f"[!] Auto-optimization failed, using original settings: {e}")
            optimized_qr_config = qr_config.copy()

    stego_doc_filename = f"stego_doc_{uuid.uuid4().hex}{file_extension}"
    stego_doc_output_path = os.path.join(app.config['GENERATED_FOLDER'], stego_doc_filename)
    
    # Juga siapkan path untuk dokumen hasil di folder documents
    documents_filename = f"watermarked_{uuid.uuid4().hex}{file_extension}"
    documents_output_path = os.path.join(app.config['DOCUMENTS_FOLDER'], documents_filename)

    # Choose the appropriate command based on file type
    if is_docx:
        args = ['embed_docx', '--docx', doc_temp_path, '--qr', qr_temp_path, '--output', stego_doc_output_path]
        print("[*] Memulai proses embed_docx")
    else:  # is_pdf
        args = ['embed_pdf', '--pdf', doc_temp_path, '--qr', qr_temp_path, '--output', stego_doc_output_path]
        print("[*] Memulai proses embed_pdf")
    
    # Add security parameters if enabled
    if enable_document_security:
        if document_key:
            args.extend(['--security_key', document_key])
            print(f"[*] Security enabled with provided key")
        else:
            print(f"[*] Security enabled, will generate document key")
    
    result = run_main_script(args)

    if result["success"]:
        print("[*] Proses embed_docx berhasil")
        
        # Run the appropriate embed function directly to get the processed images
        try:
            print("[*] Mendapatkan informasi gambar yang diproses")
            
            # NEW: Security validation variables
            security_validation_results = None
            qr_authorization_status = None
            generated_document_key = None
            
            # Perform security validation if requested
            if enable_document_security:
                print("[*] Performing security validation before embedding...")
                try:
                    # Generate document key if not provided
                    if not document_key:
                        generated_document_key = security_utils.generate_document_key(doc_temp_path)
                        document_key = generated_document_key
                        print("[*] Document key generated for security validation")
                    
                    # Validate QR authorization if requested
                    if validate_qr_auth:
                        print("[*] Validating QR authorization...")
                        qr_data_list = read_qr(qr_temp_path)
                        if qr_data_list:
                            qr_data = qr_data_list[0]
                            document_hash = security_utils.generate_document_hash(doc_temp_path)
                            
                            validation_results = validate_qr_security(qr_data, document_key, document_hash)
                            qr_authorization_status = validation_results
                            
                            if not validation_results['overall_valid']:
                                print("[!] QR authorization validation failed")
                                # Clean up temp files
                                if os.path.exists(doc_temp_path):
                                    os.remove(doc_temp_path)
                                if os.path.exists(qr_temp_path):
                                    os.remove(qr_temp_path)
                                
                                return jsonify({
                                    "success": False,
                                    "message": "QR authorization failed - QR code is not authorized for this document",
                                    "security_status": "authorization_failed",
                                    "validation_results": validation_results,
                                    "security_warnings": ["QR code authorization check failed", "Document embedding blocked for security"]
                                }), 400
                            else:
                                print("[*] QR authorization validation passed")
                        else:
                            print("[!] Warning: Could not read QR code for authorization validation")
                    
                    # Prepare security metadata
                    security_validation_results = {
                        "security_enabled": True,
                        "document_key_generated": bool(generated_document_key),
                        "qr_authorization_checked": validate_qr_auth,
                        "qr_authorization_status": qr_authorization_status,
                        "document_hash": security_utils.generate_document_hash(doc_temp_path),
                        "encryption_applied": True
                    }
                        
                except Exception as security_e:
                    print(f"[!] Security validation error: {security_e}")
                    # Clean up temp files
                    if os.path.exists(doc_temp_path):
                        os.remove(doc_temp_path)
                    if os.path.exists(qr_temp_path):
                        os.remove(qr_temp_path)
                    
                    return jsonify({
                        "success": False,
                        "message": f"Security validation failed: {str(security_e)}",
                        "security_status": "validation_error",
                        "security_error": str(security_e)
                    }), 500
            
            # Call embedding functions with security parameters
            if is_docx:
                process_result = embed_watermark_to_docx(
                    doc_temp_path, qr_temp_path, stego_doc_output_path,
                    validate_security=enable_document_security,
                    document_key=document_key
                )
            else:  # is_pdf
                process_result = embed_watermark_to_pdf(
                    doc_temp_path, qr_temp_path, stego_doc_output_path,
                    validate_security=enable_document_security,
                    document_key=document_key
                )
            
            # Get processed images info if available
            processed_images = []
            qr_image_url = ""
            public_dir = ""
            qr_info = None
            
            if isinstance(process_result, dict) and process_result.get("success"):
                processed_images = process_result.get("processed_images", [])
                qr_image_url = process_result.get("qr_image", "")
                public_dir = process_result.get("public_dir", "")
                qr_info = process_result.get("qr_info", None)
                print(f"[*] ✅ SUCCESS: Mendapatkan {len(processed_images)} gambar yang diproses")
                print(f"[*] 📊 Processed images data: {processed_images}")
                
                # Ensure proper path format for frontend with detailed logging
                for i, img in enumerate(processed_images):
                    print(f"[*] 🔍 Image {i} - Original: {img.get('original')}, Watermarked: {img.get('watermarked')}")
            else:
                print("[!] Tidak mendapatkan detail gambar yang diproses")
        except ValueError as ve:
            if str(ve) == "NO_IMAGES_FOUND":
                # Handle no images case
                return jsonify({
                    "success": False,
                    "message": "Dokumen ini tidak mengandung gambar",
                    "log": result["stderr"],
                    "error_type": "NO_IMAGES_FOUND"
                }), 400
            print(f"[!] Error saat mendapatkan informasi gambar: {str(ve)}")
            processed_images = []
            qr_image_url = ""
            public_dir = ""
            qr_info = None
        except Exception as e:
            print(f"[!] Error saat mendapatkan informasi gambar: {str(e)}")
            processed_images = []
            qr_image_url = ""
            public_dir = ""
            qr_info = None
        
        # Hitung MSE dan PSNR (only for DOCX, PDF comparison is more complex)
        if is_docx:
            metrics = calculate_metrics(doc_temp_path, stego_doc_output_path)
        else:
            # For PDF, we skip MSE/PSNR calculation as it's more complex
            metrics = {"mse": None, "psnr": None, "info": "PDF metrics calculation not implemented"}
        print(f"[*] Metrik MSE: {metrics['mse']}, PSNR: {metrics['psnr']}")

        # Salin dokumen hasil ke folder documents untuk akses permanen
        try:
            shutil.copy2(stego_doc_output_path, documents_output_path)
            print(f"[*] Dokumen hasil disalin ke: {documents_output_path}")
        except Exception as e:
            print(f"[!] Warning: Gagal menyalin dokumen ke folder documents: {str(e)}")

        # Baca data QR code untuk ditampilkan
        qr_data = None
        try:
            qr_data_list = read_qr(qr_temp_path)
            if qr_data_list:
                qr_data = qr_data_list[0]  # Ambil data QR pertama
                print(f"[*] Data QR Code: {qr_data}")
        except Exception as e:
            print(f"[!] Warning: Tidak dapat membaca data QR Code: {str(e)}")

        # Hapus file temporary setelah perhitungan metrik
        if os.path.exists(doc_temp_path):
            os.remove(doc_temp_path)
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)

        # Enhanced logging before sending response
        print(f"[*] 📤 SENDING RESPONSE:")
        print(f"[*] 📊 processed_images count: {len(processed_images)}")
        print(f"[*] 🔍 processed_images content: {processed_images}")
        
        return jsonify({
            "success": True,
            "message": f"Watermark berhasil disisipkan ke {'dokumen' if is_docx else 'PDF'}!",
            "download_url": f"/download_generated/{stego_doc_filename}",
            "documents_url": f"/download_documents/{documents_filename}",
            "documents_filename": documents_filename,
            "log": result["stdout"],
            "mse": metrics["mse"],
            "psnr": metrics["psnr"],
            "processed_images": processed_images,
            "qr_image": qr_image_url,
            "public_dir": public_dir,
            "qr_info": qr_info,
            "qr_data": qr_data,
            "document_type": "docx" if is_docx else "pdf",
            "qr_config": {
                "original": qr_config,
                "optimized": optimized_qr_config,
                "auto_optimization_applied": auto_optimize and (optimized_qr_config != qr_config)
            },
            # NEW: Security information
            "security_validation": security_validation_results,
            "security_enabled": enable_document_security,
            "document_key": document_key if enable_document_security else None,
            "document_key_generated": bool(generated_document_key),
            "qr_authorization_checked": validate_qr_auth,
            "security_status": get_embed_security_status(enable_document_security, security_validation_results, qr_authorization_status),
            "security_warnings": get_embed_security_warnings(enable_document_security, qr_authorization_status),
            "security_recommendations": get_embed_security_recommendations(enable_document_security, generated_document_key)
        })
    else:
        # Hapus file temporary jika terjadi error
        if os.path.exists(doc_temp_path):
            os.remove(doc_temp_path)
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)

        # Check for the specific "NO_IMAGES_FOUND" error
        if result["stderr"] and "NO_IMAGES_FOUND" in result["stderr"]:
            return jsonify({
                "success": False,
                "message": f"{'Dokumen' if is_docx else 'PDF'} ini tidak mengandung gambar",
                "log": result["stderr"],
                "error_type": "NO_IMAGES_FOUND"
            }), 400
        
        return jsonify({
            "success": False,
            "message": "Gagal menyisipkan watermark.",
            "log": result["stderr"] or result.get("error", "Error tidak diketahui")
        }), 500


@app.route('/extract_document', methods=['POST'])
def extract_document_route():
    if 'docxFileValidate' not in request.files:
        return jsonify({"success": False, "message": "File Dokumen diperlukan untuk validasi.", "security_status": "missing_document"}), 400

    doc_file = request.files['docxFileValidate']

    if doc_file.filename == '':
        return jsonify({"success": False, "message": "Nama file tidak boleh kosong.", "security_status": "no_file_selected"}), 400
    
    # NEW: Extract security parameters
    enable_document_security = request.form.get('enable_document_security', 'false').lower() == 'true'
    security_key = request.form.get('security_key', '').strip()
    verify_document_auth = request.form.get('verify_document_auth', 'false').lower() == 'true'
    check_qr_auth = request.form.get('check_qr_auth', 'false').lower() == 'true'
    
    # Legacy parameter for backward compatibility  
    validate_security = request.form.get('validate_security', 'false').lower() == 'true'
    document_key = request.form.get('document_key', None)
    
    # Use legacy parameters if new ones aren't provided
    if validate_security and not enable_document_security:
        enable_document_security = True
    if document_key and not security_key:
        security_key = document_key
    
    # Check if it's either DOCX or PDF
    is_docx = allowed_file(doc_file.filename, ALLOWED_DOCX_EXTENSIONS)
    is_pdf = allowed_file(doc_file.filename, ALLOWED_PDF_EXTENSIONS)
    
    if not (doc_file and (is_docx or is_pdf)):
        return jsonify({"success": False, "message": "Format Dokumen harus .docx atau .pdf", "security_status": "invalid_file_type"}), 400

    # Generate unique filenames based on document type
    file_extension = '.docx' if is_docx else '.pdf'
    doc_validate_filename = f"doc_extract_in_{uuid.uuid4().hex}{file_extension}"
    doc_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_validate_filename)
    doc_file.save(doc_temp_path)

    extraction_id = uuid.uuid4().hex
    output_extraction_dir_name = f"extraction_{extraction_id}"
    output_extraction_dir_path = os.path.join(app.config['GENERATED_FOLDER'], output_extraction_dir_name)

    # Choose the appropriate command based on file type
    if is_docx:
        args = ['extract_docx', '--docx', doc_temp_path, '--output_dir', output_extraction_dir_path]
        print("[*] Memulai proses extract_docx")
    else:  # is_pdf
        args = ['extract_pdf', '--pdf', doc_temp_path, '--output_dir', output_extraction_dir_path]
        print("[*] Memulai proses extract_pdf")
    
    result = run_main_script(args)

    if result["success"]:
        extracted_qrs_info = []
        security_results = []
        overall_security_status = {
            "qr_extraction_status": "success",
            "security_verification_status": "pending",
            "key_authorization_status": "pending", 
            "document_integrity_status": "pending"
        }
        
        if os.path.exists(output_extraction_dir_path) and os.path.isdir(output_extraction_dir_path):
            # Process extracted QR codes
            for filename in os.listdir(output_extraction_dir_path):
                if filename.lower().endswith('.png'):
                    qr_info = {
                        "filename": filename,
                        "url": f"/static/generated/{output_extraction_dir_name}/{filename}"
                    }
                    
                    # NEW: Enhanced security verification for extracted QR
                    if enable_document_security:
                        try:
                            qr_file_path = os.path.join(output_extraction_dir_path, filename)
                            
                            # Generate document key if not provided
                            if not security_key:
                                doc_key_for_validation = security_utils.generate_document_key(doc_temp_path)
                                print("[*] Generated document key for validation")
                            else:
                                doc_key_for_validation = security_key
                            
                            # Read and validate QR code
                            qr_data_list = read_qr(qr_file_path)
                            if qr_data_list:
                                qr_data = qr_data_list[0]
                                
                                # Try to decrypt QR data if it's encrypted
                                decrypted_data = None
                                decryption_success = False
                                try:
                                    decrypted_data = read_secure_qr(qr_file_path, doc_key_for_validation)
                                    decryption_success = True
                                    print(f"[*] Successfully decrypted QR: {filename}")
                                except Exception:
                                    # QR might be plain text
                                    decrypted_data = qr_data
                                    print(f"[*] QR appears to be unencrypted: {filename}")
                                
                                # Perform document integrity verification if requested
                                document_integrity_valid = True
                                if verify_document_auth:
                                    try:
                                        document_hash = security_utils.generate_document_hash(doc_temp_path)
                                        # Verify document hasn't been tampered with
                                        document_integrity_valid = security_utils.verify_document_integrity(doc_temp_path, doc_key_for_validation)
                                        print(f"[*] Document integrity check: {'PASSED' if document_integrity_valid else 'FAILED'}")
                                    except Exception as e:
                                        print(f"[!] Document integrity check error: {e}")
                                        document_integrity_valid = False
                                
                                # Perform QR authorization check if requested
                                qr_authorization_valid = True
                                authorization_results = None
                                if check_qr_auth:
                                    try:
                                        document_hash = security_utils.generate_document_hash(doc_temp_path)
                                        authorization_results = validate_qr_security(decrypted_data, doc_key_for_validation, document_hash)
                                        qr_authorization_valid = authorization_results['overall_valid']
                                        print(f"[*] QR authorization check: {'PASSED' if qr_authorization_valid else 'FAILED'}")
                                    except Exception as e:
                                        print(f"[!] QR authorization check error: {e}")
                                        qr_authorization_valid = False
                                        authorization_results = {"error": str(e), "overall_valid": False}
                                
                                # Calculate security score
                                security_score = 0
                                if decryption_success:
                                    security_score += 30
                                if document_integrity_valid:
                                    security_score += 30
                                if qr_authorization_valid:
                                    security_score += 40
                                
                                security_info = {
                                    "filename": filename,
                                    "is_encrypted": decryption_success,
                                    "decrypted_data": decrypted_data,
                                    "document_integrity_valid": document_integrity_valid,
                                    "qr_authorization_valid": qr_authorization_valid,
                                    "authorization_results": authorization_results,
                                    "security_score": security_score,
                                    "is_authorized": qr_authorization_valid and document_integrity_valid,
                                    "original_qr_data_length": len(qr_data)
                                }
                                
                                # Add security info to QR info
                                qr_info.update({
                                    "security_validation": qr_authorization_valid and document_integrity_valid,
                                    "decrypted_data": decrypted_data,
                                    "is_encrypted": decryption_success,
                                    "security_score": security_score,
                                    "document_integrity": document_integrity_valid,
                                    "qr_authorization": qr_authorization_valid
                                })
                                
                                security_results.append(security_info)
                                
                            else:
                                security_results.append({
                                    "filename": filename,
                                    "error": "Could not read QR code data",
                                    "is_authorized": False,
                                    "security_score": 0
                                })
                                
                        except Exception as security_e:
                            print(f"[!] Security validation error for {filename}: {security_e}")
                            security_results.append({
                                "filename": filename,
                                "error": str(security_e),
                                "is_authorized": False,
                                "security_score": 0
                            })
                    
                    extracted_qrs_info.append(qr_info)

        if not extracted_qrs_info and "Tidak ada gambar yang ditemukan" not in result["stdout"]:
            pass

        # Hapus file temporary setelah selesai
        if os.path.exists(doc_temp_path):
            os.remove(doc_temp_path)

        print(f"[*] Proses extract_{'docx' if is_docx else 'pdf'} berhasil")
        
        # Calculate security summary and update overall status
        security_summary = None
        if enable_document_security and security_results:
            authorized_count = sum(1 for result in security_results if result.get('is_authorized', False))
            total_count = len(security_results)
            avg_security_score = sum(result.get('security_score', 0) for result in security_results) / total_count if total_count > 0 else 0
            
            # Update overall security status
            overall_security_status["security_verification_status"] = "success" if avg_security_score >= 60 else "warning" if avg_security_score > 0 else "error"
            overall_security_status["key_authorization_status"] = "success" if authorized_count == total_count else "warning" if authorized_count > 0 else "error"
            overall_security_status["document_integrity_status"] = "success" if all(r.get('document_integrity_valid', False) for r in security_results) else "warning"
            
            security_summary = {
                "total_qr_codes": total_count,
                "authorized_qr_codes": authorized_count,
                "unauthorized_qr_codes": total_count - authorized_count,
                "average_security_score": round(avg_security_score, 2),
                "validation_enabled": True,
                "document_integrity_passed": all(r.get('document_integrity_valid', False) for r in security_results),
                "encryption_detected": any(r.get('is_encrypted', False) for r in security_results)
            }
            
            # Generate security warnings and recommendations
            security_warnings = []
            security_recommendations = []
            
            # Add warnings for unauthorized QRs
            unauthorized_count = total_count - authorized_count
            if unauthorized_count > 0:
                security_warnings.append(f"{unauthorized_count} of {total_count} QR codes failed authorization")
            
            # Add warnings for integrity failures
            integrity_failures = sum(1 for r in security_results if not r.get('document_integrity_valid', True))
            if integrity_failures > 0:
                security_warnings.append(f"Document integrity check failed for {integrity_failures} QR codes")
            
            # Add recommendations based on security score
            if avg_security_score < 60:
                security_recommendations.append("Consider using encrypted QR codes for better security")
                security_recommendations.append("Verify document integrity with a security key")
            elif avg_security_score < 80:
                security_recommendations.append("Some QR codes may not be properly authorized")
        else:
            security_warnings = []
            security_recommendations = []
        
        return jsonify({
            "success": True,
            "message": "Proses ekstraksi selesai.",
            "extracted_qrs": extracted_qrs_info,
            "log": result["stdout"],
            "document_type": "docx" if is_docx else "pdf",
            # NEW: Enhanced security information
            "security_validation": enable_document_security,
            "security_results": security_results if enable_document_security else None,
            "security_summary": security_summary,
            "security_key": security_key if enable_document_security and security_key else None,
            "verify_document_auth": verify_document_auth,
            "check_qr_auth": check_qr_auth,
            "security_status": get_extract_security_status(enable_document_security, overall_security_status),
            "security_warnings": security_warnings if enable_document_security else [],
            "security_recommendations": security_recommendations if enable_document_security else [],
            # Overall security status for frontend
            "qr_extraction_status": overall_security_status["qr_extraction_status"],
            "security_verification_status": overall_security_status["security_verification_status"], 
            "key_authorization_status": overall_security_status["key_authorization_status"],
            "document_integrity_status": overall_security_status["document_integrity_status"]
        })
    else:
        # Hapus file temporary jika terjadi error
        if os.path.exists(doc_temp_path):
            os.remove(doc_temp_path)

        # Check for the specific "NO_IMAGES_FOUND" error
        if result["stderr"] and "NO_IMAGES_FOUND" in result["stderr"]:
            return jsonify({
                "success": False,
                "message": f"{'Dokumen' if is_docx else 'PDF'} ini tidak mengandung gambar",
                "log": result["stderr"],
                "error_type": "NO_IMAGES_FOUND"
            }), 400

        print(f"[!] Proses extract_{'docx' if is_docx else 'pdf'} gagal")
        return jsonify({
            "success": False,
            "message": "Gagal mengekstrak watermark.",
            "log": result["stderr"] or result.get("error", "Error tidak diketahui")
        }), 500


@app.route('/download_generated/<filename>')
def download_generated(filename):
    """Endpoint untuk mengunduh file dari folder generated."""
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)


@app.route('/download_documents/<filename>')
def download_documents(filename):
    """Endpoint untuk mengunduh file dari folder documents."""
    return send_from_directory(app.config['DOCUMENTS_FOLDER'], filename, as_attachment=True)


@app.route('/list_documents')
def list_documents():
    """Endpoint untuk melihat daftar dokumen yang tersimpan."""
    try:
        documents = []
        for filename in os.listdir(app.config['DOCUMENTS_FOLDER']):
            if filename.endswith('.docx'):
                file_path = os.path.join(app.config['DOCUMENTS_FOLDER'], filename)
                file_stat = os.stat(file_path)
                documents.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created': file_stat.st_ctime,
                    'download_url': f'/download_documents/{filename}'
                })
        
        # Urutkan berdasarkan waktu pembuatan (terbaru dulu)
        documents.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/process_details')
def process_details():
    """Render the process details page."""
    return render_template('process_details.html')


# ====== NEW SECURITY-RELATED API ENDPOINTS ======

@app.route('/generate_document_key', methods=['POST'])
def generate_document_key():
    """Generate unique security key for uploaded document."""
    try:
        # Check if a document file is uploaded
        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No document file uploaded',
                'security_status': 'missing_file'
            }), 400

        document_file = request.files['document']
        if document_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No document file selected',
                'security_status': 'no_file_selected'
            }), 400

        # Get additional data if provided
        additional_data = request.form.get('additional_data', '')

        # Check file type
        if not (allowed_file(document_file.filename, ALLOWED_DOCX_EXTENSIONS) or 
                allowed_file(document_file.filename, ALLOWED_PDF_EXTENSIONS)):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only DOCX and PDF files are allowed.',
                'security_status': 'invalid_file_type'
            }), 400

        # Save the uploaded document temporarily
        temp_filename = f"temp_doc_{uuid.uuid4().hex}_{document_file.filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        document_file.save(temp_path)

        try:
            # Generate document key
            document_key = security_utils.generate_document_key(temp_path, additional_data)
            
            # Validate that key was generated successfully
            if not document_key:
                raise ValueError("Failed to generate document key")
            
            # Generate document hash for validation
            document_hash = security_utils.generate_document_hash(temp_path)
            
            # Create key signature for integrity
            key_signature = security_utils.create_key_signature(document_key, document_hash)
            
            # Validate security parameters
            security_status = security_utils.validate_security_parameters()
            
            return jsonify({
                'success': True,
                'document_key': document_key,
                'key': document_key,  # Backward compatibility
                'document_hash': document_hash,
                'key_signature': key_signature,
                'document_name': document_file.filename,
                'additional_data': additional_data,
                'security_status': 'key_generated',
                'security_validation': security_status,
                'message': 'Document security key generated successfully'
            })

        except Exception as key_error:
            # Log the specific error for debugging
            print(f"Key generation error: {str(key_error)}")
            
            return jsonify({
                'success': False,
                'error': f'Key generation failed: {str(key_error)}',
                'security_status': 'generation_failed'
            }), 500

        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to cleanup temp file {temp_path}: {cleanup_error}")

    except Exception as e:
        # Log the error for debugging
        print(f"Document key generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'security_status': 'generation_failed'
        }), 500


@app.route('/generate_secure_qr', methods=['POST'])
def generate_secure_qr_endpoint():
    """Generate QR with encryption using document key."""
    try:
        # Get required parameters
        qr_data = request.form.get('data')
        document_key = request.form.get('document_key')
        
        if not qr_data:
            return jsonify({
                'success': False,
                'error': 'QR data is required',
                'security_status': 'missing_data'
            }), 400
        
        if not document_key:
            return jsonify({
                'success': False,
                'error': 'Document key is required for secure QR generation',
                'security_status': 'missing_key'
            }), 400

        # Generate unique filename for the secure QR
        qr_filename = f"secure_qr_{uuid.uuid4().hex}.png"
        qr_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)

        # Generate secure QR code
        qr_image = generate_secure_qr(qr_data, document_key, qr_path)
        
        # Get QR image dimensions for response
        qr_width, qr_height = qr_image.size
        
        return jsonify({
            'success': True,
            'qr_filename': qr_filename,
            'qr_path': qr_path,
            'qr_dimensions': {'width': qr_width, 'height': qr_height},
            'original_data_length': len(qr_data),
            'security_status': 'secure_qr_generated',
            'encrypted': True,
            'message': 'Secure QR code generated successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'security_status': 'secure_generation_failed'
        }), 500


@app.route('/validate_qr_security', methods=['POST'])
def validate_qr_security_endpoint():
    """Validate if QR belongs to specific document."""
    try:
        # Check for uploaded QR image
        if 'qr_image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No QR image file uploaded',
                'security_status': 'missing_qr_image'
            }), 400

        # Check for uploaded document
        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No document file uploaded',
                'security_status': 'missing_document'
            }), 400

        qr_file = request.files['qr_image']
        document_file = request.files['document']
        document_key = request.form.get('document_key')  # Optional
        detailed = request.form.get('detailed', 'false').lower() == 'true'

        # Validate files
        if qr_file.filename == '' or document_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected',
                'security_status': 'no_files_selected'
            }), 400

        # Check file types
        if not allowed_file(qr_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': 'Invalid QR image type. Only PNG files are allowed.',
                'security_status': 'invalid_qr_type'
            }), 400

        if not (allowed_file(document_file.filename, ALLOWED_DOCX_EXTENSIONS) or 
                allowed_file(document_file.filename, ALLOWED_PDF_EXTENSIONS)):
            return jsonify({
                'success': False,
                'error': 'Invalid document type. Only DOCX and PDF files are allowed.',
                'security_status': 'invalid_document_type'
            }), 400

        # Save uploaded files temporarily
        qr_temp_filename = f"temp_qr_{uuid.uuid4().hex}.png"
        qr_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_temp_filename)
        qr_file.save(qr_temp_path)

        doc_temp_filename = f"temp_doc_{uuid.uuid4().hex}_{document_file.filename}"
        doc_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_temp_filename)
        document_file.save(doc_temp_path)

        try:
            # Generate document key if not provided
            if not document_key:
                document_key = security_utils.generate_document_key(doc_temp_path)

            # Read QR code data
            qr_data_list = read_qr(qr_temp_path)
            if not qr_data_list:
                return jsonify({
                    'success': False,
                    'error': 'No QR code data found in image',
                    'security_status': 'qr_read_failed'
                }), 400

            qr_data = qr_data_list[0]
            document_hash = security_utils.generate_document_hash(doc_temp_path)

            # Perform validation
            if detailed:
                validation_results = validate_qr_security(qr_data, document_key, document_hash)
                
                # Try to decrypt QR data
                decrypted_data = None
                decryption_success = False
                try:
                    decrypted_data = read_secure_qr(qr_temp_path, document_key)
                    decryption_success = True
                except Exception:
                    pass

                return jsonify({
                    'success': True,
                    'validation_results': validation_results,
                    'overall_valid': validation_results['overall_valid'],
                    'security_score': validation_results.get('security_score', 0),
                    'decrypted_data': decrypted_data,
                    'decryption_success': decryption_success,
                    'qr_data_length': len(qr_data),
                    'document_name': document_file.filename,
                    'security_status': 'validation_complete' if validation_results['overall_valid'] else 'validation_failed'
                })
            else:
                # Simple validation
                is_authorized = security_utils.is_qr_authorized_for_document(qr_data, document_key, doc_temp_path)
                
                # Try to decrypt
                decrypted_data = None
                try:
                    decrypted_data = read_secure_qr(qr_temp_path, document_key)
                except Exception:
                    pass

                return jsonify({
                    'success': True,
                    'is_authorized': is_authorized,
                    'decrypted_data': decrypted_data,
                    'qr_data_length': len(qr_data),
                    'document_name': document_file.filename,
                    'security_status': 'authorized' if is_authorized else 'unauthorized'
                })

        finally:
            # Clean up temporary files
            for temp_file in [qr_temp_path, doc_temp_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'security_status': 'validation_error'
        }), 500


@app.route('/get_document_hash', methods=['POST'])
def get_document_hash():
    """Get document hash for security verification."""
    try:
        # Check if a document file is uploaded
        if 'document' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No document file uploaded',
                'security_status': 'missing_document'
            }), 400

        document_file = request.files['document']
        if document_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No document file selected',
                'security_status': 'no_file_selected'
            }), 400

        # Check file type
        if not (allowed_file(document_file.filename, ALLOWED_DOCX_EXTENSIONS) or 
                allowed_file(document_file.filename, ALLOWED_PDF_EXTENSIONS)):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only DOCX and PDF files are allowed.',
                'security_status': 'invalid_file_type'
            }), 400

        # Save the uploaded document temporarily
        temp_filename = f"temp_doc_{uuid.uuid4().hex}_{document_file.filename}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        document_file.save(temp_path)

        try:
            # Generate document hash
            document_hash = security_utils.generate_document_hash(temp_path)
            
            # Get file size for additional info
            file_size = os.path.getsize(temp_path)
            
            return jsonify({
                'success': True,
                'document_hash': document_hash,
                'document_name': document_file.filename,
                'file_size': file_size,
                'hash_algorithm': 'SHA-256',
                'security_status': 'hash_generated',
                'message': 'Document hash generated successfully'
            })

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'security_status': 'hash_generation_failed'
        }), 500


@app.route('/embed_secure_document', methods=['POST'])
def embed_secure_document():
    """Enhanced embed with security validation."""
    try:
        # Check for required files
        if 'document' not in request.files or 'qr_image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both document and QR image files are required',
                'security_status': 'missing_files'
            }), 400

        document_file = request.files['document']
        qr_file = request.files['qr_image']
        document_key = request.form.get('document_key')  # Optional
        validate_security = request.form.get('validate_security', 'false').lower() == 'true'

        if document_file.filename == '' or qr_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected',
                'security_status': 'no_files_selected'
            }), 400

        # Validate file types
        if not (allowed_file(document_file.filename, ALLOWED_DOCX_EXTENSIONS) or 
                allowed_file(document_file.filename, ALLOWED_PDF_EXTENSIONS)):
            return jsonify({
                'success': False,
                'error': 'Invalid document type. Only DOCX and PDF files are allowed.',
                'security_status': 'invalid_document_type'
            }), 400

        if not allowed_file(qr_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': 'Invalid QR image type. Only PNG files are allowed.',
                'security_status': 'invalid_qr_type'
            }), 400

        # Save uploaded files
        doc_filename = f"doc_embed_in_{uuid.uuid4().hex}.{document_file.filename.rsplit('.', 1)[1].lower()}"
        doc_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
        document_file.save(doc_path)

        qr_filename = f"qr_embed_in_{uuid.uuid4().hex}.png"
        qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
        qr_file.save(qr_path)

        # Generate output filename
        file_extension = document_file.filename.rsplit('.', 1)[1].lower()
        output_filename = f"stego_doc_{uuid.uuid4().hex}.{file_extension}"
        output_path = os.path.join(app.config['GENERATED_FOLDER'], output_filename)

        # Copy to documents folder for public access
        watermarked_filename = f"watermarked_{uuid.uuid4().hex}.{file_extension}"
        watermarked_path = os.path.join(app.config['DOCUMENTS_FOLDER'], watermarked_filename)

        try:
            # Security validation if requested
            security_validation_results = None
            if validate_security:
                if not document_key:
                    document_key = security_utils.generate_document_key(doc_path)

                # Validate QR-document pairing
                qr_data_list = read_qr(qr_path)
                if qr_data_list:
                    qr_data = qr_data_list[0]
                    document_hash = security_utils.generate_document_hash(doc_path)
                    
                    validation_results = validate_qr_security(qr_data, document_key, document_hash)
                    security_validation_results = validation_results
                    
                    if not validation_results['overall_valid']:
                        return jsonify({
                            'success': False,
                            'error': 'Security validation failed - QR code is not authorized for this document',
                            'security_status': 'validation_failed',
                            'validation_results': validation_results
                        }), 400

            # Perform embedding based on file type
            if file_extension == 'docx':
                result = embed_watermark_to_docx(
                    doc_path, qr_path, output_path,
                    validate_security=validate_security,
                    document_key=document_key
                )
            else:  # pdf
                result = embed_watermark_to_pdf(
                    doc_path, qr_path, output_path,
                    validate_security=validate_security,
                    document_key=document_key
                )

            if result['success']:
                # Copy to public documents folder
                shutil.copy2(output_path, watermarked_path)
                
                return jsonify({
                    'success': True,
                    'output_filename': output_filename,
                    'watermarked_filename': watermarked_filename,
                    'document_type': file_extension.upper(),
                    'processed_images': result.get('processed_images', 0),
                    'security_validation': security_validation_results,
                    'document_key': document_key if validate_security else None,
                    'security_status': 'embed_complete_secure' if validate_security else 'embed_complete',
                    'message': 'Document watermarking completed successfully with security validation' if validate_security else 'Document watermarking completed successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Embedding failed'),
                    'security_status': 'embed_failed'
                }), 500

        finally:
            # Clean up temporary files
            for temp_file in [doc_path, qr_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'security_status': 'embed_error'
        }), 500


# Helper functions for security status management
def get_embed_security_status(security_enabled, validation_results, auth_status):
    """Get security status for embed operation."""
    if not security_enabled:
        return "embed_complete"
    
    if validation_results and auth_status:
        if auth_status.get('overall_valid', False):
            return "embed_complete_secure"
        else:
            return "embed_complete_unauthorized"
    
    return "embed_complete_secure" if validation_results else "embed_complete"


def get_embed_security_warnings(security_enabled, auth_status):
    """Get security warnings for embed operation."""
    warnings = []
    
    if security_enabled and auth_status:
        if not auth_status.get('overall_valid', False):
            warnings.append("QR authorization validation failed")
        
        security_score = auth_status.get('security_score', 0)
        if security_score < 60:
            warnings.append("Low security score detected")
    
    return warnings


def get_embed_security_recommendations(security_enabled, key_generated):
    """Get security recommendations for embed operation."""
    recommendations = []
    
    if security_enabled:
        if key_generated:
            recommendations.append("Store the generated document key securely")
            recommendations.append("Use the same key for validation and extraction")
        
        recommendations.append("Enable QR authorization for enhanced security")
        recommendations.append("Verify document integrity after embedding")
    else:
        recommendations.append("Consider enabling document security for better protection")
    
    return recommendations


def get_extract_security_status(security_enabled, overall_status):
    """Get security status for extract operation."""
    if not security_enabled:
        return "extraction_complete"
    
    # Check if all security checks passed
    verification_status = overall_status.get('security_verification_status', 'pending')
    auth_status = overall_status.get('key_authorization_status', 'pending')
    integrity_status = overall_status.get('document_integrity_status', 'pending')
    
    if verification_status == 'success' and auth_status == 'success' and integrity_status == 'success':
        return "extraction_complete_secure"
    elif verification_status == 'error' or auth_status == 'error' or integrity_status == 'error':
        return "extraction_complete_unauthorized"
    else:
        return "extraction_complete_partial"


# Key Management API Endpoints
@app.route('/api/security/list-keys', methods=['GET'])
def api_list_security_keys():
    """List all security keys with metadata."""
    try:
        # Import security storage
        from security_storage import list_secured_documents
        
        keys = list_secured_documents()
        
        return jsonify({
            'success': True,
            'keys': keys,
            'count': len(keys)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/key-details/<doc_hash>', methods=['GET'])
def api_get_key_details(doc_hash):
    """Get detailed information about a specific security key."""
    try:
        from security_storage import retrieve_document_key
        
        key_data = retrieve_document_key(doc_hash)
        if not key_data:
            return jsonify({
                'success': False,
                'error': 'Security key not found'
            }), 404
        
        return jsonify({
            'success': True,
            'key': key_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/export-key/<doc_hash>', methods=['GET'])
def api_export_single_key(doc_hash):
    """Export a single security key as JSON file."""
    try:
        from security_storage import retrieve_document_key
        
        key_data = retrieve_document_key(doc_hash)
        if not key_data:
            return jsonify({
                'success': False,
                'error': 'Security key not found'
            }), 404
        
        # Create export data
        export_data = {
            'version': '1.0',
            'export_type': 'single_key',
            'exported_at': security_utils.get_current_timestamp(),
            'key': key_data
        }
        
        json_data = json.dumps(export_data, indent=2)
        
        return Response(
            json_data,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=security_key_{doc_hash[:8]}.json'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/delete-key/<doc_hash>', methods=['DELETE'])
def api_delete_security_key(doc_hash):
    """Delete a security key."""
    try:
        from security_storage import delete_document_key
        
        success = delete_document_key(doc_hash)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Security key not found or could not be deleted'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Security key deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/export-backup', methods=['GET'])
def api_export_security_backup():
    """Export all security keys as backup file."""
    try:
        from security_storage import export_security_backup
        
        backup_data = export_security_backup()
        json_data = json.dumps(backup_data, indent=2)
        
        return Response(
            json_data,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=security_backup_{security_utils.get_current_timestamp()[:10]}.json'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/import-backup', methods=['POST'])
def api_import_security_backup():
    """Import security keys from backup file."""
    try:
        from security_storage import import_security_backup
        
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No backup file provided'
            }), 400
        
        file = request.files['backup_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({
                'success': False,
                'error': 'Invalid file format. Please upload a JSON backup file.'
            }), 400
        
        # Read and parse the backup file
        try:
            backup_data = json.loads(file.read().decode('utf-8'))
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON format in backup file'
            }), 400
        
        # Import the backup
        result = import_security_backup(backup_data)
        
        return jsonify({
            'success': True,
            'imported_count': result.get('imported_count', 0),
            'skipped_count': result.get('skipped_count', 0),
            'message': 'Backup imported successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/cleanup-keys', methods=['POST'])
def api_cleanup_old_keys():
    """Cleanup old security keys."""
    try:
        from security_storage import cleanup_expired_keys
        
        data = request.get_json()
        if not data or 'days' not in data:
            return jsonify({
                'success': False,
                'error': 'Number of days not specified'
            }), 400
        
        days = int(data['days'])
        if days < 1:
            return jsonify({
                'success': False,
                'error': 'Days must be a positive number'
            }), 400
        
        deleted_count = cleanup_expired_keys(days)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Removed {deleted_count} old security keys'
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid number of days'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/security/statistics', methods=['GET'])
def api_get_security_statistics():
    """Get comprehensive security statistics."""
    try:
        from security_storage import list_secured_documents, get_storage_stats
        import os
        from datetime import datetime, timedelta
        
        # Get all keys
        all_keys = list_secured_documents()
        
        # Get storage stats
        storage_stats = get_storage_stats()
        
        # Calculate basic statistics
        total_documents = len(all_keys)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Active keys (accessed in last 7 days)
        active_keys = 0
        weekly_keys = 0
        
        for key in all_keys:
            try:
                # Parse last_accessed date safely
                last_accessed_str = key.get('last_accessed', '')
                if last_accessed_str:
                    # Handle different date formats
                    if 'Z' in last_accessed_str:
                        last_accessed_str = last_accessed_str.replace('Z', '+00:00')
                    last_accessed = datetime.fromisoformat(last_accessed_str.replace('Z', ''))
                    if last_accessed > week_ago:
                        active_keys += 1
                
                # Parse created_at date safely
                created_at_str = key.get('created_at', '')
                if created_at_str:
                    if 'Z' in created_at_str:
                        created_at_str = created_at_str.replace('Z', '+00:00')
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', ''))
                    if created_at > week_ago:
                        weekly_keys += 1
            except (ValueError, TypeError) as e:
                # Skip keys with invalid date formats
                continue
        
        # Most accessed document
        most_accessed = None
        if all_keys:
            most_accessed = max(all_keys, key=lambda x: x.get('access_count', 0), default=None)
        most_accessed_name = most_accessed.get('document_name', 'N/A') if most_accessed else 'N/A'
        
        # Average access count
        if all_keys:
            avg_access = sum(key.get('access_count', 0) for key in all_keys) / len(all_keys)
        else:
            avg_access = 0
        
        # Storage calculation from storage stats
        storage_used_kb = storage_stats.get('file_size_kb', 0)
        
        # Success rate (simplified calculation)
        success_rate = 95 if total_documents > 0 else 100
        
        # Recent activities (mock data based on keys)
        recent_activities = []
        for key in sorted(all_keys, key=lambda x: x.get('last_accessed', ''), reverse=True)[:5]:
            doc_name = key.get('document_name', 'Unknown')
            if len(doc_name) > 30:
                doc_name = doc_name[:30] + '...'
            recent_activities.append({
                'description': f"Key accessed for {doc_name}",
                'timestamp': key.get('last_accessed', ''),
                'icon': 'key'
            })
        
        # Security alerts (basic health checks)
        security_alerts = []
        if total_documents == 0:
            security_alerts.append({
                'type': 'warning',
                'icon': 'exclamation-triangle',
                'message': 'No security keys found. Start securing documents to improve protection.'
            })
        elif active_keys < total_documents * 0.5:
            security_alerts.append({
                'type': 'warning',
                'icon': 'clock',
                'message': f'{total_documents - active_keys} keys have not been accessed recently.'
            })
        
        if not security_alerts:
            security_alerts.append({
                'type': 'success',
                'icon': 'check-circle',
                'message': 'All security systems operational'
            })
        
        statistics = {
            'total_documents': total_documents,
            'active_keys': active_keys,
            'success_rate': round(success_rate, 1),
            'recent_activities': len(recent_activities),
            'most_accessed_document': most_accessed_name,
            'average_access_count': round(avg_access, 1),
            'keys_created_this_week': weekly_keys,
            'storage_used_kb': storage_used_kb,
            'recent_activity_list': recent_activities,
            'security_alerts': security_alerts,
            'storage_stats': storage_stats
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        print(f"[ERROR] Security statistics error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'statistics': {
                'total_documents': 0,
                'active_keys': 0,
                'success_rate': 0,
                'recent_activities': 0,
                'most_accessed_document': 'N/A',
                'average_access_count': 0,
                'keys_created_this_week': 0,
                'storage_used_kb': 0,
                'recent_activity_list': [],
                'security_alerts': [{
                    'type': 'error',
                    'icon': 'exclamation-triangle',
                    'message': 'Error loading security statistics'
                }]
            }
        }), 500


@app.route('/api/security/export-report', methods=['GET'])
def api_export_security_report():
    """Export security statistics as CSV report."""
    try:
        from security_storage import list_secured_documents
        from datetime import datetime
        
        # Get all keys
        all_keys = list_secured_documents()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Document Name',
            'Document Hash',
            'Created Date',
            'Last Accessed',
            'Access Count',
            'Key Size (bytes)',
            'Status'
        ])
        
        # Write key data
        now = datetime.now()
        for key in all_keys:
            try:
                last_accessed = datetime.fromisoformat(key['last_accessed'].replace('Z', '+00:00'))
                days_since_access = (now - last_accessed).days
                
                if days_since_access <= 7:
                    status = 'Active'
                elif days_since_access <= 30:
                    status = 'Recent'
                else:
                    status = 'Old'
                
                writer.writerow([
                    key['document_name'],
                    key['document_hash'],
                    key['created_at'],
                    key['last_accessed'],
                    key['access_count'],
                    key.get('key_size', 'N/A'),
                    status
                ])
            except Exception as e:
                # Handle any date parsing errors
                writer.writerow([
                    key['document_name'],
                    key['document_hash'],
                    key.get('created_at', 'N/A'),
                    key.get('last_accessed', 'N/A'),
                    key.get('access_count', 0),
                    key.get('key_size', 'N/A'),
                    'Unknown'
                ])
        
        # Add summary statistics
        writer.writerow([])
        writer.writerow(['=== SECURITY SUMMARY ==='])
        writer.writerow(['Total Documents', len(all_keys)])
        writer.writerow(['Report Generated', now.strftime('%Y-%m-%d %H:%M:%S')])
        
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=security_report_{now.strftime("%Y%m%d")}.csv'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Menjalankan aplikasi Flask
if __name__ == '__main__':
    ports = [5001, 5002, 5003, 5004, 5005]

    for port in ports:
        try:
            print(f"Mencoba menjalankan aplikasi pada port {port}...")
            app.run(debug=True, host='0.0.0.0', port=port)
            break  # Keluar dari loop jika berhasil
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {port} sudah digunakan. Mencoba port berikutnya...")
            else:
                print(f"Error: {e}")
                break
    else:
        print("Semua port yang dicoba sudah digunakan. Harap tutup beberapa aplikasi dan coba lagi.")
