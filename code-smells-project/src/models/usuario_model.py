"""Data access for the `usuarios` entity. Passwords are never returned."""

# Public fields exclude `senha` — the password hash is never serialized out.
PUBLIC_FIELDS = ("id", "nome", "email", "tipo", "criado_em")


def _serialize(row):
    return {field: row[field] for field in PUBLIC_FIELDS}


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def all(self):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM usuarios")
        return [_serialize(r) for r in cur.fetchall()]

    def by_id(self, usuario_id):
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cur.fetchone()
        return _serialize(row) if row else None

    def by_email_with_hash(self, email):
        """Returns the full row (incl. senha hash) for authentication only."""
        cur = self.db.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cur.fetchone()

    def create(self, nome, email, senha_hash, tipo="cliente"):
        cur = self.db.connection.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        self.db.connection.commit()
        return cur.lastrowid
