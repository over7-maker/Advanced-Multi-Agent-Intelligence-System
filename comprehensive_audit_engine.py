#!/usr/bin/env python3
"""
Comprehensive Audit Engine
Advanced audit system for workflows and codebase
"""

import os
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class ComprehensiveAuditEngine:
    """
    Comprehensive audit engine for workflows and codebase
    """
    
    def __init__(self):
        """Initialize the audit engine"""
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "audit_type": "comprehensive",
            "issues": [],
            "statistics": {},
            "recommendations": []
        }
        
        # Define audit patterns
        self.patterns = {
            "direct_api_usage": r'os\.environ\.get\([\'\"]([A-Z_]+_API_KEY)[\'\"]?\)|os\.getenv\([\'\"]([A-Z_]+_API_KEY)[\'\"]?\)',
            "exposed_secrets": r'password\s*=\s*[\'\"][^\'\"]+[\'\"]|token\s*=\s*[\'\"][^\'\"]+[\'\"]',
            "insecure_patterns": r'eval\s*\(|exec\s*\(|pickle\.loads?\s*\(',
            "yaml_syntax": r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*$'
        }
        
        print("🔍 Comprehensive Audit Engine initialized")
    
    def audit_workflow_files(self) -> Dict[str, Any]:
        """Audit workflow files for issues"""
        print("🔍 Auditing workflow files...")
        
        workflow_dir = Path(".github/workflows")
        issues = []
        
        if not workflow_dir.exists():
            return {
                "status": "error",
                "message": "Workflow directory not found",
                "issues": []
            }
        
        for workflow_file in workflow_dir.glob("*.yml"):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    yaml_data = yaml.safe_load(content)
                
                # Check for basic structure
                if not isinstance(yaml_data, dict):
                    issues.append({
                        "file": str(workflow_file),
                        "type": "yaml_structure",
                        "severity": "high",
                        "message": "Invalid YAML structure"
                    })
                    continue
                
                # Check for required fields
                if "on" not in yaml_data:
                    issues.append({
                        "file": str(workflow_file),
                        "type": "missing_trigger",
                        "severity": "high",
                        "message": "Missing 'on' trigger section"
                    })
                
                if "jobs" not in yaml_data:
                    issues.append({
                        "file": str(workflow_file),
                        "type": "missing_jobs",
                        "severity": "high",
                        "message": "Missing 'jobs' section"
                    })
                
                # Check for direct API key usage
                api_matches = re.findall(self.patterns["direct_api_usage"], content)
                if api_matches:
                    issues.append({
                        "file": str(workflow_file),
                        "type": "direct_api_usage",
                        "severity": "medium",
                        "message": f"Direct API key usage found: {api_matches}",
                        "details": api_matches
                    })
                
            except yaml.YAMLError as e:
                issues.append({
                    "file": str(workflow_file),
                    "type": "yaml_syntax",
                    "severity": "high",
                    "message": f"YAML syntax error: {str(e)}"
                })
            except Exception as e:
                issues.append({
                    "file": str(workflow_file),
                    "type": "file_error",
                    "severity": "medium",
                    "message": f"Error reading file: {str(e)}"
                })
        
        return {
            "status": "completed",
            "issues": issues,
            "total_files": len(list(workflow_dir.glob("*.yml"))),
            "issues_found": len(issues)
        }
    
    def audit_python_files(self) -> Dict[str, Any]:
        """Audit Python files for issues"""
        print("🔍 Auditing Python files...")
        
        issues = []
        python_files = []
        
        # Find Python files
        for root, dirs, files in os.walk("."):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for python_file in python_files:
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for direct API key usage
                api_matches = re.findall(self.patterns["direct_api_usage"], content)
                if api_matches:
                    issues.append({
                        "file": python_file,
                        "type": "direct_api_usage",
                        "severity": "medium",
                        "message": f"Direct API key usage found: {api_matches}",
                        "details": api_matches
                    })
                
                # Check for exposed secrets
                secret_matches = re.findall(self.patterns["exposed_secrets"], content)
                if secret_matches:
                    issues.append({
                        "file": python_file,
                        "type": "exposed_secrets",
                        "severity": "high",
                        "message": f"Exposed secrets found: {secret_matches}",
                        "details": secret_matches
                    })
                
                # Check for insecure patterns
                insecure_matches = re.findall(self.patterns["insecure_patterns"], content)
                if insecure_matches:
                    issues.append({
                        "file": python_file,
                        "type": "insecure_patterns",
                        "severity": "medium",
                        "message": f"Insecure patterns found: {insecure_matches}",
                        "details": insecure_matches
                    })
                
            except Exception as e:
                issues.append({
                    "file": python_file,
                    "type": "file_error",
                    "severity": "low",
                    "message": f"Error reading file: {str(e)}"
                })
        
        return {
            "status": "completed",
            "issues": issues,
            "total_files": len(python_files),
            "issues_found": len(issues)
        }
    
    def audit_api_integration(self) -> Dict[str, Any]:
        """Audit API integration"""
        print("🔍 Auditing API integration...")
        
        issues = []
        
        # Check for API manager files
        api_manager_files = [
            "standalone_universal_ai_manager.py",
            "ultimate_16_api_fallback_manager.py",
            "universal_ai_workflow_integration.py"
        ]
        
        for file in api_manager_files:
            if not os.path.exists(file):
                issues.append({
                    "file": file,
                    "type": "missing_file",
                    "severity": "high",
                    "message": f"Required API manager file missing: {file}"
                })
        
        # Check for API key usage patterns
        workflow_dir = Path(".github/workflows")
        if workflow_dir.exists():
            for workflow_file in workflow_dir.glob("*.yml"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if using secrets properly
                    if "secrets." in content and "get_api_key" not in content:
                        issues.append({
                            "file": str(workflow_file),
                            "type": "api_integration",
                            "severity": "medium",
                            "message": "Workflow not using centralized API manager"
                        })
                
                except Exception as e:
                    issues.append({
                        "file": str(workflow_file),
                        "type": "file_error",
                        "severity": "low",
                        "message": f"Error reading workflow: {str(e)}"
                    })
        
        return {
            "status": "completed",
            "issues": issues,
            "total_checks": len(api_manager_files) + len(list(workflow_dir.glob("*.yml"))) if workflow_dir.exists() else len(api_manager_files),
            "issues_found": len(issues)
        }
    
    def audit_security(self) -> Dict[str, Any]:
        """Audit security issues"""
        print("🔍 Auditing security...")
        
        issues = []
        
        # Check for common security issues
        security_patterns = {
            "hardcoded_passwords": r'password\s*=\s*[\'\"][^\'\"]+[\'\"]',
            "hardcoded_tokens": r'token\s*=\s*[\'\"][^\'\"]+[\'\"]',
            "insecure_functions": r'eval\s*\(|exec\s*\(|pickle\.loads?\s*\(',
            "sql_injection": r'execute\s*\(\s*[\'\"].*%.*[\'\"]',
            "path_traversal": r'open\s*\(\s*[\'\"].*\.\./.*[\'\"]'
        }
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.yml', '.yaml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for pattern_name, pattern in security_patterns.items():
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                issues.append({
                                    "file": file_path,
                                    "type": pattern_name,
                                    "severity": "high",
                                    "message": f"Security issue found: {pattern_name}",
                                    "details": matches[:5]  # Limit to first 5 matches
                                })
                    
                    except Exception as e:
                        issues.append({
                            "file": file_path,
                            "type": "file_error",
                            "severity": "low",
                            "message": f"Error reading file: {str(e)}"
                        })
        
        return {
            "status": "completed",
            "issues": issues,
            "total_files_checked": len([f for f in os.walk(".") if f[2]]),
            "issues_found": len(issues)
        }
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit"""
        print("🚀 Running comprehensive audit...")
        print("=" * 50)
        
        # Run all audit types
        workflow_audit = self.audit_workflow_files()
        python_audit = self.audit_python_files()
        api_audit = self.audit_api_integration()
        security_audit = self.audit_security()
        
        # Compile results
        all_issues = []
        all_issues.extend(workflow_audit.get("issues", []))
        all_issues.extend(python_audit.get("issues", []))
        all_issues.extend(api_audit.get("issues", []))
        all_issues.extend(security_audit.get("issues", []))
        
        # Categorize issues by severity
        critical_issues = [i for i in all_issues if i.get("severity") == "high"]
        medium_issues = [i for i in all_issues if i.get("severity") == "medium"]
        low_issues = [i for i in all_issues if i.get("severity") == "low"]
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_issues)
        
        # Update audit results
        self.audit_results.update({
            "workflow_audit": workflow_audit,
            "python_audit": python_audit,
            "api_audit": api_audit,
            "security_audit": security_audit,
            "issues": all_issues,
            "statistics": {
                "total_issues": len(all_issues),
                "critical_issues": len(critical_issues),
                "medium_issues": len(medium_issues),
                "low_issues": len(low_issues),
                "workflow_files": workflow_audit.get("total_files", 0),
                "python_files": python_audit.get("total_files", 0)
            },
            "recommendations": recommendations
        })
        
        return self.audit_results
    
    def generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = 0
            issue_types[issue_type] += 1
        
        # Generate recommendations
        if issue_types.get("direct_api_usage", 0) > 0:
            recommendations.append("Migrate direct API key usage to centralized manager")
        
        if issue_types.get("exposed_secrets", 0) > 0:
            recommendations.append("Remove hardcoded secrets and use environment variables")
        
        if issue_types.get("yaml_syntax", 0) > 0:
            recommendations.append("Fix YAML syntax errors in workflow files")
        
        if issue_types.get("insecure_patterns", 0) > 0:
            recommendations.append("Replace insecure code patterns with safer alternatives")
        
        if issue_types.get("missing_file", 0) > 0:
            recommendations.append("Create missing required files")
        
        return recommendations
    
    def save_audit_results(self, filename: str = None) -> str:
        """Save audit results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_audit_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Audit results saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving audit results: {e}")
            return ""
    
    def print_summary(self):
        """Print audit summary"""
        stats = self.audit_results.get("statistics", {})
        
        print("\n📊 AUDIT SUMMARY")
        print("=" * 30)
        print(f"Total Issues: {stats.get('total_issues', 0)}")
        print(f"Critical Issues: {stats.get('critical_issues', 0)}")
        print(f"Medium Issues: {stats.get('medium_issues', 0)}")
        print(f"Low Issues: {stats.get('low_issues', 0)}")
        print(f"Workflow Files: {stats.get('workflow_files', 0)}")
        print(f"Python Files: {stats.get('python_files', 0)}")
        
        if self.audit_results.get("recommendations"):
            print("\n🎯 RECOMMENDATIONS:")
            for i, rec in enumerate(self.audit_results["recommendations"], 1):
                print(f"{i}. {rec}")

def main():
    """Main function for testing"""
    print("🔍 COMPREHENSIVE AUDIT ENGINE TEST")
    print("=" * 40)
    
    # Create audit engine
    engine = ComprehensiveAuditEngine()
    
    # Run comprehensive audit
    results = engine.run_comprehensive_audit()
    
    # Print summary
    engine.print_summary()
    
    # Save results
    filename = engine.save_audit_results()
    
    print(f"\n✅ Audit completed!")
    print(f"📁 Results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    main()