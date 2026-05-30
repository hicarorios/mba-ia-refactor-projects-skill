from flask import jsonify

from src.config.settings import settings


class HealthController:
    def __init__(self, db):
        self.db = db

    def check(self):
        cur = self.db.connection.cursor()
        counts = {}
        for table in ("produtos", "usuarios", "pedidos"):
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cur.fetchone()[0]
        # No secrets in the payload (the original leaked SECRET_KEY here).
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": settings.VERSION,
            "ambiente": settings.ENV,
        }), 200
