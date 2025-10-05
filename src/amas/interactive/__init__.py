"""
AMAS Interactive Command Interface

Advanced Multi-Agent Intelligence System - Interactive Mode
Next-generation AI-powered command interface with natural language processing,
real-time agent coordination, and comprehensive task management.
"""

__version__ = "2.0.0"
__author__ = "AMAS Development Team"

from .core.interactive_cli import AMASInteractiveCLI
from .core.command_processor import CommandProcessor
from .core.agent_coordinator import AgentCoordinator
from .core.task_manager import TaskManager
from .core.visual_interface import VisualInterface
from .ai.nlp_engine import NLPEngine
from .ai.intent_classifier import IntentClassifier
from .ai.context_manager import ContextManager
from .agents.enhanced_orchestrator import EnhancedOrchestrator
from .utils.config_manager import ConfigManager
from .utils.logger import InteractiveLogger

__all__ = [
    "AMASInteractiveCLI",
    "CommandProcessor", 
    "AgentCoordinator",
    "TaskManager",
    "VisualInterface",
    "NLPEngine",
    "IntentClassifier",
    "ContextManager",
    "EnhancedOrchestrator",
    "ConfigManager",
    "InteractiveLogger"
]