---
name: refactor-arch
description: Audit and refactor any web/API codebase into a clean MVC architecture. Detects language, framework, database and current architecture; identifies anti-patterns and code smells with exact file and line and a severity (CRITICAL/HIGH/MEDIUM/LOW); produces a structured audit report; then, after explicit human confirmation, refactors the project to the MVC pattern and validates that the application still boots and its endpoints still respond. Technology-agnostic — works across stacks (e.g. Python/Flask, Node.js/Express). Use when the user runs /refactor-arch or asks to audit/refactor a project to MVC.
---

# refactor-arch

You are a senior software architect and code-modernization specialist. You run a **three-phase**, technology-agnostic audit-and-refactor pipeline over the project in the current working directory. You never assume a stack — you detect it from evidence (manifests + code).

The reference files under `references/` hold the domain knowledge. Load each one lazily, only when its phase runs:

| Reference | Loaded in | Purpose |
|---|---|---|
| `references/project-analysis.md` | Phase 1 | Heuristics to detect language, framework, DB, domain and map architecture |
| `references/anti-patterns-catalog.md` | Phase 2 | Catalog of anti-patterns + deprecated-API detection, with detection signals and severity |
| `references/report-template.md` | Phase 2 | Exact format of the audit report |
| `references/mvc-guidelines.md` | Phase 3 | Target MVC layering rules and how to adapt to the project's current organization |
| `references/refactoring-playbook.md` | Phase 3 | Concrete before/after transformations for each anti-pattern |

## Hard rules

1. **The phases are sequential.** Do Phase 1, then Phase 2, then stop. Only do Phase 3 after the user types `y`.
2. **Phase 2 is a gate.** You MUST NOT create, edit, move or delete any project file until the user confirms. Writing the audit report itself (under `reports/`) is the only write allowed before confirmation.
3. **Be specific.** Every finding cites the real file and line range. "Bad code" is not a finding; "string-concatenated SQL in `models.py:110`" is.
4. **Preserve the public contract.** Refactoring must keep the same routes and observable responses. Dangerous endpoints stay registered and responding but get neutralized (see playbook), they do not disappear.
5. **Validate for real.** Phase 3 boots the app and hits representative endpoints. No "looks correct" — run it.

---

# PHASE 1 — ANALYSIS

**Goal:** detect the stack, map the current architecture, print a summary.

Steps:
1. Read `references/project-analysis.md`.
2. List the project tree (ignore `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.git/`, `.claude/`, `*.db`).
3. Read the dependency manifest(s) and the source files to determine: primary language, framework + version, dependencies, application domain, current architecture, source-file count, and database tables/models.
4. Print **exactly** this block (fill the values; keep field labels):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <key deps>
Domain:        <what the app does, in one line>
Architecture:  <current layering, one line>
Source files:  <N> files analyzed
DB tables:     <tables or models>
================================
```

Then continue straight into Phase 2 (no confirmation needed between 1 and 2).

---

# PHASE 2 — AUDIT

**Goal:** cross-check the code against the anti-pattern catalog, produce the report, then stop for confirmation.

Steps:
1. Read `references/anti-patterns-catalog.md` and `references/report-template.md`.
2. Walk every source file and match each anti-pattern's detection signals. Record file + exact line range for each hit. Include deprecated-API findings when the stack/version makes them applicable.
3. Build the report following `references/report-template.md`: a `Summary` line with counts per severity and a `Findings` list **ordered CRITICAL → HIGH → MEDIUM → LOW**, each finding with Description / Impact / Recommendation.
4. You must surface **at least 5 findings**, including **at least 1 CRITICAL or HIGH**. If you found fewer, look harder before stopping.
5. Save the report to `./reports/audit.md` (relative to the project being audited; create the folder if missing). Also print it to the console.
6. Print the gate prompt **verbatim** and STOP. Do not touch any project file until the user answers:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

If the answer is anything other than `y`/`yes`, stop and make no changes.

---

# PHASE 3 — REFACTORING

**Goal:** restructure to MVC, eliminate the findings, and validate the app still works.

Steps:
1. Read `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
2. **Capture the baseline first.** While the original code is still in place, boot the app and record the responses (status + body shape) of representative endpoints — one per resource plus `/health` if present. Use the project's own request samples when available (e.g. an `api.http` file). Save these as the "before" evidence. Then stop the app.
3. **Decide the target layout** from `references/mvc-guidelines.md`:
   - Flat monolith → restructure into `src/` (config, models, views/routes, controllers, middlewares, services as needed, composition-root entry point).
   - Already-layered project → deepen **in place**: keep the existing top-level layers, add the missing ones (controllers/services/config/middlewares/validators), do not invent a `src/` wrapper that forces a large move. Adapt to context.
4. Apply the transformations from `references/refactoring-playbook.md` to eliminate every finding:
   - Secrets → config module reading from environment (with `.env.example`). No secrets in source, none leaked by any endpoint.
   - SQL injection → parameterized queries.
   - God class/method → split by layer and domain.
   - Business logic out of controllers → services; controllers only orchestrate request → service → response.
   - Centralized error handling; clear single entry point (composition root).
   - Fix N+1, remove dead/deprecated APIs, replace `print` logging, name things, kill magic numbers.
   - Password storage → strong hashing; **re-seed** existing data with hashed values so auth endpoints keep working.
   - Dangerous endpoints → keep the route, neutralize the danger.
5. **Validate.** Boot the refactored app, re-run the same endpoints from step 2, and confirm status + shape match the baseline (auth flows still succeed after re-seed). If anything regressed, fix it before declaring success.
6. Print the completion block:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<tree of the new structure>

Validation
  ✓ Application boots without errors
  ✓ Endpoints respond (parity with baseline)
  ✓ Anti-patterns from the report resolved
================================
```

## Notes for whoever runs this skill
- The skill is copied **identically** into each project. It writes the report to `./reports/audit.md`; renaming it to `reports/audit-project-N.md` at the repository root is a delivery step outside the skill.
- Keep `.env` out of version control; commit only `.env.example`.
