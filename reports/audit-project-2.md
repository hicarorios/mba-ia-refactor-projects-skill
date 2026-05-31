================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2
Deprecated APIs: none detected (Express 4.18 uses express.json(); Buffer.from used correctly)

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets (AP-01)
File: src/utils.js:1-7
Description: DB user/password, the live payment gateway key (`pk_live_...`) and the SMTP user are hardcoded in a `config` object shipped in source.
Impact: A live payment key and production DB credentials are exposed to anyone with repo access; they cannot be rotated per environment.
Recommendation: Move to an env-based config module with `.env.example`; never commit real keys. See playbook T-01.

### [CRITICAL] God Class — AppManager (AP-04)
File: src/AppManager.js:1-141
Description: A single class owns the DB connection, schema/seed, HTTP routing, the checkout business flow, payment processing, auditing and the financial report — for every domain.
Impact: Impossible to test in isolation; any change risks the whole system; no separation of concerns.
Recommendation: Split into config + repositories (models) + services + controllers + routes, wired in a composition root. See playbook T-03, T-04.

### [CRITICAL] Insecure Password Storage — custom hash + plaintext seed (AP-05)
File: src/utils.js:17-23 (`badCrypto`), src/AppManager.js:18 (seed `pass = '123'`), :68 (uses badCrypto)
Description: Passwords are "hashed" by a homegrown base64 loop (`badCrypto`) and the seeded user stores the plaintext `'123'`. No salt, trivially reversible.
Impact: A DB leak exposes every credential; the scheme provides no real protection.
Recommendation: Use bcrypt (`bcrypt.hashSync`/`compareSync`); re-seed with hashed values. See playbook T-08.

### [HIGH] Global Mutable State (AP-07)
File: src/utils.js:9-10 (`globalCache`, `totalRevenue`), used at AppManager.js:59
Description: Module-level mutable `globalCache` and `totalRevenue` are shared process-wide and mutated from request handling.
Impact: Hidden coupling, state leaks across requests, not safe under concurrency, untestable.
Recommendation: Encapsulate as an injected cache service with instance state. See playbook T-03.

### [HIGH] Business logic & callback hell in the route handler (AP-06)
File: src/AppManager.js:28-78
Description: The `/api/checkout` handler nests user lookup → create → payment → enrollment → payment record → audit → cache in deeply chained callbacks, mixing routing, business rules and persistence.
Impact: Unreadable, error-prone (error handling duplicated/inconsistent), impossible to unit-test the checkout flow.
Recommendation: Extract a CheckoutService (promisified repositories); controller only orchestrates. See playbook T-04.

### [HIGH] Sensitive data written to logs (AP-06/AP-01)
File: src/AppManager.js:45
Description: `console.log("Processando cartão ${cc} na chave ${config.paymentGatewayKey}")` logs the full card number and the payment gateway key.
Impact: PCI-sensitive card data and a secret key leak into logs.
Recommendation: Never log card/secret; mask PAN, drop the key from logs; use a structured logger. See playbook T-10.

### [MEDIUM] N+1 queries in the financial report (AP-10)
File: src/AppManager.js:80-129
Description: For each course it queries enrollments, then per enrollment queries the user and the payment — nested per-row queries with manual counters.
Impact: O(courses × enrollments) round-trips; degrades sharply with data; fragile counting logic.
Recommendation: Single JOIN over courses+enrollments+users+payments, aggregate in memory. See playbook T-06.

### [MEDIUM] Missing / weak validation (AP-11)
File: src/AppManager.js:35 (password not required), :46 (card validated only by first digit), :68 (password defaulted to "123456")
Description: Checkout accepts a missing password (defaults to "123456"), and "payment" is decided by `cc.startsWith("4")` with no real validation.
Impact: Weak/guessable credentials created silently; no input integrity.
Recommendation: Validate all inputs in a validator/service; never invent default passwords. See playbook T-07.

### [MEDIUM] Delete without referential integrity (AP-11)
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` removes the user but leaves enrollments and payments orphaned — the handler literally admits it in the response text.
Impact: Orphaned rows, inconsistent data, broken reports.
Recommendation: Cascade or block deletion when dependents exist, within a service/transaction. See playbook T-04.

### [LOW] Poor variable naming (AP-16)
File: src/AppManager.js:29-33
Description: Cryptic identifiers `u`, `e`, `p`, `cid`, `cc` for user/email/password/course id/card.
Impact: Hard to read and reason about.
Recommendation: Use descriptive names. See playbook T-10.

### [LOW] console.log as logging (AP-14)
File: src/utils.js:13, src/AppManager.js:45, :59
Description: Operational logging via `console.log` with no levels/structure.
Impact: Noisy, unstructured, not configurable per environment.
Recommendation: Use a logger abstraction. See playbook T-10.

================================
Total: 11 findings
================================
