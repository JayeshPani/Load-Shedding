"""
simulators/household.py
Rajveer — data branch

Simulates a standard South African household's appliance profile.
Appliance data is hardcoded to realistic values — no hardware required.

Returns data in the exact contract shape expected by agent/scheduler.py
"""


class SimulatedHousehold:
    """
    Represents a typical Cape Town household with 6 common appliances.

    Each appliance has:
        name     : display name
        watts    : power draw in watts
        priority : 1 (highest) → 5 (lowest) — Gemini uses this for scheduling
        deadline : latest time by which the task should be completed ("HH:MM")
        flexible : True  = can be shifted to any solar / cheap window
                   False = must run at a fixed time (e.g. geyser by 8 AM)
    """

    _APPLIANCES = [
        {
            "name": "Geyser",
            "watts": 3000,
            "priority": 1,
            "deadline": "08:00",
            "flexible": False,
        },
        {
            "name": "Washing Machine",
            "watts": 2000,
            "priority": 2,
            "deadline": "18:00",
            "flexible": True,
        },
        {
            "name": "Fridge",
            "watts": 150,
            "priority": 1,
            "deadline": "23:59",
            "flexible": False,   # must always be on
        },
        {
            "name": "Water Pump",
            "watts": 1500,
            "priority": 3,
            "deadline": "20:00",
            "flexible": True,
        },
        {
            "name": "Pool Pump",
            "watts": 1100,
            "priority": 4,
            "deadline": "17:00",
            "flexible": True,
        },
        {
            "name": "Microwave",
            "watts": 1200,
            "priority": 3,
            "deadline": "21:00",
            "flexible": True,
        },
    ]

    _RULES = {
        "min_battery_reserve": 30,   # % — Gemini must never drop battery below this
        "area": "Cape Town Zone 3",
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_appliances(self) -> list[dict]:
        """
        Returns the household appliance list.

        Shape (must not change — contract with agent/scheduler.py):
            [
                {
                    "name":     str,
                    "watts":    int,
                    "priority": int,   # 1 = most important
                    "deadline": str,   # "HH:MM"
                    "flexible": bool
                },
                ...
            ]
        """
        return list(self._APPLIANCES)   # return a copy so callers can't mutate state

    def get_rules(self) -> dict:
        """
        Returns household configuration / constraints.

        Shape:
            {
                "min_battery_reserve": int,   # e.g. 30
                "area":                str    # e.g. "Cape Town Zone 3"
            }
        """
        return dict(self._RULES)
