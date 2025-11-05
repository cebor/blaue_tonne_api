import pytest
from fastapi.testclient import TestClient

from app.main import app, cache, LANDKREIS


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test to ensure test isolation."""
    cache[LANDKREIS].clear()
    yield
    cache[LANDKREIS].clear()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_dates_for_valid_district(client):
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


def test_get_dates_for_invalid_district(client):
    """Test that requesting an invalid district returns 404."""
    response = client.get("/lk_rosenheim?district=NonExistentDistrict")
    assert response.status_code == 404
    assert response.json()["detail"] == "District not found"


def test_cache_functionality(client):
    """Test that the in-memory cache works correctly."""
    district = "Bad Aibling"

    # First request should hit the PDF and cache the result
    response1 = client.get(f"/lk_rosenheim?district={district}")
    assert response1.status_code == 200
    dates1 = response1.json()

    # Verify the district is now in cache
    assert district in cache[LANDKREIS]
    assert cache[LANDKREIS][district] == dates1

    # Second request should return the same cached data
    response2 = client.get(f"/lk_rosenheim?district={district}")
    assert response2.status_code == 200
    dates2 = response2.json()

    # Both responses should be identical
    assert dates1 == dates2


def test_missing_district_parameter(client):
    """Test that missing district parameter returns 422 validation error."""
    response = client.get("/lk_rosenheim")
    assert response.status_code == 422  # FastAPI validation error


def test_multiple_districts_use_separate_cache_entries(client):
    """Test that different districts have separate cache entries."""
    district1 = "Kolbermoor"
    district2 = "Prien a. Chiemsee"

    # Request for first district
    response1 = client.get(f"/lk_rosenheim?district={district1}")
    assert response1.status_code == 200
    dates1 = response1.json()

    # Request for second district
    response2 = client.get(f"/lk_rosenheim?district={district2}")
    assert response2.status_code == 200
    dates2 = response2.json()

    # Both should be in cache
    assert district1 in cache[LANDKREIS]
    assert district2 in cache[LANDKREIS]

    # Dates should be different (different districts have different schedules)
    assert dates1 != dates2


@pytest.mark.parametrize("district", [
    "Aschau",
    "Bruckmühl 1",
    "Feldkirchen 2",
    "Raubling 3",
])
def test_districts_with_numbers(client, district):
    """Test districts that have numbers in their names."""
    response = client.get(f"/lk_rosenheim?district={district}")
    assert response.status_code == 200
    dates = response.json()
    assert isinstance(dates, list)
    assert len(dates) > 0
