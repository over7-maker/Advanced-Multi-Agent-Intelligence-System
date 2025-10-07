"""
AMAS API Module

This module provides REST API interfaces for the AMAS system,
including FastAPI and Flask-based dashboard APIs for monitoring and management.
"""

from .main import app
from .dashboard_api import DashboardAPI, create_dashboard_api

__all__ = [
    'app',
    'DashboardAPI',
    'create_dashboard_api'
]
