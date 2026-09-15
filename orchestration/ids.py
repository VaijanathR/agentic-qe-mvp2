"""Stable orchestration/decision ID generation.

`ORCH-YYYYMMDD-HHMMSS-XXXX` per the governing instruction sec. 38.
`XXXX` is a monotonically-incrementing, in-process counter combined with
a short random suffix so two IDs generated within the same wall-clock
second (a real possibility on a fast machine) never collide -- deterministic
enough to read, unique enough to trust as a primary key.
"""
from __future__ import annotations

import datetime
import itertools
import random
import string

_counter = itertools.count(1)


def _suffix() -> str:
    n = next(_counter) % 10000
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
    return f"{n:04d}{rand}"


def new_orchestration_id(now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return f"ORCH-{now.strftime('%Y%m%d-%H%M%S')}-{_suffix()}"


def new_decision_id(orchestration_id: str, stage: str, now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return f"DEC-{orchestration_id}-{stage}-{now.strftime('%H%M%S')}-{_suffix()}"


def new_approval_id(orchestration_id: str, now: datetime.datetime | None = None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return f"APPR-{orchestration_id}-{now.strftime('%H%M%S')}-{_suffix()}"
