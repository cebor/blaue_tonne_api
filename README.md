# Blaue Tonne API

Small FastAPI service that extracts waste-collection dates from remote PDF "Abfuhrplan" files and exposes them over HTTP.

## Uses
- HTTP endpoint: `GET /lk_rosenheim?district=<name>` — returns a JSON list of ISO-8601 dates for the requested district.
- Health check: `GET /health` — returns basic service status.
- Example:

```bash
curl 'http://localhost:8000/lk_rosenheim?district=Aschau'
# => ["2025-01-06T00:00:00", "2025-02-03T00:00:00", ...]
```

## Devs
Run locally (uv + fastapi):

```bash
# Install dependencies
uv sync

# dev mod
uv run fastapi dev

# prod mod
uv run fastapi run --host 127.0.0.1 --port 8000

# run tests
uv run pytest
```

Run in Docker (recommended to match CI):

```bash
docker build -t blaue-tonne-api:local .
docker run --rm -p 8000:80 blaue-tonne-api:local
```
