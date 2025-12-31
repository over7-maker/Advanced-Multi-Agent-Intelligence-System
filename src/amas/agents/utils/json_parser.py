"""
Robust JSON Parser
Multiple parsing strategies with validation and retry logic
"""

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class JSONParser:
    """
    Robust JSON parser with multiple strategies and validation
    """
    
    @staticmethod
    def parse(
        text: str,
        schema: Optional[Dict[str, Any]] = None,
        retry_with_ai: bool = False,
        ai_router = None
    ) -> Dict[str, Any]:
        """
        Parse JSON from text using multiple strategies
        
        Args:
            text: Text to parse
            schema: Optional JSON schema for validation
            retry_with_ai: Whether to retry with AI if parsing fails
            ai_router: AI router for retry (if retry_with_ai is True)
            
        Returns:
            Parsed JSON as dict
        """
        # Strategy 1: Direct JSON parsing
        try:
            if text.strip().startswith('{') or text.strip().startswith('['):
                parsed = json.loads(text.strip())
                if schema:
                    JSONParser._validate_schema(parsed, schema)
                return {"success": True, "data": parsed, "strategy": "direct"}
        except json.JSONDecodeError as e:
            logger.debug(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Extract JSON from markdown code blocks
        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                if schema:
                    JSONParser._validate_schema(parsed, schema)
                return {"success": True, "data": parsed, "strategy": "markdown_code_block"}
        except (json.JSONDecodeError, AttributeError) as e:
            logger.debug(f"Markdown code block extraction failed: {e}")
        
        # Strategy 3: Find JSON object/array in text
        try:
            # Find first { or [
            start_idx = text.find('{')
            if start_idx == -1:
                start_idx = text.find('[')
            
            if start_idx != -1:
                # Find matching closing bracket
                bracket_count = 0
                in_string = False
                escape_next = False
                
                for i in range(start_idx, len(text)):
                    char = text[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string:
                        if char == '{' or char == '[':
                            bracket_count += 1
                        elif char == '}' or char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                json_str = text[start_idx:i+1]
                                parsed = json.loads(json_str)
                                if schema:
                                    JSONParser._validate_schema(parsed, schema)
                                return {"success": True, "data": parsed, "strategy": "text_extraction"}
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Text extraction failed: {e}")
        
        # Strategy 4: Try to fix common JSON issues
        try:
            fixed_text = JSONParser._fix_common_issues(text)
            parsed = json.loads(fixed_text)
            if schema:
                JSONParser._validate_schema(parsed, schema)
            return {"success": True, "data": parsed, "strategy": "fixed"}
        except Exception as e:
            logger.debug(f"JSON fixing failed: {e}")
        
        # Strategy 5: Retry with AI if enabled
        if retry_with_ai and ai_router:
            try:
                retry_prompt = f"""The following text should contain JSON but parsing failed. 
Please extract and return ONLY valid JSON, nothing else:

{text[:2000]}

Return valid JSON:"""
                
                ai_response = ai_router.generate_with_fallback(
                    prompt=retry_prompt,
                    max_tokens=2000,
                    temperature=0.1,
                    system_prompt="You are a JSON extraction assistant. Return only valid JSON.",
                    strategy="quality_first"
                )
                
                # Try to parse AI response
                parsed = json.loads(ai_response.content)
                if schema:
                    JSONParser._validate_schema(parsed, schema)
                return {"success": True, "data": parsed, "strategy": "ai_retry"}
            except Exception as e:
                logger.warning(f"AI retry failed: {e}")
        
        # Strategy 6: Partial parsing - extract what we can
        try:
            partial_data = JSONParser._extract_partial_json(text)
            return {"success": False, "data": partial_data, "strategy": "partial", "error": "Incomplete JSON"}
        except Exception as e:
            logger.debug(f"Partial extraction failed: {e}")
        
        # All strategies failed
        return {
            "success": False,
            "data": None,
            "strategy": "failed",
            "error": "All parsing strategies failed",
            "raw_text": text[:500]  # First 500 chars for debugging
        }
    
    @staticmethod
    def _fix_common_issues(text: str) -> str:
        """Fix common JSON issues"""
        fixed = text
        
        # Remove trailing commas
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix single quotes to double quotes
        fixed = re.sub(r"'([^']*)'", r'"\1"', fixed)
        
        # Fix unquoted keys
        fixed = re.sub(r'(\w+):', r'"\1":', fixed)
        
        # Remove comments
        fixed = re.sub(r'//.*?$', '', fixed, flags=re.MULTILINE)
        fixed = re.sub(r'/\*.*?\*/', '', fixed, flags=re.DOTALL)
        
        return fixed
    
    @staticmethod
    def _extract_partial_json(text: str) -> Dict[str, Any]:
        """Extract partial JSON data"""
        partial = {}
        
        # Try to extract key-value pairs
        key_value_pattern = r'"([^"]+)"\s*:\s*"([^"]+)"'
        matches = re.findall(key_value_pattern, text)
        for key, value in matches:
            partial[key] = value
        
        # Try to extract numeric values
        numeric_pattern = r'"([^"]+)"\s*:\s*(\d+\.?\d*)'
        matches = re.findall(numeric_pattern, text)
        for key, value in matches:
            try:
                partial[key] = float(value) if '.' in value else int(value)
            except ValueError:
                pass
        
        return partial
    
    @staticmethod
    def _validate_schema(data: Any, schema: Dict[str, Any]) -> bool:
        """
        Basic schema validation
        
        For full validation, use jsonschema library
        """
        # Basic type checking
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                raise ValueError(f"Expected object, got {type(data).__name__}")
            elif expected_type == "array" and not isinstance(data, list):
                raise ValueError(f"Expected array, got {type(data).__name__}")
        
        # Check required fields
        if "required" in schema and isinstance(data, dict):
            for field in schema["required"]:
                if field not in data:
                    raise ValueError(f"Required field '{field}' is missing")
        
        return True
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """
        Convenience method to extract JSON from text
        
        Returns:
            Parsed JSON dict or None if parsing failed
        """
        result = JSONParser.parse(text)
        if result["success"]:
            return result["data"]
        return None

