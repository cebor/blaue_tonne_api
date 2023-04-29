from fastapi import FastAPI
from app.blaue_tonne import get_dates

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

    cache["lk_rosenheim"][district] = list(get_dates(URL, PAGES, district))
    return cache["lk_rosenheim"][district]
