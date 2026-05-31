# Reference — Anti-Pattern Catalog (Phase 2)

Cross-check every source file against this catalog. Each entry has **detection signals** (what to grep/read for, language-agnostic), a **severity**, and **why it matters**. Cite the exact file and line range for every hit.

Severity scale (per the challenge):

- **CRITICAL** — security holes or architecture failures that break correctness or leak sensitive data (hardcoded credentials, SQL injection, God Class mixing DB + logic + routing).
- **HIGH** — strong MVC/SOLID violations that badly hurt maintainability/testability (business logic trapped in controllers, tight coupling without DI, global mutable state).
- **MEDIUM** — standardization, duplication or moderate performance issues (N+1 queries, missing validation, generic exception swallowing).
- **LOW** — readability: bad names, magic numbers, `print` debugging, dead/unused imports.

---

## CRITICAL

### AP-01 — Hardcoded Credentials / Secrets
**Signals:** literal `SECRET_KEY = "..."`, API/payment keys, SMTP user/pass, DB passwords, tokens assigned to string literals in source; secrets returned by an endpoint (e.g. a `/health` payload echoing the secret key).
**Why:** anyone with repo or response access owns the system; secrets can't be rotated per environment.

### AP-02 — SQL Injection (string-built queries)
**Signals:** SQL assembled with string concatenation / interpolation of user input: `"... WHERE id = " + str(id)`, `f"... '{email}'"`, `` `... ${x}` ``, `"%" + termo + "%"`. No parameter binding (`?`, `%s`, named params).
**Why:** attacker-controlled input changes the query — data theft, auth bypass, data loss.

### AP-03 — Arbitrary Code / SQL Execution Endpoint
**Signals:** a route that takes a query/command/expression from the request body and runs it (`cursor.execute(request_body["sql"])`, `eval`, `exec`, shell exec of user input).
**Why:** full remote takeover of the database/host.

### AP-04 — God Class / God Method
**Signals:** one class or file that owns DB connection + queries + business rules + routing + payment/notifications for multiple domains; hundreds of lines; a single method doing validation + persistence + side effects. (e.g. an `AppManager`/`models.py` doing everything.)
**Why:** impossible to test in isolation; every change risks everything; no separation of concerns.

### AP-05 — Insecure Password Storage
**Signals:** passwords stored/compared as **plaintext** (`WHERE senha = '<input>'`), or hashed with broken/fast algorithms (MD5, SHA1, custom "badCrypto"). Password field returned in API responses / `to_dict()`.
**Why:** a DB leak exposes every credential; weak hashes are trivially reversed.

---

## HIGH

### AP-06 — Business Logic in Controller / Route
**Signals:** route handlers that compute totals, apply rules, talk to the DB directly, send emails/SMS/push, format reports — instead of delegating to a service. Notification/side-effect calls inside a request handler.
**Why:** logic can't be reused or unit-tested without HTTP; controllers balloon.

### AP-07 — Global Mutable State / Singleton Connection
**Signals:** module-level mutable globals (`db_connection = None` reused everywhere, `globalCache = {}`, `totalRevenue` accumulator); a single shared connection mutated across requests.
**Why:** hidden coupling, race conditions, untestable, leaks state between requests.

### AP-08 — Debug Mode / Insecure Defaults in Production
**Signals:** `debug=True`, `DEBUG = True`, `app.run(..., debug=True)`, binding `0.0.0.0` with debug on, stack traces returned to clients, permissive CORS `*`.
**Why:** debug consoles allow code execution; verbose errors leak internals.

### AP-09 — Tight Coupling / No Dependency Injection
**Signals:** layers importing concrete modules directly and instantiating their own dependencies (handler `import`s the DB module and the mailer directly); no seam to substitute a fake.
**Why:** can't test a layer in isolation; swapping an implementation means editing callers.

---

## MEDIUM

### AP-10 — N+1 Query
**Signals:** a loop that issues one query per iteration — `for row in rows: cursor.execute("SELECT ... WHERE fk = " + row.id)`; building a list then querying details per element.
**Why:** O(N) round-trips; degrades badly with data volume.

### AP-11 — Missing / Duplicated Validation
**Signals:** request fields used without presence/type/range checks; OR the same validation block copy-pasted across many handlers; the same derived computation (e.g. "is overdue", stats) duplicated in several places instead of one model method.
**Why:** inconsistent behavior, bugs when one copy changes, invalid data reaching the DB.

### AP-12 — Generic Exception Swallowing
**Signals:** `except:` / `except Exception: pass`, bare `catch (e) {}`, returning raw `str(e)` to the client as the only handling; no centralized error handler.
**Why:** hides real failures, leaks internals, makes debugging impossible.

### AP-13 — Deprecated / Obsolete API Usage  *(mandatory detection)*
Detect use of APIs that are deprecated or removed in the detected framework/runtime version, and recommend the modern equivalent. Common signals by stack:

| Stack | Deprecated signal | Modern replacement |
|---|---|---|
| Flask ≥2.3 | `@app.before_first_request` | run init at startup / app-factory, or a one-time guard |
| Flask | `flask.Markup`, `flask.json.JSONEncoder` | `markupsafe.Markup`, custom `app.json` provider |
| Python ≥3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(datetime.UTC)` |
| Python ≥3.12 | implicit `sqlite3` datetime adapters | register explicit adapters/converters |
| Python | `imp` module | `importlib` |
| Node/Express | `body-parser` as separate dep | built-in `express.json()` / `express.urlencoded()` |
| Node | `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
| Node | `url.parse()` | `new URL()` |
| Node | `crypto.createCipher` | `crypto.createCipheriv` |

If the project genuinely uses none, record "no deprecated APIs detected" — but always run the check.

---

## LOW

### AP-14 — `print` / `console.log` as Logging
**Signals:** `print(...)` / `console.log(...)` used for operational logging or notifications inside handlers/business code.
**Why:** no levels, no structure, noisy, not configurable per environment.

### AP-15 — Magic Numbers
**Signals:** unexplained literals in logic — discount tiers (`> 10000 → *0.1`), priority ranges, page sizes, time windows (`7` days), ports.
**Why:** intent is hidden; changes are error-prone and scattered.

### AP-16 — Poor Naming
**Signals:** single-letter / cryptic identifiers for meaningful data (`u`, `e`, `p`, `cid`, `cc`, `pwd`), misleading names.
**Why:** code is hard to read and reason about.

### AP-17 — Dead / Unused Imports & Code
**Signals:** imported modules never used (`import os, sys, json, time, math, hashlib` with no references); unreachable or commented-out blocks.
**Why:** noise, false dependencies, slower comprehension.

---

## How to use this catalog

- This catalog defines **17 anti-pattern types across all four severities**. For each project, surface **≥ 5 findings** with **≥ 1 CRITICAL/HIGH**, drawing from as many distinct types as the code warrants.
- One physical issue can map to one finding even if it recurs on many lines — cite the representative line(s) and note "and N other occurrences".
- Always include the deprecated-API check (AP-13).
