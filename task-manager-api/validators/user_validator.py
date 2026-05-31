"""User field validation, shared by create and update flows."""
import re

from middlewares.error_handler import AppError
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES

EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def validate_email(email):
    if not email:
        raise AppError('Email é obrigatório', 400)
    if not EMAIL_RE.match(email):
        raise AppError('Email inválido', 400)
    return email


def validate_password(password):
    if not password:
        raise AppError('Senha é obrigatória', 400)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError('Senha deve ter no mínimo 4 caracteres', 400)
    return password


def validate_role(role):
    if role not in VALID_ROLES:
        raise AppError('Role inválido', 400)
    return role
