#!/usr/bin/env python3
"""
Enhanced Dependency Auditor - Layer 1 Agent
Advanced dependency vulnerability and compatibility analysis
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


class EnhancedDependencyAuditor:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Audit results
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "dependencies": [],
            "vulnerabilities": [],
            "compatibility_issues": [],
            "outdated_packages": [],
            "recommendations": [],
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for dependency analysis"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "dependency_analysis"
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
                "specialization": "compatibility_analysis"
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

    def _get_dependencies(self) -> Dict[str, Any]:
        """Get project dependencies"""
        dependencies = {
            "requirements_txt": [],
            "pyproject_toml": [],
            "package_json": [],
            "pip_freeze": []
        }
        
        # Check requirements.txt
        if os.path.exists("/workspace/requirements.txt"):
            try:
                with open("/workspace/requirements.txt", "r") as f:
                    deps = f.read().strip().split('\n')
                    dependencies["requirements_txt"] = [d.strip() for d in deps if d.strip() and not d.startswith('#')]
            except Exception as e:
                print(f"Error reading requirements.txt: {e}")
        
        # Check pyproject.toml
        if os.path.exists("/workspace/pyproject.toml"):
            try:
                with open("/workspace/pyproject.toml", "r") as f:
                    content = f.read()
                    # Simple parsing for dependencies
                    if "[tool.poetry.dependencies]" in content:
                        deps_section = content.split("[tool.poetry.dependencies]")[1].split("[")[0]
                        deps = [d.strip() for d in deps_section.split('\n') if '=' in d and not d.startswith('#')]
                        dependencies["pyproject_toml"] = deps
            except Exception as e:
                print(f"Error reading pyproject.toml: {e}")
        
        # Get pip freeze output
        try:
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                deps = result.stdout.strip().split('\n')
                dependencies["pip_freeze"] = [d.strip() for d in deps if d.strip()]
        except Exception as e:
            print(f"Error running pip freeze: {e}")
        
        return dependencies

    def _run_dependency_tools(self) -> Dict[str, Any]:
        """Run dependency analysis tools"""
        tools_results = {}
        
        try:
            # Run safety check
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
        
        try:
            # Run pip-audit
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                tools_results["pip_audit"] = {"status": "clean", "vulnerabilities": []}
            else:
                try:
                    audit_issues = json.loads(result.stdout)
                    tools_results["pip_audit"] = {"status": "vulnerabilities_found", "vulnerabilities": audit_issues}
                except:
                    tools_results["pip_audit"] = {"status": "error", "output": result.stdout}
            
        except Exception as e:
            tools_results["pip_audit"] = {"status": "error", "error": str(e)}
        
        return tools_results

    async def _analyze_dependencies_with_ai(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies with AI"""
        system_prompt = """You are an expert dependency management and security analyst.
        
        Your role is to:
        1. Analyze project dependencies for security vulnerabilities
        2. Check for outdated packages and compatibility issues
        3. Identify potential conflicts and version mismatches
        4. Recommend updates and security patches
        5. Assess overall dependency health and maintenance
        
        Provide your analysis in JSON format:
        {
            "vulnerabilities": [
                {
                    "package": "package_name",
                    "version": "current_version",
                    "vulnerability": "CVE-XXXX-XXXX",
                    "severity": "critical|high|medium|low",
                    "description": "vulnerability description",
                    "fix_version": "fixed_version",
                    "recommendation": "how to fix"
                }
            ],
            "outdated_packages": [
                {
                    "package": "package_name",
                    "current_version": "1.0.0",
                    "latest_version": "2.0.0",
                    "update_type": "major|minor|patch",
                    "changelog": "what's new",
                    "breaking_changes": "any breaking changes",
                    "recommendation": "update recommendation"
                }
            ],
            "compatibility_issues": [
                {
                    "packages": ["pkg1", "pkg2"],
                    "issue": "version conflict description",
                    "severity": "critical|high|medium|low",
                    "solution": "how to resolve"
                }
            ],
            "recommendations": [
                "immediate actions to take"
            ],
            "dependency_health": {
                "overall_score": 0-100,
                "security_score": 0-100,
                "maintenance_score": 0-100,
                "compatibility_score": 0-100
            }
        }"""
        
        prompt = f"""Analyze the following project dependencies for security vulnerabilities, outdated packages, and compatibility issues:

REQUIREMENTS.TXT:
{json.dumps(dependencies['requirements_txt'], indent=2)}

PYPROJECT.TOML:
{json.dumps(dependencies['pyproject_toml'], indent=2)}

PIP FREEZE:
{json.dumps(dependencies['pip_freeze'][:20], indent=2)}  # First 20 packages

Please provide a comprehensive dependency analysis focusing on:
1. Security vulnerabilities and CVEs
2. Outdated packages and available updates
3. Version conflicts and compatibility issues
4. Maintenance and support status
5. Specific recommendations for improvements"""
        
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
                        "outdated_packages": [],
                        "compatibility_issues": [],
                        "recommendations": [],
                        "dependency_health": {"overall_score": 50}
                    }
        
        return {"error": "All AI providers failed"}

    async def run_dependency_audit(self) -> Dict[str, Any]:
        """Run comprehensive dependency audit"""
        print("📦 Enhanced Dependency Auditor Starting...")
        
        # Get dependencies
        print("Collecting project dependencies...")
        dependencies = self._get_dependencies()
        self.audit_results["dependencies"] = dependencies
        
        print(f"Found {len(dependencies['requirements_txt'])} requirements.txt dependencies")
        print(f"Found {len(dependencies['pyproject_toml'])} pyproject.toml dependencies")
        print(f"Found {len(dependencies['pip_freeze'])} installed packages")
        
        # Run dependency tools
        print("Running dependency analysis tools...")
        tools_results = self._run_dependency_tools()
        self.audit_results["tools_results"] = tools_results
        
        # Analyze with AI
        print("Analyzing dependencies with AI...")
        ai_analysis = await self._analyze_dependencies_with_ai(dependencies)
        self.audit_results["ai_analysis"] = ai_analysis
        
        # Extract vulnerabilities and issues
        if "vulnerabilities" in ai_analysis:
            self.audit_results["vulnerabilities"] = ai_analysis["vulnerabilities"]
        
        if "outdated_packages" in ai_analysis:
            self.audit_results["outdated_packages"] = ai_analysis["outdated_packages"]
        
        if "compatibility_issues" in ai_analysis:
            self.audit_results["compatibility_issues"] = ai_analysis["compatibility_issues"]
        
        if "recommendations" in ai_analysis:
            self.audit_results["recommendations"] = ai_analysis["recommendations"]
        
        # Calculate audit metrics
        critical_vulns = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "critical"])
        high_vulns = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "high"])
        outdated_count = len(self.audit_results["outdated_packages"])
        compatibility_issues = len(self.audit_results["compatibility_issues"])
        
        self.audit_results["audit_metrics"] = {
            "total_dependencies": len(dependencies["pip_freeze"]),
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "total_vulnerabilities": len(self.audit_results["vulnerabilities"]),
            "outdated_packages": outdated_count,
            "compatibility_issues": compatibility_issues,
            "dependency_health_score": ai_analysis.get("dependency_health", {}).get("overall_score", 0)
        }
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.audit_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("dependency_audit_results.json", "w") as f:
            json.dump(self.audit_results, f, indent=2)
        
        print(f"✅ Dependency Audit Complete!")
        print(f"   Total Dependencies: {self.audit_results['audit_metrics']['total_dependencies']}")
        print(f"   Critical Vulnerabilities: {critical_vulns}")
        print(f"   High Vulnerabilities: {high_vulns}")
        print(f"   Total Vulnerabilities: {len(self.audit_results['vulnerabilities'])}")
        print(f"   Outdated Packages: {outdated_count}")
        print(f"   Compatibility Issues: {compatibility_issues}")
        print(f"   Health Score: {self.audit_results['audit_metrics']['dependency_health_score']}/100")
        
        return self.audit_results


async def main():
    """Main function"""
    auditor = EnhancedDependencyAuditor()
    results = await auditor.run_dependency_audit()
    
    # Print summary
    print("\n" + "="*80)
    print("📦 ENHANCED DEPENDENCY AUDITOR - SUMMARY")
    print("="*80)
    print(f"Total Dependencies: {results['audit_metrics']['total_dependencies']}")
    print(f"Critical Vulnerabilities: {results['audit_metrics']['critical_vulnerabilities']}")
    print(f"High Vulnerabilities: {results['audit_metrics']['high_vulnerabilities']}")
    print(f"Total Vulnerabilities: {results['audit_metrics']['total_vulnerabilities']}")
    print(f"Outdated Packages: {results['audit_metrics']['outdated_packages']}")
    print(f"Compatibility Issues: {results['audit_metrics']['compatibility_issues']}")
    print(f"Health Score: {results['audit_metrics']['dependency_health_score']}/100")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())