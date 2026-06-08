"""
holidays.py — Holiday loader untuk AbsenChecker

Format JSON:
[
    {
        "date": "2026-01-01",
        "name": "Hari tahun baru",
        "type": "public"
    }
]
"""

import json
import os
from datetime import datetime
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


_CACHE = {}


def _load_holidays_from_json(year: int):
    """Load data libur dari file JSON lokal."""
    file_path = os.path.join(DATA_DIR, f"holidays_ID_{year}.json")

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    holidays = {}

    for item in data:
        date_str = item.get("date")
        name = item.get("name", "Hari Libur")
        holiday_type = item.get("type", "public")

        if not date_str:
            continue

        # Hanya ambil type public
        if holiday_type != "public":
            continue

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if date_obj.year != year:
            continue

        key = (date_obj.month, date_obj.day)
        holidays[key] = name

    return holidays


def get_holidays(year: int):
    """Ambil semua data libur untuk tahun tertentu."""
    if year not in _CACHE:
        _CACHE[year] = _load_holidays_from_json(year)

    return _CACHE[year]


def is_holiday(year: int, month: int, day: int) -> bool:
    """Cek apakah tanggal adalah hari libur nasional/public holiday."""
    return (month, day) in get_holidays(year)


def get_holiday_name(year: int, month: int, day: int) -> Optional[str]:
    """Ambil nama hari libur."""
    return get_holidays(year).get((month, day))


def print_holidays(year: int):
    """Debug helper untuk cek daftar libur yang terbaca."""
    holidays = get_holidays(year)

    if not holidays:
        print(f"Tidak ada data libur untuk tahun {year}")
        return

    print(f"Daftar libur {year}:")
    for month, day in sorted(holidays):
        print(f"{day:02d}-{month:02d}-{year}: {holidays[(month, day)]}")


if __name__ == "__main__":
    print_holidays(2026)
    print()
    print_holidays(2027)