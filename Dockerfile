FROM python:3.13-slim-trixie

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock README.md alembic.ini ./
COPY alembic/ ./alembic/
COPY src/ ./src/

RUN uv sync --no-cache --no-dev

COPY entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uv", "run", "-m", "memorius"]
