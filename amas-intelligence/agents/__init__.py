"""
AMAS Intelligence Agents Package

This package contains specialized intelligence agents for the AMAS system.
Each agent is designed for specific intelligence tasks and follows the ReAct framework.
"""

from .base.intelligence_agent import IntelligenceAgent
from .base.react_agent import ReactAgent
from .osint.osint_agent import OSINTAgent
from .investigation.investigation_agent import InvestigationAgent
from .forensics.forensics_agent import ForensicsAgent
from .data_analysis.data_analysis_agent import DataAnalysisAgent
from .reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from .metadata.metadata_agent import MetadataAgent
from .reporting.reporting_agent import ReportingAgent

__all__ = [
    'IntelligenceAgent',
    'ReactAgent',
    'OSINTAgent',
    'InvestigationAgent',
    'ForensicsAgent',
    'DataAnalysisAgent',
    'ReverseEngineeringAgent',
    'MetadataAgent',
    'ReportingAgent'
]

__version__ = "1.0.0"
__author__ = "AMAS Intelligence Team"