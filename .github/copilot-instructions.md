# AI Agent Instructions for blaue-tonne-api

This is a FastAPI service that extracts waste collection dates from PDF schedules and provides them via HTTP API. The service specifically handles schedules for the Rosenheim district (Landkreis).

## Architecture Overview

- **Entry Point**: `app/main.py` - FastAPI application with in-memory caching and configuration loading
- **Core Logic**: `app/blaue_tonne.py` - PDF parsing and date extraction using camelot-py
- **Configuration**: `app/plans.yaml` - PDF URLs and page ranges in YAML format
- **API Interface**: Single endpoint `GET /lk_rosenheim?district=<n>` returning ISO-8601 dates

## Key Patterns

1. **PDF Processing Flow**:
   - PDFs are processed on-demand when requests hit uncached districts
   - PDF tables are parsed using camelot-py's "stream" flavor
   - Dates are extracted from rows adjacent to the district name match

2. **Data Caching**:
   - Simple in-memory dict cache keyed by `landkreis -> district -> dates`
   - No cache invalidation implemented (restart service to refresh)

3. **Configuration Management**:
   - PDF sources configured in `app/plans.yaml`
   - Each plan entry requires `url` and `pages` keys
   - Example:
     ```yaml
     plans:
       - url: "https://example.com/plan.pdf"
         pages: "1,2"
     ```

## Development Workflow

1. **Local Development**:
   ```bash
   uv sync              # Install dependencies
   uv run fastapi dev   # Run development server
   ```

2. **Production Build**:
   ```bash
   docker build -t blaue-tonne-api:local .
   docker run --rm -p 8000:80 blaue-tonne-api:local
   ```

## Important Notes

- Service requires Python 3.14+
- Ruff is used for linting with 120 char line length
- PDF parsing errors are logged to stderr but don't halt execution
- All dates are returned in ISO-8601 format
- District names must match PDF content exactly, including spaces and special characters

When adding features or making changes, ensure the cache strategy and PDF processing approach are preserved unless explicitly requested otherwise.
