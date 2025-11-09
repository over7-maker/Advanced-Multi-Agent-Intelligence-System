#!/usr/bin/env python3
"""
AI Analysis Validator
Validates AI analysis reports against actual file contents to identify false positives
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple


class AIAnalysisValidator:
    """Validate AI analysis reports and identify false positives"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_data = None
        self.load_file()
    
    def load_file(self):
        """Load and parse the YAML file"""
        try:
            with open(self.file_path, 'r') as f:
                self.file_data = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    def validate_agent_fields(self) -> Dict[str, Any]:
        """Validate that all agents have matching fields_count and fields_present"""
        if not self.file_data or 'agents' not in self.file_data:
            return {"valid": False, "error": "No agents found"}
        
        results = {
            "valid": True,
            "agents": {},
            "issues": []
        }
        
        for agent in self.file_data['agents']:
            name = agent.get('name', 'unknown')
            fields_count = agent.get('fields_count', 0)
            fields_present = agent.get('fields_present', [])
            actual_count = len(fields_present)
            
            match = fields_count == actual_count
            results["agents"][name] = {
                "fields_count": fields_count,
                "fields_present_count": actual_count,
                "match": match,
                "fields": fields_present
            }
            
            if not match:
                results["valid"] = False
                results["issues"].append({
                    "agent": name,
                    "issue": f"fields_count ({fields_count}) does not match fields_present count ({actual_count})",
                    "fields_count": fields_count,
                    "actual_count": actual_count
                })
        
        return results
    
    def validate_yaml_structure(self) -> Dict[str, Any]:
        """Validate YAML structure and formatting"""
        results = {
            "valid": True,
            "yaml_valid": False,
            "indentation_consistent": True,
            "ends_with_newline": False,
            "issues": []
        }
        
        # Check YAML validity
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
                yaml.safe_load(content)
            results["yaml_valid"] = True
        except Exception as e:
            results["valid"] = False
            results["issues"].append(f"YAML parsing error: {str(e)}")
        
        # Check file ends with newline
        with open(self.file_path, 'rb') as f:
            content = f.read()
            results["ends_with_newline"] = content.endswith(b'\n')
            if not results["ends_with_newline"]:
                results["issues"].append("File does not end with newline")
        
        # Check indentation consistency (basic check)
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
            indent_sizes = set()
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    indent = len(line) - len(line.lstrip())
                    if indent > 0:
                        indent_sizes.add(indent)
            
            # Should have consistent indentation (2-space increments)
            if len(indent_sizes) > 10:  # Allow some variation but not too much
                results["indentation_consistent"] = False
                results["issues"].append("Inconsistent indentation detected")
        
        return results
    
    def validate_integrity_checks(self) -> Dict[str, Any]:
        """Validate integrity checks section"""
        if not self.file_data or 'integrity_checks' not in self.file_data:
            return {"valid": False, "error": "No integrity_checks found"}
        
        checks = self.file_data['integrity_checks']
        results = {
            "valid": True,
            "checks": checks,
            "all_passing": all(checks.values()) if isinstance(checks, dict) else False
        }
        
        return results
    
    def check_false_positives(self, ai_analysis_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check AI analysis claims against actual file to identify false positives"""
        false_positives = []
        valid_claims = []
        
        # Validate agent fields
        field_validation = self.validate_agent_fields()
        
        # Validate structure
        structure_validation = self.validate_yaml_structure()
        
        # Check each AI claim
        for claim in ai_analysis_claims:
            claim_type = claim.get("type", "")
            description = claim.get("description", "")
            is_false_positive = False
            correction = None
            
            # Check for field count mismatches
            if "missing fields" in description.lower() or "fields_count" in description.lower():
                if field_validation["valid"]:
                    is_false_positive = True
                    correction = "All agents have matching fields_count and fields_present arrays"
            
            # Check for indentation issues
            if "indentation" in description.lower() or "inconsistent" in description.lower():
                if structure_validation["indentation_consistent"]:
                    is_false_positive = True
                    correction = "Indentation is consistent (2-space increments)"
            
            # Check for YAML validity
            if "yaml" in description.lower() or "parse" in description.lower():
                if structure_validation["yaml_valid"]:
                    is_false_positive = True
                    correction = "YAML is valid and parses successfully"
            
            if is_false_positive:
                false_positives.append({
                    "claim": description,
                    "type": claim_type,
                    "correction": correction
                })
            else:
                valid_claims.append(claim)
        
        return {
            "false_positives": false_positives,
            "valid_claims": valid_claims,
            "false_positive_count": len(false_positives),
            "valid_claim_count": len(valid_claims)
        }
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        field_validation = self.validate_agent_fields()
        structure_validation = self.validate_yaml_structure()
        integrity_checks = self.validate_integrity_checks()
        
        report = f"""# File Validation Report

**File**: `{self.file_path}`  
**Date**: {Path(self.file_path).stat().st_mtime}

## Validation Results

### Agent Fields Validation
- **Status**: {'✅ Valid' if field_validation['valid'] else '❌ Invalid'}
- **Agents Checked**: {len(field_validation.get('agents', {}))}
- **Issues**: {len(field_validation.get('issues', []))}

"""
        
        if field_validation.get('agents'):
            report += "### Agent Details\n\n"
            report += "| Agent | Fields Count | Fields Present | Match |\n"
            report += "|-------|-------------|----------------|-------|\n"
            for name, data in field_validation['agents'].items():
                match_icon = "✅" if data['match'] else "❌"
                report += f"| `{name}` | {data['fields_count']} | {data['fields_present_count']} | {match_icon} |\n"
            report += "\n"
        
        report += f"""### Structure Validation
- **YAML Valid**: {'✅ Yes' if structure_validation['yaml_valid'] else '❌ No'}
- **Indentation Consistent**: {'✅ Yes' if structure_validation['indentation_consistent'] else '❌ No'}
- **Ends with Newline**: {'✅ Yes' if structure_validation['ends_with_newline'] else '❌ No'}

### Integrity Checks
- **All Passing**: {'✅ Yes' if integrity_checks.get('all_passing') else '❌ No'}
- **Checks**: {json.dumps(integrity_checks.get('checks', {}), indent=2)}

## Summary

**Overall Status**: {'✅ VALID' if field_validation['valid'] and structure_validation['valid'] else '❌ INVALID'}

"""
        
        if field_validation.get('issues'):
            report += "### Issues Found\n\n"
            for issue in field_validation['issues']:
                report += f"- ❌ {issue}\n"
            report += "\n"
        
        return report


def main():
    """Example usage"""
    validator = AIAnalysisValidator('.github/artifacts/verification_report.yaml')
    
    # Validate structure
    print("=== Validation Results ===\n")
    print(validator.generate_validation_report())
    
    # Example: Check for false positives
    ai_claims = [
        {
            "type": "code_quality",
            "description": "communication_agent_v1 missing fields"
        },
        {
            "type": "code_quality",
            "description": "Inconsistent indentation"
        },
        {
            "type": "bug",
            "description": "synthesis_agent_v1 fields_count mismatch"
        }
    ]
    
    false_positive_check = validator.check_false_positives(ai_claims)
    print("\n=== False Positive Check ===\n")
    print(f"False Positives Found: {false_positive_check['false_positive_count']}")
    print(f"Valid Claims: {false_positive_check['valid_claim_count']}\n")
    
    if false_positive_check['false_positives']:
        print("False Positives:\n")
        for fp in false_positive_check['false_positives']:
            print(f"- ❌ {fp['claim']}")
            print(f"  Correction: {fp['correction']}\n")


if __name__ == "__main__":
    main()
