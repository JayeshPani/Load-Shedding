"""
integrations/openmeteo.py
Rajveer — data branch

Fetches today's hourly solar irradiance forecast from Open-Meteo.
No API key required — completely free.

Cape Town coordinates: latitude=-33.9249, longitude=18.4241
Conversion: shortwave_radiation (W/m²) × 0.0015 → estimated kWh/hour
"""

import requests
from datetime import date

# ── Configuration ──────────────────────────────────────────────────────────────
_BASE_URL  = "https://api.open-meteo.com/v1/forecast"
_LATITUDE  = -33.9249    # Cape Town
_LONGITUDE =  18.4241
_TIMEOUT   = 10          # seconds
_KWH_FACTOR = 0.0015     # converts W/m² → kWh/hour estimate


def get_solar_forecast() -> list[dict]:
    """
    Fetches today's hourly solar irradiance forecast and converts to kWh.

    Returns a list of 24 hourly entries:
        [{"hour": "00:00", "kwh": 0.0}, ..., {"hour": "12:00", "kwh": 1.8}, ...]

    Returns fallback data if the network request fails.

    Shape (must not change — contract with agent/scheduler.py):
        list[dict] with keys: "hour" (str "HH:MM"), "kwh" (float)
    """
    try:
        params = {
            "latitude":          _LATITUDE,
            "longitude":         _LONGITUDE,
            "hourly":            "shortwave_radiation",
            "timezone":          "Africa/Johannesburg",
            "forecast_days":     1,
        }
        response = requests.get(_BASE_URL, params=params, timeout=_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return _parse_forecast(data)

    except requests.exceptions.Timeout:
        print("[openmeteo] ERROR: Request timed out — returning fallback forecast.")
        return _fallback_forecast()

    except requests.exceptions.HTTPError as e:
        print(f"[openmeteo] ERROR: HTTP {e.response.status_code} — returning fallback.")
        return _fallback_forecast()

    except Exception as e:
        print(f"[openmeteo] ERROR: {e} — returning fallback forecast.")
        return _fallback_forecast()


# ── Private helpers ────────────────────────────────────────────────────────────

def _parse_forecast(data: dict) -> list[dict]:
    """
    Parses Open-Meteo JSON into the standard contract shape.

    API response structure:
        {
            "hourly": {
                "time":                 ["2024-04-05T00:00", "2024-04-05T01:00", ...],
                "shortwave_radiation":  [0.0, 0.0, 12.5, ..., 850.0, ...]
            }
        }
    """
    try:
        hourly     = data["hourly"]
        times      = hourly["time"]
        radiation  = hourly["shortwave_radiation"]
    except KeyError as e:
        print(f"[openmeteo] WARNING: Unexpected API response structure — missing key {e}")
        return _fallback_forecast()

    forecast = []
    for time_str, rad in zip(times, radiation):
        # time_str format: "2024-04-05T14:00"  →  extract "14:00"
        hour_label = time_str[11:16] if len(time_str) >= 16 else "00:00"
        kwh = round((rad or 0.0) * _KWH_FACTOR, 3)
        forecast.append({"hour": hour_label, "kwh": kwh})

    return forecast


def _fallback_forecast() -> list[dict]:
    """
    Returns a realistic Cape Town summer solar profile used when the API is unavailable.
    Covers all 24 hours; only hours 6–18 have meaningful solar output.
    """
    profile = {
        "00:00": 0.0, "01:00": 0.0, "02:00": 0.0, "03:00": 0.0,
        "04:00": 0.0, "05:00": 0.0, "06:00": 0.05,
        "07:00": 0.3, "08:00": 0.65, "09:00": 1.05,
        "10:00": 1.35, "11:00": 1.62, "12:00": 1.80,
        "13:00": 1.75, "14:00": 1.55, "15:00": 1.20,
        "16:00": 0.85, "17:00": 0.45, "18:00": 0.10,
        "19:00": 0.0, "20:00": 0.0, "21:00": 0.0,
        "22:00": 0.0, "23:00": 0.0,
    }
    return [{"hour": h, "kwh": v} for h, v in profile.items()]
