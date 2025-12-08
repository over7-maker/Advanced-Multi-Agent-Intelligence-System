"""
Testing Agent - Specialized agent for test generation and quality assurance
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TestingAgent(BaseAgent):
    """
    Testing Agent
    
    Specializes in:
    - Test case generation
    - Test coverage analysis
    - Quality assurance
    - Test automation
    - Bug detection
    """
    
    def __init__(self):
        super().__init__(
            agent_id="testing_agent",
            name="Testing Agent",
            agent_type="testing",
            system_prompt="""You are an expert QA engineer with 15+ years of experience 
            in software testing, test automation, and quality assurance.
            
            Your expertise includes:
            • Unit test generation
            • Integration test design
            • End-to-end test scenarios
            • Test coverage analysis
            • Bug detection and reporting
            • Test automation frameworks
            • Performance testing strategies
            • Security testing approaches
            • Regression testing
            • Test data management
            
            When creating tests, you:
            1. Generate comprehensive test cases covering edge cases
            2. Ensure high test coverage
            3. Write maintainable, readable test code
            4. Follow testing best practices
            5. Include both positive and negative test cases
            
            Always produce high-quality, maintainable tests.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare test generation prompt"""
        
        test_type = parameters.get("test_type", "unit_tests")
        code_content = parameters.get("code", "")
        framework = parameters.get("framework", "pytest")
        language = parameters.get("language", "python")
        
        prompt = f"""Generate {test_type} for: {target}

Test Type: {test_type}
Framework: {framework}
Language: {language}

Code to Test:
{code_content[:5000] if code_content else "No code provided - create general test template"}

Please provide comprehensive tests including:
1. Unit tests for all functions/methods
2. Edge case tests
3. Error handling tests
4. Integration tests (if applicable)
5. Test fixtures and setup
6. Test coverage analysis

Format your response as JSON with the following structure:
{{
    "test_cases": [
        {{
            "name": "...",
            "description": "...",
            "code": "...",
            "expected_result": "...",
            "test_type": "unit|integration|e2e"
        }}
    ],
    "test_coverage": {{
        "functions_covered": X,
        "lines_covered": X,
        "coverage_percentage": X
    }},
    "test_fixtures": "...",
    "test_setup": "...",
    "framework_code": "..."
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
                "tests": result,
                "test_cases_count": len(result.get("test_cases", [])),
                "coverage_percentage": result.get("test_coverage", {}).get("coverage_percentage", 0),
                "has_fixtures": bool(result.get("test_fixtures"))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "tests": {
                    "framework_code": response,
                    "test_cases": []
                },
                "test_cases_count": 0,
                "coverage_percentage": 0,
                "has_fixtures": False
            }

