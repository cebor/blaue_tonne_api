FROM python:3.14 AS builder

WORKDIR /code

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project


FROM python:3.14-slim

WORKDIR /code

COPY --from=builder /code/.venv /code/.venv
COPY ./app /code/app

CMD ["/code/.venv/bin/fastapi", "run", "--port", "80", "--proxy-headers", "--forwarded-allow-ips", "172.17.0.1"]
