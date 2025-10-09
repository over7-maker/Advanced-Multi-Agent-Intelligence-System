#!/usr/bin/env python3
"""
Enhanced Code Quality Inspector - Layer 1 Agent
Advanced code analysis with automated fix suggestions
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


class EnhancedCodeQualityInspector:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        self.focus_area = os.environ.get("FOCUS_AREA", "comprehensive")
        self.urgency_level = os.environ.get("URGENCY_LEVEL", "normal")
        
        # Initialize AI clients with enhanced fallback
        self.ai_clients = self._initialize_ai_clients()
        
        # Analysis results
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "focus_area": self.focus_area,
            "urgency_level": self.urgency_level,
            "issues_found": [],
            "critical_issues": [],
            "recommendations": [],
            "fix_suggestions": [],
            "quality_metrics": {},
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients with enhanced configuration"""
        clients = []
        
        # Priority order with enhanced configuration
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "code_analysis"
            },
            {
                "name": "Claude",
                "key": os.environ.get("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-5-sonnet-20241022",
                "priority": 2,
                "specialization": "code_review"
            },
            {
                "name": "GPT-4",
                "key": os.environ.get("GPT4_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "priority": 3,
                "specialization": "architecture_analysis"
            },
            {
                "name": "GLM",
                "key": os.environ.get("GLM_API_KEY"),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": "glm-4-flash",
                "priority": 4,
                "specialization": "performance_analysis"
            },
            {
                "name": "Grok",
                "key": os.environ.get("GROK_API_KEY"),
                "base_url": "https://api.openrouter.ai/v1",
                "model": "x-ai/grok-beta",
                "priority": 5,
                "specialization": "security_analysis"
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
        """Analyze code with specific AI client"""
        start_time = time.time()
        
        try:
            response = client_info["client"].chat.completions.create(
                model=client_info["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            response_time = time.time() - start_time
            
            # Update performance metrics
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

    async def _get_code_files(self) -> List[str]:
        """Get list of code files to analyze"""
        try:
            # Get all Python files
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
            
            # Limit to most important files for analysis
            priority_files = []
            for file in files:
                if any(important in file for important in [
                    'main.py', 'app.py', 'src/', 'core/', 'api/', 'models/',
                    'services/', 'utils/', 'handlers/', 'workflows/'
                ]):
                    priority_files.append(file)
            
            return priority_files[:20]  # Limit to 20 most important files
            
        except Exception as e:
            print(f"Error getting code files: {e}")
            return []

    async def _analyze_code_quality(self, file_path: str) -> Dict[str, Any]:
        """Analyze code quality for a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file {file_path}: {e}"}
        
        system_prompt = f"""You are an expert code quality inspector specializing in {self.focus_area} analysis. 
        
        Your role is to:
        1. Identify code quality issues, bugs, and potential problems
        2. Suggest specific improvements and fixes
        3. Assess code maintainability, readability, and performance
        4. Check for security vulnerabilities and best practices
        5. Provide actionable recommendations with code examples
        
        Focus on: {self.focus_area}
        Urgency Level: {self.urgency_level}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "issues": [
                {{
                    "type": "bug|performance|security|maintainability|style",
                    "severity": "critical|high|medium|low",
                    "line": 123,
                    "description": "Detailed description",
                    "suggestion": "Specific fix suggestion",
                    "code_example": "Fixed code example"
                }}
            ],
            "overall_quality_score": 85,
            "recommendations": ["List of general recommendations"],
            "fix_suggestions": ["List of specific fixes"]
        }}"""
        
        prompt = f"""Analyze the following Python code for quality issues, bugs, and improvements:

File: {file_path}

```python
{content}
```

Please provide a comprehensive analysis focusing on {self.focus_area} with urgency level {self.urgency_level}."""
        
        # Try each AI client until one succeeds
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    # Parse JSON response
                    analysis = json.loads(result["content"])
                    analysis["provider"] = result["provider"]
                    analysis["response_time"] = result["response_time"]
                    return analysis
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_analysis": result["content"],
                        "issues": [],
                        "overall_quality_score": 0,
                        "recommendations": [],
                        "fix_suggestions": []
                    }
            else:
                print(f"Analysis failed with {client_info['name']}: {result.get('error', 'Unknown error') if result else 'No result'}")
        
        return {"error": "All AI providers failed"}

    async def _run_static_analysis_tools(self) -> Dict[str, Any]:
        """Run static analysis tools"""
        tools_results = {}
        
        try:
            # Run flake8 for style issues
            result = subprocess.run(
                ["python", "-m", "flake8", "--format=json", "."],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                tools_results["flake8"] = {"status": "clean", "issues": []}
            else:
                try:
                    flake8_issues = json.loads(result.stdout)
                    tools_results["flake8"] = {"status": "issues_found", "issues": flake8_issues}
                except:
                    tools_results["flake8"] = {"status": "error", "output": result.stdout}
            
        except Exception as e:
            tools_results["flake8"] = {"status": "error", "error": str(e)}
        
        try:
            # Run bandit for security issues
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
        
        return tools_results

    async def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive code quality analysis"""
        print("🔍 Enhanced Code Quality Inspector Starting...")
        print(f"Focus Area: {self.focus_area}")
        print(f"Urgency Level: {self.urgency_level}")
        print(f"AI Clients Available: {len(self.ai_clients)}")
        
        # Get code files to analyze
        code_files = await self._get_code_files()
        print(f"Analyzing {len(code_files)} code files...")
        
        # Run static analysis tools
        print("Running static analysis tools...")
        tools_results = await self._run_static_analysis_tools()
        self.analysis_results["static_analysis"] = tools_results
        
        # Analyze each file
        file_analyses = []
        for file_path in code_files:
            print(f"Analyzing {file_path}...")
            analysis = await self._analyze_code_quality(file_path)
            analysis["file_path"] = file_path
            file_analyses.append(analysis)
            
            # Collect issues and recommendations
            if "issues" in analysis:
                for issue in analysis["issues"]:
                    issue["file_path"] = file_path
                    self.analysis_results["issues_found"].append(issue)
                    
                    if issue.get("severity") in ["critical", "high"]:
                        self.analysis_results["critical_issues"].append(issue)
            
            if "recommendations" in analysis:
                self.analysis_results["recommendations"].extend(analysis["recommendations"])
            
            if "fix_suggestions" in analysis:
                self.analysis_results["fix_suggestions"].extend(analysis["fix_suggestions"])
        
        self.analysis_results["file_analyses"] = file_analyses
        
        # Calculate quality metrics
        total_issues = len(self.analysis_results["issues_found"])
        critical_issues = len(self.analysis_results["critical_issues"])
        
        self.analysis_results["quality_metrics"] = {
            "total_files_analyzed": len(code_files),
            "total_issues_found": total_issues,
            "critical_issues": critical_issues,
            "high_priority_issues": len([i for i in self.analysis_results["issues_found"] if i.get("severity") == "high"]),
            "medium_priority_issues": len([i for i in self.analysis_results["issues_found"] if i.get("severity") == "medium"]),
            "low_priority_issues": len([i for i in self.analysis_results["issues_found"] if i.get("severity") == "low"]),
            "recommendations_count": len(self.analysis_results["recommendations"]),
            "fix_suggestions_count": len(self.analysis_results["fix_suggestions"])
        }
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.analysis_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("layer1_analysis_results.json", "w") as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"✅ Analysis Complete!")
        print(f"   Total Issues Found: {total_issues}")
        print(f"   Critical Issues: {critical_issues}")
        print(f"   Files Analyzed: {len(code_files)}")
        print(f"   Recommendations: {len(self.analysis_results['recommendations'])}")
        print(f"   Fix Suggestions: {len(self.analysis_results['fix_suggestions'])}")
        
        return self.analysis_results


async def main():
    """Main function"""
    inspector = EnhancedCodeQualityInspector()
    results = await inspector.run_analysis()
    
    # Print summary
    print("\n" + "="*80)
    print("🔍 ENHANCED CODE QUALITY INSPECTOR - SUMMARY")
    print("="*80)
    print(f"Focus Area: {results['focus_area']}")
    print(f"Urgency Level: {results['urgency_level']}")
    print(f"Files Analyzed: {results['quality_metrics']['total_files_analyzed']}")
    print(f"Total Issues: {results['quality_metrics']['total_issues_found']}")
    print(f"Critical Issues: {results['quality_metrics']['critical_issues']}")
    print(f"Recommendations: {results['quality_metrics']['recommendations_count']}")
    print(f"Fix Suggestions: {results['quality_metrics']['fix_suggestions_count']}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())