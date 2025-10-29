# Use Python 3.10 slim as base
FROM python:3.10-slim-bookworm AS builder

# Build argument to control whether to use Chinese mirrors
ARG USE_CHINA_MIRROR=false

# Conditionally replace with Chinese mirrors for better connectivity in China
RUN if [ "$USE_CHINA_MIRROR" = "true" ]; then \
        sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources; \
    fi

# Set the working directory
WORKDIR /app

# Install Poetry and system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && if [ "$USE_CHINA_MIRROR" = "true" ]; then \
        pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple/; \
    else \
        pip install poetry; \
    fi \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first
COPY pyproject.toml poetry.lock /app/

# Install dependencies without creating a virtual environment
RUN poetry config virtualenvs.create false \
    && if [ "$USE_CHINA_MIRROR" = "true" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/; \
        pip config set global.trusted-host mirrors.tuna.tsinghua.edu.cn; \
    fi \
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