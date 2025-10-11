# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV POETRY_VERSION=2.2.0 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl git locales && \
    pip install "poetry==$POETRY_VERSION" && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV LANG=de_DE.UTF-8 \
    LANGUAGE=de_DE:de \
    LC_ALL=de_DE.UTF-8

# Set work directory
WORKDIR /app

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies 
# --no-root to avoid installing the package itself
# --only main to skip dev dependencies
RUN poetry install --no-root --only main

# Copy the rest of the application
COPY . .

# Expose port (adjust if needed)
EXPOSE 5000

# Start the application using gunicorn
CMD ["poetry", "run", "/app/start_prodserver.sh"]
