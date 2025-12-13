"""
Integration Agent - Specialized agent for platform integrations and connectors
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class IntegrationAgent(BaseAgent):
    """
    Integration Agent
    
    Specializes in:
    - Platform integrations
    - API connectors
    - Webhook handling
    - Data synchronization
    - Integration patterns
    """
    
    def __init__(self):
        super().__init__(
            agent_id="integration_agent",
            name="Integration Agent",
            agent_type="integration",
            system_prompt="""You are an expert integration engineer with 15+ years of experience 
            in platform integrations, API connectors, and system integration patterns.
            
            Your expertise includes:
            • REST API integrations
            • Webhook implementations
            • OAuth2 authentication flows
            • Data synchronization patterns
            • ETL (Extract, Transform, Load) processes
            • Message queue integrations
            • Third-party service connectors
            • Integration testing
            • Error handling and retry logic
            • Rate limiting and throttling
            
            When designing integrations, you:
            1. Follow integration best practices
            2. Implement proper error handling
            3. Include retry logic with exponential backoff
            4. Handle rate limiting gracefully
            5. Ensure data consistency
            
            Always produce production-ready integration code.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare integration design prompt"""
        
        platform = parameters.get("platform", target)
        integration_type = parameters.get("integration_type", "api")
        requirements = parameters.get("requirements", {})
        existing_code = parameters.get("existing_code", "")
        
        prompt = f"""Design integration for: {platform}

Integration Type: {integration_type}

Requirements:
{json.dumps(requirements, indent=2) if requirements else "No specific requirements"}

Existing Code (if reviewing):
{existing_code[:3000] if existing_code else "New integration"}

Please provide comprehensive integration design including:
1. Authentication/Authorization setup
2. API client implementation
3. Webhook handling (if applicable)
4. Error handling and retry logic
5. Rate limiting implementation
6. Data transformation logic
7. Testing strategy

Format your response as JSON with the following structure:
{{
    "authentication": {{
        "type": "oauth2|api_key|basic",
        "implementation": "..."
    }},
    "api_client": "...",
    "webhook_handler": "...",
    "error_handling": {{
        "retry_strategy": "...",
        "error_codes": {{...}}
    }},
    "rate_limiting": "...",
    "data_transformation": "...",
    "test_code": "..."
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
                "integration_design": result,
                "has_authentication": bool(result.get("authentication")),
                "has_api_client": bool(result.get("api_client")),
                "has_webhook_handler": bool(result.get("webhook_handler")),
                "has_error_handling": bool(result.get("error_handling"))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "integration_design": {
                    "raw_response": response,
                    "api_client": response
                },
                "has_authentication": False,
                "has_api_client": True,
                "has_webhook_handler": False,
                "has_error_handling": False
            }

