FROM python:3.14 AS builder

WORKDIR /code

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project


FROM python:3.14-slim

WORKDIR /code

RUN groupadd -r fastapi && useradd -r -g fastapi fastapi
USER fastapi

COPY --from=builder --chown=fastapi /code/.venv /code/.venv
COPY --chown=fastapi ./app /code/app

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/code/.venv/bin/python", "-c", "import httpx; exit(0 if httpx.get('http://localhost:80/health').status_code == 200 else 1)"]

CMD ["/code/.venv/bin/fastapi", "run", "--port", "80", "--proxy-headers", "--forwarded-allow-ips", "172.17.0.1"]
