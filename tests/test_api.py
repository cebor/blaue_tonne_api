from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.blaue_tonne import DistrictNotFoundException
from app.main import app, cache, LANDKREIS

FAKE_DATES = {
    "Kolbermoor": [datetime(2026, 1, 15), datetime(2026, 2, 15)],
    "Bad Aibling": [datetime(2026, 1, 20), datetime(2026, 2, 20)],
    "Prien a. Chiemsee": [datetime(2026, 1, 25), datetime(2026, 2, 25)],
    "Aschau": [datetime(2026, 1, 10)],
    "Bruckmühl 1": [datetime(2026, 1, 11)],
    "Feldkirchen 2": [datetime(2026, 1, 12)],
    "Raubling 3": [datetime(2026, 1, 13)],
}


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test to ensure test isolation."""
    cache[LANDKREIS].clear()
    yield
    cache[LANDKREIS].clear()


@pytest.fixture()
def mock_get_dates():
    """Patch get_dates in app.main to avoid real PDF downloads in API tests."""

    def _get_dates(url, pages, district):
        if district not in FAKE_DATES:
            raise DistrictNotFoundException
        yield from FAKE_DATES[district]

    with patch("app.main.get_dates", side_effect=_get_dates) as mock:
        yield mock


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_check_filtered_from_logs(client, caplog):
    """Test that health check requests are filtered out of access logs."""
    import logging

    # Set up logging to capture uvicorn.access logs
    caplog.set_level(logging.INFO, logger="uvicorn.access")

    # Make a health check request
    response = client.get("/health")
    assert response.status_code == 200

    # Verify no log records contain "/health"
    for record in caplog.records:
        if record.name == "uvicorn.access":
            assert "/health" not in record.getMessage()


def test_get_dates_for_valid_district(client, mock_get_dates):
    """Test retrieving waste collection dates for a valid district."""
    response = client.get("/lk_rosenheim?district=Kolbermoor")
    assert response.status_code == 200

    dates = response.json()
    assert isinstance(dates, list)
    assert len(dates) > 0

    # Verify dates are in ISO-8601 format (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD)
    for date in dates:
        assert isinstance(date, str)
        # Check it starts with YYYY-MM-DD format
        assert len(date) >= 10
        assert date[4] == "-" and date[7] == "-"


def test_get_dates_for_invalid_district(client, mock_get_dates):
    """Test that requesting an invalid district returns 404."""
    response = client.get("/lk_rosenheim?district=NonExistentDistrict")
    assert response.status_code == 404
    assert response.json()["detail"] == "District not found"


def test_cache_functionality(client, mock_get_dates):
    """Test that the in-memory cache works correctly."""
    district = "Bad Aibling"

    # First request should call get_dates and cache the result
    response1 = client.get(f"/lk_rosenheim?district={district}")
    assert response1.status_code == 200
    dates1 = response1.json()

    # Verify the district is now in cache
    assert district in cache[LANDKREIS]
    cached_dates = [dt.isoformat() for dt in cache[LANDKREIS][district]]
    assert cached_dates == dates1

    call_count_after_first = mock_get_dates.call_count

    # Second request should use the cache and NOT call get_dates again
    response2 = client.get(f"/lk_rosenheim?district={district}")
    assert response2.status_code == 200
    dates2 = response2.json()

    assert dates1 == dates2
    assert mock_get_dates.call_count == call_count_after_first


def test_missing_district_parameter(client):
    """Test that missing district parameter returns 422 validation error."""
    response = client.get("/lk_rosenheim")
    assert response.status_code == 422  # FastAPI validation error


def test_multiple_districts_use_separate_cache_entries(client, mock_get_dates):
    """Test that different districts have separate cache entries."""
    district1 = "Kolbermoor"
    district2 = "Prien a. Chiemsee"

    response1 = client.get(f"/lk_rosenheim?district={district1}")
    assert response1.status_code == 200
    dates1 = response1.json()

    response2 = client.get(f"/lk_rosenheim?district={district2}")
    assert response2.status_code == 200
    dates2 = response2.json()

    assert district1 in cache[LANDKREIS]
    assert district2 in cache[LANDKREIS]
    assert dates1 != dates2


@pytest.mark.parametrize("district", [
    "Aschau",
    "Bruckmühl 1",
    "Feldkirchen 2",
    "Raubling 3",
])
def test_districts_with_numbers(client, mock_get_dates, district):
    """Test districts that have numbers in their names."""
    response = client.get(f"/lk_rosenheim?district={district}")
    assert response.status_code == 200
    dates = response.json()
    assert isinstance(dates, list)
    assert len(dates) > 0


@pytest.mark.network
def test_live_smoke(client):
    """Smoke test against the real API – requires network access."""
    response = client.get("/lk_rosenheim?district=Kolbermoor")
    assert response.status_code == 200
    assert len(response.json()) >= 1
