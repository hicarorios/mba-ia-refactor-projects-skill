"""Admin endpoints kept registered for contract compatibility, but the
dangerous capabilities are removed/gated (no arbitrary SQL, no unauthenticated
destructive reset)."""
import os

from flask import jsonify, request

from src.middlewares.error_handler import AppError


class AdminController:
    def __init__(self, db):
        self.db = db

    def _require_admin(self):
        token = os.environ.get("ADMIN_TOKEN")
        if not token or request.headers.get("X-Admin-Token") != token:
            raise AppError("Não autorizado", 403)

    def executar_query(self):
        # Arbitrary SQL execution removed for security. Route kept for
        # contract compatibility; it now always refuses.
        raise AppError("Endpoint desativado por segurança", 403)

    def reset_db(self):
        self._require_admin()
        cur = self.db.connection.cursor()
        for table in ("itens_pedido", "pedidos", "produtos", "usuarios"):
            cur.execute(f"DELETE FROM {table}")
        self.db.connection.commit()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
