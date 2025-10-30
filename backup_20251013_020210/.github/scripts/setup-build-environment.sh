#!/bin/bash

# 🔧 AMAS Build Environment Setup Script
# Fixes Cython compilation errors and ensures all packages install correctly

set -e  # Exit on any error

echo "🚀 Setting up AMAS build environment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install build dependencies for Python packages with C extensions
echo "🔨 Installing build dependencies..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-setuptools \
    libffi-dev \
    libssl-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    pkg-config \
    cmake \
    git

# Upgrade pip, setuptools, wheel
echo "⬆️  Upgrading Python build tools..."
python -m pip install --upgrade pip setuptools wheel

# Install Cython first (needed for some packages)
echo "🐍 Installing Cython..."
python -m pip install "cython>=3.0.0"

# Install numpy first (many packages depend on it)
echo "🔢 Installing numpy (base dependency)..."
python -m pip install "numpy>=1.24.0,<2.0.0"

# Set environment variables for compilation
echo "🔧 Setting build environment variables..."
export CFLAGS="-O2"
export CXXFLAGS="-O2"
export NPY_NUM_BUILD_JOBS=2
export MAX_JOBS=2

echo "✅ Build environment setup complete!"
echo "🎯 Ready to install Python packages with C extensions"

# Verify the setup
echo "🧪 Verifying build tools..."
python -c "import setuptools; print(f'✅ setuptools: {setuptools.__version__}')"
python -c "import wheel; print(f'✅ wheel: {wheel.__version__}')"
python -c "import Cython; print(f'✅ Cython: {Cython.__version__}')"
python -c "import numpy; print(f'✅ numpy: {numpy.__version__}')"

echo "🎉 Build environment is ready for AMAS installation!"