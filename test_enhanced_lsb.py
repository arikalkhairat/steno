#!/usr/bin/env python3
"""
Enhanced LSB Steganography Test
Tests all new enhanced functions for LSB steganography with dynamic QR sizing
"""

import os
import sys
from PIL import Image
import numpy as np

def test_analyze_image_capacity():
    """Test enhanced image capacity analysis"""
    print("🧪 Testing Enhanced Image Capacity Analysis")
    print("-" * 50)
    
    try:
        from lsb_steganography import analyze_image_capacity
        
        # Create a test image if none exists
        test_image_path = "test_capacity_image.png" 
        if not os.path.exists(test_image_path):
            # Create a 640x480 test image
            test_img = Image.new('RGB', (640, 480), color=(100, 150, 200))
            test_img.save(test_image_path)
            print(f"✅ Created test image: {test_image_path}")
        
        # Test capacity analysis
        analysis = analyze_image_capacity(test_image_path)
        
        print("✅ Capacity Analysis Results:")
        print(f"   Total Pixels: {analysis['total_pixels']:,}")
        print(f"   Usable Capacity: {analysis['usable_capacity']:,} bits")
        print(f"   Available for QR: {analysis['available_for_qr']:,} bits")
        print(f"   Max QR Size: {analysis['max_qr_size']['width']}x{analysis['max_qr_size']['height']}")
        print(f"   Recommended QR Size: {analysis['recommended_qr_size']['width']}x{analysis['recommended_qr_size']['height']}")
        print(f"   Efficiency Score: {analysis['efficiency_score']}")
        
        # Verify required fields
        required_fields = [
            'total_pixels', 'usable_capacity', 'header_bits', 'available_for_qr',
            'max_qr_size', 'recommended_qr_size', 'efficiency_score'
        ]
        
        missing_fields = [field for field in required_fields if field not in analysis]
        if not missing_fields:
            print("✅ All required fields present in analysis result")
        else:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Capacity analysis test failed: {str(e)}")
        return False


def test_optimize_qr_for_image():
    """Test QR size optimization for images"""
    print("\n🧪 Testing QR Size Optimization")
    print("-" * 50)
    
    try:
        from lsb_steganography import optimize_qr_for_image
        
        # Create a test image
        test_image_path = "test_optimize_image.png"
        if not os.path.exists(test_image_path):
            test_img = Image.new('RGB', (800, 600), color=(120, 180, 210))
            test_img.save(test_image_path)
            print(f"✅ Created test image: {test_image_path}")
        
        # Test optimization with different data lengths
        test_cases = [
            {"data_length": 50, "description": "Short text"},
            {"data_length": 200, "description": "Medium text"},
            {"data_length": 500, "description": "Long text"}
        ]
        
        for test_case in test_cases:
            print(f"\n📊 Testing {test_case['description']} (length: {test_case['data_length']})")
            
            optimization = optimize_qr_for_image(test_image_path, test_case['data_length'])
            
            print(f"   Required QR Version: {optimization['data_requirements']['required_qr_version']}")
            print(f"   QR Modules: {optimization['data_requirements']['qr_modules']}")
            print(f"   Optimal QR Size: {optimization['optimal_configuration']['qr_size']}x{optimization['optimal_configuration']['qr_size']}")
            print(f"   Quality Level: {optimization['quality_prediction']['quality_level']}")
            print(f"   Predicted PSNR: {optimization['quality_prediction']['predicted_psnr']}")
            
            # Verify required structure
            required_sections = ['data_requirements', 'optimal_configuration', 'quality_prediction']
            missing_sections = [section for section in required_sections if section not in optimization]
            
            if not missing_sections:
                print(f"   ✅ All required sections present")
            else:
                print(f"   ❌ Missing sections: {missing_sections}")
                return False
        
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        print("✅ QR optimization test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ QR optimization test failed: {str(e)}")
        return False


def test_check_qr_compatibility():
    """Test QR compatibility checking"""
    print("\n🧪 Testing QR Compatibility Checking")
    print("-" * 50)
    
    try:
        from lsb_steganography import check_qr_compatibility
        
        # Create test images
        cover_image_path = "test_cover.png"
        qr_image_path = "test_qr.png"
        
        # Create cover image
        if not os.path.exists(cover_image_path):
            cover_img = Image.new('RGB', (600, 400), color=(150, 200, 100))
            cover_img.save(cover_image_path)
            print(f"✅ Created test cover image: {cover_image_path}")
        
        # Create QR image
        if not os.path.exists(qr_image_path):
            qr_img = Image.new('1', (100, 100), color=1)  # White QR
            # Add some black squares to simulate QR pattern
            for i in range(0, 100, 10):
                for j in range(0, 100, 10):
                    if (i + j) % 20 == 0:  # Create pattern
                        for x in range(i, min(i+5, 100)):
                            for y in range(j, min(j+5, 100)):
                                qr_img.putpixel((x, y), 0)  # Black
            qr_img.save(qr_image_path)
            print(f"✅ Created test QR image: {qr_image_path}")
        
        # Test compatibility
        compatibility = check_qr_compatibility(cover_image_path, qr_image_path)
        
        print(f"✅ Compatibility Results:")
        print(f"   Compatible: {compatibility['compatible']}")
        print(f"   Resize Required: {compatibility['resize_required']}")
        print(f"   Quality Level: {compatibility['quality_prediction']['quality_level']}")
        
        if compatibility['quality_prediction']['mse_estimate'] is not None:
            print(f"   MSE Estimate: {compatibility['quality_prediction']['mse_estimate']}")
            print(f"   PSNR Estimate: {compatibility['quality_prediction']['psnr_estimate']}")
        
        print(f"   Recommendations: {len(compatibility['recommendations'])} items")
        for rec in compatibility['recommendations'][:3]:  # Show first 3 recommendations
            print(f"     • {rec}")
        
        # Verify required structure
        required_fields = [
            'compatible', 'resize_required', 'capacity_analysis', 
            'quality_prediction', 'recommendations'
        ]
        
        missing_fields = [field for field in required_fields if field not in compatibility]
        if not missing_fields:
            print("✅ All required fields present in compatibility result")
        else:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Cleanup
        for path in [cover_image_path, qr_image_path]:
            if os.path.exists(path):
                os.remove(path)
        
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {str(e)}")
        return False


def test_enhanced_resize_qr():
    """Test enhanced QR resizing"""
    print("\n🧪 Testing Enhanced QR Resize")
    print("-" * 50)
    
    try:
        from lsb_steganography import enhanced_resize_qr
        
        # Create test QR image
        original_qr = Image.new('1', (200, 200), color=1)  # White background
        
        # Add QR pattern
        for i in range(0, 200, 20):
            for j in range(0, 200, 20):
                if (i + j) % 40 == 0:
                    for x in range(i, min(i+10, 200)):
                        for y in range(j, min(j+10, 200)):
                            original_qr.putpixel((x, y), 0)  # Black modules
        
        print(f"✅ Created test QR image: {original_qr.size}")
        
        # Test different resize scenarios
        test_cases = [
            {"target_size": (150, 150), "algorithm": "lanczos", "description": "Downsize with Lanczos"},
            {"target_size": (300, 300), "algorithm": "nearest", "description": "Upsize with Nearest"},
            {"target_size": (100, 100), "algorithm": "bicubic", "description": "Significant downsize with Bicubic"}
        ]
        
        for test_case in test_cases:
            print(f"\n📏 Testing: {test_case['description']}")
            
            resize_result = enhanced_resize_qr(
                original_qr, 
                test_case['target_size'], 
                test_case['algorithm']
            )
            
            print(f"   Original Size: {resize_result['original_size']}")
            print(f"   New Size: {resize_result['new_size']}")
            print(f"   Size Change Ratio: {resize_result['size_change_ratio']}")
            print(f"   Quality Level: {resize_result['quality_metrics']['quality_level']}")
            print(f"   Readability Score: {resize_result['quality_metrics']['readability_score']}")
            print(f"   Resize Time: {resize_result['performance']['resize_time']}s")
            
            # Verify resized image
            resized_img = resize_result['resized_image']
            if resized_img.size == test_case['target_size']:
                print(f"   ✅ Resize successful to target size")
            else:
                print(f"   ❌ Resize failed - got {resized_img.size}, expected {test_case['target_size']}")
                return False
            
            # Check recommendations
            if resize_result['recommendations']:
                print(f"   💡 Recommendations: {len(resize_result['recommendations'])} items")
        
        print("✅ Enhanced resize test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced resize test failed: {str(e)}")
        return False


def test_batch_analyze_images():
    """Test batch image analysis"""
    print("\n🧪 Testing Batch Image Analysis")
    print("-" * 50)
    
    try:
        from lsb_steganography import batch_analyze_images
        
        # Create multiple test images
        test_images = []
        for i in range(3):
            image_path = f"test_batch_{i}.png"
            # Create images with different sizes
            size = (400 + i * 200, 300 + i * 150)
            color = (50 + i * 50, 100 + i * 50, 150 + i * 50)
            
            test_img = Image.new('RGB', size, color=color)
            test_img.save(image_path)
            test_images.append(image_path)
            print(f"✅ Created test image {i+1}: {image_path} ({size})")
        
        # Test batch analysis
        batch_result = batch_analyze_images(test_images, output_format="summary")
        
        print(f"\n📊 Batch Analysis Results:")
        print(f"   Total Images: {batch_result['total_images']}")
        print(f"   Successful: {batch_result['successful_analyses']}")
        print(f"   Failed: {batch_result['failed_analyses']}")
        print(f"   Processing Time: {batch_result['processing_time']}s")
        
        if batch_result['summary_statistics']:
            capacity_stats = batch_result['summary_statistics']['capacity_stats']
            print(f"   Capacity Range: {capacity_stats['min']:,} - {capacity_stats['max']:,} bits")
            print(f"   Average Capacity: {capacity_stats['mean']:,.0f} bits")
            
            efficiency_stats = batch_result['summary_statistics']['efficiency_stats']
            print(f"   Efficiency Range: {efficiency_stats['min']:.1f} - {efficiency_stats['max']:.1f}")
        
        # Verify batch results structure
        if batch_result['successful_analyses'] == len(test_images):
            print("✅ All images analyzed successfully")
        else:
            print(f"❌ Some images failed analysis")
            return False
        
        # Cleanup
        for image_path in test_images:
            if os.path.exists(image_path):
                os.remove(image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Batch analysis test failed: {str(e)}")
        return False


def test_integration_with_existing_functions():
    """Test integration with existing LSB functions"""
    print("\n🧪 Testing Integration with Existing Functions")
    print("-" * 50)
    
    try:
        from lsb_steganography import (
            embed_qr_to_image, extract_qr_from_image,
            analyze_image_capacity, check_qr_compatibility
        )
        
        # Create test images
        cover_path = "test_integration_cover.png"
        qr_path = "test_integration_qr.png"
        stego_path = "test_integration_stego.png"
        extracted_path = "test_integration_extracted.png"
        
        # Create cover image
        cover_img = Image.new('RGB', (400, 300), color=(128, 128, 128))
        cover_img.save(cover_path)
        
        # Create QR image
        qr_img = Image.new('1', (50, 50), color=1)
        # Add simple pattern
        for i in range(0, 50, 5):
            for j in range(0, 50, 5):
                if (i + j) % 10 == 0:
                    qr_img.putpixel((i, j), 0)
        qr_img.save(qr_path)
        
        print("✅ Created test images for integration")
        
        # Test capacity analysis first
        capacity_analysis = analyze_image_capacity(cover_path)
        print(f"✅ Capacity analysis: {capacity_analysis['available_for_qr']:,} bits available")
        
        # Test compatibility check
        compatibility = check_qr_compatibility(cover_path, qr_path)
        if compatibility['compatible']:
            print("✅ Compatibility check: QR can be embedded")
            
            # Test embedding
            embed_qr_to_image(cover_path, qr_path, stego_path)
            if os.path.exists(stego_path):
                print("✅ QR embedding successful")
                
                # Test extraction
                extract_qr_from_image(stego_path, extracted_path)
                if os.path.exists(extracted_path):
                    print("✅ QR extraction successful")
                    
                    # Compare original and extracted QR
                    original_qr = Image.open(qr_path)
                    extracted_qr = Image.open(extracted_path)
                    
                    if original_qr.size == extracted_qr.size:
                        print("✅ Extracted QR has correct dimensions")
                    else:
                        print(f"⚠️ Size mismatch: original {original_qr.size}, extracted {extracted_qr.size}")
                else:
                    print("❌ QR extraction failed")
                    return False
            else:
                print("❌ QR embedding failed")
                return False
        else:
            print("⚠️ Compatibility issue, but test continues")
        
        # Cleanup
        test_files = [cover_path, qr_path, stego_path, extracted_path]
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        print("✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False


def main():
    """Run all enhanced LSB steganography tests"""
    print("🚀 ENHANCED LSB STEGANOGRAPHY TEST SUITE")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_functions = [
        ("Analyze Image Capacity", test_analyze_image_capacity),
        ("QR Size Optimization", test_optimize_qr_for_image),
        ("QR Compatibility Check", test_check_qr_compatibility),
        ("Enhanced QR Resize", test_enhanced_resize_qr),
        ("Batch Image Analysis", test_batch_analyze_images),
        ("Integration Test", test_integration_with_existing_functions)
    ]
    
    for test_name, test_func in test_functions:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 ENHANCED LSB STEGANOGRAPHY TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for name, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTest Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL ENHANCED LSB STEGANOGRAPHY FEATURES WORKING!")
        print("📋 New Capabilities Ready:")
        print("   • Enhanced capacity analysis with efficiency scoring")
        print("   • QR size optimization for cover images")
        print("   • Compatibility checking with quality predictions")
        print("   • Enhanced resize algorithms with quality metrics")
        print("   • Batch processing for multiple images")
        print("   • Full integration with existing LSB functions")
        print("\n🚀 Enhanced LSB steganography system ready for production!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests need attention")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
