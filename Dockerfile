FROM python:3.13-slim-trixie

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-cache --no-dev

COPY src/ ./src/
COPY entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app/src

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uv", "run", "-m", "memorius"]
