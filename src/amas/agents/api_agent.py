"""
API Agent - Specialized agent for API design and integration
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class APIAgent(BaseAgent):
    """
    API Agent
    
    Specializes in:
    - API design
    - RESTful API best practices
    - API documentation
    - API testing
    - Integration patterns
    """
    
    def __init__(self):
        super().__init__(
            agent_id="api_agent",
            name="API Agent",
            agent_type="api",
            system_prompt="""You are an expert API architect with 15+ years of experience 
            in API design, RESTful services, and API integration.
            
            Your expertise includes:
            • RESTful API design principles
            • OpenAPI/Swagger specification
            • GraphQL API design
            • API versioning strategies
            • Authentication and authorization (OAuth2, JWT)
            • Rate limiting and throttling
            • API documentation
            • API testing strategies
            • Integration patterns
            • Microservices communication
            
            When designing APIs, you:
            1. Follow RESTful best practices
            2. Design clear, consistent endpoints
            3. Include proper error handling
            4. Implement security best practices
            5. Provide comprehensive documentation
            
            Always produce production-ready API designs.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare API design prompt"""
        
        api_type = parameters.get("api_type", "rest")
        requirements = parameters.get("requirements", {})
        existing_api = parameters.get("existing_api", "")
        
        prompt = f"""Design/Review API for: {target}

API Type: {api_type}

Requirements:
{json.dumps(requirements, indent=2) if requirements else "No specific requirements"}

Existing API (if reviewing):
{existing_api[:3000] if existing_api else "New API design"}

Please provide comprehensive API design including:
1. Endpoint definitions with HTTP methods
2. Request/Response schemas
3. Authentication requirements
4. Error handling approach
5. Rate limiting strategy
6. OpenAPI/Swagger specification
7. Example requests/responses

Format your response as JSON with the following structure:
{{
    "endpoints": [
        {{
            "path": "...",
            "method": "GET|POST|PUT|DELETE",
            "description": "...",
            "request_schema": {{...}},
            "response_schema": {{...}},
            "authentication": "...",
            "examples": {{...}}
        }}
    ],
    "openapi_spec": "...",
    "authentication": "...",
    "rate_limiting": "...",
    "error_codes": {{...}}
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
                "api_design": result,
                "endpoints_count": len(result.get("endpoints", [])),
                "has_openapi_spec": bool(result.get("openapi_spec")),
                "has_authentication": bool(result.get("authentication"))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "api_design": {
                    "raw_response": response,
                    "endpoints": []
                },
                "endpoints_count": 0,
                "has_openapi_spec": False,
                "has_authentication": False
            }

