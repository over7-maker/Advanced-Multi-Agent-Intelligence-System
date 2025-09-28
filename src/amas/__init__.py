"""
AMAS - Advanced Multi-Agent Intelligence System

A sophisticated autonomous AI system designed for complete offline operation
with enterprise-grade security and performance.
"""

__version__ = "1.0.0"
__author__ = "AMAS Development Team"
__email__ = "team@amas.ai"
__license__ = "MIT"

from .core.orchestrator import IntelligenceOrchestrator
from .services.service_manager import ServiceManager
from .config.settings import AMASConfig

__all__ = [
    "IntelligenceOrchestrator",
    "ServiceManager", 
    "AMASConfig",
    "__version__"
]