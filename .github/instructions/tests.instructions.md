---
applyTo: "tests/**/*.py"
---

# Test Conventions

- **Cache isolation**: `@pytest.fixture(autouse=True)` in `conftest.py` already clears `PDF_CACHE` and `cache[LANDKREIS]` before/after every test — do not clear caches manually inside tests
- **All tests are mocked — no network**: use the `mock_download_pdf` fixture (defined in `conftest.py`) for `blaue_tonne` tests; use `patch("app.main.get_dates", ...)` for API tests. The fixture reads `tests/fixtures/lk_rosenheim_2026.pdf` locally
- **District names must be exact**: include spaces, umlauts, and numbers exactly as they appear in the PDF table (e.g. `"Bruckmühl 1"`, `"Prien a. Chiemsee"`)
- **Date assertions**: API returns `"YYYY-MM-DDTHH:MM:SS"` strings (time component always `T00:00:00`) — assert the full ISO-8601 string
- **Parallel-safe**: tests run with `-n auto` (pytest-xdist) by default; avoid shared mutable state outside the autouse fixture
