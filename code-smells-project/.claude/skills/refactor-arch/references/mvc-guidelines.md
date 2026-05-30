# Reference — Target MVC Architecture (Phase 3)

The target is a clean **MVC** layering with clear responsibilities. The skill adapts the *shape* of the change to the project's current organization, but the *responsibilities* below are constant across stacks.

## The layers and their single responsibilities

| Layer | Owns | Must NOT contain |
|---|---|---|
| **Config** | Settings read from environment (secrets, DB path/URL, host/port, flags). | Hardcoded secrets, business logic. |
| **Models** (data layer) | Data access for one domain entity: queries / ORM mapping, parameterized. Domain-derived computations that belong to the entity (e.g. `is_overdue`). | HTTP concerns, routing, cross-domain orchestration. |
| **Views / Routes** | HTTP routing only: map a method+path to a controller action; (de)serialize. In strict MVC for APIs, the "view" is the response representation. | Business rules, DB access. |
| **Controllers** | Orchestrate one request: read input → call service/model → shape response. Thin. | Heavy business logic, raw SQL, side effects like sending email. |
| **Services** (when business logic exists) | Reusable business rules and side effects (checkout flow, notifications, reports). | HTTP request/response objects, framework globals. |
| **Middlewares** | Cross-cutting concerns: centralized error handling, auth, request logging, validation. | Per-route business logic. |
| **Entry point (composition root)** | Build the app, wire layers together, register routes/blueprints, start the server. | Inline routes with logic, queries. |

Dependency direction: routes → controllers → services → models → config. Inner layers never import outer ones.

## Choosing the layout — adapt to context

**A) Flat monolith** (everything in a few root files, e.g. `app.py` + `controllers.py` + `models.py`, or a single God class):
→ Restructure into a `src/` package:

```
src/
├── config/        # settings.py (env-based)
├── models/        # one module per domain entity (+ db/connection)
├── views/ (or routes/)   # routing only
├── controllers/   # one per domain
├── services/      # business logic / side effects
├── middlewares/   # error_handler, auth
└── app.py         # composition root
```
Keep a thin root entry point (e.g. root `app.py` that imports and runs `src/app.py`) if the original boot command must keep working.

**B) Already partially layered** (folders like `models/`, `routes/`, `services/` already exist):
→ **Deepen in place. Do not move everything into a new `src/` wrapper.** Keep the existing top-level layers and add the missing ones at the same level:
- add `controllers/` so routes stop carrying business logic;
- add/expand `services/` for business rules;
- add `config/` (env-based settings) and remove inline secrets;
- add `middlewares/` for centralized error handling and auth;
- add `validators/` (or schemas) if validation is scattered;
- push duplicated domain computations down into the model.

The goal in case B is the same separation of concerns with the **least disruptive** move, so the endpoint contract stays intact. A project already having folders does not mean its architecture is adequate — judge by responsibilities, not by folder presence.

## Invariants for both layouts

- **Config from environment**, never hardcoded; ship a `.env.example`.
- **Centralized error handling** (one place turns exceptions into HTTP responses).
- **One clear entry point.**
- **Same routes, same observable responses** as before (preserve the public contract).
- Dangerous routes are **neutralized, not deleted** (keep responding).
- After auth-related changes (password hashing), **re-seed** data so login still works.
