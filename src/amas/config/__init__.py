"""
AMAS Configuration System

Centralized configuration management for AMAS.
"""

from .settings import AMASConfig, get_settings

__all__ = ["AMASConfig", "get_settings"]