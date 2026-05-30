================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 4
Deprecated APIs: none detected (Flask 3.1.1 / current stdlib usage)

## Findings

### [CRITICAL] SQL Injection — string-built queries (AP-02)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-166, 174, 188, 192, 280, 289-299 (and the /admin endpoints in app.py)
Description: Practically every query is assembled by concatenating user-controlled input into the SQL string (e.g. `"... WHERE id = " + str(id)`, `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`, `"... nome LIKE '%" + termo + "%'"`). No parameter binding anywhere.
Impact: Trivial data theft, authentication bypass on /login, and data destruction via crafted input.
Recommendation: Replace all concatenation with parameterized queries (placeholders + bind values). See playbook T-02.

### [CRITICAL] Arbitrary SQL Execution Endpoint (AP-03)
File: app.py:59-78
Description: `POST /admin/query` reads `sql` from the request body and executes it directly against the database, returning rows or committing writes.
Impact: Full remote takeover of the database — any client can read/alter/drop any table. There is also `POST /admin/reset-db` (app.py:47-57) wiping all tables with no auth.
Recommendation: Keep the route registered but remove arbitrary execution (return 403 / gate behind an admin token). See playbook T-09.

### [CRITICAL] Hardcoded Secret + secret leaked by endpoint (AP-01)
File: app.py:7 (SECRET_KEY literal); controllers.py:289 (/health returns the secret)
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` is hardcoded, and the `/health` response echoes `secret_key`, `debug` and `db_path` back to any caller.
Impact: Secret cannot be rotated per environment and is exposed to anyone hitting /health — session forgery and credential exposure.
Recommendation: Move secrets to an env-based config module; strip secrets from /health. See playbook T-01.

### [CRITICAL] Insecure Password Storage — plaintext (AP-05)
File: database.py:75-83 (seed stores plaintext), models.py:105-120 (login compares plaintext), models.py:82, 99 (password returned in user payloads)
Description: Passwords are stored and compared as plaintext, and the password field is returned by `get_todos_usuarios` / `get_usuario_por_id`.
Impact: A single DB read exposes every user credential; passwords travel in API responses.
Recommendation: Hash with werkzeug/bcrypt, stop returning the password field, and re-seed demo users with hashed values. See playbook T-08.

### [HIGH] Business logic & side effects inside controllers (AP-06)
File: controllers.py:208-210, 247-250 (notifications via print in handlers); models.py:133-169 (order total + stock rules in the data layer)
Description: Request handlers send "email/SMS/push" notifications inline and the order-creation rules live mixed into the data layer; there is no service layer.
Impact: Business rules cannot be reused or unit-tested without HTTP; concerns are tangled.
Recommendation: Introduce a service layer; controllers only orchestrate; notifications behind a NotificationService. See playbook T-04.

### [HIGH] Global mutable singleton DB connection (AP-07)
File: database.py:4-10
Description: A module-level `db_connection` global is lazily created and shared across all requests (`check_same_thread=False`).
Impact: Hidden coupling and thread-safety hazards; state leaks across requests; untestable.
Recommendation: Encapsulate connection creation in config/model layer and inject it. See playbook T-03.

### [HIGH] Debug mode + insecure defaults in production (AP-08)
File: app.py:8 (`DEBUG=True`), app.py:88 (`app.run(host="0.0.0.0", ..., debug=True)`), controllers.py:286 (`"ambiente": "producao"`)
Description: Debug is hardcoded on while the app advertises itself as "producao", bound to 0.0.0.0; raw `str(e)` is returned to clients on errors throughout.
Impact: The Werkzeug debugger allows code execution; stack traces and internals leak to clients.
Recommendation: Drive DEBUG from env (default false); centralize error handling. See playbook T-01, T-05.

### [MEDIUM] N+1 queries when assembling orders (AP-10)
File: models.py:171-201 (get_pedidos_usuario), 203-233 (get_todos_pedidos)
Description: For each order a query fetches its items, and for each item another query fetches the product name — one query per row, nested.
Impact: O(N) round-trips; performance collapses as orders/items grow.
Recommendation: Single JOIN over items+products, group in memory. See playbook T-06.

### [MEDIUM] Duplicated & scattered validation (AP-11)
File: controllers.py:28-54 vs 72-90 (product validation duplicated between create/update); 157-158, 173-174 (ad-hoc presence checks)
Description: The same presence/range/category validation is copy-pasted across handlers with no shared validator.
Impact: Rules drift between copies; inconsistent error behavior.
Recommendation: Extract per-resource validators. See playbook T-07.

### [MEDIUM] Generic exception swallowing / no central handler (AP-12)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 291-292
Description: Every handler wraps its body in `try/except Exception as e` and returns `str(e)` with 500; there is no centralized error handling.
Impact: Real errors are masked, internals leak, behavior is inconsistent.
Recommendation: Centralized error handler + typed AppError. See playbook T-05.

### [LOW] `print` used as logging (AP-14)
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Description: Operational logging and notifications use `print(...)`.
Impact: No levels/structure, not configurable per environment.
Recommendation: Use the framework logger. See playbook T-10.

### [LOW] Magic numbers in the sales report (AP-15)
File: models.py:256-262
Description: Discount tiers use unexplained literals (`> 10000 → *0.1`, `> 5000 → *0.05`, `> 1000 → *0.02`).
Impact: Intent hidden; changes are error-prone.
Recommendation: Name them as constants (DISCOUNT_TIERS). See playbook T-10.

### [LOW] Duplicated row→dict serialization (AP-11/AP-17)
File: models.py:12-21, 31-40, 79-86, 95-102, 304-313
Description: The same product/user dict-building block is copy-pasted across many functions.
Impact: Maintenance burden; drift risk.
Recommendation: A single serializer per entity (model method / schema). See playbook T-07.

### [LOW] Unused import (AP-17)
File: models.py:2 (`import sqlite3` unused), database.py:2 (`import os` unused)
Description: Imported modules are never referenced.
Impact: Noise and false dependencies.
Recommendation: Remove unused imports. See playbook T-10.

================================
Total: 14 findings
================================
