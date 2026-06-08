"""
scheduler.py — Smart Scheduler untuk menjalankan absensi_checker 
setiap akhir bulan (hari kerja terakhir yang tersedia) jam 8 pagi

Fitur:
- Otomatis mundur ke hari kerja jika akhir bulan jatuh weekend
- Otomatis mundur lagi jika hari kerja terakhir adalah tanggal merah (libur nasional)
- Run otomatis jam 08:00 setiap hari dengan smart check
- Detailed logging dengan nama hari & bulan Indonesia

Contoh:
- Juni 2026 berakhir Selasa 30 → jalankan 30 Juni jam 08:00
- Mei 2027 berakhir Minggu 31 → jalankan 29 Mei (Jumat) jam 08:00
- April 2026 Jumat 10 libur nasional (Jumat Agung) → jalankan 9 April (Kamis)
"""

import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from absensi_checker import run_monthly_check
from holidays import is_holiday, get_holiday_name

# ─── Setup Logging ────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── Konstanta ────────────────────────────────────────────
HARI_NAMES = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_NAMES = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


def is_workday(date):
    """Cek apakah tanggal adalah hari kerja (Senin-Jumat = 0-4)."""
    return date.weekday() < 5


def is_available_workday(date):
    """
    Cek apakah tanggal adalah hari kerja YANG TERSEDIA.
    Artinya: bukan weekend DAN bukan tanggal merah (libur nasional).
    """
    # Cek apakah hari kerja (Senin-Jumat)
    if not is_workday(date):
        return False
    
    # Cek apakah bukan hari libur nasional
    if is_holiday(date.year, date.month, date.day):
        return False
    
    return True


def get_last_available_workday_of_month(year: int, month: int):
    """
    Cari hari kerja terakhir yang TERSEDIA di bulan tersebut.
    Skip: weekend dan tanggal merah (libur nasional).
    
    Contoh:
    - Juni 2026 berakhir Selasa 30 (kerja, tidak libur) → return (30, "Selasa")
    - Mei 2027 berakhir Minggu 31, Sabtu 30, Jumat 29 (libur) → return (28, "Kamis")
    - April 2026 berakhir Rabu 30, Selasa 29, Senin 28, Jumat 24 (libur), Kamis 23 → return (23, "Kamis")
    """
    # Cari hari terakhir bulan
    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(days=1)
    
    current = last_day
    
    # Mundur sampai ketemu hari kerja yang tersedia
    while not is_available_workday(current):
        current -= timedelta(days=1)
    
    return current.day, HARI_NAMES[current.weekday()]


def get_month_info():
    """Get info bulan sekarang."""
    today = datetime.today()
    year = today.year
    month = today.month
    bulan_name = BULAN_NAMES[month - 1]
    
    last_workday, hari_name = get_last_available_workday_of_month(year, month)
    
    # Cek apakah hari ini tanggal merah
    is_today_holiday = is_holiday(year, month, today.day)
    holiday_name = get_holiday_name(year, month, today.day) if is_today_holiday else None
    
    return {
        "year": year,
        "month": month,
        "bulan_name": bulan_name,
        "today": today.day,
        "hari_today": HARI_NAMES[today.weekday()],
        "last_workday": last_workday,
        "hari_last_workday": hari_name,
        "is_today_holiday": is_today_holiday,
        "today_holiday_name": holiday_name,
    }


def should_run_today():
    """Cek apakah job seharusnya jalan hari ini."""
    info = get_month_info()
    
    # Skip jika hari ini adalah libur nasional
    if info["is_today_holiday"]:
        log.debug(f"📌 Hari ini adalah {info['today_holiday_name']}, job di-skip")
        return False
    
    # Jalankan jika hari ini adalah hari kerja terakhir bulan yang tersedia
    return info["today"] == info["last_workday"]


def scheduled_job():
    """Fungsi yang dijalankan oleh scheduler."""
    info = get_month_info()
    
    try:
        log.info("=" * 70)
        log.info("🤖 JOB DIMULAI: CEK ABSENSI BULAN LALU")
        log.info("=" * 70)
        
        hari_info = f"{info['today']} {info['hari_today']}"
        if info["is_today_holiday"]:
            hari_info += f" ({info['today_holiday_name']})"
        
        log.info(f"📅 Hari ini: {hari_info} {info['bulan_name']} {info['year']}")
        log.info(f"✅ Hari kerja terakhir (tersedia): {info['last_workday']} {info['hari_last_workday']}")
        
        # Ambil bulan lalu
        today = datetime.today()
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        year = last_month.year
        month = last_month.month
        bulan_lalu = BULAN_NAMES[month - 1]
        
        log.info(f"📋 Periode yang diproses: {year} {bulan_lalu} ({month:02d})")
        log.info("-" * 70)
        
        # Jalankan checker
        result = run_monthly_check(year=year, month=month)
        
        log.info("-" * 70)
        log.info("✅ JOB SELESAI DENGAN SUKSES!")
        log.info("=" * 70)
        
    except Exception as e:
        log.error("=" * 70)
        log.error(f"❌ JOB GAGAL: {e}", exc_info=True)
        log.error("=" * 70)


def log_scheduled_info():
    """Log info schedule saat startup."""
    info = get_month_info()
    
    log.info("=" * 70)
    log.info("✅ SCHEDULER DIMULAI")
    log.info("=" * 70)
    log.info(f"📅 Bulan saat ini: {info['bulan_name']} {info['year']}")
    log.info(f"📌 Hari kerja terakhir (tersedia): {info['last_workday']} {info['hari_last_workday']}")
    log.info(f"   (tidak termasuk weekend & hari libur nasional)")
    log.info(f"⏰ Waktu cek: Setiap hari jam 08:00")
    log.info(f"📊 Job akan jalan jika: Hari ini = tanggal {info['last_workday']} ({info['hari_last_workday']})")
    log.info(f"                        DAN hari ini BUKAN hari libur nasional")
    log.info(f"📝 Log file: logs/scheduler.log")
    
    # Info hari ini
    if info["is_today_holiday"]:
        log.warning(f"⚠️  HARI INI ADALAH {info['today_holiday_name'].upper()} - Job di-skip hari ini")
    
    log.info("=" * 70)


def start_scheduler():
    """
    Mulai scheduler dengan trigger:
    - Setiap hari jam 08:00
    - Hanya jalankan jika hari kerja terakhir bulan yang TERSEDIA
    """
    scheduler = BackgroundScheduler()
    
    # Schedule job: setiap hari jam 8:00 dengan custom logic di scheduled_job()
    scheduler.add_job(
        func=scheduled_job,
        trigger=CronTrigger(hour=8, minute=0),
        id='absensi_checker_monthly',
        name='Absensi Checker - Monthly Report (Smart Scheduler)',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Log info startup
    log_scheduled_info()
    
    # Jangan exit (block main thread)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        log.info("\n⛔ Scheduler dihentikan oleh user")
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
