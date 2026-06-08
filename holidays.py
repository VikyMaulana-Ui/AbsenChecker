"""
holidays.py — Database hari libur nasional Indonesia 2026-2027+

Format: {tahun: [(bulan, hari), ...]}
Update sesuai kebutuhan untuk tahun-tahun berikutnya

Note: Tanggal bisa berubah karena kalender Hijriyah (Imlek, Idul Fitri, dll)
Periksa kalender resmi pemerintah untuk data terbaru.
"""

# ─── Database Libur Nasional ──────────────────────────────
HOLIDAYS = {
    2026: [
        # Libur Nasional 2026
        (1, 1),    # 1 Januari - Tahun Baru
        (1, 28),   # 28 Januari - Isra Mi'raj
        (2, 14),   # 14 Februari - Hari Raya Imlek
        (2, 16),   # 16 Februari - Hari Libur bersama
        (3, 11),   # 11 Maret - Keputusan Presiden
        (3, 29),   # 29 Maret - Hari Raya Nyepi
        (3, 30),   # 30 Maret - Hari Libur bersama
        (3, 31),   # 31 Maret - Hari Libur bersama
        (4, 10),   # 10 April - Jumat Agung
        (4, 13),   # 13 April - Hari Raya Idul Fitri
        (4, 14),   # 14 April - Hari Raya Idul Fitri
        (4, 15),   # 15 April - Hari Libur bersama
        (4, 16),   # 16 April - Hari Libur bersama
        (4, 17),   # 17 April - Hari Libur bersama
        (5, 1),    # 1 Mei - Hari Buruh
        (5, 14),   # 14 Mei - Hari Raya Waisak
        (5, 22),   # 22 Mei - Hari Raya Idul Adha
        (6, 1),    # 1 Juni - Pancasila
        (6, 11),   # 11 Juni - Tahun Baru Hijriyah
        (8, 17),   # 17 Agustus - Kemerdekaan RI
        (9, 16),   # 16 September - Mawlid Nabi Muhammad
        (12, 25),  # 25 Desember - Hari Natal
        (12, 26),  # 26 Desember - Hari Libur bersama
    ],
    2027: [
        # Libur Nasional 2027
        (1, 1),    # 1 Januari - Tahun Baru
        (1, 17),   # 17 Januari - Isra Mi'raj
        (2, 3),    # 3 Februari - Hari Raya Imlek
        (2, 4),    # 4 Februari - Hari Libur bersama
        (3, 11),   # 11 Maret - Keputusan Presiden
        (3, 19),   # 19 Maret - Hari Raya Nyepi
        (3, 20),   # 20 Maret - Hari Libur bersama
        (3, 29),   # 29 Maret - Jumat Agung
        (4, 2),    # 2 April - Hari Raya Idul Fitri
        (4, 3),    # 3 April - Hari Raya Idul Fitri
        (4, 4),    # 4 April - Hari Libur bersama
        (4, 5),    # 5 April - Hari Libur bersama
        (4, 6),    # 6 April - Hari Libur bersama
        (5, 1),    # 1 Mei - Hari Buruh
        (5, 3),    # 3 Mei - Hari Raya Waisak
        (5, 10),   # 10 Mei - Hari Raya Idul Adha
        (6, 1),    # 1 Juni - Pancasila
        (6, 9),    # 9 Juni - Tahun Baru Hijriyah
        (8, 17),   # 17 Agustus - Kemerdekaan RI
        (9, 5),    # 5 September - Mawlid Nabi Muhammad
        (12, 25),  # 25 Desember - Hari Natal
        (12, 26),  # 26 Desember - Hari Libur bersama
    ],
}

# ─── Holiday Name Mapping ────────────────────────────────
HOLIDAY_NAMES = {
    (1, 1): "Tahun Baru",
    (1, 17): "Isra Mi'raj",
    (1, 28): "Isra Mi'raj",
    (2, 3): "Hari Raya Imlek",
    (2, 4): "Hari Libur bersama",
    (2, 14): "Hari Raya Imlek",
    (2, 16): "Hari Libur bersama",
    (3, 11): "Keputusan Presiden",
    (3, 19): "Hari Raya Nyepi",
    (3, 20): "Hari Libur bersama",
    (3, 29): "Jumat Agung",
    (3, 30): "Hari Libur bersama",
    (3, 31): "Hari Libur bersama",
    (4, 2): "Hari Raya Idul Fitri",
    (4, 3): "Hari Raya Idul Fitri",
    (4, 4): "Hari Libur bersama",
    (4, 5): "Hari Libur bersama",
    (4, 6): "Hari Libur bersama",
    (4, 10): "Jumat Agung",
    (4, 13): "Hari Raya Idul Fitri",
    (4, 14): "Hari Raya Idul Fitri",
    (4, 15): "Hari Libur bersama",
    (4, 16): "Hari Libur bersama",
    (4, 17): "Hari Libur bersama",
    (5, 1): "Hari Buruh",
    (5, 3): "Hari Raya Waisak",
    (5, 10): "Hari Raya Idul Adha",
    (5, 14): "Hari Raya Waisak",
    (5, 22): "Hari Raya Idul Adha",
    (6, 1): "Hari Pancasila",
    (6, 9): "Tahun Baru Hijriyah",
    (6, 11): "Tahun Baru Hijriyah",
    (8, 17): "Hari Kemerdekaan RI",
    (9, 5): "Mawlid Nabi Muhammad",
    (9, 16): "Mawlid Nabi Muhammad",
    (12, 25): "Hari Natal",
    (12, 26): "Hari Libur bersama",
}


def is_holiday(year: int, month: int, day: int) -> bool:
    """Cek apakah tanggal tersebut adalah hari libur nasional."""
    if year not in HOLIDAYS:
        return False
    
    return (month, day) in HOLIDAYS[year]


def get_holiday_name(year: int, month: int, day: int) -> str:
    """Get nama libur (jika ada)."""
    name = HOLIDAY_NAMES.get((month, day), "Libur Nasional")
    return name
