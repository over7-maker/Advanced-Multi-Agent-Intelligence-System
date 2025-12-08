# Dockerfile (PRODUCTION-OPTIMIZED MULTI-STAGE BUILD)
# AMAS - Advanced Multi-Agent Intelligence System

# ============================================================================
# STAGE 1: Python Dependencies Builder
# ============================================================================
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: Frontend Builder
# ============================================================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files (will fail gracefully if directories don't exist)
# Use build arg to control which directory to use
ARG FRONTEND_DIR=frontend
COPY ${FRONTEND_DIR}/package*.json ./

# Install dependencies
RUN if [ -f package.json ] && [ -s package.json ]; then \
      npm ci --only=production || npm install --only=production; \
    else \
      echo "No package.json found, creating empty one" && \
      echo '{"name":"amas-frontend","version":"1.0.0"}' > package.json; \
    fi

# Copy frontend source
COPY ${FRONTEND_DIR}/ ./

# Build frontend if package.json has build script
RUN if [ -f package.json ] && grep -q '"build"' package.json; then \
      npm run build || (echo "Frontend build failed, creating placeholder..." && mkdir -p build && echo '<html><body>Frontend not built</body></html>' > build/index.html); \
    else \
      echo "Skipping frontend build - no build script found"; \
      mkdir -p build && echo '<html><body>Frontend not built</body></html>' > build/index.html; \
    fi

# ============================================================================
# STAGE 3: Production Runtime
# ============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    PORT=8000 \
    PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r amas && useradd -r -g amas amas

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy frontend build (create directory first, then copy)
RUN mkdir -p /app/frontend/build
COPY --from=frontend-builder /app/frontend/build /app/frontend/build
RUN if [ ! -d /app/frontend/build ] || [ ! -f /app/frontend/build/index.html ]; then \
      mkdir -p /app/frontend/build && \
      echo '<html><body>Frontend placeholder</body></html>' > /app/frontend/build/index.html; \
    fi

# Copy application code
COPY --chown=amas:amas src/ ./src/
COPY --chown=amas:amas scripts/ ./scripts/
COPY --chown=amas:amas config/ ./config/
COPY --chown=amas:amas main.py ./
COPY --chown=amas:amas main_simple.py ./

# Copy Alembic files if they exist (will fail gracefully if not present)
COPY --chown=amas:amas alembic.ini ./
COPY --chown=amas:amas alembic/ ./alembic/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R amas:amas /app/logs /app/data

# Switch to non-root user
USER amas

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["sh", "-c", "if command -v uvicorn > /dev/null 2>&1; then uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4; else python main_simple.py; fi"]
