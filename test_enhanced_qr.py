#!/usr/bin/env python3
"""
Test script to verify the enhanced QR Code generation functionality
"""

import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import os

def test_enhanced_qr_generation():
    """Test the enhanced QR generation with different parameters"""
    
    # Test data
    test_data = "Test QR Code for Steganography Enhancement"
    
    # Error correction levels
    error_levels = {
        'L': ERROR_CORRECT_L,
        'M': ERROR_CORRECT_M, 
        'Q': ERROR_CORRECT_Q,
        'H': ERROR_CORRECT_H
    }
    
    print("Testing Enhanced QR Code Generation")
    print("=" * 50)
    
    for level_name, level_constant in error_levels.items():
        print(f"\nTesting Error Correction Level: {level_name}")
        
        # Create QR code
        qr = qrcode.QRCode(
            version=None,  # Auto-determine version
            error_correction=level_constant,
            box_size=10,
            border=4,
        )
        
        qr.add_data(test_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Print analysis
        print(f"  Version: {qr.version}")
        print(f"  Dimensions: {img.width}×{img.height}")
        print(f"  Data Length: {len(test_data)} characters")
        print(f"  Capacity: {get_qr_capacity(qr.version, level_name)} characters")
        print(f"  Usage: {(len(test_data) / get_qr_capacity(qr.version, level_name) * 100):.1f}%")
        
        # Save test image
        filename = f"test_qr_{level_name.lower()}.png"
        filepath = os.path.join("static", "generated", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img.save(filepath)
        print(f"  Saved: {filepath}")

def get_qr_capacity(version, error_correction):
    """Get maximum character capacity for given QR version and error correction level"""
    # QR Code capacity table for alphanumeric mode (approximate values)
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
    
    # For versions beyond 10, use approximation
    if version <= 10:
        return capacities.get(version, {}).get(error_correction, 100)
    else:
        # Rough approximation for higher versions
        base_capacity = capacities[10][error_correction]
        return int(base_capacity * (1 + (version - 10) * 0.3))

def test_character_analysis():
    """Test character count analysis functionality"""
    
    print("\n\nTesting Character Count Analysis")
    print("=" * 50)
    
    test_strings = [
        "Short",  # 5 chars - Optimal
        "This is a medium length string for QR testing",  # 46 chars - Optimal
        "This is a longer string that should fall into the good category for QR code generation",  # 93 chars - Good
        "This is an even longer string that contains much more text and should fall into the acceptable category for QR code generation and steganography purposes", # 154 chars - Acceptable
        "This is a very long string that contains a lot of text and should definitely fall into the problematic category for QR code generation and steganography purposes. It includes much more content than recommended and may cause issues." # 242 chars - Problematic
    ]
    
    for i, text in enumerate(test_strings, 1):
        length = len(text)
        print(f"\nTest {i}: {length} characters")
        print(f"Text: {text[:50]}{'...' if length > 50 else ''}")
        
        if length <= 50:
            status = "Optimal"
            percentage = (length / 50) * 100
        elif length <= 100:
            status = "Good"
            percentage = ((length - 50) / 50) * 100
        elif length <= 200:
            status = "Acceptable"
            percentage = ((length - 100) / 100) * 100
        else:
            status = "Problematic"
            percentage = 100
            
        print(f"Status: {status}")
        print(f"Usage: {percentage:.1f}%")

if __name__ == "__main__":
    test_enhanced_qr_generation()
    test_character_analysis()
    print("\n\nAll tests completed successfully!")
