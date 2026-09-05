"""SARIMAX forecasting service used by the /forecast API endpoint.

A trimmed-down version of the modeling approach in the dedicated
`parcel-volume-forecasting` repo: a SARIMAX model with a weekly seasonal
order, refit on demand against whatever history is loaded. Kept small and
dependency-light (statsmodels only, no Prophet) since this repo's job is
to demonstrate the forecast -> optimize -> serve -> visualize pipeline,
not to re-litigate model selection.
"""
from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def forecast_volume(history: pd.Series, horizon_days: int) -> pd.DataFrame:
    model = SARIMAX(
        history,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)

    forecast_result = fitted.get_forecast(steps=horizon_days)
    mean = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int(alpha=0.2)  # 80% interval

    future_index = pd.date_range(history.index[-1] + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    return pd.DataFrame(
        {
            "date": future_index,
            "forecast": mean.to_numpy().clip(min=0),
            "lower_80": conf_int.iloc[:, 0].to_numpy().clip(min=0),
            "upper_80": conf_int.iloc[:, 1].to_numpy().clip(min=0),
        }
    )
