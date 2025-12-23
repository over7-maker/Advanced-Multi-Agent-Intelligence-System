"""
Performance Agent - Specialized agent for performance analysis and optimization
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PerformanceAgent(BaseAgent):
    """
    Performance Agent
    
    Specializes in:
    - Performance analysis
    - Bottleneck identification
    - Optimization recommendations
    - Resource usage analysis
    - Scalability assessment
    """
    
    def __init__(self):
        super().__init__(
            agent_id="performance_agent",
            name="Performance Agent",
            agent_type="performance",
            system_prompt="""You are an expert performance engineer with 15+ years of experience 
            in system optimization, performance analysis, and scalability engineering.
            
            Your expertise includes:
            • Performance profiling and bottleneck identification
            • Database query optimization
            • API response time optimization
            • Memory and CPU usage analysis
            • Caching strategy recommendations
            • Load balancing and scaling strategies
            • Network performance optimization
            • Code-level performance improvements
            • Resource utilization analysis
            • Capacity planning
            
            When analyzing performance, you:
            1. Identify specific bottlenecks with metrics
            2. Provide optimization recommendations with expected impact
            3. Suggest caching strategies where appropriate
            4. Recommend scaling approaches
            5. Prioritize optimizations by impact vs effort
            
            Always provide actionable, data-driven recommendations.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare performance analysis prompt"""
        
        task_type = parameters.get("task_type", "performance_analysis")
        metrics = parameters.get("metrics", {})
        context = parameters.get("context", {})
        
        prompt = f"""Analyze the performance of: {target}

Task Type: {task_type}

Current Metrics:
{json.dumps(metrics, indent=2) if metrics else "No metrics provided"}

Context:
{json.dumps(context, indent=2) if context else "No additional context"}

Please provide:
1. Performance bottlenecks identified
2. Root cause analysis
3. Optimization recommendations with expected impact
4. Priority ranking (High/Medium/Low)
5. Implementation effort estimate
6. Expected performance improvement percentage

Format your response as JSON with the following structure:
{{
    "bottlenecks": [
        {{
            "name": "...",
            "severity": "Critical|High|Medium|Low",
            "impact": "...",
            "location": "..."
        }}
    ],
    "optimizations": [
        {{
            "recommendation": "...",
            "impact": "High|Medium|Low",
            "effort": "High|Medium|Low",
            "expected_improvement": "X%",
            "implementation_steps": ["...", "..."]
        }}
    ],
    "summary": "...",
    "priority_actions": ["...", "..."]
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
                "analysis": result,
                "bottlenecks_count": len(result.get("bottlenecks", [])),
                "optimizations_count": len(result.get("optimizations", [])),
                "critical_issues": [
                    b for b in result.get("bottlenecks", [])
                    if b.get("severity") in ["Critical", "High"]
                ]
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "analysis": {"raw_response": response},
                "bottlenecks_count": 0,
                "optimizations_count": 0
            }

