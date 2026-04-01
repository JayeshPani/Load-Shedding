"""Week 1 storage contract for the backend branch.

The real SQLAlchemy model and persistence logic are a Week 5 task. This file exists
now to freeze the schema, storage location, and backend-owned function names.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from shared.contracts import DAILY_PLAN_FIELDS, DATABASE_URL, DEFAULT_AREA, StoredPlanData

SCHEMA_STATUS: Final[str] = "Week 1 contract locked; SQLAlchemy implementation deferred to Week 5."
STORAGE_URL: Final[str] = DATABASE_URL
PLANNED_TABLE_FIELDS: Final[tuple[str, ...]] = DAILY_PLAN_FIELDS


@dataclass(frozen=True, slots=True)
class DailyPlanSchema:
    """Storage shape that the Week 5 SQLAlchemy model must match exactly."""

    id: int | None
    date: str
    area: str = DEFAULT_AREA
    outage_data: str = "[]"
    solar_data: str = "[]"
    plan_text: str = ""
    created_at: datetime | None = None


def save_plan(plan_text: str, data: StoredPlanData) -> None:
    """Persist one daily plan once the Week 5 database layer is implemented."""

    raise NotImplementedError("Week 5 task: implement SQLite persistence for DailyPlan.")


def get_latest_plan() -> DailyPlanSchema | None:
    """Return today's most recent plan once the Week 5 database layer is implemented."""

    raise NotImplementedError("Week 5 task: load today's latest DailyPlan from SQLite.")
