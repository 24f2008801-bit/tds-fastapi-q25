from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
with open("telemetry.json", "r") as f:
    DATA = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/")
def get_metrics(req: RequestBody):

    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(
                1 for r in rows
                if r["latency_ms"] > req.threshold_ms
            )
        }

    return result