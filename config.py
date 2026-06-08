"""Konfigurasi AbsenChecker."""

import os
from dotenv import load_dotenv

load_dotenv()

for folder in ("logs", "screenshots", os.getenv("DOWNLOAD_DIR", "downloads")):
    os.makedirs(folder, exist_ok=True)

CONFIG = {
    "HR_PORTAL_URL": os.getenv("HR_PORTAL_URL", "https://hrportal.toyota.co.id/Login"),
    "ATTENDANCE_PAGE_URL": os.getenv("ATTENDANCE_PAGE_URL", "https://hrportal.toyota.co.id/Attendance"),

    "HR_USERNAME": os.getenv("HR_USERNAME", ""),
    "HR_PASSWORD": os.getenv("HR_PASSWORD", ""),

    "LOGIN_FIELD_USERNAME": os.getenv("LOGIN_FIELD_USERNAME", "tfUsername"),
    "LOGIN_FIELD_PASSWORD": os.getenv("LOGIN_FIELD_PASSWORD", "tfPassword"),
    "LOGIN_BUTTON_CSS": os.getenv("LOGIN_BUTTON_CSS", "#login-button"),

    "PERIODE_FIELD_ID": os.getenv("PERIODE_FIELD_ID", "periode-text"),
    "SEARCH_BUTTON_ID": os.getenv("SEARCH_BUTTON_ID", "search-button"),
    "DOWNLOAD_BUTTON_ID": os.getenv("DOWNLOAD_BUTTON_ID", "download-button"),

    "DOWNLOAD_DIR": os.getenv("DOWNLOAD_DIR", "downloads"),

    "HEADLESS": os.getenv("HEADLESS", "true"),
    "SELENIUM_TIMEOUT": os.getenv("SELENIUM_TIMEOUT", "30"),
    "IMPLICIT_WAIT": os.getenv("IMPLICIT_WAIT", "10"),
    "AFTER_LOGIN_WAIT": os.getenv("AFTER_LOGIN_WAIT", "5"),
    "AFTER_NAVIGATE_WAIT": os.getenv("AFTER_NAVIGATE_WAIT", "3"),
    "AFTER_SEARCH_WAIT": os.getenv("AFTER_SEARCH_WAIT", "5"),
    "DOWNLOAD_TIMEOUT": os.getenv("DOWNLOAD_TIMEOUT", "60"),
    "DELETE_AFTER_EMAIL": os.getenv("DELETE_AFTER_EMAIL", "true"),
    "SEND_ATTACHMENT": os.getenv("SEND_ATTACHMENT", "true"),
    "CHROME_DRIVER_PATH": os.getenv("CHROME_DRIVER_PATH", ""),

    "SMTP_HOST": os.getenv("SMTP_HOST", ""),
    "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
    "SMTP_USER": os.getenv("SMTP_USER", ""),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    "FROM_EMAIL": os.getenv("FROM_EMAIL", ""),
    "TO_EMAIL": os.getenv("TO_EMAIL", ""),
    "CC_EMAIL": os.getenv("CC_EMAIL", ""),
    "BCC_EMAIL": os.getenv("BCC_EMAIL", ""),
}
