"""Configuration management for Family Wealth AI."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    """Application configuration from environment variables."""

    # LINE Bot credentials
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")

    # Google Sheets
    GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"
    )

    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Gemini Models
    GEMINI_OCR_MODEL = os.getenv("GEMINI_OCR_MODEL", "gemini-3-flash-preview")
    GEMINI_RESEARCH_MODEL = os.getenv("GEMINI_RESEARCH_MODEL", "gemini-3-pro-preview")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing keys."""
        missing = []
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            missing.append("LINE_CHANNEL_ACCESS_TOKEN")
        if not cls.LINE_CHANNEL_SECRET:
            missing.append("LINE_CHANNEL_SECRET")
        if not cls.GOOGLE_SHEETS_ID:
            missing.append("GOOGLE_SHEETS_ID")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        return missing
