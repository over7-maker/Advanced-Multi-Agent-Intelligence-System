#!/usr/bin/env python3
"""
AI Security Auditor - Deep security vulnerability scanning with automated patch suggestions
Integrates additional AI security vulnerability scanning
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AISecurityAuditor:
    """AI-powered security vulnerability scanning and patch suggestions"""
    
    def __init__(self):
        self.security_report_file = "artifacts/security_audit_report.json"
        self.vulnerability_db_file = "artifacts/vulnerability_database.json"
        self.patch_suggestions_file = "artifacts/patch_suggestions.json"
        self.load_vulnerability_database()
    
    def load_vulnerability_database(self):
        """Load vulnerability database"""
        self.vulnerability_db = {
            "known_vulnerabilities": {},
            "security_patterns": {},
            "patch_templates": {},
            "last_updated": None
        }
        
        if os.path.exists(self.vulnerability_db_file):
            try:
                with open(self.vulnerability_db_file, 'r') as f:
                    self.vulnerability_db = json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading vulnerability database: {e}")
    
    def save_vulnerability_database(self):
        """Save vulnerability database"""
        self.vulnerability_db["last_updated"] = datetime.now().isoformat()
        os.makedirs("artifacts", exist_ok=True)
        with open(self.vulnerability_db_file, "w") as f:
            json.dump(self.vulnerability_db, f, indent=2)
    
    async def scan_codebase_security(self, target_path: str = ".") -> Dict[str, Any]:
        """Scan codebase for security vulnerabilities"""
        print(f"🔍 Scanning codebase for security vulnerabilities...")
        
        security_issues = []
        file_issues = {}
        
        # Common security patterns to check
        security_patterns = [
            {
                "pattern": r"password\s*=\s*['\"][^'\"]+['\"]",
                "type": "hardcoded_password",
                "severity": "high",
                "description": "Hardcoded password detected"
            },
            {
                "pattern": r"api_key\s*=\s*['\"][^'\"]+['\"]",
                "type": "hardcoded_api_key",
                "severity": "high",
                "description": "Hardcoded API key detected"
            },
            {
                "pattern": r"secret\s*=\s*['\"][^'\"]+['\"]",
                "type": "hardcoded_secret",
                "severity": "high",
                "description": "Hardcoded secret detected"
            },
            {
                "pattern": r"eval\s*\(",
                "type": "eval_usage",
                "severity": "critical",
                "description": "Use of eval() function detected"
            },
            {
                "pattern": r"exec\s*\(",
                "type": "exec_usage",
                "severity": "critical",
                "description": "Use of exec() function detected"
            },
            {
                "pattern": r"subprocess\.call\s*\([^)]*shell\s*=\s*True",
                "type": "shell_injection",
                "severity": "high",
                "description": "Potential shell injection vulnerability"
            },
            {
                "pattern": r"pickle\.loads?\s*\(",
                "type": "pickle_deserialization",
                "severity": "high",
                "description": "Unsafe pickle deserialization"
            },
            {
                "pattern": r"yaml\.load\s*\([^)]*Loader\s*=\s*None",
                "type": "yaml_deserialization",
                "severity": "medium",
                "description": "Unsafe YAML deserialization"
            },
            {
                "pattern": r"sql\s*=\s*f['\"][^'\"]*\{[^}]*\}[^'\"]*['\"]",
                "type": "sql_injection",
                "severity": "high",
                "description": "Potential SQL injection vulnerability"
            },
            {
                "pattern": r"open\s*\([^)]*mode\s*=\s*['\"]w['\"]",
                "type": "file_overwrite",
                "severity": "medium",
                "description": "Potential file overwrite vulnerability"
            }
        ]
        
        # Scan files
        for root, dirs, files in os.walk(target_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.php', '.rb')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for i, line in enumerate(lines, 1):
                                for pattern_info in security_patterns:
                                    import re
                                    if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                                        issue = {
                                            "file": file_path,
                                            "line": i,
                                            "code": line.strip(),
                                            "type": pattern_info['type'],
                                            "severity": pattern_info['severity'],
                                            "description": pattern_info['description'],
                                            "pattern": pattern_info['pattern']
                                        }
                                        security_issues.append(issue)
                                        
                                        if file_path not in file_issues:
                                            file_issues[file_path] = []
                                        file_issues[file_path].append(issue)
                    except Exception as e:
                        print(f"⚠️ Error scanning {file_path}: {e}")
        
        return {
            "total_issues": len(security_issues),
            "issues_by_severity": {
                "critical": len([i for i in security_issues if i['severity'] == 'critical']),
                "high": len([i for i in security_issues if i['severity'] == 'high']),
                "medium": len([i for i in security_issues if i['severity'] == 'medium']),
                "low": len([i for i in security_issues if i['severity'] == 'low'])
            },
            "issues_by_type": {},
            "file_issues": file_issues,
            "all_issues": security_issues
        }
    
    async def get_ai_security_analysis(self, security_scan: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI analysis of security vulnerabilities"""
        print("🤖 Getting AI security analysis...")
        
        # Create security analysis prompt
        prompt = f"""
As an expert cybersecurity analyst and penetration tester, analyze these security vulnerabilities and provide comprehensive remediation.

## Security Scan Results:
{json.dumps(security_scan, indent=2)}

## Analysis Tasks:
1. **Risk Assessment**: Evaluate the actual risk level of each vulnerability
2. **Exploit Analysis**: Determine how each vulnerability could be exploited
3. **Patch Suggestions**: Provide specific code fixes for each vulnerability
4. **Security Best Practices**: Recommend security improvements
5. **Priority Ranking**: Rank vulnerabilities by urgency

## Response Format:
Provide your analysis in this JSON format:
```json
{{
  "risk_assessment": {{
    "overall_risk_score": 0.85,
    "critical_issues": ["Issue 1", "Issue 2"],
    "high_priority_fixes": ["Fix 1", "Fix 2"]
  }},
  "vulnerability_analysis": {{
    "vulnerability_id": {{
      "risk_level": "high|medium|low",
      "exploit_difficulty": "easy|medium|hard",
      "impact": "Description of potential impact",
      "exploitation_vector": "How it could be exploited",
      "patch_priority": 1
    }}
  }},
  "patch_suggestions": {{
    "vulnerability_id": {{
      "code_fix": "Specific code fix",
      "alternative_solution": "Alternative approach",
      "prevention_tips": ["Tip 1", "Tip 2"],
      "testing_guidance": "How to test the fix"
    }}
  }},
  "security_recommendations": [
    "General security recommendation 1",
    "General security recommendation 2"
  ],
  "compliance_notes": {{
    "owasp_top_10": ["Relevant OWASP categories"],
    "cwe_mappings": ["CWE-79", "CWE-89"],
    "compliance_impact": "Impact on compliance requirements"
  }}
}}
```

Focus on actionable, specific fixes that can be implemented immediately.
"""
        
        try:
            result = await ai_agent.analyze_with_fallback(prompt, "security_analysis")
            
            if result.get('success'):
                # Extract JSON from response
                content = result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        security_analysis = json.loads(json_match.group(1))
                    else:
                        # Fallback analysis
                        security_analysis = {
                            "risk_assessment": {
                                "overall_risk_score": 0.7,
                                "critical_issues": ["Security issues detected"],
                                "high_priority_fixes": ["Fix security vulnerabilities"]
                            },
                            "vulnerability_analysis": {},
                            "patch_suggestions": {},
                            "security_recommendations": ["Implement security best practices"],
                            "compliance_notes": {
                                "owasp_top_10": ["A01:2021", "A03:2021"],
                                "cwe_mappings": ["CWE-79", "CWE-89"],
                                "compliance_impact": "High security risk"
                            }
                        }
                    
                    return {
                        "success": True,
                        "security_analysis": security_analysis,
                        "provider_used": result.get('provider_used'),
                        "response_time": result.get('response_time', 0)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse security analysis"
                    }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Security analysis failed')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in security analysis: {e}"
            }
    
    async def generate_security_patches(self, security_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated security patches"""
        print("🔧 Generating automated security patches...")
        
        if not security_analysis.get('success'):
            return {
                "success": False,
                "error": "No security analysis available"
            }
        
        patches = []
        patch_files = []
        
        analysis = security_analysis['security_analysis']
        patch_suggestions = analysis.get('patch_suggestions', {})
        
        for vuln_id, patch_info in patch_suggestions.items():
            try:
                # Create patch file
                patch_content = f"""# Security Patch for {vuln_id}
# Generated by AI Security Auditor
# Timestamp: {datetime.now().isoformat()}

## Vulnerability: {vuln_id}
## Risk Level: {patch_info.get('risk_level', 'unknown')}
## Exploit Difficulty: {patch_info.get('exploit_difficulty', 'unknown')}

## Code Fix:
```python
{patch_info.get('code_fix', 'No specific fix provided')}
```

## Alternative Solution:
```python
{patch_info.get('alternative_solution', 'No alternative provided')}
```

## Prevention Tips:
{chr(10).join([f"- {tip}" for tip in patch_info.get('prevention_tips', [])])}

## Testing Guidance:
{patch_info.get('testing_guidance', 'No testing guidance provided')}

## Implementation Notes:
- Review the fix before applying
- Test in a safe environment first
- Consider the impact on existing functionality
- Update security documentation

---
*Generated by AI Security Auditor*
"""
                
                patch_file = f"artifacts/security_patch_{vuln_id}.md"
                with open(patch_file, 'w') as f:
                    f.write(patch_content)
                
                patches.append({
                    "vulnerability_id": vuln_id,
                    "patch_file": patch_file,
                    "risk_level": patch_info.get('risk_level', 'unknown'),
                    "priority": patch_info.get('patch_priority', 1)
                })
                patch_files.append(patch_file)
                
                print(f"✅ Generated patch for {vuln_id}")
                
            except Exception as e:
                print(f"❌ Failed to generate patch for {vuln_id}: {e}")
        
        return {
            "success": True,
            "patches": patches,
            "patch_files": patch_files,
            "total_patches": len(patches)
        }
    
    async def generate_security_report(self, security_scan: Dict[str, Any], security_analysis: Dict[str, Any], patches: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security audit report"""
        print("📊 Generating security audit report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "audit_type": "ai_security_audit",
            "summary": {
                "total_vulnerabilities": security_scan.get('total_issues', 0),
                "critical_issues": security_scan.get('issues_by_severity', {}).get('critical', 0),
                "high_issues": security_scan.get('issues_by_severity', {}).get('high', 0),
                "medium_issues": security_scan.get('issues_by_severity', {}).get('medium', 0),
                "low_issues": security_scan.get('issues_by_severity', {}).get('low', 0),
                "patches_generated": patches.get('total_patches', 0),
                "ai_analysis_success": security_analysis.get('success', False)
            },
            "vulnerability_details": security_scan.get('all_issues', []),
            "ai_analysis": security_analysis.get('security_analysis', {}),
            "generated_patches": patches.get('patches', []),
            "recommendations": [],
            "compliance_status": {}
        }
        
        # Add AI recommendations
        if security_analysis.get('success'):
            ai_analysis = security_analysis['security_analysis']
            report["recommendations"].extend(ai_analysis.get('security_recommendations', []))
            report["compliance_status"] = ai_analysis.get('compliance_notes', {})
        
        # Generate additional recommendations
        if report["summary"]["critical_issues"] > 0:
            report["recommendations"].append("URGENT: Address critical security vulnerabilities immediately")
        
        if report["summary"]["high_issues"] > 5:
            report["recommendations"].append("High number of high-severity issues - prioritize security fixes")
        
        if report["summary"]["patches_generated"] == 0:
            report["recommendations"].append("No patches generated - review security analysis")
        
        return report

async def main():
    """Main function to run AI security auditor"""
    print("🛡️ AI Security Auditor Starting...")
    print("=" * 60)
    
    auditor = AISecurityAuditor()
    
    try:
        # Step 1: Scan codebase for security issues
        security_scan = await auditor.scan_codebase_security()
        print(f"🔍 Found {security_scan['total_issues']} security issues")
        print(f"  - Critical: {security_scan['issues_by_severity']['critical']}")
        print(f"  - High: {security_scan['issues_by_severity']['high']}")
        print(f"  - Medium: {security_scan['issues_by_severity']['medium']}")
        print(f"  - Low: {security_scan['issues_by_severity']['low']}")
        
        # Step 2: Get AI security analysis
        security_analysis = await auditor.get_ai_security_analysis(security_scan)
        
        if security_analysis.get('success'):
            print(f"✅ AI security analysis completed using {security_analysis.get('provider_used')}")
            
            # Step 3: Generate security patches
            patches = await auditor.generate_security_patches(security_analysis)
            
            if patches.get('success'):
                print(f"🔧 Generated {patches['total_patches']} security patches")
            else:
                print(f"❌ Failed to generate patches: {patches.get('error')}")
        else:
            print(f"❌ AI security analysis failed: {security_analysis.get('error')}")
            patches = {"success": False, "patches": [], "total_patches": 0}
        
        # Step 4: Generate comprehensive report
        report = await auditor.generate_security_report(security_scan, security_analysis, patches)
        
        # Save report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/security_audit_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SECURITY AUDIT REPORT")
        print("=" * 60)
        print(f"🔍 Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
        print(f"🚨 Critical Issues: {report['summary']['critical_issues']}")
        print(f"⚠️ High Issues: {report['summary']['high_issues']}")
        print(f"📝 Patches Generated: {report['summary']['patches_generated']}")
        print(f"🤖 AI Analysis: {'✅ Success' if report['summary']['ai_analysis_success'] else '❌ Failed'}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations'][:5]:  # Show first 5
                print(f"  - {rec}")
        
        return report
        
    except Exception as e:
        print(f"❌ Critical error in security auditor: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())