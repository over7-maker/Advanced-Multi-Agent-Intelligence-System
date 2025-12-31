"""Root-level pytest configuration for AMAS tests.

This file ensures proper Python path setup and test environment initialization.
"""

import os
import sys
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.resolve()

# Add src directory to Python path BEFORE any imports
src_path = PROJECT_ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add project root to path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment variables
os.environ.setdefault("AMAS_ENVIRONMENT", "testing")
os.environ.setdefault("AMAS_DEBUG", "false")
os.environ.setdefault("AMAS_LOG_LEVEL", "WARNING")
os.environ.setdefault("PYTHONPATH", f"{PROJECT_ROOT}:{src_path}")

# Configure testing
os.environ["TESTING"] = "true"

# Import pytest fixtures from tests directory
pytest_plugins = []
