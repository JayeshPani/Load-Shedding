"""Week 1 backend assembly contract.

The FastAPI app, scheduler, and webhook handling are intentionally deferred until
Week 5. This file freezes the route paths, timezone, and pipeline order so the team
can build the other branches against a stable backend contract.
"""

from __future__ import annotations

from typing import Final

from shared.contracts import (
    BACKEND_ASSEMBLY_FLOW,
    DAILY_JOB_HOUR,
    DAILY_JOB_MINUTE,
    RUN_NOW_PATH,
    SCHEDULER_TIMEZONE,
    WEBHOOK_PATH,
)

ASSEMBLY_STATUS: Final[str] = "Week 1 contract locked; FastAPI + APScheduler implementation deferred to Week 5."
MANUAL_TRIGGER_PATH: Final[str] = RUN_NOW_PATH
WHATSAPP_WEBHOOK_PATH: Final[str] = WEBHOOK_PATH
SCHEDULE_PLAN: Final[str] = f"{DAILY_JOB_HOUR:02d}:{DAILY_JOB_MINUTE:02d} {SCHEDULER_TIMEZONE}"
DOCUMENTED_PIPELINE: Final[tuple[str, ...]] = BACKEND_ASSEMBLY_FLOW


def run_daily_job() -> None:
    """Execute the documented pipeline once the Week 5 backend is assembled."""

    raise NotImplementedError("Week 5 task: implement the scheduled pipeline in FastAPI.")
