import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://quality_user:quality_password@postgres:5432/qualitydb",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
app = FastAPI(
    title="Automotive Quality Intelligence API",
    version="0.1.0",
    description="Reusable ingestion and KPI API for automotive quality measurement data.",
)


class MeasurementIn(BaseModel):
    event_time: datetime
    vehicle_id: str = Field(min_length=3, max_length=64)
    model: str = Field(min_length=1, max_length=64)
    station_code: str = Field(min_length=1, max_length=32)
    characteristic_code: str = Field(min_length=1, max_length=64)
    shift_code: str = Field(pattern=r"^[ABC]$")
    target_value: float
    lower_spec_limit: float
    upper_spec_limit: float
    measured_value: float
    unit: str = Field(min_length=1, max_length=16)
    source: str = Field(default="synthetic", max_length=64)
    batch_id: Optional[str] = Field(default=None, max_length=64)

    @field_validator("upper_spec_limit")
    @classmethod
    def validate_limits(cls, v, info):
        data = info.data
        if "lower_spec_limit" in data and v <= data["lower_spec_limit"]:
            raise ValueError("upper_spec_limit must be greater than lower_spec_limit")
        return v


def insert_rows(rows: List[MeasurementIn]) -> int:
    sql = text("""
        INSERT INTO quality_measurement (
            event_time, vehicle_id, model, station_code, characteristic_code,
            shift_code, target_value, lower_spec_limit, upper_spec_limit,
            measured_value, unit, source, batch_id
        )
        VALUES (
            :event_time, :vehicle_id, :model, :station_code, :characteristic_code,
            :shift_code, :target_value, :lower_spec_limit, :upper_spec_limit,
            :measured_value, :unit, :source, :batch_id
        )
        ON CONFLICT (event_time, vehicle_id, station_code, characteristic_code)
        DO NOTHING
    """)
    payload = [r.model_dump() for r in rows]
    with engine.begin() as conn:
        result = conn.execute(sql, payload)
    return result.rowcount or 0


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@app.post("/measurements")
def ingest_measurement(row: MeasurementIn):
    inserted = insert_rows([row])
    return {"accepted": inserted, "received": 1}


@app.post("/measurements/batch")
def ingest_measurements(rows: List[MeasurementIn]):
    if not rows:
        raise HTTPException(status_code=400, detail="Batch cannot be empty")
    if len(rows) > 5000:
        raise HTTPException(status_code=413, detail="Maximum batch size is 5000")
    inserted = insert_rows(rows)
    return {"accepted": inserted, "received": len(rows)}


@app.get("/kpis/overview")
def kpi_overview(days: int = 30):
    sql = text("""
        SELECT
            COUNT(*) AS measurements,
            COUNT(DISTINCT vehicle_id) AS vehicles,
            ROUND(100.0 * AVG(CASE WHEN is_within_spec THEN 1 ELSE 0 END), 2) AS measurement_pass_rate_pct,
            COUNT(*) FILTER (WHERE NOT is_within_spec) AS out_of_spec_measurements,
            ROUND(100.0 * COUNT(DISTINCT vehicle_id) FILTER (
                WHERE vehicle_id NOT IN (
                    SELECT vehicle_id
                    FROM quality_measurement
                    WHERE NOT is_within_spec
                      AND event_time >= NOW() - make_interval(days => :days)
                )
            ) / NULLIF(COUNT(DISTINCT vehicle_id), 0), 2) AS first_pass_yield_pct
        FROM quality_measurement
        WHERE event_time >= NOW() - make_interval(days => :days)
    """)
    with engine.connect() as conn:
        row = conn.execute(sql, {"days": days}).mappings().one()
    return dict(row)


@app.get("/kpis/pareto")
def defect_pareto(days: int = 30, limit: int = 10):
    sql = text("""
        SELECT
            characteristic_code,
            station_code,
            COUNT(*) AS defect_count
        FROM quality_measurement
        WHERE NOT is_within_spec
          AND event_time >= NOW() - make_interval(days => :days)
        GROUP BY characteristic_code, station_code
        ORDER BY defect_count DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {"days": days, "limit": limit}).mappings().all()
    return [dict(r) for r in rows]
