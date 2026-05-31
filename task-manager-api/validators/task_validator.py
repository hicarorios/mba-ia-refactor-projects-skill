"""Task field validation, shared by create and update flows."""
from datetime import datetime

from middlewares.error_handler import AppError
from utils.helpers import (
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
)

PRIORITY_MIN = 1
PRIORITY_MAX = 5


def validate_title(title):
    if not title:
        raise AppError('Título é obrigatório', 400)
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto', 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo', 400)
    return title


def validate_status(status):
    if status not in VALID_STATUSES:
        raise AppError('Status inválido', 400)
    return status


def validate_priority(priority):
    if priority < PRIORITY_MIN or priority > PRIORITY_MAX:
        raise AppError('Prioridade deve ser entre 1 e 5', 400)
    return priority


def parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise AppError('Formato de data inválido. Use YYYY-MM-DD', 400)


def normalize_tags(tags):
    if tags is None:
        return None
    return ','.join(tags) if isinstance(tags, list) else tags
