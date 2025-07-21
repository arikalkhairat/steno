# File: qr_utils.py
# Deskripsi: Fungsi utilitas untuk membuat dan membaca QR Code.

import qrcode
import cv2
from PIL import Image
import os

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

# --- End of qr_utils.py ---
