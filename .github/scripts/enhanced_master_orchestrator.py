#!/usr/bin/env python3
"""
Enhanced Master Orchestrator - Layer 4 Agent
Coordinates all AI agents and workflows with intelligent decision making
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


class EnhancedMasterOrchestrator:
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "unknown")
        
        # Layer results from previous layers
        self.layer1_results = self._load_layer_results("layer1_analysis_results.json")
        self.layer2_results = self._load_layer_results("conflict_resolution_results.json")
        self.layer3_results = self._load_layer_results("automated_fix_results.json")
        
        # Initialize AI clients
        self.ai_clients = self._initialize_ai_clients()
        
        # Orchestration results
        self.orchestration_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "pending",
            "layer_coordination": {},
            "intelligent_decisions": [],
            "workflow_optimization": {},
            "performance_analysis": {},
            "recommendations": [],
            "next_actions": [],
            "agent_performance": {}
        }

    def _initialize_ai_clients(self) -> List[Dict[str, Any]]:
        """Initialize AI clients for orchestration"""
        clients = []
        
        providers = [
            {
                "name": "DeepSeek",
                "key": os.environ.get("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "priority": 1,
                "specialization": "orchestration"
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

    def _load_layer_results(self, filename: str) -> Dict[str, Any]:
        """Load results from a specific layer"""
        try:
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return {}

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
                max_tokens=5000,
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

    async def _analyze_layer_coordination(self) -> Dict[str, Any]:
        """Analyze coordination between all layers"""
        system_prompt = """You are an expert AI system orchestrator and workflow coordinator.
        
        Your role is to:
        1. Analyze the performance and coordination of all AI agent layers
        2. Identify bottlenecks, conflicts, and optimization opportunities
        3. Provide intelligent recommendations for system improvement
        4. Coordinate cross-layer communication and data flow
        5. Ensure optimal resource utilization and performance
        
        Analyze the multi-layer AI system performance and provide:
        {
            "layer_analysis": {
                "layer1_status": "success|partial|failed",
                "layer2_status": "success|partial|failed", 
                "layer3_status": "success|partial|failed",
                "coordination_score": 0-100,
                "bottlenecks": ["bottleneck1", "bottleneck2"],
                "optimization_opportunities": ["opt1", "opt2"]
            },
            "workflow_optimization": {
                "parallel_processing": ["task1", "task2"],
                "sequential_dependencies": ["dep1", "dep2"],
                "resource_allocation": {"cpu": "high|medium|low", "memory": "high|medium|low"},
                "timing_optimization": ["suggestion1", "suggestion2"]
            },
            "intelligent_decisions": [
                {"decision": "description", "reasoning": "why", "impact": "high|medium|low", "priority": 1-5}
            ],
            "performance_metrics": {
                "overall_efficiency": 0-100,
                "agent_utilization": 0-100,
                "error_rate": 0-100,
                "response_time_avg": "seconds"
            },
            "recommendations": [
                {"type": "immediate|short_term|long_term", "description": "what to do", "priority": 1-5}
            ]
        }"""
        
        prompt = f"""Analyze the coordination and performance of the multi-layer AI system:

LAYER 1 (Detection & Analysis) Results:
{json.dumps(self.layer1_results, indent=2)}

LAYER 2 (Intelligence & Decision) Results:
{json.dumps(self.layer2_results, indent=2)}

LAYER 3 (Execution & Fix) Results:
{json.dumps(self.layer3_results, indent=2)}

Please provide a comprehensive analysis of:
1. How well the layers are coordinating
2. Performance bottlenecks and optimization opportunities
3. Intelligent decisions for system improvement
4. Workflow optimization recommendations
5. Overall system health and efficiency"""
        
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
                        "layer_analysis": {"coordination_score": 50},
                        "workflow_optimization": {},
                        "intelligent_decisions": [],
                        "performance_metrics": {"overall_efficiency": 50},
                        "recommendations": []
                    }
        
        return {"error": "All AI providers failed"}

    async def _generate_workflow_optimization(self) -> Dict[str, Any]:
        """Generate workflow optimization recommendations"""
        system_prompt = """You are an expert workflow optimization specialist.
        
        Analyze the current AI workflow system and provide optimization recommendations:
        {
            "current_workflow_analysis": {
                "efficiency_score": 0-100,
                "bottlenecks": ["bottleneck1", "bottleneck2"],
                "redundancies": ["redundancy1", "redundancy2"],
                "missing_optimizations": ["opt1", "opt2"]
            },
            "optimization_recommendations": [
                {
                    "type": "parallel_processing|resource_optimization|workflow_restructure",
                    "description": "what to optimize",
                    "impact": "high|medium|low",
                    "effort": "high|medium|low",
                    "priority": 1-5
                }
            ],
            "immediate_actions": [
                {"action": "description", "command": "how to execute", "expected_impact": "description"}
            ],
            "long_term_strategy": {
                "vision": "long term optimization vision",
                "milestones": ["milestone1", "milestone2"],
                "success_metrics": ["metric1", "metric2"]
            }
        }"""
        
        prompt = f"""Analyze the current AI workflow system and provide optimization recommendations:

Current System Status:
- Layer 1: {self.layer1_results.get('quality_metrics', {})}
- Layer 2: {self.layer2_results.get('resolution_plan', {})}
- Layer 3: {self.layer3_results.get('performance_metrics', {})}

Please provide comprehensive workflow optimization recommendations focusing on:
1. Efficiency improvements
2. Resource optimization
3. Parallel processing opportunities
4. Workflow restructuring
5. Performance enhancements"""
        
        # Try each AI client
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    optimization = json.loads(result["content"])
                    optimization["provider"] = result["provider"]
                    optimization["response_time"] = result["response_time"]
                    return optimization
                except json.JSONDecodeError:
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_optimization": result["content"],
                        "current_workflow_analysis": {"efficiency_score": 50},
                        "optimization_recommendations": [],
                        "immediate_actions": [],
                        "long_term_strategy": {}
                    }
        
        return {"error": "All AI providers failed"}

    async def _generate_intelligent_decisions(self) -> List[Dict[str, Any]]:
        """Generate intelligent decisions for system improvement"""
        system_prompt = """You are an expert AI system decision maker and strategic planner.
        
        Based on the multi-layer AI system analysis, generate intelligent decisions:
        {
            "decisions": [
                {
                    "id": "decision_1",
                    "type": "immediate|short_term|long_term",
                    "description": "what decision to make",
                    "reasoning": "why this decision",
                    "impact": "high|medium|low",
                    "priority": 1-5,
                    "resources_required": ["resource1", "resource2"],
                    "timeline": "immediate|1-7 days|1-4 weeks|1-3 months",
                    "success_criteria": ["criteria1", "criteria2"],
                    "risk_assessment": "low|medium|high",
                    "rollback_plan": "how to undo if needed"
                }
            ],
            "decision_priorities": [
                {"decision_id": "decision_1", "priority": 1, "reason": "why this priority"}
            ],
            "resource_allocation": {
                "ai_agents": {"allocation": "description"},
                "computational_resources": {"allocation": "description"},
                "time_allocation": {"allocation": "description"}
            }
        }"""
        
        prompt = f"""Generate intelligent decisions for improving the multi-layer AI system:

System Analysis:
- Layer 1 Performance: {self.layer1_results.get('quality_metrics', {})}
- Layer 2 Intelligence: {self.layer2_results.get('resolution_plan', {})}
- Layer 3 Execution: {self.layer3_results.get('performance_metrics', {})}

Please generate strategic decisions focusing on:
1. Immediate improvements that can be implemented now
2. Short-term optimizations (1-7 days)
3. Long-term strategic improvements (1-3 months)
4. Resource allocation and prioritization
5. Risk management and mitigation"""
        
        # Try each AI client
        for client_info in self.ai_clients:
            result = await self._analyze_with_ai(prompt, system_prompt, client_info)
            
            if result and result.get("success"):
                try:
                    decisions = json.loads(result["content"])
                    decisions["provider"] = result["provider"]
                    decisions["response_time"] = result["response_time"]
                    return decisions
                except json.JSONDecodeError:
                    return {
                        "provider": result["provider"],
                        "response_time": result["response_time"],
                        "raw_decisions": result["content"],
                        "decisions": [],
                        "decision_priorities": [],
                        "resource_allocation": {}
                    }
        
        return {"error": "All AI providers failed"}

    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "overall_efficiency": 0,
            "layer_performance": {},
            "agent_utilization": {},
            "error_rates": {},
            "response_times": {},
            "success_rates": {},
            "bottlenecks": [],
            "optimization_opportunities": []
        }
        
        # Analyze Layer 1 performance
        layer1_metrics = self.layer1_results.get("quality_metrics", {})
        layer1_perf = {
            "files_analyzed": layer1_metrics.get("total_files_analyzed", 0),
            "issues_found": layer1_metrics.get("total_issues_found", 0),
            "critical_issues": layer1_metrics.get("critical_issues", 0),
            "efficiency_score": 100 - (layer1_metrics.get("critical_issues", 0) * 10)
        }
        metrics["layer_performance"]["layer1"] = layer1_perf
        
        # Analyze Layer 2 performance
        layer2_plan = self.layer2_results.get("resolution_plan", {})
        layer2_perf = {
            "conflicts_detected": len(self.layer2_results.get("conflicts_detected", [])),
            "resolution_strategy": layer2_plan.get("resolution_strategy", {}).get("approach", "unknown"),
            "risk_level": layer2_plan.get("resolution_strategy", {}).get("risk_level", "unknown"),
            "efficiency_score": 100 if layer2_plan.get("resolution_strategy", {}).get("risk_level") == "low" else 70
        }
        metrics["layer_performance"]["layer2"] = layer2_perf
        
        # Analyze Layer 3 performance
        layer3_metrics = self.layer3_results.get("performance_metrics", {})
        layer3_perf = {
            "fixes_attempted": layer3_metrics.get("fixes_attempted", 0),
            "fixes_applied": layer3_metrics.get("fixes_applied", 0),
            "success_rate": layer3_metrics.get("success_rate", 0),
            "validation_status": layer3_metrics.get("validation_status", "unknown"),
            "efficiency_score": layer3_metrics.get("success_rate", 0)
        }
        metrics["layer_performance"]["layer3"] = layer3_perf
        
        # Calculate overall efficiency
        layer_scores = [layer1_perf["efficiency_score"], layer2_perf["efficiency_score"], layer3_perf["efficiency_score"]]
        metrics["overall_efficiency"] = sum(layer_scores) / len(layer_scores) if layer_scores else 0
        
        # Analyze agent performance
        for layer_name, layer_data in [("layer1", self.layer1_results), ("layer2", self.layer2_results), ("layer3", self.layer3_results)]:
            agent_perf = layer_data.get("agent_performance", {})
            for agent_name, agent_data in agent_perf.items():
                if agent_name not in metrics["agent_utilization"]:
                    metrics["agent_utilization"][agent_name] = {
                        "success_rate": 0,
                        "avg_response_time": 0,
                        "usage_count": 0
                    }
                
                metrics["agent_utilization"][agent_name]["success_rate"] = max(
                    metrics["agent_utilization"][agent_name]["success_rate"],
                    agent_data.get("success_rate", 0)
                )
                metrics["agent_utilization"][agent_name]["avg_response_time"] = max(
                    metrics["agent_utilization"][agent_name]["avg_response_time"],
                    agent_data.get("avg_response_time", 0)
                )
                metrics["agent_utilization"][agent_name]["usage_count"] += 1
        
        return metrics

    async def run_orchestration(self) -> Dict[str, Any]:
        """Run comprehensive orchestration analysis"""
        print("🎯 Enhanced Master Orchestrator Starting...")
        print(f"Repository: {self.repo_name}")
        
        # Analyze layer coordination
        print("Analyzing layer coordination...")
        coordination_analysis = await self._analyze_layer_coordination()
        self.orchestration_results["layer_coordination"] = coordination_analysis
        
        # Generate workflow optimization
        print("Generating workflow optimization...")
        workflow_optimization = await self._generate_workflow_optimization()
        self.orchestration_results["workflow_optimization"] = workflow_optimization
        
        # Generate intelligent decisions
        print("Generating intelligent decisions...")
        intelligent_decisions = await self._generate_intelligent_decisions()
        self.orchestration_results["intelligent_decisions"] = intelligent_decisions.get("decisions", [])
        
        # Calculate performance metrics
        print("Calculating performance metrics...")
        performance_metrics = await self._calculate_performance_metrics()
        self.orchestration_results["performance_analysis"] = performance_metrics
        
        # Extract recommendations
        all_recommendations = []
        if "recommendations" in coordination_analysis:
            all_recommendations.extend(coordination_analysis["recommendations"])
        if "optimization_recommendations" in workflow_optimization:
            all_recommendations.extend(workflow_optimization["optimization_recommendations"])
        if "immediate_actions" in workflow_optimization:
            all_recommendations.extend(workflow_optimization["immediate_actions"])
        
        self.orchestration_results["recommendations"] = all_recommendations
        
        # Generate next actions
        next_actions = []
        if "immediate_actions" in workflow_optimization:
            next_actions.extend(workflow_optimization["immediate_actions"])
        if "decisions" in intelligent_decisions:
            immediate_decisions = [d for d in intelligent_decisions["decisions"] if d.get("type") == "immediate"]
            next_actions.extend(immediate_decisions)
        
        self.orchestration_results["next_actions"] = next_actions
        
        # Determine overall status
        if performance_metrics["overall_efficiency"] >= 80:
            self.orchestration_results["overall_status"] = "excellent"
        elif performance_metrics["overall_efficiency"] >= 60:
            self.orchestration_results["overall_status"] = "good"
        elif performance_metrics["overall_efficiency"] >= 40:
            self.orchestration_results["overall_status"] = "needs_improvement"
        else:
            self.orchestration_results["overall_status"] = "critical"
        
        # Update agent performance
        for client_info in self.ai_clients:
            self.orchestration_results["agent_performance"][client_info["name"]] = {
                "success_count": client_info["success_count"],
                "failure_count": client_info["failure_count"],
                "avg_response_time": client_info["avg_response_time"],
                "success_rate": client_info["success_count"] / (client_info["success_count"] + client_info["failure_count"]) * 100 if (client_info["success_count"] + client_info["failure_count"]) > 0 else 0
            }
        
        # Save results
        with open("master_orchestration_results.json", "w") as f:
            json.dump(self.orchestration_results, f, indent=2)
        
        print(f"✅ Master Orchestration Complete!")
        print(f"   Overall Status: {self.orchestration_results['overall_status']}")
        print(f"   Overall Efficiency: {performance_metrics['overall_efficiency']:.1f}%")
        print(f"   Recommendations: {len(self.orchestration_results['recommendations'])}")
        print(f"   Next Actions: {len(self.orchestration_results['next_actions'])}")
        print(f"   Intelligent Decisions: {len(self.orchestration_results['intelligent_decisions'])}")
        
        return self.orchestration_results


async def main():
    """Main function"""
    orchestrator = EnhancedMasterOrchestrator()
    results = await orchestrator.run_orchestration()
    
    # Print summary
    print("\n" + "="*80)
    print("🎯 ENHANCED MASTER ORCHESTRATOR - SUMMARY")
    print("="*80)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Overall Efficiency: {results['performance_analysis']['overall_efficiency']:.1f}%")
    print(f"Layer 1 Efficiency: {results['performance_analysis']['layer_performance']['layer1']['efficiency_score']:.1f}%")
    print(f"Layer 2 Efficiency: {results['performance_analysis']['layer_performance']['layer2']['efficiency_score']:.1f}%")
    print(f"Layer 3 Efficiency: {results['performance_analysis']['layer_performance']['layer3']['efficiency_score']:.1f}%")
    print(f"Recommendations: {len(results['recommendations'])}")
    print(f"Next Actions: {len(results['next_actions'])}")
    print(f"Intelligent Decisions: {len(results['intelligent_decisions'])}")
    
    print("\n🏥 Agent Performance:")
    for agent, perf in results['agent_performance'].items():
        print(f"  {agent}: {perf['success_rate']:.1f}% success rate, {perf['avg_response_time']:.2f}s avg")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())