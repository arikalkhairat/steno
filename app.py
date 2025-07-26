 # File: app.py
# Deskripsi: Aplikasi web Flask untuk watermarking dokumen .docx dengan QR Code LSB.

import os
import subprocess
import uuid
import shutil
import logging
import time
from collections import defaultdict
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import numpy as np
import fitz  # PyMuPDF

from main import extract_images_from_docx, embed_watermark_to_docx, extract_images_from_pdf, embed_watermark_to_pdf
from qr_utils import read_qr

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Simple cache for QR analysis results
qr_analysis_cache = {}
cache_expiry = defaultdict(float)
CACHE_DURATION = 300  # 5 minutes

# Rate limiting for real-time requests
request_counts = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX_REQUESTS = 50  # Max 50 requests per minute per IP


def rate_limit(max_requests=50, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            now = time.time()
            
            # Clean old requests
            request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] if now - req_time < window]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    "success": False,
                    "message": "Rate limit exceeded. Please wait before making more requests.",
                    "error": "RATE_LIMIT_EXCEEDED"
                }), 429
            
            # Add current request
            request_counts[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_qr_input(data, max_length=500):
    """Validate QR code input data"""
    if not data:
        return False, "QR data cannot be empty"
    
    if len(data) > max_length:
        return False, f"QR data too long. Maximum {max_length} characters allowed"
    
    # Check for potentially harmful content
    dangerous_patterns = ['<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=']
    data_lower = data.lower()
    for pattern in dangerous_patterns:
        if pattern in data_lower:
            return False, "Invalid characters detected in QR data"
    
    return True, ""


def get_cache_key(data, error_correction='M'):
    """Generate cache key for QR analysis"""
    return f"{hash(data)}_{error_correction}"


def get_cached_analysis(cache_key):
    """Get cached analysis if still valid"""
    if cache_key in qr_analysis_cache and time.time() < cache_expiry[cache_key]:
        return qr_analysis_cache[cache_key]
    return None


def cache_analysis(cache_key, analysis):
    """Cache analysis result"""
    qr_analysis_cache[cache_key] = analysis
    cache_expiry[cache_key] = time.time() + CACHE_DURATION


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
@rate_limit(max_requests=30, window=60)
def generate_qr_route():
    """Enhanced QR generation endpoint with comprehensive metadata and caching"""
    data = request.form.get('qrData')
    
    # Enhanced input validation
    is_valid, error_msg = validate_qr_input(data)
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400

    # Get enhanced parameters with defaults
    error_correction = request.form.get('errorCorrection', 'M').upper()
    qr_size = int(request.form.get('qrSize', 10))
    border_size = int(request.form.get('borderSize', 4))
    fill_color = request.form.get('fillColor', '#000000')
    back_color = request.form.get('backColor', '#ffffff')
    
    # Validate parameters
    if error_correction not in ['L', 'M', 'Q', 'H']:
        error_correction = 'M'
    
    qr_size = max(1, min(50, qr_size))  # Limit size between 1-50
    border_size = max(0, min(20, border_size))  # Limit border between 0-20

    try:
        # Import enhanced QR utilities
        from qr_utils import generate_qr_with_analysis, get_capacity_info
        
        # Check cache first
        cache_key = get_cache_key(data, error_correction)
        cached_result = get_cached_analysis(cache_key)
        
        # Generate filename
        qr_filename = f"qr_{uuid.uuid4().hex}.png"
        qr_output_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)
        
        # Use enhanced generate_qr_with_analysis function
        result = generate_qr_with_analysis(
            data,
            qr_output_path,
            error_correction=error_correction,
            box_size=qr_size,
            border=border_size,
            fill_color=fill_color,
            back_color=back_color
        )
        
        if result.get('success'):
            metadata = result.get('metadata', {})
            comprehensive_analysis = result.get('comprehensive_analysis', {})
            
            # Get capacity information for all levels
            capacity_info = get_capacity_info(len(data), error_correction)
            all_levels = capacity_info.get('all_levels', {})
            
            # Prepare enhanced response
            response_data = {
                "success": True,
                "message": "QR Code generated successfully",
                "qr_url": f"/static/generated/{qr_filename}",
                "qr_filename": qr_filename,
                "metadata": {
                    "version": metadata.get('version'),
                    "modules": int(metadata.get('module_count', '0x0').split('x')[0]) if 'x' in str(metadata.get('module_count', '')) else metadata.get('version', 1) * 4 + 17,
                    "data_length": len(data),
                    "error_correction": error_correction,
                    "capacity_usage": float(metadata.get('capacity_used', '0').replace('%', '')),
                    "max_capacity": metadata.get('max_capacity'),
                    "steganography_score": metadata.get('steganography_score', 0),
                    "recommendations": metadata.get('recommendations', [])
                },
                "capacity_breakdown": {
                    level: {
                        "max": level_data.get('capacity', 0),
                        "used": len(data),
                        "percentage": round((len(data) / level_data.get('capacity', 1)) * 100, 1) if level_data.get('capacity', 0) > 0 else 0
                    }
                    for level, level_data in all_levels.items()
                },
                "steganography_analysis": comprehensive_analysis.get('steganography_analysis', {}),
                "log": "QR Code generated successfully with enhanced analysis"
            }
            
            # Cache the analysis part
            analysis_data = {
                "metadata": response_data["metadata"],
                "capacity_breakdown": response_data["capacity_breakdown"],
                "steganography_analysis": response_data["steganography_analysis"]
            }
            cache_analysis(cache_key, analysis_data)
            
            return jsonify(response_data)
        else:
            error_message = result.get('error', 'Unknown error occurred')
            logger.error(f"QR generation failed: {error_message}")
            return jsonify({
                "success": False,
                "message": f"Failed to generate QR Code: {error_message}",
                "log": error_message
            }), 500
        
    except Exception as e:
        logger.error(f"Error in generate_qr_route: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Internal server error: {str(e)}",
            "log": str(e)
        }), 500


@app.route('/generate_qr_realtime', methods=['POST'])
def generate_qr_realtime_route():
    """Enhanced QR generation endpoint with real-time analysis using enhanced qr_utils"""
    data = request.form.get('qrData')
    if not data:
        return jsonify({"success": False, "message": "Data QR tidak boleh kosong."}), 400

    # Get enhanced parameters
    error_correction = request.form.get('errorCorrection', 'M')
    qr_size = int(request.form.get('qrSize', 10))
    border_size = int(request.form.get('borderSize', 4))
    fill_color = request.form.get('fillColor', '#000000')
    back_color = request.form.get('backColor', '#ffffff')
    is_preview = request.form.get('preview', 'false') == 'true'

    try:
        # Import enhanced QR utilities
        from qr_utils import generate_qr_with_analysis, get_capacity_info
        
        # Generate filename
        filename_prefix = "qr_preview" if is_preview else "qr_advanced"
        qr_filename = f"{filename_prefix}_{uuid.uuid4().hex}.png"
        qr_output_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)
        
        # Use enhanced generate_qr_with_analysis function
        result = generate_qr_with_analysis(
            data,
            qr_output_path,
            error_correction=error_correction,
            box_size=qr_size,
            border=border_size,
            fill_color=fill_color,
            back_color=back_color
        )
        
        if result.get('success'):
            metadata = result.get('metadata', {})
            comprehensive_analysis = result.get('comprehensive_analysis', {})
            
            # Extract analysis data for frontend
            analysis = {
                "version": metadata.get('version'),
                "dimensions": {
                    "width": int(metadata.get('size_pixels', '0x0').split('x')[0]) if 'x' in str(metadata.get('size_pixels', '')) else 0,
                    "height": int(metadata.get('size_pixels', '0x0').split('x')[1]) if 'x' in str(metadata.get('size_pixels', '')) else 0
                },
                "capacity": metadata.get('max_capacity'),
                "density": metadata.get('capacity_used')
            }
            
            # Get capacity for all error correction levels
            capacity_info = get_capacity_info(len(data), error_correction)
            capacity = {}
            for level in ['l', 'm', 'q', 'h']:
                level_upper = level.upper()
                level_data = capacity_info.get('all_levels', {}).get(level_upper, {})
                capacity[level] = level_data.get('capacity', 0)
            
            return jsonify({
                "success": True,
                "message": "QR Code berhasil dibuat dengan analisis lengkap!",
                "qr_url": f"/static/generated/{qr_filename}",
                "qr_filename": qr_filename,
                "analysis": analysis,
                "capacity": capacity,
                "metadata": metadata,
                "steganography_analysis": comprehensive_analysis.get('steganography_analysis', {}),
                "recommendations": metadata.get('recommendations', [])
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Error generating QR Code: {result.get('error', 'Unknown error')}"
            }), 500
        
    except Exception as e:
        logger.error(f"Error in generate_qr_realtime_route: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error generating QR Code: {str(e)}"
        }), 500


@app.route('/analyze_qr', methods=['POST'])
@rate_limit(max_requests=100, window=60)  # Higher limit for analysis-only requests
def analyze_qr_route():
    """Return QR analysis without generating file"""
    data = request.form.get('qrData') or request.json.get('qrData') if request.is_json else None
    
    # Enhanced input validation
    is_valid, error_msg = validate_qr_input(data)
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400

    # Get analysis parameters
    error_correction = (request.form.get('errorCorrection') or 
                       (request.json.get('errorCorrection') if request.is_json else 'M')).upper()
    
    # Validate error correction level
    if error_correction not in ['L', 'M', 'Q', 'H']:
        error_correction = 'M'

    try:
        # Import enhanced QR utilities
        from qr_utils import analyze_qr_requirements, get_capacity_info, estimate_steganography_capacity
        
        # Check cache first
        cache_key = get_cache_key(data, error_correction)
        cached_result = get_cached_analysis(cache_key)
        
        if cached_result:
            return jsonify({
                "success": True,
                "cached": True,
                "analysis": cached_result.get('analysis', {}),
                "capacity_breakdown": cached_result.get('capacity_breakdown', {}),
                "steganography_analysis": cached_result.get('steganography_analysis', {})
            })
        
        # Perform analysis
        qr_analysis = analyze_qr_requirements(data)
        capacity_info = get_capacity_info(len(data), error_correction)
        
        # For steganography analysis, we need to estimate QR size first
        # Use a reasonable default size based on the data length
        estimated_qr_size = (qr_analysis.get('modules_needed', 25) * 10, qr_analysis.get('modules_needed', 25) * 10)
        stego_analysis = estimate_steganography_capacity(estimated_qr_size)
        
        # Extract analysis data
        analysis_result = {
            "optimal_version": qr_analysis.get('recommended_version'),
            "required_modules": qr_analysis.get('modules_needed'),
            "data_complexity": qr_analysis.get('complexity_level', 'medium'),
            "capacity_breakdown": {},
            "steganography_compatibility": {
                "score": stego_analysis.get('compatibility_score', 0),
                "suitable_for_embedding": stego_analysis.get('suitable_for_embedding', False),
                "estimated_capacity": stego_analysis.get('estimated_lsb_capacity', 0)
            }
        }
        
        # Build capacity breakdown for all error correction levels
        all_levels = capacity_info.get('all_levels', {})
        for level_name, level_data in all_levels.items():
            level_key = level_name  # Keep original case (L, M, Q, H)
            max_capacity = level_data.get('capacity', 0)
            usage_percentage = round((len(data) / max_capacity * 100), 1) if max_capacity > 0 else 0
            
            analysis_result["capacity_breakdown"][level_key] = {
                "max": max_capacity,
                "used": len(data),
                "percentage": usage_percentage
            }
        
        # Prepare complete response
        response_data = {
            "success": True,
            "cached": False,
            "analysis": analysis_result,
            "recommendations": qr_analysis.get('recommendations', []),
            "processing_time": f"{time.time()}"
        }
        
        # Cache the result
        cache_data = {
            "analysis": analysis_result,
            "capacity_breakdown": analysis_result["capacity_breakdown"],
            "steganography_analysis": analysis_result["steganography_compatibility"]
        }
        cache_analysis(cache_key, cache_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in analyze_qr_route: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}",
            "error": "ANALYSIS_ERROR"
        }), 500


@app.route('/qr_config', methods=['GET'])
def qr_config_route():
    """Return available QR configuration options"""
    try:
        # Import enhanced utilities to get actual capacity data
        from qr_utils import get_capacity_info
        
        # Get sample capacity information
        sample_capacity = get_capacity_info(50, 'M')  # Sample with 50 characters
        
        config_data = {
            "error_correction_levels": {
                "L": {
                    "name": "Low",
                    "description": "~7% error correction",
                    "recovery_capability": "Can recover from ~7% data loss",
                    "recommended_for": "Clean environments, large QR codes"
                },
                "M": {
                    "name": "Medium", 
                    "description": "~15% error correction",
                    "recovery_capability": "Can recover from ~15% data loss",
                    "recommended_for": "General purpose, balanced performance"
                },
                "Q": {
                    "name": "Quartile",
                    "description": "~25% error correction", 
                    "recovery_capability": "Can recover from ~25% data loss",
                    "recommended_for": "Industrial environments, moderate damage"
                },
                "H": {
                    "name": "High",
                    "description": "~30% error correction",
                    "recovery_capability": "Can recover from ~30% data loss", 
                    "recommended_for": "Harsh environments, maximum reliability"
                }
            },
            "size_options": {
                "min_size": 1,
                "max_size": 50,
                "recommended_size": 10,
                "description": "Size affects scan reliability and file size"
            },
            "border_options": {
                "min_border": 0,
                "max_border": 20,
                "recommended_border": 4,
                "description": "Border provides quiet zone for better scanning"
            },
            "color_options": {
                "fill_color": {
                    "default": "#000000",
                    "description": "Color of QR code modules (dark areas)",
                    "recommendations": "Use dark colors for better contrast"
                },
                "back_color": {
                    "default": "#ffffff", 
                    "description": "Background color of QR code",
                    "recommendations": "Use light colors for better contrast"
                }
            },
            "capacity_limits": {
                "max_recommended_length": 500,
                "optimal_length_range": "50-200 characters",
                "performance_note": "Longer text requires larger QR versions"
            },
            "steganography_guidelines": {
                "optimal_conditions": {
                    "data_length": "< 100 characters",
                    "error_correction": "L or M",
                    "size": ">= 8",
                    "description": "Best conditions for LSB embedding"
                },
                "compatibility_scoring": {
                    "excellent": "90-100 points",
                    "good": "70-89 points", 
                    "fair": "50-69 points",
                    "poor": "< 50 points"
                }
            },
            "version_info": {
                "total_versions": 40,
                "version_range": "1-40",
                "auto_selection": "System automatically selects optimal version",
                "module_range": "21x21 to 177x177"
            },
            "api_limits": {
                "rate_limit": {
                    "generate": "30 requests per minute",
                    "analyze": "100 requests per minute",
                    "config": "No limit"
                },
                "cache_duration": "5 minutes",
                "max_data_length": 500
            }
        }
        
        return jsonify({
            "success": True,
            "message": "QR configuration options retrieved successfully",
            "config": config_data,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in qr_config_route: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve configuration: {str(e)}",
            "error": "CONFIG_ERROR"
        }), 500


def get_qr_capacity(version, error_correction):
    """Get maximum character capacity for given QR version and error correction level"""
    # Use the enhanced qr_utils function instead of the old implementation
    try:
        from qr_utils import get_capacity_info
        
        # Estimate data length for the given version (rough approximation)
        # This is used for backwards compatibility only
        estimated_data_length = 1  # Minimal data length for capacity lookup
        
        capacity_info = get_capacity_info(estimated_data_length, error_correction)
        all_levels = capacity_info.get('all_levels', {})
        
        if error_correction in all_levels:
            return all_levels[error_correction].get('capacity', 100)
        
        # Fallback to old method if enhanced function fails
        capacities = {
            1: {'L': 25, 'M': 20, 'Q': 16, 'H': 10},
            2: {'L': 47, 'M': 38, 'Q': 29, 'H': 20},
            3: {'L': 77, 'M': 61, 'Q': 47, 'H': 35},
            4: {'L': 114, 'M': 90, 'Q': 67, 'H': 50},
            5: {'L': 154, 'M': 122, 'Q': 87, 'H': 64},
            6: {'L': 195, 'M': 154, 'Q': 108, 'H': 84},
            7: {'L': 224, 'M': 178, 'Q': 125, 'H': 93},
            8: {'L': 279, 'M': 221, 'Q': 157, 'H': 122},
            9: {'L': 335, 'M': 262, 'Q': 189, 'H': 143},
            10: {'L': 395, 'M': 311, 'Q': 221, 'H': 174}
        }
        
        if version <= 10:
            return capacities.get(version, {}).get(error_correction, 100)
        else:
            base_capacity = capacities[10][error_correction]
            return int(base_capacity * (1 + (version - 10) * 0.3))
            
    except Exception as e:
        logger.error(f"Error in get_qr_capacity: {str(e)}")
        # Ultimate fallback
        return 100


@app.route('/embed_document', methods=['POST'])
def embed_document_route():
    if 'docxFileEmbed' not in request.files or 'qrFileEmbed' not in request.files:
        error_msg = "File Dokumen dan File QR Code diperlukan."
        print(f"[ERROR] /embed_document: {error_msg}")
        print(f"[ERROR] Missing fields: docxFileEmbed in files: {'docxFileEmbed' in request.files}, qrFileEmbed in files: {'qrFileEmbed' in request.files}")
        return jsonify({"success": False, "message": error_msg}), 400

    doc_file = request.files['docxFileEmbed']
    qr_file = request.files['qrFileEmbed']

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
    
    result = run_main_script(args)

    if result["success"]:
        print("[*] Proses embed_docx berhasil")
        
        # Run the appropriate embed function directly to get the processed images
        try:
            print("[*] Mendapatkan informasi gambar yang diproses")
            if is_docx:
                process_result = embed_watermark_to_docx(doc_temp_path, qr_temp_path, stego_doc_output_path)
            else:  # is_pdf
                process_result = embed_watermark_to_pdf(doc_temp_path, qr_temp_path, stego_doc_output_path)
            
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
                print(f"[*] Mendapatkan {len(processed_images)} gambar yang diproses")
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
            "document_type": "docx" if is_docx else "pdf"
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
        return jsonify({"success": False, "message": "File Dokumen diperlukan untuk validasi."}), 400

    doc_file = request.files['docxFileValidate']

    if doc_file.filename == '':
        return jsonify({"success": False, "message": "Nama file tidak boleh kosong."}), 400
    
    # Check if it's either DOCX or PDF
    is_docx = allowed_file(doc_file.filename, ALLOWED_DOCX_EXTENSIONS)
    is_pdf = allowed_file(doc_file.filename, ALLOWED_PDF_EXTENSIONS)
    
    if not (doc_file and (is_docx or is_pdf)):
        return jsonify({"success": False, "message": "Format Dokumen harus .docx atau .pdf"}), 400

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
        if os.path.exists(output_extraction_dir_path) and os.path.isdir(output_extraction_dir_path):
            for filename in os.listdir(output_extraction_dir_path):
                if filename.lower().endswith('.png'):
                    extracted_qrs_info.append({
                        "filename": filename,
                        "url": f"/static/generated/{output_extraction_dir_name}/{filename}"
                    })

        if not extracted_qrs_info and "Tidak ada gambar yang ditemukan" not in result["stdout"]:
            pass

        # Hapus file temporary setelah selesai
        if os.path.exists(doc_temp_path):
            os.remove(doc_temp_path)

        print(f"[*] Proses extract_{'docx' if is_docx else 'pdf'} berhasil")
        return jsonify({
            "success": True,
            "message": "Proses ekstraksi selesai.",
            "extracted_qrs": extracted_qrs_info,
            "log": result["stdout"],
            "document_type": "docx" if is_docx else "pdf"
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
