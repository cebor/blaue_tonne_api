from fastapi import FastAPI, HTTPException

from app.blaue_tonne import DistrictNotFoundException, get_dates

app = FastAPI()

LANDKREIS = "lk_rosenheim"

cache = {
    LANDKREIS: {}
}


@app.get("/" + LANDKREIS)
async def blaue_tonne_dates(district: str) -> list[str]:
    URL = "https://chiemgau-recycling.de/wp-content/uploads/2022/11/Abfuhrplan_LK_Rosenheim_2023.pdf"
    PAGES = "1,2"

    if district in cache[LANDKREIS]:
        return cache[LANDKREIS][district]

    try:
        cache[LANDKREIS][district] = list(get_dates(URL, PAGES, district))
    except DistrictNotFoundException:
        raise HTTPException(status_code=404, detail="District not found")

    return cache[LANDKREIS][district]
