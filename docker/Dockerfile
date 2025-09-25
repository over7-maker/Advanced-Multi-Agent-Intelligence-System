# AMAS Intelligence System Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AMAS_MODE=production
ENV AMAS_OFFLINE_MODE=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install NVIDIA CUDA toolkit (if available)
RUN if command -v nvidia-smi >/dev/null 2>&1; then \
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
        dpkg -i cuda-keyring_1.0-1_all.deb && \
        apt-get update && \
        apt-get install -y cuda-toolkit-11-8 && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-intelligence.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-intelligence.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config /app/models

# Set permissions
RUN chmod +x /app/scripts/*.py

# Create non-root user
RUN useradd -m -u 1000 amas && \
    chown -R amas:amas /app

# Switch to non-root user
USER amas

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]