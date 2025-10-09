#!/usr/bin/env python3
"""
AMAS Intelligence Package
Collective learning, adaptive personalities, and predictive intelligence
"""

from ..agents.adaptive_personality import (
    AdaptiveAgentPersonality,
    PersonalityOrchestrator,
)
from .collective_learning import (
    CollectiveIntelligenceEngine,
    CollectiveIntelligenceManager,
)
from .intelligence_manager import AMASIntelligenceManager, intelligence_manager
from .predictive_engine import PredictiveIntelligenceEngine

__all__ = [
    "CollectiveIntelligenceEngine",
    "CollectiveIntelligenceManager",
    "AdaptiveAgentPersonality",
    "PersonalityOrchestrator",
    "PredictiveIntelligenceEngine",
    "AMASIntelligenceManager",
    "intelligence_manager",
]
