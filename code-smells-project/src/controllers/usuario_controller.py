from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from src.middlewares.error_handler import AppError


class UsuarioController:
    def __init__(self, usuario_model):
        self.model = usuario_model

    def listar(self):
        return jsonify({"dados": self.model.all(), "sucesso": True}), 200

    def buscar(self, id):
        usuario = self.model.by_id(id)
        if not usuario:
            raise AppError("Usuário não encontrado", 404)
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self):
        dados = request.get_json(silent=True) or {}
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise AppError("Nome, email e senha são obrigatórios", 400)
        novo_id = self.model.create(nome, email, generate_password_hash(senha))
        return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201

    def login(self):
        dados = request.get_json(silent=True) or {}
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise AppError("Email e senha são obrigatórios", 400)

        row = self.model.by_email_with_hash(email)
        if not row or not check_password_hash(row["senha"], senha):
            raise AppError("Email ou senha inválidos", 401)

        usuario = {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
