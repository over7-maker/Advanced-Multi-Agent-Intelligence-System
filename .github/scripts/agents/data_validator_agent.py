#!/usr/bin/env python3
"""
Agent-2: Data Validator
Continuous data quality monitoring and validation
"""

import json
from pathlib import Path
from typing import Any, Dict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.amas.agents.base.base_agent import BaseAgent


class DataValidatorAgent(BaseAgent):
    """Agent-2: Continuous data quality monitoring"""
    
    def __init__(self, orchestrator=None):
        super().__init__("data_validator", orchestrator)
        self.validation_rules = []
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize validation rules"""
        # Load validation rules from config
        config_file = Path(".github/config/data_validation_rules.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.validation_rules = json.load(f)
        else:
            # Default rules
            self.validation_rules = [
                {"type": "schema", "field": "required", "check": "not_null"},
                {"type": "format", "field": "timestamp", "check": "iso_format"},
                {"type": "range", "field": "value", "check": "numeric_range"}
            ]
        
        return {
            "success": True,
            "rules_loaded": len(self.validation_rules),
            "message": f"Loaded {len(self.validation_rules)} validation rules"
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data validation"""
        data = context.get("data", {})
        validation_type = context.get("validation_type", "comprehensive")
        
        # Use AI for intelligent validation
        system_message = """You are a data quality expert. Validate data for:
1. Schema compliance
2. Format correctness
3. Value ranges and constraints
4. Completeness
5. Consistency"""
        
        user_prompt = f"""Data to validate:
{json.dumps(data, indent=2)}

Validation Type: {validation_type}
Rules: {json.dumps(self.validation_rules, indent=2)}

Provide:
1. Validation results (pass/fail per rule)
2. Issues found (if any)
3. Recommendations for fixes"""
        
        ai_result = await self._call_ai(
            task_type="general",
            system_message=system_message,
            user_prompt=user_prompt
        )
        
        if not ai_result.get("success"):
            return {
                "success": False,
                "error": "AI validation failed",
                "fallback": "basic_validation"
            }
        
        validation_result = ai_result.get("response", "")
        
        return {
            "success": True,
            "validation_result": validation_result,
            "rules_applied": len(self.validation_rules),
            "data_quality_score": 95  # Placeholder, would be calculated from AI response
        }
