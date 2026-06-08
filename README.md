# AbsenChecker

Automation tool untuk mengecek attendance Toyota HR Portal. Program bisa login ke HR Portal, membuka halaman Attendance, mengunduh laporan `Kehadiran_Individu_*.xls*`, menganalisis data absensi, mengirim email laporan, dan berjalan otomatis lewat smart scheduler.

## Fitur

- Full mode: login HR Portal, download Excel, analyze, send email.
- Analyze-only mode: analyze file Excel lokal tanpa Selenium.
- Smart scheduler: cek setiap hari jam 08:00 WIB dan hanya menjalankan job pada hari kerja terakhir yang tersedia di bulan berjalan.
- Holiday loader: membaca libur nasional dari JSON lokal di `data/holidays_ID_<year>.json`.
- Folder runtime `logs/`, `screenshots/`, dan `downloads/` dibuat otomatis.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Isi kredensial asli hanya di `.env`. Jangan isi atau commit kredensial asli ke `.env.example`.

## Konfigurasi `.env`

`.env.example` sudah berisi URL dan selector HR Portal yang dikonfirmasi:

```env
HR_PORTAL_URL=https://hrportal.toyota.co.id/Login
ATTENDANCE_PAGE_URL=https://hrportal.toyota.co.id/Attendance
LOGIN_FIELD_USERNAME=tfUsername
LOGIN_FIELD_PASSWORD=tfPassword
LOGIN_BUTTON_CSS=#login-button
PERIODE_FIELD_ID=periode-text
SEARCH_BUTTON_ID=search-button
DOWNLOAD_BUTTON_ID=download-button
DOWNLOAD_DIR=downloads
```

Lengkapi juga:

- `HR_USERNAME` dan `HR_PASSWORD`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- `FROM_EMAIL` dan `TO_EMAIL`
- Opsional: `CC_EMAIL`, `BCC_EMAIL`

Multiple recipient dipisahkan koma, misalnya `TO_EMAIL=a@example.com,b@example.com`.

## Holiday Data

Tambahkan file berikut:

```text
data/holidays_ID_2026.json
data/holidays_ID_2027.json
```

Format JSON:

```json
[
  {
    "date": "2026-01-01",
    "name": "Hari tahun baru",
    "type": "public"
  }
]
```

Hanya item dengan `"type": "public"` yang dianggap hari libur.

## Validasi dan Test

Compile file utama:

```bash
python -m py_compile config.py
python -m py_compile holidays.py
python -m py_compile absensi_checker.py
python -m py_compile scheduler.py
```

Atau sekaligus:

```bash
python -m py_compile config.py holidays.py absensi_checker.py scheduler.py
```

Test holiday loader:

```bash
python holidays.py
```

Test analyze-only dengan file terbaru di folder kerja atau `downloads/`:

```bash
python absensi_checker.py --analyze-only latest
```

Test full manual run untuk attendance Mei 2026:

```bash
python absensi_checker.py --year 2026 --month 5
```

Run scheduler:

```bash
python scheduler.py
```

## Scheduler

`scheduler.py` memakai timezone `Asia/Jakarta`, menjadwalkan trigger harian jam 08:00 WIB, dan hanya menjalankan `run_monthly_check(year=year, month=month)` jika hari ini adalah hari kerja terakhir yang tersedia pada bulan berjalan.

Hari kerja terakhir yang tersedia berarti:

- Senin sampai Jumat
- bukan public holiday dari file JSON lokal di `data/`

Saat valid, scheduler memproses attendance bulan sebelumnya. Contoh: jika scheduler berjalan pada akhir Juni 2026, periode yang diproses adalah Mei 2026.

## Catatan Manual

- Buat `.env` dari `.env.example`.
- Isi real HR credentials hanya di `.env`.
- Tambahkan `data/holidays_ID_2026.json` dan `data/holidays_ID_2027.json`.
- Verifikasi selector HR Portal jika UI portal berubah.
- Test analyze-only dengan file Excel asli dari HR Portal.
- Test full manual run sebelum mengandalkan scheduler.

## Troubleshooting

Jika download timeout, naikkan `DOWNLOAD_TIMEOUT` di `.env`.

Jika login gagal, cek kredensial dan selector login di `.env`.

Jika analyze-only gagal membaca Excel, pastikan file `.xls` memakai `xlrd` dan file `.xlsx` memakai `openpyxl` dari `requirements.txt`.
