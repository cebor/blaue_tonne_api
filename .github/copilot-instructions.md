# AI Agent Instructions for blaue-tonne-api

FastAPI service that extracts waste collection dates from PDF schedules and exposes them via HTTP API. Handles schedules for Rosenheim district (Landkreis Rosenheim). See [README.md](../README.md) for setup and [CONTRIBUTING.md](../CONTRIBUTING.md) for commit conventions.

## Architecture

**Three-file core:**
- `app/main.py` — FastAPI app, sync endpoints, in-memory cache dict, YAML config loaded at module level
- `app/blaue_tonne.py` — PDF parsing (pdfplumber), date extraction (dateutil), module-level PDF cache
- `app/plans.yaml` — Single-source config: PDF URLs and page ranges (comma-separated, 1-indexed)

**Data flow:** Request → `main.py` checks `cache[LANDKREIS][district]` → cache miss calls `get_dates()` for each plan until district found → `blaue_tonne.py` downloads/caches PDF → extracts dates → cached and returned.

## Critical Implementation Details

**Two-level cache:**
- `PDF_CACHE` in `blaue_tonne.py`: URL → `BufferedReader` (downloaded via `niquests` → `BytesIO` → `BufferedReader`)
- `cache[LANDKREIS]` in `main.py`: district → list of dates
- No TTL, no invalidation — restart to refresh (intentional)

**District matching:** `if district in row:` on table rows — **exact substring match**, including spaces, umlauts, and numbers. `"Bruckmühl"` would match both `"Bruckmühl 1"` and `"Bruckmühl 2"`. Use `"Nußdorf am Inn"` not `"Nussdorf"`.

**Date extraction:** Finds district row, reads dates from that row **and the next row** (`table[row_idx + 1]`), then returns. `_parse_dates()` strips day names, keeps last 8 chars (`dd.mm.yy`), yields `datetime` objects. FastAPI handles ISO-8601 serialization (`"2025-01-15T00:00:00"` — always includes time component).

**Page numbers:** 1-indexed in `plans.yaml`, converted to 0-indexed in `get_dates()` (`page_num - 1`).

**Error handling:**
- `DistrictNotFoundException` → HTTP 404
- HTTP 404 from PDF URL → empty list (graceful degradation)
- Non-PDF URL → `ValueError`
- `/health` requests suppressed from access logs via `HealthCheckFilter`

## Development

**Dependency management:** Always use `uv` — never edit `pyproject.toml`/`uv.lock` manually or use `pip`/`poetry`. See README.md for full setup and run commands.

**Adding a district/PDF:** Edit `app/plans.yaml` — each entry needs `url` and `pages` (comma-separated string, 1-indexed, e.g. `"1,2,3"`).

**Python version:** `./pyver.sh <version>` updates `.python-version`, `pyproject.toml`, `Dockerfile`, `.gitlab-ci.yml` in one shot, then `uv sync`.

## Testing

Prefer the IDE's built-in test runner. Terminal fallback: `uv run pytest` (runs with `-n auto --tb=short` by default).

**Key patterns:**
- `@pytest.fixture(autouse=True)` in `conftest.py` clears both caches before/after each test
- Tests are fully mocked — **no network required**: `mock_download_pdf` fixture in `conftest.py` patches `_download_pdf` with a local fixture PDF (`tests/fixtures/lk_rosenheim_2026.pdf`); API tests patch `app.main.get_dates` directly
- HTTP error scenarios (404, timeout, invalid content-type) tested via `unittest.mock.patch` on `_download_pdf`
- `if __name__ == "__main__":` in `blaue_tonne.py` marked `# pragma: no cover`

## Pylance MCP Tools

Use Pylance MCP tools instead of raw terminal commands for code quality:

| Task | Tool |
|------|------|
| Validate a file | `pylanceFileSyntaxErrors` |
| Check a snippet before writing | `pylanceSyntaxErrors` |
| Run a Python snippet | `pylanceRunCodeSnippet` |
| Remove unused imports | `pylanceInvokeRefactoring` → `source.unusedImports` |
| Add type annotations | `pylanceInvokeRefactoring` → `source.addTypeAnnotation` |
| Apply all auto-fixes | `pylanceInvokeRefactoring` → `source.fixAll.pylance` |
