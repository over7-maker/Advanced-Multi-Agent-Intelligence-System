# AMAS Development Container
# Optimized for development with all tools and dependencies

FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/workspaces \
    AMAS_ENV=development \
    DEVCONTAINER=true

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    gcc \
    g++ \
    make \
    # Version control
    git \
    curl \
    wget \
    # Utilities
    vim \
    nano \
    sudo \
    ca-certificates \
    # Network tools
    iputils-ping \
    netcat-openbsd \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

# Create workspace directory
WORKDIR /workspaces

# Install development tools (these will be available immediately)
# Dependencies will be installed in post-create script for better flexibility
RUN pip install --no-cache-dir \
    black \
    ruff \
    isort \
    mypy \
    pytest \
    pytest-asyncio \
    pytest-cov \
    ipython \
    jupyter \
    fastapi \
    uvicorn \
    pydantic \
    pyyaml

# Install Node.js 18.x for frontend development
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version && \
    npm --version

# Set up git (will be overridden by user config)
RUN git config --global --add safe.directory '*'

# Default command
CMD ["/bin/bash"]
