"""Thin entry point — delegates to the application factory in src/.

Kept at the project root so the original boot command (`python app.py`)
still works after the refactor.
"""
from src.app import app
from src.config.settings import settings

if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
