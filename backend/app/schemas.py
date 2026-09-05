from __future__ import annotations

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    date: str
    forecast: float
    lower_80: float
    upper_80: float


class ForecastResponse(BaseModel):
    history_days_used: int
    horizon_days: int
    points: list[ForecastPoint]


class ShiftAssignment(BaseModel):
    date: str
    pattern_id: str
    start_hour: int
    duration_hours: int
    workers_assigned: int
    shift_cost: float


class StaffingPlanResponse(BaseModel):
    status: str
    total_cost: float
    horizon_days: int
    schedule: list[ShiftAssignment]
