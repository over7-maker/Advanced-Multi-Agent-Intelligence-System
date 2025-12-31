"""
Code Analysis Agent - Specialized agent for code quality and security analysis
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
from src.amas.agents.schemas import CodeAnalysisResult

logger = logging.getLogger(__name__)


class CodeAnalysisAgent(BaseAgent):
    """
    Code Analysis Agent
    
    Specializes in:
    - Code quality assessment
    - Security vulnerability detection
    - Performance optimization
    - Best practices compliance
    - Architecture review
    - Dependency analysis
    """
    
    def __init__(self):
        super().__init__(
            agent_id="code_analysis",
            name="Code Analysis Agent",
            agent_type="code",
            system_prompt="""You are an expert code analyst with 15+ years of experience 
            in software engineering, code review, and security analysis.
            
            Your expertise includes:
            • Code quality assessment (readability, maintainability, complexity)
            • Security vulnerability detection (OWASP Top 10, CWE, etc.)
            • Performance optimization and bottleneck identification
            • Best practices compliance (SOLID, DRY, KISS, etc.)
            • Architecture review and design patterns
            • Dependency analysis and vulnerability scanning
            • Code smell detection
            • Testing coverage analysis
            • Documentation quality assessment
            • Refactoring recommendations
            
            When analyzing code, you:
            1. Assess code quality and maintainability
            2. Identify security vulnerabilities with severity ratings
            3. Detect performance bottlenecks and optimization opportunities
            4. Review architecture and design patterns
            5. Check compliance with best practices and coding standards
            6. Analyze dependencies for known vulnerabilities
            7. Identify code smells and technical debt
            8. Evaluate test coverage and quality
            9. Review documentation completeness
            10. Provide prioritized refactoring recommendations
            
            Always provide:
            - Specific line numbers or code sections
            - Severity ratings (Critical, High, Medium, Low)
            - Clear explanations of issues
            - Concrete remediation steps
            - Code examples when helpful
            - Priority-based recommendations
            
            Follow industry standards: OWASP, CWE, CVE, and language-specific best practices.""",
            tools=[],  # Tools can be added here
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.code_tools = [
            "github_api",
            "npm_package",
            "pypi_package"
        ]
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare code analysis prompt"""
        
        analysis_type = parameters.get("analysis_type", "comprehensive")
        language = parameters.get("language", "unknown")
        code_content = parameters.get("code", "")
        focus_areas = parameters.get("focus_areas", [])
        
        if code_content:
            prompt = f"""Perform comprehensive code analysis on the following code:

Language: {language}
Analysis Type: {analysis_type}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

Code to analyze:
```{language}
{code_content}
```

Please analyze:
1. Code Quality:
   - Readability and maintainability
   - Code complexity (cyclomatic, cognitive)
   - Code smells and anti-patterns
   - Naming conventions and consistency

2. Security Vulnerabilities:
   - OWASP Top 10 vulnerabilities
   - Injection vulnerabilities (SQL, XSS, Command, etc.)
   - Authentication and authorization issues
   - Sensitive data exposure
   - Security misconfigurations
   - Known vulnerable dependencies

3. Performance:
   - Performance bottlenecks
   - Memory leaks and resource management
   - Algorithm efficiency
   - Database query optimization
   - Caching opportunities

4. Best Practices:
   - SOLID principles compliance
   - Design patterns usage
   - Error handling and logging
   - Testing coverage and quality
   - Documentation completeness

5. Architecture:
   - Design patterns and architecture decisions
   - Separation of concerns
   - Dependency management
   - Scalability considerations

Provide a detailed analysis report with:
- Specific issues with line numbers or code sections
- Severity ratings (Critical, High, Medium, Low, Info)
- Clear explanations and impact assessment
- Concrete remediation steps with code examples
- Priority-based recommendations
- Overall code quality score (0-100)

Format the response as structured JSON."""
        else:
            prompt = f"""Perform code analysis for target: {target}

Analysis Type: {analysis_type}
Language: {language}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

Please provide:
1. General code analysis guidelines for this target
2. Common security vulnerabilities to check
3. Best practices recommendations
4. Architecture considerations
5. Performance optimization strategies

Format the response as structured JSON with actionable recommendations."""

        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse code analysis response"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                return {
                    "success": True,
                    "analysis_report": parsed,
                    "summary": parsed.get("summary", "Code analysis completed"),
                    "vulnerabilities": parsed.get("vulnerabilities", []),
                    "quality_issues": parsed.get("quality_issues", []),
                    "performance_issues": parsed.get("performance_issues", []),
                    "recommendations": parsed.get("recommendations", []),
                    "quality_score": parsed.get("quality_score", 0.0)
                }
        except json.JSONDecodeError:
            pass
        
        # If not JSON, parse as structured text
        return {
            "success": True,
            "analysis_report": {
                "raw_response": response,
                "summary": response[:500] + "..." if len(response) > 500 else response
            },
            "summary": "Code analysis completed",
            "vulnerabilities": [],
            "quality_issues": [],
            "performance_issues": [],
            "recommendations": [],
            "quality_score": 0.0
        }
    
    async def _parse_code_structure(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Parse code structure using AST (for Python) or basic parsing for other languages
        """
        structure_analysis = {
            "language": language,
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity_metrics": {},
            "error": None
        }
        
        try:
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    
                    # Extract functions
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            structure_analysis["functions"].append({
                                "name": node.name,
                                "line": node.lineno,
                                "args_count": len(node.args.args),
                                "has_docstring": ast.get_docstring(node) is not None
                            })
                        
                        # Extract classes
                        if isinstance(node, ast.ClassDef):
                            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                            structure_analysis["classes"].append({
                                "name": node.name,
                                "line": node.lineno,
                                "methods": methods,
                                "has_docstring": ast.get_docstring(node) is not None
                            })
                        
                        # Extract imports
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    structure_analysis["imports"].append(alias.name)
                            else:
                                module = node.module or ""
                                for alias in node.names:
                                    structure_analysis["imports"].append(f"{module}.{alias.name}" if module else alias.name)
                    
                    # Calculate basic complexity metrics
                    structure_analysis["complexity_metrics"] = {
                        "total_functions": len(structure_analysis["functions"]),
                        "total_classes": len(structure_analysis["classes"]),
                        "total_imports": len(structure_analysis["imports"]),
                        "lines_of_code": len(code.splitlines())
                    }
                    
                    logger.info(f"CodeAnalysisAgent: Parsed {language} code structure: "
                               f"{len(structure_analysis['functions'])} functions, "
                               f"{len(structure_analysis['classes'])} classes")
                
                except SyntaxError as e:
                    structure_analysis["error"] = f"Syntax error: {str(e)}"
                    logger.warning(f"CodeAnalysisAgent: Syntax error in code: {e}")
                except Exception as e:
                    structure_analysis["error"] = f"AST parsing failed: {str(e)}"
                    logger.error(f"CodeAnalysisAgent: AST parsing failed: {e}", exc_info=True)
            else:
                # Basic parsing for non-Python languages
                # Extract function-like patterns
                function_patterns = {
                    "javascript": r"function\s+(\w+)\s*\(",
                    "java": r"(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(",
                    "go": r"func\s+(\w+)\s*\("
                }
                
                pattern = function_patterns.get(language.lower(), r"def\s+(\w+)\s*\(")
                functions = re.findall(pattern, code)
                structure_analysis["functions"] = [{"name": f, "line": 0} for f in functions]
                structure_analysis["complexity_metrics"] = {
                    "total_functions": len(functions),
                    "lines_of_code": len(code.splitlines())
                }
        
        except Exception as e:
            structure_analysis["error"] = f"Code structure parsing failed: {str(e)}"
            logger.error(f"CodeAnalysisAgent: Code structure parsing failed: {e}", exc_info=True)
        
        return structure_analysis
    
    async def _analyze_dependencies(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze dependencies from code
        
        Extracts dependencies and checks for vulnerabilities
        """
        dependency_analysis = {
            "dependencies": {},
            "vulnerable_packages": [],
            "outdated_packages": [],
            "error": None
        }
        
        try:
            tool_registry = get_tool_registry()
            npm_tool = tool_registry.get("npm_package")
            pypi_tool = tool_registry.get("pypi_package")
            
            logger.info(f"CodeAnalysisAgent: Analyzing dependencies for {language} code")
            
            # Extract dependencies based on language
            dependencies = {}
            
            if language.lower() == "python":
                # Extract import statements
                import_pattern = r"^(?:from\s+(\S+)\s+)?import\s+(\S+)"
                matches = re.findall(import_pattern, code, re.MULTILINE)
                for match in matches:
                    if match[0]:  # from X import Y
                        module = match[0].split(".")[0]
                    else:  # import X
                        module = match[1].split(".")[0]
                    if module and not module.startswith("_"):
                        dependencies[module] = None  # Version unknown from code
            
            elif language.lower() == "javascript":
                # Extract require/import statements
                require_pattern = r"require\(['\"]([^'\"]+)['\"]\)"
                import_pattern = r"import\s+.*from\s+['\"]([^'\"]+)['\"]"
                matches = re.findall(require_pattern, code) + re.findall(import_pattern, code)
                for match in matches:
                    module = match.split("/")[0]  # Get package name (before /)
                    if module and not module.startswith("."):
                        dependencies[module] = None
            
            # Check dependencies for vulnerabilities
            for package_name in dependencies.keys():
                try:
                    if language.lower() == "python" and pypi_tool:
                        result = await pypi_tool.execute({"package_name": package_name})
                        if result.get("success"):
                            dependency_analysis["dependencies"][package_name] = result.get("result", {})
                    elif language.lower() == "javascript" and npm_tool:
                        result = await npm_tool.execute({"package_name": package_name})
                        if result.get("success"):
                            dependency_analysis["dependencies"][package_name] = result.get("result", {})
                except Exception as e:
                    logger.debug(f"Failed to check dependency {package_name}: {e}")
            
            logger.info(f"CodeAnalysisAgent: Analyzed {len(dependency_analysis['dependencies'])} dependencies")
        
        except Exception as e:
            dependency_analysis["error"] = f"Dependency analysis failed: {str(e)}"
            logger.error(f"CodeAnalysisAgent: Dependency analysis failed: {e}", exc_info=True)
        
        return dependency_analysis
    
    async def _check_code_metrics(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Calculate code complexity metrics
        """
        metrics = {
            "lines_of_code": 0,
            "cyclomatic_complexity": 0,
            "function_count": 0,
            "class_count": 0,
            "average_function_length": 0,
            "comment_ratio": 0.0,
            "error": None
        }
        
        try:
            lines = code.splitlines()
            metrics["lines_of_code"] = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
            
            # Count comments
            comment_lines = len([l for l in lines if l.strip().startswith("#") or "//" in l.strip()])
            metrics["comment_ratio"] = comment_lines / len(lines) if lines else 0.0
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    
                    # Count functions and classes
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    metrics["function_count"] = len(functions)
                    metrics["class_count"] = len(classes)
                    
                    # Calculate average function length
                    if functions:
                        total_length = sum(len(ast.get_source_segment(code, f) or "").splitlines() for f in functions)
                        metrics["average_function_length"] = total_length / len(functions) if functions else 0
                    
                    # Basic cyclomatic complexity (count decision points)
                    complexity = 1  # Base complexity
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                            complexity += 1
                        elif isinstance(node, ast.BoolOp):
                            complexity += len(node.values) - 1
                    
                    metrics["cyclomatic_complexity"] = complexity
                
                except SyntaxError:
                    metrics["error"] = "Syntax error - cannot calculate all metrics"
                except Exception as e:
                    logger.debug(f"Metrics calculation error: {e}")
            
            logger.info(f"CodeAnalysisAgent: Calculated metrics: LOC={metrics['lines_of_code']}, "
                       f"Complexity={metrics['cyclomatic_complexity']}")
        
        except Exception as e:
            metrics["error"] = f"Metrics calculation failed: {str(e)}"
            logger.error(f"CodeAnalysisAgent: Metrics calculation failed: {e}", exc_info=True)
        
        return metrics
    
    async def _scan_for_secrets(self, code: str) -> Dict[str, Any]:
        """
        Scan code for hardcoded secrets, API keys, passwords, etc.
        """
        secret_scan_results = {
            "secrets_found": [],
            "high_risk_patterns": [],
            "error": None
        }
        
        try:
            logger.info("CodeAnalysisAgent: Scanning for secrets in code")
            
            # Common secret patterns
            secret_patterns = {
                "api_key": [
                    r"api[_-]?key\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                    r"apikey\s*[=:]\s*['\"]([^'\"]{20,})['\"]"
                ],
                "password": [
                    r"password\s*[=:]\s*['\"]([^'\"]+)['\"]",
                    r"passwd\s*[=:]\s*['\"]([^'\"]+)['\"]",
                    r"pwd\s*[=:]\s*['\"]([^'\"]+)['\"]"
                ],
                "secret": [
                    r"secret\s*[=:]\s*['\"]([^'\"]{10,})['\"]",
                    r"secret[_-]?key\s*[=:]\s*['\"]([^'\"]{10,})['\"]"
                ],
                "token": [
                    r"token\s*[=:]\s*['\"]([^'\"]{20,})['\"]",
                    r"access[_-]?token\s*[=:]\s*['\"]([^'\"]{20,})['\"]"
                ],
                "aws_key": [
                    r"aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*['\"]([^'\"]+)['\"]",
                    r"aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]([^'\"]+)['\"]"
                ],
                "private_key": [
                    r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----"
                ]
            }
            
            lines = code.splitlines()
            
            for secret_type, patterns in secret_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = code[:match.start()].count('\n') + 1
                        secret_value = match.group(1) if match.groups() else match.group(0)
                        
                        # Mask the secret value
                        if len(secret_value) > 10:
                            masked_value = secret_value[:4] + "..." + secret_value[-4:]
                        else:
                            masked_value = "***"
                        
                        secret_scan_results["secrets_found"].append({
                            "type": secret_type,
                            "line": line_num,
                            "pattern": pattern,
                            "masked_value": masked_value,
                            "severity": "Critical" if secret_type in ["password", "private_key", "aws_key"] else "High"
                        })
            
            # Check for high-risk patterns
            high_risk_patterns = [
                (r"eval\s*\(", "Use of eval() - security risk"),
                (r"exec\s*\(", "Use of exec() - security risk"),
                (r"shell\s*=\s*True", "Shell execution enabled - security risk"),
                (r"subprocess\.call.*shell\s*=\s*True", "Shell execution in subprocess - security risk")
            ]
            
            for pattern, description in high_risk_patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    secret_scan_results["high_risk_patterns"].append({
                        "pattern": pattern,
                        "description": description,
                        "line": line_num,
                        "severity": "High"
                    })
            
            logger.info(f"CodeAnalysisAgent: Secret scan completed: "
                       f"{len(secret_scan_results['secrets_found'])} secrets found, "
                       f"{len(secret_scan_results['high_risk_patterns'])} high-risk patterns")
        
        except Exception as e:
            secret_scan_results["error"] = f"Secret scanning failed: {str(e)}"
            logger.error(f"CodeAnalysisAgent: Secret scanning failed: {e}", exc_info=True)
        
        return secret_scan_results
    
    async def _analyze_test_coverage(self, code: str, test_code: str = None) -> Dict[str, Any]:
        """
        Analyze test coverage (basic implementation)
        """
        coverage_analysis = {
            "coverage_percentage": 0.0,
            "functions_tested": [],
            "functions_untested": [],
            "test_quality": "unknown",
            "error": None
        }
        
        try:
            logger.info("CodeAnalysisAgent: Analyzing test coverage")
            
            # Extract function names from code
            function_pattern = r"def\s+(\w+)\s*\("
            functions = re.findall(function_pattern, code)
            
            # Extract test function names
            test_functions = []
            if test_code:
                test_function_pattern = r"(?:def\s+test_(\w+)|def\s+(\w+)_test)\s*\("
                test_matches = re.findall(test_function_pattern, test_code)
                test_functions = [m[0] or m[1] for m in test_matches if m[0] or m[1]]
            
            # Simple coverage calculation
            if functions:
                # Assume a function is tested if there's a test with similar name
                tested = []
                untested = []
                
                for func in functions:
                    # Check if there's a test for this function
                    has_test = any(
                        func.lower() in test.lower() or test.lower() in func.lower()
                        for test in test_functions
                    )
                    if has_test:
                        tested.append(func)
                    else:
                        untested.append(func)
                
                coverage_analysis["functions_tested"] = tested
                coverage_analysis["functions_untested"] = untested
                coverage_analysis["coverage_percentage"] = len(tested) / len(functions) if functions else 0.0
            
            logger.info(f"CodeAnalysisAgent: Coverage analysis: {coverage_analysis['coverage_percentage']:.1%}")
        
        except Exception as e:
            coverage_analysis["error"] = f"Coverage analysis failed: {str(e)}"
            logger.error(f"CodeAnalysisAgent: Coverage analysis failed: {e}", exc_info=True)
        
        return coverage_analysis
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced code analysis with AST parsing and dependency scanning
        Overrides BaseAgent.execute to add comprehensive code analysis
        """
        execution_start = time.time()
        
        try:
            logger.info(f"CodeAnalysisAgent: Starting enhanced code analysis for {target}")
            
            code_content = parameters.get("code", "")
            language = parameters.get("language", "python")
            
            # STEP 1: Parse code structure
            structure_data = {}
            if code_content:
                structure_data = await self._parse_code_structure(code_content, language)
            
            # STEP 2: Analyze dependencies
            dependency_data = {}
            if code_content:
                dependency_data = await self._analyze_dependencies(code_content, language)
            
            # STEP 3: Calculate code metrics
            metrics_data = {}
            if code_content:
                metrics_data = await self._check_code_metrics(code_content, language)
            
            # STEP 4: Scan for secrets
            secret_data = {}
            if code_content:
                secret_data = await self._scan_for_secrets(code_content)
            
            # STEP 5: Analyze test coverage (if test code provided)
            coverage_data = {}
            test_code = parameters.get("test_code")
            if code_content:
                coverage_data = await self._analyze_test_coverage(code_content, test_code)
            
            # STEP 6: Prepare enhanced prompt
            prompt = await self._prepare_prompt(target, parameters, structure_data, dependency_data, metrics_data, secret_data, coverage_data)
            
            # STEP 7: Call AI via router
            logger.info(f"CodeAnalysisAgent: Calling AI with enhanced analysis data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"CodeAnalysisAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 8: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 9: Merge real analysis data with AI results
            if parsed_result.get("success") and parsed_result.get("analysis_report"):
                analysis_report = parsed_result["analysis_report"]
                
                # Merge structure data
                if structure_data:
                    analysis_report["code_structure"] = structure_data
                
                # Merge dependency data
                if dependency_data:
                    analysis_report["dependencies"] = dependency_data
                
                # Merge metrics
                if metrics_data:
                    analysis_report["code_metrics"] = metrics_data
                
                # Merge secret scan results
                if secret_data:
                    analysis_report["secret_scan"] = secret_data
                    # Add secrets to vulnerabilities
                    if secret_data.get("secrets_found"):
                        if "vulnerabilities" not in analysis_report:
                            analysis_report["vulnerabilities"] = []
                        for secret in secret_data["secrets_found"]:
                            analysis_report["vulnerabilities"].append({
                                "id": f"SECRET-{secret['line']}",
                                "severity": secret["severity"],
                                "title": f"Hardcoded {secret['type']} found",
                                "description": f"Secret detected at line {secret['line']}",
                                "location": f"Line {secret['line']}",
                                "remediation": "Move secret to environment variables or secure vault"
                            })
                
                # Merge coverage data
                if coverage_data:
                    analysis_report["test_coverage"] = coverage_data
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("analysis_report", {}),
                "output": parsed_result.get("analysis_report", {}),
                "quality_score": parsed_result.get("quality_score", 0.8),
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": parsed_result.get("summary", "Code analysis completed")
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"CodeAnalysisAgent: Execution failed: {e}", exc_info=True)
            
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
        structure_data: Dict[str, Any] = None,
        dependency_data: Dict[str, Any] = None,
        metrics_data: Dict[str, Any] = None,
        secret_data: Dict[str, Any] = None,
        coverage_data: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced code analysis prompt with all collected data"""
        
        analysis_type = parameters.get("analysis_type", "comprehensive")
        language = parameters.get("language", "unknown")
        code_content = parameters.get("code", "")
        focus_areas = parameters.get("focus_areas", [])
        
        # Build context from collected data
        analysis_context = ""
        
        if structure_data:
            analysis_context += f"\n=== CODE STRUCTURE ANALYSIS ===\n"
            analysis_context += f"Functions: {len(structure_data.get('functions', []))}\n"
            analysis_context += f"Classes: {len(structure_data.get('classes', []))}\n"
            analysis_context += f"Imports: {len(structure_data.get('imports', []))}\n"
            if structure_data.get("complexity_metrics"):
                metrics = structure_data["complexity_metrics"]
                analysis_context += f"Lines of Code: {metrics.get('lines_of_code', 0)}\n"
        
        if dependency_data:
            analysis_context += f"\n=== DEPENDENCY ANALYSIS ===\n"
            deps = dependency_data.get("dependencies", {})
            analysis_context += f"Dependencies Found: {len(deps)}\n"
            if dependency_data.get("vulnerable_packages"):
                analysis_context += f"Potentially Vulnerable: {len(dependency_data['vulnerable_packages'])}\n"
        
        if metrics_data:
            analysis_context += f"\n=== CODE METRICS ===\n"
            analysis_context += f"Lines of Code: {metrics_data.get('lines_of_code', 0)}\n"
            analysis_context += f"Cyclomatic Complexity: {metrics_data.get('cyclomatic_complexity', 0)}\n"
            analysis_context += f"Functions: {metrics_data.get('function_count', 0)}\n"
            analysis_context += f"Classes: {metrics_data.get('class_count', 0)}\n"
            analysis_context += f"Comment Ratio: {metrics_data.get('comment_ratio', 0.0):.1%}\n"
        
        if secret_data:
            analysis_context += f"\n=== SECRET SCAN RESULTS ===\n"
            secrets = secret_data.get("secrets_found", [])
            analysis_context += f"Secrets Found: {len(secrets)}\n"
            if secrets:
                critical_secrets = [s for s in secrets if s.get("severity") == "Critical"]
                analysis_context += f"Critical Secrets: {len(critical_secrets)}\n"
            if secret_data.get("high_risk_patterns"):
                analysis_context += f"High-Risk Patterns: {len(secret_data['high_risk_patterns'])}\n"
        
        if coverage_data:
            analysis_context += f"\n=== TEST COVERAGE ===\n"
            analysis_context += f"Coverage: {coverage_data.get('coverage_percentage', 0.0):.1%}\n"
            analysis_context += f"Functions Tested: {len(coverage_data.get('functions_tested', []))}\n"
            analysis_context += f"Functions Untested: {len(coverage_data.get('functions_untested', []))}\n"
        
        if code_content:
            prompt = f"""Perform comprehensive code analysis on the following code:

Language: {language}
Analysis Type: {analysis_type}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

{analysis_context}

Code to analyze:
```{language}
{code_content[:5000]}  # Limit to first 5000 chars
```

Based on the ANALYSIS DATA collected above, please provide:
1. Code Quality Assessment (use structure and metrics data)
2. Security Vulnerabilities (use secret scan results and dependency analysis)
3. Performance Issues (use metrics data)
4. Best Practices Compliance
5. Refactoring Recommendations

IMPORTANT: Reference the specific findings from the analysis data above (secrets found, dependencies, metrics, etc.)

Format the response as structured JSON."""
        else:
            prompt = f"""Perform code analysis for target: {target}

Analysis Type: {analysis_type}
Language: {language}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'Comprehensive analysis'}

{analysis_context}

Please provide comprehensive code analysis recommendations.

Format the response as structured JSON."""

        return prompt


