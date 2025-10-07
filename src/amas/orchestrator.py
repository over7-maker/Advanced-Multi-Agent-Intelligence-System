#!/usr/bin/env python3
"""
AMAS Main Orchestrator
Coordinates all agents and manages task execution
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from .providers.manager import provider_manager
from .intelligence.intelligence_manager import intelligence_manager

class AMASOrchestrator:
    """Main orchestrator for the AMAS system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = self._initialize_agents()
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
    def _initialize_agents(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all available agents"""
        return {
            "security_expert": {
                "name": "Security Expert",
                "description": "Specializes in security analysis, vulnerability scanning, and threat assessment",
                "capabilities": ["vulnerability_scanning", "penetration_testing", "threat_analysis", "security_audit"],
                "status": "ready"
            },
            "code_analysis": {
                "name": "Code Analysis",
                "description": "Analyzes code quality, performance, and architectural patterns",
                "capabilities": ["static_analysis", "code_quality", "performance_optimization", "architectural_review"],
                "status": "ready"
            },
            "intelligence_gathering": {
                "name": "Intelligence Gathering",
                "description": "Conducts OSINT research and data collection",
                "capabilities": ["osint_research", "social_media_analysis", "domain_investigation", "threat_intelligence"],
                "status": "ready"
            },
            "performance_monitor": {
                "name": "Performance Monitor",
                "description": "Monitors system performance and optimizes resource usage",
                "capabilities": ["system_monitoring", "performance_profiling", "resource_optimization", "bottleneck_identification"],
                "status": "ready"
            },
            "documentation_specialist": {
                "name": "Documentation Specialist",
                "description": "Creates and maintains technical documentation",
                "capabilities": ["technical_writing", "api_documentation", "user_guides", "knowledge_management"],
                "status": "ready"
            },
            "testing_coordinator": {
                "name": "Testing Coordinator",
                "description": "Manages testing strategies and quality assurance",
                "capabilities": ["test_planning", "quality_assurance", "automation_testing", "regression_testing"],
                "status": "ready"
            },
            "integration_manager": {
                "name": "Integration Manager",
                "description": "Handles system integration and API coordination",
                "capabilities": ["system_integration", "api_coordination", "workflow_orchestration", "service_mesh"],
                "status": "ready"
            }
        }
    
    async def execute_task(self, task_type: str, target: str, parameters: Dict[str, Any] = None, 
                          user_id: str = "system") -> Dict[str, Any]:
        """Execute a task using the optimal agent combination"""
        
        task_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        self.logger.info(f"🎯 Executing task {task_id}: {task_type} on {target}")
        
        try:
            # Prepare task data
            task_data = {
                "task_id": task_id,
                "task_type": task_type,
                "target": target,
                "parameters": parameters or {},
                "user_id": user_id,
                "start_time": start_time.isoformat()
            }
            
            # Optimize task using intelligence systems
            optimization = await intelligence_manager.optimize_task_before_execution(task_data)
            
            # Select optimal agents
            optimal_agents = optimization['optimal_agents']
            task_prediction = optimization['task_prediction']
            
            self.logger.info(f"🤖 Selected agents: {', '.join(optimal_agents)}")
            self.logger.info(f"📊 Predicted success: {task_prediction.success_probability:.2f}")
            
            # Execute task with selected agents
            result = await self._execute_with_agents(task_id, task_type, target, 
                                                   parameters or {}, optimal_agents)
            
            # Calculate execution metrics
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Process task completion for learning
            completion_data = {
                **task_data,
                "agents_used": optimal_agents,
                "execution_time": execution_time,
                "success_rate": result.get('success_rate', 0.8),
                "solution_quality": result.get('quality_score', 0.8),
                "error_patterns": result.get('errors', []),
                "result": result
            }
            
            await intelligence_manager.process_task_completion(completion_data)
            
            # Store completed task
            self.completed_tasks.append(completion_data)
            
            self.logger.info(f"✅ Task {task_id} completed successfully in {execution_time:.2f}s")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "execution_time": execution_time,
                "agents_used": optimal_agents,
                "result": result,
                "prediction_accuracy": task_prediction.confidence
            }
            
        except Exception as e:
            self.logger.error(f"❌ Task {task_id} failed: {e}")
            
            # Record failure for learning
            failure_data = {
                **task_data,
                "agents_used": optimization.get('optimal_agents', []),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "success_rate": 0.0,
                "solution_quality": 0.0,
                "error_patterns": [str(e)],
                "result": {"error": str(e)}
            }
            
            await intelligence_manager.process_task_completion(failure_data)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _execute_with_agents(self, task_id: str, task_type: str, target: str, 
                                 parameters: Dict[str, Any], agents: List[str]) -> Dict[str, Any]:
        """Execute task with specific agents"""
        
        # Get the best available provider
        provider = provider_manager.get_best_provider()
        if not provider:
            raise RuntimeError("No AI providers available")
        
        # Prepare the prompt for the agents
        prompt = self._create_agent_prompt(task_type, target, parameters, agents)
        
        # Execute with the provider
        try:
            response = provider.infer(prompt)
            
            # Parse response (simplified for now)
            result = {
                "response": response,
                "success_rate": 0.9,
                "quality_score": 0.8,
                "errors": [],
                "agent_analysis": self._analyze_agent_performance(agents, response)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Provider execution failed: {e}")
            raise
    
    def _create_agent_prompt(self, task_type: str, target: str, parameters: Dict[str, Any], 
                           agents: List[str]) -> str:
        """Create a prompt for the selected agents"""
        
        agent_descriptions = []
        for agent_id in agents:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent_descriptions.append(f"- {agent['name']}: {agent['description']}")
        
        prompt = f"""
You are a team of AI specialists working together on a {task_type} task.

TARGET: {target}
PARAMETERS: {parameters}

AGENT TEAM:
{chr(10).join(agent_descriptions)}

Please collaborate to complete this task effectively. Each agent should contribute their expertise to provide a comprehensive solution.

Provide a detailed analysis and recommendations.
"""
        return prompt
    
    def _analyze_agent_performance(self, agents: List[str], response: str) -> Dict[str, Any]:
        """Analyze how well the agents performed"""
        
        # Simple analysis based on response length and content
        analysis = {
            "agents_used": agents,
            "response_length": len(response),
            "has_recommendations": "recommend" in response.lower(),
            "has_analysis": "analysis" in response.lower(),
            "completeness_score": min(1.0, len(response) / 500)  # Simple completeness metric
        }
        
        return analysis
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        
        # Get provider status
        provider_status = provider_manager.get_provider_status()
        enabled_providers = len([p for p in provider_status.values() if p['available']])
        
        # Get intelligence system status
        intelligence_data = await intelligence_manager.get_intelligence_dashboard_data()
        
        return {
            "system_status": "operational",
            "agents": {
                "total": len(self.agents),
                "ready": len([a for a in self.agents.values() if a['status'] == 'ready']),
                "busy": len([a for a in self.agents.values() if a['status'] == 'busy'])
            },
            "providers": {
                "total_configured": len(provider_status),
                "enabled": enabled_providers,
                "status": provider_status
            },
            "tasks": {
                "completed": len(self.completed_tasks),
                "active": len(self.active_tasks),
                "queued": self.task_queue.qsize()
            },
            "intelligence": intelligence_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get detailed agent capabilities"""
        
        capabilities = {}
        for agent_id, agent_info in self.agents.items():
            capabilities[agent_id] = {
                "name": agent_info["name"],
                "description": agent_info["description"],
                "capabilities": agent_info["capabilities"],
                "status": agent_info["status"]
            }
        
        return capabilities

# Global orchestrator instance
orchestrator = AMASOrchestrator()

async def get_orchestrator() -> AMASOrchestrator:
    """Get the global orchestrator instance"""
    return orchestrator

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AMAS Orchestrator")
    parser.add_argument("--task", help="Task type to execute")
    parser.add_argument("--target", help="Target for the task")
    parser.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def main():
        if args.status:
            status = await orchestrator.get_system_status()
            print("📊 AMAS System Status:")
            print(f"  Agents: {status['agents']['ready']}/{status['agents']['total']} ready")
            print(f"  Providers: {status['providers']['enabled']}/{status['providers']['total_configured']} enabled")
            print(f"  Tasks: {status['tasks']['completed']} completed, {status['tasks']['active']} active")
        
        elif args.task and args.target:
            result = await orchestrator.execute_task(args.task, args.target)
            print(f"✅ Task completed: {result}")
        
        else:
            print("Use --help for available options")
    
    asyncio.run(main())