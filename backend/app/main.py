"""FastAPI service wiring together the forecasting and staffing-optimization
services behind a small REST API that the Next.js dashboard consumes.

    GET  /api/health
    GET  /api/forecast?horizon_days=14
    GET  /api/staffing-plan?horizon_days=14

This is the "productionize it" step referenced throughout this portfolio:
the same forecasting and optimization logic developed as scripts in
`parcel-volume-forecasting` and `workforce-capacity-optimization` becomes
a service that a frontend (or another internal system) can call on demand.
"""
from __future__ import annotations

import os
import sys

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .forecasting import forecast_volume
from .optimization import daily_volume_to_hourly_requirements, solve_staffing_plan
from .schemas import ForecastResponse, StaffingPlanResponse

BACKEND_ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_PATH = os.path.join(BACKEND_ROOT, "data", "daily_volume.csv")
sys.path.insert(0, BACKEND_ROOT)

app = FastAPI(title="Demand & Capacity Ops Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo only -- restrict to the dashboard's origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_history() -> pd.Series:
    if not os.path.exists(DATA_PATH):
        sys.path.insert(0, os.path.join(BACKEND_ROOT, "data"))
        import generate_data as gen

        df = gen.generate()
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        df.to_csv(DATA_PATH, index=False)

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df.set_index("date")["parcel_volume"].asfreq("D")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/forecast", response_model=ForecastResponse)
def get_forecast(horizon_days: int = 14):
    history = _load_history()
    forecast_df = forecast_volume(history, horizon_days)
    return {
        "history_days_used": len(history),
        "horizon_days": horizon_days,
        "points": [
            {
                "date": str(row.date.date()),
                "forecast": round(row.forecast, 1),
                "lower_80": round(row.lower_80, 1),
                "upper_80": round(row.upper_80, 1),
            }
            for row in forecast_df.itertuples()
        ],
    }


@app.get("/api/staffing-plan", response_model=StaffingPlanResponse)
def get_staffing_plan(horizon_days: int = 14):
    history = _load_history()
    forecast_df = forecast_volume(history, horizon_days)
    requirements = daily_volume_to_hourly_requirements(forecast_df)
    result = solve_staffing_plan(requirements)
    return {
        "status": result["status"],
        "total_cost": result["total_cost"],
        "horizon_days": horizon_days,
        "schedule": result["schedule"],
    }
