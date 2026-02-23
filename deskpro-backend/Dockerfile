# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install Python dependencies (cached as a separate layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy application code
COPY . .

EXPOSE 8000

# Default: migrate + create-admin + runserver
# Override CMD in docker-compose for production (e.g. gunicorn)
CMD ["sh", "-c", \
     "uv run manage.py migrate --noinput && \
      uv run manage.py create_saas_admin && \
      uv run manage.py runserver 0.0.0.0:8000"]
