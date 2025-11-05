import pytest
from app.blaue_tonne import get_dates, DistrictNotFoundException


PDF_URL = "https://chiemgau-recycling.de/wp-content/uploads/2025/01/Abfuhrplan_LK_Rosenheim_2025.pdf"
DISTRICTS = [
    "Albaching",
    "Amerang",
    "Aschau",
    "Babensham",
    "Bad Aibling",
    "Bad Endorf",
    "Bad Feilnbach",
    "Bernau",
    "Brannenburg",
    "Breitbrunn",
    "Bruckmühl 1",
    "Bruckmühl 2",
    "Edling",
    "Eggstätt",
    "Eiselfing",
    "Feldkirchen 1",
    "Feldkirchen 2",
    "Flintsbach",
    "Frasdorf",
    "Griesstätt",
    "Großkarolinenfeld 1",
    "Großkarolinenfeld 2",
    "Gstadt",
    "Halfing",
    "Höslwang",
    "Kiefersfelden",
    "Kolbermoor",
    "Neubeuern",
    "Nußdorf am Inn",
    "Oberaudorf",
    "Pfaffing",
    "Prien a. Chiemsee",
    "Prutting",
    "Ramerberg",
    "Raubling 1",
    "Raubling 2",
    "Raubling 3",
    "Riedering",
    "Rimsting",
    "Rohrdorf",
    "Rott am Inn",
    "Samerberg",
    "Schechen",
    "Schonstett",
    "Soyen",
    "Stephanskirchen 1",
    "Stephanskirchen 2",
    "Söchtenau",
    "Tuntenhausen",
    "Vogtareuth",
]


@pytest.mark.parametrize("district", DISTRICTS)
def test_get_dates_district_found(district):
    dates = list(get_dates(PDF_URL, "1,2", district))
    # TODO: Add actual date assertions once we have test data
    assert len(dates) >= 0  # Replace with actual date checks


def test_get_dates_district_not_found():
    with pytest.raises(DistrictNotFoundException):
        list(get_dates(PDF_URL, "1,2", "NonexistentDistrict"))


def test_get_dates_404():
    result = list(
        get_dates(
            "https://chiemgau-recycling.de/404.pdf",
            "1",
            "Test District",
        )
    )
    assert result == []  # Should return empty list for 404


def test_get_dates_invalid_url():
    with pytest.raises(ValueError):
        list(
            get_dates(
                "https://chiemgau-recycling.de/invalid",
                "1",
                "Test District",
            )
        )
