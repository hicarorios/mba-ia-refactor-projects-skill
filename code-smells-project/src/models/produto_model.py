"""Data access for the `produtos` entity. All queries are parameterized."""

FIELDS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def _serialize(row):
    return {field: row[field] for field in FIELDS}


class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def all(self):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM produtos")
        return [_serialize(r) for r in cur.fetchall()]

    def by_id(self, produto_id):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cur.fetchone()
        return _serialize(row) if row else None

    def search(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        sql = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            sql += " AND (nome LIKE ? OR descricao LIKE ?)"
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            sql += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            sql += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            sql += " AND preco <= ?"
            params.append(preco_max)
        cur = self.db.connection.cursor()
        cur.execute(sql, params)
        return [_serialize(r) for r in cur.fetchall()]

    def create(self, nome, descricao, preco, estoque, categoria):
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria)"
            " VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.connection.commit()
        return cur.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        cur = self.db.connection.cursor()
        cur.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?,"
            " categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.connection.commit()
        return True

    def delete(self, produto_id):
        cur = self.db.connection.cursor()
        cur.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.connection.commit()
        return True
