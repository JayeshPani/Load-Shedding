# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
uvicorn api.main:app --reload

# Run in production (Railway start command)
uvicorn api.main:app --host 0.0.0.0 --port $PORT

# Test individual modules from the Python shell
python -c 'from simulators.inverter import SimulatedInverter; print(SimulatedInverter().get_snapshot())'
python -c 'from simulators.household import SimulatedHousehold; print(SimulatedHousehold().get_appliances())'
python -c 'from integrations.eskomsepush import get_schedule; print(get_schedule())'
python -c 'from integrations.openmeteo import get_solar_forecast; print(get_solar_forecast())'

# Trigger the full pipeline manually (for demos — requires the server to be running)
# GET /run-now
```

## Architecture

The system is a **daily automated pipeline** triggered at 6 AM by APScheduler inside the FastAPI process. There is no user-facing web UI — the interface is WhatsApp.

### Pipeline execution order (runs every day at 6 AM)

```
APScheduler → run_daily_job() in api/main.py
    1. integrations/eskomsepush.py  → get_schedule()
    2. integrations/openmeteo.py    → get_solar_forecast()
    3. simulators/inverter.py       → SimulatedInverter().get_snapshot()
    4. simulators/household.py      → SimulatedHousehold().get_appliances()
    5. agent/scheduler.py           → generate_plan(outage, solar, inverter, household)
    6. db/models.py                 → save_plan(plan_text, data)
    7. integrations/whatsapp.py     → send_message(phone, plan_text)
```

### Inbound WhatsApp replies

```
Twilio → POST /webhook (api/main.py)
    → integrations/whatsapp.py → handle_webhook(request)
    → agent/scheduler.py       → handle_reply(user_message, current_plan)
    → integrations/whatsapp.py → send_message(phone, response)
```

### Module ownership (team branches)

| Branch    | Owner    | Files                                                                 |
|-----------|----------|-----------------------------------------------------------------------|
| `backend` | Jayesh   | `api/main.py`, `db/models.py`, Railway deployment                     |
| `data`    | Rajveer  | `simulators/inverter.py`, `simulators/household.py`, `integrations/eskomsepush.py`, `integrations/openmeteo.py` |
| `ai`      | Harshita | `agent/scheduler.py`, `integrations/whatsapp.py`                      |

Jayesh merges all branches into `main` during Week 5.

## Data Format Contract

All modules must produce and consume data in this exact shape — mismatches here are the #1 source of integration bugs:

```python
# integrations/eskomsepush.py → get_schedule()
outage = [{"start": "10:00", "end": "12:00", "stage": 3}]

# integrations/openmeteo.py → get_solar_forecast()
solar = [{"hour": "06:00", "kwh": 0.0}, {"hour": "12:00", "kwh": 1.8}]

# simulators/inverter.py → SimulatedInverter().get_snapshot()
inverter = {"battery_pct": 78, "solar_watts": 0, "grid_on": True}

# simulators/household.py → SimulatedHousehold().get_appliances()
household = [{"name": "Geyser", "watts": 3000, "priority": 1, "deadline": "08:00", "flexible": False}]
```

Function signatures that must not change:
- `generate_plan(outage, solar, inverter, household)` → returns `str`
- `handle_reply(user_message, current_plan)` → returns `str`
- `send_message(to, body)` → sends WhatsApp message
- `save_plan(plan_text, data)` → writes to SQLite
- `get_latest_plan()` → returns today's plan from SQLite

## Key Implementation Details

**SimulatedInverter**: `solar_watts` follows a bell curve — 0 at 6 AM, peaks at 1200W at noon, 0 by 6 PM. Battery drains slightly when `grid_on` is False.

**Open-Meteo**: No API key required. Cape Town coords: `latitude=-33.9249, longitude=18.4241`. Multiply `shortwave_radiation` values by `0.0015` to get estimated kWh/hour.

**EskomSePush**: API key goes in header, not query params. Endpoint: `https://developer.sepush.co.za/business/2.0/area`. If the API fails, return an empty list — never crash the pipeline.

**Gemini prompt**: Must include all 4 data inputs, the 30% minimum battery reserve rule, priority order, and end with: `"Format this as a friendly WhatsApp message under 500 characters"`.

**APScheduler**: Started via FastAPI lifespan event. Cron: `hour=6, minute=0`. The `/run-now` GET endpoint bypasses the schedule for demos.

**SQLite `DailyPlan` model fields**: `id`, `date`, `area`, `outage_data` (JSON string), `solar_data` (JSON string), `plan_text`, `created_at`.

## Environment Variables

```
ESKOMSEPUSH_KEY=     # from eskomsepush.com
GEMINI_KEY=          # from aistudio.google.com
TWILIO_SID=          # from twilio.com console
TWILIO_TOKEN=        # from twilio.com console
TWILIO_FROM=         # whatsapp:+14155238886 (Twilio Sandbox number)
```

`.env` is never committed. `.gitignore` must include: `.env venv/ __pycache__/ *.pyc *.db .DS_Store`

## Git Workflow

- Three long-lived branches: `backend`, `data`, `ai` — each person works only on their own branch
- Never push directly to `main`
- Jayesh merges everything into `main` in Week 5
- `test_all_data.py` (Rajveer creates this) — calls all 4 data functions and prints formatted output; run before every push
