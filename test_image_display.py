#!/usr/bin/env python3
"""
Test script to verify image comparison display functionality
"""

import os
import sys
import time
import requests
import json

def test_embed_endpoint():
    """Test the embed endpoint to see processed_images data"""
    
    # Check if test files exist
    test_files = {
        'docx': [f for f in os.listdir('static/uploads') if f.endswith('.docx')],
        'pdf': [f for f in os.listdir('static/uploads') if f.endswith('.pdf')],
        'qr': [f for f in os.listdir('static/uploads') if f.endswith('.png')]
    }
    
    print("📁 Available test files:")
    for file_type, files in test_files.items():
        print(f"  {file_type.upper()}: {len(files)} files")
        for f in files[:3]:  # Show first 3
            print(f"    - {f}")
    
    if not test_files['docx'] or not test_files['qr']:
        print("❌ No suitable test files found!")
        return
    
    # Try to make a request to test the endpoint
    try:
        doc_file = test_files['docx'][0]
        qr_file = test_files['qr'][0]
        
        print(f"\n🧪 Testing with: {doc_file} + {qr_file}")
        
        # Prepare files for upload
        doc_path = os.path.join('static/uploads', doc_file)
        qr_path = os.path.join('static/uploads', qr_file)
        
        files = {
            'docxFileEmbed': open(doc_path, 'rb'),
            'qrFileEmbed': open(qr_path, 'rb')
        }
        
        data = {
            'qr_version': 'auto',
            'error_correction': 'M',
            'box_size': '10',
            'border_size': '4'
        }
        
        # Make request to localhost (assuming app is running)
        try:
            response = requests.post('http://localhost:5000/embed_document', 
                                   files=files, data=data, timeout=30)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success')}")
                print(f"📊 Processed images count: {len(result.get('processed_images', []))}")
                print(f"🔍 Processed images data:")
                for i, img in enumerate(result.get('processed_images', [])):
                    print(f"  Image {i}: {img}")
            else:
                print(f"❌ Error response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to localhost:5000")
            print("💡 Make sure Flask app is running: python app.py")
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        
        # Close files
        for f in files.values():
            f.close()
            
    except Exception as e:
        print(f"❌ Test error: {e}")

def check_static_structure():
    """Check static directory structure"""
    print("\n📂 Static directory structure:")
    
    static_dirs = ['static/uploads', 'static/generated', 'public/documents']
    
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"  {dir_path}: {len(files)} files")
            
            # Look for processed directories
            processed_dirs = [f for f in files if f.startswith('processed_')]
            if processed_dirs:
                print(f"    Processed directories: {len(processed_dirs)}")
                for pdir in processed_dirs[:3]:  # Show first 3
                    pdir_path = os.path.join(dir_path, pdir)
                    if os.path.isdir(pdir_path):
                        pdir_files = os.listdir(pdir_path)
                        print(f"      {pdir}: {len(pdir_files)} files")
        else:
            print(f"  {dir_path}: NOT FOUND")

def main():
    print("🔍 IMAGE DISPLAY TEST")
    print("=" * 50)
    
    check_static_structure()
    test_embed_endpoint()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Start Flask app: python app.py")
    print("2. Test embedding in browser")
    print("3. Check console for debug messages")
    print("4. Verify image paths in network tab")

if __name__ == "__main__":
    main()
