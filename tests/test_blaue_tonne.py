from unittest.mock import MagicMock, patch

import niquests
import pytest

from app.blaue_tonne import PDF_CACHE, DistrictNotFoundException, _download_pdf, get_dates
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

@pytest.fixture(autouse=True)
def clear_pdf_cache():
    """Clear the PDF cache before and after each test for isolation."""
    PDF_CACHE.clear()
    yield
    PDF_CACHE.clear()


@pytest.mark.parametrize("district", DISTRICTS)
def test_get_dates_district_found(district, mock_download_pdf):
    """Test that all known districts can be found in the PDF schedules."""
    for plan in PLANS:
        dates = list(get_dates(plan["url"], plan["pages"], district))
        assert len(dates) >= 1


def test_get_dates_district_not_found(mock_download_pdf):
    """Test that DistrictNotFoundException is raised for non-existent districts."""
    with pytest.raises(DistrictNotFoundException):
        list(get_dates(PLANS[0]["url"], PLANS[0]["pages"], "NonexistentDistrict"))


def test_get_dates_404():
    """Test that a 404 PDF URL returns an empty list (graceful degradation)."""
    response = niquests.Response()
    response.status_code = 404
    request = niquests.PreparedRequest()
    request.prepare_method("GET")
    request.prepare_url("https://example.com/404.pdf", None)
    response.request = request
    response.url = "https://example.com/404.pdf"

    with patch(
        "app.blaue_tonne._download_pdf",
        side_effect=niquests.HTTPError(response=response),
    ):
        result = list(get_dates("https://example.com/404.pdf", "1", "Test District"))
    assert result == []


def test_get_dates_invalid_url():
    """Test that ValueError is raised for non-PDF URLs."""
    with pytest.raises(ValueError) as e:
        list(
            get_dates(
                "https://example.com/invalid",
                "1",
                "Test District",
            )
        )
    assert "URL must point to a PDF file" in str(e.value)


def test_get_dates_invalid_content_type():
    """Test that ValueError is raised when content-type is not application/pdf."""
    mock_response = MagicMock(spec=niquests.Response)
    mock_response.headers = {"content-type": "text/html"}
    mock_response.status_code = 200
    mock_response.content = b"<html>not a pdf</html>"

    with patch("niquests.get", return_value=mock_response):
        with pytest.raises(ValueError) as e:
            list(get_dates("https://example.com/not_a_pdf.pdf", "1", "Test District"))
    assert "URL does not point to a valid PDF file" in str(e.value)


def test_get_dates_non_404_http_error():
    """Test that non-404 HTTP errors are re-raised."""
    response = niquests.Response()
    response.status_code = 500
    request = niquests.PreparedRequest()
    request.prepare_method("GET")
    request.prepare_url("https://example.com/test.pdf", None)
    response.request = request
    response.url = "https://example.com/test.pdf"
    with patch(
        "app.blaue_tonne._download_pdf",
        side_effect=niquests.HTTPError(response=response),
    ):
        with pytest.raises(niquests.HTTPError):
            list(get_dates("https://example.com/test.pdf", "1", "Test District"))


def test_download_pdf_cache_hit(pdf_bytes):
    """Test that _download_pdf returns the cached reader on the second call without re-downloading."""
    url = "https://example.com/test.pdf"

    mock_response = MagicMock(spec=niquests.Response)
    mock_response.headers = {"content-type": "application/pdf"}
    mock_response.status_code = 200
    mock_response.content = pdf_bytes

    with patch("niquests.get", return_value=mock_response) as mock_get:
        first = _download_pdf(url)
        second = _download_pdf(url)

    assert mock_get.call_count == 1
    assert first is second
    assert url in PDF_CACHE


@pytest.mark.network
def test_live_smoke():
    """Smoke test against the real PDF URL – requires network access."""
    dates = list(get_dates(PLANS[0]["url"], PLANS[0]["pages"], "Kolbermoor"))
    assert len(dates) >= 1
