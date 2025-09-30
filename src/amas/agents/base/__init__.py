"""
Base Intelligence Agent Classes

This module contains the base classes for all intelligence agents in the AMAS system.
"""

from .intelligence_agent import IntelligenceAgent
from .react_agent import ReactAgent
from .agent_communication import AgentCommunication

__all__ = [
    'IntelligenceAgent',
    'ReactAgent',
    'AgentCommunication'
]
