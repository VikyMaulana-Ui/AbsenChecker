"""
scheduler.py - Smart scheduler untuk menjalankan absensi_checker pada
hari kerja terakhir yang tersedia di akhir bulan, jam 08:00 WIB.
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from absensi_checker import run_monthly_check
from holidays import get_holiday_name, is_holiday

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - fallback untuk Python lama
    ZoneInfo = None

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

JAKARTA_TZ = ZoneInfo("Asia/Jakarta") if ZoneInfo else None
HARI_NAMES = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN_NAMES = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


def now_jakarta() -> datetime:
    return datetime.now(JAKARTA_TZ) if JAKARTA_TZ else datetime.now()


def is_workday(date: datetime) -> bool:
    return date.weekday() < 5


def is_available_workday(date: datetime) -> bool:
    if not is_workday(date):
        return False
    return not is_holiday(date.year, date.month, date.day)


def get_last_available_workday_of_month(year: int, month: int):
    if month == 12:
        current = datetime(year + 1, 1, 1, tzinfo=JAKARTA_TZ) - timedelta(days=1)
    else:
        current = datetime(year, month + 1, 1, tzinfo=JAKARTA_TZ) - timedelta(days=1)

    while not is_available_workday(current):
        current -= timedelta(days=1)

    return current.day, HARI_NAMES[current.weekday()]


def get_month_info(today: Optional[datetime] = None):
    today = today or now_jakarta()
    year = today.year
    month = today.month
    bulan_name = BULAN_NAMES[month - 1]
    last_workday, hari_name = get_last_available_workday_of_month(year, month)
    is_today_holiday = is_holiday(year, month, today.day)

    return {
        "year": year,
        "month": month,
        "bulan_name": bulan_name,
        "today": today.day,
        "hari_today": HARI_NAMES[today.weekday()],
        "last_workday": last_workday,
        "hari_last_workday": hari_name,
        "is_today_holiday": is_today_holiday,
        "today_holiday_name": get_holiday_name(year, month, today.day) if is_today_holiday else None,
    }


def should_run_today(today: Optional[datetime] = None) -> bool:
    info = get_month_info(today)
    if info["is_today_holiday"]:
        log.debug("Hari ini adalah %s, job di-skip", info["today_holiday_name"])
        return False
    return info["today"] == info["last_workday"]


def get_previous_month(today: Optional[datetime] = None):
    today = today or now_jakarta()
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)
    return last_month.year, last_month.month


def scheduled_job():
    info = get_month_info()

    if not should_run_today():
        log.info("=" * 70)
        log.info("JOB DI-SKIP")
        log.info(
            "Hari ini: %s %s %s %s",
            info["today"], info["hari_today"], info["bulan_name"], info["year"],
        )
        if info["is_today_holiday"]:
            log.info("Alasan: Hari libur nasional - %s", info["today_holiday_name"])
        else:
            log.info("Alasan: Hari ini bukan hari kerja terakhir bulan ini.")
        log.info("Hari kerja terakhir tersedia: %s %s", info["last_workday"], info["hari_last_workday"])
        log.info("=" * 70)
        return None

    try:
        log.info("=" * 70)
        log.info("JOB DIMULAI: CEK ABSENSI BULAN LALU")
        log.info("=" * 70)
        log.info(
            "Hari ini: %s %s %s %s",
            info["today"], info["hari_today"], info["bulan_name"], info["year"],
        )
        log.info("Hari kerja terakhir tersedia: %s %s", info["last_workday"], info["hari_last_workday"])

        year, month = get_previous_month()
        log.info("Periode yang diproses: %s %s (%02d)", year, BULAN_NAMES[month - 1], month)
        log.info("-" * 70)

        result = run_monthly_check(year=year, month=month)

        log.info("-" * 70)
        log.info("JOB SELESAI DENGAN SUKSES")
        log.info("=" * 70)
        return result
    except Exception as exc:
        log.error("=" * 70)
        log.error("JOB GAGAL: %s", exc, exc_info=True)
        log.error("=" * 70)
        return None


def log_scheduled_info():
    info = get_month_info()
    log.info("=" * 70)
    log.info("SCHEDULER DIMULAI")
    log.info("=" * 70)
    log.info("Bulan saat ini: %s %s", info["bulan_name"], info["year"])
    log.info("Hari kerja terakhir tersedia: %s %s", info["last_workday"], info["hari_last_workday"])
    log.info("Waktu cek: setiap hari jam 08:00 WIB")
    log.info("Job berjalan jika hari ini adalah tanggal %s dan bukan hari libur nasional", info["last_workday"])
    log.info("Log file: logs/scheduler.log")
    if info["is_today_holiday"]:
        log.warning("HARI INI ADALAH %s - job di-skip hari ini", info["today_holiday_name"].upper())
    log.info("=" * 70)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(
        func=scheduled_job,
        trigger=CronTrigger(hour=8, minute=0, timezone="Asia/Jakarta"),
        id="absensi_checker_monthly",
        name="Absensi Checker - Monthly Report (Smart Scheduler)",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    log_scheduled_info()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Scheduler dihentikan oleh user")
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
