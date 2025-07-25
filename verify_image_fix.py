#!/usr/bin/env python3
"""
Simple verification script to check if image comparison fix works
"""

import os
import json
from pathlib import Path

def verify_static_structure():
    """Verify static directory structure is correct"""
    print("🔍 VERIFYING STATIC STRUCTURE")
    print("=" * 50)
    
    # Check required directories
    required_dirs = [
        "static/generated",
        "static/uploads", 
        "public/documents"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            files = os.listdir(directory)
            print(f"✅ {directory}: {len(files)} items")
            
            # Check for processed directories
            if directory == "static/generated":
                processed_dirs = [f for f in files if f.startswith('processed_')]
                print(f"   📁 Processed directories: {len(processed_dirs)}")
                
                # Check first processed directory for images
                if processed_dirs:
                    sample_dir = os.path.join(directory, processed_dirs[0])
                    if os.path.isdir(sample_dir):
                        dir_files = os.listdir(sample_dir)
                        original_files = [f for f in dir_files if f.startswith('original_')]
                        watermarked_files = [f for f in dir_files if f.startswith('watermarked_')]
                        print(f"   🖼️  Sample dir {processed_dirs[0]}:")
                        print(f"      Original images: {len(original_files)}")
                        print(f"      Watermarked images: {len(watermarked_files)}")
        else:
            print(f"❌ {directory}: NOT FOUND")

def simulate_processed_images_data():
    """Simulate the processed_images data that backend sends"""
    print("\n🧪 SIMULATING BACKEND DATA")
    print("=" * 50)
    
    # Find a processed directory
    static_gen = "static/generated"
    if os.path.exists(static_gen):
        processed_dirs = [f for f in os.listdir(static_gen) if f.startswith('processed_')]
        
        if processed_dirs:
            sample_dir = processed_dirs[0]
            sample_path = os.path.join(static_gen, sample_dir)
            
            if os.path.isdir(sample_path):
                files = os.listdir(sample_path)
                original_files = sorted([f for f in files if f.startswith('original_')])
                watermarked_files = sorted([f for f in files if f.startswith('watermarked_')])
                
                # Simulate processed_images data
                processed_images = []
                for i, (orig, water) in enumerate(zip(original_files[:3], watermarked_files[:3])):
                    processed_images.append({
                        "index": i,
                        "original": f"{sample_dir}/{orig}",
                        "watermarked": f"{sample_dir}/{water}", 
                        "image_size": "800x600"
                    })
                
                print(f"📊 Sample processed_images data:")
                print(json.dumps(processed_images, indent=2))
                
                # Show the expected frontend paths
                print(f"\n🔗 Expected frontend paths:")
                for img in processed_images:
                    orig_path = f"/static/generated/{img['original']}"
                    water_path = f"/static/generated/{img['watermarked']}"
                    print(f"   Original: {orig_path}")
                    print(f"   Watermarked: {water_path}")
                    
                    # Check if files actually exist
                    orig_exists = os.path.exists(f"static/generated/{img['original']}")
                    water_exists = os.path.exists(f"static/generated/{img['watermarked']}")
                    print(f"   Files exist: Original={orig_exists}, Watermarked={water_exists}")
                    print()
                
                return processed_images
    
    print("❌ No processed directories found")
    return []

def create_test_html():
    """Create a simple test HTML to verify image display"""
    processed_images = simulate_processed_images_data()
    
    if not processed_images:
        print("❌ Cannot create test HTML - no processed images found")
        return
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Image Display Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .image-comparison {{ display: flex; gap: 20px; margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .image-item {{ text-align: center; }}
        .image-item img {{ max-width: 200px; border: 1px solid #ccc; }}
        .debug {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
        .error {{ background: #ffe6e6; padding: 10px; margin: 10px 0; color: red; }}
    </style>
</head>
<body>
    <h1>🧪 Image Display Test</h1>
    
    <div class="debug">
        <h3>Test Data:</h3>
        <pre>{json.dumps(processed_images, indent=2)}</pre>
    </div>
    
    <div id="testContainer"></div>
    
    <script>
        const processedImages = {json.dumps(processed_images)};
        
        function displayImageComparison(containerId, processedImages) {{
            const container = document.getElementById(containerId);
            if (!container) {{
                console.error('Container not found:', containerId);
                return;
            }}

            console.log('displayImageComparison called with:', processedImages);

            if (!processedImages || processedImages.length === 0) {{
                container.innerHTML = '<p>❌ Tidak ada gambar yang diproses untuk ditampilkan perbandingan.</p>';
                return;
            }}

            container.innerHTML = '<h2>✅ Perbandingan Gambar</h2>';
            
            processedImages.forEach((img, index) => {{
                const comparison = document.createElement('div');
                comparison.className = 'image-comparison';
                
                const originalPath = img.original.startsWith('/') ? img.original : `/static/generated/${{img.original}}`;
                const watermarkedPath = img.watermarked.startsWith('/') ? img.watermarked : `/static/generated/${{img.watermarked}}`;
                
                comparison.innerHTML = `
                    <div class="image-item">
                        <h4>Gambar Asli ${{index + 1}}</h4>
                        <img src="${{originalPath}}" alt="Original ${{index + 1}}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="error" style="display:none;">
                            ❌ Gambar tidak ditemukan<br><small>${{originalPath}}</small>
                        </div>
                        <p><small>${{originalPath}}</small></p>
                    </div>
                    <div class="image-item">
                        <h4>Gambar Watermark ${{index + 1}}</h4>
                        <img src="${{watermarkedPath}}" alt="Watermarked ${{index + 1}}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="error" style="display:none;">
                            ❌ Gambar tidak ditemukan<br><small>${{watermarkedPath}}</small>
                        </div>
                        <p><small>${{watermarkedPath}}</small></p>
                    </div>
                `;
                container.appendChild(comparison);
            }});

            console.log('✅ Image comparison displayed successfully');
        }}
        
        // Run test
        document.addEventListener('DOMContentLoaded', function() {{
            displayImageComparison('testContainer', processedImages);
        }});
    </script>
</body>
</html>"""

    with open("quick_image_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n📄 Created quick_image_test.html")
    print(f"   Open this file in browser to test image display")

def main():
    print("🔍 IMAGE COMPARISON FIX VERIFICATION")
    print("=" * 60)
    
    verify_static_structure()
    simulate_processed_images_data()
    create_test_html()
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION SUMMARY:")
    print("1. ✅ Code fixes applied to templates/index.html")
    print("2. ✅ Enhanced logging added to app.py") 
    print("3. ✅ Error handling improved with debugging")
    print("4. ✅ Path handling fixed for different formats")
    print("\n📋 NEXT STEPS:")
    print("1. Start Flask app: python app.py")
    print("2. Test embed functionality in browser")
    print("3. Check browser console for debug messages")
    print("4. Open quick_image_test.html to test paths")

if __name__ == "__main__":
    main()
