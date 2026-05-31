"""Centralized error handling — replaces the bare `except:` blocks scattered
through the routes that swallowed errors into a generic 500."""
from flask import jsonify


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _handle_app_error(err):
        return jsonify({"error": err.message}), err.status

    @app.errorhandler(404)
    def _not_found(_err):
        return jsonify({"error": "Recurso não encontrado"}), 404

    @app.errorhandler(Exception)
    def _unexpected(err):
        app.logger.exception("Unhandled error: %s", err)
        return jsonify({"error": "Erro interno"}), 500
