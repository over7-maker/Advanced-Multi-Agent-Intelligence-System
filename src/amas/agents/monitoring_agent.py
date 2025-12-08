"""
Monitoring Agent - Specialized agent for system monitoring and observability
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent
    
    Specializes in:
    - System monitoring setup
    - Metrics collection
    - Alert configuration
    - Logging strategies
    - Observability best practices
    """
    
    def __init__(self):
        super().__init__(
            agent_id="monitoring_agent",
            name="Monitoring Agent",
            agent_type="monitoring",
            system_prompt="""You are an expert SRE/DevOps engineer with 15+ years of experience 
            in system monitoring, observability, and reliability engineering.
            
            Your expertise includes:
            • Prometheus metrics design
            • Grafana dashboard creation
            • Alert rule configuration
            • Distributed tracing (OpenTelemetry, Jaeger)
            • Log aggregation (ELK, Loki)
            • APM (Application Performance Monitoring)
            • SLI/SLO definition
            • Error tracking and analysis
            • Performance monitoring
            • Capacity planning
            
            When setting up monitoring, you:
            1. Define comprehensive metrics (RED: Rate, Errors, Duration)
            2. Create meaningful dashboards
            3. Configure actionable alerts
            4. Set up proper logging
            5. Implement distributed tracing
            
            Always produce production-ready monitoring configurations.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare monitoring setup prompt"""
        
        monitoring_type = parameters.get("monitoring_type", "application")
        tools = parameters.get("tools", ["prometheus", "grafana"])
        app_info = parameters.get("app_info", {})
        
        prompt = f"""Design monitoring setup for: {target}

Monitoring Type: {monitoring_type}
Tools: {', '.join(tools)}

Application Information:
{json.dumps(app_info, indent=2) if app_info else "No app info provided"}

Please provide comprehensive monitoring configuration including:
1. Key metrics to track (RED metrics: Rate, Errors, Duration)
2. Prometheus metric definitions
3. Grafana dashboard JSON
4. Alert rules configuration
5. Logging strategy
6. Distributed tracing setup
7. SLI/SLO definitions

Format your response as JSON with the following structure:
{{
    "metrics": [
        {{
            "name": "...",
            "type": "counter|gauge|histogram",
            "description": "...",
            "labels": ["...", "..."]
        }}
    ],
    "dashboards": [
        {{
            "name": "...",
            "panels": [...]
        }}
    ],
    "alerts": [
        {{
            "name": "...",
            "condition": "...",
            "severity": "critical|warning|info"
        }}
    ],
    "logging_strategy": "...",
    "tracing_config": "...",
    "sli_slo": {{
        "sli": "...",
        "slo": "..."
    }}
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            result = json.loads(response)
            
            return {
                "success": True,
                "monitoring_config": result,
                "metrics_count": len(result.get("metrics", [])),
                "dashboards_count": len(result.get("dashboards", [])),
                "alerts_count": len(result.get("alerts", []))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "monitoring_config": {
                    "raw_response": response,
                    "metrics": []
                },
                "metrics_count": 0,
                "dashboards_count": 0,
                "alerts_count": 0
            }

