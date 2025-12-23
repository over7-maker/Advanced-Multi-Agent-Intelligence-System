"""
Security Expert Agent - Specialized agent for security analysis
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SecurityExpertAgent(BaseAgent):
    """
    Security Expert Agent
    
    Specializes in:
    - Vulnerability assessment
    - Security auditing
    - Penetration testing
    - Threat analysis
    """
    
    def __init__(self):
        super().__init__(
            agent_id="security_expert",
            name="Security Expert",
            agent_type="security",
            system_prompt="""You are an elite cybersecurity expert with 15+ years of experience 
            in penetration testing, vulnerability assessment, and security auditing.
            
            Your expertise includes:
            • OWASP Top 10 vulnerabilities
            • Network security analysis
            • Web application security
            • API security testing
            • SSL/TLS configuration review
            • Security header analysis
            • Common vulnerability detection (SQL injection, XSS, CSRF, etc.)
            
            When analyzing a target, you:
            1. Perform comprehensive security assessment
            2. Identify specific vulnerabilities with CVE references when applicable
            3. Provide severity ratings (Critical, High, Medium, Low)
            4. Suggest concrete remediation steps
            5. Prioritize findings by risk
            
            Always provide actionable, technical recommendations.""",
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
        """Prepare security analysis prompt"""
        
        depth = parameters.get("depth", "standard")
        
        prompt = f"""Perform a comprehensive security analysis of the target: {target}

Analysis Depth: {depth}

Please analyze:
1. Port scanning results (if URL/domain)
2. SSL/TLS configuration
3. Security headers (X-Frame-Options, CSP, HSTS, etc.)
4. Common vulnerabilities (OWASP Top 10)
5. Technology stack identification
6. Known CVEs for detected technologies
7. Configuration issues
8. Potential attack vectors

Provide results in the following JSON format:
{{
    "vulnerabilities": [
        {{
            "id": "VULN-001",
            "severity": "Critical|High|Medium|Low",
            "title": "SQL Injection in Login Form",
            "description": "Detailed description",
            "location": "Specific location",
            "cwe": "CWE-89",
            "cvss_score": 9.8,
            "remediation": "Concrete fix steps"
        }}
    ],
    "ssl_analysis": {{
        "valid": true,
        "expires": "2026-01-15",
        "issues": []
    }},
    "security_headers": {{
        "present": ["X-Frame-Options", "HSTS"],
        "missing": ["Content-Security-Policy"],
        "issues": []
    }},
    "technology_stack": {{
        "server": "Apache 2.4.52",
        "backend": "PHP 8.1",
        "framework": "WordPress 6.2",
        "known_cves": ["CVE-2023-XXXX"]
    }},
    "summary": "Overall security assessment",
    "risk_rating": "Critical|High|Medium|Low",
    "recommendations": ["Action 1", "Action 2"]
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            # AI might wrap JSON in markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            
            return {
                "success": True,
                "data": parsed,
                "raw_response": response
            }
        
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw text
            logger.warning("Failed to parse JSON response, returning raw text")
            
            return {
                "success": True,
                "data": {
                    "vulnerabilities": [],
                    "summary": response,
                    "parsing_error": True
                },
                "raw_response": response
            }

