from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from prophet import Prophet
from typing import List

app = FastAPI(title="Prophet Forecast Microservice", version="1.0")

class TimeSeriesRequest(BaseModel):
    dates: List[str]   # ISO date strings
    values: List[float]
    periods: int

@app.post("/forecast")
def forecast(req: TimeSeriesRequest):
    if len(req.dates) != len(req.values) or len(req.dates) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 observations; dates and values must be same length.")
    # Build dataframe
    try:
        df = pd.DataFrame({"ds": pd.to_datetime(req.dates), "y": req.values})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid dates or values: {e}")

    # Fit Prophet
    m = Prophet()
    m.fit(df)

    # Create future days
    future = m.make_future_dataframe(periods=req.periods, freq="D")
    fcst = m.predict(future)

    # Return only the next req.periods days (exclude training days)
    # If last training ds is X, we want rows where ds > X and only next req.periods rows
    last_train = df["ds"].max()
    next_fcst = fcst[fcst["ds"] > last_train].head(req.periods)
    out = next_fcst[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    out["ds"] = out["ds"].dt.strftime("%Y-%m-%d")
    return {"forecast": out.to_dict(orient="records")}
