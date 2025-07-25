#!/usr/bin/env python3
"""
Test for processed_images issue - Check what data is being sent
"""

import os
import json

def check_backend_function():
    """Check if backend functions return processed_images correctly"""
    print("🔍 CHECKING BACKEND FUNCTION")
    print("=" * 50)
    
    # Import main functions
    try:
        import sys
        sys.path.insert(0, os.getcwd())
        from main import embed_watermark_to_docx
        
        print("✅ Successfully imported embed_watermark_to_docx")
        
        # Check function signature
        import inspect
        sig = inspect.signature(embed_watermark_to_docx)
        print(f"📝 Function signature: {sig}")
        
        # Check return type annotation
        print(f"📤 Return annotation: {sig.return_annotation}")
        
    except Exception as e:
        print(f"❌ Error importing function: {e}")

def simulate_data_flow():
    """Simulate the data flow from backend to frontend"""
    print("\n🔄 SIMULATING DATA FLOW")
    print("=" * 50)
    
    # Find a processed directory to simulate data
    static_path = "static/generated"
    if os.path.exists(static_path):
        processed_dirs = [d for d in os.listdir(static_path) if d.startswith('processed_')]
        
        if processed_dirs:
            sample_dir = processed_dirs[0]
            print(f"📁 Using sample directory: {sample_dir}")
            
            dir_path = os.path.join(static_path, sample_dir)
            files = os.listdir(dir_path)
            
            # Find original and watermarked files
            original_files = sorted([f for f in files if f.startswith('original_')])
            watermarked_files = sorted([f for f in files if f.startswith('watermarked_')])
            
            print(f"🖼️  Found {len(original_files)} original files")
            print(f"🖼️  Found {len(watermarked_files)} watermarked files")
            
            # Simulate processed_images data
            processed_images = []
            for i, (orig, water) in enumerate(zip(original_files[:3], watermarked_files[:3])):
                processed_images.append({
                    "index": i,
                    "original": f"{sample_dir}/{orig}",
                    "watermarked": f"{sample_dir}/{water}",
                    "image_size": "800x600"
                })
            
            print(f"\n📊 Simulated processed_images:")
            print(json.dumps(processed_images, indent=2))
            
            # Test frontend path conversion
            print(f"\n🔗 Frontend path conversion:")
            for img in processed_images:
                orig_frontend = f"/static/generated/{img['original']}"
                water_frontend = f"/static/generated/{img['watermarked']}"
                
                print(f"   Original: {orig_frontend}")
                print(f"   Watermarked: {water_frontend}")
                
                # Check if files exist
                orig_exists = os.path.exists(f"static/generated/{img['original']}")
                water_exists = os.path.exists(f"static/generated/{img['watermarked']}")
                print(f"   Exists: Orig={orig_exists}, Water={water_exists}")
                print()
            
            return processed_images
    
    print("❌ No processed directories found")
    return []

def create_simple_test_page():
    """Create a simple test page to verify image display"""
    processed_images = simulate_data_flow()
    
    if not processed_images:
        print("❌ Cannot create test page - no data")
        return
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Simple Image Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .test-container {{ margin: 20px 0; }}
        .image-comparison {{ 
            display: flex; 
            gap: 20px; 
            margin: 20px 0; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 8px;
        }}
        .image-item {{ text-align: center; flex: 1; }}
        .image-item img {{ 
            max-width: 200px; 
            border: 1px solid #ccc; 
            border-radius: 4px;
        }}
        .debug {{ 
            background: #f5f5f5; 
            padding: 10px; 
            margin: 10px 0; 
            font-family: monospace; 
            font-size: 12px;
        }}
        .error {{ 
            background: #ffe6e6; 
            padding: 10px; 
            margin: 5px 0; 
            color: red; 
            font-size: 12px;
        }}
        .success {{ 
            background: #e6ffe6; 
            padding: 10px; 
            margin: 5px 0; 
            color: green; 
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>🧪 Simple Image Display Test</h1>
    
    <div class="debug">
        <h3>Test Data:</h3>
        <pre>{json.dumps(processed_images, indent=2)}</pre>
    </div>
    
    <div class="test-container">
        <h2>Manual Path Test</h2>
        <div class="image-comparison">
            <div class="image-item">
                <h4>Manual Original</h4>
                <img src="/static/generated/{processed_images[0]['original']}" 
                     alt="Original" 
                     onload="this.nextElementSibling.innerHTML='✅ Loaded successfully'"
                     onerror="this.nextElementSibling.innerHTML='❌ Failed to load: ' + this.src">
                <div class="success"></div>
            </div>
            <div class="image-item">
                <h4>Manual Watermarked</h4>
                <img src="/static/generated/{processed_images[0]['watermarked']}" 
                     alt="Watermarked"
                     onload="this.nextElementSibling.innerHTML='✅ Loaded successfully'"
                     onerror="this.nextElementSibling.innerHTML='❌ Failed to load: ' + this.src">
                <div class="success"></div>
            </div>
        </div>
    </div>
    
    <div class="test-container">
        <h2>JavaScript Function Test</h2>
        <div id="jsTestContainer"></div>
    </div>
    
    <script>
        const testData = {json.dumps(processed_images)};
        
        // Copy of the displayImageComparison function
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

            container.innerHTML = '<h3>✅ Perbandingan Gambar</h3>';
            
            processedImages.forEach((img, index) => {{
                const comparison = document.createElement('div');
                comparison.className = 'image-comparison';
                
                // Handle different path formats - use the full path as provided by backend
                const originalPath = img.original.startsWith('/') ? img.original : `/static/generated/${{img.original}}`;
                const watermarkedPath = img.watermarked.startsWith('/') ? img.watermarked : `/static/generated/${{img.watermarked}}`;
                
                comparison.innerHTML = `
                    <div class="image-item">
                        <h4>Gambar Asli ${{index + 1}}</h4>
                        <img src="${{originalPath}}" alt="Original ${{index + 1}}" 
                             onload="this.nextElementSibling.innerHTML='✅ JS: Loaded successfully'"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="error" style="display:none;">
                            ❌ JS: Gambar tidak ditemukan<br><small>${{originalPath}}</small>
                        </div>
                        <div class="success"></div>
                        <p style="font-size:10px; color:#666;">${{originalPath}}</p>
                    </div>
                    <div class="image-item">
                        <h4>Gambar Watermark ${{index + 1}}</h4>
                        <img src="${{watermarkedPath}}" alt="Watermarked ${{index + 1}}" 
                             onload="this.nextElementSibling.innerHTML='✅ JS: Loaded successfully'"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div class="error" style="display:none;">
                            ❌ JS: Gambar tidak ditemukan<br><small>${{watermarkedPath}}</small>
                        </div>
                        <div class="success"></div>
                        <p style="font-size:10px; color:#666;">${{watermarkedPath}}</p>
                    </div>
                `;
                container.appendChild(comparison);
            }});

            console.log('✅ Image comparison displayed successfully');
        }}
        
        // Run test
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🧪 Running JavaScript test...');
            displayImageComparison('jsTestContainer', testData);
        }});
    </script>
</body>
</html>"""

    with open("simple_image_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n📄 Created simple_image_test.html")
    print(f"   Open this file in browser while Flask is running to test images")

def main():
    print("🔍 PROCESSED IMAGES DEBUG TEST")
    print("=" * 60)
    
    check_backend_function()
    simulate_data_flow()
    create_simple_test_page()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG STEPS:")
    print("1. Start Flask: python app.py")
    print("2. Open simple_image_test.html in browser")
    print("3. Check if manual paths work")
    print("4. Check if JavaScript function works") 
    print("5. Compare with actual embed results")
    print("\n💡 If images don't load, check:")
    print("   - Flask static route configuration")
    print("   - File permissions")
    print("   - Path case sensitivity")

if __name__ == "__main__":
    main()
