"""Application configuration, sourced from environment variables.

No secret is hardcoded here: required values are read from the environment
(see .env.example). Copy .env.example to .env to run locally.
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
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    ENV = os.environ.get("APP_ENV", "development")
    VERSION = "1.0.0"


settings = Settings()
