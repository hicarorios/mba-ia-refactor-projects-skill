from flask import jsonify, request

from src.middlewares.error_handler import AppError
from src.validators.produto_validator import validate_produto


class ProdutoController:
    def __init__(self, produto_model):
        self.model = produto_model

    def listar(self):
        return jsonify({"dados": self.model.all(), "sucesso": True}), 200

    def buscar(self, id):
        produto = self.model.by_id(id)
        if not produto:
            raise AppError("Produto não encontrado", 404)
        return jsonify({"dados": produto, "sucesso": True}), 200

    def buscar_lista(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria")
        preco_min = request.args.get("preco_min", type=float)
        preco_max = request.args.get("preco_max", type=float)
        resultados = self.model.search(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

    def criar(self):
        dados = validate_produto(request.get_json(silent=True))
        novo_id = self.model.create(**dados)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    def atualizar(self, id):
        if not self.model.by_id(id):
            raise AppError("Produto não encontrado", 404)
        dados = validate_produto(request.get_json(silent=True))
        self.model.update(id, **dados)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, id):
        if not self.model.by_id(id):
            raise AppError("Produto não encontrado", 404)
        self.model.delete(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
