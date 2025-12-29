"""
API Agent - Specialized agent for API design and integration
Implements PART_3 requirements
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser

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
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.api_tools = []
    
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
    
    async def _generate_openapi_spec(self, endpoints: List[Dict[str, Any]], api_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate OpenAPI 3.0 specification from endpoints
        """
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": api_info.get("title", "API"),
                "version": api_info.get("version", "1.0.0"),
                "description": api_info.get("description", ""),
                "contact": api_info.get("contact", {}),
                "license": api_info.get("license", {})
            },
            "servers": api_info.get("servers", [
                {"url": "https://api.example.com", "description": "Production server"}
            ]),
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            },
            "security": []
        }
        
        try:
            logger.info(f"APIAgent: Generating OpenAPI spec for {len(endpoints)} endpoints")
            
            # Process each endpoint
            for endpoint in endpoints:
                path = endpoint.get("path", "")
                method = endpoint.get("method", "GET").lower()
                
                if path not in openapi_spec["paths"]:
                    openapi_spec["paths"][path] = {}
                
                # Build operation
                operation = {
                    "summary": endpoint.get("summary", endpoint.get("description", "")),
                    "description": endpoint.get("description", ""),
                    "operationId": endpoint.get("operation_id", f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"),
                    "tags": endpoint.get("tags", []),
                    "responses": {}
                }
                
                # Request body
                if method in ["post", "put", "patch"]:
                    request_schema = endpoint.get("request_schema", {})
                    if request_schema:
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": request_schema
                                    }
                                }
                            }
                        }
                
                # Parameters (path, query)
                parameters = []
                if "{" in path:
                    # Extract path parameters
                    import re
                    path_params = re.findall(r'\{(\w+)\}', path)
                    for param in path_params:
                        parameters.append({
                            "name": param,
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        })
                
                query_params = endpoint.get("query_parameters", [])
                for param in query_params:
                    parameters.append({
                        "name": param.get("name", ""),
                        "in": "query",
                        "required": param.get("required", False),
                        "schema": {"type": param.get("type", "string")},
                        "description": param.get("description", "")
                    })
                
                if parameters:
                    operation["parameters"] = parameters
                
                # Responses
                response_schema = endpoint.get("response_schema", {})
                operation["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": response_schema
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request"
                    },
                    "401": {
                        "description": "Unauthorized"
                    },
                    "404": {
                        "description": "Not Found"
                    },
                    "500": {
                        "description": "Internal Server Error"
                    }
                }
                
                # Security
                auth = endpoint.get("authentication")
                if auth:
                    if "bearer" in auth.lower() or "jwt" in auth.lower():
                        operation["security"] = [{"bearerAuth": []}]
                    elif "oauth" in auth.lower():
                        operation["security"] = [{"oauth2": []}]
                
                openapi_spec["paths"][path][method] = operation
            
            # Add security schemes
            if any("bearer" in str(endpoint.get("authentication", "")).lower() for endpoint in endpoints):
                openapi_spec["components"]["securitySchemes"]["bearerAuth"] = {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            
            if any("oauth" in str(endpoint.get("authentication", "")).lower() for endpoint in endpoints):
                openapi_spec["components"]["securitySchemes"]["oauth2"] = {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": "https://example.com/oauth/authorize",
                            "tokenUrl": "https://example.com/oauth/token",
                            "scopes": {}
                        }
                    }
                }
            
            logger.info(f"APIAgent: Generated OpenAPI spec with {len(openapi_spec['paths'])} paths")
        
        except Exception as e:
            logger.error(f"APIAgent: OpenAPI spec generation failed: {e}", exc_info=True)
            openapi_spec["error"] = str(e)
        
        return openapi_spec
    
    async def _review_api_design(self, api_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review API design for best practices and issues
        """
        review = {
            "score": 0.0,
            "strengths": [],
            "issues": [],
            "recommendations": [],
            "best_practices": [],
            "security_concerns": []
        }
        
        try:
            logger.info("APIAgent: Reviewing API design")
            
            endpoints = api_design.get("endpoints", [])
            score = 100.0
            
            # Check RESTful conventions
            for endpoint in endpoints:
                path = endpoint.get("path", "")
                method = endpoint.get("method", "").upper()
                
                # Path naming
                if not path.startswith("/"):
                    review["issues"].append(f"Path '{path}' should start with '/'")
                    score -= 2
                elif path.count("//") > 0:
                    review["issues"].append(f"Path '{path}' contains double slashes")
                    score -= 1
                
                # HTTP method usage
                if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                    review["issues"].append(f"Invalid HTTP method '{method}' for path '{path}'")
                    score -= 5
                
                # Resource naming (should be nouns, plural)
                if method == "GET" and path.count("/") == 1:
                    resource = path.strip("/")
                    if not resource.endswith("s") and resource not in ["user", "me", "health"]:
                        review["recommendations"].append(f"Consider pluralizing resource name: '{resource}' -> '{resource}s'")
                
                # Idempotency
                if method in ["PUT", "DELETE"]:
                    if "{" not in path and method == "PUT":
                        review["issues"].append(f"PUT method should include resource ID in path: '{path}'")
                        score -= 3
                
                # Request/Response schemas
                if method in ["POST", "PUT", "PATCH"]:
                    if not endpoint.get("request_schema"):
                        review["issues"].append(f"Missing request schema for {method} {path}")
                        score -= 3
                
                if not endpoint.get("response_schema"):
                    review["issues"].append(f"Missing response schema for {method} {path}")
                    score -= 2
                
                # Authentication
                if not endpoint.get("authentication") and method not in ["GET", "OPTIONS"]:
                    review["security_concerns"].append(f"Missing authentication for {method} {path}")
                    score -= 5
            
            # Check for versioning
            has_versioning = any("/v" in endpoint.get("path", "") for endpoint in endpoints)
            if not has_versioning:
                review["recommendations"].append("Consider API versioning (e.g., /api/v1/...)")
            
            # Check for pagination
            has_pagination = any("page" in str(endpoint.get("query_parameters", [])).lower() or "limit" in str(endpoint.get("query_parameters", [])).lower() for endpoint in endpoints)
            if not has_pagination and any(endpoint.get("method") == "GET" for endpoint in endpoints):
                review["recommendations"].append("Consider adding pagination for list endpoints")
            
            # Check error handling
            has_error_codes = bool(api_design.get("error_codes"))
            if not has_error_codes:
                review["recommendations"].append("Define standard error codes and messages")
            
            # Strengths
            if all(endpoint.get("description") for endpoint in endpoints):
                review["strengths"].append("All endpoints have descriptions")
            
            if all(endpoint.get("response_schema") for endpoint in endpoints):
                review["strengths"].append("All endpoints have response schemas")
            
            # Best practices
            review["best_practices"] = [
                "Use HTTP status codes correctly (200, 201, 400, 401, 404, 500)",
                "Implement rate limiting",
                "Use consistent naming conventions",
                "Include request/response examples",
                "Document authentication requirements",
                "Version your API",
                "Implement proper error handling"
            ]
            
            review["score"] = max(0.0, min(100.0, score))
            
            logger.info(f"APIAgent: API design review complete - Score: {review['score']:.1f}/100")
        
        except Exception as e:
            logger.error(f"APIAgent: API design review failed: {e}", exc_info=True)
            review["error"] = str(e)
        
        return review
    
    async def _generate_testing_strategy(self, api_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive API testing strategy
        """
        testing_strategy = {
            "test_types": [],
            "test_cases": [],
            "test_scenarios": [],
            "tools": [],
            "error": None
        }
        
        try:
            logger.info("APIAgent: Generating testing strategy")
            
            endpoints = api_design.get("endpoints", [])
            
            # Test types
            testing_strategy["test_types"] = [
                "Unit Tests - Test individual endpoint logic",
                "Integration Tests - Test endpoint interactions",
                "Contract Tests - Validate request/response schemas",
                "Security Tests - Authentication, authorization, input validation",
                "Performance Tests - Load testing, stress testing",
                "E2E Tests - Complete user workflows"
            ]
            
            # Generate test cases for each endpoint
            for endpoint in endpoints:
                path = endpoint.get("path", "")
                method = endpoint.get("method", "").upper()
                
                # Happy path
                testing_strategy["test_cases"].append({
                    "name": f"{method} {path} - Success",
                    "type": "positive",
                    "method": method,
                    "path": path,
                    "expected_status": 200 if method != "POST" else 201,
                    "description": f"Test successful {method} request to {path}"
                })
                
                # Error cases
                if method in ["GET", "PUT", "DELETE", "PATCH"]:
                    testing_strategy["test_cases"].append({
                        "name": f"{method} {path} - Not Found",
                        "type": "negative",
                        "method": method,
                        "path": path.replace("{id}", "999999"),
                        "expected_status": 404,
                        "description": f"Test {method} request with non-existent resource"
                    })
                
                # Validation errors
                if method in ["POST", "PUT", "PATCH"]:
                    testing_strategy["test_cases"].append({
                        "name": f"{method} {path} - Validation Error",
                        "type": "negative",
                        "method": method,
                        "path": path,
                        "expected_status": 400,
                        "description": f"Test {method} request with invalid data"
                    })
                
                # Authentication
                if endpoint.get("authentication"):
                    testing_strategy["test_cases"].append({
                        "name": f"{method} {path} - Unauthorized",
                        "type": "security",
                        "method": method,
                        "path": path,
                        "expected_status": 401,
                        "description": f"Test {method} request without authentication"
                    })
            
            # Test scenarios
            testing_strategy["test_scenarios"] = [
                {
                    "name": "Complete CRUD Workflow",
                    "description": "Test create, read, update, delete operations",
                    "steps": [
                        "POST /resources - Create resource",
                        "GET /resources/{id} - Read resource",
                        "PUT /resources/{id} - Update resource",
                        "DELETE /resources/{id} - Delete resource"
                    ]
                },
                {
                    "name": "Authentication Flow",
                    "description": "Test authentication and authorization",
                    "steps": [
                        "POST /auth/login - Login",
                        "GET /protected - Access protected resource",
                        "POST /auth/logout - Logout"
                    ]
                }
            ]
            
            # Recommended tools
            testing_strategy["tools"] = [
                "Postman - API testing and documentation",
                "Newman - Automated Postman test runs",
                "REST Assured - Java API testing",
                "Pytest + Requests - Python API testing",
                "JMeter - Performance testing",
                "K6 - Load testing",
                "Dredd - API contract testing",
                "Schemathesis - Property-based API testing"
            ]
            
            logger.info(f"APIAgent: Generated testing strategy with {len(testing_strategy['test_cases'])} test cases")
        
        except Exception as e:
            testing_strategy["error"] = f"Testing strategy generation failed: {str(e)}"
            logger.error(f"APIAgent: Testing strategy generation failed: {e}", exc_info=True)
        
        return testing_strategy
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced API design with OpenAPI generation, design review, and testing strategy
        Overrides BaseAgent.execute to add comprehensive API capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"APIAgent: Starting enhanced API design for {target}")
            
            api_type = parameters.get("api_type", "rest")
            requirements = parameters.get("requirements", {})
            existing_api = parameters.get("existing_api", "")
            generate_openapi = parameters.get("generate_openapi", True)
            review_design = parameters.get("review_design", True)
            generate_tests = parameters.get("generate_tests", True)
            
            # STEP 1: Prepare initial prompt
            prompt = await self._prepare_prompt(target, parameters)
            
            # STEP 2: Call AI via router
            logger.info(f"APIAgent: Calling AI for API design")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"APIAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 3: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            if not parsed_result.get("success"):
                raise ValueError("Failed to parse API design from AI response")
            
            api_design = parsed_result.get("api_design", {})
            endpoints = api_design.get("endpoints", [])
            
            # STEP 4: Generate OpenAPI spec
            openapi_spec = {}
            if generate_openapi and endpoints:
                api_info = {
                    "title": requirements.get("title", "API"),
                    "version": requirements.get("version", "1.0.0"),
                    "description": requirements.get("description", ""),
                    "servers": requirements.get("servers", [])
                }
                openapi_spec = await self._generate_openapi_spec(endpoints, api_info)
                api_design["openapi_spec"] = openapi_spec
            
            # STEP 5: Review API design
            review = {}
            if review_design:
                review = await self._review_api_design(api_design)
                api_design["review"] = review
            
            # STEP 6: Generate testing strategy
            testing_strategy = {}
            if generate_tests:
                testing_strategy = await self._generate_testing_strategy(api_design)
                api_design["testing_strategy"] = testing_strategy
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": True,
                "result": api_design,
                "output": api_design,
                "quality_score": review.get("score", 80.0) / 100.0 if review else 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Designed API with {len(endpoints)} endpoints, OpenAPI spec: {bool(openapi_spec)}, Review score: {review.get('score', 0):.1f}/100"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"APIAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0
            }

