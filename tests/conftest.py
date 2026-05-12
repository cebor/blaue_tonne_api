from io import BufferedReader, BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

FIXTURE_PDF = Path(__file__).parent / "fixtures" / "lk_rosenheim_2026.pdf"


@pytest.fixture()
def pdf_bytes() -> bytes:
    return FIXTURE_PDF.read_bytes()


@pytest.fixture()
def mock_download_pdf(pdf_bytes):
    """Patch _download_pdf to return a fresh BufferedReader from the local fixture PDF.

    Uses side_effect so each call gets a fresh reader (pdfplumber seeks from start).
    """

    def _fresh_reader(url: str) -> BufferedReader:
        return BufferedReader(BytesIO(pdf_bytes))

    with patch("app.blaue_tonne._download_pdf", side_effect=_fresh_reader) as mock:
        yield mock
