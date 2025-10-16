#!/usr/bin/env python3
"""
Enhanced Docker Health Monitor - Layer 1 Agent
Advanced Docker container and infrastructure analysis
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


class EnhancedDockerMonitor:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Monitor results
        self.monitor_results = {
            "timestamp": datetime.now().isoformat(),
            "docker_status": "unknown",
            "container_health": {},
            "image_analysis": {},
            "infrastructure_issues": [],
            "fix_recommendations": [],
            "performance_metrics": {},
            "security_issues": [],
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for Docker analysis"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "docker_analysis"
            },
            {
                "name": "Claude",
                "key": os.environ.get("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-5-sonnet-20241022",
                "priority": 2,
                "specialization": "infrastructure_analysis"
            },
            {
                "name": "GPT-4",
                "key": os.environ.get("GPT4_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "priority": 3,
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

    def _check_docker_installation(self) -> Dict[str, Any]:
        """Check if Docker is installed and accessible"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "installed": True,
                    "version": result.stdout.strip(),
                    "status": "available"
                }
            else:
                return {
                    "installed": False,
                    "error": result.stderr.strip(),
                    "status": "error"
                }
        except subprocess.TimeoutExpired:
            return {
                "installed": False,
                "error": "Docker command timed out",
                "status": "timeout"
            }
        except FileNotFoundError:
            return {
                "installed": False,
                "error": "Docker not found in PATH",
                "status": "not_found"
            }
        except Exception as e:
            return {
                "installed": False,
                "error": str(e),
                "status": "error"
            }

    def _analyze_dockerfile(self) -> Dict[str, Any]:
        """Analyze Dockerfile for issues"""
        dockerfile_paths = [
            "/workspace/Dockerfile",
            "/workspace/docker/Dockerfile",
            "/workspace/Dockerfile.offline"
        ]
        
        analysis = {
            "dockerfiles_found": [],
            "issues": [],
            "recommendations": [],
            "security_concerns": [],
            "optimization_suggestions": []
        }
        
        for dockerfile_path in dockerfile_paths:
            if os.path.exists(dockerfile_path):
                try:
                    with open(dockerfile_path, 'r') as f:
                        content = f.read()
                    
                    analysis["dockerfiles_found"].append(dockerfile_path)
                    
                    # Basic analysis
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        line = line.strip()
                        
                        # Check for common issues
                        if line.startswith('FROM') and 'latest' in line:
                            analysis["issues"].append({
                                "type": "version_pinning",
                                "line": i,
                                "description": "Using 'latest' tag instead of specific version",
                                "severity": "medium",
                                "file": dockerfile_path
                            })
                        
                        if line.startswith('RUN') and 'apt-get update' in line and 'apt-get clean' not in content:
                            analysis["issues"].append({
                                "type": "cleanup",
                                "line": i,
                                "description": "Missing apt-get clean to reduce image size",
                                "severity": "low",
                                "file": dockerfile_path
                            })
                        
                        if line.startswith('USER') and 'root' in line:
                            analysis["security_concerns"].append({
                                "type": "root_user",
                                "line": i,
                                "description": "Running as root user",
                                "severity": "high",
                                "file": dockerfile_path
                            })
                        
                        if line.startswith('COPY') and 'requirements.txt' in line:
                            analysis["optimization_suggestions"].append({
                                "type": "layer_optimization",
                                "line": i,
                                "description": "Good practice: copying requirements.txt before source code",
                                "severity": "info",
                                "file": dockerfile_path
                            })
                
                except Exception as e:
                    analysis["issues"].append({
                        "type": "file_error",
                        "description": f"Error reading {dockerfile_path}: {e}",
                        "severity": "high",
                        "file": dockerfile_path
                    })
        
        return analysis

    def _analyze_docker_compose(self) -> Dict[str, Any]:
        """Analyze docker-compose files"""
        compose_files = [
            "/workspace/docker-compose.yml",
            "/workspace/docker-compose.dev.yml",
            "/workspace/docker-compose.test.yml",
            "/workspace/docker-compose-offline.yml"
        ]
        
        analysis = {
            "compose_files_found": [],
            "services": [],
            "issues": [],
            "recommendations": [],
            "networking_issues": [],
            "volume_issues": []
        }
        
        for compose_file in compose_files:
            if os.path.exists(compose_file):
                try:
                    with open(compose_file, 'r') as f:
                        content = f.read()
                    
                    analysis["compose_files_found"].append(compose_file)
                    
                    # Basic YAML analysis (simplified)
                    if 'version:' in content:
                        analysis["recommendations"].append({
                            "type": "version_specification",
                            "description": "Docker Compose version specified",
                            "severity": "info",
                            "file": compose_file
                        })
                    
                    if 'networks:' in content:
                        analysis["recommendations"].append({
                            "type": "networking",
                            "description": "Custom networks defined",
                            "severity": "info",
                            "file": compose_file
                        })
                    
                    if 'volumes:' in content:
                        analysis["recommendations"].append({
                            "type": "volumes",
                            "description": "Volume mounts defined",
                            "severity": "info",
                            "file": compose_file
                        })
                
                except Exception as e:
                    analysis["issues"].append({
                        "type": "file_error",
                        "description": f"Error reading {compose_file}: {e}",
                        "severity": "high",
                        "file": compose_file
                    })
        
        return analysis

    async def _analyze_with_ai_insights(self, dockerfile_content: str, compose_content: str) -> Dict[str, Any]:
        """Get AI insights on Docker configuration"""
        system_prompt = """You are an expert Docker and containerization specialist. 
        
        Your role is to:
        1. Analyze Docker configurations for best practices
        2. Identify security vulnerabilities and performance issues
        3. Suggest optimizations for image size and build time
        4. Recommend improvements for production readiness
        5. Check for compliance with container security standards
        
        Provide your analysis in JSON format with:
        {
            "security_issues": [{"type": "issue_type", "severity": "level", "description": "details", "fix": "suggestion"}],
            "performance_issues": [{"type": "issue_type", "severity": "level", "description": "details", "fix": "suggestion"}],
            "best_practices": [{"practice": "description", "status": "implemented|missing", "priority": "high|medium|low"}],
            "optimization_suggestions": [{"area": "area_name", "suggestion": "details", "impact": "high|medium|low"}],
            "overall_score": 85,
            "critical_issues": 2,
            "recommendations": ["list of top recommendations"]
        }"""
        
        prompt = f"""Analyze the following Docker configuration for issues and improvements:

Dockerfile:
```dockerfile
{dockerfile_content}
```

Docker Compose:
```yaml
{compose_content}
```

Please provide a comprehensive analysis focusing on security, performance, and best practices."""
        
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
                        "security_issues": [],
                        "performance_issues": [],
                        "best_practices": [],
                        "optimization_suggestions": [],
                        "overall_score": 0,
                        "critical_issues": 0,
                        "recommendations": []
                    }
        
        return {"error": "All AI providers failed"}

    async def run_monitoring(self) -> Dict[str, Any]:
        """Run comprehensive Docker monitoring"""
        print("🐳 Enhanced Docker Health Monitor Starting...")
        
        # Check Docker installation
        print("Checking Docker installation...")
        docker_status = self._check_docker_installation()
        self.monitor_results["docker_status"] = docker_status["status"]
        
        if not docker_status["installed"]:
            print(f"❌ Docker not available: {docker_status['error']}")
            self.monitor_results["infrastructure_issues"].append({
                "type": "docker_not_available",
                "severity": "critical",
                "description": docker_status["error"],
                "fix": "Install Docker or ensure it's accessible"
            })
            return self.monitor_results
        
        print(f"✅ Docker available: {docker_status['version']}")
        
        # Analyze Dockerfile
        print("Analyzing Dockerfile...")
        dockerfile_analysis = self._analyze_dockerfile()
        self.monitor_results["image_analysis"]["dockerfile"] = dockerfile_analysis
        
        # Analyze docker-compose files
        print("Analyzing Docker Compose files...")
        compose_analysis = self._analyze_docker_compose()
        self.monitor_results["image_analysis"]["compose"] = compose_analysis
        
        # Get AI insights
        print("Getting AI insights...")
        dockerfile_content = ""
        compose_content = ""
        
        if dockerfile_analysis["dockerfiles_found"]:
            try:
                with open(dockerfile_analysis["dockerfiles_found"][0], 'r') as f:
                    dockerfile_content = f.read()
            except:
                pass
        
        if compose_analysis["compose_files_found"]:
            try:
                with open(compose_analysis["compose_files_found"][0], 'r') as f:
                    compose_content = f.read()
            except:
                pass
        
        if dockerfile_content or compose_content:
            ai_insights = await self._analyze_with_ai_insights(dockerfile_content, compose_content)
            self.monitor_results["ai_insights"] = ai_insights
            
            # Extract issues and recommendations
            if "security_issues" in ai_insights:
                self.monitor_results["security_issues"].extend(ai_insights["security_issues"])
            
            if "recommendations" in ai_insights:
                self.monitor_results["fix_recommendations"].extend(ai_insights["recommendations"])
        
        # Collect all issues
        all_issues = []
        all_issues.extend(dockerfile_analysis["issues"])
        all_issues.extend(compose_analysis["issues"])
        all_issues.extend(self.monitor_results["infrastructure_issues"])
        all_issues.extend(self.monitor_results["security_issues"])
        
        self.monitor_results["infrastructure_issues"] = all_issues
        
        # Calculate performance metrics
        self.monitor_results["performance_metrics"] = {
            "dockerfiles_analyzed": len(dockerfile_analysis["dockerfiles_found"]),
            "compose_files_analyzed": len(compose_analysis["compose_files_found"]),
            "total_issues": len(all_issues),
            "critical_issues": len([i for i in all_issues if i.get("severity") == "critical"]),
            "high_priority_issues": len([i for i in all_issues if i.get("severity") == "high"]),
            "security_issues": len(self.monitor_results["security_issues"]),
            "recommendations": len(self.monitor_results["fix_recommendations"])
        }
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.monitor_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Determine overall status
        if docker_status["status"] != "available":
            self.monitor_results["docker_status"] = "unhealthy"
        elif len([i for i in all_issues if i.get("severity") == "critical"]) > 0:
            self.monitor_results["docker_status"] = "critical_issues"
        elif len([i for i in all_issues if i.get("severity") == "high"]) > 0:
            self.monitor_results["docker_status"] = "issues_found"
        else:
            self.monitor_results["docker_status"] = "healthy"
        
        # Save results
        with open("docker_monitor_results.json", "w") as f:
            json.dump(self.monitor_results, f, indent=2)
        
        print(f"✅ Docker Monitoring Complete!")
        print(f"   Status: {self.monitor_results['docker_status']}")
        print(f"   Total Issues: {self.monitor_results['performance_metrics']['total_issues']}")
        print(f"   Critical Issues: {self.monitor_results['performance_metrics']['critical_issues']}")
        print(f"   Security Issues: {self.monitor_results['performance_metrics']['security_issues']}")
        print(f"   Recommendations: {self.monitor_results['performance_metrics']['recommendations']}")
        
        return self.monitor_results


async def main():
    """Main function"""
    monitor = EnhancedDockerMonitor()
    results = await monitor.run_monitoring()
    
    # Print summary
    print("\n" + "="*80)
    print("🐳 ENHANCED DOCKER HEALTH MONITOR - SUMMARY")
    print("="*80)
    print(f"Docker Status: {results['docker_status']}")
    print(f"Files Analyzed: {results['performance_metrics']['dockerfiles_analyzed']} Dockerfiles, {results['performance_metrics']['compose_files_analyzed']} Compose files")
    print(f"Total Issues: {results['performance_metrics']['total_issues']}")
    print(f"Critical Issues: {results['performance_metrics']['critical_issues']}")
    print(f"Security Issues: {results['performance_metrics']['security_issues']}")
    print(f"Recommendations: {results['performance_metrics']['recommendations']}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())