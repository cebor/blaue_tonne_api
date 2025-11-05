# Blaue Tonne API

FastAPI service that extracts waste collection dates from PDF schedules and exposes them via HTTP API. Currently supports the Rosenheim district (Landkreis Rosenheim).

## Features

- **PDF Parsing**: Automatically downloads and parses waste collection schedules from PDF files
- **In-Memory Caching**: Caches both downloaded PDFs and extracted dates for fast subsequent requests
- **RESTful API**: Simple HTTP endpoints for date retrieval and health checks

## API Endpoints

### Get Collection Dates
```bash
GET /lk_rosenheim?district=<name>
```

Returns a JSON list of ISO-8601 datetime strings for the requested district.

**Example:**
```bash
curl 'http://localhost:8000/lk_rosenheim?district=Aschau'
# => ["2025-01-06T00:00:00", "2025-02-03T00:00:00", ...]
```

**Supported Districts**: See `app/plans.yaml` for the full list of available districts.

### Health Check
```bash
GET /health
```

Returns service status.

## Development

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

### Local Setup

```bash
# Install dependencies
uv sync

# Run development server (with auto-reload)
uv run fastapi dev

# Run production server
uv run fastapi run --host 127.0.0.1 --port 8000
```

### Running Tests

```bash
# Run all tests (with parallel execution via pytest-xdist)
uv run pytest

# Run specific test file
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov

# Run with coverage HTML report
uv run pytest --cov --cov-report=html
```

**Test Features:**
- Parallel test execution enabled by default (`-n auto`)
- Unit tests for PDF parsing logic (`tests/test_blaue_tonne.py`)
- Integration tests for API endpoints (`tests/test_api.py`)
- 50+ parametrized district tests to ensure data quality

### Docker

Run in Docker (recommended to match CI environment):

```bash
# Build image
docker build -t blaue-tonne-api:local .

# Run container
docker run --rm -p 8000:80 blaue-tonne-api:local
```

## Configuration

Edit `app/plans.yaml` to add or modify PDF sources:

```yaml
- url: "https://example.com/schedule.pdf"
  pages: "1,2,3"  # Comma-separated page numbers (1-indexed)
```

## License

See [LICENSE](LICENSE) file for details.
