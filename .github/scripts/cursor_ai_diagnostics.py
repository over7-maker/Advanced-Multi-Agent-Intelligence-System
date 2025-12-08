#!/usr/bin/env python3
"""
Bulletproof AI Diagnostics for Cursor IDE
Provides real-time AI analysis as VS Code-compatible diagnostics
Uses the same bulletproof AI system as GitHub Actions PR analysis
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}", file=sys.stderr)
    else:
        print(f"⚠️  .env file not found at: {env_file}", file=sys.stderr)
except ImportError:
    # dotenv not installed, try to load .env manually
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment from: {env_file} (manual)", file=sys.stderr)

# Try to import AI router - handle gracefully if dependencies missing
# Import directly from the file to avoid circular imports
try:
    import importlib.util
    router_path = PROJECT_ROOT / "src" / "amas" / "ai" / "enhanced_router_v2.py"
    if router_path.exists():
        spec = importlib.util.spec_from_file_location("enhanced_router_v2", router_path)
        router_module = importlib.util.module_from_spec(spec)
        # Don't execute the module fully to avoid circular imports
        # Just get the functions we need
        spec.loader.exec_module(router_module)
        generate_with_fallback = router_module.generate_with_fallback
        AI_ROUTER_AVAILABLE = True
    else:
        raise ImportError(f"Router file not found: {router_path}")
except Exception as e:
    AI_ROUTER_AVAILABLE = False
    AI_ROUTER_ERROR = str(e)
    # Create a dummy function for testing
    async def generate_with_fallback(*args, **kwargs):
        return {
            "success": False,
            "error": f"AI Router not available: {AI_ROUTER_ERROR}. Please install dependencies: pip install -r requirements.txt",
            "content": ""
        }


class BulletproofAIDiagnostics:
    """Bulletproof AI Diagnostics for Cursor IDE"""
    
    def __init__(self):
        self.cache: Dict[str, tuple[float, List[Dict[str, Any]]]] = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_provider: Optional[str] = None
        self.last_response_time: float = 0.0
    
    async def analyze_code(
        self,
        file_path: str,
        code_content: str,
        analysis_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze code and return VS Code compatible diagnostics.
        
        Args:
            file_path: Path to the file being analyzed
            code_content: Content of the file
            analysis_types: Types of analysis to perform (optional)
            
        Returns:
            List of VS Code diagnostic dictionaries
        """
        if analysis_types is None:
            analysis_types = ["code_quality", "security", "performance", "best_practices"]
        
        # Check cache
        cache_key = f"{file_path}:{hash(code_content)}"
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            if (time.time() - cached_time) < self.cache_timeout:
                return cached_result
        
        # Build analysis prompt matching GitHub Actions format
        prompt = self._build_analysis_prompt(file_path, code_content, analysis_types)
        
        # Use existing bulletproof AI router
        start_time = time.time()
        try:
            if not AI_ROUTER_AVAILABLE:
                return [{
                    "severity": 2,  # Warning
                    "line": 0,
                    "column": 0,
                    "message": f"AI Router not available: {AI_ROUTER_ERROR}. Install dependencies: pip install -r requirements.txt",
                    "source": "Bulletproof AI",
                    "code": "setup_error"
                }]
            
            result = await generate_with_fallback(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                max_tokens=4000,
                temperature=0.3,
                timeout=60.0
            )
            
            self.last_response_time = time.time() - start_time
            
            if not result.get("success"):
                return [{
                    "severity": 2,  # Warning
                    "line": 0,
                    "column": 0,
                    "message": f"AI Analysis unavailable: {result.get('error', 'Unknown error')}",
                    "source": "Bulletproof AI",
                    "code": "analysis_error"
                }]
            
            self.last_provider = result.get("provider", "unknown")
            content = result.get("content", "")
            
            # Parse AI response into diagnostics
            diagnostics = self._parse_ai_response(content, file_path)
            
            # Cache result
            self.cache[cache_key] = (time.time(), diagnostics)
            
            return diagnostics
            
        except Exception as e:
            return [{
                "severity": 2,  # Warning
                "line": 0,
                "column": 0,
                "message": f"AI Analysis error: {str(e)}",
                "source": "Bulletproof AI",
                "code": "analysis_error"
            }]
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analysis"""
        return """You are an expert Python code analyzer. Analyze code for:
1. Critical Issues: Syntax errors, incomplete code, import errors
2. Code Quality: PEP 8 violations, missing docstrings, type hints
3. Security: SSRF risks, hardcoded secrets, injection vulnerabilities
4. Performance: Inefficient operations, missing async, memory leaks
5. Best Practices: Error handling, logging, testing gaps

For each issue, provide JSON format:
{
  "line": <line_number>,
  "severity": "critical|high|medium|low",
  "category": "syntax|code_quality|security|performance|best_practice",
  "message": "<clear description>",
  "recommendation": "<specific fix>"
}

Return ONLY a JSON array of issues, no markdown formatting."""
    
    def _build_analysis_prompt(
        self,
        file_path: str,
        code: str,
        analysis_types: List[str]
    ) -> str:
        """Build analysis prompt matching GitHub Actions format"""
        file_name = Path(file_path).name
        
        prompt = f"""Analyze this Python code file for issues and provide actionable feedback.

File: {file_path}
File Name: {file_name}

Code:
```python
{code}
```

Analyze for:
"""
        
        type_descriptions = {
            "code_quality": "Code Quality: PEP 8 violations, missing docstrings, type hints, code style",
            "security": "Security: SSRF risks, hardcoded secrets, injection vulnerabilities, unsafe operations",
            "performance": "Performance: Inefficient operations, missing async/await, memory leaks, bottlenecks",
            "best_practices": "Best Practices: Error handling, logging, testing gaps, maintainability",
            "syntax": "Syntax: Syntax errors, incomplete code, import errors, type errors"
        }
        
        for analysis_type in analysis_types:
            if analysis_type in type_descriptions:
                prompt += f"- {type_descriptions[analysis_type]}\n"
        
        prompt += """
For each issue found, provide:
- Line number (exact, 1-indexed)
- Severity (critical/high/medium/low)
- Category (syntax/code_quality/security/performance/best_practice)
- Clear description
- Specific fix recommendation

Return a JSON array of issues:
[
  {
    "line": 73,
    "severity": "critical",
    "category": "syntax",
    "message": "ANTHROPIC enum member incomplete - missing value assignment",
    "recommendation": "Add: ANTHROPIC = 'anthropic'"
  }
]

Return ONLY the JSON array, no markdown, no explanations outside the JSON."""
        
        return prompt
    
    def _parse_ai_response(self, response: str, file_path: str) -> List[Dict[str, Any]]:
        """Parse AI response into VS Code diagnostics format"""
        diagnostics = []
        
        try:
            # Try to extract JSON from response
            json_str = self._extract_json(response)
            
            if not json_str:
                # Fallback: parse text response
                return self._parse_text_response(response, file_path)
            
            issues = json.loads(json_str)
            
            if not isinstance(issues, list):
                issues = [issues]
            
            # Convert to VS Code diagnostic format
            severity_map = {
                "critical": 1,  # Error
                "high": 1,      # Error
                "medium": 2,    # Warning
                "low": 3,       # Information
                "info": 4       # Hint
            }
            
            for issue in issues:
                if not isinstance(issue, dict):
                    continue
                
                line_num = max(1, issue.get("line", 1)) - 1  # VS Code uses 0-indexed
                severity_name = issue.get("severity", "medium").lower()
                severity = severity_map.get(severity_name, 2)
                
                message = issue.get("message", "Issue detected")
                recommendation = issue.get("recommendation", "")
                
                if recommendation:
                    message += f"\n💡 Fix: {recommendation}"
                
                diagnostic = {
                    "severity": severity,
                    "line": line_num,
                    "column": max(0, issue.get("column", 0)),
                    "message": message,
                    "source": "Bulletproof AI",
                    "code": issue.get("category", "general")
                }
                
                diagnostics.append(diagnostic)
            
            return diagnostics
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_text_response(response, file_path)
        except Exception as e:
            return [{
                "severity": 2,
                "line": 0,
                "column": 0,
                "message": f"Failed to parse AI response: {str(e)}",
                "source": "Bulletproof AI",
                "code": "parse_error"
            }]
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from text response"""
        # Try to find JSON array
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            if json_end > json_start:
                return text[json_start:json_end].strip()
        
        # Try to find JSON array brackets
        if "[" in text and "]" in text:
            json_start = text.find("[")
            json_end = text.rfind("]") + 1
            if json_end > json_start:
                candidate = text[json_start:json_end]
                # Validate it's valid JSON
                try:
                    json.loads(candidate)
                    return candidate
                except:
                    pass
        
        return None
    
    def _parse_text_response(self, response: str, file_path: str) -> List[Dict[str, Any]]:
        """Fallback: parse text response for issues"""
        diagnostics = []
        lines = response.split('\n')
        
        for line in lines:
            # Pattern: Line 73: ...
            if 'Line' in line and ':' in line:
                try:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        line_part = parts[0].strip()
                        if 'Line' in line_part:
                            line_num = int(line_part.replace('Line', '').strip())
                            message = parts[2].strip() if len(parts) > 2 else parts[1].strip()
                            
                            severity = 2  # Warning by default
                            if any(word in line.lower() for word in ['critical', 'error', 'syntax']):
                                severity = 1  # Error
                            elif any(word in line.lower() for word in ['info', 'suggestion', 'hint']):
                                severity = 3  # Info
                            
                            diagnostics.append({
                                "severity": severity,
                                "line": line_num - 1,  # 0-indexed
                                "column": 0,
                                "message": message,
                                "source": "Bulletproof AI"
                            })
                except (ValueError, IndexError):
                    continue
        
        return diagnostics


async def analyze_file_cli(file_path: str, output_format: str = "diagnostics"):
    """
    CLI interface for analyzing a file.
    
    Args:
        file_path: Path to file to analyze
        output_format: Output format - "diagnostics" (VS Code) or "json"
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not file_path.endswith('.py'):
        print(f"Warning: File is not a Python file: {file_path}", file=sys.stderr)
    
    # Read file
    try:
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Analyze
    analyzer = BulletproofAIDiagnostics()
    diagnostics = await analyzer.analyze_code(str(file_path), code)
    
    if output_format == "json":
        # Output JSON
        output = {
            "file": str(file_path),
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat(),
            "provider": analyzer.last_provider,
            "response_time": analyzer.last_response_time
        }
        print(json.dumps(output, indent=2))
    else:
        # Output VS Code problem matcher format
        severity_names = {1: "error", 2: "warning", 3: "info", 4: "hint"}
        
        # Print status to stderr so it doesn't interfere with problem matcher
        print(f"🤖 Analyzing {Path(file_path).name}...", file=sys.stderr)
        if analyzer.last_provider:
            print(f"✅ Using provider: {analyzer.last_provider}", file=sys.stderr)
        if diagnostics:
            print(f"📊 Found {len(diagnostics)} issue(s)", file=sys.stderr)
        else:
            print("✅ No issues found!", file=sys.stderr)
        print("", file=sys.stderr)  # Empty line
        
        for diag in diagnostics:
            severity = severity_names.get(diag["severity"], "warning")
            line = diag["line"] + 1  # Convert back to 1-indexed for display
            col = diag["column"] + 1
            message = diag["message"].replace('\n', ' ').replace('\r', '')
            
            # VS Code problem matcher format (to stdout)
            print(f"{file_path}:{line}:{col}: {severity}: {message}")
        
        # Also save JSON for programmatic use
        json_output = {
            "file": str(file_path),
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat(),
            "provider": analyzer.last_provider,
            "response_time": analyzer.last_response_time
        }
        
        json_file = file_path_obj.with_suffix(file_path_obj.suffix + '.diagnostics.json')
        with open(json_file, 'w') as f:
            json.dump(json_output, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cursor_ai_diagnostics.py <file_path> [json]", file=sys.stderr)
        print("  file_path: Path to Python file to analyze", file=sys.stderr)
        print("  json: Optional - output JSON instead of diagnostics format", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_format = "json" if len(sys.argv) > 2 and sys.argv[2] == "json" else "diagnostics"
    
    asyncio.run(analyze_file_cli(file_path, output_format))

