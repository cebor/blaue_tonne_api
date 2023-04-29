from fastapi import FastAPI, HTTPException

from app.blaue_tonne import DistrictNotFoundException, get_dates

app = FastAPI()

cache = {
    "lk_rosenheim": {}
}


@app.get("/lk_rosenheim")
async def blaue_tonne_dates(district):
    URL = "https://chiemgau-recycling.de/wp-content/uploads/2022/11/Abfuhrplan_LK_Rosenheim_2023.pdf"
    PAGES = "1,2"

    if district in cache["lk_rosenheim"]:
        return cache["lk_rosenheim"][district]

    try:
        cache["lk_rosenheim"][district] = list(get_dates(URL, PAGES, district))
    except DistrictNotFoundException:
        raise HTTPException(status_code=404, detail="District not found")

    return cache["lk_rosenheim"][district]
