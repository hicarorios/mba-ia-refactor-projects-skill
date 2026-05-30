from flask import jsonify, request

from src.config.constants import VALID_ORDER_STATUSES
from src.middlewares.error_handler import AppError


class PedidoController:
    def __init__(self, pedido_service):
        self.service = pedido_service

    def criar(self):
        dados = request.get_json(silent=True) or {}
        resultado = self.service.criar(dados.get("usuario_id"), dados.get("itens", []))
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

    def listar_todos(self):
        return jsonify({"dados": self.service.listar_todos(), "sucesso": True}), 200

    def listar_por_usuario(self, usuario_id):
        return jsonify({"dados": self.service.listar_por_usuario(usuario_id), "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json(silent=True) or {}
        novo_status = dados.get("status", "")
        if novo_status not in VALID_ORDER_STATUSES:
            raise AppError("Status inválido", 400)
        self.service.atualizar_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
