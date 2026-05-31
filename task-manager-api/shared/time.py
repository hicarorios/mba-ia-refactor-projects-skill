"""Time helpers.

`now_utc()` replaces the deprecated `datetime.utcnow()` (removed-track in
Python 3.12+) while preserving the previous behavior: a *naive* UTC timestamp.
Keeping it naive matters because the stored due_date/created_at columns are
naive, so comparisons stay naive-vs-naive and never raise.
"""
from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)
