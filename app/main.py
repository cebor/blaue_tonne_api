from datetime import datetime
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException

from app.blaue_tonne import DistrictNotFoundException, get_dates

app = FastAPI()

LANDKREIS = "lk_rosenheim"

# Load waste collection plans from YAML configuration
yaml_path = Path(__file__).parent / "plans.yaml"
with open(yaml_path, "r") as f:
    config = yaml.safe_load(f)
    PLANS = config["plans"]

# simple in-memory cache keyed by LANDKREIS -> district -> dates
cache = {LANDKREIS: {}}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get(
    "/" + LANDKREIS,
    responses={
        200: {"description": "List of waste collection dates for the specified district"},
        404: {"description": "District not found"},
    },
)
async def blaue_tonne_dates(district: str) -> list[datetime]:
    # PLANS are sourced from app/plans.yaml
    # Edit app/plans.yaml to add or update plan entries

    if district in cache[LANDKREIS]:
        return cache[LANDKREIS][district]

    dates = []
    for plan in PLANS:
        try:
            dates.extend(list(get_dates(plan["url"], plan["pages"], district)))
        except DistrictNotFoundException:
            raise HTTPException(status_code=404, detail="District not found")

    cache[LANDKREIS][district] = dates
    return cache[LANDKREIS][district]
