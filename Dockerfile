# Use the pre-built Python base image
FROM python:3.13-slim

# Install required system dependencies
RUN apt update && apt install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    python3-click \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create restricted user FIRST to ensure proper ownership
RUN addgroup --system --gid 1001 micro && \
    adduser --system --uid 1001 --gid 1001 --no-create-home micro

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=off

# Set the working directory inside the container
WORKDIR /app

# Copy requirements FIRST for layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt  # Removed --user flag

# Copy application files with proper ownership
COPY --chown=micro:micro . .

# Create directories for volumes
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Final permissions fix
RUN chmod 755 /app && \
    chown -R micro:micro /app

# Switch to non-root user
USER micro

# Single entrypoint copy with exec permissions
COPY --chown=micro:micro entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]