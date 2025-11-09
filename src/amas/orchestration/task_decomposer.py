"""
AI-Powered Task Decomposition Engine

Intelligently breaks down complex user requests into coordinated
specialist workflows with dependency management and resource estimation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskComplexity(str, Enum):
    SIMPLE = "simple"          # Single agent, <30 minutes
    MODERATE = "moderate"      # 2-3 agents, 30min-2hours  
    COMPLEX = "complex"        # 4-6 agents, 2-8 hours
    ENTERPRISE = "enterprise"  # 6+ agents, 8+ hours
    INVESTIGATION = "investigation"  # Specialized long-term

class AgentSpecialty(str, Enum):
    # Research specialists
    ACADEMIC_RESEARCHER = "academic_researcher"
    WEB_INTELLIGENCE = "web_intelligence_gatherer"
    NEWS_ANALYST = "news_trends_analyzer"
    COMPETITIVE_INTEL = "competitive_intelligence"
    SOCIAL_MONITOR = "social_media_monitor"
    
    # Analysis specialists  
    DATA_ANALYST = "data_analyst"
    STATISTICAL_MODELER = "statistical_modeler"
    PATTERN_RECOGNIZER = "pattern_recognition_expert"
    RISK_ASSESSOR = "risk_assessment_specialist"
    FINANCIAL_ANALYZER = "financial_performance_analyst"
    
    # Creative specialists
    GRAPHICS_DESIGNER = "graphics_diagram_designer"
    CONTENT_WRITER = "content_writer_editor"
    PRESENTATION_FORMATTER = "presentation_formatter"
    MEDIA_PRODUCER = "media_video_producer"
    INFOGRAPHIC_CREATOR = "infographic_creator"
    
    # Technical specialists
    CODE_REVIEWER = "code_reviewer_optimizer"
    SYSTEM_ARCHITECT = "system_architect"
    SECURITY_ANALYST = "security_analyst"
    PERFORMANCE_ENGINEER = "performance_engineer"
    DEVOPS_SPECIALIST = "devops_specialist"
    
    # Investigation specialists
    DIGITAL_FORENSICS = "digital_forensics_expert"
    NETWORK_ANALYZER = "network_security_analyzer"
    REVERSE_ENGINEER = "reverse_engineering_specialist"
    CASE_INVESTIGATOR = "case_investigation_manager"
    EVIDENCE_COMPILER = "evidence_compilation_expert"
    
    # QA specialists
    FACT_CHECKER = "fact_checker_validator"
    QUALITY_CONTROLLER = "output_quality_controller"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    ERROR_DETECTOR = "error_detection_specialist"
    DELIVERY_APPROVER = "final_delivery_approver"

@dataclass
class TaskRequirement:
    """Represents a specific skill or capability requirement"""
    skill_type: AgentSpecialty
    priority: int  # 1-10, higher = more critical
    estimated_hours: float
    dependencies: List[str] = field(default_factory=list)
    parallel_eligible: bool = True
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    quality_gates: List[str] = field(default_factory=list)

@dataclass 
class SubTask:
    """Individual sub-task within a complex workflow"""
    id: str
    title: str
    description: str
    assigned_agent: AgentSpecialty
    estimated_duration_hours: float
    priority: int
    
    # Dependencies and coordination
    depends_on: List[str] = field(default_factory=list)
    enables: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    
    # Quality and validation
    success_criteria: List[str] = field(default_factory=list)
    quality_checkpoints: List[str] = field(default_factory=list)
    review_required: bool = True
    
    # Execution metadata
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_summary: Optional[str] = None

@dataclass
class WorkflowPlan:
    """Complete execution plan for a complex task"""
    id: str
    user_request: str
    complexity: TaskComplexity
    
    # Task breakdown
    sub_tasks: List[SubTask] = field(default_factory=list)
    execution_phases: List[str] = field(default_factory=list)
    
    # Resource planning
    estimated_total_hours: float = 0.0
    estimated_cost_usd: float = 0.0
    required_specialists: Set[AgentSpecialty] = field(default_factory=set)
    
    # Quality assurance
    quality_gates: List[Dict[str, Any]] = field(default_factory=list)
    final_deliverable_format: str = "comprehensive_report"
    
    # Execution tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "planned"
    progress_percentage: float = 0.0
    
    # Metadata
    risk_assessment: str = "medium"
    user_approval_required: bool = False
    estimated_completion: Optional[datetime] = None

class TaskDecomposer:
    """AI-powered task decomposition for multi-agent coordination"""
    
    def __init__(self):
        # Load task pattern knowledge base
        self.task_patterns = self._load_task_patterns()
        self.specialist_capabilities = self._load_specialist_capabilities()
        self.coordination_rules = self._load_coordination_rules()
        
        logger.info(f"Task Decomposer initialized with {len(self.task_patterns)} patterns")
    
    def _load_task_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common task patterns for intelligent decomposition"""
        return {
            # Research & Analysis patterns
            "market_research": {
                "keywords": ["market", "research", "analysis", "trends", "competition"],
                "required_specialists": [AgentSpecialty.WEB_INTELLIGENCE, AgentSpecialty.DATA_ANALYST, 
                                       AgentSpecialty.COMPETITIVE_INTEL, AgentSpecialty.GRAPHICS_DESIGNER],
                "typical_duration": 4.0,
                "complexity": TaskComplexity.COMPLEX,
                "phases": ["research", "analysis", "synthesis", "presentation"]
            },
            
            "competitive_analysis": {
                "keywords": ["competitor", "competitive", "analysis", "comparison", "market position"],
                "required_specialists": [AgentSpecialty.COMPETITIVE_INTEL, AgentSpecialty.DATA_ANALYST,
                                       AgentSpecialty.FINANCIAL_ANALYZER, AgentSpecialty.PRESENTATION_FORMATTER],
                "typical_duration": 6.0,
                "complexity": TaskComplexity.COMPLEX,
                "phases": ["intelligence_gathering", "data_analysis", "comparison_matrix", "presentation"]
            },
            
            # Investigation patterns
            "digital_investigation": {
                "keywords": ["investigate", "investigation", "forensics", "evidence", "case"],
                "required_specialists": [AgentSpecialty.DIGITAL_FORENSICS, AgentSpecialty.NETWORK_ANALYZER,
                                       AgentSpecialty.EVIDENCE_COMPILER, AgentSpecialty.CASE_INVESTIGATOR],
                "typical_duration": 12.0,
                "complexity": TaskComplexity.INVESTIGATION,
                "phases": ["evidence_collection", "analysis", "correlation", "reporting"]
            },
            
            "social_intelligence": {
                "keywords": ["social", "media", "monitoring", "sentiment", "influence"],
                "required_specialists": [AgentSpecialty.SOCIAL_MONITOR, AgentSpecialty.DATA_ANALYST,
                                       AgentSpecialty.PATTERN_RECOGNIZER, AgentSpecialty.CONTENT_WRITER],
                "typical_duration": 3.0,
                "complexity": TaskComplexity.MODERATE,
                "phases": ["social_monitoring", "sentiment_analysis", "reporting"]
            },
            
            # Technical patterns
            "system_analysis": {
                "keywords": ["system", "architecture", "technical", "code", "performance"],
                "required_specialists": [AgentSpecialty.SYSTEM_ARCHITECT, AgentSpecialty.CODE_REVIEWER,
                                       AgentSpecialty.SECURITY_ANALYST, AgentSpecialty.PERFORMANCE_ENGINEER],
                "typical_duration": 8.0,
                "complexity": TaskComplexity.COMPLEX,
                "phases": ["system_review", "security_analysis", "performance_audit", "recommendations"]
            },
            
            # Content creation patterns
            "content_creation": {
                "keywords": ["create", "write", "content", "article", "blog", "document"],
                "required_specialists": [AgentSpecialty.CONTENT_WRITER, AgentSpecialty.GRAPHICS_DESIGNER,
                                       AgentSpecialty.QUALITY_CONTROLLER, AgentSpecialty.FACT_CHECKER],
                "typical_duration": 2.0,
                "complexity": TaskComplexity.MODERATE,
                "phases": ["research", "writing", "graphics", "review"]
            },
            
            "presentation_creation": {
                "keywords": ["presentation", "slides", "executive", "pitch", "report"],
                "required_specialists": [AgentSpecialty.CONTENT_WRITER, AgentSpecialty.DATA_ANALYST,
                                       AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.PRESENTATION_FORMATTER],
                "typical_duration": 3.0,
                "complexity": TaskComplexity.MODERATE,
                "phases": ["content_development", "data_analysis", "design", "formatting"]
            }
        }
    
    def _load_specialist_capabilities(self) -> Dict[AgentSpecialty, Dict[str, Any]]:
        """Load detailed capabilities for each specialist agent"""
        return {
            # Research specialists capabilities
            AgentSpecialty.ACADEMIC_RESEARCHER: {
                "skills": ["academic_search", "paper_analysis", "citation_management", "literature_review"],
                "tools": ["google_scholar", "arxiv_search", "pubmed", "semantic_scholar"],
                "avg_task_duration": 1.5,
                "max_parallel_tasks": 3,
                "quality_score": 0.95,
                "cost_per_hour": 0.15
            },
            
            AgentSpecialty.WEB_INTELLIGENCE: {
                "skills": ["web_scraping", "data_extraction", "trend_analysis", "source_validation"],
                "tools": ["web_scraper", "rss_monitor", "news_aggregator", "fact_checker"],
                "avg_task_duration": 1.0,
                "max_parallel_tasks": 5,
                "quality_score": 0.88,
                "cost_per_hour": 0.10
            },
            
            AgentSpecialty.COMPETITIVE_INTEL: {
                "skills": ["competitor_tracking", "market_analysis", "pricing_intelligence", "strategic_analysis"],
                "tools": ["market_data_apis", "pricing_monitors", "company_databases", "patent_search"],
                "avg_task_duration": 2.0,
                "max_parallel_tasks": 2,
                "quality_score": 0.92,
                "cost_per_hour": 0.20
            },
            
            # Analysis specialists capabilities
            AgentSpecialty.DATA_ANALYST: {
                "skills": ["statistical_analysis", "data_visualization", "trend_identification", "hypothesis_testing"],
                "tools": ["pandas", "numpy", "plotly", "scipy", "sklearn"],
                "avg_task_duration": 1.5,
                "max_parallel_tasks": 4,
                "quality_score": 0.93,
                "cost_per_hour": 0.12
            },
            
            AgentSpecialty.PATTERN_RECOGNIZER: {
                "skills": ["pattern_detection", "anomaly_identification", "correlation_analysis", "predictive_modeling"],
                "tools": ["tensorflow", "pytorch", "scikit_learn", "time_series_analysis"],
                "avg_task_duration": 2.5,
                "max_parallel_tasks": 2,
                "quality_score": 0.90,
                "cost_per_hour": 0.25
            },
            
            # Creative specialists capabilities
            AgentSpecialty.GRAPHICS_DESIGNER: {
                "skills": ["infographic_design", "chart_creation", "visual_storytelling", "brand_consistency"],
                "tools": ["matplotlib", "plotly", "canva_api", "image_generation", "svg_creation"],
                "avg_task_duration": 1.0,
                "max_parallel_tasks": 3,
                "quality_score": 0.87,
                "cost_per_hour": 0.08
            },
            
            AgentSpecialty.CONTENT_WRITER: {
                "skills": ["professional_writing", "technical_documentation", "executive_summaries", "editing"],
                "tools": ["grammar_check", "style_guide", "citation_formatter", "readability_analyzer"],
                "avg_task_duration": 1.5,
                "max_parallel_tasks": 4,
                "quality_score": 0.91,
                "cost_per_hour": 0.12
            },
            
            # QA specialists capabilities
            AgentSpecialty.FACT_CHECKER: {
                "skills": ["fact_verification", "source_validation", "accuracy_assessment", "bias_detection"],
                "tools": ["fact_check_apis", "source_credibility_db", "bias_detector", "claim_validator"],
                "avg_task_duration": 0.8,
                "max_parallel_tasks": 5,
                "quality_score": 0.96,
                "cost_per_hour": 0.10
            },
            
            AgentSpecialty.QUALITY_CONTROLLER: {
                "skills": ["output_validation", "format_checking", "completeness_review", "professional_standards"],
                "tools": ["format_validator", "completeness_checker", "style_guide", "quality_metrics"],
                "avg_task_duration": 0.5,
                "max_parallel_tasks": 6,
                "quality_score": 0.94,
                "cost_per_hour": 0.08
            }
        }
    
    def _load_coordination_rules(self) -> Dict[str, Any]:
        """Load rules for agent coordination and workflow optimization"""
        return {
            "dependency_rules": {
                # Research must complete before analysis
                "research_before_analysis": {
                    "prerequisites": [AgentSpecialty.ACADEMIC_RESEARCHER, AgentSpecialty.WEB_INTELLIGENCE],
                    "enables": [AgentSpecialty.DATA_ANALYST, AgentSpecialty.PATTERN_RECOGNIZER]
                },
                
                # Analysis before creative work
                "analysis_before_creative": {
                    "prerequisites": [AgentSpecialty.DATA_ANALYST],
                    "enables": [AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.PRESENTATION_FORMATTER]
                },
                
                # Everything before QA
                "work_before_qa": {
                    "prerequisites": ["all_specialists"],
                    "enables": [AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER]
                }
            },
            
            "parallel_groups": {
                "research_group": [AgentSpecialty.ACADEMIC_RESEARCHER, AgentSpecialty.WEB_INTELLIGENCE, 
                                  AgentSpecialty.NEWS_ANALYST, AgentSpecialty.COMPETITIVE_INTEL],
                
                "analysis_group": [AgentSpecialty.DATA_ANALYST, AgentSpecialty.STATISTICAL_MODELER,
                                  AgentSpecialty.PATTERN_RECOGNIZER, AgentSpecialty.RISK_ASSESSOR],
                
                "creative_group": [AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.CONTENT_WRITER,
                                  AgentSpecialty.MEDIA_PRODUCER, AgentSpecialty.INFOGRAPHIC_CREATOR],
                
                "qa_group": [AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER,
                            AgentSpecialty.COMPLIANCE_REVIEWER, AgentSpecialty.ERROR_DETECTOR]
            },
            
            "quality_thresholds": {
                "minimum_quality_score": 0.85,
                "fact_check_confidence": 0.90,
                "output_completeness": 0.95,
                "professional_standard": 0.92
            }
        }
    
    async def analyze_task_complexity(self, user_request: str) -> Tuple[TaskComplexity, float]:
        """Analyze user request to determine complexity and confidence"""
        request_lower = user_request.lower()
        
        # Count complexity indicators
        complexity_signals = {
            "simple_indicators": ["simple", "quick", "basic", "one", "single"],
            "moderate_indicators": ["analyze", "compare", "create", "write", "design"],
            "complex_indicators": ["comprehensive", "detailed", "multiple", "compare", "investigate"],
            "enterprise_indicators": ["enterprise", "executive", "strategic", "complete", "professional"],
            "investigation_indicators": ["investigate", "forensics", "evidence", "case", "security"]
        }
        
        scores = {}
        for complexity, indicators in complexity_signals.items():
            score = sum(1 for indicator in indicators if indicator in request_lower)
            # Weight by indicator importance
            if "enterprise" in complexity:
                score *= 1.5
            elif "investigation" in complexity:
                score *= 1.3
            scores[complexity] = score
        
        # Determine primary complexity
        max_score = max(scores.values())
        if max_score == 0:
            return TaskComplexity.SIMPLE, 0.6
        
        dominant_type = max(scores.items(), key=lambda x: x[1])[0]
        confidence = min(0.95, 0.5 + (max_score * 0.1))
        
        complexity_mapping = {
            "simple_indicators": TaskComplexity.SIMPLE,
            "moderate_indicators": TaskComplexity.MODERATE,
            "complex_indicators": TaskComplexity.COMPLEX,
            "enterprise_indicators": TaskComplexity.ENTERPRISE,
            "investigation_indicators": TaskComplexity.INVESTIGATION
        }
        
        return complexity_mapping[dominant_type], confidence
    
    async def identify_required_specialists(self, 
                                          user_request: str,
                                          complexity: TaskComplexity) -> List[TaskRequirement]:
        """Identify which specialist agents are needed for the task"""
        request_lower = user_request.lower()
        requirements = []
        
        # Match against task patterns
        pattern_matches = []
        for pattern_name, pattern_data in self.task_patterns.items():
            match_score = sum(1 for keyword in pattern_data["keywords"] 
                            if keyword in request_lower)
            if match_score > 0:
                pattern_matches.append((pattern_name, match_score, pattern_data))
        
        # Sort by relevance
        pattern_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Build requirements from top matches
        used_specialists = set()
        
        for pattern_name, score, pattern_data in pattern_matches:
            pattern_specialists = pattern_data.get("required_specialists", [])
            
            for specialist in pattern_specialists:
                if specialist not in used_specialists:
                    capabilities = self.specialist_capabilities.get(specialist, {})
                    
                    requirement = TaskRequirement(
                        skill_type=specialist,
                        priority=min(10, 5 + score),
                        estimated_hours=capabilities.get("avg_task_duration", 1.0),
                        parallel_eligible=True,
                        resource_requirements={
                            "max_parallel": capabilities.get("max_parallel_tasks", 2),
                            "cost_per_hour": capabilities.get("cost_per_hour", 0.10),
                            "quality_score": capabilities.get("quality_score", 0.85)
                        }
                    )
                    
                    requirements.append(requirement)
                    used_specialists.add(specialist)
        
        # Always add QA specialists for complex tasks
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.ENTERPRISE, TaskComplexity.INVESTIGATION]:
            qa_specialists = [AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER]
            
            if complexity == TaskComplexity.ENTERPRISE:
                qa_specialists.append(AgentSpecialty.COMPLIANCE_REVIEWER)
            
            for specialist in qa_specialists:
                if specialist not in used_specialists:
                    capabilities = self.specialist_capabilities.get(specialist, {})
                    
                    requirement = TaskRequirement(
                        skill_type=specialist,
                        priority=8,  # QA is high priority
                        estimated_hours=capabilities.get("avg_task_duration", 0.5),
                        dependencies=["all_specialists"],  # QA comes last
                        parallel_eligible=True
                    )
                    
                    requirements.append(requirement)
                    used_specialists.add(specialist)
        
        return requirements
    
    async def create_execution_phases(self, requirements: List[TaskRequirement]) -> List[str]:
        """Create logical execution phases based on dependencies"""
        # Standard phase progression
        phases = []
        
        # Determine which phases are needed
        specialist_types = {req.skill_type for req in requirements}
        
        research_specialists = {
            AgentSpecialty.ACADEMIC_RESEARCHER, AgentSpecialty.WEB_INTELLIGENCE,
            AgentSpecialty.NEWS_ANALYST, AgentSpecialty.COMPETITIVE_INTEL, AgentSpecialty.SOCIAL_MONITOR
        }
        
        analysis_specialists = {
            AgentSpecialty.DATA_ANALYST, AgentSpecialty.STATISTICAL_MODELER,
            AgentSpecialty.PATTERN_RECOGNIZER, AgentSpecialty.RISK_ASSESSOR, AgentSpecialty.FINANCIAL_ANALYZER
        }
        
        creative_specialists = {
            AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.CONTENT_WRITER,
            AgentSpecialty.PRESENTATION_FORMATTER, AgentSpecialty.MEDIA_PRODUCER, AgentSpecialty.INFOGRAPHIC_CREATOR
        }
        
        qa_specialists = {
            AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER,
            AgentSpecialty.COMPLIANCE_REVIEWER, AgentSpecialty.ERROR_DETECTOR, AgentSpecialty.DELIVERY_APPROVER
        }
        
        # Build phases based on specialist requirements
        if research_specialists & specialist_types:
            phases.append("research_and_intelligence_gathering")
        
        if analysis_specialists & specialist_types:
            phases.append("data_analysis_and_modeling")
        
        if creative_specialists & specialist_types:
            phases.append("content_creation_and_formatting")
        
        if qa_specialists & specialist_types:
            phases.append("quality_assurance_and_review")
        
        # Always end with delivery phase
        phases.append("final_delivery_and_approval")
        
        return phases
    
    async def generate_sub_tasks(self, 
                               user_request: str,
                               requirements: List[TaskRequirement],
                               phases: List[str]) -> List[SubTask]:
        """Generate specific sub-tasks for each specialist"""
        sub_tasks = []
        task_counter = 1
        
        # Group requirements by phase
        phase_groups = {
            "research_and_intelligence_gathering": [
                AgentSpecialty.ACADEMIC_RESEARCHER, AgentSpecialty.WEB_INTELLIGENCE,
                AgentSpecialty.NEWS_ANALYST, AgentSpecialty.COMPETITIVE_INTEL, AgentSpecialty.SOCIAL_MONITOR
            ],
            "data_analysis_and_modeling": [
                AgentSpecialty.DATA_ANALYST, AgentSpecialty.STATISTICAL_MODELER,
                AgentSpecialty.PATTERN_RECOGNIZER, AgentSpecialty.RISK_ASSESSOR, AgentSpecialty.FINANCIAL_ANALYZER
            ],
            "content_creation_and_formatting": [
                AgentSpecialty.GRAPHICS_DESIGNER, AgentSpecialty.CONTENT_WRITER,
                AgentSpecialty.PRESENTATION_FORMATTER, AgentSpecialty.MEDIA_PRODUCER, AgentSpecialty.INFOGRAPHIC_CREATOR
            ],
            "quality_assurance_and_review": [
                AgentSpecialty.FACT_CHECKER, AgentSpecialty.QUALITY_CONTROLLER,
                AgentSpecialty.COMPLIANCE_REVIEWER, AgentSpecialty.ERROR_DETECTOR
            ]
        }
        
        # Generate sub-tasks for each phase
        for phase in phases:
            if phase in phase_groups:
                phase_specialists = set(phase_groups[phase])
                phase_requirements = [req for req in requirements if req.skill_type in phase_specialists]
                
                for req in phase_requirements:
                    # Generate task description based on specialist and user request
                    task_description = await self._generate_task_description(
                        req.skill_type, user_request, phase
                    )
                    
                    sub_task = SubTask(
                        id=f"task_{task_counter:03d}_{req.skill_type.value}",
                        title=f"{req.skill_type.value.replace('_', ' ').title()} - {phase.replace('_', ' ').title()}",
                        description=task_description,
                        assigned_agent=req.skill_type,
                        estimated_duration_hours=req.estimated_hours,
                        priority=req.priority,
                        parallel_group=phase if req.parallel_eligible else None,
                        success_criteria=await self._generate_success_criteria(req.skill_type),
                        quality_checkpoints=await self._generate_quality_checkpoints(req.skill_type)
                    )
                    
                    # Set dependencies
                    if phase != "research_and_intelligence_gathering":
                        # Non-research phases depend on previous phases
                        previous_phase_tasks = [t.id for t in sub_tasks 
                                              if t.parallel_group and t.parallel_group != phase]
                        sub_task.depends_on = previous_phase_tasks
                    
                    sub_tasks.append(sub_task)
                    task_counter += 1
        
        # Add coordination dependencies
        await self._add_coordination_dependencies(sub_tasks)
        
        return sub_tasks
    
    async def _generate_task_description(self, 
                                       specialist: AgentSpecialty, 
                                       user_request: str,
                                       phase: str) -> str:
        """Generate specific task description for specialist"""
        templates = {
            AgentSpecialty.ACADEMIC_RESEARCHER: 
                f"Conduct academic research for: {user_request}. "
                f"Search academic databases, analyze relevant papers, compile literature review with proper citations.",
            
            AgentSpecialty.WEB_INTELLIGENCE:
                f"Gather web intelligence for: {user_request}. "
                f"Scrape relevant websites, monitor news sources, validate information credibility, compile findings.",
            
            AgentSpecialty.DATA_ANALYST:
                f"Analyze data related to: {user_request}. "
                f"Process gathered information, identify trends, perform statistical analysis, create data visualizations.",
            
            AgentSpecialty.GRAPHICS_DESIGNER:
                f"Create visual assets for: {user_request}. "
                f"Design charts, infographics, and diagrams based on analysis results, ensure professional presentation quality.",
            
            AgentSpecialty.CONTENT_WRITER:
                f"Write professional content for: {user_request}. "
                f"Create executive summary, detailed analysis, and recommendations based on research and analysis findings.",
            
            AgentSpecialty.FACT_CHECKER:
                f"Verify accuracy of all content for: {user_request}. "
                f"Check facts, validate sources, assess credibility, flag any inaccuracies or biased information.",
            
            AgentSpecialty.QUALITY_CONTROLLER:
                f"Review output quality for: {user_request}. "
                f"Ensure professional standards, check completeness, validate formatting, approve final deliverable."
        }
        
        return templates.get(specialist, 
            f"Execute {specialist.value.replace('_', ' ')} tasks for: {user_request}")
    
    async def _generate_success_criteria(self, specialist: AgentSpecialty) -> List[str]:
        """Generate success criteria for each specialist type"""
        criteria_map = {
            AgentSpecialty.ACADEMIC_RESEARCHER: [
                "Minimum 10 relevant academic sources identified",
                "All sources from last 5 years unless historical context needed",
                "Citations properly formatted and verifiable",
                "Literature review covers all major perspectives"
            ],
            
            AgentSpecialty.WEB_INTELLIGENCE: [
                "Minimum 15 credible web sources gathered",
                "Source credibility assessed and documented",
                "Information cross-referenced across multiple sources",
                "Recent developments (last 6 months) prioritized"
            ],
            
            AgentSpecialty.DATA_ANALYST: [
                "Statistical significance of findings validated (p<0.05)",
                "Data visualizations clearly communicate insights",
                "Trends and patterns identified with confidence scores",
                "Analysis methodology documented and reproducible"
            ],
            
            AgentSpecialty.GRAPHICS_DESIGNER: [
                "Visual assets professionally designed and branded",
                "Charts and diagrams accurately represent data",
                "Design consistency maintained across all assets",
                "Assets optimized for both digital and print use"
            ],
            
            AgentSpecialty.CONTENT_WRITER: [
                "Content follows professional writing standards",
                "Executive summary captures key insights (1-2 pages)",
                "Technical accuracy maintained throughout",
                "Recommendations are actionable and specific"
            ],
            
            AgentSpecialty.FACT_CHECKER: [
                "All factual claims verified against primary sources",
                "Source credibility assessed using established frameworks",
                "Potential biases identified and flagged",
                "Confidence scores assigned to all major claims"
            ],
            
            AgentSpecialty.QUALITY_CONTROLLER: [
                "Output meets professional business presentation standards",
                "All sections complete with no gaps or placeholders",
                "Formatting consistent and visually appealing",
                "Final deliverable ready for executive presentation"
            ]
        }
        
        return criteria_map.get(specialist, ["Task completed according to agent capabilities"])
    
    async def _generate_quality_checkpoints(self, specialist: AgentSpecialty) -> List[str]:
        """Generate quality checkpoints for continuous validation"""
        checkpoint_map = {
            AgentSpecialty.ACADEMIC_RESEARCHER: [
                "Source relevance validation",
                "Citation accuracy check",
                "Literature coverage assessment"
            ],
            
            AgentSpecialty.DATA_ANALYST: [
                "Data quality validation",
                "Statistical method verification",
                "Visualization accuracy check"
            ],
            
            AgentSpecialty.CONTENT_WRITER: [
                "Grammar and style check",
                "Technical accuracy review",
                "Readability assessment"
            ]
        }
        
        return checkpoint_map.get(specialist, ["Output quality validation"])
    
    async def _add_coordination_dependencies(self, sub_tasks: List[SubTask]):
        """Add intelligent coordination dependencies between sub-tasks"""
        # Build task lookup
        task_lookup = {task.id: task for task in sub_tasks}
        
        # Apply coordination rules
        for rule_name, rule_data in self.coordination_rules["dependency_rules"].items():
            prerequisites = rule_data["prerequisites"]
            enables = rule_data["enables"]
            
            # Find prerequisite tasks
            prereq_tasks = []
            for task in sub_tasks:
                if (isinstance(prerequisites[0], str) and prerequisites[0] == "all_specialists") or \
                   task.assigned_agent in prerequisites:
                    prereq_tasks.append(task.id)
            
            # Find enabled tasks
            for task in sub_tasks:
                if task.assigned_agent in enables:
                    task.depends_on.extend(prereq_tasks)
    
    async def calculate_resource_estimates(self, sub_tasks: List[SubTask]) -> Tuple[float, float]:
        """Calculate total time and cost estimates"""
        # Calculate critical path for time estimate
        total_hours = 0.0
        total_cost = 0.0
        
        # Group by parallel execution
        parallel_groups = {}
        for task in sub_tasks:
            if task.parallel_group:
                if task.parallel_group not in parallel_groups:
                    parallel_groups[task.parallel_group] = []
                parallel_groups[task.parallel_group].append(task)
            else:
                # Sequential tasks
                total_hours += task.estimated_duration_hours
        
        # Add parallel group durations (max within each group)
        for group_name, group_tasks in parallel_groups.items():
            max_duration = max(task.estimated_duration_hours for task in group_tasks)
            total_hours += max_duration
        
        # Calculate cost
        for task in sub_tasks:
            capabilities = self.specialist_capabilities.get(task.assigned_agent, {})
            cost_per_hour = capabilities.get("cost_per_hour", 0.10)
            total_cost += task.estimated_duration_hours * cost_per_hour
        
        return total_hours, total_cost
    
    async def decompose_task(self, user_request: str) -> WorkflowPlan:
        """
        Main entry point: decompose user request into executable workflow plan.
        
        This method orchestrates the complete task decomposition process:
        1. Analyzes task complexity and requirements
        2. Identifies required specialist agents
        3. Creates execution phases with dependencies
        4. Generates detailed sub-tasks
        5. Calculates resource estimates
        6. Creates comprehensive workflow plan
        
        Args:
            user_request: Natural language description of the task to be executed
            
        Returns:
            WorkflowPlan: Complete execution plan with all sub-tasks, phases, and estimates
            
        Raises:
            ValueError: If user_request is empty or invalid
            TimeoutError: If decomposition exceeds timeout threshold
            
        Example:
            >>> decomposer = TaskDecomposer()
            >>> workflow = await decomposer.decompose_task(
            ...     "Research AI market trends and create executive presentation"
            ... )
            >>> print(f"Created workflow with {len(workflow.sub_tasks)} tasks")
        """
        if not user_request or not user_request.strip():
            raise ValueError("User request cannot be empty")
        
        logger.info(f"Decomposing task: {user_request[:100]}...")
        
        try:
            # Step 1: Analyze complexity
            complexity, confidence = await self.analyze_task_complexity(user_request)
            logger.info(f"Task complexity: {complexity.value} (confidence: {confidence:.2f})")
            
            # Step 2: Identify required specialists
            requirements = await self.identify_required_specialists(user_request, complexity)
            logger.info(f"Required specialists: {len(requirements)}")
            
            # Validate we have requirements
            if not requirements:
                logger.warning("No specialists identified for task, using default analysis specialist")
                from .config import get_config
                config = get_config()
                # Add default specialist if none found
                requirements = [TaskRequirement(
                    skill_type=AgentSpecialty.DATA_ANALYST,
                    priority=config.default_task_priority,
                    estimated_hours=1.0
                )]
            
            # Step 3: Create execution phases
            phases = await self.create_execution_phases(requirements)
            logger.info(f"Execution phases: {len(phases)}")
            
            # Step 4: Generate sub-tasks
            sub_tasks = await self.generate_sub_tasks(user_request, requirements, phases)
            logger.info(f"Generated sub-tasks: {len(sub_tasks)}")
            
            # Validate sub-task count
            from .config import get_config
            config = get_config()
            if len(sub_tasks) > config.max_sub_tasks_per_workflow:
                logger.warning(
                    f"Generated {len(sub_tasks)} sub-tasks, exceeding limit of "
                    f"{config.max_sub_tasks_per_workflow}. Truncating..."
                )
                sub_tasks = sub_tasks[:config.max_sub_tasks_per_workflow]
            
            # Step 5: Calculate estimates
            total_hours, total_cost = await self.calculate_resource_estimates(sub_tasks)
            
            # Step 6: Create workflow plan
            workflow_plan = WorkflowPlan(
                id=f"workflow_{uuid.uuid4().hex[:8]}",
                user_request=user_request,
                complexity=complexity,
                sub_tasks=sub_tasks,
                execution_phases=phases,
                estimated_total_hours=total_hours,
                estimated_cost_usd=total_cost,
                required_specialists={req.skill_type for req in requirements},
                estimated_completion=datetime.now(timezone.utc) + timedelta(hours=total_hours)
            )
            
            # Add quality gates
            workflow_plan.quality_gates = await self._generate_quality_gates(complexity, requirements)
            
            # Risk assessment
            workflow_plan.risk_assessment = await self._assess_workflow_risk(workflow_plan)
            
            # Approval requirements
            workflow_plan.user_approval_required = await self._requires_user_approval(workflow_plan)
            
            logger.info(f"Workflow plan created: {len(sub_tasks)} tasks, "
                       f"{total_hours:.1f}h estimated, ${total_cost:.2f} cost")
            
            return workflow_plan
            
        except Exception as e:
            logger.error(f"Error decomposing task: {e}", exc_info=True)
            raise
    
    async def _generate_quality_gates(self, 
                                    complexity: TaskComplexity, 
                                    requirements: List[TaskRequirement]) -> List[Dict[str, Any]]:
        """Generate quality gates based on task complexity"""
        gates = []
        
        # Standard quality gates
        gates.append({
            "name": "research_completeness_gate",
            "description": "Verify all research requirements met",
            "threshold": 0.90,
            "checkpoint": "end_of_research_phase"
        })
        
        gates.append({
            "name": "analysis_accuracy_gate",
            "description": "Validate analysis accuracy and methodology",
            "threshold": 0.85,
            "checkpoint": "end_of_analysis_phase"
        })
        
        gates.append({
            "name": "output_quality_gate", 
            "description": "Ensure professional output standards",
            "threshold": 0.92,
            "checkpoint": "pre_delivery"
        })
        
        # Add complexity-specific gates
        if complexity in [TaskComplexity.ENTERPRISE, TaskComplexity.INVESTIGATION]:
            gates.append({
                "name": "compliance_review_gate",
                "description": "Verify regulatory and ethical compliance",
                "threshold": 0.95,
                "checkpoint": "pre_delivery"
            })
        
        return gates
    
    async def _assess_workflow_risk(self, workflow: WorkflowPlan) -> str:
        """Assess risk level of workflow execution"""
        risk_factors = 0
        
        # Time-based risk
        if workflow.estimated_total_hours > 8:
            risk_factors += 1
        if workflow.estimated_total_hours > 16:
            risk_factors += 2
        
        # Complexity-based risk
        if workflow.complexity == TaskComplexity.ENTERPRISE:
            risk_factors += 2
        elif workflow.complexity == TaskComplexity.INVESTIGATION:
            risk_factors += 3
        
        # Specialist count risk
        if len(workflow.required_specialists) > 6:
            risk_factors += 1
        if len(workflow.required_specialists) > 10:
            risk_factors += 2
        
        # Cost-based risk
        if workflow.estimated_cost_usd > 10.0:
            risk_factors += 1
        if workflow.estimated_cost_usd > 25.0:
            risk_factors += 2
        
        # Assess overall risk
        if risk_factors <= 2:
            return "low"
        elif risk_factors <= 5:
            return "medium"
        elif risk_factors <= 8:
            return "high"
        else:
            return "critical"
    
    async def _requires_user_approval(self, workflow: WorkflowPlan) -> bool:
        """Determine if workflow requires user approval before execution"""
        # High-cost workflows need approval
        if workflow.estimated_cost_usd > 15.0:
            return True
        
        # Long-duration workflows need approval
        if workflow.estimated_total_hours > 12:
            return True
        
        # High-risk workflows need approval
        if workflow.risk_assessment in ["high", "critical"]:
            return True
        
        # Investigation workflows always need approval
        if workflow.complexity == TaskComplexity.INVESTIGATION:
            return True
        
        return False
    
    def serialize_workflow(self, workflow: WorkflowPlan) -> Dict[str, Any]:
        """Serialize workflow plan for storage and transmission"""
        return {
            "id": workflow.id,
            "user_request": workflow.user_request,
            "complexity": workflow.complexity.value,
            "estimated_hours": workflow.estimated_total_hours,
            "estimated_cost": workflow.estimated_cost_usd,
            "risk_assessment": workflow.risk_assessment,
            "requires_approval": workflow.user_approval_required,
            "sub_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "agent": task.assigned_agent.value,
                    "duration": task.estimated_duration_hours,
                    "priority": task.priority,
                    "dependencies": task.depends_on,
                    "success_criteria": task.success_criteria
                }
                for task in workflow.sub_tasks
            ],
            "execution_phases": workflow.execution_phases,
            "quality_gates": workflow.quality_gates,
            "created_at": workflow.created_at.isoformat(),
            "estimated_completion": workflow.estimated_completion.isoformat() if workflow.estimated_completion else None
        }

# Global task decomposer instance
_global_task_decomposer: Optional[TaskDecomposer] = None

def get_task_decomposer() -> TaskDecomposer:
    """Get global task decomposer instance"""
    global _global_task_decomposer
    if _global_task_decomposer is None:
        _global_task_decomposer = TaskDecomposer()
    return _global_task_decomposer

# Example usage and testing
if __name__ == "__main__":
    async def test_decomposition():
        decomposer = TaskDecomposer()
        
        # Test complex market research task
        user_request = (
            "Investigate AI automation market trends, analyze competitor pricing strategies, "
            "identify key market opportunities, and create an executive presentation with "
            "professional graphics and strategic recommendations for our product launch"
        )
        
        workflow = await decomposer.decompose_task(user_request)
        
        print(f"\n=== WORKFLOW DECOMPOSITION RESULTS ===")
        print(f"Task: {workflow.user_request[:100]}...")
        print(f"Complexity: {workflow.complexity.value}")
        print(f"Estimated Duration: {workflow.estimated_total_hours:.1f} hours")
        print(f"Estimated Cost: ${workflow.estimated_cost_usd:.2f}")
        print(f"Required Specialists: {len(workflow.required_specialists)}")
        print(f"Risk Assessment: {workflow.risk_assessment}")
        print(f"User Approval Required: {workflow.user_approval_required}")
        
        print(f"\n=== EXECUTION PHASES ({len(workflow.execution_phases)}) ===")
        for i, phase in enumerate(workflow.execution_phases, 1):
            print(f"{i}. {phase.replace('_', ' ').title()}")
        
        print(f"\n=== SUB-TASKS ({len(workflow.sub_tasks)}) ===")
        for task in workflow.sub_tasks:
            deps = f" (depends on: {', '.join(task.depends_on)})" if task.depends_on else ""
            print(f"• {task.title} - {task.estimated_duration_hours:.1f}h{deps}")
        
        # Serialize for API response
        serialized = decomposer.serialize_workflow(workflow)
        print(f"\n=== SERIALIZED WORKFLOW ===")
        print(json.dumps(serialized, indent=2))
    
    # Run test
    asyncio.run(test_decomposition())
