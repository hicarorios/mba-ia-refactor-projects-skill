"""Centralized error handling — replaces the per-handler try/except that
swallowed exceptions and leaked str(e) to clients."""
from flask import jsonify


class AppError(Exception):
    """Domain/HTTP error raised by controllers and services."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _handle_app_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status

    @app.errorhandler(404)
    def _handle_not_found(_err):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def _handle_unexpected(err):
        app.logger.exception("Unhandled error: %s", err)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
