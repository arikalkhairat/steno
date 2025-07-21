# 🔐 QR Code Watermarking Tool - LSB Steganography

**Created by Arikal Khairat**

Aplikasi web Flask yang mudah digunakan untuk menyembunyikan dan mengekstrak watermark QR Code pada dokumen DOCX dan PDF menggunakan teknik LSB (Least Significant Bit) Steganography.

## 🎯 Apa itu Aplikasi Ini?

Aplikasi ini memungkinkan Anda untuk:
- **Menyembunyikan pesan rahasia** dalam gambar yang ada di dokumen Word/PDF
- **Memverifikasi keaslian dokumen** dengan mengecek watermark tersembunyi
- **Melindungi hak cipta** dokumen dengan tanda tangan digital invisible

### 🔍 Bagaimana Cara Kerjanya?
1. **LSB Steganography**: Mengubah bit terakhir pada pixel gambar (tidak terlihat mata)
2. **QR Code**: Pesan rahasia diubah menjadi QR Code terlebih dahulu
3. **Embedding**: QR Code disembunyikan ke dalam gambar-gambar di dokumen
4. **Extraction**: QR Code dapat diekstrak kembali untuk verifikasi

## 🚀 Fitur Utama (Yang Bisa Dilakukan)

### 1. 📝 Generate QR Code
**Apa yang dilakukan**: Membuat kode QR dari teks yang Anda masukkan
- ✅ Ketik pesan apa saja (nama, tanggal, kode rahasia, dll)
- ✅ Otomatis diubah menjadi gambar QR Code (.png)
- ✅ Siap digunakan untuk watermarking
- ✅ Nama file otomatis unik (tidak bentrok)

**Contoh penggunaan**: 
- Membuat QR berisi "Copyright 2025 - Arikal Khairat"
- Membuat QR berisi nomor dokumen "DOC-001-2025"

### 2. 🔒 Embed Watermark (Sembunyikan Pesan)
**Apa yang dilakukan**: Menyembunyikan QR Code ke dalam dokumen
- ✅ **DOCX Support**: Bisa untuk file Word (.docx)
- ✅ **PDF Support**: Bisa untuk file PDF  
- ✅ Otomatis mencari semua gambar dalam dokumen
- ✅ Menyembunyikan QR Code di setiap gambar
- ✅ Gambar terlihat sama (tidak ada perubahan visual)
- ✅ Menghitung kualitas hasil (MSE & PSNR untuk DOCX)

**Contoh penggunaan**:
- Dokumen kontrak → disembunyikan QR "KONTRAK-ASLI-2025"
- Sertifikat → disembunyikan QR "CERT-VALID-12345"

### 3. 🔍 Extract/Validasi Dokumen (Cek Keaslian)
**Apa yang dilakukan**: Mengecek apakah dokumen asli atau palsu
- ✅ Upload dokumen yang ingin dicek
- ✅ Otomatis ekstrak semua QR Code tersembunyi
- ✅ Tampilkan isi pesan rahasia
- ✅ Bisa detect multiple QR dalam satu dokumen
- ✅ Warning jika dokumen tidak ada gambar

**Contoh penggunaan**:
- Cek sertifikat → muncul "CERT-VALID-12345" = ASLI
- Cek sertifikat → tidak muncul apa-apa = PALSU atau DIUBAH

## 🛠️ Teknologi yang Digunakan (Untuk Developer)

### Backend (Server)
- **Flask**: Framework web Python yang ringan dan mudah
- **LSB Steganography**: Teknik menyembunyikan data di bit terakhir pixel
- **UUID**: Sistem penamaan file otomatis yang unik

### Document Processing (Pengolah Dokumen)
- **python-docx**: Library untuk membaca/menulis file Word (.docx)
- **PyMuPDF (fitz)**: Library untuk membaca/menulis file PDF
- **Pillow (PIL)**: Library untuk edit gambar (resize, convert, dll)

### QR Code & Image
- **qrcode**: Membuat QR Code dari text
- **pyzbar**: Membaca QR Code dari gambar
- **NumPy**: Perhitungan matematika untuk MSE/PSNR

### Frontend (Tampilan Web)
- **HTML5, CSS3, JavaScript**: Interface web modern
- **AJAX**: Upload file tanpa refresh halaman

## 🌐 Halaman Web yang Tersedia

### Halaman Utama
- **`/`** → Halaman utama dengan 3 fitur lengkap
- **`/process_details`** → Penjelasan detail cara kerja aplikasi

### API untuk Generate & Process
- **`/generate_qr`** → Buat QR Code dari text
- **`/embed_document`** → Sembunyikan QR ke dokumen
- **`/extract_document`** → Ekstrak QR dari dokumen

### Download & Management
- **`/download_generated/<nama_file>`** → Download file hasil proses
- **`/download_documents/<nama_file>`** → Download dokumen permanen
- **`/list_documents`** → Lihat daftar semua dokumen yang pernah diproses

## 📁 Struktur Folder Project

```
/workspaces/steno/                    # 📂 Folder utama project
├── 🖥️ app.py                        # Server web Flask (MAIN FILE)
├── ⚙️ main.py                       # Functions inti steganography
├── 🔧 lsb_steganography.py          # Logic LSB steganography
├── 📱 qr_utils.py                   # Functions QR Code
├── 📋 requirements.txt              # Daftar library yang dibutuhkan
├── 📖 README.md                     # File dokumentasi ini
│
├── 🌐 templates/                    # 📂 Template HTML untuk web
│   ├── index.html                   #    🏠 Halaman utama
│   └── process_details.html         #    📄 Halaman detail proses
│
├── 📁 static/                       # 📂 File upload & hasil
│   ├── uploads/                     #    ⬆️ File yang diupload user (temporary)
│   └── generated/                   #    ⬇️ File hasil proses (QR, dokumen)
│
├── 🏛️ public/                       # 📂 Penyimpanan permanen
│   └── documents/                   #    💾 Dokumen final yang sudah diproses
│
└── 🗂️ __pycache__/                  # 📂 Cache Python (otomatis)
```

### 📝 Penjelasan Setiap Folder:

**📂 static/uploads/** → File yang baru diupload user (sementara, akan dihapus)
**📂 static/generated/** → QR Code dan dokumen hasil proses 
**📂 public/documents/** → Dokumen final disimpan permanen di sini
**📂 templates/** → File HTML untuk tampilan web

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

## ⚙️ Pengaturan Aplikasi (Sudah Diatur Otomatis)

- **📏 Batas Upload**: Maksimal 16MB per file
- **📄 Format Dokumen**: .docx (Word), .pdf (PDF)
- **🖼️ Format QR Code**: .png saja
- **🔌 Port Otomatis**: 5001, 5002, 5003, 5004, 5005 (coba berurutan)
- **🐛 Debug Mode**: Aktif (untuk development)
- **🗑️ Auto Cleanup**: File temporary otomatis dihapus

## 🚀 Cara Install & Menjalankan (Step by Step)

### 📱 Windows (Langkah Mudah)

#### Step 1: Install Python
```bash
# Cek apakah Python sudah ada
python --version

# Jika belum ada, download dari https://python.org
# ⚠️ PENTING: Centang "Add Python to PATH" saat install
```

#### Step 2: Download Project
```bash
# Download project (ganti <repository-url> dengan link GitHub yang benar)
git clone <repository-url>
cd steno

# ATAU download ZIP dari GitHub, lalu extract
```

#### Step 3: Buat Virtual Environment (Ruang Terisolasi)
```bash
# Buat environment baru (seperti folder khusus untuk project ini)
python -m venv .venv

# Aktifkan environment
.venv\Scripts\activate
# 👆 Jika berhasil, akan ada "(venv)" di depan prompt
```

#### Step 4: Install Library yang Dibutuhkan
```bash
# Update pip dulu
pip install --upgrade pip

# Install semua library
pip install -r requirements.txt
# 👆 Ini akan download Flask, PIL, numpy, dll secara otomatis
```

#### Step 5: Jalankan Aplikasi
```bash
python app.py
# 👆 Server akan start dan mencari port kosong (5001-5005)
```

#### Step 6: Buka di Browser
```
http://localhost:5001
# 👆 Atau port lain yang muncul di terminal
```

#### Step 7: Stop Aplikasi
```bash
# Tekan Ctrl + C di terminal
# Lalu ketik:
deactivate
# 👆 Untuk keluar dari virtual environment
```

### 🐧 Ubuntu/Linux (Langkah Mudah)

#### Step 1: Install Python & Tools
```bash
# Update sistem dulu
sudo apt update

# Install Python dan tools yang dibutuhkan
sudo apt install python3 python3-pip python3-venv git
```

#### Step 2: Download Project
```bash
# Clone project
git clone <repository-url>
cd steno
```

#### Step 3: Buat Virtual Environment
```bash
# Buat environment
python3 -m venv .venv

# Aktifkan environment
source .venv/bin/activate
# 👆 Jika berhasil, akan ada "(venv)" di depan prompt
```

#### Step 4: Install System Dependencies (Untuk PyMuPDF)
```bash
# Install library system yang dibutuhkan
sudo apt install -y build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev
```

#### Step 5: Install Python Libraries
```bash
# Update pip
pip install --upgrade pip

# Install semua library
pip install -r requirements.txt
```

#### Step 6: Jalankan Aplikasi
```bash
python app.py
# 👆 Server akan start di port 5001-5005
```

#### Step 7: Buka di Browser
```
http://localhost:5001
# 👆 Atau port yang muncul di terminal
```

#### Step 8: Stop Aplikasi
```bash
# Tekan Ctrl + C untuk stop
deactivate  # Keluar dari virtual environment
```

### 🚀 One-Liner Ubuntu (Copy-Paste Langsung)
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev && git clone <repository-url> && cd steno && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && python app.py
```

### 🍎 macOS (Langkah Mudah)

#### Step 1: Install Tools yang Dibutuhkan
```bash
# Install Homebrew jika belum ada (package manager untuk Mac)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python dan Git
brew install python3 git
```

#### Step 2-7: Sama seperti Linux
```bash
# Download, setup, dan jalankan (sama seperti Ubuntu di atas)
git clone <repository-url>
cd steno
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## 📖 Cara Menggunakan Aplikasi (Tutorial Lengkap)

### 🎯 Skenario 1: Membuat Watermark untuk Sertifikat

#### Langkah 1: Buat QR Code
1. **Buka browser** ke `http://localhost:5001`
2. **Di bagian "Generate QR Code":**
   - Ketik: `SERTIFIKAT-VALID-2025-ARIKAL`
   - Klik **"Generate QR Code"**
   - QR Code akan muncul di layar
   - Klik **Download** untuk simpan file .png

#### Langkah 2: Sembunyikan QR ke Sertifikat
1. **Di bagian "Embed Watermark":**
   - **Upload Dokumen**: Pilih file sertifikat (.docx atau .pdf)
   - **Upload QR Code**: Pilih QR yang baru dibuat
   - Klik **"Sisipkan Watermark"**
   - Tunggu proses selesai (beberapa detik)
   - **Download** sertifikat yang sudah di-watermark

#### Langkah 3: Test Validasi
1. **Di bagian "Validasi Dokumen":**
   - **Upload** sertifikat yang sudah di-watermark
   - Klik **"Validasi Dokumen"**
   - Akan muncul: `SERTIFIKAT-VALID-2025-ARIKAL` ✅ = ASLI

### 🎯 Skenario 2: Cek Dokumen Palsu
1. **Upload dokumen** yang mencurigakan
2. **Klik Validasi**
3. **Jika tidak muncul QR** atau **QR berbeda** = DOKUMEN PALSU/DIUBAH ❌

## � Bagaimana Aplikasi Bekerja? (Detail Teknis Sederhana)

### 🔄 Alur Kerja Aplikasi:
```
1. User upload file 📁
2. File disimpan temporary dengan nama unik 🔄
3. Aplikasi baca gambar dari dokumen 📖
4. QR Code disembunyikan ke gambar pakai LSB 🔒
5. Gambar yang sudah di-watermark dikembalikan ke dokumen ✅
6. File temporary dihapus otomatis 🗑️
7. User download hasil ⬇️
```

### 🧠 LSB Steganography (Penjelasan Mudah):
- **LSB = Least Significant Bit** (bit terakhir)
- Setiap pixel gambar punya 3 warna: Merah, Hijau, **Biru**
- Kita ubah bit terakhir di channel **Biru** saja
- Mata manusia tidak bisa melihat perubahan sekecil itu
- Tapi komputer bisa baca dan ekstrak pesannya

**Contoh:**
```
Pixel Biru Original: 11011010 (218)
Pixel Biru Modified: 11011011 (219) ← Beda 1 angka saja!
Mata manusia: Sama saja, tidak keliatan
Komputer: Bisa deteksi ada data tersembunyi
```

### 📊 Quality Metrics (MSE & PSNR):
- **MSE (Mean Square Error)**: Seberapa beda gambar asli vs watermarked
  - Semakin kecil = semakin bagus (hampir sama)
- **PSNR (Peak Signal-to-Noise Ratio)**: Kualitas gambar
  - Semakin besar = semakin bagus (>30 dB = excellent)

## 🎯 Contoh Penggunaan di Dunia Nyata

### 1. 🏆 **Sertifikat & Ijazah**
**Problem**: Banyak ijazah palsu beredar
**Solusi**: 
- Universitas embed QR berisi "UNIV-XYZ-2025-VALID"
- HR tinggal scan → jika muncul QR yang benar = ijazah asli

### 2. 📄 **Kontrak Bisnis**
**Problem**: Kontrak bisa diubah tanpa sepengetahuan
**Solusi**:
- Embed QR berisi hash dokumen asli
- Jika ada yang ubah kontrak → QR tidak match = ada perubahan

### 3. 🏥 **Dokumen Medis**
**Problem**: Resep atau hasil lab bisa dipalsukan  
**Solusi**:
- Rumah sakit embed QR berisi kode verifikasi
- Apotek/dokter lain bisa validasi keaslian

### 4. � **Dokumen Keuangan**
**Problem**: Laporan keuangan bisa dimanipulasi
**Solusi**:
- Akuntan embed QR berisi signature digital
- Auditor bisa cek keaslian laporan

### 5. 🎓 **Tugas & Skripsi** 
**Problem**: Plagiarisme dan copy-paste
**Solusi**:
- Mahasiswa embed QR berisi nama + tanggal submit
- Dosen bisa track siapa yang submit duluan

## ⚠️ Batasan & Yang Perlu Diperhatikan

### 📏 **Batasan File**
- **Ukuran maksimal**: 16MB per file (bisa diubah di kode)
- **Format dokumen**: Hanya .docx dan .pdf
- **Format QR**: Hanya .png (tidak bisa .jpg atau .gif)

### 🖼️ **Batasan Gambar**
- **Dokumen harus ada gambar**: Jika tidak ada gambar, tidak bisa di-watermark
- **Kualitas tergantung gambar asli**: Gambar blur → hasil juga blur
- **QR otomatis di-resize**: Jika gambar terlalu kecil untuk QR

### 🔌 **Batasan Teknis**
- **Port 5001-5005**: Jika semua terpakai, aplikasi tidak bisa jalan
- **PDF Metrics**: Belum ada MSE/PSNR untuk PDF (hanya DOCX)
- **Browser modern**: Perlu JavaScript aktif

### 💾 **File Management**
- **Auto cleanup**: File temporary otomatis dihapus (jangan khawatir)
- **Backup**: File asli tidak berubah, yang di-watermark adalah copy-an

## 🆘 Troubleshooting (Cara Mengatasi Masalah)

### ❌ **Error: "python not found"**
**Solusi:**
```bash
# Windows: Install Python dari python.org dengan centang "Add to PATH"
# Ubuntu: sudo apt install python3
# macOS: brew install python3
```

### ❌ **Error: "Permission denied"**
**Solusi:**
```bash
# Jangan pakai sudo, gunakan virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### ❌ **Error: "Port already in use"**
**Solusi:** Aplikasi otomatis cari port kosong (5001-5005), tunggu saja

### ❌ **Error: "No module named 'cv2' atau library lain"**
**Solusi:**
```bash
# Pastikan virtual environment aktif (ada tulisan "venv" di terminal)
# Lalu install ulang
pip install -r requirements.txt
```

### ❌ **Error: "Dokumen tidak mengandung gambar"**
**Solusi:** 
- Tambahkan gambar ke dokumen Word/PDF dulu
- Atau gunakan dokumen lain yang sudah ada gambarnya

### ❌ **Error: "QR Code tidak terbaca"**
**Solusi:**
- Pastikan file QR format .png
- Coba buat ulang QR Code
- Pastikan gambar tidak blur

### ❌ **Error saat install di Ubuntu**
**Solusi:**
```bash
# Install dependencies system dulu
sudo apt update
sudo apt install build-essential python3-dev libffi-dev libjpeg-dev zlib1g-dev
```

## � Pengembangan Selanjutnya (Future Updates)

### 📋 **Yang Akan Ditambahkan:**
- [ ] **Format lebih banyak**: Support .ppt, .odt, .txt
- [ ] **Multiple QR**: Bisa embed beberapa QR dalam satu dokumen  
- [ ] **Enkripsi advanced**: QR Code di-encrypt dulu sebelum di-embed
- [ ] **Batch processing**: Upload banyak file sekaligus
- [ ] **API REST**: Untuk integrasi dengan aplikasi lain
- [ ] **Real-time progress**: Progress bar saat processing file besar
- [ ] **User login**: Sistem user dengan history dokumen
- [ ] **Database**: Simpan history di database, bukan folder
- [ ] **Folder management**: Organize dokumen dalam folder-folder

### 🎯 **Kontribusi Welcome!**
Jika Anda developer dan ingin bantu:
1. Fork repository ini
2. Buat branch baru untuk fitur Anda
3. Submit pull request
4. Atau buat issue untuk bug report/feature request

## �‍💻 About Developer

**Arikal Khairat**
- 🎓 Specialist dalam Digital Steganography  
- 💻 Expert implementasi LSB (Least Significant Bit)
- 🔐 Fokus pada Document Security Solutions
- 📧 Contact: [Your Email Here]
- 🌐 GitHub: [Your GitHub Profile]

### 🙏 **Acknowledgments**
Terima kasih untuk semua library open source yang digunakan:
- Flask Framework Team
- Pillow (PIL) Contributors  
- PyMuPDF Team
- python-docx Developers
- qrcode & pyzbar Libraries

## � **License & Disclaimer**

⚖️ **Educational Purpose**: Project ini dibuat untuk tujuan edukasi dan penelitian

⚠️ **Disclaimer**: 
- Gunakan dengan bijak dan bertanggung jawab
- Hormati hak cipta dan hukum yang berlaku
- Developer tidak bertanggung jawab atas penyalahgunaan
- Pastikan Anda punya hak untuk memodifikasi dokumen yang diproses

📜 **License**: MIT License (atau sesuai kebutuhan project Anda)

---

## 🎉 **Selamat Mencoba!**

🚀 **Quick Start:**
1. Install Python
2. Clone project  
3. `python -m venv .venv`
4. `source .venv/bin/activate` (Linux/Mac) atau `.venv\Scripts\activate` (Windows)
5. `pip install -r requirements.txt`
6. `python app.py`
7. Buka `http://localhost:5001`

---
*"Securing documents with invisible watermarks through advanced LSB steganography"* ✨

**🏠 Repository**: `/workspaces/steno/`  
**🖥️ Main Application**: `app.py` (Flask Web Server)  
**🔧 Development Mode**: Multi-port auto-detection (5001-5005)
**📅 Last Updated**: July 2025
