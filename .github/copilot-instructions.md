# AI Agent Instructions for blaue-tonne-api

This is a FastAPI service that extracts waste collection dates from PDF schedules and provides them via HTTP API. The service specifically handles schedules for the Rosenheim district (Landkreis).

## Architecture Overview

- **Entry Point**: `app/main.py` - FastAPI application with in-memory caching and configuration loading
- **Core Logic**: `app/blaue_tonne.py` - PDF parsing and date extraction using pdfplumber
- **Configuration**: `app/plans.yaml` - PDF URLs and page ranges in YAML format
- **API Interface**:
  - Health check: `GET /health` returns service status
  - Collection dates: `GET /lk_rosenheim?district=<n>` returning ISO-8601 dates

## Key Patterns

1. **PDF Processing Flow**:
   - PDFs are processed on-demand when requests hit uncached districts
   - PDF tables are parsed using pdfplumber with in-memory caching
   - Dates are extracted and validated using dateutil parser
   - PDF data is cached in memory to avoid repeated downloads

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
   uv sync                 # Install dependencies
   uv sync --extra test        # Install test dependencies
   uv run fastapi dev     # Run development server
   uv run pytest          # Run tests
   ```

2. **Production Build**:
   ```bash
   docker build -t blaue-tonne-api:local .
   docker run --rm -p 8000:80 blaue-tonne-api:local
   ```

## Important Notes

- Service requires Python 3.14+
- Dependencies:
  - pdfplumber for PDF table extraction
  - python-dateutil for date parsing
  - FastAPI for web service
  - PyYAML for configuration
- Ruff is used for linting with 120 char line length
- All dates are returned in ISO-8601 format
- District names must match PDF content exactly, including spaces and special characters
- Test suite available using pytest with asyncio support

When adding features or making changes, ensure the cache strategy and PDF processing approach are preserved unless explicitly requested otherwise.
