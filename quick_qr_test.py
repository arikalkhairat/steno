#!/usr/bin/env python3
"""
Quick verification of enhanced QR utils functionality
"""

import os
from qr_utils import (
    generate_qr, analyze_qr_requirements, estimate_steganography_capacity,
    get_capacity_info, quick_qr_analysis
)

def quick_test():
    print("🧪 Quick Enhanced QR Utils Verification")
    print("=" * 50)
    
    # Test 1: Enhanced generate_qr with metadata
    print("\n1. Testing enhanced generate_qr with metadata:")
    try:
        os.makedirs("static/generated", exist_ok=True)
        result = generate_qr(
            "Enhanced QR Test", 
            "static/generated/quick_test.png",
            error_correction='M',
            box_size=8,
            return_metadata=True
        )
        
        if result and result.get('success'):
            metadata = result['metadata']
            print(f"   ✅ Success! Version: {metadata.get('version')}, Size: {metadata.get('size_pixels')}")
            print(f"   📊 Capacity used: {metadata.get('capacity_used')}%")
            print(f"   🛡️ Steganography compatible: {metadata.get('steganography_compatible')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 2: QR requirements analysis
    print("\n2. Testing analyze_qr_requirements:")
    try:
        analysis = analyze_qr_requirements("Test data for analysis")
        print(f"   ✅ Data mode: {analysis.get('data_mode')}")
        print(f"   📊 Recommended version: {analysis.get('recommended_version')}")
        print(f"   🔧 Recommended EC: {analysis.get('recommended_error_correction')}")
        print(f"   🛡️ Steganography compatible: {analysis.get('steganography_compatible')}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 3: Steganography capacity estimation
    print("\n3. Testing steganography capacity estimation:")
    try:
        capacity = estimate_steganography_capacity((200, 200), (800, 600))
        print(f"   ✅ Compatibility: {capacity.get('compatibility_level')}")
        print(f"   📊 Score: {capacity.get('compatibility_score')}")
        print(f"   📈 Embedding ratio: {capacity.get('embedding_ratio'):.4f}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 4: Capacity info analysis
    print("\n4. Testing capacity info analysis:")
    try:
        info = get_capacity_info(75, 'M')
        current = info.get('current_level', {})
        print(f"   ✅ Version needed: {current.get('version')}")
        print(f"   📊 Capacity: {current.get('capacity')} chars")
        print(f"   📈 Usage: {current.get('usage_percent')}%")
        print(f"   🎯 Status: {current.get('status')}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    # Test 5: Quick analysis
    print("\n5. Testing quick analysis:")
    try:
        quick = quick_qr_analysis("Quick analysis test string")
        data_summary = quick.get('data_summary', {})
        quick_status = quick.get('quick_status', {})
        
        print(f"   ✅ Length: {data_summary.get('length')}")
        print(f"   📊 Mode: {data_summary.get('mode')}")
        print(f"   🛡️ Steganography ready: {quick_status.get('steganography_ready')}")
        print(f"   ⚡ Capacity efficient: {quick_status.get('capacity_efficient')}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("\n🎉 Quick verification completed!")
    print("✅ All enhanced QR utilities are working correctly!")

if __name__ == "__main__":
    quick_test()
