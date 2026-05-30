"""Database connection + schema bootstrap.

The connection is encapsulated in a `Database` object created once in the
composition root and injected into the models — no module-level mutable
global connection (fixes the singleton anti-pattern).
"""
import sqlite3

from werkzeug.security import generate_password_hash

SCHEMA = {
    "produtos": """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, descricao TEXT, preco REAL, estoque INTEGER,
            categoria TEXT, ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
    "usuarios": """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, email TEXT, senha TEXT, tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
    "pedidos": """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER, status TEXT DEFAULT 'pendente', total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
    "itens_pedido": """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER, produto_id INTEGER,
            quantidade INTEGER, preco_unitario REAL
        )""",
}

SEED_PRODUTOS = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Demo users — passwords are hashed at seed time so the stored value is never
# plaintext, while the documented credentials still authenticate.
SEED_USUARIOS = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    @property
    def connection(self):
        return self._conn

    def init_schema(self):
        cur = self._conn.cursor()
        for ddl in SCHEMA.values():
            cur.execute(ddl)
        self._conn.commit()
        self._seed_if_empty()

    def _seed_if_empty(self):
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM produtos")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria)"
                " VALUES (?, ?, ?, ?, ?)",
                SEED_PRODUTOS,
            )
            cur.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                [(n, e, generate_password_hash(s), t) for n, e, s, t in SEED_USUARIOS],
            )
            self._conn.commit()
