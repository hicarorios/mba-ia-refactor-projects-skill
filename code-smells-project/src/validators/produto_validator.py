"""Centralized product validation — replaces the duplicated checks that were
copy-pasted across the create/update handlers."""
from src.config.constants import (
    PRODUCT_NAME_MAX_LEN,
    PRODUCT_NAME_MIN_LEN,
    VALID_PRODUCT_CATEGORIES,
)
from src.middlewares.error_handler import AppError


def validate_produto(data, *, require_categoria=False):
    if not data:
        raise AppError("Dados inválidos", 400)

    for field in ("nome", "preco", "estoque"):
        if field not in data:
            raise AppError(f"{field.capitalize()} é obrigatório", 400)

    nome = data["nome"]
    preco = data["preco"]
    estoque = data["estoque"]
    categoria = data.get("categoria", "geral")

    if preco < 0:
        raise AppError("Preço não pode ser negativo", 400)
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo", 400)
    if len(nome) < PRODUCT_NAME_MIN_LEN:
        raise AppError("Nome muito curto", 400)
    if len(nome) > PRODUCT_NAME_MAX_LEN:
        raise AppError("Nome muito longo", 400)
    if categoria not in VALID_PRODUCT_CATEGORIES:
        raise AppError(f"Categoria inválida. Válidas: {VALID_PRODUCT_CATEGORIES}", 400)

    return {
        "nome": nome,
        "descricao": data.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }
