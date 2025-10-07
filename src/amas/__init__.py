"""
AMAS - Advanced Multi-Agent Intelligence System

A sophisticated autonomous AI system designed for complete offline operation
with enterprise-grade security and performance.
"""

__version__ = "1.0.0"
__author__ = "AMAS Development Team"
__email__ = "team@amas.ai"
__license__ = "MIT"

from .config.settings import AMASConfig
from .core.unified_orchestrator_v2 import UnifiedOrchestratorV2
from .services.service_manager import ServiceManager

__all__ = [
    "UnifiedOrchestratorV2",
    "ServiceManager",
    "AMASConfig",
    "__version__",
]
