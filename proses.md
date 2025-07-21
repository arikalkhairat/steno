# Dokumentasi Proses QR Code Watermarking

Dokumentasi ini menjelaskan snippet code penting dari proses input QR code sampai ekstraksi menggunakan teknik LSB steganography.

## 1. Generate QR Code

### Fungsi Utama: `generate_qr()` di qr_utils.py

```python
def generate_qr(data: str, output_path: str):
    """Membuat citra QR Code dari data teks dan menyimpannya ke file."""
    try:
        # Konfigurasi QR Code
        qr = qrcode.QRCode(
            version=1,  # Ukuran QR Code (1-40)
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Level koreksi error
            box_size=10,  # Ukuran setiap kotak dalam piksel
            border=4,  # Lebar border minimum
        )
        
        # Tambahkan data dan buat QR Code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Generate dan simpan image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
    except Exception as e:
        print(f"[!] Error saat membuat QR Code: {e}")
        raise
```

**Penjelasan:**
- Menggunakan library `qrcode` untuk membuat QR Code
- Parameter `version=1` mengatur ukuran QR Code secara otomatis
- `ERROR_CORRECT_L` memberikan tingkat koreksi error terendah (optimal untuk watermarking)
- Output berupa file PNG hitam-putih

---

## 2. LSB Steganography - Embedding Process

### Fungsi Utama: `embed_qr_to_image()` di lsb_steganography.py

```python
def _embed_bit(pixel_value: int, bit: str) -> int:
    """Menyisipkan satu bit ke LSB dari nilai piksel"""
    if bit == '0':
        return pixel_value & 254  # Set LSB ke 0 (AND dengan 11111110)
    else:
        return pixel_value | 1    # Set LSB ke 1 (OR dengan 00000001)
```

```python
def embed_qr_to_image(cover_image_path: str, qr_image_path: str, output_path: str):
    """Menyisipkan QR Code ke dalam gambar menggunakan LSB steganography"""
    
    # 1. Load dan resize QR Code
    cover_img = Image.open(cover_image_path).convert('RGB')
    qr_img = Image.open(qr_image_path).convert('L')  # Grayscale
    
    # 2. Hitung kapasitas dan resize QR jika perlu
    cover_width, cover_height = cover_img.size
    max_capacity = cover_width * cover_height * 3  # RGB channels
    
    qr_resized = _resize_qr_for_capacity(qr_img, max_capacity)
    qr_width, qr_height = qr_resized.size
    
    # 3. Buat header dengan informasi QR Code
    header = _create_header(qr_width, qr_height)
    
    # 4. Konversi QR ke binary
    qr_binary = _qr_to_binary(qr_resized)
    
    # 5. Gabungkan header + QR binary + terminator
    full_data = header + qr_binary + HEADER_TERMINATOR_BIN
    
    # 6. Embed ke cover image
    cover_pixels = list(cover_img.getdata())
    data_index = 0
    
    for i, pixel in enumerate(cover_pixels):
        if data_index < len(full_data):
            r, g, b = pixel
            
            # Embed ke channel R, G, B secara berurutan
            if data_index < len(full_data):
                r = _embed_bit(r, full_data[data_index])
                data_index += 1
            if data_index < len(full_data):
                g = _embed_bit(g, full_data[data_index])
                data_index += 1
            if data_index < len(full_data):
                b = _embed_bit(b, full_data[data_index])
                data_index += 1
                
            cover_pixels[i] = (r, g, b)
        else:
            break
    
    # 7. Simpan stego image
    stego_img = Image.new('RGB', cover_img.size)
    stego_img.putdata(cover_pixels)
    stego_img.save(output_path)
```

**Penjelasan:**
- QR Code di-resize sesuai kapasitas cover image (max 1/8 dari total piksel)
- Header berisi informasi ukuran QR Code (width + height dalam 16 bit)
- Data QR disimpan dalam LSB channel RGB secara berurutan
- Terminator (`00000000`) menandai akhir data

---

## 3. Document Processing - Embedding

### Fungsi Utama: `embed_watermark_to_docx()` di main.py

```python
def embed_watermark_to_docx(docx_path: str, qr_path: str, output_path: str):
    """Embed QR Code watermark ke semua gambar dalam dokumen DOCX"""
    
    # 1. Ekstrak semua gambar dari dokumen
    temp_extraction_dir = f"temp_extraction_{uuid.uuid4().hex}"
    original_images = extract_images_from_docx(docx_path, temp_extraction_dir)
    
    if not original_images:
        raise ValueError("NO_IMAGES_FOUND")
    
    # 2. Buat direktori untuk gambar hasil watermarking
    temp_watermarked_dir = f"temp_watermarked_{uuid.uuid4().hex}"
    os.makedirs(temp_watermarked_dir, exist_ok=True)
    
    watermarked_images = []
    
    # 3. Proses setiap gambar
    for i, original_image_path in enumerate(original_images):
        try:
            watermarked_image_path = os.path.join(temp_watermarked_dir, f"watermarked_{i}.png")
            
            # Embed QR Code ke gambar
            embed_qr_to_image(original_image_path, qr_path, watermarked_image_path)
            watermarked_images.append(watermarked_image_path)
            
        except Exception as e:
            print(f"[!] Error memproses gambar {i}: {str(e)}")
            # Gunakan gambar asli jika embedding gagal
            watermarked_images.append(original_image_path)
    
    # 4. Replace gambar dalam dokumen dengan versi watermarked
    success = replace_images_in_docx(docx_path, original_images, watermarked_images, output_path)
    
    # 5. Cleanup temporary files
    cleanup_temp_dirs([temp_extraction_dir, temp_watermarked_dir])
    
    return {"success": success, "processed_images": len(watermarked_images)}
```

**Penjelasan:**
- Ekstrak semua gambar dari dokumen DOCX menggunakan `python-docx`
- Setiap gambar di-watermark dengan QR Code yang sama
- Gambar hasil watermarking menggantikan gambar asli dalam dokumen
- Struktur dan format dokumen tetap dipertahankan

---

## 4. LSB Steganography - Extraction Process

### Fungsi Utama: `extract_qr_from_image()` di lsb_steganography.py

```python
def _extract_lsb(pixel_value: int) -> str:
    """Ekstrak LSB dari nilai piksel"""
    return '1' if pixel_value % 2 == 1 else '0'

def extract_qr_from_image(stego_image_path: str, output_dir: str):
    """Ekstrak QR Code dari stego image menggunakan LSB"""
    
    # 1. Load stego image
    stego_img = Image.open(stego_image_path).convert('RGB')
    stego_pixels = list(stego_img.getdata())
    
    # 2. Ekstrak header untuk mendapatkan ukuran QR
    extracted_bits = []
    bit_index = 0
    
    # Ekstrak bit dari LSB setiap channel RGB
    for pixel in stego_pixels:
        r, g, b = pixel
        extracted_bits.append(_extract_lsb(r))
        extracted_bits.append(_extract_lsb(g))
        extracted_bits.append(_extract_lsb(b))
        
        # Cek apakah sudah menemukan terminator
        if len(extracted_bits) >= HEADER_TERMINATOR_LEN:
            current_bits = ''.join(extracted_bits[-HEADER_TERMINATOR_LEN:])
            if current_bits == HEADER_TERMINATOR_BIN:
                break
    
    # 3. Parse header untuk mendapatkan dimensi QR
    if len(extracted_bits) < 32 + HEADER_TERMINATOR_LEN:
        raise ValueError("Header tidak lengkap atau tidak valid")
    
    header_bits = ''.join(extracted_bits[:32])
    qr_width = _binary_to_int(header_bits[:16])
    qr_height = _binary_to_int(header_bits[16:32])
    
    # 4. Ekstrak data QR Code
    qr_data_start = 32
    qr_data_end = qr_data_start + (qr_width * qr_height)
    
    if len(extracted_bits) < qr_data_end:
        raise ValueError("Data QR tidak lengkap")
    
    qr_bits = extracted_bits[qr_data_start:qr_data_end]
    
    # 5. Rekonstruksi QR Code image
    qr_pixels = []
    for bit in qr_bits:
        pixel_value = 0 if bit == '0' else 255  # Hitam atau putih
        qr_pixels.append(pixel_value)
    
    # 6. Simpan QR Code hasil ekstraksi
    qr_img = Image.new('L', (qr_width, qr_height))
    qr_img.putdata(qr_pixels)
    
    output_filename = f"extracted_qr_{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, output_filename)
    qr_img.save(output_path)
    
    return output_path
```

**Penjelasan:**
- Ekstrak LSB dari setiap channel RGB secara berurutan
- Parse header 32-bit untuk mendapatkan dimensi QR Code (width + height)
- Rekonstruksi QR Code dari bit-bit yang diekstrak
- Terminator digunakan untuk mendeteksi akhir data

---

## 5. QR Code Reading

### Fungsi Utama: `read_qr()` di qr_utils.py

```python
def read_qr(image_path: str) -> list[str]:
    """Membaca data dari QR Code menggunakan OpenCV"""
    try:
        # Load image
        img = cv2.imread(image_path)
        
        # Inisialisasi QR Code detector
        detector = cv2.QRCodeDetector()
        
        # Deteksi dan decode QR Code
        data, vertices_array, straight_qrcode = detector.detectAndDecode(img)
        
        if data:
            return [data]  # Return sebagai list
        else:
            print(f"[!] Tidak dapat membaca QR Code dari: {image_path}")
            return []
            
    except Exception as e:
        print(f"[!] Error saat membaca QR Code: {e}")
        return []
```

**Penjelasan:**
- Menggunakan OpenCV `QRCodeDetector` untuk membaca QR Code
- Mendukung berbagai format gambar (PNG, JPG, dll.)
- Return data dalam bentuk list string

---

## 6. Flask Web Interface - Key Endpoints

### Generate QR Code Endpoint
```python
@app.route('/generate_qr', methods=['POST'])
def generate_qr_route():
    data = request.form.get('qrData')
    qr_filename = f"qr_{uuid.uuid4().hex}.png"
    qr_output_path = os.path.join(app.config['GENERATED_FOLDER'], qr_filename)
    
    # Panggil fungsi generate_qr
    args = ['generate_qr', '--data', data, '--output', qr_output_path]
    result = run_main_script(args)
    
    return jsonify({
        "success": True,
        "qr_url": f"/static/generated/{qr_filename}",
        "qr_filename": qr_filename
    })
```

### Embed Watermark Endpoint
```python
@app.route('/embed_document', methods=['POST'])
def embed_document_route():
    doc_file = request.files['docxFileEmbed']
    qr_file = request.files['qrFileEmbed']
    
    # Simpan file temporary
    doc_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], doc_filename)
    qr_temp_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    
    # Panggil fungsi embedding
    args = ['embed_docx', '--docx', doc_temp_path, '--qr', qr_temp_path, '--output', output_path]
    result = run_main_script(args)
    
    # Hitung metrik MSE dan PSNR
    metrics = calculate_metrics(doc_temp_path, output_path)
    
    return jsonify({
        "success": True,
        "download_url": f"/download_generated/{stego_doc_filename}",
        "mse": metrics["mse"],
        "psnr": metrics["psnr"]
    })
```

---

## Alur Lengkap Proses

1. **Input**: User upload dokumen (.docx/.pdf) dan input data untuk QR Code
2. **Generate QR**: Sistem membuat QR Code dari data input
3. **Extract Images**: Ekstrak semua gambar dari dokumen
4. **Watermarking**: Setiap gambar di-watermark dengan QR Code menggunakan LSB
5. **Replace Images**: Gambar hasil watermarking menggantikan gambar asli dalam dokumen
6. **Output**: Dokumen baru dengan watermark tersembunyi
7. **Validation**: User dapat meng-upload dokumen untuk ekstraksi dan verifikasi watermark

Setiap tahap menggunakan teknik LSB steganography yang memungkinkan penyisipan data secara invisible dengan degradasi kualitas minimal.