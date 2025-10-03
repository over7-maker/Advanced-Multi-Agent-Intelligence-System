#!/usr/bin/env python3
"""
AMAS Enhanced Multi-Agent Orchestrator with Intelligent API Management
Comprehensive orchestrator with 16 AI provider fallback system
"""

import os
import sys
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# Import our intelligent API manager
from .ai_api_manager import (
    IntelligentAPIManager, APIProvider, TaskType, 
    generate_ai_response, get_api_manager
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Agent roles in the intelligence system"""
    OSINT_COLLECTOR = "osint_collector"
    INTELLIGENCE_ANALYST = "intelligence_analyst"
    STRATEGIC_ADVISOR = "strategic_advisor"
    CODE_SPECIALIST = "code_specialist"
    FORENSICS_EXPERT = "forensics_expert"
    DATA_ANALYST = "data_analyst"
    REPORTING_AGENT = "reporting_agent"
    COORDINATION_AGENT = "coordination_agent"

class InvestigationPhase(Enum):
    """Investigation phases"""
    INITIALIZATION = "initialization"
    OSINT_COLLECTION = "osint_collection"
    DEEP_ANALYSIS = "deep_analysis"
    TECHNICAL_ASSESSMENT = "technical_assessment"
    STRATEGIC_EVALUATION = "strategic_evaluation"
    REPORT_GENERATION = "report_generation"
    COMPLETION = "completion"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class InvestigationTask:
    """Investigation task data structure"""
    id: str
    phase: InvestigationPhase
    description: str
    assigned_agent: AgentRole
    preferred_provider: Optional[APIProvider] = None
    task_type: TaskType = TaskType.CHAT_COMPLETION
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Agent:
    """Intelligent agent with API provider preferences"""
    id: str
    role: AgentRole
    name: str
    description: str
    preferred_providers: List[APIProvider] = field(default_factory=list)
    capabilities: List[TaskType] = field(default_factory=list)
    current_task: Optional[str] = None
    status: str = "idle"
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0

class EnhancedMultiAgentOrchestrator:
    """Enhanced orchestrator with intelligent API management"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_manager = get_api_manager()
        
        # Agent management
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, InvestigationTask] = {}
        self.investigation_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.total_investigations = 0
        self.successful_investigations = 0
        self.average_investigation_time = 0.0
        
        # Initialize agents
        self._initialize_agents()
        
        # Start health monitoring
        asyncio.create_task(self._start_monitoring())
        
        logger.info("Enhanced Multi-Agent Orchestrator initialized with intelligent API management")
    
    def _initialize_agents(self):
        """Initialize the agent fleet with optimized provider preferences"""
        
        # OSINT Collector - Fast, reliable providers for data gathering
        self.agents["osint_001"] = Agent(
            id="osint_001",
            role=AgentRole.OSINT_COLLECTOR,
            name="OSINT Collector Alpha",
            description="Open source intelligence gathering and preliminary analysis",
            preferred_providers=[
                APIProvider.DEEPSEEK,     # Fast and reliable
                APIProvider.GROQAI,      # High speed processing
                APIProvider.GLM,         # Good for data analysis
                APIProvider.CEREBRAS     # High performance
            ],
            capabilities=[TaskType.CHAT_COMPLETION, TaskType.TEXT_GENERATION, TaskType.QUESTION_ANSWERING]
        )
        
        # Intelligence Analyst - Reasoning-focused providers
        self.agents["analyst_001"] = Agent(
            id="analyst_001",
            role=AgentRole.INTELLIGENCE_ANALYST,
            name="Intelligence Analyst Prime",
            description="Deep analysis, pattern recognition, and threat assessment",
            preferred_providers=[
                APIProvider.CEREBRAS,     # Excellent reasoning
                APIProvider.NVIDIA,      # Advanced reasoning models
                APIProvider.GROK,        # Strategic thinking
                APIProvider.GEMINIAI     # Advanced analysis
            ],
            capabilities=[TaskType.REASONING, TaskType.QUESTION_ANSWERING, TaskType.TEXT_GENERATION]
        )
        
        # Strategic Advisor - High-level reasoning providers
        self.agents["advisor_001"] = Agent(
            id="advisor_001",
            role=AgentRole.STRATEGIC_ADVISOR,
            name="Strategic Advisor Omega",
            description="Strategic synthesis, recommendations, and risk assessment",
            preferred_providers=[
                APIProvider.GROK,        # Strategic insights
                APIProvider.CEREBRAS,    # Advanced reasoning
                APIProvider.GEMINI2,     # Latest capabilities
                APIProvider.NVIDIA       # High-end reasoning
            ],
            capabilities=[TaskType.REASONING, TaskType.SUMMARIZATION, TaskType.QUESTION_ANSWERING]
        )
        
        # Code Specialist - Code-focused providers
        self.agents["coder_001"] = Agent(
            id="coder_001",
            role=AgentRole.CODE_SPECIALIST,
            name="Code Intelligence Specialist",
            description="Technical code analysis, vulnerability detection, and software assessment",
            preferred_providers=[
                APIProvider.CODESTRAL,   # Specialized for code
                APIProvider.QWEN,       # Code analysis
                APIProvider.NVIDIA,     # Technical reasoning
                APIProvider.DEEPSEEK    # Code understanding
            ],
            capabilities=[TaskType.CODE_ANALYSIS, TaskType.REASONING, TaskType.TEXT_GENERATION]
        )
        
        # Forensics Expert - Detailed analysis providers
        self.agents["forensics_001"] = Agent(
            id="forensics_001",
            role=AgentRole.FORENSICS_EXPERT,
            name="Digital Forensics Expert",
            description="Forensic analysis, evidence examination, and detailed investigation",
            preferred_providers=[
                APIProvider.CEREBRAS,    # Detailed analysis
                APIProvider.NVIDIA,     # Technical depth
                APIProvider.CODESTRAL,  # Technical understanding
                APIProvider.GLM         # Methodical analysis
            ],
            capabilities=[TaskType.REASONING, TaskType.TEXT_GENERATION, TaskType.QUESTION_ANSWERING]
        )
        
        # Data Analyst - Pattern recognition providers
        self.agents["data_001"] = Agent(
            id="data_001",
            role=AgentRole.DATA_ANALYST,
            name="Data Pattern Analyst",
            description="Data pattern recognition, statistical analysis, and correlation detection",
            preferred_providers=[
                APIProvider.GLM,        # Data processing
                APIProvider.QWEN,      # Pattern recognition
                APIProvider.CEREBRAS,  # Complex analysis
                APIProvider.COHERE     # Text analysis
            ],
            capabilities=[TaskType.TEXT_GENERATION, TaskType.REASONING, TaskType.SUMMARIZATION]
        )
        
        # Reporting Agent - Communication-focused providers
        self.agents["reporter_001"] = Agent(
            id="reporter_001",
            role=AgentRole.REPORTING_AGENT,
            name="Intelligence Reporter",
            description="Report generation, communication, and documentation",
            preferred_providers=[
                APIProvider.COHERE,     # Excellent text generation
                APIProvider.GLM,       # Clear communication
                APIProvider.GROQAI,    # Fast generation
                APIProvider.CHUTES     # Alternative text gen
            ],
            capabilities=[TaskType.TEXT_GENERATION, TaskType.SUMMARIZATION, TaskType.TRANSLATION]
        )
        
        # Coordination Agent - Reliable, fast providers
        self.agents["coordinator_001"] = Agent(
            id="coordinator_001",
            role=AgentRole.COORDINATION_AGENT,
            name="Investigation Coordinator",
            description="Investigation coordination, task management, and workflow optimization",
            preferred_providers=[
                APIProvider.DEEPSEEK,   # Reliable and fast
                APIProvider.GROQAI,    # Quick responses
                APIProvider.GLM,       # Good reasoning
                APIProvider.GPTOSS     # Backup option
            ],
            capabilities=[TaskType.CHAT_COMPLETION, TaskType.REASONING, TaskType.TEXT_GENERATION]
        )
        
        logger.info(f"Initialized {len(self.agents)} intelligent agents")
    
    async def conduct_investigation(self, topic: str, investigation_type: str = "comprehensive") -> Dict[str, Any]:
        """Conduct a comprehensive multi-agent investigation"""
        investigation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"🚀 Starting investigation: {topic}")
        logger.info(f"📋 Investigation ID: {investigation_id}")
        
        investigation_result = {
            'id': investigation_id,
            'topic': topic,
            'type': investigation_type,
            'started_at': start_time.isoformat(),
            'phases': [],
            'agents_used': [],
            'api_usage': {},
            'performance_metrics': {},
            'final_report': None,
            'status': 'in_progress'
        }
        
        try:
            # Phase 1: Initialization and Planning
            await self._execute_phase(
                investigation_result, 
                InvestigationPhase.INITIALIZATION,
                "coordinator_001",
                f"Initialize comprehensive investigation on: {topic}. Create investigation plan, identify key areas to explore, and set priorities.",
                TaskType.REASONING
            )
            
            # Phase 2: OSINT Collection
            await self._execute_phase(
                investigation_result,
                InvestigationPhase.OSINT_COLLECTION,
                "osint_001",
                f"Conduct comprehensive OSINT collection on: {topic}. Gather information from public sources, social media, news, technical reports, and identify key indicators.",
                TaskType.QUESTION_ANSWERING
            )
            
            # Phase 3: Deep Analysis
            await self._execute_phase(
                investigation_result,
                InvestigationPhase.DEEP_ANALYSIS,
                "analyst_001",
                f"Perform deep intelligence analysis on: {topic}. Analyze patterns, identify threats, assess TTPs, and evaluate risks based on collected data.",
                TaskType.REASONING
            )
            
            # Phase 4: Technical Assessment (if relevant)
            if any(keyword in topic.lower() for keyword in ['code', 'software', 'vulnerability', 'security', 'malware', 'exploit']):
                await self._execute_phase(
                    investigation_result,
                    InvestigationPhase.TECHNICAL_ASSESSMENT,
                    "coder_001",
                    f"Perform technical code and security analysis for: {topic}. Identify vulnerabilities, assess technical risks, and provide technical recommendations.",
                    TaskType.CODE_ANALYSIS
                )
            
            # Phase 5: Strategic Evaluation
            await self._execute_phase(
                investigation_result,
                InvestigationPhase.STRATEGIC_EVALUATION,
                "advisor_001",
                f"Provide strategic assessment and recommendations for: {topic}. Synthesize findings, assess overall impact, and recommend actionable strategies.",
                TaskType.REASONING
            )
            
            # Phase 6: Report Generation
            await self._execute_phase(
                investigation_result,
                InvestigationPhase.REPORT_GENERATION,
                "reporter_001",
                f"Generate comprehensive investigation report for: {topic}. Compile all findings into executive summary, detailed analysis, and actionable recommendations.",
                TaskType.SUMMARIZATION
            )
            
            # Phase 7: Completion
            investigation_result['completed_at'] = datetime.now().isoformat()
            investigation_result['status'] = 'completed'
            investigation_result['duration'] = (datetime.now() - start_time).total_seconds()
            
            # Generate performance metrics
            investigation_result['performance_metrics'] = await self._generate_performance_metrics(investigation_result)
            
            # Update statistics
            self.total_investigations += 1
            self.successful_investigations += 1
            
            logger.info(f"✅ Investigation completed successfully in {investigation_result['duration']:.2f} seconds")
            
            # Save investigation
            self.investigation_history.append(investigation_result)
            
            return investigation_result
            
        except Exception as e:
            investigation_result['status'] = 'failed'
            investigation_result['error'] = str(e)
            investigation_result['completed_at'] = datetime.now().isoformat()
            
            logger.error(f"❌ Investigation failed: {e}")
            return investigation_result
    
    async def _execute_phase(
        self,
        investigation: Dict[str, Any],
        phase: InvestigationPhase,
        agent_id: str,
        prompt: str,
        task_type: TaskType
    ):
        """Execute a single investigation phase"""
        
        task_id = str(uuid.uuid4())
        agent = self.agents[agent_id]
        
        # Create task
        task = InvestigationTask(
            id=task_id,
            phase=phase,
            description=prompt,
            assigned_agent=agent.role,
            task_type=task_type,
            status=TaskStatus.IN_PROGRESS
        )
        
        # Add context from previous phases
        context = self._build_context(investigation)
        if context:
            enhanced_prompt = f"Context from previous analysis:\n{context}\n\nTask: {prompt}"
        else:
            enhanced_prompt = prompt
        
        self.tasks[task_id] = task
        agent.current_task = task_id
        agent.status = "busy"
        task.started_at = datetime.now()
        
        logger.info(f"🤖 Executing {phase.value} with {agent.name}")
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": f"You are {agent.name}, a {agent.description}. Provide detailed, actionable intelligence analysis."
                },
                {
                    "role": "user", 
                    "content": enhanced_prompt
                }
            ]
            
            # Execute with preferred providers
            response = await generate_ai_response(
                messages=messages,
                task_type=task_type,
                preferred_provider=agent.preferred_providers[0] if agent.preferred_providers else None,
                max_tokens=4000,
                temperature=0.7
            )
            
            # Record success
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = response
            
            agent.total_tasks += 1
            agent.successful_tasks += 1
            agent.status = "idle"
            agent.current_task = None
            
            # Update investigation
            phase_result = {
                'phase': phase.value,
                'agent': agent.name,
                'task_id': task_id,
                'started_at': task.started_at.isoformat(),
                'completed_at': task.completed_at.isoformat(),
                'duration': (task.completed_at - task.started_at).total_seconds(),
                'response': response['content'],
                'provider_used': response['provider'],
                'model_used': response['model'],
                'response_time': response['response_time'],
                'fallback_attempts': response.get('fallback_attempts', 1)
            }
            
            investigation['phases'].append(phase_result)
            
            # Track agent usage
            if agent.role.value not in investigation['agents_used']:
                investigation['agents_used'].append(agent.role.value)
            
            # Track API usage
            provider = response['provider']
            if provider not in investigation['api_usage']:
                investigation['api_usage'][provider] = 0
            investigation['api_usage'][provider] += 1
            
            logger.info(f"✅ {phase.value} completed using {provider} in {response['response_time']:.2f}s")
            
        except Exception as e:
            # Record failure
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            agent.total_tasks += 1
            agent.failed_tasks += 1
            agent.status = "idle"
            agent.current_task = None
            
            logger.error(f"❌ {phase.value} failed: {e}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                logger.info(f"🔄 Retrying {phase.value} (attempt {task.retry_count + 1})")
                await asyncio.sleep(2)  # Brief delay before retry
                await self._execute_phase(investigation, phase, agent_id, prompt, task_type)
            else:
                raise Exception(f"Phase {phase.value} failed after {task.max_retries} retries: {e}")
    
    def _build_context(self, investigation: Dict[str, Any]) -> str:
        """Build context from previous phases"""
        context_parts = []
        
        for phase_result in investigation['phases']:
            if phase_result.get('response'):
                context_parts.append(f"{phase_result['phase']}: {phase_result['response'][:500]}...")
        
        return "\n\n".join(context_parts)
    
    async def _generate_performance_metrics(self, investigation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance metrics"""
        
        # Calculate phase durations
        phase_durations = {phase['phase']: phase['duration'] for phase in investigation['phases']}
        
        # Calculate API performance
        api_stats = {}
        for phase in investigation['phases']:
            provider = phase.get('provider_used')
            if provider:
                if provider not in api_stats:
                    api_stats[provider] = {
                        'usage_count': 0,
                        'total_response_time': 0,
                        'fallback_attempts': 0
                    }
                api_stats[provider]['usage_count'] += 1
                api_stats[provider]['total_response_time'] += phase.get('response_time', 0)
                api_stats[provider]['fallback_attempts'] += phase.get('fallback_attempts', 1) - 1
        
        # Calculate average response times
        for provider_stats in api_stats.values():
            if provider_stats['usage_count'] > 0:
                provider_stats['average_response_time'] = provider_stats['total_response_time'] / provider_stats['usage_count']
        
        # Agent performance
        agent_performance = {}
        for agent_id, agent in self.agents.items():
            if agent.total_tasks > 0:
                agent_performance[agent_id] = {
                    'success_rate': (agent.successful_tasks / agent.total_tasks) * 100,
                    'total_tasks': agent.total_tasks,
                    'successful_tasks': agent.successful_tasks,
                    'failed_tasks': agent.failed_tasks
                }
        
        return {
            'total_duration': investigation.get('duration', 0),
            'phase_durations': phase_durations,
            'api_performance': api_stats,
            'agent_performance': agent_performance,
            'total_phases': len(investigation['phases']),
            'successful_phases': len([p for p in investigation['phases'] if 'response' in p]),
            'unique_providers_used': len(set(p.get('provider_used') for p in investigation['phases'] if p.get('provider_used')))
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Get API manager statistics
        api_stats = self.api_manager.get_provider_statistics()
        
        # Agent statistics
        agent_stats = {}
        for agent_id, agent in self.agents.items():
            agent_stats[agent_id] = {
                'name': agent.name,
                'role': agent.role.value,
                'status': agent.status,
                'current_task': agent.current_task,
                'total_tasks': agent.total_tasks,
                'successful_tasks': agent.successful_tasks,
                'failed_tasks': agent.failed_tasks,
                'success_rate': (agent.successful_tasks / agent.total_tasks * 100) if agent.total_tasks > 0 else 0,
                'preferred_providers': [p.value for p in agent.preferred_providers]
            }
        
        # Investigation statistics
        investigation_stats = {
            'total_investigations': self.total_investigations,
            'successful_investigations': self.successful_investigations,
            'success_rate': (self.successful_investigations / self.total_investigations * 100) if self.total_investigations > 0 else 0,
            'average_duration': self.average_investigation_time
        }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'api_manager': api_stats,
            'agents': agent_stats,
            'investigations': investigation_stats,
            'active_tasks': len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            'system_health': 'healthy' if api_stats['overview']['healthy_providers'] > 0 else 'degraded'
        }
    
    async def _start_monitoring(self):
        """Start background monitoring tasks"""
        
        async def health_monitor():
            """Monitor system health"""
            while True:
                try:
                    await self.api_manager.health_check_all_providers()
                    await asyncio.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)
        
        async def performance_optimizer():
            """Optimize performance based on metrics"""
            while True:
                try:
                    await self.api_manager.optimize_provider_usage()
                    await asyncio.sleep(600)  # Optimize every 10 minutes
                except Exception as e:
                    logger.error(f"Performance optimization error: {e}")
                    await asyncio.sleep(120)
        
        # Start monitoring tasks
        asyncio.create_task(health_monitor())
        asyncio.create_task(performance_optimizer())
        
        logger.info("Background monitoring started")
    
    async def generate_comprehensive_report(self, investigation: Dict[str, Any]) -> str:
        """Generate a comprehensive investigation report"""
        
        report_sections = []
        
        # Header
        report_sections.extend([
            "# 🔍 AMAS Enhanced Intelligence Investigation Report",
            "",
            f"**Investigation Topic:** {investigation['topic']}",
            f"**Investigation ID:** {investigation['id']}",
            f"**Type:** {investigation['type']}",
            f"**Started:** {investigation['started_at']}",
            f"**Completed:** {investigation.get('completed_at', 'In Progress')}",
            f"**Duration:** {investigation.get('duration', 0):.2f} seconds",
            f"**Status:** {investigation['status'].upper()}",
            "",
            "---",
            ""
        ])
        
        # Executive Summary
        if investigation['phases']:
            last_phase = investigation['phases'][-1]
            if 'response' in last_phase:
                report_sections.extend([
                    "## 📊 Executive Summary",
                    "",
                    last_phase['response'][:1000] + "..." if len(last_phase['response']) > 1000 else last_phase['response'],
                    "",
                    "---",
                    ""
                ])
        
        # Detailed Phase Analysis
        report_sections.extend([
            "## 🔍 Detailed Phase Analysis",
            ""
        ])
        
        for phase in investigation['phases']:
            report_sections.extend([
                f"### {phase['phase'].replace('_', ' ').title()}",
                f"**Agent:** {phase['agent']}",
                f"**Duration:** {phase['duration']:.2f} seconds",
                f"**Provider:** {phase.get('provider_used', 'Unknown')}",
                f"**Model:** {phase.get('model_used', 'Unknown')}",
                f"**Response Time:** {phase.get('response_time', 0):.2f} seconds",
                "",
                "#### Analysis:",
                phase.get('response', 'No response available'),
                "",
                "---",
                ""
            ])
        
        # Performance Metrics
        if 'performance_metrics' in investigation:
            metrics = investigation['performance_metrics']
            report_sections.extend([
                "## 📈 Performance Metrics",
                "",
                f"**Total Duration:** {metrics.get('total_duration', 0):.2f} seconds",
                f"**Total Phases:** {metrics.get('total_phases', 0)}",
                f"**Successful Phases:** {metrics.get('successful_phases', 0)}",
                f"**Unique Providers Used:** {metrics.get('unique_providers_used', 0)}",
                "",
                "### API Performance:",
                ""
            ])
            
            for provider, stats in metrics.get('api_performance', {}).items():
                report_sections.append(f"- **{provider}**: {stats['usage_count']} requests, avg {stats.get('average_response_time', 0):.2f}s")
            
            report_sections.extend(["", "---", ""])
        
        # API Usage Summary
        report_sections.extend([
            "## 🤖 API Usage Summary",
            "",
            f"**Total API Calls:** {sum(investigation.get('api_usage', {}).values())}",
            f"**Agents Used:** {', '.join(investigation.get('agents_used', []))}",
            "",
            "### Provider Usage:"
        ])
        
        for provider, count in investigation.get('api_usage', {}).items():
            report_sections.append(f"- **{provider}**: {count} requests")
        
        report_sections.extend([
            "",
            "---",
            "",
            "## 🎯 Recommendations",
            "",
            "Based on this investigation, we recommend:",
            "1. Continuous monitoring of identified indicators",
            "2. Implementation of recommended security measures",
            "3. Regular reassessment of threat landscape",
            "4. Stakeholder briefings on findings",
            "",
            "---",
            "",
            f"*Report generated by AMAS Enhanced Multi-Agent Intelligence System*",
            f"*Timestamp: {datetime.now().isoformat()}*",
            f"*API Providers Available: {len(self.api_manager.endpoints)}*"
        ])
        
        return "\n".join(report_sections)

# Global instance
_orchestrator = None

def get_orchestrator() -> EnhancedMultiAgentOrchestrator:
    """Get the global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EnhancedMultiAgentOrchestrator()
    return _orchestrator

async def conduct_ai_investigation(topic: str, investigation_type: str = "comprehensive") -> Dict[str, Any]:
    """Convenience function to conduct an investigation"""
    orchestrator = get_orchestrator()
    return await orchestrator.conduct_investigation(topic, investigation_type)

if __name__ == "__main__":
    async def test_orchestrator():
        """Test the enhanced orchestrator"""
        orchestrator = EnhancedMultiAgentOrchestrator()
        
        # Get system status
        status = await orchestrator.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
        
        # Conduct test investigation
        try:
            investigation = await orchestrator.conduct_investigation(
                "Recent cybersecurity threats targeting software supply chains",
                "comprehensive"
            )
            
            # Generate report
            report = await orchestrator.generate_comprehensive_report(investigation)
            
            # Save outputs
            os.makedirs('artifacts', exist_ok=True)
            
            with open('artifacts/enhanced_investigation_report.md', 'w') as f:
                f.write(report)
            
            with open('artifacts/enhanced_investigation_data.json', 'w') as f:
                json.dump(investigation, f, indent=2)
            
            print("✅ Test investigation completed successfully!")
            print(f"📄 Report saved to artifacts/enhanced_investigation_report.md")
            
        except Exception as e:
            print(f"❌ Test investigation failed: {e}")
    
    asyncio.run(test_orchestrator())