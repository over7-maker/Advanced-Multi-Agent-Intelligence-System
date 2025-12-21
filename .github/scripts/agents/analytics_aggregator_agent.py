#!/usr/bin/env python3
"""
Agent-6: Analytics Aggregator
Unified metrics and AI-driven insights
"""

from pathlib import Path
from typing import Any, Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.amas.agents.base.base_agent import BaseAgent


class AnalyticsAggregatorAgent(BaseAgent):
    """Agent-6: Unified metrics and AI-driven insights"""
    
    def __init__(self, orchestrator=None):
        super().__init__("analytics_aggregator", orchestrator)
        self.metrics_sources = []
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize metrics aggregation"""
        # Identify metrics sources
        metrics_dir = Path(".github/data/metrics")
        if metrics_dir.exists():
            self.metrics_sources = [str(f) for f in metrics_dir.glob("*.jsonl")]
        
        return {
            "success": True,
            "metrics_sources": len(self.metrics_sources),
            "message": f"Found {len(self.metrics_sources)} metrics sources"
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analytics aggregation"""
        time_range = context.get("time_range", "24h")
        metrics_types = context.get("metrics_types", ["all"])
        
        # Use AI for analytics insights
        system_message = """You are an analytics expert. Analyze metrics and provide:
1. Key performance indicators
2. Trends and patterns
3. Anomalies and outliers
4. Actionable insights
5. Predictions and forecasts"""
        
        user_prompt = f"""Analytics Request:
Time Range: {time_range}
Metrics Types: {', '.join(metrics_types)}
Metrics Sources: {len(self.metrics_sources)} files

Provide comprehensive analytics and insights."""
        
        ai_result = await self._call_ai(
            task_type="general",
            system_message=system_message,
            user_prompt=user_prompt
        )
        
        if not ai_result.get("success"):
            return {
                "success": False,
                "error": "AI analytics failed"
            }
        
        analytics_result = ai_result.get("response", "")
        
        return {
            "success": True,
            "analytics_report": analytics_result,
            "metrics_aggregated": len(self.metrics_sources)
        }
