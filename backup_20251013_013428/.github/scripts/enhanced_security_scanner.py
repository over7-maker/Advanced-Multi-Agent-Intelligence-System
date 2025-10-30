#!/usr/bin/env python3
"""
Enhanced Security Scanner - Layer 1 Agent
Advanced security vulnerability detection and analysis
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from openai import OpenAI


class EnhancedSecurityScanner:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Security results
        self.security_results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "security_issues": [],
            "compliance_issues": [],
            "recommendations": [],
            "risk_assessment": {},
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for security analysis"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "security_analysis"
            },
            {
                "name": "Claude",
                "key": os.environ.get("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-5-sonnet-20241022",
                "priority": 2,
                "specialization": "vulnerability_assessment"
            },
            {
                "name": "GPT-4",
                "key": os.environ.get("GPT4_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "priority": 3,
                "specialization": "compliance_analysis"
            }
        ]
        
        for provider in providers:
            if provider["key"]:
                try:
                    client = OpenAI(
                        base_url=provider["base_url"],
                        api_key=provider["key"]
                    )
                    clients.append({
                        "name": provider["name"],
                        "client": client,
                        "model": provider["model"],
                        "priority": provider["priority"],
                        "specialization": provider["specialization"],
                        "success_count": 0,
                        "failure_count": 0,
                        "avg_response_time": 0.0
                    })
                except Exception as e:
                    print(f"Failed to initialize {provider['name']}: {e}")
        
        return sorted(clients, key=lambda x: x["priority"])

    async def _analyze_with_ai(self, prompt: str, system_prompt: str, client_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze with specific AI client"""
        start_time = time.time()
        
        try:
            response = client_info["client"].chat.completions.create(
                model=client_info["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.2
            )
            
            response_time = time.time() - start_time
            client_info["success_count"] += 1
            if client_info["avg_response_time"] == 0:
                client_info["avg_response_time"] = response_time
            else:
                client_info["avg_response_time"] = (client_info["avg_response_time"] + response_time) / 2
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "response_time": response_time,
                "provider": client_info["name"],
                "model": client_info["model"]
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            client_info["failure_count"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "provider": client_info["name"]
            }

    def _run_static_security_tools(self) -> Dict[str, Any]:
        """Run static security analysis tools"""
        tools_results = {}
        
        try:
            # Run bandit for Python security issues
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", ".", "-f", "json"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                tools_results["bandit"] = {"status": "clean", "issues": []}
            else:
                try:
                    bandit_issues = json.loads(result.stdout)
                    tools_results["bandit"] = {"status": "issues_found", "issues": bandit_issues}
                except:
                    tools_results["bandit"] = {"status": "error", "output": result.stdout}
            
        except Exception as e:
            tools_results["bandit"] = {"status": "error", "error": str(e)}
        
        try:
            # Run safety for dependency vulnerabilities
            result = subprocess.run(
                ["python", "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                tools_results["safety"] = {"status": "clean", "vulnerabilities": []}
            else:
                try:
                    safety_issues = json.loads(result.stdout)
                    tools_results["safety"] = {"status": "vulnerabilities_found", "vulnerabilities": safety_issues}
                except:
                    tools_results["safety"] = {"status": "error", "output": result.stdout}
            
        except Exception as e:
            tools_results["safety"] = {"status": "error", "error": str(e)}
        
        return tools_results

    async def _analyze_code_security(self, file_path: str) -> Dict[str, Any]:
        """Analyze code security for a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file {file_path}: {e}"}
        
        system_prompt = """You are an expert cybersecurity analyst and vulnerability researcher.
        
        Your role is to:
        1. Identify security vulnerabilities and weaknesses in code
        2. Check for common security anti-patterns and vulnerabilities
        3. Assess compliance with security best practices
        4. Provide specific remediation recommendations
        5. Evaluate risk levels and potential impact
        
        Focus on:
        - SQL injection vulnerabilities
        - Cross-site scripting (XSS)
        - Authentication and authorization issues
        - Input validation problems
        - Cryptographic weaknesses
        - Information disclosure
        - Insecure direct object references
        - Security misconfigurations
        - Insecure deserialization
        - Known vulnerable components
        
        Provide your analysis in JSON format:
        {
            "vulnerabilities": [
                {
                    "type": "vulnerability_type",
                    "severity": "critical|high|medium|low",
                    "line": 123,
                    "description": "detailed description",
                    "cve": "CVE-XXXX-XXXX",
                    "cvss_score": 0.0-10.0,
                    "remediation": "how to fix",
                    "code_example": "fixed code example"
                }
            ],
            "security_issues": [
                {
                    "type": "issue_type",
                    "severity": "critical|high|medium|low",
                    "description": "description",
                    "remediation": "how to fix"
                }
            ],
            "compliance_issues": [
                {
                    "standard": "OWASP|NIST|ISO27001",
                    "requirement": "requirement description",
                    "status": "compliant|non_compliant",
                    "remediation": "how to fix"
                }
            ],
            "risk_assessment": {
                "overall_risk": "critical|high|medium|low",
                "data_exposure_risk": "high|medium|low",
                "system_compromise_risk": "high|medium|low",
                "business_impact": "high|medium|low"
            },
            "recommendations": [
                "immediate actions to take"
            ]
        }"""
        
        prompt = f"""Analyze the following code for security vulnerabilities and compliance issues:

File: {file_path}

```python
{content}
```

Please provide a comprehensive security analysis focusing on:
1. Common vulnerability patterns
2. Security best practices compliance
3. Risk assessment and impact analysis
4. Specific remediation recommendations
5. Code examples for fixes"""
        
        # Try each AI client
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    analysis = json.loads(result["content"])
                    analysis["provider"] = result["provider"]
                    analysis["response_time"] = result["response_time"]
                    return analysis
                except json.JSONDecodeError:
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_analysis": result["content"],
                        "vulnerabilities": [],
                        "security_issues": [],
                        "compliance_issues": [],
                        "risk_assessment": {"overall_risk": "medium"},
                        "recommendations": []
                    }
        
        return {"error": "All AI providers failed"}

    async def run_security_scan(self) -> Dict[str, Any]:
        """Run comprehensive security scan"""
        print("🔒 Enhanced Security Scanner Starting...")
        
        # Run static security tools
        print("Running static security tools...")
        tools_results = self._run_static_security_tools()
        self.security_results["static_tools"] = tools_results
        
        # Get Python files to analyze
        try:
            result = subprocess.run(
                ["find", ".", "-name", "*.py", "-type", "f"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            files = [f for f in result.stdout.strip().split('\n') if f and not any(
                skip in f for skip in [
                    '__pycache__', '.git', '.github', 'venv', 'env',
                    'node_modules', '.pytest_cache', 'build', 'dist'
                ]
            )]
            
            # Focus on important files
            priority_files = []
            for file in files:
                if any(important in file for important in [
                    'main.py', 'app.py', 'src/', 'api/', 'auth/', 'models/',
                    'handlers/', 'services/', 'utils/', 'config/'
                ]):
                    priority_files.append(file)
            
            files = priority_files[:15]  # Limit to 15 most important files
            
        except Exception as e:
            print(f"Error getting files: {e}")
            files = []
        
        print(f"Analyzing {len(files)} files for security issues...")
        
        # Analyze each file
        file_analyses = []
        for file_path in files:
            print(f"Analyzing {file_path}...")
            analysis = await self._analyze_code_security(file_path)
            analysis["file_path"] = file_path
            file_analyses.append(analysis)
            
            # Collect vulnerabilities and issues
            if "vulnerabilities" in analysis:
                for vuln in analysis["vulnerabilities"]:
                    vuln["file_path"] = file_path
                    self.security_results["vulnerabilities"].append(vuln)
            
            if "security_issues" in analysis:
                for issue in analysis["security_issues"]:
                    issue["file_path"] = file_path
                    self.security_results["security_issues"].append(issue)
            
            if "compliance_issues" in analysis:
                for compliance in analysis["compliance_issues"]:
                    compliance["file_path"] = file_path
                    self.security_results["compliance_issues"].append(compliance)
            
            if "recommendations" in analysis:
                self.security_results["recommendations"].extend(analysis["recommendations"])
        
        self.security_results["file_analyses"] = file_analyses
        
        # Calculate risk assessment
        critical_vulns = len([v for v in self.security_results["vulnerabilities"] if v.get("severity") == "critical"])
        high_vulns = len([v for v in self.security_results["vulnerabilities"] if v.get("severity") == "high"])
        medium_vulns = len([v for v in self.security_results["vulnerabilities"] if v.get("severity") == "medium"])
        
        if critical_vulns > 0:
            overall_risk = "critical"
        elif high_vulns > 2:
            overall_risk = "high"
        elif high_vulns > 0 or medium_vulns > 5:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        self.security_results["risk_assessment"] = {
            "overall_risk": overall_risk,
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "medium_vulnerabilities": medium_vulns,
            "total_vulnerabilities": len(self.security_results["vulnerabilities"]),
            "security_issues": len(self.security_results["security_issues"]),
            "compliance_issues": len(self.security_results["compliance_issues"]),
            "files_analyzed": len(files)
        }
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.security_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("security_scan_results.json", "w") as f:
            json.dump(self.security_results, f, indent=2)
        
        print(f"✅ Security Scan Complete!")
        print(f"   Overall Risk: {overall_risk.upper()}")
        print(f"   Critical Vulnerabilities: {critical_vulns}")
        print(f"   High Vulnerabilities: {high_vulns}")
        print(f"   Total Vulnerabilities: {len(self.security_results['vulnerabilities'])}")
        print(f"   Security Issues: {len(self.security_results['security_issues'])}")
        print(f"   Compliance Issues: {len(self.security_results['compliance_issues'])}")
        print(f"   Files Analyzed: {len(files)}")
        
        return self.security_results


async def main():
    """Main function"""
    scanner = EnhancedSecurityScanner()
    results = await scanner.run_security_scan()
    
    # Print summary
    print("\n" + "="*80)
    print("🔒 ENHANCED SECURITY SCANNER - SUMMARY")
    print("="*80)
    print(f"Overall Risk: {results['risk_assessment']['overall_risk'].upper()}")
    print(f"Critical Vulnerabilities: {results['risk_assessment']['critical_vulnerabilities']}")
    print(f"High Vulnerabilities: {results['risk_assessment']['high_vulnerabilities']}")
    print(f"Total Vulnerabilities: {results['risk_assessment']['total_vulnerabilities']}")
    print(f"Security Issues: {results['risk_assessment']['security_issues']}")
    print(f"Compliance Issues: {results['risk_assessment']['compliance_issues']}")
    print(f"Files Analyzed: {results['risk_assessment']['files_analyzed']}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())