"""
Intelligent Tool Selector
AI-powered tool selection based on task requirements and tool performance
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.amas.agents.tools.tool_categories import (
    ToolCategory,
    ToolMetadata,
    get_tools_by_category,
    get_tool_metadata,
    get_free_tools,
    TOOL_CATEGORY_MAP
)
from src.amas.agents.tools.tool_performance_tracker import get_tool_performance_tracker
from src.amas.agents.tools import get_tool_registry
from src.amas.ai.enhanced_router_class import get_ai_router

logger = logging.getLogger(__name__)


@dataclass
class ToolRecommendation:
    """Tool recommendation with confidence score"""
    tool_name: str
    confidence: float  # 0.0 to 1.0
    reason: str
    execution_mode: str  # parallel, sequential, independent
    estimated_time: float
    estimated_cost: float = 0.0


class IntelligentToolSelector:
    """AI-powered tool selection system"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.performance_tracker = get_tool_performance_tracker()
        self.ai_router = get_ai_router()
        logger.info("IntelligentToolSelector initialized")
    
    async def select_tools(
        self,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        strategy: str = "comprehensive",
        max_tools: int = 5,
        agent_type: Optional[str] = None
    ) -> List[ToolRecommendation]:
        """
        Select optimal tools for a task using AI
        
        Args:
            task_type: Type of task (e.g., "security_scan", "web_research")
            task_description: Description of the task
            parameters: Task parameters
            strategy: Selection strategy (comprehensive, efficient, reliable, cost_optimized)
            max_tools: Maximum number of tools to recommend
            agent_type: Type of agent requesting tools
            
        Returns:
            List of tool recommendations sorted by confidence
        """
        logger.info(
            f"Selecting tools for task: {task_type} "
            f"(strategy={strategy}, max_tools={max_tools})"
        )
        
        # Step 1: Get relevant tool categories based on task type
        relevant_categories = self._infer_categories_from_task(task_type, task_description)
        
        # Step 2: Get available tools in those categories
        candidate_tools = self._get_candidate_tools(relevant_categories, agent_type)
        
        # Step 3: Use AI to analyze and rank tools
        ai_recommendations = await self._ai_analyze_tools(
            task_type,
            task_description,
            parameters,
            candidate_tools,
            strategy
        )
        
        # Step 4: Apply performance metrics to refine recommendations
        refined_recommendations = await self._refine_with_metrics(
            ai_recommendations,
            strategy,
            max_tools
        )
        
        logger.info(
            f"Selected {len(refined_recommendations)} tools: "
            f"{[r.tool_name for r in refined_recommendations]}"
        )
        
        return refined_recommendations
    
    def _infer_categories_from_task(
        self,
        task_type: str,
        task_description: str
    ) -> List[ToolCategory]:
        """Infer relevant tool categories from task"""
        categories = []
        
        # Map task types to categories
        task_category_map = {
            "security_scan": [ToolCategory.SECURITY_ANALYSIS, ToolCategory.NETWORK_ANALYSIS],
            "web_research": [ToolCategory.WEB_RESEARCH],
            "osint": [ToolCategory.OSINT, ToolCategory.WEB_RESEARCH],
            "dark_web": [ToolCategory.DARK_WEB],
            "code_analysis": [ToolCategory.CODE_ANALYSIS, ToolCategory.SECURITY_ANALYSIS],
            "data_analysis": [ToolCategory.DATA_ANALYSIS],
            "intelligence_gathering": [ToolCategory.OSINT, ToolCategory.WEB_RESEARCH, ToolCategory.DARK_WEB],
        }
        
        # Check task type
        task_lower = task_type.lower()
        for key, cats in task_category_map.items():
            if key in task_lower:
                categories.extend(cats)
        
        # Check description keywords
        desc_lower = task_description.lower()
        if any(kw in desc_lower for kw in ["web", "search", "browse", "research"]):
            if ToolCategory.WEB_RESEARCH not in categories:
                categories.append(ToolCategory.WEB_RESEARCH)
        
        if any(kw in desc_lower for kw in ["osint", "asset", "discovery", "fofa", "shodan"]):
            if ToolCategory.OSINT not in categories:
                categories.append(ToolCategory.OSINT)
        
        if any(kw in desc_lower for kw in ["dark web", "tor", "onion", "robin"]):
            if ToolCategory.DARK_WEB not in categories:
                categories.append(ToolCategory.DARK_WEB)
        
        if any(kw in desc_lower for kw in ["security", "vulnerability", "scan", "audit"]):
            if ToolCategory.SECURITY_ANALYSIS not in categories:
                categories.append(ToolCategory.SECURITY_ANALYSIS)
        
        # Default to web research if no categories found
        if not categories:
            categories = [ToolCategory.WEB_RESEARCH]
        
        return list(set(categories))  # Remove duplicates
    
    def _get_candidate_tools(
        self,
        categories: List[ToolCategory],
        agent_type: Optional[str] = None
    ) -> List[str]:
        """Get candidate tools from relevant categories"""
        candidate_tools = []
        
        for category in categories:
            try:
                tools = get_tools_by_category(category)
                candidate_tools.extend(tools)
            except Exception as e:
                logger.warning(f"Failed to get tools for category {category}: {e}")
                # Fallback: get from TOOL_CATEGORY_MAP
                tools = [
                    name for name, metadata in TOOL_CATEGORY_MAP.items()
                    if metadata.category == category
                ]
                candidate_tools.extend(tools)
        
        # Filter by agent preferences if specified
        if agent_type:
            agent_tool_preferences = self._get_agent_tool_preferences(agent_type)
            if agent_tool_preferences:
                # Prioritize agent-preferred tools
                preferred = [t for t in candidate_tools if t in agent_tool_preferences]
                others = [t for t in candidate_tools if t not in agent_tool_preferences]
                candidate_tools = preferred + others
        
        return list(set(candidate_tools))  # Remove duplicates
    
    def _get_agent_tool_preferences(self, agent_type: str) -> List[str]:
        """Get default tool preferences for an agent type"""
        preferences = {
            "security_expert": [
                "virustotal", "shodan", "censys", "nmap", "semgrep",
                "bandit", "trivy", "gitleaks", "owasp_zap", "sonarqube",
                "ssl_analyzer", "abuseipdb"
            ],
            "security": [
                "virustotal", "shodan", "censys", "nmap", "semgrep",
                "bandit", "trivy", "gitleaks", "ssl_analyzer"
            ],
            "web_research": [
                "agenticseek", "searxng", "duckduckgo", "startpage",
                "web_scraper", "api_fetcher", "bing", "brave_search"
            ],
            "search_federation": [
                "searxng", "duckduckgo", "startpage", "bing",
                "brave_search", "qwant", "yandex", "google_cse"
            ],
            "dark_web": [
                "robin", "torbot", "onionscan", "vigilant_onion",
                "onion_ingestor", "onioff"
            ],
            "intelligence_gathering": [
                "fofa", "shodan", "censys", "zoomeye", "netlas",
                "criminal_ip", "web_scraper", "dns_lookup", "whois_lookup"
            ],
            "intelligence": [
                "fofa", "shodan", "censys", "zoomeye", "web_scraper",
                "dns_lookup", "whois_lookup"
            ],
            "osint": [
                "fofa", "shodan", "censys", "zoomeye", "netlas",
                "criminal_ip", "haveibeenpwned"
            ],
            "research": [
                "agenticseek", "searxng", "duckduckgo", "web_scraper",
                "api_fetcher", "github_api", "pypi_package", "npm_package"
            ],
            "code_analysis": [
                "pylint", "flake8", "semgrep", "bandit", "sonarqube",
                "github_api", "gitlab_api"
            ],
            "data_analysis": [
                "polars", "duckdb", "great_expectations"
            ],
            "monitoring": [
                "prometheus", "grafana", "loki", "jaeger", "pyroscope"
            ],
            "testing": [
                "semgrep", "bandit", "trivy", "gitleaks", "osv_scanner"
            ],
            "deployment": [
                "prometheus", "grafana", "loki", "jaeger"
            ],
            "performance": [
                "prometheus", "grafana", "pyroscope"
            ],
            "documentation": [
                "web_scraper", "api_fetcher", "github_api"
            ],
            "integration": [
                "api_fetcher", "web_scraper"
            ],
        }
        
        agent_lower = agent_type.lower()
        for key, tools in preferences.items():
            if key in agent_lower:
                return tools
        
        return []
    
    async def _ai_analyze_tools(
        self,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        candidate_tools: List[str],
        strategy: str
    ) -> List[ToolRecommendation]:
        """Use AI to analyze and rank tools"""
        
        # Get tool metadata for candidates
        tool_info = []
        for tool_name in candidate_tools[:20]:  # Limit to 20 for AI analysis
            metadata = get_tool_metadata(tool_name)
            if metadata:
                tool_info.append({
                    "name": tool_name,
                    "category": metadata.category.value,
                    "description": metadata.description,
                    "execution_mode": metadata.execution_mode.value,
                    "cost_tier": metadata.cost_tier,
                    "avg_execution_time": metadata.avg_execution_time,
                })
        
        # Create AI prompt
        prompt = f"""Analyze the following task and recommend the best tools to use.

Task Type: {task_type}
Task Description: {task_description}
Task Parameters: {parameters}
Selection Strategy: {strategy}

Available Tools:
{self._format_tool_info(tool_info)}

Selection Strategies:
- comprehensive: Use multiple tools for maximum coverage and accuracy
- efficient: Use minimal tools for speed
- reliable: Use tools with highest success rates
- cost_optimized: Prefer free/local tools

For each recommended tool, provide:
1. Tool name
2. Confidence score (0.0-1.0)
3. Reason for selection
4. Execution mode (parallel, sequential, or independent)
5. Estimated execution time in seconds

Return a JSON list of recommendations, sorted by confidence (highest first).
Format:
[
  {{
    "tool_name": "tool_name",
    "confidence": 0.95,
    "reason": "Why this tool is recommended",
    "execution_mode": "parallel",
    "estimated_time": 5.0
  }}
]

Limit to top 5-7 tools based on the strategy."""

        try:
            # Call AI router
            response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=None,
                max_tokens=2000,
                temperature=0.3,
                system_prompt="You are an expert at selecting the right tools for tasks. Provide clear, actionable recommendations.",
                strategy="quality_first"
            )
            
            # Parse AI response
            recommendations = self._parse_ai_response(response.content, candidate_tools)
            
            return recommendations
        
        except Exception as e:
            logger.warning(f"AI tool selection failed: {e}, falling back to rule-based selection")
            return self._fallback_selection(candidate_tools, strategy)
    
    def _format_tool_info(self, tool_info: List[Dict]) -> str:
        """Format tool information for AI prompt"""
        lines = []
        for tool in tool_info:
            lines.append(
                f"- {tool['name']}: {tool['description']} "
                f"(Category: {tool['category']}, "
                f"Mode: {tool['execution_mode']}, "
                f"Cost: {tool['cost_tier']}, "
                f"Time: {tool['avg_execution_time']}s)"
            )
        return "\n".join(lines)
    
    def _parse_ai_response(
        self,
        response: str,
        candidate_tools: List[str]
    ) -> List[ToolRecommendation]:
        """Parse AI response into tool recommendations"""
        import json
        import re
        
        recommendations = []
        
        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                for item in data:
                    tool_name = item.get("tool_name", "")
                    if tool_name in candidate_tools:
                        recommendations.append(ToolRecommendation(
                            tool_name=tool_name,
                            confidence=float(item.get("confidence", 0.5)),
                            reason=item.get("reason", "AI recommended"),
                            execution_mode=item.get("execution_mode", "parallel"),
                            estimated_time=float(item.get("estimated_time", 5.0)),
                            estimated_cost=float(item.get("estimated_cost", 0.0))
                        ))
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        # If parsing failed, use fallback
        if not recommendations:
            return self._fallback_selection(candidate_tools, "comprehensive")
        
        return recommendations
    
    def _fallback_selection(
        self,
        candidate_tools: List[str],
        strategy: str
    ) -> List[ToolRecommendation]:
        """Fallback rule-based tool selection"""
        recommendations = []
        
        # Get free tools first if cost-optimized
        if strategy == "cost_optimized":
            free_tools = get_free_tools()
            candidate_tools = [t for t in candidate_tools if t in free_tools] + \
                            [t for t in candidate_tools if t not in free_tools]
        
        # Select top tools
        for i, tool_name in enumerate(candidate_tools[:7]):
            metadata = get_tool_metadata(tool_name)
            if metadata:
                confidence = 0.9 - (i * 0.1)  # Decreasing confidence
                recommendations.append(ToolRecommendation(
                    tool_name=tool_name,
                    confidence=max(0.5, confidence),
                    reason=f"Rule-based selection ({strategy} strategy)",
                    execution_mode=metadata.execution_mode.value,
                    estimated_time=metadata.avg_execution_time,
                    estimated_cost=0.0 if metadata.cost_tier == "free" else 0.01
                ))
        
        return recommendations
    
    async def _refine_with_metrics(
        self,
        recommendations: List[ToolRecommendation],
        strategy: str,
        max_tools: int
    ) -> List[ToolRecommendation]:
        """Refine recommendations using performance metrics"""
        refined = []
        
        for rec in recommendations:
            # Get performance metrics
            metrics = await self.performance_tracker.get_metrics(rec.tool_name)
            
            if metrics and metrics.total_executions > 0:
                # Adjust confidence based on success rate
                if strategy == "reliable":
                    rec.confidence *= metrics.success_rate
                
                # Adjust estimated time based on actual average
                if metrics.avg_execution_time > 0:
                    rec.estimated_time = metrics.avg_execution_time
                
                # Adjust cost based on actual average
                if metrics.avg_cost > 0:
                    rec.estimated_cost = metrics.avg_cost
                
                # Add reliability info to reason
                rec.reason += f" (Success rate: {metrics.success_rate:.1%})"
            
            refined.append(rec)
        
        # Sort by confidence and limit
        refined.sort(key=lambda r: r.confidence, reverse=True)
        return refined[:max_tools]


# Global selector instance
_selector: Optional[IntelligentToolSelector] = None


def get_intelligent_tool_selector() -> IntelligentToolSelector:
    """Get the global intelligent tool selector"""
    global _selector
    if _selector is None:
        _selector = IntelligentToolSelector()
    return _selector


__all__ = [
    'ToolRecommendation',
    'IntelligentToolSelector',
    'get_intelligent_tool_selector',
]

