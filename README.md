# QR Code Watermarking Tool - LSB Steganography

**Created by Arikal Sayangg ❤️**

Alat canggih untuk menyisipkan dan mengekstrak watermark QR Code pada dokumen DOCX dan PDF menggunakan teknik LSB (Least Significant Bit) Steganography.

## 🚀 Fitur Utama

### 1. Generate QR Code
- Membuat QR Code dari teks yang diinginkan
- Format output: PNG dengan resolusi tinggi
- Dapat langsung digunakan sebagai watermark

### 2. Embed Watermark (DOCX & PDF)
- **DOCX Support**: Menyisipkan watermark ke semua gambar dalam dokumen Word
- **PDF Support**: Menyisipkan watermark ke semua gambar dalam dokumen PDF  
- Menggunakan teknik LSB pada channel biru untuk menjaga kualitas visual
- Automatic QR code resizing jika gambar terlalu kecil
- Real-time quality metrics (MSE & PSNR) untuk DOCX
- Preview before/after dengan analisis detail

### 3. Validasi Dokumen (DOCX & PDF)
- Ekstraksi watermark QR Code dari dokumen
- Verifikasi keaslian dokumen
- Mendukung multiple QR codes dalam satu dokumen

## 🛠️ Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **Steganography**: LSB pada channel biru gambar
- **Document Processing**: 
  - python-docx untuk file DOCX
  - PyMuPDF untuk file PDF
- **QR Code**: qrcode & pyzbar libraries
- **Image Processing**: Pillow (PIL)
- **Math**: NumPy untuk kalkulasi MSE/PSNR
- **Frontend**: Modern HTML5, CSS3, JavaScript

## 📋 Requirements

```
Flask==2.3.3
python-docx==0.8.11
qrcode==7.4.2
Pillow==10.0.0
pyzbar==0.1.9
numpy==1.24.3
PyMuPDF==1.23.5
```

## 🚀 Instalasi & Menjalankan

1. **Clone repository:**
```bash
git clone <repository-url>
cd ika-sayangg
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Jalankan aplikasi:**
```bash
python app.py
```

4. **Buka browser:**
```
http://localhost:5000
```

## 📖 Cara Penggunaan

### Via Web Interface

1. **Generate QR Code**
   - Masukkan teks yang ingin di-encode
   - Klik "Generate QR Code"
   - Download hasil QR Code

2. **Embed Watermark**
   - Upload dokumen DOCX atau PDF
   - Upload QR Code PNG
   - Klik "Sisipkan Watermark"
   - Download dokumen yang sudah di-watermark

3. **Validasi Dokumen**
   - Upload dokumen DOCX atau PDF yang sudah di-watermark
   - Klik "Validasi Dokumen"
   - Lihat hasil ekstraksi QR Code

### Via Command Line

```bash
# Generate QR Code
python main.py generate_qr --data "Arikal Sayangg" --output qr.png

# Embed watermark ke DOCX
python main.py embed_docx --docx document.docx --qr qr.png --output watermarked.docx

# Embed watermark ke PDF
python main.py embed_pdf --pdf document.pdf --qr qr.png --output watermarked.pdf

# Extract watermark dari DOCX
python main.py extract_docx --docx watermarked.docx --output_dir extracted/

# Extract watermark dari PDF
python main.py extract_pdf --pdf watermarked.pdf --output_dir extracted/
```

## 🔬 Detail Teknis

### LSB Steganography
- Modifikasi bit terakhir (LSB) pada channel biru pixel
- Minimal impact pada kualitas visual gambar
- Robust terhadap kompresi ringan

### Quality Metrics (DOCX)
- **MSE (Mean Square Error)**: Mengukur perbedaan pixel
- **PSNR (Peak Signal-to-Noise Ratio)**: Mengukur kualitas gambar
- Automatic quality assessment dan interpretasi

### PDF Processing
- Extract images dari semua halaman PDF
- Convert berbagai format gambar ke PNG
- Preserve layout dan posisi gambar
- Replace images dengan versi watermarked

### Error Handling
- Deteksi dokumen tanpa gambar
- Handle berbagai format gambar
- Automatic QR code resizing
- Graceful error recovery

## 📁 Struktur Project

```
ika-sayangg/
├── app.py                 # Flask web application
├── main.py               # CLI interface & core functions
├── lsb_steganography.py  # LSB steganography implementation
├── qr_utils.py           # QR code utilities
├── requirements.txt      # Python dependencies
├── README.md            # Documentation
├── templates/
│   └── index.html       # Web interface
├── static/
│   ├── uploads/         # Temporary uploads
│   └── generated/       # Generated files
└── public/
    └── documents/       # Processed documents
```

## 🎯 Use Cases

1. **Document Authentication**: Verifikasi keaslian dokumen penting
2. **Copyright Protection**: Watermarking untuk dokumen rahasia
3. **Digital Forensics**: Tracking sumber dokumen
4. **Academic Integrity**: Mencegah plagiarism dokumen
5. **Legal Documents**: Autentikasi kontrak dan surat resmi

## ⚠️ Batasan

1. **File PDF**: MSE/PSNR calculation belum diimplementasikan
2. **Image Quality**: Hasil bergantung kualitas gambar asli
3. **File Size**: Terbatas oleh kapasitas server (16MB default)
4. **QR Size**: QR Code akan di-resize otomatis jika gambar terlalu kecil

## 🔮 Future Development

- [ ] Support format dokumen lain (PPT, ODT)
- [ ] Multiple watermark patterns
- [ ] Advanced encryption untuk QR content
- [ ] Batch processing multiple files
- [ ] API endpoints untuk integrasi
- [ ] PDF quality metrics implementation

## 👨‍💻 Developer

**Arikal Sayangg**
- Specialized in Digital Steganography
- LSB Implementation Expert
- Document Security Solutions

## 📄 License

This project is created for educational and research purposes. Please use responsibly and respect copyright laws.

---
*"Securing documents with invisible watermarks"* ✨
