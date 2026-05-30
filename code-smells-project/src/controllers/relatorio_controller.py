from flask import jsonify


class RelatorioController:
    def __init__(self, relatorio_service):
        self.service = relatorio_service

    def vendas(self):
        return jsonify({"dados": self.service.vendas(), "sucesso": True}), 200
