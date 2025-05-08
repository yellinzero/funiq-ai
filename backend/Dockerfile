# Use Python 3.10 slim as base
FROM python:3.10-slim-bookworm AS builder

# Set the working directory
WORKDIR /app

# Install Poetry and system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install poetry \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first
COPY pyproject.toml poetry.lock /app/

# Install dependencies without creating a virtual environment
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root --no-interaction --no-ansi \
    && rm -rf ~/.cache/pypoetry \
    && rm -rf ~/.cache/pip

# Start fresh from a smaller image
FROM python:3.10-slim-bookworm AS final

WORKDIR /app

# Copy only the necessary files from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . /app

# Copy the entrypoint script and set executable permissions
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose FastAPI port
EXPOSE 5000

# Default entrypoint
ENTRYPOINT ["/entrypoint.sh"]