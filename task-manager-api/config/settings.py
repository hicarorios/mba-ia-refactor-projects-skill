"""Application configuration, sourced from environment variables.

No secret is hardcoded. Copy .env.example to .env to run locally.
"""
import os

from dotenv import load_dotenv

load_dotenv()


def _require(key):
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"{key} is required — copy .env.example to .env and fill it in"
        )
    return value


def _bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    SECRET_KEY = _require("SECRET_KEY")
    DEBUG = _bool(os.environ.get("DEBUG"), default=False)
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")

    # SMTP — read from env; empty by default (no real credentials in source).
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


settings = Settings()
