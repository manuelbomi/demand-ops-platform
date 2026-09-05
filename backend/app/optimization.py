"""Forecast-driven staffing optimization service used by the
/staffing-plan API endpoint.

Takes a forecasted daily parcel volume, converts it to an hourly headcount
requirement using a fixed intraday workload shape and processing rate, then
solves a small shift-scheduling set-covering MILP (same formulation as the
dedicated `workforce-capacity-optimization` repo in this portfolio) to
decide how many workers to schedule per shift, per day, at minimum cost.
This is the "forecast becomes an optimization input" pipeline stitched
into one live service.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pyomo.environ as pyo

OPERATING_HOURS = list(range(6, 22))
PARCELS_PER_WORKER_HOUR = 55


@dataclass(frozen=True)
class ShiftPattern:
    pattern_id: str
    start_hour: int
    duration_hours: int
    hourly_cost: float

    @property
    def hours_covered(self) -> list[int]:
        return list(range(self.start_hour, self.start_hour + self.duration_hours))

    @property
    def shift_cost(self) -> float:
        return self.hourly_cost * self.duration_hours


SHIFT_PATTERNS = [
    ShiftPattern("FT-06", 6, 8, 24.50),
    ShiftPattern("FT-10", 10, 8, 24.50),
    ShiftPattern("FT-14", 14, 8, 24.50),
    ShiftPattern("PT-08", 8, 4, 27.00),
    ShiftPattern("PT-16", 16, 4, 27.00),
]


def _hourly_shape(hour: int) -> float:
    morning_peak = np.exp(-((hour - 10) ** 2) / (2 * 2.2 ** 2))
    evening_peak = np.exp(-((hour - 18) ** 2) / (2 * 1.8 ** 2)) * 1.15
    return 0.15 + morning_peak + evening_peak


def daily_volume_to_hourly_requirements(forecast_df: pd.DataFrame) -> pd.DataFrame:
    shape = np.array([_hourly_shape(h) for h in OPERATING_HOURS])
    shape = shape / shape.sum()

    rows = []
    for row in forecast_df.itertuples():
        hourly_volume = row.forecast * shape
        for hour, volume in zip(OPERATING_HOURS, hourly_volume):
            rows.append(
                {
                    "date": row.date,
                    "hour": hour,
                    "required_workers": int(np.ceil(volume / PARCELS_PER_WORKER_HOUR)),
                }
            )
    return pd.DataFrame(rows)


def solve_staffing_plan(requirements: pd.DataFrame) -> dict:
    days = list(requirements["date"].unique())
    pattern_lookup = {p.pattern_id: p for p in SHIFT_PATTERNS}
    req_lookup = {(row.date, row.hour): row.required_workers for row in requirements.itertuples()}

    model = pyo.ConcreteModel()
    model.DAYS = pyo.Set(initialize=days)
    model.PATTERNS = pyo.Set(initialize=list(pattern_lookup.keys()))
    model.x = pyo.Var(model.PATTERNS, model.DAYS, domain=pyo.NonNegativeIntegers, bounds=(0, 30))

    model.total_cost = pyo.Objective(
        expr=sum(pattern_lookup[p].shift_cost * model.x[p, d] for p in model.PATTERNS for d in model.DAYS),
        sense=pyo.minimize,
    )

    def coverage_rule(m, d, h):
        covering = [p for p in m.PATTERNS if h in pattern_lookup[p].hours_covered]
        return sum(m.x[p, d] for p in covering) >= req_lookup.get((d, h), 0)

    model.coverage = pyo.Constraint(
        [(d, h) for d in days for h in OPERATING_HOURS], rule=coverage_rule
    )

    solver = pyo.SolverFactory("appsi_highs")
    results = solver.solve(model, tee=False)

    schedule = []
    for p in pattern_lookup:
        for d in days:
            count = round(pyo.value(model.x[p, d]))
            if count > 0:
                schedule.append(
                    {
                        "date": str(pd.Timestamp(d).date()),
                        "pattern_id": p,
                        "start_hour": pattern_lookup[p].start_hour,
                        "duration_hours": pattern_lookup[p].duration_hours,
                        "workers_assigned": count,
                        "shift_cost": pattern_lookup[p].shift_cost * count,
                    }
                )

    return {
        "status": str(results.solver.termination_condition),
        "total_cost": round(pyo.value(model.total_cost), 2),
        "schedule": schedule,
    }
