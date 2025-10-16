#!/usr/bin/env python3
"""
Enhanced Conflict Resolution Specialist - Layer 2 Agent
Intelligent merge conflict resolution with AI-powered decision making
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


class EnhancedConflictResolver:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        self.issues_found = os.environ.get("ISSUES_FOUND", "0")
        self.critical_issues = os.environ.get("CRITICAL_ISSUES", "0")
        self.docker_status = os.environ.get("DOCKER_STATUS", "unknown")
        self.security_issues = os.environ.get("SECURITY_ISSUES", "0")
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Resolution results
        self.resolution_results = {
            "timestamp": datetime.now().isoformat(),
            "conflicts_detected": [],
            "resolution_plan": {},
            "intelligent_decisions": [],
            "merge_strategies": [],
            "risk_assessment": {},
            "recommended_actions": [],
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for conflict resolution"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "conflict_analysis"
            },
            {
                "name": "Claude",
                "key": os.environ.get("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-5-sonnet-20241022",
                "priority": 2,
                "specialization": "decision_making"
            },
            {
                "name": "GPT-4",
                "key": os.environ.get("GPT4_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "priority": 3,
                "specialization": "strategy_planning"
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
                max_tokens=4000,
                temperature=0.3
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

    def _detect_git_conflicts(self) -> List[Dict[str, Any]]:
        """Detect current git conflicts"""
        conflicts = []
        
        try:
            # Check for merge conflicts
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('UU') or line.startswith('AA') or line.startswith('DD'):
                        file_path = line[3:].strip()
                        conflicts.append({
                            "file": file_path,
                            "type": "merge_conflict",
                            "status": line[:2],
                            "severity": "high"
                        })
            
            # Check for rebase conflicts
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if "rebase in progress" in result.stdout.lower():
                conflicts.append({
                    "file": "rebase",
                    "type": "rebase_conflict",
                    "status": "in_progress",
                    "severity": "critical"
                })
            
            # Check for cherry-pick conflicts
            if "cherry-pick in progress" in result.stdout.lower():
                conflicts.append({
                    "file": "cherry-pick",
                    "type": "cherry_pick_conflict",
                    "status": "in_progress",
                    "severity": "high"
                })
        
        except Exception as e:
            print(f"Error detecting git conflicts: {e}")
        
        return conflicts

    def _analyze_project_context(self) -> Dict[str, Any]:
        """Analyze project context for conflict resolution"""
        context = {
            "project_type": "unknown",
            "main_language": "python",
            "has_docker": False,
            "has_tests": False,
            "has_ci_cd": False,
            "recent_commits": [],
            "active_branches": [],
            "dependencies": []
        }
        
        try:
            # Check for Python project
            if os.path.exists("/workspace/requirements.txt") or os.path.exists("/workspace/pyproject.toml"):
                context["project_type"] = "python"
                context["main_language"] = "python"
            
            # Check for Docker
            if os.path.exists("/workspace/Dockerfile") or os.path.exists("/workspace/docker-compose.yml"):
                context["has_docker"] = True
            
            # Check for tests
            if os.path.exists("/workspace/tests") or os.path.exists("/workspace/test_"):
                context["has_tests"] = True
            
            # Check for CI/CD
            if os.path.exists("/workspace/.github/workflows"):
                context["has_ci_cd"] = True
            
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                context["recent_commits"] = result.stdout.strip().split('\n')[:5]
            
            # Get active branches
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                cwd="/workspace"
            )
            
            if result.returncode == 0:
                branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
                context["active_branches"] = branches[:10]
        
        except Exception as e:
            print(f"Error analyzing project context: {e}")
        
        return context

    async def _generate_resolution_strategy(self, conflicts: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent resolution strategy"""
        system_prompt = """You are an expert Git conflict resolution specialist and software architect.
        
        Your role is to:
        1. Analyze merge conflicts and project context
        2. Generate intelligent resolution strategies
        3. Assess risks and recommend safe approaches
        4. Provide step-by-step resolution plans
        5. Consider project stability and team workflow
        
        Context provided:
        - Issues found: {issues_found}
        - Critical issues: {critical_issues}
        - Docker status: {docker_status}
        - Security issues: {security_issues}
        
        Provide your analysis in JSON format:
        {{
            "conflict_analysis": {{
                "total_conflicts": 0,
                "critical_conflicts": 0,
                "file_types_affected": [],
                "complexity_score": 0-100
            }},
            "resolution_strategy": {{
                "approach": "merge|rebase|cherry-pick|manual",
                "priority_order": ["file1", "file2"],
                "risk_level": "low|medium|high|critical",
                "estimated_time": "minutes|hours|days"
            }},
            "step_by_step_plan": [
                {{"step": 1, "action": "description", "command": "git command", "risk": "low|medium|high"}}
            ],
            "safety_measures": [
                "backup_branch", "test_validation", "rollback_plan"
            ],
            "recommended_actions": [
                "immediate actions to take"
            ],
            "risk_assessment": {{
                "data_loss_risk": "low|medium|high",
                "functionality_risk": "low|medium|high",
                "team_impact": "low|medium|high"
            }}
        }}"""
        
        prompt = f"""Analyze the following Git conflicts and project context to generate an intelligent resolution strategy:

CONFLICTS DETECTED:
{json.dumps(conflicts, indent=2)}

PROJECT CONTEXT:
{json.dumps(context, indent=2)}

CURRENT SITUATION:
- Issues found: {self.issues_found}
- Critical issues: {self.critical_issues}
- Docker status: {self.docker_status}
- Security issues: {self.security_issues}

Please provide a comprehensive conflict resolution strategy that considers:
1. Project stability and safety
2. Team workflow impact
3. Risk mitigation
4. Step-by-step execution plan
5. Rollback capabilities"""
        
        # Try each AI client
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    strategy = json.loads(result["content"])
                    strategy["provider"] = result["provider"]
                    strategy["response_time"] = result["response_time"]
                    return strategy
                except json.JSONDecodeError:
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_strategy": result["content"],
                        "conflict_analysis": {"total_conflicts": len(conflicts), "critical_conflicts": 0},
                        "resolution_strategy": {"approach": "manual", "risk_level": "medium"},
                        "step_by_step_plan": [],
                        "safety_measures": [],
                        "recommended_actions": [],
                        "risk_assessment": {"data_loss_risk": "medium", "functionality_risk": "medium"}
                    }
        
        return {"error": "All AI providers failed"}

    async def _generate_merge_strategies(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific merge strategies for each conflict"""
        strategies = []
        
        for conflict in conflicts:
            system_prompt = f"""You are a Git merge conflict resolution expert.
            
            Analyze the specific conflict in file: {conflict.get('file', 'unknown')}
            Conflict type: {conflict.get('type', 'unknown')}
            Status: {conflict.get('status', 'unknown')}
            
            Provide a specific resolution strategy for this conflict:
            {{
                "file": "{conflict.get('file', 'unknown')}",
                "strategy": "accept_incoming|accept_current|manual_merge|skip",
                "reasoning": "why this strategy",
                "commands": ["git commands to execute"],
                "validation": "how to verify the fix",
                "risk_level": "low|medium|high"
            }}"""
            
            prompt = f"""Provide a specific resolution strategy for this conflict:
            
            File: {conflict.get('file', 'unknown')}
            Type: {conflict.get('type', 'unknown')}
            Status: {conflict.get('status', 'unknown')}
            Severity: {conflict.get('severity', 'unknown')}
            
            Consider the project context and provide the safest resolution approach."""
            
            # Try each AI client
            for client_info in self.ai_clients:
                result = await self._analyze_with_ai(prompt, system_prompt, client_info)
                
                if result and result.get("success"):
                    try:
                        strategy = json.loads(result["content"])
                        strategy["provider"] = result["provider"]
                        strategies.append(strategy)
                        break
                    except json.JSONDecodeError:
                        strategies.append({
                            "file": conflict.get('file', 'unknown'),
                            "strategy": "manual_merge",
                            "reasoning": "AI analysis failed, manual review required",
                            "commands": ["git status", "git diff"],
                            "validation": "manual verification",
                            "risk_level": "high",
                            "provider": result["provider"]
                        })
                        break
        
        return strategies

    async def run_conflict_resolution(self) -> Dict[str, Any]:
        """Run comprehensive conflict resolution analysis"""
        print("🧠 Enhanced Conflict Resolution Specialist Starting...")
        print(f"Context: {self.issues_found} issues, {self.critical_issues} critical, Docker: {self.docker_status}")
        
        # Detect conflicts
        print("Detecting Git conflicts...")
        conflicts = self._detect_git_conflicts()
        self.resolution_results["conflicts_detected"] = conflicts
        
        if not conflicts:
            print("✅ No active conflicts detected")
            self.resolution_results["resolution_plan"] = {
                "status": "no_conflicts",
                "message": "No active Git conflicts detected"
            }
            return self.resolution_results
        
        print(f"Found {len(conflicts)} conflicts")
        
        # Analyze project context
        print("Analyzing project context...")
        context = self._analyze_project_context()
        
        # Generate resolution strategy
        print("Generating resolution strategy...")
        strategy = await self._generate_resolution_strategy(conflicts, context)
        self.resolution_results["resolution_plan"] = strategy
        
        # Generate merge strategies
        print("Generating merge strategies...")
        merge_strategies = await self._generate_merge_strategies(conflicts)
        self.resolution_results["merge_strategies"] = merge_strategies
        
        # Extract intelligent decisions
        if "step_by_step_plan" in strategy:
            self.resolution_results["intelligent_decisions"] = strategy["step_by_step_plan"]
        
        if "recommended_actions" in strategy:
            self.resolution_results["recommended_actions"] = strategy["recommended_actions"]
        
        if "risk_assessment" in strategy:
            self.resolution_results["risk_assessment"] = strategy["risk_assessment"]
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.resolution_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("conflict_resolution_results.json", "w") as f:
            json.dump(self.resolution_results, f, indent=2)
        
        print(f"✅ Conflict Resolution Analysis Complete!")
        print(f"   Conflicts Detected: {len(conflicts)}")
        print(f"   Resolution Strategy: {strategy.get('resolution_strategy', {}).get('approach', 'unknown')}")
        print(f"   Risk Level: {strategy.get('resolution_strategy', {}).get('risk_level', 'unknown')}")
        print(f"   Merge Strategies: {len(merge_strategies)}")
        
        return self.resolution_results


async def main():
    """Main function"""
    resolver = EnhancedConflictResolver()
    results = await resolver.run_conflict_resolution()
    
    # Print summary
    print("\n" + "="*80)
    print("🧠 ENHANCED CONFLICT RESOLUTION SPECIALIST - SUMMARY")
    print("="*80)
    print(f"Conflicts Detected: {len(results['conflicts_detected'])}")
    print(f"Resolution Strategy: {results['resolution_plan'].get('resolution_strategy', {}).get('approach', 'unknown')}")
    print(f"Risk Level: {results['resolution_plan'].get('resolution_strategy', {}).get('risk_level', 'unknown')}")
    print(f"Merge Strategies: {len(results['merge_strategies'])}")
    print(f"Intelligent Decisions: {len(results['intelligent_decisions'])}")
    print(f"Recommended Actions: {len(results['recommended_actions'])}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())