FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Python deps (cached layer)
COPY pyproject.toml .
RUN uv sync --no-dev

# Copy source
COPY . .

EXPOSE 8000

# Default: API server. Celery overrides this in compose.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
