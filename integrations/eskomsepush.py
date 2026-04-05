"""
integrations/eskomsepush.py
Rajveer — data branch

Fetches the real load shedding schedule for Cape Town from the EskomSePush API.
API key must be set in the .env file as ESKOMSEPUSH_KEY.

Key rules:
  - API key goes in the REQUEST HEADERS (not query params)
  - If the API call fails for any reason → return [] (never crash the pipeline)
  - Area ID for Cape Town Zone 3: "capetown-3-capetown" (see note below)

EskomSePush docs: https://documenter.getpostman.com/view/1296288/UzQuNk3E
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
_API_KEY   = os.getenv("ESKOMSEPUSH_KEY", "")
_BASE_URL  = "https://developer.sepush.co.za/business/2.0"
_AREA_ID   = "capetown-3-capetown"   # Cape Town Zone 3
_TIMEOUT   = 10                      # seconds


def get_schedule() -> list[dict]:
    """
    Fetches today's load shedding schedule from the EskomSePush API.

    Returns a list of outage windows for today, e.g.:
        [{"start": "10:00", "end": "12:00", "stage": 3}]

    Returns [] if:
      - The API key is missing / invalid
      - The network request fails
      - The API returns an unexpected payload

    Shape (must not change — contract with agent/scheduler.py):
        list[dict] with keys: "start" (str), "end" (str), "stage" (int)
    """
    if not _API_KEY:
        print("[eskomsepush] WARNING: ESKOMSEPUSH_KEY not set — returning fallback schedule.")
        return _fallback_schedule()

    try:
        response = requests.get(
            f"{_BASE_URL}/area",
            headers={"token": _API_KEY},
            params={"id": _AREA_ID, "test": "current"},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return _parse_schedule(data)

    except requests.exceptions.Timeout:
        print("[eskomsepush] ERROR: Request timed out — returning fallback schedule.")
        return _fallback_schedule()

    except requests.exceptions.HTTPError as e:
        print(f"[eskomsepush] ERROR: HTTP {e.response.status_code} — returning fallback.")
        return _fallback_schedule()

    except Exception as e:
        print(f"[eskomsepush] ERROR: {e} — returning fallback schedule.")
        return _fallback_schedule()


# ── Private helpers ────────────────────────────────────────────────────────────

def _parse_schedule(data: dict) -> list[dict]:
    """
    Parses the EskomSePush API response into the standard contract shape.

    The API returns "events" — each event contains:
        note  : e.g. "Stage 3"
        start : ISO 8601 datetime  e.g. "2024-04-05T10:00:00+02:00"
        end   : ISO 8601 datetime  e.g. "2024-04-05T12:00:00+02:00"
    """
    outages = []

    events = data.get("events", [])
    if not events:
        print("[eskomsepush] No outage events found for today — grid is clear.")
        return []

    for event in events:
        try:
            # Extract HH:MM from ISO datetime string (positions 11–16)
            start_str = event.get("start", "")
            end_str   = event.get("end",   "")
            note      = event.get("note",  "Stage 0")

            start_time = start_str[11:16] if len(start_str) >= 16 else "00:00"
            end_time   = end_str[11:16]   if len(end_str)   >= 16 else "00:00"

            # Parse stage number from note like "Stage 3"
            stage = int(note.split()[-1]) if note.startswith("Stage") else 0

            outages.append({
                "start": start_time,
                "end":   end_time,
                "stage": stage,
            })
        except (ValueError, IndexError, KeyError) as e:
            print(f"[eskomsepush] WARNING: Could not parse event {event}: {e}")
            continue

    return outages


def _fallback_schedule() -> list[dict]:
    """
    Returns a hardcoded realistic outage schedule used when the API is unavailable.
    Gemini will still produce a plan — it just won't be the real schedule for today.
    """
    return [
        {"start": "10:00", "end": "12:00", "stage": 3},
        {"start": "18:00", "end": "20:00", "stage": 3},
    ]
