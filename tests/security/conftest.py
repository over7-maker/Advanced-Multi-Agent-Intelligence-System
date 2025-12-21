"""
Security test fixtures and configuration
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_authenticated_user():
    """Mock authenticated user"""
    user = MagicMock()
    user.id = "auth_user_123"
    user.username = "authuser"
    user.email = "auth@example.com"
    user.is_active = True
    user.roles = ["user"]
    return user


@pytest.fixture
def mock_admin_user():
    """Mock admin user"""
    user = MagicMock()
    user.id = "admin_user_123"
    user.username = "admin"
    user.email = "admin@example.com"
    user.is_active = True
    user.roles = ["admin", "user"]
    return user


@pytest.fixture
def mock_unauthenticated_user():
    """Mock unauthenticated user (None)"""
    return None

