#!/usr/bin/env python3
"""
AMAS API Integration Module

This module integrates the new AI API Manager with existing AMAS agents and orchestrators,
providing seamless fallback and enhanced reliability across all AI operations.
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging

# Import the new API manager components
from .ai_api_manager import AIAPIManager, get_ai_response
from .enhanced_orchestrator import EnhancedOrchestrator, execute_task, run_investigation

# Import existing AMAS components
from ..agents.orchestrator import (
    AgentOrchestrator,
    BaseAgent,
    Task,
    TaskStatus,
    AgentType,
)
from ..agents.osint.osint_agent import OSINTAgent
from ..agents.investigation.investigation_agent import InvestigationAgent
from ..agents.forensics.forensics_agent import ForensicsAgent
from ..agents.reporting.reporting_agent import ReportingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedLLMService:
    """Enhanced LLM service with multi-API fallback"""

    def __init__(self):
        self.api_manager = AIAPIManager()
        self.orchestrator = EnhancedOrchestrator()

    async def generate_response(
        self, prompt: str, system_prompt: str = None, task_type: str = None, **kwargs
    ) -> str:
        """Generate response using the enhanced API manager"""
        try:
            result = await self.api_manager.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type=task_type,
                **kwargs,
            )
            return result["content"]
        except Exception as e:
            logger.error(f"LLM service failed: {e}")
            # Fallback to simple response
            return f"AI Response: {prompt[:100]}... (API unavailable)"

    async def generate_streaming_response(
        self, prompt: str, system_prompt: str = None, task_type: str = None, **kwargs
    ):
        """Generate streaming response"""
        try:
            async for chunk in self.api_manager.generate_streaming_response(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type=task_type,
                **kwargs,
            ):
                yield chunk["content"]
        except Exception as e:
            logger.error(f"Streaming LLM service failed: {e}")
            yield f"AI Response: {prompt[:100]}... (API unavailable)"


class EnhancedAgent(BaseAgent):
    """Enhanced base agent with multi-API fallback"""

    def __init__(self, agent_id: str, name: str, agent_type: AgentType):
        super().__init__(agent_id, name, agent_type)
        self.llm_service = EnhancedLLMService()
        self.api_manager = AIAPIManager()

    async def generate_ai_response(
        self, prompt: str, system_prompt: str = None, task_type: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response with fallback"""
        try:
            return await self.api_manager.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type=task_type,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return {
                "content": f"AI Response: {prompt[:100]}... (API unavailable)",
                "api_used": "fallback",
                "error": str(e),
            }

    async def execute_task_with_fallback(self, task: Task) -> Dict[str, Any]:
        """Execute task with comprehensive fallback mechanisms"""
        try:
            # Try primary execution
            result = await self.execute_task(task)
            return result
        except Exception as e:
            logger.warning(f"Primary task execution failed: {e}")

            # Try fallback execution
            try:
                fallback_result = await self._execute_fallback_task(task)
                return fallback_result
            except Exception as fallback_error:
                logger.error(f"Fallback execution also failed: {fallback_error}")
                return {
                    "success": False,
                    "error": f"Primary: {e}, Fallback: {fallback_error}",
                    "task_id": task.id,
                    "timestamp": datetime.now().isoformat(),
                }

    async def _execute_fallback_task(self, task: Task) -> Dict[str, Any]:
        """Execute fallback task with simplified approach"""
        try:
            # Use the enhanced orchestrator for fallback
            result = await execute_task(
                task_id=task.id,
                task_type=task.type,
                prompt=task.description,
                agent_type=self._get_agent_type_for_fallback(),
            )

            return {
                "success": result.success,
                "result": result.result,
                "api_used": result.api_used,
                "execution_time": result.execution_time,
                "fallback": True,
            }
        except Exception as e:
            raise Exception(f"Fallback execution failed: {e}")

    def _get_agent_type_for_fallback(self) -> str:
        """Get appropriate agent type for fallback"""
        agent_type_map = {
            AgentType.OSINT: "osint_agent",
            AgentType.INVESTIGATION: "analysis_agent",
            AgentType.FORENSICS: "forensics_agent",
            AgentType.REPORTING: "reporting_agent",
            AgentType.DATA_ANALYSIS: "analysis_agent",
            AgentType.REVERSE_ENGINEERING: "code_agent",
            AgentType.METADATA: "analysis_agent",
            AgentType.TECHNOLOGY_MONITOR: "analysis_agent",
        }
        return agent_type_map.get(self.agent_type, "general_agent")


class EnhancedOSINTAgent(EnhancedAgent):
    """Enhanced OSINT agent with multi-API fallback"""

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or "osint_001", "Enhanced OSINT Agent", AgentType.OSINT
        )
        self.capabilities = [
            "osint_collection",
            "source_validation",
            "data_gathering",
            "threat_intelligence",
            "social_media_analysis",
        ]

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute OSINT task with enhanced capabilities"""
        try:
            # Use the enhanced orchestrator for OSINT tasks
            result = await execute_task(
                task_id=task.id,
                task_type="osint",
                prompt=task.description,
                agent_type="osint_agent",
            )

            return {
                "success": result.success,
                "osint_data": (
                    result.result.get("content", "") if result.success else None
                ),
                "sources": self._extract_sources(result.result.get("content", "")),
                "confidence": self._assess_confidence(result.result.get("content", "")),
                "api_used": result.api_used,
                "execution_time": result.execution_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"OSINT task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_sources(self, content: str) -> List[str]:
        """Extract sources from OSINT content"""
        # Simple source extraction - in production, use more sophisticated NLP
        sources = []
        lines = content.split("\n")
        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["source:", "reference:", "according to", "reported by"]
            ):
                sources.append(line.strip())
        return sources

    def _assess_confidence(self, content: str) -> float:
        """Assess confidence level of OSINT data"""
        # Simple confidence assessment based on content characteristics
        confidence_indicators = [
            "verified",
            "confirmed",
            "reliable",
            "official",
            "documented",
        ]
        uncertainty_indicators = [
            "unverified",
            "unconfirmed",
            "rumor",
            "alleged",
            "possible",
        ]

        content_lower = content.lower()
        confidence_score = 0.5  # Base confidence

        for indicator in confidence_indicators:
            if indicator in content_lower:
                confidence_score += 0.1

        for indicator in uncertainty_indicators:
            if indicator in content_lower:
                confidence_score -= 0.1

        return max(0.0, min(1.0, confidence_score))

    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the task"""
        osint_keywords = [
            "osint",
            "open source",
            "intelligence",
            "gathering",
            "social media",
            "public information",
            "threat intelligence",
        ]

        task_description = task.description.lower()
        return any(keyword in task_description for keyword in osint_keywords)


class EnhancedInvestigationAgent(EnhancedAgent):
    """Enhanced investigation agent with multi-API fallback"""

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or "investigation_001",
            "Enhanced Investigation Agent",
            AgentType.INVESTIGATION,
        )
        self.capabilities = [
            "investigation",
            "analysis",
            "pattern_recognition",
            "threat_assessment",
            "incident_response",
        ]

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute investigation task with enhanced capabilities"""
        try:
            # Use the enhanced orchestrator for investigation tasks
            result = await execute_task(
                task_id=task.id,
                task_type="analysis",
                prompt=task.description,
                agent_type="analysis_agent",
            )

            return {
                "success": result.success,
                "analysis": (
                    result.result.get("content", "") if result.success else None
                ),
                "threat_level": self._assess_threat_level(
                    result.result.get("content", "")
                ),
                "recommendations": self._extract_recommendations(
                    result.result.get("content", "")
                ),
                "api_used": result.api_used,
                "execution_time": result.execution_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Investigation task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _assess_threat_level(self, content: str) -> str:
        """Assess threat level from analysis content"""
        content_lower = content.lower()

        if any(
            keyword in content_lower
            for keyword in ["critical", "severe", "immediate", "urgent"]
        ):
            return "CRITICAL"
        elif any(
            keyword in content_lower for keyword in ["high", "significant", "serious"]
        ):
            return "HIGH"
        elif any(
            keyword in content_lower for keyword in ["medium", "moderate", "concerning"]
        ):
            return "MEDIUM"
        else:
            return "LOW"

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from analysis content"""
        recommendations = []
        lines = content.split("\n")

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "must", "action"]
            ):
                recommendations.append(line.strip())

        return recommendations

    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the task"""
        investigation_keywords = [
            "investigate",
            "analysis",
            "threat",
            "incident",
            "forensics",
            "evidence",
            "malware",
            "attack",
        ]

        task_description = task.description.lower()
        return any(keyword in task_description for keyword in investigation_keywords)


class EnhancedForensicsAgent(EnhancedAgent):
    """Enhanced forensics agent with multi-API fallback"""

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or "forensics_001", "Enhanced Forensics Agent", AgentType.FORENSICS
        )
        self.capabilities = [
            "digital_forensics",
            "evidence_analysis",
            "malware_analysis",
            "incident_response",
            "timeline_reconstruction",
        ]

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute forensics task with enhanced capabilities"""
        try:
            # Use the enhanced orchestrator for forensics tasks
            result = await execute_task(
                task_id=task.id,
                task_type="forensics",
                prompt=task.description,
                agent_type="forensics_agent",
            )

            return {
                "success": result.success,
                "forensics_analysis": (
                    result.result.get("content", "") if result.success else None
                ),
                "evidence_types": self._identify_evidence_types(
                    result.result.get("content", "")
                ),
                "timeline": self._extract_timeline(result.result.get("content", "")),
                "api_used": result.api_used,
                "execution_time": result.execution_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Forensics task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _identify_evidence_types(self, content: str) -> List[str]:
        """Identify types of evidence mentioned in analysis"""
        evidence_types = []
        content_lower = content.lower()

        evidence_keywords = {
            "log_files": ["log", "logs", "logging"],
            "memory_dumps": ["memory", "dump", "ram"],
            "network_traffic": ["network", "traffic", "packet", "pcap"],
            "file_system": ["file", "filesystem", "directory", "folder"],
            "registry": ["registry", "reg", "hive"],
            "browser_data": ["browser", "cache", "history", "cookies"],
        }

        for evidence_type, keywords in evidence_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                evidence_types.append(evidence_type)

        return evidence_types

    def _extract_timeline(self, content: str) -> List[str]:
        """Extract timeline information from forensics analysis"""
        timeline = []
        lines = content.split("\n")

        for line in lines:
            # Look for timestamp patterns
            if any(
                pattern in line
                for pattern in ["2024-", "2023-", "timestamp", "time:", "date:"]
            ):
                timeline.append(line.strip())

        return timeline

    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the task"""
        forensics_keywords = [
            "forensics",
            "evidence",
            "malware",
            "incident",
            "timeline",
            "analysis",
            "investigation",
            "digital",
        ]

        task_description = task.description.lower()
        return any(keyword in task_description for keyword in forensics_keywords)


class EnhancedReportingAgent(EnhancedAgent):
    """Enhanced reporting agent with multi-API fallback"""

    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id or "reporting_001", "Enhanced Reporting Agent", AgentType.REPORTING
        )
        self.capabilities = [
            "report_generation",
            "synthesis",
            "documentation",
            "executive_summary",
            "intelligence_briefing",
        ]

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute reporting task with enhanced capabilities"""
        try:
            # Use the enhanced orchestrator for reporting tasks
            result = await execute_task(
                task_id=task.id,
                task_type="reporting",
                prompt=task.description,
                agent_type="reporting_agent",
            )

            return {
                "success": result.success,
                "report": result.result.get("content", "") if result.success else None,
                "executive_summary": self._extract_executive_summary(
                    result.result.get("content", "")
                ),
                "key_findings": self._extract_key_findings(
                    result.result.get("content", "")
                ),
                "recommendations": self._extract_recommendations(
                    result.result.get("content", "")
                ),
                "api_used": result.api_used,
                "execution_time": result.execution_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Reporting task execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_executive_summary(self, content: str) -> str:
        """Extract executive summary from report"""
        lines = content.split("\n")
        summary_lines = []

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["executive summary", "summary", "overview"]
            ):
                summary_lines.append(line.strip())

        return "\n".join(summary_lines) if summary_lines else content[:500] + "..."

    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from report"""
        findings = []
        lines = content.split("\n")

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["finding", "discovered", "identified", "key"]
            ):
                findings.append(line.strip())

        return findings

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from report"""
        recommendations = []
        lines = content.split("\n")

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["recommend", "suggest", "should", "must", "action"]
            ):
                recommendations.append(line.strip())

        return recommendations

    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the task"""
        reporting_keywords = [
            "report",
            "summary",
            "briefing",
            "documentation",
            "synthesis",
            "analysis",
            "findings",
            "recommendations",
        ]

        task_description = task.description.lower()
        return any(keyword in task_description for keyword in reporting_keywords)


class EnhancedAgentOrchestrator(AgentOrchestrator):
    """Enhanced orchestrator with multi-API fallback integration"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.enhanced_llm_service = EnhancedLLMService()
        self.enhanced_orchestrator = EnhancedOrchestrator()

        # Replace the basic LLM service with enhanced version
        self.llm_service = self.enhanced_llm_service

    async def register_enhanced_agents(self):
        """Register enhanced agents with fallback capabilities"""
        # Register enhanced agents
        enhanced_agents = [
            EnhancedOSINTAgent(),
            EnhancedInvestigationAgent(),
            EnhancedForensicsAgent(),
            EnhancedReportingAgent(),
        ]

        for agent in enhanced_agents:
            await self.register_agent(agent)

        logger.info(f"Registered {len(enhanced_agents)} enhanced agents")

    async def execute_enhanced_react_cycle(self, task_id: str) -> List[Dict[str, Any]]:
        """Execute enhanced ReAct cycle with multi-API fallback"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return []

        task = self.tasks[task_id]
        if not task.assigned_agent:
            logger.error(f"Task {task_id} not assigned to any agent")
            return []

        agent = self.agents[task.assigned_agent]
        steps = []

        try:
            # Enhanced reasoning phase with fallback
            reasoning_prompt = f"""
            You are an intelligence agent tasked with: {task.description}
            
            Current context:
            - Task type: {task.type}
            - Priority: {task.priority.name}
            - Available data sources: {list(self.config.get('data_sources', []))}
            
            Please reason about the best approach to complete this task.
            Consider:
            1. What information do you need?
            2. What actions should you take?
            3. What are the potential risks or challenges?
            4. How will you validate your results?
            
            Provide a step-by-step plan.
            """

            reasoning = await self.enhanced_llm_service.generate_response(
                reasoning_prompt, task_type="analysis"
            )
            steps.append(
                {
                    "phase": "reasoning",
                    "content": reasoning,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Enhanced acting phase
            action_prompt = f"""
            Based on your reasoning, execute the following actions:
            
            {reasoning}
            
            For each action:
            1. Describe what you're doing
            2. Execute the action
            3. Record the results
            4. Assess if more information is needed
            
            Be specific and actionable.
            """

            actions = await self.enhanced_llm_service.generate_response(
                action_prompt, task_type="analysis"
            )
            steps.append(
                {
                    "phase": "acting",
                    "content": actions,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Enhanced observing phase
            observation_prompt = f"""
            Review the results of your actions:
            
            {actions}
            
            Analyze:
            1. What did you learn?
            2. Are there any gaps in your understanding?
            3. Do you need to take additional actions?
            4. What conclusions can you draw?
            
            Provide a comprehensive analysis.
            """

            observations = await self.enhanced_llm_service.generate_response(
                observation_prompt, task_type="analysis"
            )
            steps.append(
                {
                    "phase": "observing",
                    "content": observations,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Execute the actual task with fallback
            if isinstance(agent, EnhancedAgent):
                result = await agent.execute_task_with_fallback(task)
            else:
                result = await agent.execute_task(task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now()

            steps.append(
                {
                    "phase": "completion",
                    "content": f"Task completed successfully. Result: {result}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"Task {task_id} completed successfully")
            await self.event_bus.publish(
                "task_completed", {"task_id": task_id, "result": result}
            )

        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.now()

            steps.append(
                {
                    "phase": "error",
                    "content": f"Task failed with error: {e}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            await self.event_bus.publish(
                "task_failed", {"task_id": task_id, "error": str(e)}
            )

        finally:
            # Reset agent status
            agent.status = "idle"
            agent.current_task = None

        return steps

    async def run_enhanced_investigation(
        self, topic: str, investigation_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Run enhanced investigation with multi-API fallback"""
        try:
            # Use the enhanced orchestrator for investigation
            investigation_result = (
                await self.enhanced_orchestrator.run_investigation_workflow(
                    topic=topic, investigation_type=investigation_type
                )
            )

            return investigation_result

        except Exception as e:
            logger.error(f"Enhanced investigation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "investigation_type": investigation_type,
                "timestamp": datetime.now().isoformat(),
            }

    async def get_enhanced_performance_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics"""
        # Get basic orchestrator stats
        basic_stats = {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
            ),
            "failed_tasks": len(
                [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
            ),
            "active_agents": len(
                [a for a in self.agents.values() if a.status == "busy"]
            ),
            "idle_agents": len([a for a in self.agents.values() if a.status == "idle"]),
        }

        # Get enhanced orchestrator stats
        enhanced_stats = self.enhanced_orchestrator.get_performance_stats()

        # Combine stats
        combined_stats = {
            "basic_stats": basic_stats,
            "enhanced_stats": enhanced_stats,
            "timestamp": datetime.now().isoformat(),
        }

        return combined_stats


# Global enhanced orchestrator instance
enhanced_orchestrator = EnhancedAgentOrchestrator(
    {
        "llm_service_url": "http://localhost:11434",
        "vector_service_url": "http://localhost:8001",
        "graph_service_url": "http://localhost:7474",
        "data_sources": ["osint", "threat_intel", "malware_db", "vulnerability_db"],
    }
)


# Convenience functions
async def initialize_enhanced_system():
    """Initialize the enhanced AMAS system"""
    await enhanced_orchestrator.register_enhanced_agents()
    logger.info("Enhanced AMAS system initialized with multi-API fallback")


async def run_enhanced_investigation(
    topic: str, investigation_type: str = "comprehensive"
):
    """Run enhanced investigation"""
    return await enhanced_orchestrator.run_enhanced_investigation(
        topic, investigation_type
    )


# Example usage
async def main():
    """Example usage of the enhanced integration"""
    print("🚀 AMAS Enhanced Integration - Multi-API Fallback System")
    print("=" * 60)

    try:
        # Initialize enhanced system
        await initialize_enhanced_system()

        # Test enhanced investigation
        print("\n🔍 Testing enhanced investigation...")
        investigation = await run_enhanced_investigation(
            topic="Advanced Persistent Threats targeting critical infrastructure",
            investigation_type="focused",
        )

        print(f"✅ Investigation completed")
        print(f"📊 Phases: {len(investigation.get('phases', []))}")
        print(
            f"📄 Final report available: {'Yes' if investigation.get('final_report') else 'No'}"
        )

        # Get performance stats
        print(f"\n📈 Performance Statistics:")
        stats = await enhanced_orchestrator.get_enhanced_performance_stats()
        print(f"  Basic stats: {stats['basic_stats']}")
        print(f"  Enhanced stats: {stats['enhanced_stats']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
