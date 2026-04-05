"""
simulators/inverter.py
Rajveer — data branch

Simulates a home solar inverter.
- solar_watts follows a bell curve: 0 at 6 AM → 1200 W peak at 12 PM → 0 at 6 PM
- battery_pct drains slightly when grid_on is False (load shedding active)
- Returns data in the exact contract shape expected by agent/scheduler.py
"""

import math
from datetime import datetime


class SimulatedInverter:
    """
    Simulates a household solar inverter + battery system.

    Default state (used when no real hardware is available):
      battery_pct : 78    — healthy charge level
      solar_watts : 0     — recalculated per current hour
      grid_on     : True  — assume grid is available unless overridden
    """

    # Bell curve parameters — peak at hour 12 (noon), spread ≈ 3 hours either side
    _PEAK_HOUR = 12          # noon
    _PEAK_WATTS = 1200       # maximum solar output (watts)
    _SIGMA = 2.5             # controls how wide the bell curve is (hours)

    # Battery drain rate when grid is off (% per hour, simulated)
    _DRAIN_RATE = 0.8        # 0.8 % per hour under typical load during outage

    def __init__(self, battery_pct: float = 78, grid_on: bool = True):
        """
        Args:
            battery_pct: Starting battery percentage (0–100).
            grid_on:     Whether the grid is currently live.
        """
        self._battery_pct = float(battery_pct)
        self._grid_on = grid_on

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_snapshot(self) -> dict:
        """
        Returns the current inverter state as a dict.

        Shape (must not change — contract with agent/scheduler.py):
            {
                "battery_pct": float,   # e.g. 78
                "solar_watts": float,   # e.g. 0 at night, up to 1200 at noon
                "grid_on":     bool     # True if grid is live
            }
        """
        current_hour = datetime.now().hour + datetime.now().minute / 60.0
        solar = self._bell_curve_watts(current_hour)
        battery = self._current_battery(current_hour)

        return {
            "battery_pct": round(battery, 1),
            "solar_watts": round(solar, 1),
            "grid_on": self._grid_on,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _bell_curve_watts(self, hour: float) -> float:
        """
        Gaussian bell curve centred on PEAK_HOUR.
        Only produces power between 6 AM and 6 PM (solar window).
        """
        if hour < 6 or hour > 18:
            return 0.0
        return self._PEAK_WATTS * math.exp(
            -((hour - self._PEAK_HOUR) ** 2) / (2 * self._SIGMA ** 2)
        )

    def _current_battery(self, hour: float) -> float:
        """
        Simulates battery drain during load shedding hours.
        Assumes the inverter has been running since midnight.
        Battery cannot go below 0 or above 100.
        """
        if self._grid_on:
            # Grid is on — battery stays at its initialised level
            return max(0.0, min(100.0, self._battery_pct))
        else:
            # Grid is off — drain proportionally to how long outage has run
            # (simplified: assume outage started at current hour for demo)
            drained = self._DRAIN_RATE * max(0, hour - 6)
            return max(0.0, min(100.0, self._battery_pct - drained))
