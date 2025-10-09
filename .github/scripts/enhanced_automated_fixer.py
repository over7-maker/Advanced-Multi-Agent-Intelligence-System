#!/usr/bin/env python3
"""
Enhanced Automated Fixer - Layer 3 Agent
Intelligent automated fixing with multi-layer validation
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


class EnhancedAutomatedFixer:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        self.resolution_plan = os.environ.get("RESOLUTION_PLAN", "comprehensive")
        self.fix_recommendations = os.environ.get("FIX_RECOMMENDATIONS", "advanced")
        self.priority_actions = os.environ.get("PRIORITY_ACTIONS", "optimized")
        self.auto_apply = os.environ.get("AUTO_APPLY", "true").lower() == "true"
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Fix results
        self.fix_results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": [],
            "fixes_attempted": [],
            "fixes_failed": [],
            "validation_results": {},
            "rollback_plan": [],
            "performance_metrics": {},
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for automated fixing"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "code_fixing"
            },
            {
                "name": "Claude",
                "key": os.environ.get("CLAUDE_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "model": "claude-3-5-sonnet-20241022",
                "priority": 2,
                "specialization": "validation"
            },
            {
                "name": "GPT-4",
                "key": os.environ.get("GPT4_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o",
                "priority": 3,
                "specialization": "architecture_fixes"
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

    def _load_analysis_results(self) -> Dict[str, Any]:
        """Load analysis results from Layer 1"""
        results = {
            "issues": [],
            "critical_issues": [],
            "recommendations": [],
            "fix_suggestions": []
        }
        
        try:
            if os.path.exists("layer1_analysis_results.json"):
                with open("layer1_analysis_results.json", "r") as f:
                    data = json.load(f)
                    results["issues"] = data.get("issues_found", [])
                    results["critical_issues"] = data.get("critical_issues", [])
                    results["recommendations"] = data.get("recommendations", [])
                    results["fix_suggestions"] = data.get("fix_suggestions", [])
        except Exception as e:
            print(f"Error loading analysis results: {e}")
        
        return results

    def _load_conflict_results(self) -> Dict[str, Any]:
        """Load conflict resolution results from Layer 2"""
        results = {
            "conflicts": [],
            "resolution_plan": {},
            "merge_strategies": []
        }
        
        try:
            if os.path.exists("conflict_resolution_results.json"):
                with open("conflict_resolution_results.json", "r") as f:
                    data = json.load(f)
                    results["conflicts"] = data.get("conflicts_detected", [])
                    results["resolution_plan"] = data.get("resolution_plan", {})
                    results["merge_strategies"] = data.get("merge_strategies", [])
        except Exception as e:
            print(f"Error loading conflict results: {e}")
        
        return results

    async def _generate_fix_plan(self, analysis_results: Dict[str, Any], conflict_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive fix plan"""
        system_prompt = """You are an expert automated code fixer and system repair specialist.
        
        Your role is to:
        1. Analyze issues and generate safe, automated fixes
        2. Prioritize fixes based on severity and impact
        3. Create step-by-step fix execution plans
        4. Ensure fixes don't break existing functionality
        5. Provide rollback plans for each fix
        
        Context:
        - Resolution Plan: {resolution_plan}
        - Fix Recommendations: {fix_recommendations}
        - Priority Actions: {priority_actions}
        - Auto Apply: {auto_apply}
        
        Provide your fix plan in JSON format:
        {{
            "fix_priorities": [
                {{"priority": 1, "type": "critical|high|medium|low", "description": "fix description", "files": ["file1", "file2"]}}
            ],
            "automated_fixes": [
                {{"id": "fix_1", "type": "code_fix|config_fix|dependency_fix", "description": "what it fixes", "commands": ["command1", "command2"], "validation": "how to verify", "rollback": "how to undo"}}
            ],
            "manual_fixes": [
                {{"id": "manual_1", "description": "requires manual intervention", "reason": "why manual", "steps": ["step1", "step2"]}}
            ],
            "validation_plan": [
                {{"step": "test_execution", "command": "pytest", "expected": "all tests pass"}}
            ],
            "rollback_plan": [
                {{"fix_id": "fix_1", "rollback_command": "git checkout HEAD~1 file1", "description": "how to rollback"}}
            ],
            "risk_assessment": {{
                "overall_risk": "low|medium|high",
                "data_loss_risk": "low|medium|high",
                "functionality_risk": "low|medium|high"
            }}
        }}"""
        
        prompt = f"""Generate a comprehensive automated fix plan based on the following analysis:

ANALYSIS RESULTS:
{json.dumps(analysis_results, indent=2)}

CONFLICT RESULTS:
{json.dumps(conflict_results, indent=2)}

CONTEXT:
- Resolution Plan: {self.resolution_plan}
- Fix Recommendations: {self.fix_recommendations}
- Priority Actions: {self.priority_actions}
- Auto Apply: {self.auto_apply}

Please generate a safe, automated fix plan that:
1. Prioritizes critical issues first
2. Provides automated fixes where possible
3. Identifies manual fixes that require human intervention
4. Includes comprehensive validation
5. Provides rollback capabilities for each fix"""
        
        # Try each AI client
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    plan = json.loads(result["content"])
                    plan["provider"] = result["provider"]
                    plan["response_time"] = result["response_time"]
                    return plan
                except json.JSONDecodeError:
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_plan": result["content"],
                        "fix_priorities": [],
                        "automated_fixes": [],
                        "manual_fixes": [],
                        "validation_plan": [],
                        "rollback_plan": [],
                        "risk_assessment": {"overall_risk": "medium"}
                    }
        
        return {"error": "All AI providers failed"}

    async def _execute_automated_fix(self, fix: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single automated fix"""
        fix_result = {
            "id": fix.get("id", "unknown"),
            "type": fix.get("type", "unknown"),
            "description": fix.get("description", ""),
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "commands_executed": [],
            "output": "",
            "error": None,
            "validation_passed": False
        }
        
        try:
            print(f"🔧 Executing fix: {fix['description']}")
            
            # Execute each command
            for command in fix.get("commands", []):
                print(f"   Running: {command}")
                
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    cwd="/workspace",
                    timeout=300  # 5 minute timeout
                )
                
                fix_result["commands_executed"].append({
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
                if result.returncode != 0:
                    fix_result["error"] = f"Command failed: {result.stderr}"
                    fix_result["status"] = "failed"
                    break
            
            if fix_result["status"] != "failed":
                # Run validation if provided
                validation_command = fix.get("validation")
                if validation_command:
                    print(f"   Validating: {validation_command}")
                    
                    val_result = subprocess.run(
                        validation_command.split(),
                        capture_output=True,
                        text=True,
                        cwd="/workspace",
                        timeout=60
                    )
                    
                    fix_result["validation_passed"] = val_result.returncode == 0
                    fix_result["validation_output"] = val_result.stdout
                    
                    if not fix_result["validation_passed"]:
                        fix_result["error"] = f"Validation failed: {val_result.stderr}"
                        fix_result["status"] = "validation_failed"
                    else:
                        fix_result["status"] = "success"
                else:
                    fix_result["status"] = "success"
                    fix_result["validation_passed"] = True
            
            fix_result["end_time"] = datetime.now().isoformat()
            
        except subprocess.TimeoutExpired:
            fix_result["error"] = "Fix execution timed out"
            fix_result["status"] = "timeout"
        except Exception as e:
            fix_result["error"] = str(e)
            fix_result["status"] = "error"
        
        return fix_result

    async def _validate_fixes(self, validation_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive validation of all fixes"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "overall_status": "pending",
            "passed_tests": 0,
            "failed_tests": 0,
            "warnings": []
        }
        
        for test in validation_plan:
            test_result = {
                "step": test.get("step", "unknown"),
                "command": test.get("command", ""),
                "expected": test.get("expected", ""),
                "status": "pending",
                "output": "",
                "error": None
            }
            
            try:
                print(f"🧪 Running validation: {test['step']}")
                
                result = subprocess.run(
                    test["command"].split(),
                    capture_output=True,
                    text=True,
                    cwd="/workspace",
                    timeout=120
                )
                
                test_result["output"] = result.stdout
                test_result["error"] = result.stderr
                test_result["return_code"] = result.returncode
                
                if result.returncode == 0:
                    test_result["status"] = "passed"
                    validation_results["passed_tests"] += 1
                else:
                    test_result["status"] = "failed"
                    validation_results["failed_tests"] += 1
                
                validation_results["tests_run"].append(test_result)
                
            except subprocess.TimeoutExpired:
                test_result["status"] = "timeout"
                test_result["error"] = "Validation timed out"
                validation_results["failed_tests"] += 1
                validation_results["tests_run"].append(test_result)
            except Exception as e:
                test_result["status"] = "error"
                test_result["error"] = str(e)
                validation_results["failed_tests"] += 1
                validation_results["tests_run"].append(test_result)
        
        # Determine overall status
        if validation_results["failed_tests"] == 0:
            validation_results["overall_status"] = "passed"
        elif validation_results["passed_tests"] > 0:
            validation_results["overall_status"] = "partial"
        else:
            validation_results["overall_status"] = "failed"
        
        return validation_results

    async def run_automated_fixing(self) -> Dict[str, Any]:
        """Run comprehensive automated fixing"""
        print("🔧 Enhanced Automated Fixer Starting...")
        print(f"Auto Apply: {self.auto_apply}")
        print(f"Resolution Plan: {self.resolution_plan}")
        
        # Load analysis results
        print("Loading analysis results...")
        analysis_results = self._load_analysis_results()
        conflict_results = self._load_conflict_results()
        
        print(f"Loaded {len(analysis_results['issues'])} issues, {len(analysis_results['critical_issues'])} critical")
        print(f"Loaded {len(conflict_results['conflicts'])} conflicts")
        
        # Generate fix plan
        print("Generating fix plan...")
        fix_plan = await self._generate_fix_plan(analysis_results, conflict_results)
        self.fix_results["fix_plan"] = fix_plan
        
        if not self.auto_apply:
            print("⚠️  Auto-apply disabled, generating plan only")
            self.fix_results["status"] = "plan_generated"
            return self.fix_results
        
        # Execute automated fixes
        print("Executing automated fixes...")
        automated_fixes = fix_plan.get("automated_fixes", [])
        
        for fix in automated_fixes:
            fix_result = await self._execute_automated_fix(fix)
            self.fix_results["fixes_attempted"].append(fix_result)
            
            if fix_result["status"] == "success":
                self.fix_results["fixes_applied"].append(fix_result)
                print(f"✅ Fix applied: {fix_result['description']}")
            else:
                self.fix_results["fixes_failed"].append(fix_result)
                print(f"❌ Fix failed: {fix_result['description']} - {fix_result.get('error', 'Unknown error')}")
        
        # Run validation
        print("Running validation...")
        validation_plan = fix_plan.get("validation_plan", [])
        if validation_plan:
            validation_results = await self._validate_fixes(validation_plan)
            self.fix_results["validation_results"] = validation_results
        
        # Create rollback plan
        self.fix_results["rollback_plan"] = fix_plan.get("rollback_plan", [])
        
        # Calculate performance metrics
        self.fix_results["performance_metrics"] = {
            "fixes_attempted": len(self.fix_results["fixes_attempted"]),
            "fixes_applied": len(self.fix_results["fixes_applied"]),
            "fixes_failed": len(self.fix_results["fixes_failed"]),
            "success_rate": len(self.fix_results["fixes_applied"]) / len(self.fix_results["fixes_attempted"]) * 100 if self.fix_results["fixes_attempted"] else 0,
            "validation_status": self.fix_results["validation_results"].get("overall_status", "unknown"),
            "validation_passed": self.fix_results["validation_results"].get("passed_tests", 0),
            "validation_failed": self.fix_results["validation_results"].get("failed_tests", 0)
        }
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.fix_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("automated_fix_results.json", "w") as f:
            json.dump(self.fix_results, f, indent=2)
        
        print(f"✅ Automated Fixing Complete!")
        print(f"   Fixes Attempted: {self.fix_results['performance_metrics']['fixes_attempted']}")
        print(f"   Fixes Applied: {self.fix_results['performance_metrics']['fixes_applied']}")
        print(f"   Fixes Failed: {self.fix_results['performance_metrics']['fixes_failed']}")
        print(f"   Success Rate: {self.fix_results['performance_metrics']['success_rate']:.1f}%")
        print(f"   Validation Status: {self.fix_results['performance_metrics']['validation_status']}")
        
        return self.fix_results


async def main():
    """Main function"""
    fixer = EnhancedAutomatedFixer()
    results = await fixer.run_automated_fixing()
    
    # Print summary
    print("\n" + "="*80)
    print("🔧 ENHANCED AUTOMATED FIXER - SUMMARY")
    print("="*80)
    print(f"Fixes Attempted: {results['performance_metrics']['fixes_attempted']}")
    print(f"Fixes Applied: {results['performance_metrics']['fixes_applied']}")
    print(f"Fixes Failed: {results['performance_metrics']['fixes_failed']}")
    print(f"Success Rate: {results['performance_metrics']['success_rate']:.1f}%")
    print(f"Validation Status: {results['performance_metrics']['validation_status']}")
    print(f"Validation Passed: {results['performance_metrics']['validation_passed']}")
    print(f"Validation Failed: {results['performance_metrics']['validation_failed']}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())