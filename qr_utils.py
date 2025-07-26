# File: qr_utils.py
# Deskripsi: Fungsi utilitas untuk membuat dan membaca QR Code dengan fitur analisis lanjutan.

import qrcode
import cv2
from PIL import Image
import os
import math
from typing import Dict, Tuple, List, Optional, Union
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# QR Code capacity tables for different modes and error correction levels
QR_CAPACITY_NUMERIC = {
    1: {'L': 41, 'M': 34, 'Q': 27, 'H': 17},
    2: {'L': 77, 'M': 63, 'Q': 48, 'H': 34},
    3: {'L': 127, 'M': 101, 'Q': 77, 'H': 58},
    4: {'L': 187, 'M': 149, 'Q': 111, 'H': 82},
    5: {'L': 255, 'M': 202, 'Q': 144, 'H': 106},
    6: {'L': 322, 'M': 255, 'Q': 178, 'H': 139},
    7: {'L': 370, 'M': 293, 'Q': 207, 'H': 154},
    8: {'L': 461, 'M': 365, 'Q': 259, 'H': 202},
    9: {'L': 552, 'M': 432, 'Q': 312, 'H': 235},
    10: {'L': 652, 'M': 513, 'Q': 364, 'H': 288}
}

QR_CAPACITY_ALPHANUMERIC = {
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

QR_CAPACITY_BYTE = {
    1: {'L': 17, 'M': 14, 'Q': 11, 'H': 7},
    2: {'L': 32, 'M': 26, 'Q': 20, 'H': 14},
    3: {'L': 53, 'M': 42, 'Q': 32, 'H': 24},
    4: {'L': 78, 'M': 62, 'Q': 46, 'H': 34},
    5: {'L': 106, 'M': 84, 'Q': 60, 'H': 44},
    6: {'L': 134, 'M': 106, 'Q': 74, 'H': 58},
    7: {'L': 154, 'M': 122, 'Q': 86, 'H': 64},
    8: {'L': 192, 'M': 152, 'Q': 108, 'H': 84},
    9: {'L': 230, 'M': 180, 'Q': 130, 'H': 98},
    10: {'L': 271, 'M': 213, 'Q': 151, 'H': 119}
}

def generate_qr(data: str, output_path: str, 
                error_correction: str = 'L',
                box_size: int = 10,
                border: int = 4,
                fill_color: str = "black",
                back_color: str = "white",
                return_metadata: bool = False) -> Union[None, Dict]:
    """
    Enhanced QR Code generation with comprehensive analysis and configuration options.

    Args:
        data (str): Data teks yang akan dikodekan
        output_path (str): Path file untuk menyimpan citra QR Code
        error_correction (str): Tingkat koreksi error ('L', 'M', 'Q', 'H')
        box_size (int): Ukuran setiap kotak dalam QR Code (default: 10)
        border (int): Lebar border di sekitar QR Code (default: 4)
        fill_color (str): Warna foreground QR Code (default: "black")
        back_color (str): Warna background QR Code (default: "white")
        return_metadata (bool): Return detailed metadata (default: False)

    Returns:
        Union[None, Dict]: None untuk backward compatibility, atau metadata jika return_metadata=True

    Raises:
        ValueError: Jika parameter tidak valid
        Exception: Jika terjadi error saat pembuatan QR Code

    Example:
        >>> generate_qr("Hello World", "qr.png", error_correction='M', box_size=8)
        >>> metadata = generate_qr("Test", "qr.png", return_metadata=True)
        >>> print(f"QR Version: {metadata['metadata']['version']}")
    """
    try:
        # Validasi parameter
        if not data:
            raise ValueError("Data tidak boleh kosong")
        
        if error_correction not in ['L', 'M', 'Q', 'H']:
            raise ValueError("Error correction harus 'L', 'M', 'Q', atau 'H'")
        
        if box_size < 1 or box_size > 50:
            raise ValueError("Box size harus antara 1-50")
        
        if border < 0 or border > 20:
            raise ValueError("Border harus antara 0-20")

        # Konversi error correction ke konstanta qrcode
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }

        # Membuat instance QRCode dengan parameter yang dapat dikonfigurasi
        qr = qrcode.QRCode(
            version=None,  # Auto-determine optimal version
            error_correction=error_levels[error_correction],
            box_size=box_size,
            border=border,
        )
        
        # Menambahkan data dan membuat QR Code
        qr.add_data(data)
        qr.make(fit=True)

        # Membuat citra dengan warna kustom
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Menyimpan citra ke file
        img.save(output_path)
        logger.info(f"QR Code berhasil dibuat dan disimpan di: {output_path}")

        # Jika metadata diperlukan, generate dan return
        if return_metadata:
            metadata = _generate_metadata(qr, img, data, error_correction, output_path)
            return {
                "success": True,
                "qr_path": output_path,
                "metadata": metadata
            }

    except Exception as e:
        logger.error(f"Error saat membuat QR Code: {e}")
        if return_metadata:
            return {
                "success": False,
                "error": str(e),
                "qr_path": None,
                "metadata": None
            }
        raise

def analyze_qr_requirements(data: str) -> Dict:
    """
    Analyze QR code requirements without generating the actual image.
    
    Args:
        data (str): Data yang akan dianalisis
    
    Returns:
        Dict: Comprehensive analysis of QR requirements
        
    Example:
        >>> analysis = analyze_qr_requirements("Hello World!")
        >>> print(f"Recommended version: {analysis['recommended_version']}")
        >>> print(f"Steganography compatible: {analysis['steganography_compatible']}")
    """
    try:
        if not data:
            raise ValueError("Data tidak boleh kosong")

        data_length = len(data)
        
        # Determine data mode (numeric, alphanumeric, or byte)
        data_mode = _determine_data_mode(data)
        
        # Get capacity table based on data mode
        capacity_table = _get_capacity_table(data_mode)
        
        # Find minimum version for each error correction level
        version_analysis = {}
        for ec_level in ['L', 'M', 'Q', 'H']:
            min_version = _find_minimum_version(data_length, ec_level, capacity_table)
            if min_version:
                capacity = capacity_table.get(min_version, {}).get(ec_level, 0)
                usage_percent = (data_length / capacity) * 100 if capacity > 0 else 100
                
                version_analysis[ec_level] = {
                    'minimum_version': min_version,
                    'capacity': capacity,
                    'usage_percent': round(usage_percent, 1),
                    'recommended': usage_percent <= 80  # Recommend if usage < 80%
                }
            else:
                version_analysis[ec_level] = {
                    'minimum_version': None,
                    'capacity': 0,
                    'usage_percent': 100,
                    'recommended': False
                }

        # Determine best error correction level
        recommended_ec = _recommend_error_correction(version_analysis)
        recommended_version = version_analysis[recommended_ec]['minimum_version'] if recommended_ec else 1
        
        # Calculate steganography compatibility
        stego_analysis = _analyze_steganography_compatibility(data_length, recommended_version)
        
        # Generate recommendations
        recommendations = _generate_recommendations(data_length, version_analysis, stego_analysis)

        return {
            'data_length': data_length,
            'data_mode': data_mode,
            'recommended_version': recommended_version,
            'recommended_error_correction': recommended_ec,
            'version_analysis': version_analysis,
            'steganography_analysis': stego_analysis,
            'steganography_compatible': stego_analysis['compatibility_score'] >= 70,
            'recommendations': recommendations,
            'analysis_timestamp': None  # Could add timestamp if needed
        }

    except Exception as e:
        logger.error(f"Error dalam analisis QR requirements: {e}")
        return {
            'error': str(e),
            'data_length': len(data) if data else 0,
            'recommendations': ['Terjadi error dalam analisis, periksa input data']
        }

def estimate_steganography_capacity(qr_size: Tuple[int, int], 
                                   target_image_size: Tuple[int, int] = (800, 600)) -> Dict:
    """
    Estimate how well a QR code fits in typical document images for steganography.
    
    Args:
        qr_size (Tuple[int, int]): Ukuran QR code (width, height) dalam piksel
        target_image_size (Tuple[int, int]): Ukuran target gambar dokumen
    
    Returns:
        Dict: Analysis of steganographic embedding capacity
        
    Example:
        >>> capacity = estimate_steganography_capacity((290, 290), (1024, 768))
        >>> print(f"Embedding ratio: {capacity['embedding_ratio']:.2%}")
    """
    try:
        qr_width, qr_height = qr_size
        target_width, target_height = target_image_size
        
        if qr_width <= 0 or qr_height <= 0:
            raise ValueError("QR size harus lebih besar dari 0")
        
        if target_width <= 0 or target_height <= 0:
            raise ValueError("Target image size harus lebih besar dari 0")

        # Calculate basic metrics
        qr_pixels = qr_width * qr_height
        target_pixels = target_width * target_height
        embedding_ratio = qr_pixels / target_pixels
        
        # Calculate optimal embedding areas (avoid corners and edges)
        safe_width = target_width * 0.8  # 80% of width is safe for embedding
        safe_height = target_height * 0.8  # 80% of height is safe for embedding
        safe_pixels = safe_width * safe_height
        safe_embedding_ratio = qr_pixels / safe_pixels
        
        # Determine compatibility level
        if safe_embedding_ratio <= 0.01:  # QR uses ≤1% of safe area
            compatibility = "Excellent"
            score = 95
        elif safe_embedding_ratio <= 0.05:  # QR uses ≤5% of safe area
            compatibility = "Good"
            score = 80
        elif safe_embedding_ratio <= 0.15:  # QR uses ≤15% of safe area
            compatibility = "Fair"
            score = 60
        else:  # QR uses >15% of safe area
            compatibility = "Poor"
            score = 30

        # Estimate LSB embedding capacity
        # Assuming 1 bit per pixel for LSB steganography
        available_lsb_bits = target_pixels * 3  # RGB channels
        qr_bits_needed = qr_pixels  # 1 bit per QR pixel (black/white)
        lsb_utilization = qr_bits_needed / available_lsb_bits
        
        # Calculate quality impact estimation
        quality_impact = _estimate_quality_impact(embedding_ratio, qr_size)
        
        return {
            'qr_size': qr_size,
            'target_size': target_image_size,
            'qr_pixels': qr_pixels,
            'target_pixels': target_pixels,
            'embedding_ratio': embedding_ratio,
            'safe_embedding_ratio': safe_embedding_ratio,
            'compatibility_level': compatibility,
            'compatibility_score': score,
            'lsb_capacity_bits': available_lsb_bits,
            'qr_bits_needed': qr_bits_needed,
            'lsb_utilization': lsb_utilization,
            'quality_impact': quality_impact,
            'recommendations': _generate_steganography_recommendations(compatibility, embedding_ratio)
        }

    except Exception as e:
        logger.error(f"Error dalam estimasi steganography capacity: {e}")
        return {
            'error': str(e),
            'compatibility_level': 'Unknown',
            'compatibility_score': 0,
            'recommendations': ['Error dalam analisis kapasitas steganografi']
        }

def get_capacity_info(data_length: int, error_correction: str = 'M') -> Dict:
    """
    Get comprehensive capacity information for different error correction levels.
    
    Args:
        data_length (int): Panjang data dalam karakter
        error_correction (str): Level error correction saat ini ('L', 'M', 'Q', 'H')
    
    Returns:
        Dict: Detailed capacity analysis for all error correction levels
        
    Example:
        >>> info = get_capacity_info(150, 'M')
        >>> print(f"Current usage: {info['current_level']['usage_percent']:.1f}%")
        >>> print(f"Alternative: {info['alternatives']['L']['capacity']} chars")
    """
    try:
        if data_length < 0:
            raise ValueError("Data length tidak boleh negatif")
        
        if error_correction not in ['L', 'M', 'Q', 'H']:
            raise ValueError("Error correction harus 'L', 'M', 'Q', atau 'H'")

        # Determine data mode
        data_mode = "byte"  # Conservative assumption for mixed content
        capacity_table = _get_capacity_table(data_mode)
        
        # Analyze all error correction levels
        level_analysis = {}
        for ec_level in ['L', 'M', 'Q', 'H']:
            min_version = _find_minimum_version(data_length, ec_level, capacity_table)
            
            if min_version and min_version <= 10:  # Focus on versions 1-10 for practical use
                capacity = capacity_table[min_version][ec_level]
                usage_percent = (data_length / capacity) * 100
                
                # Calculate QR dimensions (approximate)
                module_count = 17 + 4 * min_version  # QR formula: 17 + 4 * version
                
                level_analysis[ec_level] = {
                    'version': min_version,
                    'capacity': capacity,
                    'usage_percent': round(usage_percent, 1),
                    'remaining_capacity': capacity - data_length,
                    'module_count': module_count,
                    'error_correction_percent': {'L': 7, 'M': 15, 'Q': 25, 'H': 30}[ec_level],
                    'recommended': 50 <= usage_percent <= 80,  # Sweet spot for capacity usage
                    'status': _get_capacity_status(usage_percent)
                }
            else:
                level_analysis[ec_level] = {
                    'version': None,
                    'capacity': 0,
                    'usage_percent': 100,
                    'remaining_capacity': 0,
                    'module_count': 0,
                    'error_correction_percent': {'L': 7, 'M': 15, 'Q': 25, 'H': 30}[ec_level],
                    'recommended': False,
                    'status': 'Data terlalu panjang'
                }

        # Current level analysis
        current_level = level_analysis.get(error_correction, {})
        
        # Find best alternative
        best_alternative = None
        best_score = 0
        for level, analysis in level_analysis.items():
            if level != error_correction and analysis['recommended']:
                # Score based on capacity efficiency and error correction strength
                efficiency_score = 100 - abs(analysis['usage_percent'] - 65)  # Target 65% usage
                error_strength = analysis['error_correction_percent']
                combined_score = efficiency_score + (error_strength * 0.5)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_alternative = level

        return {
            'data_length': data_length,
            'current_error_correction': error_correction,
            'current_level': current_level,
            'all_levels': level_analysis,
            'best_alternative': best_alternative,
            'alternatives': {k: v for k, v in level_analysis.items() if k != error_correction},
            'summary': {
                'optimal_version': current_level.get('version'),
                'capacity_utilization': current_level.get('usage_percent', 0),
                'steganography_friendly': current_level.get('usage_percent', 100) <= 75,
                'upgrade_recommended': best_alternative is not None
            }
        }

    except Exception as e:
        logger.error(f"Error dalam get_capacity_info: {e}")
        return {
            'error': str(e),
            'data_length': data_length,
            'current_error_correction': error_correction,
            'summary': {'error': True}
        }


# ===============================
# HELPER FUNCTIONS
# ===============================

def _generate_metadata(qr, img, data: str, error_correction: str, output_path: str) -> Dict:
    """Generate comprehensive metadata for QR code."""
    try:
        data_length = len(data)
        version = qr.version
        
        # Calculate module count and dimensions
        module_count = 17 + 4 * version  # QR formula
        pixel_width = img.width
        pixel_height = img.height
        
        # Get capacity information
        capacity_info = get_capacity_info(data_length, error_correction)
        current_capacity = capacity_info['current_level'].get('capacity', 0)
        
        # Calculate usage percentage
        capacity_used = (data_length / current_capacity * 100) if current_capacity > 0 else 100
        
        # Estimate steganography capacity
        stego_capacity = estimate_steganography_capacity((pixel_width, pixel_height))
        
        # Generate recommendations
        recommendations = []
        if capacity_used > 80:
            recommendations.append("Pertimbangkan untuk mengurangi panjang data")
        if stego_capacity['compatibility_score'] < 70:
            recommendations.append("QR Code mungkin terlalu besar untuk steganografi optimal")
        if error_correction == 'L' and data_length > 100:
            recommendations.append("Pertimbangkan error correction level yang lebih tinggi")
        
        return {
            'version': version,
            'size_pixels': f"{pixel_width}x{pixel_height}",
            'module_count': f"{module_count}x{module_count}",
            'data_length': data_length,
            'error_correction': error_correction,
            'capacity_used': round(capacity_used, 1),
            'max_capacity': current_capacity,
            'estimated_embedding_capacity': stego_capacity.get('lsb_capacity_bits', 0),
            'steganography_compatible': stego_capacity.get('compatibility_score', 0) >= 70,
            'steganography_score': stego_capacity.get('compatibility_score', 0),
            'quality_impact': stego_capacity.get('quality_impact', {}),
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Error generating metadata: {e}")
        return {'error': str(e)}

def _determine_data_mode(data: str) -> str:
    """Determine the most efficient QR data mode for given data."""
    if data.isdigit():
        return "numeric"
    elif all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:=" for c in data.upper()):
        return "alphanumeric"
    else:
        return "byte"

def _get_capacity_table(data_mode: str) -> Dict:
    """Get capacity table for specified data mode."""
    tables = {
        "numeric": QR_CAPACITY_NUMERIC,
        "alphanumeric": QR_CAPACITY_ALPHANUMERIC,
        "byte": QR_CAPACITY_BYTE
    }
    return tables.get(data_mode, QR_CAPACITY_BYTE)

def _find_minimum_version(data_length: int, error_correction: str, capacity_table: Dict) -> Optional[int]:
    """Find minimum QR version that can accommodate the data."""
    for version in range(1, 11):  # Focus on versions 1-10 for practical use
        if version in capacity_table:
            capacity = capacity_table[version].get(error_correction, 0)
            if capacity >= data_length:
                return version
    return None

def _recommend_error_correction(version_analysis: Dict) -> Optional[str]:
    """Recommend best error correction level based on analysis."""
    # Priority: M > Q > L > H (balance between reliability and capacity)
    priority_order = ['M', 'Q', 'L', 'H']
    
    for ec_level in priority_order:
        if ec_level in version_analysis and version_analysis[ec_level]['recommended']:
            return ec_level
    
    # If no recommended level, return the one with lowest version
    min_version = float('inf')
    best_level = None
    
    for ec_level, analysis in version_analysis.items():
        if analysis['minimum_version'] and analysis['minimum_version'] < min_version:
            min_version = analysis['minimum_version']
            best_level = ec_level
    
    return best_level

def _analyze_steganography_compatibility(data_length: int, qr_version: Optional[int]) -> Dict:
    """Analyze steganography compatibility based on data length and QR version."""
    if not qr_version:
        return {
            'compatibility_score': 0,
            'level': 'Poor',
            'concerns': ['QR code tidak dapat dibuat dengan data ini']
        }
    
    # Calculate estimated pixel size
    module_count = 17 + 4 * qr_version
    estimated_pixels = (module_count * 10 + 8) ** 2  # Assuming 10px box_size + border
    
    concerns = []
    
    # Analyze based on data length
    if data_length <= 50:
        length_score = 90
    elif data_length <= 100:
        length_score = 75
    elif data_length <= 200:
        length_score = 60
        concerns.append("Data agak panjang, mungkin mempengaruhi kualitas embedding")
    else:
        length_score = 30
        concerns.append("Data terlalu panjang untuk steganografi optimal")
    
    # Analyze based on QR version/size
    if qr_version <= 3:
        size_score = 95
    elif qr_version <= 5:
        size_score = 80
    elif qr_version <= 7:
        size_score = 65
        concerns.append("QR code berukuran sedang, perhatikan ukuran gambar target")
    else:
        size_score = 40
        concerns.append("QR code besar, mungkin sulit disembunyikan")
    
    # Combined score
    compatibility_score = (length_score + size_score) / 2
    
    if compatibility_score >= 85:
        level = 'Excellent'
    elif compatibility_score >= 70:
        level = 'Good'
    elif compatibility_score >= 50:
        level = 'Fair'
    else:
        level = 'Poor'
    
    return {
        'compatibility_score': round(compatibility_score, 1),
        'level': level,
        'length_score': length_score,
        'size_score': size_score,
        'estimated_pixels': estimated_pixels,
        'concerns': concerns
    }

def _generate_recommendations(data_length: int, version_analysis: Dict, stego_analysis: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    # Data length recommendations
    if data_length <= 50:
        recommendations.append("✓ Panjang data optimal untuk steganografi")
    elif data_length <= 100:
        recommendations.append("• Data dalam batas baik, pertimbangkan kompresi jika memungkinkan")
    elif data_length <= 200:
        recommendations.append("⚠ Pertimbangkan untuk mempersingkat data atau menggunakan singkatan")
    else:
        recommendations.append("❌ Data terlalu panjang, sangat disarankan untuk mempersingkat")
    
    # Error correction recommendations
    recommended_ec = None
    for ec, analysis in version_analysis.items():
        if analysis.get('recommended', False):
            recommended_ec = ec
            break
    
    if recommended_ec:
        ec_names = {'L': 'Low', 'M': 'Medium', 'Q': 'Quartile', 'H': 'High'}
        recommendations.append(f"✓ Gunakan error correction level {recommended_ec} ({ec_names[recommended_ec]})")
    
    # Steganography recommendations
    if stego_analysis['compatibility_score'] >= 85:
        recommendations.append("✓ Sangat cocok untuk steganografi pada gambar berukuran standar")
    elif stego_analysis['compatibility_score'] >= 70:
        recommendations.append("• Cocok untuk steganografi, gunakan gambar dengan resolusi tinggi")
    else:
        recommendations.append("⚠ Gunakan gambar target berukuran besar atau kurangi data")
    
    return recommendations

def _estimate_quality_impact(embedding_ratio: float, qr_size: Tuple[int, int]) -> Dict:
    """Estimate quality impact of QR embedding on target image."""
    qr_pixels = qr_size[0] * qr_size[1]
    
    if embedding_ratio <= 0.01:
        impact_level = "Minimal"
        visual_change = "Tidak terlihat dengan mata biasa"
        psnr_estimate = ">40 dB"
    elif embedding_ratio <= 0.05:
        impact_level = "Low"
        visual_change = "Sedikit perubahan pada analisis detail"
        psnr_estimate = "35-40 dB"
    elif embedding_ratio <= 0.15:
        impact_level = "Moderate"
        visual_change = "Perubahan mungkin terlihat pada pemeriksaan teliti"
        psnr_estimate = "25-35 dB"
    else:
        impact_level = "High"
        visual_change = "Perubahan cukup terlihat"
        psnr_estimate = "<25 dB"
    
    return {
        'impact_level': impact_level,
        'visual_change': visual_change,
        'psnr_estimate': psnr_estimate,
        'embedding_ratio': embedding_ratio,
        'affected_pixels': qr_pixels
    }

def _generate_steganography_recommendations(compatibility: str, embedding_ratio: float) -> List[str]:
    """Generate specific recommendations for steganography."""
    recommendations = []
    
    if compatibility == "Excellent":
        recommendations.append("✓ Ideal untuk semua jenis gambar dokumen")
        recommendations.append("✓ Kualitas visual akan tetap terjaga")
    elif compatibility == "Good":
        recommendations.append("• Gunakan gambar dengan resolusi minimal 800x600")
        recommendations.append("• Hindari area dengan detail tinggi untuk embedding")
    elif compatibility == "Fair":
        recommendations.append("⚠ Gunakan gambar dengan resolusi tinggi (>1024x768)")
        recommendations.append("⚠ Pertimbangkan untuk mengurangi ukuran QR code")
    else:
        recommendations.append("❌ QR code terlalu besar untuk steganografi yang baik")
        recommendations.append("❌ Pertimbangkan kompresi data atau penggunaan gambar yang sangat besar")
    
    if embedding_ratio > 0.1:
        recommendations.append("• Pertimbangkan penggunaan multiple gambar untuk distribusi QR")
    
    return recommendations

def _get_capacity_status(usage_percent: float) -> str:
    """Get human-readable status for capacity usage."""
    if usage_percent <= 50:
        return "Kapasitas rendah - sangat aman"
    elif usage_percent <= 75:
        return "Kapasitas optimal - direkomendasikan"
    elif usage_percent <= 90:
        return "Kapasitas tinggi - masih aman"
    else:
        return "Kapasitas hampir penuh - perlu hati-hati"


# ===============================
# ORIGINAL FUNCTIONS (Backward Compatibility)
# ===============================

def read_qr(image_path: str) -> List[str]:
    """
    Membaca data dari sebuah citra QR Code menggunakan OpenCV.
    (Original function maintained for backward compatibility)

    Args:
        image_path (str): Path ke file citra QR Code.

    Returns:
        List[str]: List berisi data (string UTF-8) yang berhasil dibaca dari QR Code.
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
            logger.warning(f"Tidak ada QR Code yang terdeteksi di: {image_path}")
        return data_list
    except Exception as e:
        # Menangani potensi error saat membuka citra atau proses decoding
        logger.error(f"Error saat membaca QR Code: {e}")
        raise # Melempar kembali error


# ===============================
# NEW CONVENIENCE FUNCTIONS
# ===============================

def quick_qr_analysis(data: str, error_correction: str = 'M') -> Dict:
    """
    Quick analysis function that combines requirements analysis and capacity info.
    
    Args:
        data (str): Data untuk dianalisis
        error_correction (str): Error correction level
    
    Returns:
        Dict: Combined analysis results
    """
    try:
        requirements = analyze_qr_requirements(data)
        capacity = get_capacity_info(len(data), error_correction)
        
        return {
            'data_summary': {
                'length': len(data),
                'mode': requirements.get('data_mode', 'unknown'),
                'recommended_version': requirements.get('recommended_version'),
                'recommended_ec': requirements.get('recommended_error_correction')
            },
            'capacity_analysis': capacity,
            'steganography_analysis': requirements.get('steganography_analysis', {}),
            'overall_recommendation': requirements.get('recommendations', [])[:3],  # Top 3 recommendations
            'quick_status': {
                'steganography_ready': requirements.get('steganography_compatible', False),
                'capacity_efficient': capacity['summary'].get('capacity_utilization', 100) <= 80,
                'version_reasonable': requirements.get('recommended_version', 99) <= 5
            }
        }
    except Exception as e:
        logger.error(f"Error in quick_qr_analysis: {e}")
        return {'error': str(e)}

def generate_qr_with_analysis(data: str, output_path: str, **kwargs) -> Dict:
    """
    Generate QR code with comprehensive analysis in one call.
    
    Args:
        data (str): Data untuk QR code
        output_path (str): Path output file
        **kwargs: Additional parameters for generate_qr
    
    Returns:
        Dict: Generation result with complete analysis
    """
    try:
        # Generate QR with metadata
        result = generate_qr(data, output_path, return_metadata=True, **kwargs)
        
        if result['success']:
            # Add comprehensive analysis
            analysis = quick_qr_analysis(data, kwargs.get('error_correction', 'M'))
            result['comprehensive_analysis'] = analysis
            
            # Add file info
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                result['file_info'] = {
                    'size_bytes': file_size,
                    'size_kb': round(file_size / 1024, 2)
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_qr_with_analysis: {e}")
        return {
            'success': False,
            'error': str(e),
            'qr_path': None
        }

# --- End of enhanced qr_utils.py ---
