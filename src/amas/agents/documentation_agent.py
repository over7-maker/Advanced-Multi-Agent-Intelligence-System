"""
Documentation Agent - Specialized agent for documentation generation and management
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
from src.amas.agents.schemas import DocumentationResult

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
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.documentation_tools = ["github_api"]
    
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
    
    async def _generate_code_documentation(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate documentation from code structure
        """
        code_docs = {
            "functions_documented": [],
            "classes_documented": [],
            "module_docstring": "",
            "error": None
        }
        
        try:
            logger.info(f"DocumentationAgent: Generating code documentation for {language} code")
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    
                    # Extract module docstring
                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        code_docs["module_docstring"] = module_doc
                    
                    # Extract function documentation
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_doc = ast.get_docstring(node)
                            args = [arg.arg for arg in node.args.args]
                            
                            code_docs["functions_documented"].append({
                                "name": node.name,
                                "line": node.lineno,
                                "docstring": func_doc or "",
                                "parameters": args,
                                "has_docstring": func_doc is not None
                            })
                        
                        # Extract class documentation
                        if isinstance(node, ast.ClassDef):
                            class_doc = ast.get_docstring(node)
                            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                            
                            code_docs["classes_documented"].append({
                                "name": node.name,
                                "line": node.lineno,
                                "docstring": class_doc or "",
                                "methods": methods,
                                "has_docstring": class_doc is not None
                            })
                    
                    logger.info(f"DocumentationAgent: Documented {len(code_docs['functions_documented'])} functions, "
                               f"{len(code_docs['classes_documented'])} classes")
                
                except SyntaxError as e:
                    code_docs["error"] = f"Syntax error: {str(e)}"
                except Exception as e:
                    logger.debug(f"Code documentation generation error: {e}")
            
        except Exception as e:
            code_docs["error"] = f"Code documentation generation failed: {str(e)}"
            logger.error(f"DocumentationAgent: Code documentation generation failed: {e}", exc_info=True)
        
        return code_docs
    
    async def _generate_api_spec(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate OpenAPI/Swagger specification from code
        """
        api_spec = {
            "openapi_version": "3.0.0",
            "info": {
                "title": "API Documentation",
                "version": "1.0.0"
            },
            "paths": {},
            "components": {
                "schemas": {}
            },
            "error": None
        }
        
        try:
            logger.info("DocumentationAgent: Generating API specification")
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    
                    # Look for FastAPI/Flask route decorators
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Check for decorators
                            decorators = [d.id if isinstance(d, ast.Name) else "" for d in node.decorator_list]
                            
                            # FastAPI routes
                            if "router" in str(decorators) or "app" in str(decorators):
                                # Extract route information
                                route_path = "/api/endpoint"  # Default
                                method = "GET"  # Default
                                
                                # Try to extract from decorators
                                for decorator in node.decorator_list:
                                    if isinstance(decorator, ast.Call):
                                        if isinstance(decorator.func, ast.Attribute):
                                            method = decorator.func.attr.upper()
                                        if decorator.args:
                                            if isinstance(decorator.args[0], ast.Constant):
                                                route_path = decorator.args[0].value
                                
                                # Extract parameters
                                params = []
                                for arg in node.args.args:
                                    if arg.arg != "self":
                                        params.append({
                                            "name": arg.arg,
                                            "in": "query",
                                            "schema": {"type": "string"}
                                        })
                                
                                # Extract return type hint
                                return_type = "object"
                                if node.returns:
                                    return_type = "object"
                                
                                api_spec["paths"][route_path] = {
                                    method.lower(): {
                                        "summary": ast.get_docstring(node) or f"{node.name} endpoint",
                                        "operationId": node.name,
                                        "parameters": params,
                                        "responses": {
                                            "200": {
                                                "description": "Success",
                                                "content": {
                                                    "application/json": {
                                                        "schema": {"type": return_type}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                
                except SyntaxError:
                    pass
                except Exception as e:
                    logger.debug(f"API spec generation error: {e}")
            
            logger.info(f"DocumentationAgent: Generated API spec with {len(api_spec['paths'])} paths")
        
        except Exception as e:
            api_spec["error"] = f"API spec generation failed: {str(e)}"
            logger.error(f"DocumentationAgent: API spec generation failed: {e}", exc_info=True)
        
        return api_spec
    
    async def _generate_diagrams(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate architecture diagrams (Mermaid, PlantUML)
        """
        diagrams = {
            "mermaid_diagrams": [],
            "plantuml_diagrams": [],
            "architecture_diagram": "",
            "error": None
        }
        
        try:
            logger.info("DocumentationAgent: Generating architecture diagrams")
            
            if language.lower() == "python":
                try:
                    tree = ast.parse(code)
                    
                    # Generate class diagram (Mermaid)
                    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    if classes:
                        mermaid_class_diagram = "classDiagram\n"
                        for cls in classes:
                            mermaid_class_diagram += f"    class {cls.name} {{\n"
                            
                            # Add methods
                            methods = [m for m in cls.body if isinstance(m, ast.FunctionDef)]
                            for method in methods:
                                mermaid_class_diagram += f"        +{method.name}()\n"
                            
                            mermaid_class_diagram += "    }\n"
                            
                            # Add relationships (simplified)
                            for base in cls.bases:
                                if isinstance(base, ast.Name):
                                    mermaid_class_diagram += f"    {base.id} <|-- {cls.name}\n"
                        
                        diagrams["mermaid_diagrams"].append({
                            "type": "class_diagram",
                            "content": mermaid_class_diagram,
                            "description": "Class structure diagram"
                        })
                    
                    # Generate sequence diagram (basic)
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    if functions:
                        mermaid_sequence = "sequenceDiagram\n"
                        for i, func in enumerate(functions[:5]):  # Limit to 5 functions
                            mermaid_sequence += f"    participant {func.name}\n"
                        mermaid_sequence += "    Note over functions: Function call flow\n"
                        
                        diagrams["mermaid_diagrams"].append({
                            "type": "sequence_diagram",
                            "content": mermaid_sequence,
                            "description": "Function call sequence"
                        })
                    
                    # Generate architecture diagram
                    if classes or functions:
                        diagrams["architecture_diagram"] = f"""# Architecture Overview

## Components
- Classes: {len(classes)}
- Functions: {len(functions)}

## Class Structure
{chr(10).join([f"- {cls.name}" for cls in classes[:10]])}

## Function Overview
{chr(10).join([f"- {func.name}" for func in functions[:10]])}
"""
                    
                    logger.info(f"DocumentationAgent: Generated {len(diagrams['mermaid_diagrams'])} diagrams")
                
                except SyntaxError:
                    pass
                except Exception as e:
                    logger.debug(f"Diagram generation error: {e}")
            
        except Exception as e:
            diagrams["error"] = f"Diagram generation failed: {str(e)}"
            logger.error(f"DocumentationAgent: Diagram generation failed: {e}", exc_info=True)
        
        return diagrams
    
    async def _assess_documentation_quality(self, code: str, existing_docs: str = None) -> Dict[str, Any]:
        """
        Assess documentation quality and completeness
        """
        quality_assessment = {
            "completeness_score": 0.0,
            "missing_docstrings": [],
            "incomplete_docstrings": [],
            "recommendations": [],
            "error": None
        }
        
        try:
            logger.info("DocumentationAgent: Assessing documentation quality")
            
            if code:
                try:
                    tree = ast.parse(code)
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    total_items = len(functions) + len(classes)
                    documented_items = 0
                    
                    # Check functions
                    for func in functions:
                        docstring = ast.get_docstring(func)
                        if docstring:
                            documented_items += 1
                            # Check if docstring is complete (has description, params, returns)
                            if "param" not in docstring.lower() and "parameter" not in docstring.lower():
                                quality_assessment["incomplete_docstrings"].append({
                                    "type": "function",
                                    "name": func.name,
                                    "issue": "Missing parameter documentation"
                                })
                        else:
                            quality_assessment["missing_docstrings"].append({
                                "type": "function",
                                "name": func.name,
                                "line": func.lineno
                            })
                    
                    # Check classes
                    for cls in classes:
                        docstring = ast.get_docstring(cls)
                        if docstring:
                            documented_items += 1
                        else:
                            quality_assessment["missing_docstrings"].append({
                                "type": "class",
                                "name": cls.name,
                                "line": cls.lineno
                            })
                    
                    # Calculate completeness
                    if total_items > 0:
                        quality_assessment["completeness_score"] = documented_items / total_items
                    
                    # Generate recommendations
                    if quality_assessment["missing_docstrings"]:
                        quality_assessment["recommendations"].append({
                            "priority": "High",
                            "recommendation": f"Add docstrings to {len(quality_assessment['missing_docstrings'])} undocumented items"
                        })
                    
                    if quality_assessment["incomplete_docstrings"]:
                        quality_assessment["recommendations"].append({
                            "priority": "Medium",
                            "recommendation": f"Complete docstrings for {len(quality_assessment['incomplete_docstrings'])} items"
                        })
                    
                    logger.info(f"DocumentationAgent: Quality assessment: {quality_assessment['completeness_score']:.1%} complete")
                
                except SyntaxError:
                    pass
                except Exception as e:
                    logger.debug(f"Quality assessment error: {e}")
        
        except Exception as e:
            quality_assessment["error"] = f"Quality assessment failed: {str(e)}"
            logger.error(f"DocumentationAgent: Quality assessment failed: {e}", exc_info=True)
        
        return quality_assessment
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced documentation generation with code analysis
        Overrides BaseAgent.execute to add comprehensive documentation capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"DocumentationAgent: Starting enhanced documentation generation for {target}")
            
            code_content = parameters.get("code", "")
            language = parameters.get("language", "python")
            doc_type = parameters.get("doc_type", "code_documentation")
            
            # STEP 1: Generate code documentation
            code_docs = {}
            if code_content and doc_type in ["code_documentation", "api_documentation"]:
                code_docs = await self._generate_code_documentation(code_content, language)
            
            # STEP 2: Generate API spec (if requested)
            api_spec = {}
            if parameters.get("generate_api_spec", False) and code_content:
                api_spec = await self._generate_api_spec(code_content, language)
            
            # STEP 3: Generate diagrams (if requested)
            diagrams = {}
            if parameters.get("generate_diagrams", False) and code_content:
                diagrams = await self._generate_diagrams(code_content, language)
            
            # STEP 4: Assess documentation quality (if existing docs provided)
            quality_assessment = {}
            existing_docs = parameters.get("existing_documentation")
            if existing_docs or code_content:
                quality_assessment = await self._assess_documentation_quality(code_content, existing_docs)
            
            # STEP 5: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, code_docs, api_spec, diagrams, quality_assessment
            )
            
            # STEP 6: Call AI via router
            logger.info(f"DocumentationAgent: Calling AI with documentation analysis data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"DocumentationAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 7: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 8: Merge real analysis data with AI results
            if parsed_result.get("success") and parsed_result.get("documentation"):
                documentation = parsed_result["documentation"]
                
                # Merge code documentation
                if code_docs:
                    documentation["code_structure"] = code_docs
                
                # Merge API spec
                if api_spec:
                    documentation["api_spec"] = api_spec
                
                # Merge diagrams
                if diagrams:
                    documentation["diagrams"] = diagrams
                    if diagrams.get("mermaid_diagrams"):
                        # Add Mermaid diagrams to markdown
                        mermaid_content = "\n\n## Architecture Diagrams\n\n"
                        for diagram in diagrams["mermaid_diagrams"]:
                            mermaid_content += f"### {diagram.get('description', 'Diagram')}\n\n"
                            mermaid_content += f"```mermaid\n{diagram.get('content', '')}\n```\n\n"
                        if "markdown_content" in documentation:
                            documentation["markdown_content"] += mermaid_content
                
                # Merge quality assessment
                if quality_assessment:
                    documentation["quality_assessment"] = quality_assessment
                    documentation["completeness_score"] = quality_assessment.get("completeness_score", 0.0)
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("documentation", {}),
                "output": parsed_result.get("documentation", {}),
                "quality_score": parsed_result.get("documentation", {}).get("completeness_score", 0.8),
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Generated documentation with {parsed_result.get('markdown_length', 0)} characters"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"DocumentationAgent: Execution failed: {e}", exc_info=True)
            
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
        code_docs: Dict[str, Any] = None,
        api_spec: Dict[str, Any] = None,
        diagrams: Dict[str, Any] = None,
        quality_assessment: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced documentation prompt with all collected data"""
        
        doc_type = parameters.get("doc_type", "code_documentation")
        code_content = parameters.get("code", "")
        format_type = parameters.get("format", "markdown")
        audience = parameters.get("audience", "developers")
        
        # Build context from collected data
        documentation_context = ""
        
        if code_docs:
            documentation_context += f"\n=== CODE STRUCTURE ANALYSIS ===\n"
            documentation_context += f"Functions: {len(code_docs.get('functions_documented', []))}\n"
            documentation_context += f"Classes: {len(code_docs.get('classes_documented', []))}\n"
            if code_docs.get("module_docstring"):
                documentation_context += f"Module Docstring: {code_docs['module_docstring'][:200]}...\n"
            # List undocumented items
            undocumented = [f for f in code_docs.get("functions_documented", []) if not f.get("has_docstring")]
            if undocumented:
                documentation_context += f"Undocumented Functions: {', '.join([f['name'] for f in undocumented[:5]])}\n"
        
        if api_spec:
            documentation_context += f"\n=== API SPECIFICATION ===\n"
            documentation_context += f"API Endpoints: {len(api_spec.get('paths', {}))}\n"
            if api_spec.get("paths"):
                for path, methods in list(api_spec["paths"].items())[:5]:
                    documentation_context += f"  - {path}: {', '.join(methods.keys())}\n"
        
        if diagrams:
            documentation_context += f"\n=== DIAGRAMS ===\n"
            documentation_context += f"Mermaid Diagrams: {len(diagrams.get('mermaid_diagrams', []))}\n"
            if diagrams.get("architecture_diagram"):
                documentation_context += f"Architecture Diagram: Available\n"
        
        if quality_assessment:
            documentation_context += f"\n=== DOCUMENTATION QUALITY ===\n"
            documentation_context += f"Completeness Score: {quality_assessment.get('completeness_score', 0.0):.1%}\n"
            documentation_context += f"Missing Docstrings: {len(quality_assessment.get('missing_docstrings', []))}\n"
            if quality_assessment.get("recommendations"):
                for rec in quality_assessment["recommendations"][:3]:
                    documentation_context += f"  - {rec.get('recommendation')} ({rec.get('priority')})\n"
        
        prompt = f"""Generate comprehensive {doc_type} for: {target}

Documentation Type: {doc_type}
Format: {format_type}
Target Audience: {audience}

{documentation_context}

Code/Content to Document:
{code_content[:5000] if code_content else "No code provided - create general documentation"}

Based on the CODE ANALYSIS DATA collected above (code structure, API spec, diagrams, quality assessment), please provide:
1. Overview/Introduction (use code structure analysis)
2. Detailed explanation (reference functions and classes identified)
3. Usage examples (use code structure)
4. API reference (use generated API spec if available)
5. Architecture diagrams (use generated diagrams)
6. Best practices
7. Common pitfalls

IMPORTANT: 
- Reference the code structure analysis to document all functions and classes
- Use the API spec to create accurate API documentation
- Include the generated diagrams in markdown format
- Address missing docstrings identified in quality assessment

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
    "api_reference": {json.dumps(api_spec.get('paths', {})) if api_spec else {}},
    "diagrams": {json.dumps(diagrams.get('mermaid_diagrams', [])) if diagrams else []},
    "best_practices": ["...", "..."],
    "common_pitfalls": ["...", "..."],
    "markdown_content": "...",
    "quality_improvements": {json.dumps(quality_assessment.get('recommendations', [])) if quality_assessment else []}
}}"""
        
        return prompt

