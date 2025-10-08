#!/usr/bin/env python3
"""
AMAS Enhanced Orchestrator with Multi-API Fallback

This module provides an enhanced orchestrator that integrates with the AI API Manager
to ensure maximum reliability and performance across all AI operations.
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from .ai_api_manager import AIAPIManager, get_ai_response
from .api_clients import APIClientFactory, get_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of a task execution"""

    task_id: str
    task_type: str
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None
    api_used: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = ""
    retry_count: int = 0

@dataclass
class AgentCapability:
    """Agent capability definition"""

    name: str
    description: str
    task_types: List[str]
    preferred_apis: List[str]
    max_retries: int = 3
    timeout: int = 30

class EnhancedOrchestrator:
    """Enhanced orchestrator with multi-API fallback and intelligent task routing"""

    def __init__(self):
        """Initialize the enhanced orchestrator"""
        self.api_manager = AIAPIManager()
        self.task_queue: List[Dict] = []
        self.results: Dict[str, TaskResult] = {}
        self.agent_capabilities: Dict[str, AgentCapability] = {}

        # Initialize agent capabilities
        self._setup_agent_capabilities()

        logger.info("Enhanced Orchestrator initialized")

    def _setup_agent_capabilities(self):
        """Setup agent capabilities and their preferred APIs"""

        self.agent_capabilities = {
            "osint_agent": AgentCapability(
                name="OSINT Agent",
                description="Open Source Intelligence collection and analysis",
                task_types=["osint", "data_gathering", "source_validation"],
                preferred_apis=["deepseek", "grok", "codestral", "nvidia"],
                max_retries=3,
                timeout=45,
            ),
            "analysis_agent": AgentCapability(
                name="Analysis Agent",
                description="Deep analysis and pattern recognition",
                task_types=["analysis", "pattern_recognition", "threat_assessment"],
                preferred_apis=["glm", "grok", "deepseek", "nvidia"],
                max_retries=3,
                timeout=60,
            ),
            "code_agent": AgentCapability(
                name="Code Intelligence Agent",
                description="Code analysis and vulnerability detection",
                task_types=[
                    "code_analysis",
                    "vulnerability_detection",
                    "technical_assessment",
                ],
                preferred_apis=["codestral", "nvidia", "deepseek", "qwen"],
                max_retries=2,
                timeout=30,
            ),
            "reporting_agent": AgentCapability(
                name="Reporting Agent",
                description="Report generation and synthesis",
                task_types=["reporting", "synthesis", "documentation"],
                preferred_apis=["grok", "glm", "deepseek", "gemini"],
                max_retries=3,
                timeout=45,
            ),
            "forensics_agent": AgentCapability(
                name="Forensics Agent",
                description="Digital forensics and investigation",
                task_types=["forensics", "investigation", "evidence_analysis"],
                preferred_apis=["deepseek", "nvidia", "codestral", "grok"],
                max_retries=3,
                timeout=60,
            ),
            "general_agent": AgentCapability(
                name="General Agent",
                description="General purpose AI assistance",
                task_types=["general", "reasoning", "analysis"],
                preferred_apis=["deepseek", "glm", "grok", "nvidia"],
                max_retries=3,
                timeout=30,
            ),
        }

    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        prompt: str,
        system_prompt: str = None,
        agent_type: str = None,
        max_retries: int = None,
        timeout: int = None,
    ) -> TaskResult:
        """
        Execute a task with intelligent API selection and fallback

        Args:
            task_id: Unique identifier for the task
            task_type: Type of task (osint, analysis, code_analysis, etc.)
            prompt: Task prompt
            system_prompt: System prompt (optional)
            agent_type: Specific agent type to use (optional)
            max_retries: Maximum retry attempts (optional)
            timeout: Task timeout (optional)

        Returns:
            TaskResult with execution details
        """
        start_time = time.time()

        # Determine agent type if not specified
        if not agent_type:
            agent_type = self._determine_agent_type(task_type)

        # Get agent capabilities
        agent_cap = self.agent_capabilities.get(
            agent_type, self.agent_capabilities["general_agent"]
        )

        # Set retry and timeout parameters
        max_retries = max_retries or agent_cap.max_retries
        timeout = timeout or agent_cap.timeout

        # Create task result
        result = TaskResult(
            task_id=task_id,
            task_type=task_type,
            success=False,
            timestamp=datetime.now().isoformat(),
        )

        # Execute with retries
        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"Executing task {task_id} (attempt {attempt + 1}/{max_retries + 1})"
                )

                # Get AI response with fallback
                ai_response = await self.api_manager.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt
                    or self._get_system_prompt(agent_type, task_type),
                    task_type=task_type,
                    max_tokens=4000,
                    temperature=0.7,
                    timeout=timeout,
                )

                # Update result with success
                result.success = True
                result.result = ai_response
                result.api_used = ai_response.get("api_used", "unknown")
                result.execution_time = time.time() - start_time
                result.retry_count = attempt

                logger.info(
                    f"Task {task_id} completed successfully using {result.api_used}"
                )
                break

            except Exception as e:
                result.error = str(e)
                result.retry_count = attempt

                if attempt < max_retries:
                    wait_time = min(2**attempt, 10)  # Exponential backoff
                    logger.warning(
                        f"Task {task_id} attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"Task {task_id} failed after {max_retries + 1} attempts: {e}"
                    )

        result.execution_time = time.time() - start_time
        self.results[task_id] = result

        return result

    def _determine_agent_type(self, task_type: str) -> str:
        """Determine the best agent type for a given task type"""

        # Map task types to agent types
        task_agent_map = {
            "osint": "osint_agent",
            "data_gathering": "osint_agent",
            "source_validation": "osint_agent",
            "analysis": "analysis_agent",
            "pattern_recognition": "analysis_agent",
            "threat_assessment": "analysis_agent",
            "code_analysis": "code_agent",
            "vulnerability_detection": "code_agent",
            "technical_assessment": "code_agent",
            "reporting": "reporting_agent",
            "synthesis": "reporting_agent",
            "documentation": "reporting_agent",
            "forensics": "forensics_agent",
            "investigation": "forensics_agent",
            "evidence_analysis": "forensics_agent",
        }

        return task_agent_map.get(task_type, "general_agent")

    def _get_system_prompt(self, agent_type: str, task_type: str) -> str:
        """Get appropriate system prompt for agent type and task"""

        system_prompts = {
            "osint_agent": """You are an OSINT (Open Source Intelligence) specialist. Your role is to:
1. Collect and analyze open source information
2. Validate sources and assess credibility
3. Identify patterns and connections
4. Provide actionable intelligence

Focus on accuracy, source verification, and comprehensive analysis.""",
            "analysis_agent": """You are an Intelligence Analysis specialist. Your role is to:
1. Perform deep analysis of information
2. Identify patterns, trends, and anomalies
3. Assess threats and risks
4. Provide strategic insights

Focus on analytical rigor, pattern recognition, and strategic thinking.""",
            "code_agent": """You are a Code Intelligence specialist. Your role is to:
1. Analyze code for vulnerabilities and issues
2. Assess technical architecture and design
3. Provide security recommendations
4. Evaluate code quality and maintainability

Focus on technical accuracy, security best practices, and actionable recommendations.""",
            "reporting_agent": """You are a Reporting and Synthesis specialist. Your role is to:
1. Synthesize complex information into clear reports
2. Create executive summaries and briefings
3. Organize information logically
4. Ensure clarity and actionable insights

Focus on clarity, organization, and executive-level communication.""",
            "forensics_agent": """You are a Digital Forensics specialist. Your role is to:
1. Analyze digital evidence and artifacts
2. Investigate security incidents
3. Trace attack vectors and timelines
4. Provide forensic insights

Focus on technical accuracy, evidence preservation, and investigative methodology.""",
            "general_agent": """You are a general-purpose AI assistant specialized in intelligence and analysis. Your role is to:
1. Provide accurate and helpful responses
2. Analyze information thoroughly
3. Offer insights and recommendations
4. Maintain professional standards

Focus on accuracy, helpfulness, and professional communication.""",
        }

        return system_prompts.get(agent_type, system_prompts["general_agent"])

    async def execute_parallel_tasks(
        self, tasks: List[Dict], max_concurrent: int = 5
    ) -> List[TaskResult]:
        """
        Execute multiple tasks in parallel with concurrency control

        Args:
            tasks: List of task dictionaries with required fields
            max_concurrent: Maximum concurrent task execution

        Returns:
            List of TaskResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_task(**task)

        # Execute all tasks
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks], return_exceptions=True
        )

        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, TaskResult):
                valid_results.append(result)
            else:
                logger.error(f"Task execution failed with exception: {result}")

        return valid_results

    async def run_investigation_workflow(
        self, topic: str, investigation_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Run a comprehensive investigation workflow

        Args:
            topic: Investigation topic
            investigation_type: Type of investigation (comprehensive, focused, rapid)

        Returns:
            Investigation results and report
        """
        logger.info(f"Starting {investigation_type} investigation: {topic}")

        # Define investigation phases based on type
        if investigation_type == "comprehensive":
            phases = [
                {
                    "task_id": f"osint_{int(time.time())}",
                    "task_type": "osint",
                    "prompt": f"Conduct comprehensive OSINT collection on: {topic}. Focus on recent developments, key players, and threat indicators.",
                    "agent_type": "osint_agent",
                },
                {
                    "task_id": f"analysis_{int(time.time())}",
                    "task_type": "analysis",
                    "prompt": f"Perform deep analysis of the OSINT findings for: {topic}. Identify patterns, threats, and strategic implications.",
                    "agent_type": "analysis_agent",
                },
                {
                    "task_id": f"technical_{int(time.time())}",
                    "task_type": "technical_assessment",
                    "prompt": f"Provide technical assessment of: {topic}. Focus on technical vulnerabilities, attack vectors, and mitigation strategies.",
                    "agent_type": "code_agent",
                },
                {
                    "task_id": f"report_{int(time.time())}",
                    "task_type": "reporting",
                    "prompt": f"Synthesize all findings into a comprehensive intelligence report on: {topic}. Include executive summary, key findings, and recommendations.",
                    "agent_type": "reporting_agent",
                },
            ]
        elif investigation_type == "focused":
            phases = [
                {
                    "task_id": f"focused_analysis_{int(time.time())}",
                    "task_type": "analysis",
                    "prompt": f"Perform focused analysis on: {topic}. Provide detailed assessment with specific recommendations.",
                    "agent_type": "analysis_agent",
                },
                {
                    "task_id": f"focused_report_{int(time.time())}",
                    "task_type": "reporting",
                    "prompt": f"Create a focused intelligence report on: {topic}. Include key findings and actionable recommendations.",
                    "agent_type": "reporting_agent",
                },
            ]
        else:  # rapid
            phases = [
                {
                    "task_id": f"rapid_assessment_{int(time.time())}",
                    "task_type": "analysis",
                    "prompt": f"Provide rapid assessment of: {topic}. Focus on immediate threats and urgent recommendations.",
                    "agent_type": "analysis_agent",
                }
            ]

        # Execute phases sequentially (each phase depends on previous results)
        investigation_results = {
            "topic": topic,
            "investigation_type": investigation_type,
            "started_at": datetime.now().isoformat(),
            "phases": [],
            "final_report": None,
        }

        context = ""
        for i, phase in enumerate(phases):
            logger.info(f"Executing phase {i + 1}: {phase['task_type']}")

            # Add context from previous phases
            if context:
                phase["prompt"] = (
                    f"Context from previous analysis:\n{context}\n\n{phase['prompt']}"
                )

            # Execute phase
            result = await self.execute_task(**phase)
            investigation_results["phases"].append(
                {"phase": i + 1, "task_type": phase["task_type"], "result": result}
            )

            # Add successful results to context
            if result.success and result.result:
                context += f"\n{phase['task_type'].title()} Results:\n{result.result.get('content', '')}\n"

        investigation_results["completed_at"] = datetime.now().isoformat()

        # Generate final report
        if investigation_results["phases"]:
            final_phase = investigation_results["phases"][-1]
            if final_phase["result"].success:
                investigation_results["final_report"] = final_phase[
                    "result"
                ].result.get("content", "")

        return investigation_results

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.results:
            return {"message": "No tasks executed yet"}

        total_tasks = len(self.results)
        successful_tasks = len([r for r in self.results.values() if r.success])
        failed_tasks = total_tasks - successful_tasks

        # API usage statistics
        api_usage = {}
        for result in self.results.values():
            if result.api_used:
                api_usage[result.api_used] = api_usage.get(result.api_used, 0) + 1

        # Average execution time
        avg_execution_time = (
            sum(r.execution_time for r in self.results.values()) / total_tasks
        )

        # Task type statistics
        task_type_stats = {}
        for result in self.results.values():
            task_type = result.task_type
            if task_type not in task_type_stats:
                task_type_stats[task_type] = {"total": 0, "successful": 0}
            task_type_stats[task_type]["total"] += 1
            if result.success:
                task_type_stats[task_type]["successful"] += 1

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (
                (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            ),
            "average_execution_time": avg_execution_time,
            "api_usage": api_usage,
            "task_type_stats": task_type_stats,
            "health_status": self.api_manager.get_health_status(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        logger.info("Performing comprehensive health check...")

        # Check API manager health
        api_health = await self.api_manager.health_check()

        # Test each agent capability
        agent_tests = {}
        for agent_name, agent_cap in self.agent_capabilities.items():
            try:
                test_result = await self.execute_task(
                    task_id=f"health_check_{agent_name}",
                    task_type=agent_cap.task_types[0],
                    prompt="This is a health check. Please respond with 'OK'.",
                    agent_type=agent_name,
                    max_retries=1,
                    timeout=10,
                )
                agent_tests[agent_name] = {
                    "status": "healthy" if test_result.success else "unhealthy",
                    "api_used": test_result.api_used,
                    "execution_time": test_result.execution_time,
                }
            except Exception as e:
                agent_tests[agent_name] = {"status": "unhealthy", "error": str(e)}

        return {
            "api_health": api_health,
            "agent_tests": agent_tests,
            "timestamp": datetime.now().isoformat(),
        }

# Global orchestrator instance
orchestrator = EnhancedOrchestrator()

# Convenience functions
async def execute_task(
    task_id: str, task_type: str, prompt: str, **kwargs
) -> TaskResult:
    """Execute a single task using the global orchestrator"""
    return await orchestrator.execute_task(task_id, task_type, prompt, **kwargs)

async def run_investigation(
    topic: str, investigation_type: str = "comprehensive"
) -> Dict[str, Any]:
    """Run an investigation using the global orchestrator"""
    return await orchestrator.run_investigation_workflow(topic, investigation_type)

# Example usage
async def main():
    """Example usage of the Enhanced Orchestrator"""
    print("🚀 AMAS Enhanced Orchestrator - Multi-API Fallback System")
    print("=" * 60)

    try:
        # Test single task execution
        print("\n🧪 Testing single task execution...")
        result = await execute_task(
            task_id="test_001",
            task_type="analysis",
            prompt="Analyze the current state of AI security threats and provide key recommendations.",
            agent_type="analysis_agent",
        )

        print(f"✅ Task completed: {result.success}")
        print(f"🔧 API used: {result.api_used}")
        print(f"⏱️ Execution time: {result.execution_time:.2f}s")
        if result.success:
            print(f"📝 Response preview: {result.result['content'][:200]}...")

        # Test investigation workflow
        print(f"\n🔍 Testing investigation workflow...")
        investigation = await run_investigation(
            topic="Advanced Persistent Threats targeting software supply chains",
            investigation_type="focused",
        )

        print(f"✅ Investigation completed")
        print(f"📊 Phases executed: {len(investigation['phases'])}")
        print(
            f"📄 Final report available: {'Yes' if investigation['final_report'] else 'No'}"
        )

        # Get performance stats
        print(f"\n📈 Performance Statistics:")
        stats = orchestrator.get_performance_stats()
        print(f"  Total tasks: {stats['total_tasks']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Average execution time: {stats['average_execution_time']:.2f}s")
        print(f"  API usage: {stats['api_usage']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
