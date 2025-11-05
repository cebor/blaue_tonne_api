# AI Agent Instructions for blaue-tonne-api

FastAPI service that extracts waste collection dates from PDF schedules and exposes them via HTTP API. Handles schedules for Rosenheim district (Landkreis).

## Architecture Overview

**Three-file core:**
- `app/main.py` - FastAPI app, in-memory cache, YAML config loading
- `app/blaue_tonne.py` - PDF parsing with pdfplumber, date extraction with dateutil
- `app/plans.yaml` - PDF URLs and page ranges

**API endpoints:**
- `GET /health` - Service status
- `GET /lk_rosenheim?district=<name>` - Returns ISO-8601 datetime strings (e.g., `"2025-01-15T00:00:00"`)

## Critical Implementation Details

### PDF Processing & Caching Strategy
- **Two-level cache**: `PDF_CACHE` in `blaue_tonne.py` stores downloaded PDFs as `BufferedReader` objects; `cache` in `main.py` stores extracted dates per district
- PDFs downloaded on first request, wrapped in `BytesIO` + `BufferedReader` for pdfplumber reusability
- No cache invalidation - restart service to refresh data
- District matching uses simple `if district in row:` on table rows (exact string match required)
- Dates extracted from two rows: current row + next row (`table[row_idx + 1]`)

### Date Parsing Pattern
```python
# In _parse_dates(): strips day names, keeps last 8 chars (dd.mm.yy format)
if len(col) > DATE_LENGTH:
    col = col[-DATE_LENGTH:]
yield parse(col, dayfirst=True).isoformat()
```

### Error Handling Specifics
- `DistrictNotFoundException` raised when district not found in any table
- HTTP 404 from PDF URL returns empty list (graceful degradation)
- Non-PDF URLs raise `ValueError` (checked via content-type header)

## Testing Approach

**Two test files:**
1. `tests/test_blaue_tonne.py` - Unit tests for PDF parsing logic (50+ parametrized district tests)
2. `tests/test_api.py` - Integration tests using `TestClient` for HTTP endpoints

**Key testing patterns:**
- `@pytest.fixture(autouse=True)` clears cache before/after each test for isolation
- Tests use live PDF from production (chiemgau-recycling.de)
- District names with special chars/numbers tested (e.g., "Bruckmühl 1", "Prien a. Chiemsee")
- Main block in `blaue_tonne.py` marked with `# pragma: no cover` (manual testing only)

**Run tests:**
```bash
uv run pytest              # All tests with xdist parallel
uv run pytest tests/test_api.py -v  # Specific file
pytest --cov               # Coverage report (pytest-cov installed)
```

## Development Workflow

**Local dev (uv + Python 3.14+):**
```bash
uv sync                    # Install deps from uv.lock
uv run fastapi dev         # Dev server with auto-reload
```

**Docker (matches CI):**
```bash
docker build -t blaue-tonne-api:local .
docker run --rm -p 8000:80 blaue-tonne-api:local
```

**Adding new districts/PDFs:**
Edit `app/plans.yaml` - each entry needs `url` and `pages` (comma-separated, 1-indexed)

## Code Style & Conventions

- **Ruff**: 120 char line length (`pyproject.toml`)
- **pytest config**: `addopts = "-n auto -v --tb=short"` (parallel execution by default)
- **Type hints**: Used on function signatures (e.g., `get_dates(url: str, pages: str, district: str)`)
- **Generator pattern**: `_parse_dates()` and `get_dates()` yield results for memory efficiency

## Gotchas

1. **District name matching is exact** - spaces, umlauts, numbers must match PDF exactly (e.g., "Nußdorf am Inn" not "Nussdorf")
2. **Dates include time component** - API returns `"2025-01-15T00:00:00"` not just `"2025-01-15"`
3. **Page numbers are 1-indexed** in YAML config but converted to 0-indexed internally
4. **Cache is global module-level** - `cache[LANDKREIS]` in main.py and `PDF_CACHE` in blaue_tonne.py persist across requests
5. **Coverage files excluded** - `.coverage`, `htmlcov/` in `.gitignore`
