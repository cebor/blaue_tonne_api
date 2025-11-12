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

CMD ["/code/.venv/bin/fastapi", "run", "--port", "80", "--proxy-headers", "--forwarded-allow-ips", "172.17.0.1"]
