"""
AMAS CrewAI Integration - Enhanced Team-Based Agent Collaboration

Advanced multi-agent team collaboration using CrewAI framework:
- Role-based agent specialization
- Hierarchical task delegation
- Collaborative problem-solving
- Team coordination and communication
- Performance optimization and monitoring

Implements the "AI Team" metaphor from the Advanced Multi-Agent Intelligence System Blueprint.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import json
import uuid

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    # Fallback if CrewAI not available
    CREWAI_AVAILABLE = False
    Agent = Task = Crew = Process = BaseTool = None
    logger.warning("CrewAI not available, using fallback implementation")

from agents.base.intelligence_agent import IntelligenceAgent
from tools.amas_tools import AMASToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class CrewMember:
    """Enhanced crew member with AMAS integration"""
    agent_id: str
    crewai_agent: Any  # CrewAI Agent instance
    amas_agent: IntelligenceAgent
    role: str
    specialization: str
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    collaboration_history: List[str] = field(default_factory=list)
    team_relationships: Dict[str, float] = field(default_factory=dict)  # Trust scores with other agents


@dataclass
class CrewMission:
    """Mission definition for crew execution"""
    mission_id: str
    name: str
    description: str
    objectives: List[str]
    crew_composition: List[str]  # Required agent roles
    expected_deliverables: List[str]
    success_criteria: Dict[str, Any]
    priority: int = 2
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)


class AMASIntelligenceCrew:
    """
    Advanced intelligence crew using CrewAI framework.
    
    Implements sophisticated team-based collaboration with:
    - Specialized intelligence roles
    - Hierarchical coordination
    - Dynamic team formation
    - Performance monitoring
    - Learning and adaptation
    """
    
    def __init__(self, config: Dict[str, Any], amas_system=None):
        self.config = config
        self.amas_system = amas_system
        
        # Crew management
        self.crew_members: Dict[str, CrewMember] = {}
        self.active_crews: Dict[str, Any] = {}  # CrewAI Crew instances
        self.mission_history: List[CrewMission] = []
        
        # Performance tracking
        self.crew_metrics = {
            'total_missions': 0,
            'successful_missions': 0,
            'failed_missions': 0,
            'average_mission_time': 0.0,
            'team_effectiveness': 0.0,
            'collaboration_quality': 0.0
        }
        
        # Tool registry
        self.tool_registry = AMASToolRegistry()
        
        # Role definitions based on blueprint
        self.role_definitions = self._initialize_role_definitions()
        
        # Initialize crew if CrewAI is available
        if CREWAI_AVAILABLE:
            self._initialize_crew_members()
        else:
            logger.warning("CrewAI not available, using fallback crew implementation")
        
        logger.info("AMAS Intelligence Crew initialized")
    
    def _initialize_role_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize role definitions based on the blueprint matrix"""
        return {
            'orchestrator': {
                'role': 'Intelligence Operations Manager',
                'goal': 'Coordinate and optimize intelligence operations across the team',
                'backstory': 'You are a master intelligence operations manager with extensive experience in coordinating complex multi-source intelligence operations. You excel at breaking down complex objectives into actionable tasks and ensuring seamless team coordination.',
                'capabilities': ['task_planning', 'agent_routing', 'state_management'],
                'cognitive_bias': 'deliberate',
                'tools': ['task_delegator', 'progress_monitor', 'resource_allocator']
            },
            'planner': {
                'role': 'Strategic Intelligence Planner',
                'goal': 'Transform high-level intelligence objectives into detailed, executable action plans',
                'backstory': 'You are a strategic intelligence planner with deep expertise in operational planning and risk assessment. You excel at creating precise, ordered action sequences that maximize intelligence collection effectiveness while minimizing operational risks.',
                'capabilities': ['sequential_logic', 'dependency_analysis', 'risk_assessment'],
                'cognitive_bias': 'analytical',
                'tools': ['planning_framework', 'dependency_analyzer', 'risk_calculator']
            },
            'researcher': {
                'role': 'Intelligence Research Specialist',
                'goal': 'Gather, filter, and synthesize intelligence from diverse external sources',
                'backstory': 'You are an expert intelligence researcher with mastery of open-source intelligence collection, database analysis, and information synthesis. You have an intuitive ability to identify relevant information and connect disparate data points.',
                'capabilities': ['web_search', 'database_querying', 'document_analysis'],
                'cognitive_bias': 'exploratory',
                'tools': ['web_search', 'database_connector', 'document_analyzer', 'source_validator']
            },
            'analyst': {
                'role': 'Intelligence Data Analyst',
                'goal': 'Perform deep analysis, correlation, and pattern recognition on collected intelligence',
                'backstory': 'You are a senior intelligence analyst with expertise in data correlation, pattern recognition, and threat assessment. You excel at finding hidden connections and generating actionable insights from complex datasets.',
                'capabilities': ['data_analysis', 'pattern_recognition', 'correlation_analysis'],
                'cognitive_bias': 'logical',
                'tools': ['data_analyzer', 'pattern_detector', 'correlation_engine', 'threat_assessor']
            },
            'critic': {
                'role': 'Intelligence Quality Validator',
                'goal': 'Critically evaluate intelligence outputs for accuracy, completeness, and reliability',
                'backstory': 'You are a meticulous intelligence quality specialist with a keen eye for inconsistencies, gaps, and potential errors. You serve as the final quality gate, ensuring all intelligence products meet the highest standards.',
                'capabilities': ['fact_checking', 'logical_consistency', 'quality_scoring'],
                'cognitive_bias': 'skeptical',
                'tools': ['fact_checker', 'consistency_analyzer', 'quality_scorer', 'source_verifier']
            },
            'writer': {
                'role': 'Intelligence Report Writer',
                'goal': 'Synthesize all intelligence findings into clear, actionable reports',
                'backstory': 'You are an expert intelligence writer with the ability to transform complex analytical findings into clear, compelling, and actionable intelligence reports. You excel at tailoring communication style to different audiences while maintaining analytical rigor.',
                'capabilities': ['report_writing', 'summarization', 'communication'],
                'cognitive_bias': 'creative',
                'tools': ['report_generator', 'summarizer', 'formatter', 'visualizer']
            }
        }
    
    def _initialize_crew_members(self):
        """Initialize CrewAI crew members based on role definitions"""
        try:
            if not CREWAI_AVAILABLE:
                return
            
            for role_id, role_def in self.role_definitions.items():
                # Create CrewAI agent
                crewai_agent = Agent(
                    role=role_def['role'],
                    goal=role_def['goal'],
                    backstory=role_def['backstory'],
                    tools=self._get_tools_for_role(role_id),
                    verbose=True,
                    allow_delegation=True,
                    max_iter=5
                )
                
                # Find corresponding AMAS agent
                amas_agent = self._find_amas_agent_for_role(role_id)
                
                # Create crew member
                crew_member = CrewMember(
                    agent_id=f"crew_{role_id}",
                    crewai_agent=crewai_agent,
                    amas_agent=amas_agent,
                    role=role_def['role'],
                    specialization=role_id
                )
                
                self.crew_members[role_id] = crew_member
                
                logger.info(f"Crew member initialized: {role_id} ({role_def['role']})")
            
        except Exception as e:
            logger.error(f"Error initializing crew members: {e}")
    
    def _get_tools_for_role(self, role_id: str) -> List[Any]:
        """Get tools for a specific role"""
        try:
            role_tools = self.role_definitions[role_id].get('tools', [])
            tools = []
            
            for tool_name in role_tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    tools.append(tool)
            
            return tools
            
        except Exception as e:
            logger.error(f"Error getting tools for role {role_id}: {e}")
            return []
    
    def _find_amas_agent_for_role(self, role_id: str) -> Optional[IntelligenceAgent]:
        """Find corresponding AMAS agent for a crew role"""
        try:
            if not self.amas_system or not self.amas_system.agents:
                return None
            
            # Role mapping to AMAS agent types
            role_mapping = {
                'orchestrator': 'orchestrator',
                'planner': 'investigation',
                'researcher': 'osint',
                'analyst': 'data_analysis',
                'critic': 'investigation',
                'writer': 'reporting'
            }
            
            agent_type = role_mapping.get(role_id)
            if not agent_type:
                return None
            
            # Find agent with matching capabilities
            for agent_id, agent in self.amas_system.agents.items():
                if agent_type in agent.capabilities or any(
                    agent_type in cap.lower() for cap in agent.capabilities
                ):
                    return agent
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding AMAS agent for role {role_id}: {e}")
            return None
    
    async def create_intelligence_crew(
        self,
        mission: CrewMission,
        crew_composition: Optional[List[str]] = None
    ) -> str:
        """
        Create a specialized intelligence crew for a mission.
        
        Args:
            mission: Mission definition
            crew_composition: Optional specific crew composition
            
        Returns:
            Crew ID
        """
        try:
            if not CREWAI_AVAILABLE:
                return await self._create_fallback_crew(mission, crew_composition)
            
            crew_id = str(uuid.uuid4())
            
            # Determine crew composition
            if not crew_composition:
                crew_composition = await self._determine_optimal_crew_composition(mission)
            
            # Create CrewAI agents for the mission
            crew_agents = []
            crew_tasks = []
            
            for role_id in crew_composition:
                if role_id not in self.crew_members:
                    logger.warning(f"Role {role_id} not available for crew")
                    continue
                
                crew_member = self.crew_members[role_id]
                crew_agents.append(crew_member.crewai_agent)
                
                # Create tasks for each agent based on mission objectives
                agent_tasks = await self._create_tasks_for_agent(mission, role_id)
                crew_tasks.extend(agent_tasks)
            
            # Create CrewAI crew
            crew = Crew(
                agents=crew_agents,
                tasks=crew_tasks,
                process=Process.sequential,  # Can be changed to hierarchical
                verbose=True,
                memory=True
            )
            
            self.active_crews[crew_id] = {
                'crew': crew,
                'mission': mission,
                'composition': crew_composition,
                'created_at': datetime.utcnow(),
                'status': 'created'
            }
            
            logger.info(f"Intelligence crew created: {crew_id} for mission {mission.name}")
            
            return crew_id
            
        except Exception as e:
            logger.error(f"Error creating intelligence crew: {e}")
            raise
    
    async def _determine_optimal_crew_composition(
        self,
        mission: CrewMission
    ) -> List[str]:
        """Determine optimal crew composition for a mission"""
        try:
            # Analyze mission requirements
            mission_text = f"{mission.description} {' '.join(mission.objectives)}".lower()
            
            # Base crew always includes orchestrator
            crew_composition = ['orchestrator']
            
            # Add roles based on mission requirements
            if any(keyword in mission_text for keyword in ['collect', 'gather', 'osint', 'research']):
                crew_composition.append('researcher')
            
            if any(keyword in mission_text for keyword in ['analyze', 'correlation', 'pattern', 'assessment']):
                crew_composition.append('analyst')
            
            if any(keyword in mission_text for keyword in ['plan', 'strategy', 'approach', 'methodology']):
                crew_composition.append('planner')
            
            if any(keyword in mission_text for keyword in ['validate', 'verify', 'check', 'quality']):
                crew_composition.append('critic')
            
            if any(keyword in mission_text for keyword in ['report', 'summary', 'document', 'brief']):
                crew_composition.append('writer')
            
            # Ensure minimum viable crew
            if len(crew_composition) < 3:
                # Add essential roles
                if 'researcher' not in crew_composition:
                    crew_composition.append('researcher')
                if 'analyst' not in crew_composition:
                    crew_composition.append('analyst')
                if 'writer' not in crew_composition:
                    crew_composition.append('writer')
            
            return crew_composition
            
        except Exception as e:
            logger.error(f"Error determining crew composition: {e}")
            return ['orchestrator', 'researcher', 'analyst', 'writer']  # Default crew
    
    async def _create_tasks_for_agent(
        self,
        mission: CrewMission,
        role_id: str
    ) -> List[Any]:
        """Create CrewAI tasks for a specific agent role"""
        try:
            if not CREWAI_AVAILABLE:
                return []
            
            role_def = self.role_definitions[role_id]
            tasks = []
            
            # Create role-specific tasks based on mission objectives
            if role_id == 'orchestrator':
                task = Task(
                    description=f"Coordinate the intelligence mission: {mission.description}. "
                              f"Ensure all team members understand their roles and objectives. "
                              f"Monitor progress and optimize team performance.",
                    agent=self.crew_members[role_id].crewai_agent,
                    expected_output="Mission coordination plan and team assignments"
                )
                tasks.append(task)
                
            elif role_id == 'planner':
                task = Task(
                    description=f"Create a detailed operational plan for: {mission.description}. "
                              f"Break down objectives into specific, actionable steps. "
                              f"Identify dependencies, risks, and resource requirements.",
                    agent=self.crew_members[role_id].crewai_agent,
                    expected_output="Detailed operational plan with step-by-step procedures"
                )
                tasks.append(task)
                
            elif role_id == 'researcher':
                for i, objective in enumerate(mission.objectives):
                    task = Task(
                        description=f"Research and collect intelligence for objective: {objective}. "
                                  f"Use multiple sources and validate information quality. "
                                  f"Focus on accuracy and completeness.",
                        agent=self.crew_members[role_id].crewai_agent,
                        expected_output=f"Comprehensive research findings for objective {i+1}"
                    )
                    tasks.append(task)
                    
            elif role_id == 'analyst':
                task = Task(
                    description=f"Analyze all collected intelligence for mission: {mission.description}. "
                              f"Identify patterns, correlations, and insights. "
                              f"Assess threats, opportunities, and implications.",
                    agent=self.crew_members[role_id].crewai_agent,
                    expected_output="Analytical assessment with findings and recommendations"
                )
                tasks.append(task)
                
            elif role_id == 'critic':
                task = Task(
                    description=f"Review and validate all intelligence products for mission: {mission.description}. "
                              f"Check for accuracy, consistency, and completeness. "
                              f"Identify any gaps or potential errors.",
                    agent=self.crew_members[role_id].crewai_agent,
                    expected_output="Quality assessment report with validation results"
                )
                tasks.append(task)
                
            elif role_id == 'writer':
                task = Task(
                    description=f"Synthesize all intelligence findings into a comprehensive report for: {mission.description}. "
                              f"Create clear, actionable intelligence products. "
                              f"Tailor content for intended audience and use case.",
                    agent=self.crew_members[role_id].crewai_agent,
                    expected_output="Professional intelligence report with executive summary"
                )
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error creating tasks for agent {role_id}: {e}")
            return []
    
    async def execute_intelligence_mission(
        self,
        mission: CrewMission,
        crew_composition: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute an intelligence mission using crew-based collaboration.
        
        Args:
            mission: Mission to execute
            crew_composition: Optional specific crew composition
            
        Returns:
            Mission execution results
        """
        try:
            start_time = time.time()
            
            # Create crew for mission
            crew_id = await self.create_intelligence_crew(mission, crew_composition)
            
            if not CREWAI_AVAILABLE:
                return await self._execute_fallback_mission(mission, crew_id)
            
            # Get crew
            crew_info = self.active_crews[crew_id]
            crew = crew_info['crew']
            
            # Update crew status
            crew_info['status'] = 'executing'
            crew_info['started_at'] = datetime.utcnow()
            
            # Execute mission using CrewAI
            logger.info(f"Executing intelligence mission: {mission.name} with crew {crew_id}")
            
            # CrewAI execution
            try:
                crew_result = await asyncio.get_event_loop().run_in_executor(
                    None, crew.kickoff
                )
                
                execution_time = time.time() - start_time
                
                # Process crew results
                mission_result = {
                    'mission_id': mission.mission_id,
                    'crew_id': crew_id,
                    'status': 'completed',
                    'execution_time': execution_time,
                    'crew_result': crew_result,
                    'team_composition': crew_info['composition'],
                    'completed_at': datetime.utcnow().isoformat(),
                    'performance_metrics': await self._calculate_mission_performance(
                        mission, crew_info, execution_time
                    )
                }
                
                # Update crew status
                crew_info['status'] = 'completed'
                crew_info['completed_at'] = datetime.utcnow()
                crew_info['result'] = mission_result
                
                # Update metrics
                await self._update_crew_metrics(mission_result, True)
                
                # Store in mission history
                self.mission_history.append(mission)
                
                logger.info(f"Intelligence mission completed: {mission.name} in {execution_time:.2f}s")
                
                return mission_result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                mission_result = {
                    'mission_id': mission.mission_id,
                    'crew_id': crew_id,
                    'status': 'failed',
                    'execution_time': execution_time,
                    'error': str(e),
                    'team_composition': crew_info['composition'],
                    'failed_at': datetime.utcnow().isoformat()
                }
                
                crew_info['status'] = 'failed'
                crew_info['error'] = str(e)
                
                await self._update_crew_metrics(mission_result, False)
                
                logger.error(f"Intelligence mission failed: {mission.name} - {e}")
                
                return mission_result
            
        except Exception as e:
            logger.error(f"Error executing intelligence mission: {e}")
            return {
                'mission_id': mission.mission_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def _create_fallback_crew(
        self,
        mission: CrewMission,
        crew_composition: Optional[List[str]]
    ) -> str:
        """Create fallback crew when CrewAI is not available"""
        try:
            crew_id = str(uuid.uuid4())
            
            if not crew_composition:
                crew_composition = await self._determine_optimal_crew_composition(mission)
            
            # Create fallback crew structure
            fallback_crew = {
                'crew_id': crew_id,
                'mission': mission,
                'composition': crew_composition,
                'created_at': datetime.utcnow(),
                'status': 'created',
                'type': 'fallback'
            }
            
            self.active_crews[crew_id] = fallback_crew
            
            logger.info(f"Fallback crew created: {crew_id}")
            
            return crew_id
            
        except Exception as e:
            logger.error(f"Error creating fallback crew: {e}")
            raise
    
    async def _execute_fallback_mission(
        self,
        mission: CrewMission,
        crew_id: str
    ) -> Dict[str, Any]:
        """Execute mission using fallback implementation"""
        try:
            start_time = time.time()
            
            crew_info = self.active_crews[crew_id]
            crew_info['status'] = 'executing'
            crew_info['started_at'] = datetime.utcnow()
            
            # Sequential execution of objectives using AMAS agents
            results = {}
            
            for i, objective in enumerate(mission.objectives):
                # Find suitable agent for objective
                agent = await self._find_agent_for_objective(objective)
                
                if agent:
                    task_data = {
                        'id': f"{mission.mission_id}_obj_{i}",
                        'type': 'mission_objective',
                        'description': objective,
                        'parameters': {
                            **mission.context,
                            'mission_id': mission.mission_id,
                            'objective_index': i
                        }
                    }
                    
                    result = await agent.process_task(task_data)
                    results[f'objective_{i}'] = result
                else:
                    results[f'objective_{i}'] = {
                        'success': False,
                        'error': 'No suitable agent found'
                    }
            
            execution_time = time.time() - start_time
            
            # Determine overall success
            successful_objectives = sum(1 for r in results.values() if r.get('success', False))
            overall_success = successful_objectives >= len(mission.objectives) * 0.7  # 70% success threshold
            
            mission_result = {
                'mission_id': mission.mission_id,
                'crew_id': crew_id,
                'status': 'completed' if overall_success else 'partial_failure',
                'execution_time': execution_time,
                'objective_results': results,
                'success_rate': successful_objectives / len(mission.objectives),
                'team_composition': crew_info['composition'],
                'completed_at': datetime.utcnow().isoformat(),
                'execution_type': 'fallback'
            }
            
            crew_info['status'] = 'completed'
            crew_info['result'] = mission_result
            
            await self._update_crew_metrics(mission_result, overall_success)
            
            return mission_result
            
        except Exception as e:
            logger.error(f"Error executing fallback mission: {e}")
            return {
                'mission_id': mission.mission_id,
                'crew_id': crew_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def _find_agent_for_objective(self, objective: str) -> Optional[IntelligenceAgent]:
        """Find the best AMAS agent for a specific objective"""
        try:
            if not self.amas_system or not self.amas_system.agents:
                return None
            
            objective_lower = objective.lower()
            
            # Simple keyword-based agent selection
            if any(keyword in objective_lower for keyword in ['collect', 'gather', 'osint', 'research']):
                # Find OSINT agent
                for agent in self.amas_system.agents.values():
                    if 'osint' in agent.capabilities:
                        return agent
            
            elif any(keyword in objective_lower for keyword in ['analyze', 'correlate', 'assess', 'evaluate']):
                # Find analysis agent
                for agent in self.amas_system.agents.values():
                    if 'data_analysis' in agent.capabilities or 'analysis' in agent.capabilities:
                        return agent
            
            elif any(keyword in objective_lower for keyword in ['investigate', 'examine', 'probe']):
                # Find investigation agent
                for agent in self.amas_system.agents.values():
                    if 'investigation' in agent.capabilities:
                        return agent
            
            elif any(keyword in objective_lower for keyword in ['report', 'document', 'summarize', 'write']):
                # Find reporting agent
                for agent in self.amas_system.agents.values():
                    if 'reporting' in agent.capabilities:
                        return agent
            
            # Default to first available agent
            return next(iter(self.amas_system.agents.values()), None)
            
        except Exception as e:
            logger.error(f"Error finding agent for objective: {e}")
            return None
    
    async def _calculate_mission_performance(
        self,
        mission: CrewMission,
        crew_info: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics for mission execution"""
        try:
            performance = {
                'execution_time': execution_time,
                'team_size': len(crew_info['composition']),
                'objectives_count': len(mission.objectives),
                'efficiency_score': 0.0,
                'collaboration_score': 0.0,
                'quality_score': 0.0
            }
            
            # Calculate efficiency score (based on execution time vs expected)
            expected_time = len(mission.objectives) * 300  # 5 minutes per objective baseline
            if execution_time > 0:
                performance['efficiency_score'] = min(1.0, expected_time / execution_time)
            
            # Calculate collaboration score (simplified)
            team_size = len(crew_info['composition'])
            if team_size > 1:
                performance['collaboration_score'] = min(1.0, team_size / 6.0)  # Optimal team size is 6
            
            # Calculate quality score (would integrate with actual results in full implementation)
            performance['quality_score'] = 0.8  # Mock quality score
            
            return performance
            
        except Exception as e:
            logger.error(f"Error calculating mission performance: {e}")
            return {}
    
    async def _update_crew_metrics(
        self,
        mission_result: Dict[str, Any],
        success: bool
    ):
        """Update crew performance metrics"""
        try:
            self.crew_metrics['total_missions'] += 1
            
            if success:
                self.crew_metrics['successful_missions'] += 1
            else:
                self.crew_metrics['failed_missions'] += 1
            
            # Update average mission time
            execution_time = mission_result.get('execution_time', 0.0)
            if execution_time > 0:
                current_avg = self.crew_metrics['average_mission_time']
                total_missions = self.crew_metrics['total_missions']
                self.crew_metrics['average_mission_time'] = (
                    (current_avg * (total_missions - 1) + execution_time) / total_missions
                )
            
            # Update team effectiveness
            if self.crew_metrics['total_missions'] > 0:
                self.crew_metrics['team_effectiveness'] = (
                    self.crew_metrics['successful_missions'] / self.crew_metrics['total_missions']
                )
            
            # Update collaboration quality (simplified)
            performance_metrics = mission_result.get('performance_metrics', {})
            collaboration_score = performance_metrics.get('collaboration_score', 0.0)
            if collaboration_score > 0:
                current_collab = self.crew_metrics['collaboration_quality']
                total_missions = self.crew_metrics['total_missions']
                self.crew_metrics['collaboration_quality'] = (
                    (current_collab * (total_missions - 1) + collaboration_score) / total_missions
                )
            
        except Exception as e:
            logger.error(f"Error updating crew metrics: {e}")
    
    async def get_crew_status(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific crew"""
        try:
            if crew_id not in self.active_crews:
                return None
            
            crew_info = self.active_crews[crew_id]
            mission = crew_info['mission']
            
            status = {
                'crew_id': crew_id,
                'mission_name': mission.name,
                'mission_id': mission.mission_id,
                'status': crew_info['status'],
                'composition': crew_info['composition'],
                'created_at': crew_info['created_at'].isoformat(),
                'team_size': len(crew_info['composition'])
            }
            
            if 'started_at' in crew_info:
                status['started_at'] = crew_info['started_at'].isoformat()
                
                if crew_info['status'] in ['executing', 'running']:
                    status['execution_time'] = (datetime.utcnow() - crew_info['started_at']).total_seconds()
            
            if 'completed_at' in crew_info:
                status['completed_at'] = crew_info['completed_at'].isoformat()
            
            if 'result' in crew_info:
                status['result_summary'] = {
                    'status': crew_info['result'].get('status'),
                    'execution_time': crew_info['result'].get('execution_time'),
                    'performance_metrics': crew_info['result'].get('performance_metrics', {})
                }
            
            if 'error' in crew_info:
                status['error'] = crew_info['error']
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting crew status: {e}")
            return None
    
    def get_crew_system_status(self) -> Dict[str, Any]:
        """Get overall crew system status"""
        try:
            active_crews = len([c for c in self.active_crews.values() if c['status'] in ['created', 'executing']])
            
            return {
                'crew_system_status': 'active',
                'crewai_available': CREWAI_AVAILABLE,
                'total_crew_members': len(self.crew_members),
                'active_crews': active_crews,
                'total_crews': len(self.active_crews),
                'mission_history': len(self.mission_history),
                'metrics': self.crew_metrics,
                'available_roles': list(self.role_definitions.keys()),
                'role_definitions': {
                    role_id: {
                        'role': role_def['role'],
                        'capabilities': role_def['capabilities'],
                        'cognitive_bias': role_def['cognitive_bias']
                    }
                    for role_id, role_def in self.role_definitions.items()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting crew system status: {e}")
            return {'error': str(e)}


class IntelligenceMissionTemplates:
    """Pre-defined mission templates for common intelligence operations"""
    
    @staticmethod
    def create_comprehensive_osint_mission(target: str) -> CrewMission:
        """Create comprehensive OSINT collection mission"""
        return CrewMission(
            mission_id=f"osint_mission_{int(time.time())}",
            name=f"Comprehensive OSINT Collection - {target}",
            description=f"Conduct comprehensive open-source intelligence collection on target: {target}",
            objectives=[
                f"Collect domain intelligence for {target}",
                f"Gather social media intelligence related to {target}",
                f"Scan threat intelligence feeds for {target}",
                f"Analyze collected intelligence for patterns and insights",
                f"Generate comprehensive intelligence report"
            ],
            crew_composition=['orchestrator', 'researcher', 'analyst', 'critic', 'writer'],
            expected_deliverables=[
                "Domain intelligence report",
                "Social media analysis",
                "Threat assessment",
                "Comprehensive intelligence summary"
            ],
            success_criteria={
                'min_confidence': 0.8,
                'min_sources': 5,
                'completeness_threshold': 0.85
            },
            context={'target': target, 'collection_type': 'comprehensive'}
        )
    
    @staticmethod
    def create_threat_assessment_mission(threat_indicator: str) -> CrewMission:
        """Create threat assessment mission"""
        return CrewMission(
            mission_id=f"threat_mission_{int(time.time())}",
            name=f"Threat Assessment - {threat_indicator}",
            description=f"Conduct comprehensive threat assessment for indicator: {threat_indicator}",
            objectives=[
                f"Research threat indicator {threat_indicator}",
                f"Analyze threat patterns and TTPs",
                f"Assess risk level and potential impact",
                f"Generate threat intelligence report with recommendations"
            ],
            crew_composition=['orchestrator', 'researcher', 'analyst', 'writer'],
            expected_deliverables=[
                "Threat intelligence report",
                "Risk assessment",
                "Mitigation recommendations"
            ],
            success_criteria={
                'threat_confidence': 0.8,
                'risk_assessment_quality': 0.9
            },
            context={'threat_indicator': threat_indicator, 'assessment_type': 'comprehensive'}
        )
    
    @staticmethod
    def create_investigation_mission(case_description: str) -> CrewMission:
        """Create investigation mission"""
        return CrewMission(
            mission_id=f"investigation_mission_{int(time.time())}",
            name=f"Investigation - {case_description[:50]}",
            description=f"Conduct thorough investigation: {case_description}",
            objectives=[
                "Plan investigation approach and methodology",
                "Collect and analyze evidence",
                "Reconstruct timeline of events",
                "Generate hypotheses and test them",
                "Produce investigation report with findings"
            ],
            crew_composition=['orchestrator', 'planner', 'researcher', 'analyst', 'critic', 'writer'],
            expected_deliverables=[
                "Investigation plan",
                "Evidence analysis",
                "Timeline reconstruction",
                "Investigation report"
            ],
            success_criteria={
                'evidence_quality': 0.8,
                'timeline_accuracy': 0.9,
                'hypothesis_confidence': 0.75
            },
            context={'case_description': case_description, 'investigation_type': 'comprehensive'}
        )