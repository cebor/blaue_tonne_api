from fastapi import FastAPI, HTTPException

from app.blaue_tonne import DistrictNotFoundException, get_dates
from app.plans import PLANS


app = FastAPI()

LANDKREIS = "lk_rosenheim"

# simple in-memory cache keyed by LANDKREIS -> district -> dates
cache = {LANDKREIS: {}}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/" + LANDKREIS)
async def blaue_tonne_dates(district: str) -> list[str]:
    # PLANS are sourced from `app.plans.PLANS`
    # edit `app/plans.py` to add or update plan entries

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
