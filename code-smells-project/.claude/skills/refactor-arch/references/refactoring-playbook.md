# Reference — Refactoring Playbook (Phase 3)

Concrete before/after transformations, one per major anti-pattern. Examples are given in Python/Flask and Node/Express; apply the same idea to any stack. Each transformation maps back to an anti-pattern ID from `anti-patterns-catalog.md`.

---

## T-01 — Externalize secrets to a config module (AP-01, AP-08)

**Before (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**After — `src/config/settings.py`:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

def _require(key):
    v = os.environ.get(key)
    if not v:
        raise RuntimeError(f"{key} is required — copy .env.example to .env and fill it in")
    return v

class Settings:
    SECRET_KEY = _require("SECRET_KEY")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

settings = Settings()
```
Ship `.env.example` listing every variable. **Never** return a secret from an endpoint (strip it from `/health`).

**Node equivalent:** a `src/config/settings.js` reading `process.env`, loaded via `dotenv`.

---

## T-02 — Parameterized queries (AP-02)

**Before:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))  # verify password via hash, see T-08
```
For dynamic filters, build the parameter list, never the values:
```python
sql = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    sql += " AND (nome LIKE ? OR descricao LIKE ?)"; params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    sql += " AND categoria = ?"; params.append(categoria)
cursor.execute(sql, params)
```
**Node:** `db.all("SELECT * FROM x WHERE id = ?", [id], cb)` — placeholders + bind array.

---

## T-03 — Split a God Class/method into layers (AP-04, AP-09)

**Before:** one `models.py` / `AppManager` holding connection + queries + rules + routing for every domain.
**After:** per-domain repository (model) + service + controller, wired in the composition root.
```python
# src/models/produto_model.py
class ProdutoModel:
    def __init__(self, db): self.db = db
    def all(self):
        cur = self.db.cursor(); cur.execute("SELECT * FROM produtos")
        return [dict(r) for r in cur.fetchall()]

# src/controllers/produto_controller.py
class ProdutoController:
    def __init__(self, model): self.model = model
    def listar(self):
        return jsonify({"dados": self.model.all(), "sucesso": True}), 200
```
Dependencies are **injected** (constructor params), not imported-and-instantiated inside, so each layer is testable with a fake.

---

## T-04 — Move business logic out of controllers into services (AP-06)

**Before (route handler computes total, persists, sends notifications):**
```python
def criar_pedido():
    ...
    print("ENVIANDO EMAIL: ..."); print("ENVIANDO SMS: ...")
```
**After:**
```python
# src/services/pedido_service.py
class PedidoService:
    def __init__(self, pedido_model, notifier): self.model, self.notifier = pedido_model, notifier
    def criar(self, usuario_id, itens):
        pedido = self.model.criar(usuario_id, itens)   # data layer
        self.notifier.pedido_criado(pedido)            # side effect, abstracted
        return pedido

# controller just orchestrates
def criar_pedido():
    dados = request.get_json()
    pedido = service.criar(dados["usuario_id"], dados["itens"])
    return jsonify({"dados": pedido, "sucesso": True}), 201
```
Notifications go behind a `NotificationService` (which may still log in dev) — not `print` in the handler.

---

## T-05 — Centralized error handling (AP-12)

**Before:** every handler wrapped in `try/except Exception as e: return jsonify({"erro": str(e)}), 500`.
**After — one error handler:**
```python
# src/middlewares/error_handler.py
class AppError(Exception):
    def __init__(self, message, status=400): super().__init__(message); self.status = status

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app_err(e): return jsonify({"erro": str(e), "sucesso": False}), e.status
    @app.errorhandler(Exception)
    def _unexpected(e):
        app.logger.exception(e)
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
```
Handlers raise `AppError("Produto não encontrado", 404)`; they no longer swallow exceptions or leak `str(e)`.
**Node:** an `errorHandler(err, req, res, next)` middleware registered last + an `asyncHandler` wrapper.

---

## T-06 — Fix N+1 queries (AP-10)

**Before:**
```python
for row in pedidos:
    cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
**After — single join, group in memory:**
```python
cursor.execute("""
    SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
    FROM itens_pedido ip JOIN produtos p ON p.id = ip.produto_id
    WHERE ip.pedido_id IN ({})
""".format(",".join("?" * len(ids))), ids)
# then group rows by pedido_id in Python
```
Same observable response, O(1) round-trips.

---

## T-07 — Extract & centralize validation (AP-11)

**Before:** the same presence/range checks copy-pasted across handlers; the same derived computation repeated in many places.
**After:** a validator/schema per resource, and domain computations pushed into the model.
```python
# src/validators/produto_validator.py
def validate_produto(data):
    errors = []
    if not data.get("nome") or len(data["nome"]) < 2: errors.append("nome inválido")
    if data.get("preco", 0) < 0: errors.append("preço negativo")
    if errors: raise AppError("; ".join(errors), 400)
```
```python
# duplicated "is overdue" logic → one model method
class Task(db.Model):
    def is_overdue(self):
        return self.due_date is not None and self.due_date < datetime.now(UTC) and not self.done
```

---

## T-08 — Secure password storage + re-seed (AP-05)

**Before:** plaintext compare (`WHERE senha = '<input>'`) or MD5; password returned in payloads.
**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
# on create:  senha_hash = generate_password_hash(senha)
# on login:   user = model.by_email(email); ok = check_password_hash(user["senha"], senha)
```
- Remove the password field from every serialized response / `to_dict()`.
- **Re-seed** existing demo users with hashed passwords so the login endpoint keeps returning 200 for the documented credentials after the change. (Update the seed/DB-init to store `generate_password_hash(...)`.)
**Node:** `bcrypt.hashSync` / `bcrypt.compareSync`; never a custom `badCrypto`.

---

## T-09 — Neutralize dangerous endpoints, keep them responding (AP-03)

**Before:** `POST /admin/query` runs arbitrary SQL from the body.
**After:** keep the route registered (contract preserved) but remove the capability:
```python
def admin_query():
    # arbitrary SQL execution removed for security; route kept for contract compatibility
    raise AppError("Endpoint desativado por segurança", 403)
```
Or gate behind an admin token and a fixed, safe operation. The route still **responds** (now 403/safe), it does not 404.

---

## T-10 — Replace `print` logging, kill magic numbers & dead code (AP-14, AP-15, AP-17)

- Swap `print(...)` for the framework logger (`app.logger.info(...)` / a `logger` util with levels).
- Name magic numbers as constants with intent:
```python
# src/config/constants.py
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]
```
- Delete unused imports (`os, sys, json, time, math, hashlib` when unreferenced) and dead/commented code.
- Rename cryptic identifiers (`u`→`user`, `cc`→`card_number`, `pwd`→`password`).

---

## T-11 — Replace deprecated APIs (AP-13)

Apply the modern equivalent from the catalog's deprecated-API table, e.g.:
- `datetime.utcnow()` → `datetime.now(datetime.UTC)`
- Flask `@app.before_first_request` → init in the app factory / one-time guard
- Express `body-parser` → `express.json()`; `new Buffer(x)` → `Buffer.from(x)`

---

## Applying the playbook

Work finding-by-finding from the audit report (CRITICAL first). After each layer is in place, keep the **same routes and response shapes**. When done, run the Phase-3 validation (boot + baseline parity) before printing the completion block.
