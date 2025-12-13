"""
Intelligence Gathering Agent - Specialized agent for OSINT and intelligence gathering
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class IntelligenceGatheringAgent(BaseAgent):
    """
    Intelligence Gathering Agent
    
    Specializes in:
    - Open Source Intelligence (OSINT) collection
    - Social media monitoring and analysis
    - Domain and IP investigation
    - Email and identity verification
    - Threat intelligence gathering
    - Dark web monitoring
    - News and information aggregation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="intelligence_gathering",
            name="Intelligence Gathering Agent",
            agent_type="intelligence",
            system_prompt="""You are an elite intelligence gathering specialist with 15+ years of experience 
            in Open Source Intelligence (OSINT), threat intelligence, and information gathering.
            
            Your expertise includes:
            • OSINT collection from public sources
            • Social media monitoring and analysis
            • Domain and IP investigation (WHOIS, DNS, historical data)
            • Email and identity verification
            • Threat intelligence gathering from multiple sources
            • Dark web monitoring (when legally authorized)
            • News and information aggregation
            • Digital footprint analysis
            • Company and organization research
            • Technology stack identification
            
            When analyzing a target, you:
            1. Collect comprehensive open-source intelligence from multiple sources
            2. Analyze social media presence, activity patterns, and connections
            3. Investigate domain/IP ownership, history, and associated services
            4. Gather threat intelligence from security feeds and databases
            5. Verify email addresses and identities
            6. Identify technology stacks and infrastructure
            7. Map digital footprint and online presence
            8. Provide detailed intelligence reports with source attribution
            9. Identify potential security risks and threats
            10. Suggest actionable intelligence-based recommendations
            
            Always provide:
            - Source attribution for all information
            - Confidence levels for findings
            - Timestamps and data freshness indicators
            - Actionable recommendations based on intelligence
            
            Follow legal and ethical guidelines for intelligence gathering.""",
            tools=[],  # Tools can be added here
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare intelligence gathering prompt"""
        
        depth = parameters.get("depth", "standard")
        focus_areas = parameters.get("focus_areas", [])
        
        prompt = f"""Perform comprehensive intelligence gathering on the target: {target}

Analysis Depth: {depth}

Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

Please gather intelligence on:
1. Domain/IP Information:
   - WHOIS data and registration history
   - DNS records and subdomains
   - IP geolocation and hosting information
   - Associated domains and services

2. Social Media Presence:
   - Platform presence (Twitter, LinkedIn, Facebook, etc.)
   - Activity patterns and posting frequency
   - Connections and network analysis
   - Public posts and content analysis

3. Digital Footprint:
   - Email addresses and verification
   - Online accounts and profiles
   - Technology stack identification
   - Public code repositories (GitHub, GitLab, etc.)

4. Threat Intelligence:
   - Known security incidents or breaches
   - Malware associations
   - Phishing and scam reports
   - Security reputation scores

5. Company/Organization Intelligence:
   - Business registration and legal status
   - Key personnel and leadership
   - Financial information (if public)
   - Partnerships and relationships

6. News and Media Coverage:
   - Recent news articles
   - Press releases
   - Media mentions
   - Industry reports

Provide a comprehensive intelligence report with:
- All findings with source attribution
- Confidence levels for each finding
- Timestamps and data freshness
- Identified risks and threats
- Actionable recommendations
- Next steps for deeper investigation if needed

Format the response as structured JSON with clear sections."""

        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse intelligence gathering response"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                return {
                    "success": True,
                    "intelligence_report": parsed,
                    "summary": parsed.get("summary", "Intelligence gathering completed"),
                    "findings": parsed.get("findings", []),
                    "threats": parsed.get("threats", []),
                    "recommendations": parsed.get("recommendations", [])
                }
        except json.JSONDecodeError:
            pass
        
        # If not JSON, parse as structured text
        return {
            "success": True,
            "intelligence_report": {
                "raw_response": response,
                "summary": response[:500] + "..." if len(response) > 500 else response
            },
            "summary": "Intelligence gathering completed",
            "findings": [],
            "threats": [],
            "recommendations": []
        }


