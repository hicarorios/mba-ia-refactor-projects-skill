"""Notifications behind a service — replaces print() side effects that lived
directly inside the request handlers."""
import logging

logger = logging.getLogger("loja.notifications")


class NotificationService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("Email/SMS/Push: pedido %s criado para usuário %s", pedido_id, usuario_id)

    def status_alterado(self, pedido_id, status):
        if status == "aprovado":
            logger.info("Pedido %s aprovado — preparar envio.", pedido_id)
        elif status == "cancelado":
            logger.info("Pedido %s cancelado — devolver estoque.", pedido_id)
