# AMAS Docker Image
# Multi-stage build for optimized production image

# ============================================================================
# Builder Stage - Install dependencies and build the application
# ============================================================================
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Runtime Stage - Create the final production image
# ============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r amas \
    && useradd -r -g amas -d /app -s /bin/bash amas

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create application directory and set ownership
WORKDIR /app
RUN chown -R amas:amas /app

# Copy application code
COPY --chown=amas:amas src/ ./src/
COPY --chown=amas:amas config/ ./config/
COPY --chown=amas:amas docker/entrypoint.sh ./entrypoint.sh

# Create data directories
RUN mkdir -p logs data models && \
    chown -R amas:amas logs data models

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER amas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["uvicorn", "amas.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ============================================================================
# Development Stage - For development with hot reload
# ============================================================================
FROM production as development

# Switch back to root for development tools installation
USER root

# Install development dependencies
RUN pip install pytest black flake8 mypy pre-commit

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to amas user
USER amas

# Override command for development
CMD ["uvicorn", "amas.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]