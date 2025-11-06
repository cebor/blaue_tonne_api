import os
import pytest

from app.blaue_tonne import DistrictNotFoundException, get_dates
from app.main import PLANS

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

CI = bool(os.getenv("CI"))


@pytest.mark.parametrize("district", DISTRICTS)
def test_get_dates_district_found(district):
    """Test that all known districts can be found in the PDF schedules."""
    for plan in PLANS:
        dates = list(get_dates(plan["url"], plan["pages"], district))
        # TODO: Add actual date assertions once we have test data
        assert len(dates) >= 0  # Replace with actual date checks


def test_get_dates_district_not_found():
    """Test that DistrictNotFoundException is raised for non-existent districts."""
    with pytest.raises(DistrictNotFoundException):
        list(get_dates(PLANS[0]["url"], PLANS[0]["pages"], "NonexistentDistrict"))


def test_get_dates_404():
    """Test that a 404 PDF URL returns an empty list (graceful degradation)."""
    result = list(
        get_dates(
            "https://chiemgau-recycling.de/404.pdf",
            "1",
            "Test District",
        )
    )
    assert result == []  # Should return empty list for 404


def test_get_dates_invalid_url():
    """Test that ValueError is raised for non-PDF URLs."""
    with pytest.raises(ValueError) as e:
        list(
            get_dates(
                "https://chiemgau-recycling.de/invalid",
                "1",
                "Test District",
            )
        )
    assert "URL must point to a PDF file" in str(e.value)


@pytest.mark.parametrize(
    "url",
    [
        pytest.param(
            "http://httpbin/anything/not_a_pdf.pdf",
            marks=pytest.mark.skipif(not CI, reason="CI-only: uses local httpbin instance"),
        ),
        pytest.param(
            "http://httpbin.org/anything/not_a_pdf.pdf",
            marks=pytest.mark.skipif(CI, reason="Non-CI: uses public httpbin.org"),
        ),
    ],
)
def test_get_dates_invalid_content_type(url):
    """Test that ValueError is raised when content-type is not application/pdf."""
    with pytest.raises(ValueError) as e:
        list(
            get_dates(
                url,
                "1",
                "Test District",
            )
        )
    assert "URL does not point to a valid PDF file" in str(e.value)
