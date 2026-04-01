# Backend Week 1 Contract Lock-In

This document is the Week 1 handoff for Jayesh's `backend` branch. It freezes the
contracts and backend decisions needed before Week 5 implementation starts.

## Source of Truth

- Cross-branch data shapes and runtime constants: `shared/contracts.py`
- Backend-owned storage contract: `db/models.py`
- Backend-owned assembly contract: `api/main.py`

## Locked Function Signatures

```python
get_schedule() -> list[dict]
get_solar_forecast() -> list[dict]
SimulatedInverter().get_snapshot() -> dict
SimulatedHousehold().get_appliances() -> list[dict]
generate_plan(outage, solar, inverter, household) -> str
handle_reply(user_message, current_plan) -> str
send_message(to, body) -> None
save_plan(plan_text, data) -> None
get_latest_plan() -> DailyPlanSchema | None
```

## Frozen Data Shapes

```python
outage = [{"start": "10:00", "end": "12:00", "stage": 3}]
solar = [{"hour": "06:00", "kwh": 0.0}, {"hour": "12:00", "kwh": 1.8}]
inverter = {"battery_pct": 78, "solar_watts": 0, "grid_on": True}
household = [
    {
        "name": "Geyser",
        "watts": 3000,
        "priority": 1,
        "deadline": "08:00",
        "flexible": False,
    }
]
```

Do not change these keys or return types without changing every branch that consumes
them.

## Backend Assembly Flow

1. Startup loads environment variables and initializes the database.
2. APScheduler runs `run_daily_job()` at `06:00` in `Africa/Johannesburg`.
3. `GET /run-now` will call the same pipeline manually for demos.
4. `POST /webhook` will accept Twilio inbound messages.
5. `run_daily_job()` will execute this order:
   - `get_schedule()`
   - `get_solar_forecast()`
   - `SimulatedInverter().get_snapshot()`
   - `SimulatedHousehold().get_appliances()`
   - `generate_plan(outage, solar, inverter, household)`
   - `save_plan(plan_text, data)`
   - `send_message(to, body)`

## Database Decision for Week 5

- SQLite URL: `sqlite:///./smart_scheduler.db`
- Table name: `DailyPlan`
- Fields:
  - `id`
  - `date`
  - `area`
  - `outage_data`
  - `solar_data`
  - `plan_text`
  - `created_at`

`outage_data` and `solar_data` are stored as JSON strings.

## Deployment Decisions

- Railway start command:
  - `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Required environment variables:
  - `ESKOMSEPUSH_KEY`
  - `GEMINI_KEY`
  - `TWILIO_SID`
  - `TWILIO_TOKEN`
  - `TWILIO_FROM`
- Twilio webhook target:
  - `https://<railway-app>/webhook`

## Explicitly Deferred Until Week 5

- Full SQLAlchemy implementation
- FastAPI app construction
- APScheduler wiring
- Twilio request parsing
- Persistence logic
- End-to-end pipeline execution

