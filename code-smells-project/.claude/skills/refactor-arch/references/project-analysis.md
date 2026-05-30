# Reference — Project Analysis (Phase 1)

Heuristics to detect the stack and map the architecture **without assuming** any language up front. Always reason from evidence: manifests first, then code.

## 1. Detect the primary language

Look for manifest / lockfiles and source extensions:

| Evidence | Language |
|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | Python |
| `package.json`, `package-lock.json`, `yarn.lock`, `*.js`, `*.ts` | Node.js (JS/TS) |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `composer.json`, `*.php` | PHP |
| `Gemfile`, `*.rb` | Ruby |
| `go.mod`, `*.go` | Go |

Pick the language with the most source files / the manifest at the project root.

## 2. Detect the framework + version

Read the manifest's dependency list, then confirm by import statements in code.

| Signal | Framework |
|---|---|
| `flask` in requirements + `from flask import` | Flask |
| `flask-sqlalchemy`, `from flask_sqlalchemy import SQLAlchemy` | Flask + SQLAlchemy ORM |
| `fastapi` / `from fastapi import` | FastAPI |
| `django` / `manage.py`, `settings.py` | Django |
| `express` in package.json + `require('express')` / `from 'express'` | Express |
| `@nestjs/*` | NestJS |

Record the **version** from the manifest (e.g. `flask==3.1.1` → "Flask 3.1.1"). The version matters for deprecated-API detection.

## 3. Detect the database

- **Driver in deps:** `sqlite3` (Node), stdlib `sqlite3` (Python), `flask-sqlalchemy`, `psycopg2`/`pg`, `mysqlclient`/`mysql2`, `mongoose`/`pymongo`.
- **Connection strings / paths in code:** `sqlite:///tasks.db`, `sqlite3.connect("loja.db")`, `new sqlite3.Database(...)`, `:memory:` (in-memory — data resets each boot), `DATABASE_URL`.
- **Tables / models:**
  - Raw SQL: grep for `CREATE TABLE <name>` and `INSERT INTO <name>` to list tables.
  - ORM: each model class (e.g. SQLAlchemy `db.Model` subclass, Mongoose schema) is a table/collection. Read `__tablename__` or the class name.

## 4. Identify the domain

Infer from table/model names, route paths and seed data. Examples: `produtos/pedidos/usuarios` → e-commerce; `tasks/users/categories` → task manager; `courses/enrollments/payments` → LMS/checkout. State it in one human line ("E-commerce API: products, orders, users").

## 5. Map the current architecture

Classify the current layering honestly:

- **Flat monolith** — everything in a handful of root files; routing + business logic + data access + config mixed together. (e.g. `app.py` + `controllers.py` + `models.py` doing raw SQL, or a single `GodManager` class.)
- **Partially layered** — some folders exist (`models/`, `routes/`, `services/`) but responsibilities still leak (heavy logic in routes, no controllers, config/secrets inline).
- **Layered MVC** — clear models / views|routes / controllers separation with a thin entry point.

Note where the entry point is and how the app boots (e.g. `app.run(...)`, `npm start` → `node src/app.js`, `flask run`), and the port. You will need the boot command for Phase 3 validation.

## 6. Count source files

Count the project's own source files (the ones you analyzed), excluding dependencies, virtualenvs, caches, the `.claude/` skill folder and DB binaries. Report a number that matches reality.

## Output

Feed all of the above into the Phase-1 output block defined in `SKILL.md`. Keep one value per field; be concrete (real versions, real table names, real file count).
