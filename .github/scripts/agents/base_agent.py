#!/usr/bin/env python3
"""
Base Agent Framework
Common interface for all 7 autonomous agents in PR #274
"""

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_orchestrator import AIOrchestrator


@dataclass
class AgentMetrics:
    """Metrics collected by agent"""
    agent_name: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: int = 0
    last_execution: Optional[str] = None
    errors: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for all autonomous agents"""
    
    def __init__(self, name: str, orchestrator: Optional[AIOrchestrator] = None):
        self.name = name
        self.orchestrator = orchestrator or AIOrchestrator(cache_enabled=True)
        self.metrics = AgentMetrics(agent_name=name)
        self.initialized = False
        self.metrics_dir = Path(".github/data/agent_metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def initialize(self) -> Dict[str, Any]:
        """Initialize agent - must be implemented by subclass"""
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's main task - must be implemented by subclass"""
        pass
    
    async def monitor(self) -> Dict[str, Any]:
        """Monitor agent health and status"""
        return {
            "agent_name": self.name,
            "initialized": self.initialized,
            "metrics": {
                "execution_count": self.metrics.execution_count,
                "success_count": self.metrics.success_count,
                "failure_count": self.metrics.failure_count,
                "success_rate": (
                    self.metrics.success_count / self.metrics.execution_count
                    if self.metrics.execution_count > 0 else 0
                ),
                "avg_duration_ms": (
                    self.metrics.total_duration_ms / self.metrics.execution_count
                    if self.metrics.execution_count > 0 else 0
                ),
                "last_execution": self.metrics.last_execution
            }
        }
    
    async def cleanup(self) -> Dict[str, Any]:
        """Cleanup agent resources"""
        # Save metrics before cleanup
        self._save_metrics()
        return {
            "agent_name": self.name,
            "status": "cleaned_up",
            "final_metrics": {
                "execution_count": self.metrics.execution_count,
                "success_count": self.metrics.success_count,
                "failure_count": self.metrics.failure_count
            }
        }
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent with full lifecycle"""
        start_time = datetime.now()
        
        try:
            # Initialize if not already done
            if not self.initialized:
                init_result = await self.initialize()
                if not init_result.get("success", False):
                    return {
                        "success": False,
                        "error": f"Initialization failed: {init_result.get('error', 'Unknown error')}",
                        "agent": self.name
                    }
                self.initialized = True
            
            # Execute main task
            result = await self.execute(context)
            
            # Update metrics
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.metrics.execution_count += 1
            if result.get("success", False):
                self.metrics.success_count += 1
            else:
                self.metrics.failure_count += 1
                if "error" in result:
                    self.metrics.errors.append(result["error"])
            self.metrics.total_duration_ms += duration_ms
            self.metrics.last_execution = datetime.now().isoformat()
            
            # Save metrics
            self._save_metrics()
            
            return {
                **result,
                "agent": self.name,
                "duration_ms": duration_ms
            }
        
        except Exception as e:
            self.metrics.execution_count += 1
            self.metrics.failure_count += 1
            self.metrics.errors.append(str(e))
            self._save_metrics()
            
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def _save_metrics(self) -> None:
        """Save agent metrics to file"""
        try:
            metric_file = self.metrics_dir / f"{self.name}_metrics.json"
            with open(metric_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "agent_name": self.metrics.agent_name,
                    "execution_count": self.metrics.execution_count,
                    "success_count": self.metrics.success_count,
                    "failure_count": self.metrics.failure_count,
                    "total_duration_ms": self.metrics.total_duration_ms,
                    "last_execution": self.metrics.last_execution,
                    "errors": self.metrics.errors[-10:]  # Keep last 10 errors
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently fail if metrics save fails
    
    async def _call_ai(self, task_type: str, system_message: str, user_prompt: str) -> Dict[str, Any]:
        """Helper method to call AI orchestrator"""
        return await self.orchestrator.execute(
            task_type=task_type,
            system_message=system_message,
            user_prompt=user_prompt
        )
