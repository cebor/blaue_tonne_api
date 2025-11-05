# AI Agent Instructions for blaue-tonne-api

FastAPI service that extracts waste collection dates from PDF schedules and exposes them via HTTP API. Handles schedules for Rosenheim district (Landkreis Rosenheim).

## Architecture Overview

**Three-file core:**
- `app/main.py` - FastAPI app with sync endpoints, in-memory cache dict, YAML config loading at module level
- `app/blaue_tonne.py` - PDF parsing with pdfplumber, date extraction with dateutil, module-level PDF cache
- `app/plans.yaml` - Single-source config: PDF URLs and page ranges (comma-separated, 1-indexed)

**API endpoints:**
- `GET /health` - Service status (always returns `{"status": "healthy"}`)
- `GET /lk_rosenheim?district=<name>` - Returns JSON list of ISO-8601 datetime strings (e.g., `["2025-01-15T00:00:00"]`)

**Data flow:**
1. Request → `main.py` checks `cache[LANDKREIS][district]` dict
2. Cache miss → iterates `PLANS` list, calls `get_dates()` for each plan until district found
3. `blaue_tonne.py` checks `PDF_CACHE` dict → downloads PDF if needed → extracts dates via pdfplumber tables
4. Results cached in `main.py` and returned

## Critical Implementation Details

### PDF Processing & Caching Strategy
- **Two-level cache**: `PDF_CACHE` (module dict in `blaue_tonne.py`) stores `BufferedReader` objects keyed by URL; `cache[LANDKREIS]` (module dict in `main.py`) stores `district → dates` mappings
- PDF download wrapping: `httpx.get()` → `BytesIO(response.content)` → `BufferedReader()` for pdfplumber reusability across requests
- **No cache invalidation** - restart service to refresh data (intentional design, no TTL or manual clear endpoints)
- District matching: simple substring `if district in row:` on table rows - **exact string match required** including spaces, umlauts, numbers
- Date extraction pattern: finds district row, extracts dates from **both current row and next row** (`table[row_idx + 1]`), then returns immediately

### Date Parsing Pattern
```python
# In _parse_dates(): strips day names, keeps last 8 chars (dd.mm.yy format)
if len(col) > DATE_LENGTH:
    col = col[-DATE_LENGTH:]
yield parse(col, dayfirst=True).isoformat()
```

### Error Handling Specifics
- `DistrictNotFoundException` raised when district not found in any table → converts to HTTP 404 in `main.py`
- HTTP 404 from PDF URL returns empty list (graceful degradation in `get_dates()`)
- Non-PDF URLs raise `ValueError` (checked via content-type header and `.pdf` extension)
- FastAPI returns HTTP 422 for missing `district` query parameter (built-in validation)

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
uv run pytest                      # All tests with xdist parallel execution (-n auto)
uv run pytest tests/test_api.py -v # Specific file, verbose output
uv run pytest --cov                # Coverage report (pytest-cov)
uv run pytest --cov --cov-report=html  # HTML coverage in htmlcov/
```

## Development Workflow

**Local dev (uv + Python 3.14+):**
```bash
uv sync                               # Install deps from uv.lock (includes dev group)
uv run fastapi dev                    # Dev server with auto-reload on port 8000
uv run fastapi run --port 8000        # Production mode (no auto-reload)
uv run python app/blaue_tonne.py      # Manual test: prints dates for hardcoded DISTRICT
```

**Docker (matches GitLab CI):**
```bash
docker build -t blaue-tonne-api:local .  # Multi-stage build with uv
docker run --rm -p 8000:80 blaue-tonne-api:local  # Exposes on port 80 inside container
```

**Adding new districts/PDFs:**
Edit `app/plans.yaml` - each entry needs `url` (PDF URL) and `pages` (comma-separated string, 1-indexed like "1,2,3")

**Python version management:**
```bash
./pyver.sh 3.13  # Updates .python-version, pyproject.toml, Dockerfile, .gitlab-ci.yml
uv sync          # Re-sync after version change
```

## Code Style & Conventions

- **Ruff**: 120 char line length (`pyproject.toml`)
- **pytest config**: `addopts = "-n auto -v --tb=short"` (parallel execution by default)
- **Type hints**: Used on function signatures (e.g., `get_dates(url: str, pages: str, district: str)`)
- **Generator pattern**: `_parse_dates()` and `get_dates()` yield results for memory efficiency

## Gotchas & Edge Cases

1. **District name matching is substring-based** - `"Bruckmühl"` matches both `"Bruckmühl 1"` and `"Bruckmühl 2"` rows. Exact strings required: `"Nußdorf am Inn"` not `"Nussdorf"`, `"Prien a. Chiemsee"` not `"Prien a Chiemsee"`
2. **Dates include time component** - API always returns `"2025-01-15T00:00:00"` format, not just `"2025-01-15"` (from `parse().isoformat()`)
3. **Page numbers are 1-indexed** in YAML config but converted to 0-indexed internally (`page_num - 1` in `get_dates()`)
4. **Cache is global module-level** - `cache[LANDKREIS]` and `PDF_CACHE` are plain dicts at module scope, persist across all requests (not thread-safe but acceptable for this use case)
5. **Test isolation via fixtures** - `@pytest.fixture(autouse=True)` in both test files clears caches before/after each test
6. **Live PDF in tests** - tests hit actual chiemgau-recycling.de URL (no mocking), so network required
7. **Main block excluded from coverage** - `if __name__ == "__main__":` block in `blaue_tonne.py` marked `# pragma: no cover`
8. **GitLab CI uses uv** - `.gitlab-ci.yml` installs uv via curl script, runs `uv sync --locked` before tests
9. **Docker uses multi-stage build** - builder stage runs `uv sync --no-dev --no-install-project`, final stage copies `.venv` and `app/` only
