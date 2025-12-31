"""
Code Analysis Tools
Implementations for code quality tools: Pylint, Flake8
"""

import logging
import subprocess
from typing import Any, Dict

from . import AgentTool

logger = logging.getLogger(__name__)


class PylintTool(AgentTool):
    """Pylint Python code quality analyzer"""
    
    def __init__(self):
        super().__init__(
            name="pylint",
            description="Python code quality analyzer"
        )
        self.category = "code_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "File or directory to analyze"},
                "output_format": {"type": "string", "enum": ["text", "json"], "default": "json"}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Pylint analysis"""
        try:
            target = params.get("target")
            output_format = params.get("output_format", "json")
            
            # Check if pylint is installed
            try:
                subprocess.run(["pylint", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Pylint not installed. Install with: pip install pylint"}
            
            # Run pylint
            cmd = ["pylint", target]
            if output_format == "json":
                cmd.extend(["--output-format", "json"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Pylint returns non-zero if issues found, but that's success for us
            if output_format == "json":
                import json
                try:
                    data = json.loads(result.stdout) if result.stdout else []
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "issues": data if isinstance(data, list) else [],
                            "count": len(data) if isinstance(data, list) else 0
                        }
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "result": {
                            "target": target,
                            "issues": [],
                            "count": 0,
                            "raw_output": result.stdout
                        }
                    }
            else:
                return {
                    "success": True,
                    "result": {
                        "target": target,
                        "output": result.stdout,
                        "stderr": result.stderr
                    }
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Pylint analysis timed out"}
        except Exception as e:
            logger.error(f"Pylint analysis failed: {e}")
            return {"success": False, "error": str(e)}


class Flake8Tool(AgentTool):
    """Flake8 Python style guide checker"""
    
    def __init__(self):
        super().__init__(
            name="flake8",
            description="Python style guide checker"
        )
        self.category = "code_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "File or directory to check"},
                "max_line_length": {"type": "integer", "default": 79}
            },
            "required": ["target"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Flake8 check"""
        try:
            target = params.get("target")
            max_line_length = params.get("max_line_length", 79)
            
            # Check if flake8 is installed
            try:
                subprocess.run(["flake8", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {"success": False, "error": "Flake8 not installed. Install with: pip install flake8"}
            
            # Run flake8
            cmd = ["flake8", "--max-line-length", str(max_line_length), target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Flake8 returns non-zero if issues found, but that's success for us
            issues = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        issues.append({
                            "file": parts[0],
                            "line": parts[1],
                            "column": parts[2],
                            "message": parts[3],
                            "code": parts[3].split()[0] if parts[3] else ""
                        })
            
            return {
                "success": True,
                "result": {
                    "target": target,
                    "issues": issues,
                    "count": len(issues)
                }
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Flake8 check timed out"}
        except Exception as e:
            logger.error(f"Flake8 check failed: {e}")
            return {"success": False, "error": str(e)}

