"""
AMAS Intelligence Core Components

This package contains the core components for the AMAS Intelligence System,
including the orchestrator, agentic RAG, prompt maker, and workflow engine.
"""

from .orchestrator import IntelligenceOrchestrator
from .agentic_rag import AgenticRAG

__all__ = [
    'IntelligenceOrchestrator',
    'AgenticRAG'
]

__version__ = "1.0.0"