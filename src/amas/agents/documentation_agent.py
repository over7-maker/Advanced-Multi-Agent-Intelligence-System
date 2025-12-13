"""
Documentation Agent - Specialized agent for documentation generation and management
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """
    Documentation Agent
    
    Specializes in:
    - Code documentation generation
    - API documentation
    - Technical writing
    - Documentation review
    - User guides creation
    """
    
    def __init__(self):
        super().__init__(
            agent_id="documentation_agent",
            name="Documentation Agent",
            agent_type="documentation",
            system_prompt="""You are an expert technical writer with 15+ years of experience 
            in software documentation, API documentation, and technical communication.
            
            Your expertise includes:
            • Code documentation (docstrings, comments, README files)
            • API documentation (OpenAPI/Swagger specs, endpoint docs)
            • Architecture documentation
            • User guides and tutorials
            • Technical specifications
            • Code examples and snippets
            • Documentation review and improvement
            • Markdown formatting
            • Clear, concise technical writing
            
            When creating documentation, you:
            1. Write clear, concise, and accurate documentation
            2. Include code examples where appropriate
            3. Follow documentation best practices
            4. Ensure documentation is up-to-date
            5. Make documentation accessible to target audience
            
            Always produce high-quality, maintainable documentation.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare documentation generation prompt"""
        
        doc_type = parameters.get("doc_type", "code_documentation")
        code_content = parameters.get("code", "")
        format_type = parameters.get("format", "markdown")
        audience = parameters.get("audience", "developers")
        
        prompt = f"""Generate {doc_type} for: {target}

Documentation Type: {doc_type}
Format: {format_type}
Target Audience: {audience}

Code/Content to Document:
{code_content[:5000] if code_content else "No code provided - create general documentation"}

Please provide comprehensive documentation including:
1. Overview/Introduction
2. Detailed explanation
3. Usage examples
4. API reference (if applicable)
5. Best practices
6. Common pitfalls

Format your response as JSON with the following structure:
{{
    "overview": "...",
    "detailed_documentation": "...",
    "examples": [
        {{
            "title": "...",
            "code": "...",
            "explanation": "..."
        }}
    ],
    "api_reference": {{...}},
    "best_practices": ["...", "..."],
    "common_pitfalls": ["...", "..."],
    "markdown_content": "..."
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
                "documentation": result,
                "has_examples": len(result.get("examples", [])) > 0,
                "has_api_reference": bool(result.get("api_reference")),
                "markdown_length": len(result.get("markdown_content", ""))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response as markdown
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "documentation": {
                    "markdown_content": response,
                    "overview": response[:500]
                },
                "has_examples": False,
                "has_api_reference": False,
                "markdown_length": len(response)
            }

