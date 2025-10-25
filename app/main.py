from fastapi import FastAPI, HTTPException

from app.blaue_tonne import DistrictNotFoundException, get_dates

app = FastAPI()

LANDKREIS = "lk_rosenheim"

cache = {LANDKREIS: {}}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/" + LANDKREIS)
async def blaue_tonne_dates(district: str) -> list[str]:
    PLANS = [
        # {
        #     "url": "https://chiemgau-recycling.de/wp-content/uploads/2022/11/Abfuhrplan_LK_Rosenheim_2023.pdf",
        #     "pages": "1,2",
        # },
        # {
        #     "url": "https://chiemgau-recycling.de/wp-content/uploads/2023/11/Abfuhrplan_LK_Rosenheim_2024.pdf",
        #     "pages": "1,2",
        # },
        {
            "url": "https://chiemgau-recycling.de/wp-content/uploads/2025/01/Abfuhrplan_LK_Rosenheim_2025.pdf",
            "pages": "1,2",
        },
    ]

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
