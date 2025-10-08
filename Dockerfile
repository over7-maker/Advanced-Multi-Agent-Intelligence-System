# AMAS - Advanced Multi-Agent Intelligence System
# Production-ready Docker configuration

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AMAS_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for React dashboard
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/
COPY web/ ./web/
COPY main.py .
COPY pytest.ini .
COPY .env.example .

# Create necessary directories
RUN mkdir -p logs data/collective_knowledge data/personalities data/models

# Build React dashboard
WORKDIR /app/web
RUN npm install && npm run build

# Return to app directory
WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash amas
RUN chown -R amas:amas /app
USER amas

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command
CMD ["python", "main.py"]