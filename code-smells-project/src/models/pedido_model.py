"""Data access for orders. Order assembly uses a single JOIN (no N+1)."""


class PedidoModel:
    def __init__(self, db):
        self.db = db

    def produto_estoque_preco(self, produto_id):
        cur = self.db.connection.cursor()
        cur.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?", (produto_id,)
        )
        return cur.fetchone()

    def create(self, usuario_id, total):
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        self.db.connection.commit()
        return cur.lastrowid

    def add_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)"
            " VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario),
        )
        self.db.connection.commit()

    def decrement_estoque(self, produto_id, quantidade):
        cur = self.db.connection.cursor()
        cur.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )
        self.db.connection.commit()

    def update_status(self, pedido_id, status):
        cur = self.db.connection.cursor()
        cur.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
        self.db.connection.commit()
        return True

    def _items_by_pedido(self, pedido_ids):
        """All items for the given orders in ONE query joined to product names."""
        if not pedido_ids:
            return {}
        placeholders = ",".join("?" * len(pedido_ids))
        cur = self.db.connection.cursor()
        cur.execute(
            f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})
            """,
            list(pedido_ids),
        )
        grouped = {}
        for r in cur.fetchall():
            grouped.setdefault(r["pedido_id"], []).append({
                "produto_id": r["produto_id"],
                "produto_nome": r["produto_nome"] or "Desconhecido",
                "quantidade": r["quantidade"],
                "preco_unitario": r["preco_unitario"],
            })
        return grouped

    def _assemble(self, rows):
        items_map = self._items_by_pedido([r["id"] for r in rows])
        return [{
            "id": r["id"],
            "usuario_id": r["usuario_id"],
            "status": r["status"],
            "total": r["total"],
            "criado_em": r["criado_em"],
            "itens": items_map.get(r["id"], []),
        } for r in rows]

    def all(self):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM pedidos")
        return self._assemble(cur.fetchall())

    def by_usuario(self, usuario_id):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return self._assemble(cur.fetchall())

    def report_counts(self):
        cur = self.db.connection.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(total), 0) AS faturamento,
                SUM(status = 'pendente')  AS pendentes,
                SUM(status = 'aprovado')  AS aprovados,
                SUM(status = 'cancelado') AS cancelados
            FROM pedidos
            """
        )
        return cur.fetchone()
