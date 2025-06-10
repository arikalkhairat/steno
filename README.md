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

### 📱 Windows

1. **Pastikan Python 3.8+ terinstall:**
```bash
python --version
# Jika belum ada, download dari https://python.org
```

2. **Clone repository:**
```bash
git clone <repository-url>
cd ika-sayangg
```

3. **Buat virtual environment:**
```bash
python -m venv .venv
```

4. **Aktivasi virtual environment:**
```bash
# Windows Command Prompt
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Git Bash
source .venv/Scripts/activate
```

5. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

6. **Jalankan aplikasi:**
```bash
python app.py
```

7. **Buka browser:**
```
http://localhost:5000
```

8. **Untuk menghentikan:**
```bash
# Tekan Ctrl+C untuk stop server
# Deactivate virtual environment
deactivate
```

### 🐧 Ubuntu/Linux

1. **Update sistem dan install Python:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

2. **Clone repository:**
```bash
git clone <repository-url>
cd ika-sayangg
```

3. **Buat virtual environment:**
```bash
python3 -m venv .venv
```

4. **Aktivasi virtual environment:**
```bash
source .venv/bin/activate
```

5. **Install system dependencies untuk PyMuPDF:**
```bash
sudo apt install -y build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev
```

6. **Install Python dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

7. **Jalankan aplikasi:**
```bash
python app.py
```

8. **Buka browser:**
```
http://localhost:5000
```

9. **Untuk menghentikan aplikasi:**
```bash
# Tekan Ctrl+C untuk stop server
# Deactivate virtual environment
deactivate
```

### 🚀 Quick Start Ubuntu (One-liner)
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev && git clone <repository-url> && cd ika-sayangg && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && python app.py
```

### 🍎 macOS

1. **Install Homebrew (jika belum ada):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python dan dependencies:**
```bash
brew install python3 git
```

3. **Clone repository:**
```bash
git clone <repository-url>
cd ika-sayangg
```

4. **Buat virtual environment:**
```bash
python3 -m venv .venv
```

5. **Aktivasi virtual environment:**
```bash
source .venv/bin/activate
```

6. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

7. **Jalankan aplikasi:**
```bash
python app.py
```

8. **Untuk menghentikan:**
```bash
# Tekan Ctrl+C untuk stop server
deactivate
```

### 🐧 Distribusi Linux Lain

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip python3-devel gcc git
# Fedora
sudo dnf install python3 python3-pip python3-devel gcc git

git clone <repository-url>
cd ika-sayangg
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git base-devel
git clone <repository-url>
cd ika-sayangg
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

**Alpine Linux:**
```bash
sudo apk add python3 python3-dev py3-pip git gcc musl-dev libffi-dev jpeg-dev zlib-dev
git clone <repository-url>
cd ika-sayangg
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## 🔄 Manajemen Virtual Environment

### Mengaktifkan Virtual Environment

**Windows:**
```bash
# Command Prompt
.venv\Scripts\activate

# PowerShell
.venv\Scripts\Activate.ps1

# Git Bash
source .venv/Scripts/activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### Menambah Dependencies Baru

```bash
# Pastikan virtual environment aktif
source .venv/bin/activate  # Linux/macOS
# atau .venv\Scripts\activate  # Windows

# Install package baru
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Menghapus Virtual Environment

```bash
# Deactivate dulu
deactivate

# Hapus folder .venv
rm -rf .venv  # Linux/macOS
# atau rmdir /s .venv  # Windows
```

### Recreate Virtual Environment

```bash
# Hapus .venv lama
rm -rf .venv

# Buat ulang
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 📝 Catatan Penting

- **Folder `.venv`** sudah ada di `.gitignore` untuk menghindari commit virtual environment
- Selalu aktifkan virtual environment sebelum install/menjalankan aplikasi
- Gunakan `pip freeze > requirements.txt` untuk update dependencies
- Virtual environment bersifat lokal per project dan tidak portable

## 🚀 Production Deployment

### Menggunakan Gunicorn (Ubuntu/Linux)

1. **Aktivasi virtual environment:**
```bash
source .venv/bin/activate
```

2. **Install Gunicorn:**
```bash
pip install gunicorn
```

3. **Jalankan dengan Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. **Dengan Nginx (optional):**
```bash
sudo apt install nginx
# Configure nginx reverse proxy ke localhost:5000
```

### Menggunakan Docker

1. **Buat Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev \
    && pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

2. **Build dan Run:**
```bash
docker build -t qr-watermarking .
docker run -p 5000:5000 qr-watermarking
```

### Systemd Service (Ubuntu)

1. **Buat service file:**
```bash
sudo nano /etc/systemd/system/qr-watermarking.service
```

2. **Isi service file:**
```ini
[Unit]
Description=QR Watermarking Tool
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ika-sayangg
Environment=PATH=/path/to/ika-sayangg/.venv/bin
ExecStart=/path/to/ika-sayangg/.venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Enable dan start:**
```bash
sudo systemctl enable qr-watermarking
sudo systemctl start qr-watermarking
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

## 🔧 Troubleshooting

### Ubuntu/Linux Issues

**Error: "Python.h: No such file or directory"**
```bash
sudo apt install python3-dev
```

**Error: "Failed building wheel for PyMuPDF"**
```bash
sudo apt install build-essential python3-dev libffi-dev
pip install --upgrade pip setuptools wheel
pip install PyMuPDF
```

**Error: "Permission denied" saat install**
```bash
# Gunakan virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Error: "zbar shared library not found"**
```bash
sudo apt install libzbar0
```

**Error: "No module named '_tkinter'"**
```bash
sudo apt install python3-tk
```

### Windows Issues

**Error: "Microsoft Visual C++ 14.0 is required"**
- Download dan install Microsoft C++ Build Tools
- Atau install Visual Studio Community

**Error: "pip is not recognized"**
- Pastikan Python dan pip sudah ada di PATH
- Reinstall Python dengan opsi "Add to PATH"

### General Issues

**Port 5000 sudah digunakan:**
```bash
# Ganti port di app.py
app.run(host='0.0.0.0', port=8080, debug=True)
```

**Memory error saat processing PDF besar:**
- Gunakan PDF dengan ukuran lebih kecil (<16MB)
- Compress PDF terlebih dahulu

**QR Code tidak terbaca:**
- Pastikan kualitas gambar cukup baik
- Coba dengan gambar yang lebih besar
- Periksa format file (harus PNG untuk QR input)

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
