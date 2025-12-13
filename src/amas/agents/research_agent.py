"""
Research Agent - Specialized agent for research and information gathering
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent
    
    Specializes in:
    - Technical research
    - Information synthesis
    - Literature review
    - Technology evaluation
    - Best practices research
    """
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent",
            name="Research Agent",
            agent_type="research",
            system_prompt="""You are an expert researcher with 15+ years of experience 
            in technical research, information synthesis, and technology evaluation.
            
            Your expertise includes:
            • Technical research methodologies
            • Information gathering and synthesis
            • Literature review
            • Technology stack evaluation
            • Best practices research
            • Competitive analysis
            • Trend analysis
            • Academic paper analysis
            • Documentation review
            • Knowledge synthesis
            
            When conducting research, you:
            1. Gather information from multiple sources
            2. Synthesize findings clearly
            3. Provide citations and references
            4. Evaluate pros and cons
            5. Make evidence-based recommendations
            
            Always produce thorough, well-researched reports.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare research prompt"""
        
        research_topic = parameters.get("research_topic", target)
        research_type = parameters.get("research_type", "technology_evaluation")
        scope = parameters.get("scope", "comprehensive")
        sources = parameters.get("sources", [])
        
        prompt = f"""Conduct research on: {research_topic}

Research Type: {research_type}
Scope: {scope}

Sources to Consider:
{json.dumps(sources, indent=2) if sources else "Use general knowledge and best practices"}

Please provide comprehensive research report including:
1. Executive summary
2. Key findings
3. Detailed analysis
4. Pros and cons evaluation
5. Best practices identified
6. Recommendations
7. References and sources

Format your response as JSON with the following structure:
{{
    "executive_summary": "...",
    "key_findings": ["...", "..."],
    "detailed_analysis": "...",
    "pros_cons": {{
        "pros": ["...", "..."],
        "cons": ["...", "..."]
    }},
    "best_practices": ["...", "..."],
    "recommendations": ["...", "..."],
    "references": ["...", "..."]
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
                "research_report": result,
                "findings_count": len(result.get("key_findings", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "has_references": len(result.get("references", [])) > 0
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "research_report": {
                    "executive_summary": response[:500],
                    "detailed_analysis": response,
                    "key_findings": []
                },
                "findings_count": 0,
                "recommendations_count": 0,
                "has_references": False
            }

