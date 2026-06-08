# 🤖 **AbsenChecker - Automation Cek Absensi HR Portal**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.21+-green?logo=selenium)](https://www.selenium.dev/)
[![APScheduler](https://img.shields.io/badge/APScheduler-3.10+-orange?logo=python)](https://apscheduler.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Sistem otomasi untuk cek absensi HR Portal dengan fitur **smart scheduling**. Program login otomatis ke HR Portal, download laporan kehadiran bulanan, analisis data absensi, dan kirim email ringkasan. Dilengkapi scheduler yang intelligent untuk run otomatis setiap akhir bulan (hari kerja terakhir) jam 8 pagi, dengan handling untuk weekend dan hari libur nasional.

---

## ✨ **Fitur Utama**

### 📊 Automation Absensi Bulanan
- ✅ Login otomatis ke HR Portal menggunakan Selenium WebDriver
- ✅ Download laporan kehadiran individu (format Excel .xls)
- ✅ Analisis data: hadir, mangkir, sakit, izin, terlambat, tidak scan
- ✅ Deteksi keterlambatan dengan perhitungan menit detail
- ✅ Kirim email ringkasan dengan file Excel attached
- ✅ Hapus file lokal otomatis setelah email terkirim

### 📅 **Smart Scheduling** ⭐ (FITUR BARU)
- ✅ Jalankan otomatis setiap akhir bulan pada jam **08:00** (8 pagi)
- ✅ Jika akhir bulan jatuh **weekend (Sabtu-Minggu)** → otomatis mundur ke hari kerja terakhir
- ✅ Jika hari kerja terakhir adalah **tanggal merah** → otomatis mundur ke hari kerja sebelumnya
- ✅ Support multiple periode sesuai kebutuhan

**Contoh Timeline:**
- Juni 2026: Berakhir Selasa 30 → Jalankan **30 Juni** jam 08:00
- Mei 2027: Berakhir Minggu 31 → Jalankan **29 Mei (Jumat)** jam 08:00
- April 2026: Jumat 10 libur (Jumat Agung) → Jalankan **9 April (Kamis)** jam 08:00

### 🗓️ **Holiday Detection** ⭐ (FITUR BARU)
- ✅ Database lengkap libur nasional Indonesia 2026-2027
- ✅ Otomatis skip job execution jika hari itu adalah tanggal merah
- ✅ Mudah extend untuk tahun-tahun berikutnya

### 📝 Logging & Monitoring
- ✅ Log file terpisah: `logs/absensi_checker.log` dan `logs/scheduler.log`
- ✅ Info detail kapan job akan jalan berikutnya
- ✅ Screenshot debug otomatis saat login/error
- ✅ Timestamp dan informasi ringkas

### 🔧 Production Ready
- ✅ Setup script otomatis
- ✅ Run scheduler script
- ✅ Konfigurasi via `.env` (aman, tidak di-commit)
- ✅ Error handling comprehensive
- ✅ Dokumentasi lengkap Bahasa Indonesia

---

## 📋 **Struktur Folder**

```
AbsenChecker/
├── absensi_checker.py          # Main scraper & email sender
├── analyzer.py                 # Parser & analisis Excel
├── config.py                   # Load konfigurasi .env
├── scheduler.py                # Smart scheduler dengan APScheduler ⭐
├── holidays.py                 # Database libur nasional ⭐
│
├── setup.sh                    # Script setup awal
├── run_scheduler.sh            # Script run scheduler di background ⭐
│
├── .env.example                # Template konfigurasi
├── .env                        # Konfigurasi aktual (JANGAN commit!)
├── requirements.txt            # Python dependencies
├── .gitignore                  # Abaikan file sensitif
├── README.md                   # File ini
│
├── logs/                       # Log files (auto-created)
│   ├── absensi_checker.log
│   └── scheduler.log
├── downloads/                  # Excel files (auto-created)
└── screenshots/                # Debug screenshots (auto-created)
```

---

## 🚀 **Quick Start**

### **Prasyarat**
- Python 3.8+
- Google Chrome browser
- pip (Python package manager)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/VikyMaulana-Ui/AbsenChecker.git
cd AbsenChecker
```

### **Step 2: Run Setup Script**
```bash
bash setup.sh
```

Script ini akan:
- Install Python dependencies
- Create virtual environment
- Buat folder `logs`, `downloads`, `screenshots`
- Copy `.env.example` ke `.env`

### **Step 3: Edit Konfigurasi (.env)**
```bash
nano .env
```

Isi dengan data asli kamu (lihat **Konfigurasi** section di bawah).

### **Step 4: Test Program**
```bash
# Activate virtual environment
source venv/bin/activate

# Test analisis file lokal (tanpa login)
python absensi_checker.py --analyze-only "Kehadiran_Individu_2026-06.xls"

# Test run lengkap (dengan login)
python absensi_checker.py --year 2026 --month 6
```

### **Step 5: Setup Scheduler (Otomatis)**
```bash
# Run scheduler di background
bash run_scheduler.sh

# Atau jalankan di foreground (untuk debug)
python scheduler.py
```

---

## ⚙️ **Konfigurasi (.env)**

Salin `.env.example` ke `.env` dan isi nilai berikut:

```env
# ── HR PORTAL ─────────────────────────────────
HR_PORTAL_URL=https://hrportal.perusahaanmu.co.id/login
ATTENDANCE_PAGE_URL=https://hrportal.perusahaanmu.co.id/attendance/individual
HR_USERNAME=nomor_pegawaimu
HR_PASSWORD=passwordmu

# ── SELECTOR HTML ─────────────────────────────
# Cek dengan F12 > Inspector di browser
LOGIN_FIELD_USERNAME=username
LOGIN_FIELD_PASSWORD=password
LOGIN_BUTTON_CSS=button[type=submit]

# ── EMAIL (SMTP) ───────────────────────────────
# Gmail: buat App Password di myaccount.google.com > Security
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=emailkamu@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
FROM_EMAIL=emailkamu@gmail.com
TO_EMAIL=emailkamu@gmail.com

# ── STORAGE ────────────────────────────────────
DOWNLOAD_DIR=/home/ubuntu/absensi_checker/downloads
```

### **Cara Cari CSS Selector:**

1. Buka HR Portal di Chrome
2. Tekan `F12` (buka Developer Tools)
3. Klik icon Inspector (panah + kotak)
4. Klik elemen input yang ingin dicari
5. Lihat HTML atribut `id=` atau `name=` atau `class=`

**Contoh:**
```html
<!-- Input username -->
<input type="text" id="username" placeholder="Username">
<!-- Maka: LOGIN_FIELD_USERNAME=username -->

<!-- Tombol login -->
<button class="btn-login" type="submit">Login</button>
<!-- Maka: LOGIN_BUTTON_CSS=button.btn-login -->
```

### **Setup Gmail App Password:**

1. Buka https://myaccount.google.com
2. Klik **Security** (sidebar kiri)
3. Scroll ke **App passwords**
4. Pilih app: **Mail** | Device: **Windows Computer** (atau sesuai device)
5. Google generate password 16 karakter
6. Copy-paste ke `.env` → `SMTP_PASSWORD=`

⚠️ **JANGAN** pakai password Gmail biasa! Gunakan App Password.

---

## 📖 **Cara Jalankan**

### **1. Manual (One-time Check)**

```bash
# Activate venv
source venv/bin/activate

# Bulan lalu (default)
python absensi_checker.py

# Periode spesifik
python absensi_checker.py --year 2026 --month 6

# Analisis file lokal saja (tanpa login)
python absensi_checker.py --analyze-only "Kehadiran_Individu_2026-06.xls"

# File terbaru
python absensi_checker.py --analyze-only latest
```

### **2. Scheduler (Otomatis Setiap Akhir Bulan)**

```bash
# Run di foreground (untuk development/debug)
python scheduler.py

# Run di background (untuk production)
bash run_scheduler.sh

# Lihat log real-time
tail -f logs/scheduler.log
```

### **3. Production Deployment (VPS/Server)**

#### **Linux (systemd):**

1. Buat file service:
```bash
sudo nano /etc/systemd/system/absen-checker.service
```

2. Isi dengan:
```ini
[Unit]
Description=AbsenChecker Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/AbsenChecker
ExecStart=/usr/bin/python3 /home/ubuntu/AbsenChecker/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable & start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable absen-checker
sudo systemctl start absen-checker

# Check status
sudo systemctl status absen-checker

# View logs
journalctl -u absen-checker -f
```

#### **Windows (NSSM):**

1. Download NSSM: https://nssm.cc/download
2. Extract ke folder, buka Command Prompt (Admin):
```batch
cd C:\nssm-2.24\win64
nssm install AbsenChecker "C:\Python311\python.exe" "C:\path\to\scheduler.py"
nssm start AbsenChecker
```

3. Check di Services (services.msc)

---

## 📊 **Expected Output**

### **Console Output:**
```
2026-06-30 08:00:00 [INFO] ======================================================================
2026-06-30 08:00:00 [INFO] 🤖 JOB DIMULAI: CEK ABSENSI BULAN LALU
2026-06-30 08:00:00 [INFO] ======================================================================
2026-06-30 08:00:00 [INFO] 📅 Hari ini: 30 Selasa Juni 2026
2026-06-30 08:00:00 [INFO] ✅ Hari kerja terakhir (tersedia): 30 Selasa
2026-06-30 08:00:00 [INFO] 📋 Periode yang diproses: 2026 Mei (05)
2026-06-30 08:00:00 [INFO] ----------
2026-06-30 08:00:05 [INFO] Chrome driver berhasil diinisialisasi.
2026-06-30 08:00:10 [INFO] Login berhasil. URL: https://...
2026-06-30 08:00:15 [INFO] Halaman absensi 2026-05 berhasil dimuat.
2026-06-30 08:00:20 [INFO] File berhasil diunduh: downloads/Kehadiran_Individu_2026-05.xls
2026-06-30 08:00:21 [INFO] Hasil: workdays=21, hadir=20, mangkir=1, sakit=0, izin=0, terlambat=3x
2026-06-30 08:00:25 [INFO] Email terkirim ke emailkamu@gmail.com
2026-06-30 08:00:26 [INFO] File Kehadiran_Individu_2026-05.xls dihapus setelah email terkirim.
2026-06-30 08:00:26 [INFO] ----------
2026-06-30 08:00:27 [INFO] ✅ JOB SELESAI DENGAN SUKSES!
2026-06-30 08:00:27 [INFO] ======================================================================
```

### **Email Format:**
```
📋 Laporan Kehadiran Individu — 2026-05

Noreg: 12345678
Periode: 2026-05

📊 Ringkasan:
├─ Hari Kerja: 21 hari
├─ Hadir: 20 hari ✅
├─ Mangkir: 1 hari ⚠️ PERHATIAN
├─ Sakit: 0 hari
├─ Izin: 0 hari
└─ Terlambat: 3 hari (total 45 menit)

🚨 Peringatan:
├─ Terdapat 1 hari MANGKIR/Alpha (tidak scan: 2026-05-15)
└─ Terlambat 3 kali (total 45 menit)

🕐 Detail Keterlambatan:
├─ 2026-05-01 → Standar 08:00, Aktual 08:15 (telat 15 menit)
├─ 2026-05-03 → Standar 08:00, Aktual 08:20 (telat 20 menit)
└─ 2026-05-05 → Standar 08:00, Aktual 08:10 (telat 10 menit)

[File Excel attached]
```

---

## 🗓️ **Smart Scheduler Logic**

### **Bagaimana Scheduler Bekerja:**

1. **Setiap hari jam 08:00**, scheduler check: "Apakah hari ini adalah hari kerja terakhir bulan yang tersedia?"
2. **Jika YA** → Jalankan `run_monthly_check()` untuk bulan lalu
3. **Jika TIDAK** → Skip, cek lagi besok hari

### **"Hari Kerja Terakhir yang Tersedia" = ?**

Artinya: **Hari kerja (Senin-Jumat) yang bukan weekend dan bukan hari libur nasional**

**Contoh Hitung:**
```
Juni 2026:
  Hari terakhir bulan = 30 Juni (Selasa)
  Apakah hari kerja? → YA (Selasa = Senin-Jumat)
  Apakah weekend? → TIDAK
  Apakah libur nasional? → TIDAK
  ✅ JALANKAN pada 30 Juni jam 08:00

Mei 2027:
  Hari terakhir bulan = 31 Mei (Minggu)
  Apakah hari kerja? → TIDAK (Minggu = weekend)
  Mundur ke 30 Mei (Sabtu) → TIDAK (Sabtu = weekend)
  Mundur ke 29 Mei (Jumat) → YA (Jumat = hari kerja, bukan libur)
  ✅ JALANKAN pada 29 Mei jam 08:00

April 2026:
  Hari terakhir bulan = 30 April (Rabu)
  Apakah hari kerja? → YA (Rabu = hari kerja)
  Apakah libur nasional? → TIDAK
  ✅ JALANKAN pada 30 April jam 08:00
  
  TAPI jika 30 April adalah libur nasional:
  Mundur ke 29 April (Selasa) → Cek lagi
  Mundur ke 28 April (Senin) → Cek lagi
  ... sampai ketemu hari kerja yang tidak libur
  ✅ JALANKAN pada tanggal tersebut
```

---

## 🔄 **Cara Update Libur Nasional**

1. Edit file `holidays.py`
2. Tambah tahun baru ke `HOLIDAYS` dict:

```python
HOLIDAYS = {
    2026: [...],  # existing
    2027: [...],  # existing
    2028: [       # ← TAHUN BARU
        (1, 1),    # Tahun Baru
        (2, 10),   # Imlek 2028 (perkiraan)
        # ... dst
    ],
}
```

3. Tambah nama libur ke `HOLIDAY_NAMES` dict:
```python
HOLIDAY_NAMES = {
    # ... existing
    (2, 10): "Hari Raya Imlek",  # ← TAMBAH
    # ... dst
}
```

---

## ❓ **FAQ & Troubleshooting**

### **Q: Berapa resource yang diperlukan?**
A: Minimal 512MB RAM, CPU 1 core. Untuk production, disarankan 1GB RAM, 2 core.

### **Q: Berapa lama proses cek absensi?**
A: Tergantung HR Portal. Biasanya 3-5 menit (login → download → analisis → email).

### **Q: Gimana jika terjadi error di tengah job?**
A: Error di-log ke `logs/scheduler.log`. Job akan retry otomatis sesuai schedule APScheduler.

### **Q: Bisa trigger manual di tengah bulan?**
A: Ya, gunakan: `python absensi_checker.py --year 2026 --month 5`

### **Q: Gimana jika overlap (manual + scheduler)?**
A: Aman. Setiap run download file baru, jadi tidak ada conflict.

### **Q: Support HR Portal lain?**
A: Ya, ubah URL & CSS selector di `.env` sesuai HR Portal target.

### **Q: Bisa tambah recipient email lain?**
A: Edit `TO_EMAIL` di `.env` untuk multiple emails: `email1@gmail.com,email2@gmail.com`

### **Error: ModuleNotFoundError: No module named 'selenium'**
```bash
pip install -r requirements.txt
```

### **Error: TimeoutError: File download tidak selesai**
- Ubah timeout di `absensi_checker.py` baris 180: `timeout=30` → `timeout=60`
- Check folder download permissions

### **Error: SMTPAuthenticationError**
- Pastikan **App Password** Gmail benar (bukan password biasa)
- Check 2FA aktif atau tidak
- Coba generate App Password baru

### **Error: Chrome driver not found**
```bash
pip install webdriver-manager
```

### **Error: Selector element tidak ditemukan**
- Buka HR Portal di Chrome
- Tekan F12, cek nama atribut input yang benar
- Update di `.env`

---

## 📝 **License**

MIT License - Bebas digunakan untuk kebutuhan apapun. Lihat file `LICENSE`.

---

## 🤝 **Contributing**

Contribusi welcome! Silakan:
1. Fork repository
2. Buat branch fitur: `git checkout -b feature/nama-fitur`
3. Commit changes: `git commit -m "Add feature X"`
4. Push ke branch: `git push origin feature/nama-fitur`
5. Buat Pull Request

---

## 📧 **Support & Contact**

Bila ada pertanyaan atau issue:
- Buka GitHub Issues
- Email: [contact info]
- Telegram/WhatsApp: [contact info]

---

**Dibuat dengan ❤️ untuk otomasi absensi yang lebih cerdas.**
