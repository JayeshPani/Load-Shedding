"""Week 1 source-of-truth contracts for backend, data, and AI branches."""

from __future__ import annotations

from typing import Final, Literal, TypeAlias, TypedDict

DATABASE_URL: Final[str] = "sqlite:///./smart_scheduler.db"
DEFAULT_AREA: Final[str] = "Cape Town"
SCHEDULER_TIMEZONE: Final[str] = "Africa/Johannesburg"
DAILY_JOB_HOUR: Final[int] = 6
DAILY_JOB_MINUTE: Final[int] = 0
RUN_NOW_PATH: Final[str] = "/run-now"
WEBHOOK_PATH: Final[str] = "/webhook"
RAILWAY_START_COMMAND: Final[str] = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"

REQUIRED_ENV_VARS: Final[tuple[str, ...]] = (
    "ESKOMSEPUSH_KEY",
    "GEMINI_KEY",
    "TWILIO_SID",
    "TWILIO_TOKEN",
    "TWILIO_FROM",
)


class OutageWindow(TypedDict):
    start: str
    end: str
    stage: int


class SolarForecastPoint(TypedDict):
    hour: str
    kwh: float


class InverterSnapshot(TypedDict):
    battery_pct: int
    solar_watts: int
    grid_on: bool


class HouseholdAppliance(TypedDict):
    name: str
    watts: int
    priority: int
    deadline: str
    flexible: bool


OutageSchedule: TypeAlias = list[OutageWindow]
SolarForecast: TypeAlias = list[SolarForecastPoint]
HouseholdProfile: TypeAlias = list[HouseholdAppliance]


class StoredPlanData(TypedDict, total=False):
    date: str
    area: str
    outage_data: OutageSchedule
    solar_data: SolarForecast


DailyPlanField: TypeAlias = Literal[
    "id",
    "date",
    "area",
    "outage_data",
    "solar_data",
    "plan_text",
    "created_at",
]

DAILY_PLAN_FIELDS: Final[tuple[DailyPlanField, ...]] = (
    "id",
    "date",
    "area",
    "outage_data",
    "solar_data",
    "plan_text",
    "created_at",
)

BACKEND_ASSEMBLY_FLOW: Final[tuple[str, ...]] = (
    "startup -> init_db()",
    "06:00 Africa/Johannesburg -> APScheduler triggers run_daily_job()",
    "GET /run-now -> run_daily_job() for demos",
    "POST /webhook -> handle Twilio inbound reply",
    "run_daily_job() -> get_schedule()",
    "run_daily_job() -> get_solar_forecast()",
    "run_daily_job() -> SimulatedInverter().get_snapshot()",
    "run_daily_job() -> SimulatedHousehold().get_appliances()",
    "run_daily_job() -> generate_plan(outage, solar, inverter, household)",
    "run_daily_job() -> save_plan(plan_text, data)",
    "run_daily_job() -> send_message(to, body)",
)

