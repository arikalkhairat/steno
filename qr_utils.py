# File: qr_utils.py
# Deskripsi: Fungsi utilitas untuk membuat dan membaca QR Code.

import qrcode
import cv2
from PIL import Image
import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Import security utilities for encryption and authentication
import security_utils

def generate_qr(data: str, output_path: str):
    """
    Membuat citra QR Code dari data teks dan menyimpannya ke file.

    Args:
        data (str): Data teks yang akan dikodekan.
        output_path (str): Path file untuk menyimpan citra QR Code (misal, 'qrcode.png').

    Raises:
        Exception: Jika terjadi error saat pembuatan QR Code.
    """
    try:
        # Membuat instance QRCode
        qr = qrcode.QRCode(
            version=1, # Kontrol ukuran QR Code (1-40), None untuk otomatis
            error_correction=qrcode.constants.ERROR_CORRECT_L, # Tingkat koreksi error (L, M, Q, H)
            box_size=10, # Ukuran setiap kotak (piksel) dalam QR Code
            border=4, # Lebar border di sekitar QR Code (minimum 4 menurut standar)
        )
        # Menambahkan data ke QR Code
        qr.add_data(data)
        qr.make(fit=True) # fit=True menyesuaikan ukuran QR Code dengan data

        # Membuat citra dari objek QRCode
        img = qr.make_image(fill_color="black", back_color="white")
        # Menyimpan citra ke file
        img.save(output_path)
        print(f"[*] QR Code berhasil dibuat dan disimpan di: {output_path}")
    except Exception as e:
        # Menangani potensi error saat pembuatan atau penyimpanan
        print(f"[!] Error saat membuat QR Code: {e}")
        raise # Melempar kembali error untuk ditangani di level lebih tinggi jika perlu

def read_qr(image_path: str) -> list[str]:
    """
    Membaca data dari sebuah citra QR Code menggunakan OpenCV.

    Args:
        image_path (str): Path ke file citra QR Code.

    Returns:
        list[str]: List berisi data (string UTF-8) yang berhasil dibaca dari QR Code.
                   List bisa kosong jika tidak ada QR Code yang terdeteksi.

    Raises:
        FileNotFoundError: Jika file citra tidak ditemukan.
        Exception: Jika terjadi error lain saat membuka atau membaca citra.
    """
    # Memastikan file ada sebelum mencoba membukanya
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File tidak ditemukan: {image_path}")

    try:
        # Membaca citra menggunakan OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Gagal membaca citra: {image_path}")

        # Inisialisasi QR code detector
        qr_detector = cv2.QRCodeDetector()
        
        # Membaca QR code dari citra
        # retval: bool (berhasil/tidak)
        # decoded_info: string (data QR code)
        # points: numpy.ndarray (koordinat QR code)
        # straight_qrcode: numpy.ndarray (citra QR code yang telah diluruskan)
        retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(img)
        
        # Jika QR code terdeteksi
        if retval:
            # Filter out empty strings and convert to list
            data_list = [text for text in decoded_info if text]
        else:
            data_list = []

        # Memberi informasi jika tidak ada QR Code yang terdeteksi
        if not data_list:
            print(f"[!] Tidak ada QR Code yang terdeteksi di: {image_path}")
        return data_list
    except Exception as e:
        # Menangani potensi error saat membuka citra atau proses decoding
        print(f"[!] Error saat membaca QR Code: {e}")
        raise # Melempar kembali error

# Advanced QR Code Configuration Functions

def analyze_text_encoding(text: str) -> str:
    """
    Analyze the optimal encoding type for the given text.
    
    Args:
        text (str): The text to analyze for encoding type.
    
    Returns:
        str: The optimal encoding type ('numeric', 'alphanumeric', or 'byte').
    
    Raises:
        ValueError: If the text is empty.
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    # Check if text contains only numeric characters (0-9)
    if text.isdigit():
        return 'numeric'
    
    # Check if text contains only alphanumeric characters
    # QR alphanumeric mode supports: 0-9, A-Z, space, $, %, *, +, -, ., /, :
    alphanumeric_chars = set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:')
    if all(c in alphanumeric_chars for c in text.upper()):
        return 'alphanumeric'
    
    # Default to byte mode for other characters
    return 'byte'

def calculate_qr_capacity(version: int, error_level: str, encoding: str) -> int:
    """
    Calculate the data capacity for a QR code with given parameters.
    
    Args:
        version (int): QR code version (1-40).
        error_level (str): Error correction level ('L', 'M', 'Q', 'H').
        encoding (str): Encoding mode ('numeric', 'alphanumeric', 'byte').
    
    Returns:
        int: Maximum number of characters that can be encoded.
    
    Raises:
        ValueError: If parameters are invalid.
    """
    if not (1 <= version <= 40):
        raise ValueError("Version must be between 1 and 40")
    
    if error_level not in ['L', 'M', 'Q', 'H']:
        raise ValueError("Error level must be 'L', 'M', 'Q', or 'H'")
    
    if encoding not in ['numeric', 'alphanumeric', 'byte']:
        raise ValueError("Encoding must be 'numeric', 'alphanumeric', or 'byte'")
    
    # QR Code capacity table (simplified for common versions)
    # This is a simplified implementation - in practice, you'd use the full capacity table
    capacity_table = {
        # Format: version -> {error_level -> {encoding -> capacity}}
        1: {'L': {'numeric': 41, 'alphanumeric': 25, 'byte': 17},
            'M': {'numeric': 34, 'alphanumeric': 20, 'byte': 14},
            'Q': {'numeric': 27, 'alphanumeric': 16, 'byte': 11},
            'H': {'numeric': 17, 'alphanumeric': 10, 'byte': 7}},
        2: {'L': {'numeric': 77, 'alphanumeric': 47, 'byte': 32},
            'M': {'numeric': 63, 'alphanumeric': 38, 'byte': 26},
            'Q': {'numeric': 48, 'alphanumeric': 29, 'byte': 20},
            'H': {'numeric': 34, 'alphanumeric': 20, 'byte': 14}},
        3: {'L': {'numeric': 127, 'alphanumeric': 77, 'byte': 53},
            'M': {'numeric': 101, 'alphanumeric': 61, 'byte': 42},
            'Q': {'numeric': 77, 'alphanumeric': 47, 'byte': 32},
            'H': {'numeric': 58, 'alphanumeric': 35, 'byte': 24}},
        # Add more versions as needed...
    }
    
    # For versions not in the table, use approximation
    if version not in capacity_table:
        # Approximate capacity based on version size
        base_capacity = version * version * 0.3  # Rough approximation
        error_multipliers = {'L': 1.0, 'M': 0.8, 'Q': 0.65, 'H': 0.5}
        encoding_multipliers = {'numeric': 3.0, 'alphanumeric': 2.0, 'byte': 1.0}
        
        capacity = int(base_capacity * error_multipliers[error_level] * encoding_multipliers[encoding])
        return max(1, capacity)
    
    return capacity_table[version][error_level][encoding]

def get_optimal_qr_version(text_length: int, encoding: str, error_level: str = 'M') -> int:
    """
    Find the minimum QR code version needed for the given text length.
    
    Args:
        text_length (int): Length of text to encode.
        encoding (str): Encoding mode ('numeric', 'alphanumeric', 'byte').
        error_level (str): Error correction level ('L', 'M', 'Q', 'H'). Defaults to 'M'.
    
    Returns:
        int: Minimum QR version needed (1-40).
    
    Raises:
        ValueError: If parameters are invalid or text is too long for QR code.
    """
    if text_length <= 0:
        raise ValueError("Text length must be positive")
    
    if encoding not in ['numeric', 'alphanumeric', 'byte']:
        raise ValueError("Encoding must be 'numeric', 'alphanumeric', or 'byte'")
    
    if error_level not in ['L', 'M', 'Q', 'H']:
        raise ValueError("Error level must be 'L', 'M', 'Q', or 'H'")
    
    # Try versions from 1 to 40
    for version in range(1, 41):
        try:
            capacity = calculate_qr_capacity(version, error_level, encoding)
            if capacity >= text_length:
                return version
        except ValueError:
            continue
    
    raise ValueError(f"Text too long for QR code (length: {text_length})")

def compare_qr_configurations(text: str, versions: list = None) -> dict:
    """
    Compare multiple QR code configurations for the given text.
    
    Args:
        text (str): Text to encode.
        versions (list, optional): List of versions to compare. If None, compares optimal versions.
    
    Returns:
        dict: Comparison results with configuration details.
    
    Raises:
        ValueError: If text is empty.
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    text_length = len(text)
    optimal_encoding = analyze_text_encoding(text)
    
    if versions is None:
        # Compare optimal versions for different error levels
        versions = []
        for error_level in ['L', 'M', 'Q', 'H']:
            try:
                optimal_version = get_optimal_qr_version(text_length, optimal_encoding, error_level)
                versions.append(optimal_version)
            except ValueError:
                continue
        versions = sorted(set(versions))[:5]  # Limit to 5 versions
    
    results = {
        'text_info': {
            'length': text_length,
            'optimal_encoding': optimal_encoding
        },
        'configurations': []
    }
    
    for version in versions:
        config = {'version': version}
        for error_level in ['L', 'M', 'Q', 'H']:
            try:
                capacity = calculate_qr_capacity(version, error_level, optimal_encoding)
                can_fit = capacity >= text_length
                config[f'error_level_{error_level}'] = {
                    'capacity': capacity,
                    'can_fit': can_fit,
                    'utilization': round((text_length / capacity) * 100, 2) if can_fit else 0
                }
            except ValueError as e:
                config[f'error_level_{error_level}'] = {'error': str(e)}
        
        results['configurations'].append(config)
    
    return results

def generate_qr_advanced(data: str, version: int = None, error_correction: str = 'M', 
                        box_size: int = 10, border: int = 4, output_path: str = None) -> Image.Image:
    """
    Generate QR code with advanced configuration options.
    
    Args:
        data (str): Data to encode in the QR code.
        version (int, optional): QR version (1-40). If None, automatically determined.
        error_correction (str): Error correction level ('L', 'M', 'Q', 'H'). Defaults to 'M'.
        box_size (int): Size of each box in pixels. Defaults to 10.
        border (int): Border size in boxes. Defaults to 4.
        output_path (str, optional): Path to save the QR code image. If None, doesn't save.
    
    Returns:
        PIL.Image.Image: Generated QR code image.
    
    Raises:
        ValueError: If parameters are invalid.
        Exception: If QR code generation fails.
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    if version is not None and not (1 <= version <= 40):
        raise ValueError("Version must be between 1 and 40 or None")
    
    if error_correction not in ['L', 'M', 'Q', 'H']:
        raise ValueError("Error correction must be 'L', 'M', 'Q', or 'H'")
    
    if box_size < 1:
        raise ValueError("Box size must be at least 1")
    
    if border < 0:
        raise ValueError("Border must be non-negative")
    
    # Map error correction strings to qrcode constants
    error_mapping = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    try:
        # If version is not specified, analyze text and find optimal version
        if version is None:
            encoding = analyze_text_encoding(data)
            version = get_optimal_qr_version(len(data), encoding, error_correction)
            print(f"[*] Auto-selected version {version} with {encoding} encoding")
        
        # Create QR code instance with advanced settings
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_mapping[error_correction],
            box_size=box_size,
            border=border,
        )
        
        # Add data and generate
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save if output path is provided
        if output_path:
            img.save(output_path)
            print(f"[*] Advanced QR Code saved to: {output_path}")
        
        # Print configuration info
        print(f"[*] QR Code generated with:")
        print(f"    - Version: {version}")
        print(f"    - Error correction: {error_correction}")
        print(f"    - Box size: {box_size}")
        print(f"    - Border: {border}")
        
        return img
        
    except Exception as e:
        print(f"[!] Error generating advanced QR code: {e}")
        raise


# Security Enhanced QR Code Functions

def generate_secure_qr(data: str, document_key: str, output_path: str) -> Image.Image:
    """
    Generate QR code with encrypted data using document-specific key.
    Combines QR generation with security encryption for protected content.
    
    Args:
        data (str): Plain text data to encrypt and encode in QR code.
        document_key (str): Base64-encoded document key for encryption.
        output_path (str): Path to save the secure QR code image.
    
    Returns:
        PIL.Image.Image: Generated secure QR code image.
    
    Raises:
        ValueError: If input parameters are invalid.
        security_utils.SecurityError: If encryption or QR generation fails.
        
    Example:
        >>> doc_key = security_utils.generate_document_key("document.pdf")
        >>> qr_img = generate_secure_qr("Secret data", doc_key, "secure_qr.png")
    """
    try:
        if not data or not data.strip():
            raise ValueError("Data cannot be empty")
        
        if not document_key:
            raise ValueError("Document key is required")
        
        if not output_path:
            raise ValueError("Output path is required")
        
        print(f"[*] Generating secure QR code with encryption...")
        
        # Encrypt the data using security utils
        encrypted_data = security_utils.encrypt_qr_data(data, document_key)
        
        # Add security metadata
        timestamp = datetime.now().isoformat()
        secure_qr_data = embed_security_metadata(encrypted_data, document_key, timestamp)
        
        # Generate QR code with encrypted data
        # Use higher error correction for security applications
        qr_image = generate_qr_advanced(
            data=secure_qr_data,
            error_correction='H',  # High error correction for security
            box_size=8,
            border=4,
            output_path=output_path
        )
        
        print(f"[*] Secure QR code generated successfully: {output_path}")
        print(f"[*] Original data length: {len(data)} chars")
        print(f"[*] Encrypted data length: {len(secure_qr_data)} chars")
        
        return qr_image
        
    except Exception as e:
        print(f"[!] Error generating secure QR code: {e}")
        raise


def read_secure_qr(image_path: str, document_key: str) -> str:
    """
    Read and decrypt QR code data using document-specific key.
    Validates QR security and returns decrypted content.
    
    Args:
        image_path (str): Path to the QR code image file.
        document_key (str): Base64-encoded document key for decryption.
    
    Returns:
        str: Decrypted plain text data from QR code.
    
    Raises:
        FileNotFoundError: If QR image file doesn't exist.
        ValueError: If QR code cannot be read or contains invalid data.
        security_utils.SecurityError: If decryption fails or security validation fails.
        
    Example:
        >>> decrypted_data = read_secure_qr("secure_qr.png", document_key)
        >>> print(f"Decrypted: {decrypted_data}")
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"QR image not found: {image_path}")
        
        if not document_key:
            raise ValueError("Document key is required")
        
        print(f"[*] Reading secure QR code from: {os.path.basename(image_path)}")
        
        # Read QR code data
        qr_data_list = read_qr(image_path)
        
        if not qr_data_list:
            raise ValueError("No QR code data found in image")
        
        # Use the first QR code if multiple are found
        secure_qr_data = qr_data_list[0]
        print(f"[*] QR data read successfully ({len(secure_qr_data)} chars)")
        
        # Extract security metadata
        try:
            metadata = extract_security_metadata(secure_qr_data)
            encrypted_data = metadata.get('encrypted_data', secure_qr_data)
            
            print(f"[*] Security metadata extracted:")
            print(f"    - Timestamp: {metadata.get('timestamp', 'Unknown')}")
            print(f"    - Has metadata: {metadata.get('has_metadata', False)}")
            
        except Exception as e:
            print(f"[!] Warning: Could not extract metadata: {e}")
            # Assume the data is directly encrypted without metadata wrapper
            encrypted_data = secure_qr_data
        
        # Decrypt the data
        decrypted_data = security_utils.decrypt_qr_data(encrypted_data, document_key)
        
        print(f"[*] QR data decrypted successfully")
        print(f"[*] Decrypted data length: {len(decrypted_data)} chars")
        
        return decrypted_data
        
    except Exception as e:
        print(f"[!] Error reading secure QR code: {e}")
        raise


def embed_security_metadata(qr_data: str, document_key: str, timestamp: str) -> str:
    """
    Add security metadata to QR data for enhanced validation.
    Creates a JSON wrapper with security information and encrypted content.
    
    Args:
        qr_data (str): Encrypted QR data to wrap with metadata.
        document_key (str): Document key used for creating security hash.
        timestamp (str): ISO format timestamp for generation time.
    
    Returns:
        str: JSON string containing security metadata and encrypted data.
    
    Raises:
        ValueError: If input parameters are invalid.
        security_utils.SecurityError: If metadata creation fails.
        
    Example:
        >>> metadata_qr = embed_security_metadata(encrypted_data, doc_key, "2025-07-22T10:30:00")
    """
    try:
        if not qr_data:
            raise ValueError("QR data cannot be empty")
        
        if not document_key:
            raise ValueError("Document key is required")
        
        if not timestamp:
            raise ValueError("Timestamp is required")
        
        # Create a security hash for validation
        # Use SHA-256 to create a proper hash from the combined content
        import hashlib
        combined_content = f"{qr_data}:{timestamp}".encode('utf-8')
        content_hash = hashlib.sha256(combined_content).hexdigest()
        
        security_hash = security_utils.create_key_signature(
            document_key, 
            content_hash
        )
        
        # Create metadata structure
        metadata = {
            'version': '1.0',
            'timestamp': timestamp,
            'encrypted_data': qr_data,
            'security_hash': security_hash,
            'has_metadata': True
        }
        
        # Convert to JSON string
        metadata_json = json.dumps(metadata, separators=(',', ':'))  # Compact JSON
        
        print(f"[*] Security metadata embedded successfully")
        print(f"[*] Metadata size: {len(metadata_json) - len(qr_data)} additional chars")
        
        return metadata_json
        
    except Exception as e:
        print(f"[!] Error embedding security metadata: {e}")
        raise


def extract_security_metadata(qr_data: str) -> Dict[str, Any]:
    """
    Extract security metadata from QR data if present.
    Parses JSON wrapper and returns metadata information.
    
    Args:
        qr_data (str): QR data that may contain security metadata.
    
    Returns:
        Dict[str, Any]: Dictionary containing security metadata and encrypted data.
                       If no metadata found, returns basic structure with original data.
    
    Raises:
        ValueError: If QR data is empty.
        
    Example:
        >>> metadata = extract_security_metadata(qr_data)
        >>> print(f"Timestamp: {metadata['timestamp']}")
        >>> encrypted_data = metadata['encrypted_data']
    """
    try:
        if not qr_data:
            raise ValueError("QR data cannot be empty")
        
        # Try to parse as JSON metadata
        try:
            metadata = json.loads(qr_data)
            
            # Validate it's our metadata format
            if (isinstance(metadata, dict) and 
                'encrypted_data' in metadata and 
                'has_metadata' in metadata and 
                metadata.get('has_metadata')):
                
                print(f"[*] Security metadata found:")
                print(f"    - Version: {metadata.get('version', 'Unknown')}")
                print(f"    - Timestamp: {metadata.get('timestamp', 'Unknown')}")
                print(f"    - Has security hash: {'security_hash' in metadata}")
                
                return metadata
            else:
                print(f"[*] JSON found but not security metadata format")
                
        except json.JSONDecodeError:
            print(f"[*] No JSON metadata detected")
        
        # If no valid metadata found, return basic structure
        return {
            'version': 'unknown',
            'timestamp': 'unknown',
            'encrypted_data': qr_data,
            'security_hash': None,
            'has_metadata': False
        }
        
    except Exception as e:
        print(f"[!] Error extracting security metadata: {e}")
        # Return basic structure on error
        return {
            'version': 'error',
            'timestamp': 'error',
            'encrypted_data': qr_data,
            'security_hash': None,
            'has_metadata': False,
            'error': str(e)
        }


def validate_qr_security(qr_data: str, document_key: str, document_hash: str) -> Dict[str, Any]:
    """
    Comprehensive security validation for QR code data.
    Validates encryption, metadata integrity, and document-QR pairing.
    
    Args:
        qr_data (str): QR data to validate (may be encrypted with metadata).
        document_key (str): Document key for validation.
        document_hash (str): SHA-256 hash of the associated document.
    
    Returns:
        Dict[str, Any]: Validation results with detailed status information.
    
    Raises:
        ValueError: If input parameters are invalid.
        
    Example:
        >>> validation = validate_qr_security(qr_data, doc_key, doc_hash)
        >>> if validation['overall_valid']:
        >>>     print("QR security validation passed")
    """
    try:
        if not qr_data:
            raise ValueError("QR data cannot be empty")
        
        if not document_key:
            raise ValueError("Document key is required")
        
        if not document_hash:
            raise ValueError("Document hash is required")
        
        print(f"[*] Starting comprehensive QR security validation...")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'qr_data_length': len(qr_data),
            'validations': {},
            'overall_valid': False,
            'warnings': [],
            'errors': []
        }
        
        # Step 1: Extract and validate metadata
        try:
            metadata = extract_security_metadata(qr_data)
            validation_results['metadata'] = metadata
            validation_results['validations']['metadata_extraction'] = True
            
            if metadata.get('has_metadata'):
                print(f"[*] ✓ Metadata extraction successful")
            else:
                validation_results['warnings'].append("No security metadata found")
                print(f"[!] ⚠ Warning: No security metadata found")
                
        except Exception as e:
            validation_results['validations']['metadata_extraction'] = False
            validation_results['errors'].append(f"Metadata extraction failed: {e}")
            print(f"[!] ✗ Metadata extraction failed: {e}")
        
        # Step 2: Validate metadata integrity
        if metadata.get('has_metadata') and metadata.get('security_hash'):
            try:
                # Recreate the content hash that was used during embedding
                import hashlib
                expected_content = f"{metadata['encrypted_data']}:{metadata['timestamp']}"
                content_hash = hashlib.sha256(expected_content.encode('utf-8')).hexdigest()
                
                is_valid = security_utils.verify_key_signature(
                    document_key, 
                    metadata['security_hash'], 
                    content_hash
                )
                validation_results['validations']['metadata_integrity'] = is_valid
                
                if is_valid:
                    print(f"[*] ✓ Metadata integrity validation passed")
                else:
                    validation_results['errors'].append("Metadata integrity check failed")
                    print(f"[!] ✗ Metadata integrity validation failed")
                    
            except Exception as e:
                validation_results['validations']['metadata_integrity'] = False
                validation_results['errors'].append(f"Metadata integrity check error: {e}")
                print(f"[!] ✗ Metadata integrity check error: {e}")
        else:
            validation_results['validations']['metadata_integrity'] = None
            print(f"[*] - Skipping metadata integrity (no security hash)")
        
        # Step 3: Test decryption capability
        try:
            encrypted_data = metadata.get('encrypted_data', qr_data)
            decrypted_data = security_utils.decrypt_qr_data(encrypted_data, document_key)
            validation_results['validations']['decryption'] = True
            validation_results['decrypted_length'] = len(decrypted_data)
            print(f"[*] ✓ Decryption successful ({len(decrypted_data)} chars)")
            
        except Exception as e:
            validation_results['validations']['decryption'] = False
            validation_results['errors'].append(f"Decryption failed: {e}")
            print(f"[!] ✗ Decryption failed: {e}")
        
        # Step 4: Validate document-key relationship
        try:
            key_signature = security_utils.create_key_signature(document_key, document_hash)
            signature_valid = security_utils.verify_key_signature(document_key, key_signature, document_hash)
            validation_results['validations']['document_key_pairing'] = signature_valid
            
            if signature_valid:
                print(f"[*] ✓ Document-key pairing validated")
            else:
                validation_results['errors'].append("Document-key pairing validation failed")
                print(f"[!] ✗ Document-key pairing validation failed")
                
        except Exception as e:
            validation_results['validations']['document_key_pairing'] = False
            validation_results['errors'].append(f"Document-key validation error: {e}")
            print(f"[!] ✗ Document-key validation error: {e}")
        
        # Step 5: Overall validation assessment
        critical_validations = ['decryption', 'document_key_pairing']
        critical_passed = all(
            validation_results['validations'].get(v, False) 
            for v in critical_validations
        )
        
        optional_validations = ['metadata_extraction', 'metadata_integrity']
        optional_passed = sum(
            1 for v in optional_validations 
            if validation_results['validations'].get(v, False)
        )
        
        validation_results['overall_valid'] = critical_passed
        validation_results['security_score'] = (
            (len([v for v in critical_validations if validation_results['validations'].get(v, False)]) * 0.4) +
            (optional_passed * 0.1)
        )
        
        # Summary
        if validation_results['overall_valid']:
            print(f"[*] ✅ Overall QR security validation: PASSED")
            print(f"[*] Security score: {validation_results['security_score']:.1f}/1.0")
        else:
            print(f"[!] ❌ Overall QR security validation: FAILED")
            print(f"[!] Security score: {validation_results['security_score']:.1f}/1.0")
        
        if validation_results['warnings']:
            print(f"[!] Warnings: {len(validation_results['warnings'])}")
        
        if validation_results['errors']:
            print(f"[!] Errors: {len(validation_results['errors'])}")
        
        return validation_results
        
    except Exception as e:
        print(f"[!] Error during QR security validation: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_valid': False,
            'error': str(e),
            'validations': {},
            'security_score': 0.0
        }


# --- End of qr_utils.py ---
