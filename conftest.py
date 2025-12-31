"""Root-level pytest configuration for AMAS tests.

This file ensures proper Python path setup, test environment initialization,
and provides shared fixtures for all tests.
"""

import os
import sys
from pathlib import Path

import pytest

# Get the project root
PROJECT_ROOT = Path(__file__).parent.resolve()

# Add src directory to Python path BEFORE any imports
# This allows both 'from amas' and 'from src.amas' import styles
src_path = PROJECT_ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add project root to path for relative imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure testing environment
os.environ.setdefault("AMAS_ENVIRONMENT", "testing")
os.environ.setdefault("AMAS_DEBUG", "false")
os.environ.setdefault("AMAS_LOG_LEVEL", "ERROR")
os.environ.setdefault("AMAS_OFFLINE_MODE", "true")
os.environ["TESTING"] = "true"

# Suppress warnings during testing
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=pytest.PytestUnraisableExceptionWarning)


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory path."""
    data_dir = PROJECT_ROOT / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    # Store original env vars
    original_env = os.environ.copy()
    
    yield
    
    # Restore original env vars (except for testing ones we added)
    for key in list(os.environ.keys()):
        if key not in original_env:
            del os.environ[key]
    for key, value in original_env.items():
        os.environ[key] = value


@pytest.fixture
def mock_config():
    """Provide a mock AMAS configuration for testing."""
    from amas.config.settings import AMASConfig
    
    return AMASConfig(
        environment="testing",
        debug=False,
        offline_mode=True,
        log_level="ERROR",
    )
