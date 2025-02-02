FROM python:3.13-slim

WORKDIR /code

# Install dependencies
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY ./app /code/app

CMD ["/code/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--forwarded-allow-ips", "172.17.0.1"]
