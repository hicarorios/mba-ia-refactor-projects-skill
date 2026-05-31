================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (Flask-SQLAlchemy ORM)
Files:   14 analyzed | ~1158 lines of code

## Summary
CRITICAL: 1 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secret (AP-01)
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` is hardcoded in source.
Impact: The session-signing secret cannot be rotated per environment and is exposed to anyone with repo access.
Recommendation: Read SECRET_KEY from an env-based config module with `.env.example`. See playbook T-01.

### [HIGH] Insecure password hashing — MD5 (AP-05)
File: models/user.py:27-32
Description: `set_password`/`check_password` use `hashlib.md5(...)` with no salt.
Impact: MD5 is fast and broken; a DB leak makes passwords trivially recoverable.
Recommendation: Use werkzeug `generate_password_hash`/`check_password_hash` and re-seed users. See playbook T-08.

### [HIGH] Password exposed in API responses (AP-05)
File: models/user.py:16-25 (`to_dict` includes `password`); consumed by routes/user_routes.py:33,85,209 and routes/task_routes via user
Description: `User.to_dict()` returns the password hash; it is sent by GET /users/<id>, POST /users and /login.
Impact: Credential material leaks to any API consumer.
Recommendation: Remove `password` from `to_dict()`; never serialize it. See playbook T-08.

### [HIGH] Hardcoded SMTP credentials (AP-01)
File: services/notification_service.py:7-10
Description: SMTP host/user/password (`taskmanager@gmail.com` / `senha123`) are hardcoded in the service.
Impact: Email credentials exposed in source; cannot vary per environment.
Recommendation: Move to env-based config. See playbook T-01.

### [HIGH] Business logic in routes — no controller/service layer (AP-06)
File: routes/task_routes.py (whole), routes/user_routes.py (whole), routes/report_routes.py (whole)
Description: Route handlers perform validation, persistence, derived calculations and report assembly directly; there are folders for models/routes/services but no controllers and the service layer is unused by the routes.
Impact: Logic cannot be reused/tested without HTTP; handlers are long and tangled.
Recommendation: Add controllers (orchestration) + services (business rules); routes only route. See playbook T-03, T-04.

### [MEDIUM] Duplicated "overdue"/stats logic — model method unused (AP-11)
File: routes/task_routes.py:30-39, 71-80, 283-287; routes/user_routes.py:171-180; routes/report_routes.py:33-43, 132-135
Description: The same "is the task overdue" computation is re-implemented in 6 places while `Task.is_overdue()` already exists and is never called.
Impact: Drift risk; a rule change must be made in many spots.
Recommendation: Use/extend `Task.is_overdue()`; centralize stats in a service. See playbook T-07.

### [MEDIUM] Generic exception swallowing (AP-12)
File: routes/task_routes.py:62-63, 236-237; routes/user_routes.py:130-132, 149-151; routes/report_routes.py:186-188, 207-209, 221-223
Description: Bare `except:` / `except Exception` blocks return a generic 500 and hide the real error; no centralized handler.
Impact: Real failures masked; debugging is hard; inconsistent error responses.
Recommendation: Centralized error handler + typed errors. See playbook T-05.

### [MEDIUM] Deprecated API — datetime.utcnow() (AP-13)
File: models/user.py:14, models/task.py:15-16,52, routes/task_routes.py:31,72,285, routes/user_routes.py:172, routes/report_routes.py:35,42,45,71, utils/helpers.py:38
Description: `datetime.utcnow()` is deprecated as of Python 3.12 (the runtime here is 3.12) and returns a naive datetime.
Impact: Deprecation warnings now; removal in a future Python; subtle tz-naive bugs.
Recommendation: Use `datetime.now(datetime.UTC)`. See playbook T-11.

### [LOW] Unused imports (AP-17)
File: app.py:7 (`os, sys, json`), routes/task_routes.py:7 (`json, os, sys, time`), utils/helpers.py:3-7 (`os, json, sys, math, hashlib`)
Description: Several modules import names they never use.
Impact: Noise and false dependencies.
Recommendation: Remove unused imports. See playbook T-10.

### [LOW] Duplicated task serialization (AP-11/AP-17)
File: routes/task_routes.py:17-28, routes/user_routes.py:162-169
Description: The task→dict mapping is hand-rolled inline in routes instead of reusing `Task.to_dict()`.
Impact: Maintenance burden; shapes drift.
Recommendation: Reuse the model serializer. See playbook T-07.

### [LOW] Magic numbers / constants not reused (AP-15)
File: routes/task_routes.py:113,182 (priority 1..5), routes/report_routes.py:45 (7-day window), models/task.py:46
Description: Validation bounds and time windows are inline literals; `utils/helpers.py` defines constants (MIN/MAX_TITLE_LENGTH, VALID_STATUSES) that the routes ignore.
Impact: Intent hidden; changes scattered and error-prone.
Recommendation: Use named constants everywhere. See playbook T-10.

================================
Total: 11 findings
================================
