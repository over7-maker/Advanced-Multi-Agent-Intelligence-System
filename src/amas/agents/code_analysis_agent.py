"""
Code Analysis Agent - Specialized agent for code quality and security analysis
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

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
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
        
        self.expertise_score = 0.95  # High expertise
    
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


