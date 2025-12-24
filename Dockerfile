# syntax=docker/dockerfile:1.4

# ============================================================================
# Stage 1: Builder - Compile dependencies and prepare application
# ============================================================================
FROM python:3.11-slim-bookworm AS builder

# Set build-time arguments for better control
ARG PYTHON_VERSION=3.11

# Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for dependency isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies with security flags
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim-bookworm AS runtime

# Metadata labels following OCI standards
LABEL maintainer="your-email@example.com" \
      org.opencontainers.image.title="Flask Entra ID SSO" \
      org.opencontainers.image.description="Flask application with Microsoft Entra ID authentication" \
      org.opencontainers.image.version="1.0.0"

# Security: Create non-root user with specific UID/GID
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -s /sbin/nologin -c "Application user" appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables for production
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Security: Remove write permissions from application files
RUN chmod -R 555 /app && \
    chmod -R 755 /app/app

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8080

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/').read()" || exit 1

# Production-ready WSGI server with Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "run:app"]
