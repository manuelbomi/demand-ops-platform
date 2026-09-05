"""Synthetic daily parcel-volume history for a single distribution center,
used to drive both the forecasting and staffing-optimization endpoints in
this demo platform. Same generative approach (trend + weekly/annual
seasonality + holiday effects + noise) as the dedicated
`parcel-volume-forecasting` repo in this portfolio, trimmed to a single
facility since this repo's focus is the end-to-end service + UI, not the
forecasting methodology itself.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG_SEED = 3
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
BASE_VOLUME = 19_000


def _weekly_seasonality(dow: int) -> float:
    factors = [1.12, 1.15, 1.08, 1.05, 1.00, 0.75, 0.55]
    return factors[dow]


def _annual_seasonality(day_of_year: int, year_len: int) -> float:
    phase = (day_of_year / year_len) * 2 * np.pi
    peak_season = 0.22 * np.sin(phase - 1.55) ** 5
    base_wave = 0.08 * np.sin(phase - 1.2)
    return 1.0 + base_wave + peak_season


def generate(seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    years_elapsed = (dates - dates[0]).days / 365.25
    growth = 1.06 ** years_elapsed

    dow_factor = np.array([_weekly_seasonality(d.weekday()) for d in dates])
    annual_factor = np.array(
        [_annual_seasonality(d.dayofyear, 366 if d.is_leap_year else 365) for d in dates]
    )
    noise = rng.normal(1.0, 0.045, size=len(dates))

    volume = BASE_VOLUME * growth * dow_factor * annual_factor * noise
    volume = np.clip(volume, 200, None).round().astype(int)

    return pd.DataFrame({"date": dates, "parcel_volume": volume})


if __name__ == "__main__":
    df = generate()
    df.to_csv("data/daily_volume.csv", index=False)
    print(f"Wrote {len(df)} rows to data/daily_volume.csv")
