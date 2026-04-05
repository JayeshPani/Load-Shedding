"""
test_all_data.py
Rajveer — data branch

Smoke test — run this before every push to the data branch:
    python test_all_data.py

Calls all 4 data functions and pretty-prints their output.
Does NOT test Gemini, WhatsApp, or the database — those belong to other branches.
"""

import json
import sys


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_shape(result, expected_keys: list, name: str) -> bool:
    """Basic shape validation — checks keys exist on first element."""
    if not isinstance(result, (list, dict)):
        print(f"  ✗ {name}: expected list or dict, got {type(result).__name__}")
        return False
    sample = result[0] if isinstance(result, list) else result
    missing = [k for k in expected_keys if k not in sample]
    if missing:
        print(f"  ✗ {name}: missing keys {missing}")
        return False
    print(f"  ✓ {name}: shape OK")
    return True


def main() -> int:
    errors = 0

    # ── 1. SimulatedInverter ───────────────────────────────────────────────────
    section("1 / 4  —  simulators/inverter.py  →  SimulatedInverter().get_snapshot()")
    try:
        from simulators.inverter import SimulatedInverter
        snapshot = SimulatedInverter().get_snapshot()
        print(json.dumps(snapshot, indent=2))
        ok = check_shape(snapshot, ["battery_pct", "solar_watts", "grid_on"], "get_snapshot()")
        if not ok:
            errors += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        errors += 1

    # ── 2. SimulatedHousehold ─────────────────────────────────────────────────
    section("2 / 4  —  simulators/household.py  →  SimulatedHousehold().get_appliances()")
    try:
        from simulators.household import SimulatedHousehold
        hh = SimulatedHousehold()
        appliances = hh.get_appliances()
        rules = hh.get_rules()
        print("Appliances:")
        print(json.dumps(appliances, indent=2))
        print("\nRules:")
        print(json.dumps(rules, indent=2))
        ok = check_shape(appliances, ["name", "watts", "priority", "deadline", "flexible"], "get_appliances()")
        if not ok:
            errors += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        errors += 1

    # ── 3. EskomSePush ────────────────────────────────────────────────────────
    section("3 / 4  —  integrations/eskomsepush.py  →  get_schedule()")
    try:
        from integrations.eskomsepush import get_schedule
        schedule = get_schedule()
        print(json.dumps(schedule, indent=2))
        if schedule:
            ok = check_shape(schedule, ["start", "end", "stage"], "get_schedule()")
            if not ok:
                errors += 1
        else:
            print("  ℹ  Empty list returned (no outages today, or API key missing — check .env)")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        errors += 1

    # ── 4. Open-Meteo ─────────────────────────────────────────────────────────
    section("4 / 4  —  integrations/openmeteo.py  →  get_solar_forecast()")
    try:
        from integrations.openmeteo import get_solar_forecast
        forecast = get_solar_forecast()
        # Show only the solar window (6 AM – 6 PM) to keep output readable
        solar_window = [f for f in forecast if "06:00" <= f["hour"] <= "18:00"]
        print("Solar window (06:00 – 18:00):")
        print(json.dumps(solar_window, indent=2))
        ok = check_shape(forecast, ["hour", "kwh"], "get_solar_forecast()")
        if not ok:
            errors += 1
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        errors += 1

    # ── Summary ───────────────────────────────────────────────────────────────
    section("RESULT")
    if errors == 0:
        print("  ✅  All 4 data functions passed — safe to push to data branch.")
    else:
        print(f"  ❌  {errors} function(s) failed — fix before pushing.")
    print()
    return errors


if __name__ == "__main__":
    sys.exit(main())
