"""
Unified Orchestrator - Compatibility Layer

This module provides backward compatibility for the refactored orchestrator.
The implementation has been moved to unified_orchestrator_v2.py as part of PR #162
integration fixes.

Key improvements:
- Fixed API endpoint references
- Enhanced orchestrator initialization with proper error handling
- Implemented graceful service shutdown logic
"""

# Import everything from the new implementation
from .unified_orchestrator_v2 import *

# Maintain backward compatibility
__all__ = ['UnifiedOrchestratorV2']

# Alias for backward compatibility
UnifiedOrchestrator = UnifiedOrchestratorV2