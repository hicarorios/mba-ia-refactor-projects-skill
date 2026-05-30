"""Composition root — builds the app and wires the layers together."""
import logging
from types import SimpleNamespace

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.controllers.admin_controller import AdminController
from src.controllers.health_controller import HealthController
from src.controllers.pedido_controller import PedidoController
from src.controllers.produto_controller import ProdutoController
from src.controllers.relatorio_controller import RelatorioController
from src.controllers.usuario_controller import UsuarioController
from src.middlewares.error_handler import register_error_handlers
from src.models.connection import Database
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.services.notification_service import NotificationService
from src.services.pedido_service import PedidoService
from src.services.relatorio_service import RelatorioService
from src.views.routes import register_routes


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    # Data layer
    db = Database(settings.DB_PATH)
    db.init_schema()
    produto_model = ProdutoModel(db)
    usuario_model = UsuarioModel(db)
    pedido_model = PedidoModel(db)

    # Service layer
    notifier = NotificationService()
    pedido_service = PedidoService(pedido_model, notifier)
    relatorio_service = RelatorioService(pedido_model)

    # Controllers (dependencies injected)
    controllers = SimpleNamespace(
        produto=ProdutoController(produto_model),
        usuario=UsuarioController(usuario_model),
        pedido=PedidoController(pedido_service),
        relatorio=RelatorioController(relatorio_service),
        health=HealthController(db),
        admin=AdminController(db),
    )

    register_routes(app, controllers)
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
