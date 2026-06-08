"""
Automation cek absensi HR Portal Toyota.

Mode penuh: login, buka Attendance, unduh Excel, analisis, dan kirim email.
Mode analyze-only: analisis file Excel lokal tanpa mengimpor Selenium.
"""

import argparse
import glob
import logging
import os
import smtplib
import time
import traceback
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional, Set

from analyzer import AbsensiAnalyzer
from config import CONFIG


def _ensure_runtime_dirs():
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path(CONFIG["DOWNLOAD_DIR"]).mkdir(parents=True, exist_ok=True)


_ensure_runtime_dirs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/absensi_checker.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def _as_bool(value, default=False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _as_int(key: str, default: int) -> int:
    try:
        return int(CONFIG.get(key, default))
    except (TypeError, ValueError):
        return default


def _split_emails(value: str) -> List[str]:
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _month_label(year: int, month: int) -> str:
    return datetime(year, month, 1).strftime("%b-%Y")


def validate_full_run_config():
    required = [
        "HR_PORTAL_URL",
        "ATTENDANCE_PAGE_URL",
        "HR_USERNAME",
        "HR_PASSWORD",
        "LOGIN_FIELD_USERNAME",
        "LOGIN_FIELD_PASSWORD",
        "LOGIN_BUTTON_CSS",
        "PERIODE_FIELD_ID",
        "SEARCH_BUTTON_ID",
        "DOWNLOAD_BUTTON_ID",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "FROM_EMAIL",
        "TO_EMAIL",
    ]
    missing = [key for key in required if not str(CONFIG.get(key, "")).strip()]
    if missing:
        raise ValueError("Konfigurasi wajib belum diisi: " + ", ".join(missing))


class HRPortalScraper:
    def __init__(self):
        self.driver = None
        self.By = None
        self.WebDriverWait = None
        self.EC = None
        self.download_dir = Path(CONFIG["DOWNLOAD_DIR"]).resolve()
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.timeout = _as_int("SELENIUM_TIMEOUT", 30)

    def _shot(self, step: str):
        if not self.driver:
            return
        path = self.screenshot_dir / f"{step}.png"
        self.driver.save_screenshot(str(path))

    def _init_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        self.By = By
        self.WebDriverWait = WebDriverWait
        self.EC = EC

        chrome_options = Options()
        if _as_bool(CONFIG.get("HEADLESS"), True):
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        })

        driver_path = str(CONFIG.get("CHROME_DRIVER_PATH", "")).strip()
        if driver_path:
            self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        self.driver.implicitly_wait(_as_int("IMPLICIT_WAIT", 10))
        log.info("Chrome driver berhasil diinisialisasi.")

    def _wait(self, key: str, default: int):
        time.sleep(_as_int(key, default))

    def _xpath_literal(self, value: str) -> str:
        if '"' not in value:
            return f'"{value}"'
        if "'" not in value:
            return f"'{value}'"
        parts = value.split('"')
        return "concat(" + ', \'"\', '.join(f'"{part}"' for part in parts) + ")"

    def _locator_candidates(self, value: str):
        value = str(value or "").strip()
        if value.startswith("css="):
            return [(self.By.CSS_SELECTOR, value[4:])]
        if value.startswith("id="):
            return [(self.By.ID, value[3:])]
        if value.startswith("name="):
            return [(self.By.NAME, value[5:])]
        if value.startswith("text="):
            text_value = self._xpath_literal(value[5:].strip())
            return [(
                self.By.XPATH,
                "//*[self::button or self::a or self::span][contains(normalize-space(.), "
                + text_value
                + ")]",
            )]

        css_markers = ("[", "]", ".", "#", " ", ">", ":", "=")
        if any(marker in value for marker in css_markers):
            return [(self.By.CSS_SELECTOR, value)]

        return [
            (self.By.ID, value),
            (self.By.NAME, value),
            (self.By.CSS_SELECTOR, value),
        ]

    def _find_visible(self, selector: str):
        for by, value in self._locator_candidates(selector):
            for element in self.driver.find_elements(by, value):
                if element.is_displayed():
                    return element
        return False

    def _find_clickable(self, selector: str):
        element = self._find_visible(selector)
        if element and element.is_enabled():
            return element
        return False

    def _wait_for_visible(self, wait, selector: str, label: str):
        try:
            return wait.until(lambda _driver: self._find_visible(selector))
        except Exception:
            self._shot(f"{label}_not_found")
            raise

    def _wait_for_clickable(self, wait, selector: str, label: str):
        try:
            return wait.until(lambda _driver: self._find_clickable(selector))
        except Exception:
            self._shot(f"{label}_not_found")
            raise

    def login(self):
        log.info("Membuka HR Portal: %s", CONFIG["HR_PORTAL_URL"])
        self.driver.get(CONFIG["HR_PORTAL_URL"])

        wait = self.WebDriverWait(self.driver, self.timeout)
        username_field = self._wait_for_visible(wait, CONFIG["LOGIN_FIELD_USERNAME"], "login_username")
        password_field = self._wait_for_visible(wait, CONFIG["LOGIN_FIELD_PASSWORD"], "login_password")

        username_field.clear()
        username_field.send_keys(CONFIG["HR_USERNAME"])
        password_field.clear()
        password_field.send_keys(CONFIG["HR_PASSWORD"])

        login_btn = self._wait_for_clickable(wait, CONFIG["LOGIN_BUTTON_CSS"], "login_button")
        login_btn.click()
        self._wait("AFTER_LOGIN_WAIT", 5)
        self._validate_login_success()
        log.info("Login berhasil. URL: %s", self.driver.current_url)

    def _validate_login_success(self):
        current_url = self.driver.current_url.lower()
        login_url = CONFIG["HR_PORTAL_URL"].lower()
        if current_url != login_url and "login" not in current_url:
            return

        if self._find_visible(CONFIG["LOGIN_FIELD_USERNAME"]):
            self._shot("login_failed")
            raise RuntimeError("Login belum berhasil; halaman login masih tampil setelah tombol Masuk diklik.")

    def navigate_to_attendance(self, year: int, month: int):
        periode_id = CONFIG["PERIODE_FIELD_ID"]
        search_id = CONFIG["SEARCH_BUTTON_ID"]
        period_value = _month_label(year, month)
        period_date = f"{year}-{month:02d}-01"

        log.info("Navigasi ke halaman absensi %s-%02d", year, month)
        self.driver.get(CONFIG["ATTENDANCE_PAGE_URL"])
        self._wait("AFTER_NAVIGATE_WAIT", 3)

        wait = self.WebDriverWait(self.driver, self.timeout)
        period_input = self._wait_for_visible(wait, periode_id, "attendance_period")

        used_datepicker = self.driver.execute_script(
            """
            const field = arguments[0];
            const isoDate = arguments[1];
            const visibleValue = arguments[2];
            let usedDatepicker = false;
            if (window.jQuery && jQuery.fn && jQuery.fn.datepicker) {
                try {
                    jQuery(field).datepicker('update', new Date(isoDate));
                    usedDatepicker = true;
                } catch (error) {
                    usedDatepicker = false;
                }
            }
            if (!usedDatepicker) {
                field.removeAttribute('readonly');
                field.value = visibleValue;
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
            return usedDatepicker;
            """,
            period_input,
            period_date,
            period_value,
        )
        log.info("Periode diset ke %s (%s)", period_value, "datepicker" if used_datepicker else "fallback")

        try:
            param = self.driver.execute_script(
                "return (typeof getParam === 'function') ? JSON.stringify(getParam()) : null;"
            )
            if param:
                log.info("getParam setelah set: %s", param)
        except Exception as exc:
            log.debug("getParam tidak tersedia: %s", exc)

        search_btn = self._wait_for_clickable(wait, search_id, "attendance_search")
        self.driver.execute_script("arguments[0].click()", search_btn)
        self._wait("AFTER_SEARCH_WAIT", 5)
        log.info("Halaman absensi %s-%02d berhasil dimuat.", year, month)

    def download_excel(self) -> Path:
        wait = self.WebDriverWait(self.driver, self.timeout)
        existing_files = set(self.download_dir.glob("Kehadiran_Individu_*.xls*"))
        download_btn = self._wait_for_clickable(wait, CONFIG["DOWNLOAD_BUTTON_ID"], "attendance_download")
        self.driver.execute_script("arguments[0].click()", download_btn)
        log.info("Tombol Unduh diklik, menunggu download...")

        downloaded_file = self._wait_for_download(
            existing_files=existing_files,
            timeout=_as_int("DOWNLOAD_TIMEOUT", 60),
        )
        log.info("File berhasil diunduh: %s", downloaded_file)
        return downloaded_file

    def _wait_for_download(self, existing_files: Optional[Set[Path]] = None, timeout: int = 60) -> Path:
        existing_files = existing_files or set()
        deadline = time.time() + timeout
        stable_candidate = None
        stable_size = -1
        stable_since = 0.0

        while time.time() < deadline:
            crdownloads = list(self.download_dir.glob("*.crdownload"))
            current_files = {
                path for path in self.download_dir.glob("Kehadiran_Individu_*.xls*")
                if not path.name.endswith(".crdownload")
            }
            new_files = current_files - existing_files

            if new_files and not crdownloads:
                newest = max(new_files, key=lambda path: path.stat().st_mtime)
                size = newest.stat().st_size
                if newest == stable_candidate and size == stable_size and size > 0:
                    if time.time() - stable_since >= 2:
                        return newest
                else:
                    stable_candidate = newest
                    stable_size = size
                    stable_since = time.time()

            time.sleep(1)

        raise TimeoutError("File download tidak selesai dalam waktu yang ditentukan.")

    def close(self):
        if self.driver:
            self.driver.quit()
            log.info("Browser ditutup.")


class EmailSender:
    def __init__(self):
        self.smtp_host = CONFIG["SMTP_HOST"]
        self.smtp_port = _as_int("SMTP_PORT", 587)
        self.smtp_user = CONFIG["SMTP_USER"]
        self.smtp_password = CONFIG["SMTP_PASSWORD"]
        self.from_email = CONFIG["FROM_EMAIL"]
        self.to_emails = _split_emails(CONFIG["TO_EMAIL"])
        self.cc_emails = _split_emails(CONFIG.get("CC_EMAIL", ""))
        self.bcc_emails = _split_emails(CONFIG.get("BCC_EMAIL", ""))

    def send_report(self, subject: str, html_body: str, attachment_path: Optional[Path] = None):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to_emails)
        if self.cc_emails:
            msg["Cc"] = ", ".join(self.cc_emails)

        msg.attach(MIMEText(html_body, "html"))

        if attachment_path and attachment_path.exists():
            with open(attachment_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={attachment_path.name}")
            msg.attach(part)

        recipients = self.to_emails + self.cc_emails + self.bcc_emails
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, recipients, msg.as_string())

        log.info("Email terkirim ke %s", ", ".join(recipients))


def run_monthly_check(year: int = None, month: int = None):
    validate_full_run_config()

    if year is None or month is None:
        today = datetime.today()
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        year = last_month.year
        month = last_month.month

    period_label = f"{year}-{month:02d}"
    log.info("==== Memulai pengecekan absensi periode %s ====", period_label)

    scraper = HRPortalScraper()
    try:
        scraper._init_driver()
        scraper.login()
        scraper.navigate_to_attendance(year, month)
        xls_file = scraper.download_excel()
    except Exception as exc:
        log.error("Gagal saat scraping: %s\n%s", exc, traceback.format_exc())
        raise
    finally:
        scraper.close()

    log.info("Menganalisis data absensi...")
    analyzer = AbsensiAnalyzer(xls_file)
    result = analyzer.analyze()

    subject = f"[Absensi] Laporan Kehadiran {period_label}"
    html_body = build_email_html(result, period_label)

    sender = EmailSender()
    attachment_path = xls_file if _as_bool(CONFIG.get("SEND_ATTACHMENT"), True) else None
    sender.send_report(subject, html_body, attachment_path=attachment_path)

    if not attachment_path:
        log.info("SEND_ATTACHMENT=false; email dikirim tanpa lampiran Excel.")

    if _as_bool(CONFIG.get("DELETE_AFTER_EMAIL"), True):
        try:
            xls_file.unlink()
            log.info("File %s dihapus setelah email terkirim.", xls_file.name)
        except Exception as exc:
            log.warning("Gagal hapus file: %s", exc)
    else:
        log.info("DELETE_AFTER_EMAIL=false; file Excel disimpan: %s", xls_file)

    log.info("==== Selesai. Laporan dikirim untuk periode %s ====", period_label)
    return result


def build_email_html(result: dict, period_label: str) -> str:
    def badge(text, color):
        return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:12px;">{text}</span>'

    warnings = result.get("warnings", [])
    warning_rows = "".join(f"<tr><td>!</td><td>{w}</td></tr>" for w in warnings)
    if not warning_rows:
        warning_rows = "<tr><td colspan='2' style='color:green;'>Tidak ada peringatan</td></tr>"

    late_rows = ""
    for item in result.get("late_days", []):
        late_rows += f"""
        <tr>
          <td>{item['tanggal']}</td>
          <td>{item['jam_masuk_standar']}</td>
          <td>{item['jam_masuk_aktual']}</td>
          <td>{item['telat_menit']} menit</td>
        </tr>"""
    if not late_rows:
        late_rows = "<tr><td colspan='4' style='color:green;'>Tidak ada keterlambatan</td></tr>"

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;color:#333;">
      <h2 style="background:#1a73e8;color:white;padding:16px;border-radius:6px;">
        Laporan Kehadiran Individu - {period_label}
      </h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <tr><td style="padding:8px;width:50%;">
          <b>Noreg</b><br><span style="font-size:18px;">{result.get('noreg','-')}</span>
        </td><td style="padding:8px;">
          <b>Periode</b><br><span style="font-size:18px;">{period_label}</span>
        </td></tr>
      </table>
      <h3 style="border-bottom:2px solid #1a73e8;">Ringkasan</h3>
      <table style="width:100%;border-collapse:collapse;">
        <tr style="background:#f1f3f4;">
          <td style="padding:10px;">Hari Kerja (PLA/shift)</td>
          <td style="padding:10px;text-align:right;font-weight:bold;">{result.get('total_workdays',0)} hari</td>
        </tr>
        <tr>
          <td style="padding:10px;">Hadir</td>
          <td style="padding:10px;text-align:right;color:green;font-weight:bold;">{result.get('hadir',0)} hari</td>
        </tr>
        <tr style="background:#f1f3f4;">
          <td style="padding:10px;">Mangkir</td>
          <td style="padding:10px;text-align:right;">
            {result.get('mangkir',0)} hari
            {"&nbsp;" + badge("PERHATIAN","#e53935") if result.get('mangkir',0) > 0 else ""}
          </td>
        </tr>
        <tr>
          <td style="padding:10px;">Sakit</td>
          <td style="padding:10px;text-align:right;">
            {result.get('sakit',0)} hari
            {"&nbsp;" + badge("> 6 HARI","#e53935") if result.get('sakit',0) > 6 else ""}
          </td>
        </tr>
        <tr style="background:#f1f3f4;">
          <td style="padding:10px;">Izin</td>
          <td style="padding:10px;text-align:right;">{result.get('izin',0)} hari</td>
        </tr>
        <tr>
          <td style="padding:10px;">Terlambat</td>
          <td style="padding:10px;text-align:right;">{result.get('total_late_days',0)} hari
            (total {result.get('total_late_minutes',0)} menit)
          </td>
        </tr>
      </table>
      <h3 style="border-bottom:2px solid #e53935;margin-top:24px;">Peringatan</h3>
      <table style="width:100%;border-collapse:collapse;">
        {warning_rows}
      </table>
      <h3 style="border-bottom:2px solid #f9a825;margin-top:24px;">Detail Keterlambatan</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <tr style="background:#f1f3f4;font-weight:bold;">
          <th style="padding:8px;text-align:left;">Tanggal</th>
          <th style="padding:8px;text-align:left;">Standar Masuk</th>
          <th style="padding:8px;text-align:left;">Aktual Masuk</th>
          <th style="padding:8px;text-align:left;">Selisih</th>
        </tr>
        {late_rows}
      </table>
      <p style="color:#888;font-size:12px;margin-top:30px;">
        Email ini dikirim otomatis oleh AbsenChecker - {datetime.now().strftime('%d %b %Y %H:%M')}
      </p>
    </body></html>
    """


def find_analyze_target(target: str) -> Path:
    download_dir = Path(CONFIG["DOWNLOAD_DIR"])
    if target == "latest":
        candidates = list(Path.cwd().glob("Kehadiran_Individu_*.xls*"))
        candidates.extend(download_dir.glob("Kehadiran_Individu_*.xls*"))
        candidates = [path for path in candidates if not path.name.endswith(".crdownload")]
        if not candidates:
            raise FileNotFoundError("Tidak ada file Kehadiran_Individu_*.xls* di folder kerja atau downloads/.")
        return max(candidates, key=lambda path: path.stat().st_mtime)

    if "*" in target:
        matches = [Path(path) for path in glob.glob(target)]
        if not matches:
            raise FileNotFoundError(f"Tidak ada file yang cocok dengan pattern: {target}")
        return max(matches, key=lambda path: path.stat().st_mtime)

    path = Path(target)
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {target}")
    return path


def analyze_only(target: str) -> dict:
    xls_file = find_analyze_target(target)
    print(f"File dianalisis: {xls_file}")
    analyzer = AbsensiAnalyzer(xls_file)
    result = analyzer.analyze()

    print("\n" + "=" * 50)
    print("HASIL ANALISIS ABSENSI")
    print("=" * 50)
    for key, value in result.items():
        if key not in ("late_days",):
            print(f"  {key:30s}: {value}")
    print("\nKeterlambatan:")
    for item in result.get("late_days", []):
        print(f"  {item['tanggal']} -> telat {item['telat_menit']} menit")
    print("\nPeringatan:")
    for warning in result.get("warnings", []):
        print(f"  {warning}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Cek absensi HR Portal")
    parser.add_argument("--year", type=int, help="Tahun (default: bulan lalu)")
    parser.add_argument("--month", type=int, help="Bulan 1-12 (default: bulan lalu)")
    parser.add_argument("--analyze-only", metavar="FILE", help="Analisis file XLS lokal tanpa login. Pakai 'latest' untuk file terbaru.")
    args = parser.parse_args()

    if args.analyze_only:
        analyze_only(args.analyze_only)
    else:
        run_monthly_check(year=args.year, month=args.month)


if __name__ == "__main__":
    main()
