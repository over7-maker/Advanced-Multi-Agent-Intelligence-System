"""
Testing Agent - Specialized agent for test generation and quality assurance
Implements PART_3 requirements
"""

import ast
import json
import logging
import re
from typing import Any, Dict, List

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import TestingResult

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
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.testing_tools = ["github_api"]
    
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
    
    async def _analyze_test_coverage(self, code: str, test_code: str = None, language: str = "python") -> Dict[str, Any]:
        """
        Analyze test coverage for code
        """
        coverage_analysis = {
            "coverage_percentage": 0.0,
            "functions_covered": [],
            "functions_untested": [],
            "lines_covered": 0,
            "total_lines": 0,
            "branches_covered": 0,
            "total_branches": 0,
            "error": None
        }
        
        try:
            logger.info("TestingAgent: Analyzing test coverage")
            
            if language.lower() == "python" and code:
                # Parse code to get functions
                try:
                    tree = ast.parse(code)
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    coverage_analysis["total_functions"] = len(functions)
                    coverage_analysis["total_classes"] = len(classes)
                    
                    # Count lines
                    code_lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith("#")]
                    coverage_analysis["total_lines"] = len(code_lines)
                    
                    # Check test coverage
                    if test_code:
                        # Extract test function names
                        test_tree = ast.parse(test_code)
                        test_functions = [node.name for node in ast.walk(test_tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
                        
                        # Match functions to tests
                        covered = []
                        untested = []
                        
                        for func in functions:
                            # Check if there's a test for this function
                            has_test = any(
                                func.lower() in test.lower() or test.lower().replace("test_", "") == func.lower()
                                for test in test_functions
                            )
                            if has_test:
                                covered.append(func)
                            else:
                                untested.append(func)
                        
                        coverage_analysis["functions_covered"] = covered
                        coverage_analysis["functions_untested"] = untested
                        coverage_analysis["coverage_percentage"] = len(covered) / len(functions) if functions else 0.0
                    else:
                        coverage_analysis["functions_untested"] = functions
                        coverage_analysis["coverage_percentage"] = 0.0
                
                except SyntaxError as e:
                    coverage_analysis["error"] = f"Syntax error: {str(e)}"
                except Exception as e:
                    logger.debug(f"Coverage analysis error: {e}")
            
            logger.info(f"TestingAgent: Coverage analysis: {coverage_analysis['coverage_percentage']:.1%}")
        
        except Exception as e:
            coverage_analysis["error"] = f"Coverage analysis failed: {str(e)}"
            logger.error(f"TestingAgent: Coverage analysis failed: {e}", exc_info=True)
        
        return coverage_analysis
    
    async def _generate_test_cases(self, code: str, language: str = "python", test_type: str = "unit") -> Dict[str, Any]:
        """
        Generate test cases from code structure
        """
        test_generation = {
            "test_cases": [],
            "test_code": "",
            "framework": "pytest" if language == "python" else "jest" if language == "javascript" else "unknown",
            "error": None
        }
        
        try:
            logger.info(f"TestingAgent: Generating {test_type} test cases for {language} code")
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    
                    for func in functions:
                        func_name = func.name
                        args = [arg.arg for arg in func.args.args if arg.arg != "self"]
                        
                        # Generate test cases for this function
                        test_cases = []
                        
                        # Positive test case
                        test_cases.append({
                            "name": f"test_{func_name}_positive",
                            "description": f"Test {func_name} with valid inputs",
                            "test_type": test_type,
                            "function": func_name,
                            "inputs": {arg: "valid_value" for arg in args},
                            "expected": "success"
                        })
                        
                        # Negative test case (if function has parameters)
                        if args:
                            test_cases.append({
                                "name": f"test_{func_name}_negative",
                                "description": f"Test {func_name} with invalid inputs",
                                "test_type": test_type,
                                "function": func_name,
                                "inputs": {arg: "invalid_value" for arg in args},
                                "expected": "error_or_exception"
                            })
                        
                        # Edge case
                        if args:
                            test_cases.append({
                                "name": f"test_{func_name}_edge_case",
                                "description": f"Test {func_name} with edge case inputs",
                                "test_type": test_type,
                                "function": func_name,
                                "inputs": {arg: "edge_case_value" for arg in args},
                                "expected": "edge_case_handling"
                            })
                        
                        test_generation["test_cases"].extend(test_cases)
                
                except SyntaxError as e:
                    test_generation["error"] = f"Syntax error: {str(e)}"
                except Exception as e:
                    logger.debug(f"Test generation error: {e}")
            
            logger.info(f"TestingAgent: Generated {len(test_generation['test_cases'])} test cases")
        
        except Exception as e:
            test_generation["error"] = f"Test generation failed: {str(e)}"
            logger.error(f"TestingAgent: Test generation failed: {e}", exc_info=True)
        
        return test_generation
    
    async def _suggest_mutation_tests(self, code: str, test_code: str = None) -> Dict[str, Any]:
        """
        Suggest mutation testing scenarios
        """
        mutation_suggestions = {
            "mutations": [],
            "test_gaps": [],
            "recommendations": [],
            "error": None
        }
        
        try:
            logger.info("TestingAgent: Analyzing mutation testing opportunities")
            
            if code:
                # Common mutation operators
                mutation_operators = [
                    {
                        "type": "arithmetic_operator_replacement",
                        "description": "Replace + with -, * with /, etc.",
                        "example": "a + b -> a - b"
                    },
                    {
                        "type": "logical_operator_replacement",
                        "description": "Replace && with ||, == with !=, etc.",
                        "example": "a == b -> a != b"
                    },
                    {
                        "type": "constant_replacement",
                        "description": "Replace constants with different values",
                        "example": "if x > 10 -> if x > 5"
                    },
                    {
                        "type": "condition_negation",
                        "description": "Negate boolean conditions",
                        "example": "if condition -> if not condition"
                    },
                    {
                        "type": "statement_deletion",
                        "description": "Remove statements",
                        "example": "Remove return statement"
                    }
                ]
                
                # Analyze code for mutation opportunities
                if "if" in code or "while" in code or "for" in code:
                    mutation_suggestions["mutations"].append({
                        "operator": "condition_negation",
                        "description": "Test with negated conditions",
                        "priority": "High"
                    })
                
                if re.search(r"[+\-*/]", code):
                    mutation_suggestions["mutations"].append({
                        "operator": "arithmetic_operator_replacement",
                        "description": "Test with different arithmetic operators",
                        "priority": "Medium"
                    })
                
                # Check if tests would catch these mutations
                if test_code:
                    mutation_suggestions["test_gaps"] = [
                        "Ensure tests fail when mutations are applied",
                        "Add tests for edge cases that mutations might reveal"
                    ]
                
                mutation_suggestions["recommendations"] = [
                    "Use mutation testing tools (e.g., mutmut for Python)",
                    "Ensure test suite kills all mutations",
                    "Focus on high-priority mutation operators first"
                ]
            
            logger.info(f"TestingAgent: Mutation analysis completed: {len(mutation_suggestions['mutations'])} mutations suggested")
        
        except Exception as e:
            mutation_suggestions["error"] = f"Mutation analysis failed: {str(e)}"
            logger.error(f"TestingAgent: Mutation analysis failed: {e}", exc_info=True)
        
        return mutation_suggestions
    
    async def _generate_performance_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate performance test cases
        """
        performance_tests = {
            "test_cases": [],
            "benchmarks": [],
            "error": None
        }
        
        try:
            logger.info("TestingAgent: Generating performance tests")
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    
                    for func in functions:
                        func_name = func.name
                        
                        # Generate performance test
                        performance_tests["test_cases"].append({
                            "name": f"test_{func_name}_performance",
                            "description": f"Performance test for {func_name}",
                            "test_type": "performance",
                            "function": func_name,
                            "max_execution_time_ms": 1000,
                            "memory_limit_mb": 100
                        })
                        
                        # Generate benchmark
                        performance_tests["benchmarks"].append({
                            "function": func_name,
                            "benchmark_name": f"benchmark_{func_name}",
                            "iterations": 1000,
                            "warmup_iterations": 100
                        })
                
                except SyntaxError:
                    pass
                except Exception as e:
                    logger.debug(f"Performance test generation error: {e}")
            
            logger.info(f"TestingAgent: Generated {len(performance_tests['test_cases'])} performance tests")
        
        except Exception as e:
            performance_tests["error"] = f"Performance test generation failed: {str(e)}"
            logger.error(f"TestingAgent: Performance test generation failed: {e}", exc_info=True)
        
        return performance_tests
    
    async def _generate_security_tests(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate security test cases
        """
        security_tests = {
            "test_cases": [],
            "vulnerability_tests": [],
            "error": None
        }
        
        try:
            logger.info("TestingAgent: Generating security tests")
            
            # Common security test scenarios
            security_scenarios = [
                {
                    "name": "sql_injection_test",
                    "description": "Test for SQL injection vulnerabilities",
                    "test_inputs": ["'; DROP TABLE users; --", "1' OR '1'='1"]
                },
                {
                    "name": "xss_test",
                    "description": "Test for XSS vulnerabilities",
                    "test_inputs": ["<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>"]
                },
                {
                    "name": "command_injection_test",
                    "description": "Test for command injection vulnerabilities",
                    "test_inputs": ["; rm -rf /", "| cat /etc/passwd"]
                },
                {
                    "name": "path_traversal_test",
                    "description": "Test for path traversal vulnerabilities",
                    "test_inputs": ["../../../etc/passwd", "..\\..\\..\\windows\\system32"]
                },
                {
                    "name": "authentication_bypass_test",
                    "description": "Test for authentication bypass",
                    "test_inputs": ["admin", "admin'--", "' OR 1=1--"]
                }
            ]
            
            # Check if code has patterns that need security testing
            if re.search(r"(SELECT|INSERT|UPDATE|DELETE)", code, re.IGNORECASE):
                security_tests["vulnerability_tests"].append({
                    "type": "sql_injection",
                    "test_cases": security_scenarios[0]["test_inputs"],
                    "priority": "Critical"
                })
            
            if re.search(r"(eval|exec|subprocess)", code, re.IGNORECASE):
                security_tests["vulnerability_tests"].append({
                    "type": "command_injection",
                    "test_cases": security_scenarios[2]["test_inputs"],
                    "priority": "Critical"
                })
            
            if re.search(r"(open|file|read)", code, re.IGNORECASE):
                security_tests["vulnerability_tests"].append({
                    "type": "path_traversal",
                    "test_cases": security_scenarios[3]["test_inputs"],
                    "priority": "High"
                })
            
            # Generate test cases
            for scenario in security_scenarios:
                security_tests["test_cases"].append({
                    "name": f"test_security_{scenario['name']}",
                    "description": scenario["description"],
                    "test_type": "security",
                    "test_inputs": scenario["test_inputs"],
                    "expected": "should_reject_or_sanitize"
                })
            
            logger.info(f"TestingAgent: Generated {len(security_tests['test_cases'])} security tests")
        
        except Exception as e:
            security_tests["error"] = f"Security test generation failed: {str(e)}"
            logger.error(f"TestingAgent: Security test generation failed: {e}", exc_info=True)
        
        return security_tests
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced testing with coverage analysis and test generation
        Overrides BaseAgent.execute to add comprehensive testing capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"TestingAgent: Starting enhanced testing for {target}")
            
            code_content = parameters.get("code", "")
            test_code = parameters.get("test_code")
            language = parameters.get("language", "python")
            test_type = parameters.get("test_type", "unit_tests")
            
            # STEP 1: Analyze test coverage
            coverage_data = {}
            if code_content:
                coverage_data = await self._analyze_test_coverage(code_content, test_code, language)
            
            # STEP 2: Generate test cases
            test_generation_data = {}
            if code_content and parameters.get("generate_tests", True):
                test_generation_data = await self._generate_test_cases(code_content, language, test_type)
            
            # STEP 3: Mutation testing suggestions
            mutation_data = {}
            if parameters.get("mutation_testing", False) and code_content:
                mutation_data = await self._suggest_mutation_tests(code_content, test_code)
            
            # STEP 4: Generate performance tests (if requested)
            performance_test_data = {}
            if parameters.get("performance_tests", False) and code_content:
                performance_test_data = await self._generate_performance_tests(code_content, language)
            
            # STEP 5: Generate security tests (if requested)
            security_test_data = {}
            if parameters.get("security_tests", False) and code_content:
                security_test_data = await self._generate_security_tests(code_content, language)
            
            # STEP 6: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, coverage_data, test_generation_data, mutation_data,
                performance_test_data, security_test_data
            )
            
            # STEP 7: Call AI via router
            logger.info(f"TestingAgent: Calling AI with testing analysis data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"TestingAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 8: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 9: Merge real analysis data with AI results
            if parsed_result.get("success") and parsed_result.get("tests"):
                tests = parsed_result["tests"]
                
                # Merge coverage analysis
                if coverage_data:
                    tests["coverage_analysis"] = coverage_data
                    if "test_coverage" not in tests:
                        tests["test_coverage"] = {}
                    tests["test_coverage"].update({
                        "coverage_percentage": coverage_data.get("coverage_percentage", 0.0),
                        "functions_covered": len(coverage_data.get("functions_covered", [])),
                        "functions_untested": len(coverage_data.get("functions_untested", []))
                    })
                
                # Merge generated test cases
                if test_generation_data:
                    if "generated_test_cases" not in tests:
                        tests["generated_test_cases"] = []
                    tests["generated_test_cases"].extend(test_generation_data.get("test_cases", []))
                
                # Merge mutation testing
                if mutation_data:
                    tests["mutation_testing"] = mutation_data
                
                # Merge performance tests
                if performance_test_data:
                    tests["performance_tests"] = performance_test_data
                
                # Merge security tests
                if security_test_data:
                    tests["security_tests"] = security_test_data
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("tests", {}),
                "output": parsed_result.get("tests", {}),
                "quality_score": 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Generated {parsed_result.get('test_cases_count', 0)} test cases with {parsed_result.get('coverage_percentage', 0):.1%} coverage"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"TestingAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0
            }
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any],
        coverage_data: Dict[str, Any] = None,
        test_generation_data: Dict[str, Any] = None,
        mutation_data: Dict[str, Any] = None,
        performance_test_data: Dict[str, Any] = None,
        security_test_data: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced testing prompt with all collected data"""
        
        test_type = parameters.get("test_type", "unit_tests")
        code_content = parameters.get("code", "")
        framework = parameters.get("framework", "pytest")
        language = parameters.get("language", "python")
        
        # Build context from collected data
        testing_context = ""
        
        if coverage_data:
            testing_context += f"\n=== TEST COVERAGE ANALYSIS ===\n"
            testing_context += f"Coverage: {coverage_data.get('coverage_percentage', 0.0):.1%}\n"
            testing_context += f"Functions Covered: {len(coverage_data.get('functions_covered', []))}\n"
            testing_context += f"Functions Untested: {len(coverage_data.get('functions_untested', []))}\n"
            if coverage_data.get("functions_untested"):
                testing_context += f"Untested Functions: {', '.join(coverage_data['functions_untested'][:5])}\n"
        
        if test_generation_data:
            testing_context += f"\n=== GENERATED TEST CASES ===\n"
            testing_context += f"Test Cases Generated: {len(test_generation_data.get('test_cases', []))}\n"
            for i, test_case in enumerate(test_generation_data.get("test_cases", [])[:5], 1):
                testing_context += f"{i}. {test_case.get('name', 'N/A')}: {test_case.get('description', '')}\n"
        
        if mutation_data:
            testing_context += f"\n=== MUTATION TESTING ===\n"
            testing_context += f"Mutations Suggested: {len(mutation_data.get('mutations', []))}\n"
            if mutation_data.get("recommendations"):
                testing_context += f"Recommendations: {', '.join(mutation_data['recommendations'])}\n"
        
        if performance_test_data:
            testing_context += f"\n=== PERFORMANCE TESTS ===\n"
            testing_context += f"Performance Tests: {len(performance_test_data.get('test_cases', []))}\n"
        
        if security_test_data:
            testing_context += f"\n=== SECURITY TESTS ===\n"
            testing_context += f"Security Tests: {len(security_test_data.get('test_cases', []))}\n"
            testing_context += f"Vulnerability Tests: {len(security_test_data.get('vulnerability_tests', []))}\n"
        
        prompt = f"""Generate comprehensive {test_type} for: {target}

Test Type: {test_type}
Framework: {framework}
Language: {language}

{testing_context}

Code to Test:
{code_content[:5000] if code_content else "No code provided - create general test template"}

Based on the TESTING ANALYSIS DATA collected above (coverage analysis, generated test cases, mutation testing), please provide:
1. Comprehensive test cases (use generated test cases as reference)
2. Test coverage improvement (focus on untested functions identified)
3. Edge case tests (use mutation testing suggestions)
4. Error handling tests
5. Integration tests (if applicable)
6. Test fixtures and setup
7. Test code implementation (use framework: {framework})

IMPORTANT: 
- Reference the coverage analysis to ensure all functions are tested
- Include mutation testing scenarios
- Add performance and security tests if applicable
- Follow {framework} best practices

Format your response as JSON with the following structure:
{{
    "test_cases": [
        {{
            "name": "...",
            "description": "...",
            "code": "...",
            "expected_result": "...",
            "test_type": "unit|integration|e2e|performance|security"
        }}
    ],
    "test_coverage": {{
        "functions_covered": X,
        "lines_covered": X,
        "coverage_percentage": X,
        "improvement_suggestions": ["...", "..."]
    }},
    "mutation_testing": {{
        "mutations_tested": ["...", "..."],
        "test_gaps": ["...", "..."]
    }},
    "test_fixtures": "...",
    "test_setup": "...",
    "framework_code": "..."
}}"""
        
        return prompt

