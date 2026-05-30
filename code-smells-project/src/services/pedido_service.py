"""Order business rules — stock check, total computation, persistence and
notification. Lives in the service layer, not in controllers or the data layer."""
from src.middlewares.error_handler import AppError


class PedidoService:
    def __init__(self, pedido_model, notifier):
        self.pedido_model = pedido_model
        self.notifier = notifier

    def criar(self, usuario_id, itens):
        if not usuario_id:
            raise AppError("Usuario ID é obrigatório", 400)
        if not itens:
            raise AppError("Pedido deve ter pelo menos 1 item", 400)

        total = 0
        validados = []
        for item in itens:
            produto = self.pedido_model.produto_estoque_preco(item["produto_id"])
            if produto is None:
                raise AppError(f"Produto {item['produto_id']} não encontrado", 400)
            if produto["estoque"] < item["quantidade"]:
                raise AppError(f"Estoque insuficiente para {produto['nome']}", 400)
            total += produto["preco"] * item["quantidade"]
            validados.append((item, produto))

        pedido_id = self.pedido_model.create(usuario_id, total)
        for item, produto in validados:
            self.pedido_model.add_item(
                pedido_id, item["produto_id"], item["quantidade"], produto["preco"]
            )
            self.pedido_model.decrement_estoque(item["produto_id"], item["quantidade"])

        self.notifier.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self):
        return self.pedido_model.all()

    def listar_por_usuario(self, usuario_id):
        return self.pedido_model.by_usuario(usuario_id)

    def atualizar_status(self, pedido_id, status):
        self.pedido_model.update_status(pedido_id, status)
        self.notifier.status_alterado(pedido_id, status)
        return True
