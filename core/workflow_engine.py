"""
AMAS Advanced Workflow Engine - Graph-Based Orchestration

Sophisticated workflow orchestration system implementing:
- Graph-based workflow execution with nodes and edges
- Conditional branching and iterative loops
- Parallel execution and synchronization
- Error handling and recovery mechanisms
- Workflow state management and persistence
- Dynamic workflow modification
- Performance optimization and monitoring

Enables complex intelligence workflows with enterprise-grade reliability.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
import time
from collections import defaultdict, deque
import networkx as nx
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of workflow nodes"""
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    MERGE = "merge"
    LOOP = "loop"
    CONDITION = "condition"
    SUBPROCESS = "subprocess"
    HUMAN_INPUT = "human_input"
    DELAY = "delay"


class NodeStatus(Enum):
    """Status of workflow nodes"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class WorkflowStatus(Enum):
    """Overall workflow status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class EdgeType(Enum):
    """Types of workflow edges"""
    SEQUENTIAL = "sequential"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    LOOP_BACK = "loop_back"
    ERROR_HANDLER = "error_handler"
    TIMEOUT = "timeout"


@dataclass
class WorkflowNode:
    """Individual node in a workflow graph"""
    node_id: str
    node_type: NodeType
    name: str
    description: str = ""
    agent_type: Optional[str] = None
    action: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    status: NodeStatus = NodeStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """Edge connecting workflow nodes"""
    edge_id: str
    from_node: str
    to_node: str
    edge_type: EdgeType
    condition: Optional[str] = None
    condition_params: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0"
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: Dict[str, WorkflowEdge] = field(default_factory=dict)
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Runtime execution state of a workflow"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_nodes: Set[str] = field(default_factory=set)
    completed_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)
    node_results: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    initiated_by: str = ""
    priority: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedWorkflowEngine:
    """
    Advanced workflow orchestration engine with graph-based execution.
    
    Features:
    - Graph-based workflow definition and execution
    - Conditional branching and iterative loops
    - Parallel execution with synchronization
    - Error handling and recovery
    - Dynamic workflow modification
    - Performance monitoring and optimization
    """
    
    def __init__(self, config: Dict[str, Any], amas_system=None):
        self.config = config
        self.amas_system = amas_system
        
        # Workflow storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        
        # Execution management
        self.execution_queue = asyncio.PriorityQueue()
        self.node_executors: Dict[str, Callable] = {}
        self.condition_evaluators: Dict[str, Callable] = {}
        
        # Performance metrics
        self.workflow_metrics = {
            'total_workflows': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'active_executions': 0,
            'node_execution_stats': defaultdict(lambda: {'count': 0, 'avg_time': 0.0, 'success_rate': 0.0})
        }
        
        # Configuration
        self.max_concurrent_executions = config.get('max_concurrent_executions', 10)
        self.default_timeout_minutes = config.get('default_timeout_minutes', 60)
        self.max_execution_history = config.get('max_execution_history', 1000)
        
        # Background processing
        self._running = False
        self._background_tasks = []
        
        # Initialize built-in workflows
        self._initialize_built_in_workflows()
        self._initialize_node_executors()
        self._initialize_condition_evaluators()
        
        logger.info("Advanced Workflow Engine initialized")
    
    async def start(self):
        """Start the workflow engine and background tasks"""
        try:
            self._running = True
            
            # Start background tasks
            self._background_tasks = [
                asyncio.create_task(self._execution_processor()),
                asyncio.create_task(self._timeout_monitor()),
                asyncio.create_task(self._performance_monitor()),
                asyncio.create_task(self._cleanup_completed_executions())
            ]
            
            logger.info("Workflow Engine started with background processing")
            
        except Exception as e:
            logger.error(f"Error starting workflow engine: {e}")
            raise
    
    async def stop(self):
        """Stop the workflow engine and cleanup"""
        try:
            self._running = False
            
            # Cancel all active executions
            for execution_id in list(self.active_executions.keys()):
                await self.cancel_execution(execution_id, "Engine shutdown")
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("Workflow Engine stopped")
            
        except Exception as e:
            logger.error(f"Error stopping workflow engine: {e}")
    
    def _initialize_built_in_workflows(self):
        """Initialize built-in intelligence workflows"""
        try:
            # Comprehensive Intelligence Collection Workflow
            self.register_workflow(self._create_intelligence_collection_workflow())
            
            # Threat Assessment Workflow
            self.register_workflow(self._create_threat_assessment_workflow())
            
            # Investigation Workflow
            self.register_workflow(self._create_investigation_workflow())
            
            # Forensics Analysis Workflow
            self.register_workflow(self._create_forensics_workflow())
            
            logger.info("Built-in intelligence workflows initialized")
            
        except Exception as e:
            logger.error(f"Error initializing built-in workflows: {e}")
    
    def _create_intelligence_collection_workflow(self) -> WorkflowDefinition:
        """Create comprehensive intelligence collection workflow"""
        workflow = WorkflowDefinition(
            workflow_id="intelligence_collection_v2",
            name="Comprehensive Intelligence Collection",
            description="Advanced multi-source intelligence collection with analysis and reporting",
            version="2.0",
            timeout_minutes=120
        )
        
        # Define nodes
        nodes = {
            "start": WorkflowNode(
                node_id="start",
                node_type=NodeType.START,
                name="Start Intelligence Collection"
            ),
            "assess_target": WorkflowNode(
                node_id="assess_target",
                node_type=NodeType.TASK,
                name="Assess Target",
                description="Initial target assessment and source planning",
                agent_type="osint",
                action="assess_target",
                timeout_seconds=300
            ),
            "parallel_collection": WorkflowNode(
                node_id="parallel_collection",
                node_type=NodeType.PARALLEL,
                name="Parallel Intelligence Collection"
            ),
            "osint_collection": WorkflowNode(
                node_id="osint_collection",
                node_type=NodeType.TASK,
                name="OSINT Collection",
                description="Open source intelligence collection",
                agent_type="osint",
                action="collect_intelligence",
                timeout_seconds=1800
            ),
            "social_monitoring": WorkflowNode(
                node_id="social_monitoring",
                node_type=NodeType.TASK,
                name="Social Media Monitoring",
                description="Social media intelligence collection",
                agent_type="osint",
                action="monitor_social_media",
                timeout_seconds=900
            ),
            "threat_scanning": WorkflowNode(
                node_id="threat_scanning",
                node_type=NodeType.TASK,
                name="Threat Intelligence Scanning",
                description="Threat intelligence feed analysis",
                agent_type="osint",
                action="scan_threat_feeds",
                timeout_seconds=600
            ),
            "merge_collection": WorkflowNode(
                node_id="merge_collection",
                node_type=NodeType.MERGE,
                name="Merge Collection Results"
            ),
            "quality_check": WorkflowNode(
                node_id="quality_check",
                node_type=NodeType.DECISION,
                name="Quality Assessment",
                description="Assess quality of collected intelligence",
                conditions={
                    "min_confidence": 0.7,
                    "min_sources": 3,
                    "completeness_threshold": 0.8
                }
            ),
            "additional_collection": WorkflowNode(
                node_id="additional_collection",
                node_type=NodeType.TASK,
                name="Additional Collection",
                description="Collect additional intelligence if quality is insufficient",
                agent_type="osint",
                action="targeted_collection",
                timeout_seconds=1200
            ),
            "analysis": WorkflowNode(
                node_id="analysis",
                node_type=NodeType.TASK,
                name="Intelligence Analysis",
                description="Analyze and correlate collected intelligence",
                agent_type="data_analysis",
                action="analyze_intelligence",
                timeout_seconds=1800
            ),
            "reporting": WorkflowNode(
                node_id="reporting",
                node_type=NodeType.TASK,
                name="Generate Intelligence Report",
                description="Generate comprehensive intelligence report",
                agent_type="reporting",
                action="generate_intelligence_report",
                timeout_seconds=900
            ),
            "end": WorkflowNode(
                node_id="end",
                node_type=NodeType.END,
                name="Intelligence Collection Complete"
            )
        }
        
        # Add nodes to workflow
        workflow.nodes = nodes
        
        # Define edges (workflow flow)
        edges = {
            "start_to_assess": WorkflowEdge(
                edge_id="start_to_assess",
                from_node="start",
                to_node="assess_target",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "assess_to_parallel": WorkflowEdge(
                edge_id="assess_to_parallel",
                from_node="assess_target",
                to_node="parallel_collection",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "parallel_to_osint": WorkflowEdge(
                edge_id="parallel_to_osint",
                from_node="parallel_collection",
                to_node="osint_collection",
                edge_type=EdgeType.PARALLEL
            ),
            "parallel_to_social": WorkflowEdge(
                edge_id="parallel_to_social",
                from_node="parallel_collection",
                to_node="social_monitoring",
                edge_type=EdgeType.PARALLEL
            ),
            "parallel_to_threat": WorkflowEdge(
                edge_id="parallel_to_threat",
                from_node="parallel_collection",
                to_node="threat_scanning",
                edge_type=EdgeType.PARALLEL
            ),
            "osint_to_merge": WorkflowEdge(
                edge_id="osint_to_merge",
                from_node="osint_collection",
                to_node="merge_collection",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "social_to_merge": WorkflowEdge(
                edge_id="social_to_merge",
                from_node="social_monitoring",
                to_node="merge_collection",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "threat_to_merge": WorkflowEdge(
                edge_id="threat_to_merge",
                from_node="threat_scanning",
                to_node="merge_collection",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "merge_to_quality": WorkflowEdge(
                edge_id="merge_to_quality",
                from_node="merge_collection",
                to_node="quality_check",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "quality_to_additional": WorkflowEdge(
                edge_id="quality_to_additional",
                from_node="quality_check",
                to_node="additional_collection",
                edge_type=EdgeType.CONDITIONAL,
                condition="quality_insufficient"
            ),
            "quality_to_analysis": WorkflowEdge(
                edge_id="quality_to_analysis",
                from_node="quality_check",
                to_node="analysis",
                edge_type=EdgeType.CONDITIONAL,
                condition="quality_sufficient"
            ),
            "additional_to_analysis": WorkflowEdge(
                edge_id="additional_to_analysis",
                from_node="additional_collection",
                to_node="analysis",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "analysis_to_reporting": WorkflowEdge(
                edge_id="analysis_to_reporting",
                from_node="analysis",
                to_node="reporting",
                edge_type=EdgeType.SEQUENTIAL
            ),
            "reporting_to_end": WorkflowEdge(
                edge_id="reporting_to_end",
                from_node="reporting",
                to_node="end",
                edge_type=EdgeType.SEQUENTIAL
            )
        }
        
        workflow.edges = edges
        
        return workflow
    
    def _create_threat_assessment_workflow(self) -> WorkflowDefinition:
        """Create threat assessment workflow with iterative analysis"""
        workflow = WorkflowDefinition(
            workflow_id="threat_assessment_v2",
            name="Advanced Threat Assessment",
            description="Comprehensive threat assessment with iterative refinement",
            version="2.0",
            timeout_minutes=90
        )
        
        # Define nodes for threat assessment
        nodes = {
            "start": WorkflowNode(
                node_id="start",
                node_type=NodeType.START,
                name="Start Threat Assessment"
            ),
            "initial_scan": WorkflowNode(
                node_id="initial_scan",
                node_type=NodeType.TASK,
                name="Initial Threat Scan",
                agent_type="osint",
                action="scan_threats",
                timeout_seconds=600
            ),
            "threat_analysis": WorkflowNode(
                node_id="threat_analysis",
                node_type=NodeType.TASK,
                name="Threat Analysis",
                agent_type="data_analysis",
                action="analyze_threats",
                timeout_seconds=900
            ),
            "risk_scoring": WorkflowNode(
                node_id="risk_scoring",
                node_type=NodeType.TASK,
                name="Risk Scoring",
                agent_type="data_analysis",
                action="calculate_risk_score",
                timeout_seconds=300
            ),
            "confidence_check": WorkflowNode(
                node_id="confidence_check",
                node_type=NodeType.DECISION,
                name="Confidence Assessment",
                conditions={
                    "min_confidence": 0.8,
                    "min_threat_sources": 2
                }
            ),
            "deep_analysis": WorkflowNode(
                node_id="deep_analysis",
                node_type=NodeType.TASK,
                name="Deep Threat Analysis",
                agent_type="investigation",
                action="deep_threat_investigation",
                timeout_seconds=1800
            ),
            "final_assessment": WorkflowNode(
                node_id="final_assessment",
                node_type=NodeType.TASK,
                name="Final Threat Assessment",
                agent_type="reporting",
                action="generate_threat_report",
                timeout_seconds=600
            ),
            "end": WorkflowNode(
                node_id="end",
                node_type=NodeType.END,
                name="Threat Assessment Complete"
            )
        }
        
        workflow.nodes = nodes
        
        # Define edges with conditional logic
        edges = {
            "start_to_scan": WorkflowEdge("start_to_scan", "start", "initial_scan", EdgeType.SEQUENTIAL),
            "scan_to_analysis": WorkflowEdge("scan_to_analysis", "initial_scan", "threat_analysis", EdgeType.SEQUENTIAL),
            "analysis_to_scoring": WorkflowEdge("analysis_to_scoring", "threat_analysis", "risk_scoring", EdgeType.SEQUENTIAL),
            "scoring_to_confidence": WorkflowEdge("scoring_to_confidence", "risk_scoring", "confidence_check", EdgeType.SEQUENTIAL),
            "confidence_to_deep": WorkflowEdge(
                "confidence_to_deep", "confidence_check", "deep_analysis", 
                EdgeType.CONDITIONAL, condition="low_confidence"
            ),
            "confidence_to_final": WorkflowEdge(
                "confidence_to_final", "confidence_check", "final_assessment", 
                EdgeType.CONDITIONAL, condition="high_confidence"
            ),
            "deep_to_final": WorkflowEdge("deep_to_final", "deep_analysis", "final_assessment", EdgeType.SEQUENTIAL),
            "final_to_end": WorkflowEdge("final_to_end", "final_assessment", "end", EdgeType.SEQUENTIAL)
        }
        
        workflow.edges = edges
        
        return workflow
    
    def _create_investigation_workflow(self) -> WorkflowDefinition:
        """Create investigation workflow with loops and branching"""
        workflow = WorkflowDefinition(
            workflow_id="investigation_v2",
            name="Advanced Investigation Workflow",
            description="Comprehensive investigation with iterative evidence gathering",
            version="2.0",
            timeout_minutes=180
        )
        
        # Investigation workflow nodes
        nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start Investigation"),
            "evidence_collection": WorkflowNode(
                "evidence_collection", NodeType.TASK, "Evidence Collection",
                agent_type="forensics", action="collect_evidence", timeout_seconds=1800
            ),
            "evidence_analysis": WorkflowNode(
                "evidence_analysis", NodeType.TASK, "Evidence Analysis",
                agent_type="forensics", action="analyze_evidence", timeout_seconds=1200
            ),
            "timeline_construction": WorkflowNode(
                "timeline_construction", NodeType.TASK, "Timeline Construction",
                agent_type="investigation", action="construct_timeline", timeout_seconds=900
            ),
            "hypothesis_generation": WorkflowNode(
                "hypothesis_generation", NodeType.TASK, "Hypothesis Generation",
                agent_type="investigation", action="generate_hypotheses", timeout_seconds=600
            ),
            "hypothesis_testing": WorkflowNode(
                "hypothesis_testing", NodeType.TASK, "Hypothesis Testing",
                agent_type="investigation", action="test_hypotheses", timeout_seconds=1200
            ),
            "evidence_gap_check": WorkflowNode(
                "evidence_gap_check", NodeType.DECISION, "Evidence Gap Assessment",
                conditions={"evidence_completeness": 0.8, "hypothesis_confidence": 0.7}
            ),
            "additional_evidence": WorkflowNode(
                "additional_evidence", NodeType.TASK, "Additional Evidence Collection",
                agent_type="forensics", action="targeted_evidence_collection", timeout_seconds=1200
            ),
            "final_analysis": WorkflowNode(
                "final_analysis", NodeType.TASK, "Final Investigation Analysis",
                agent_type="investigation", action="final_analysis", timeout_seconds=900
            ),
            "investigation_report": WorkflowNode(
                "investigation_report", NodeType.TASK, "Investigation Report",
                agent_type="reporting", action="generate_investigation_report", timeout_seconds=600
            ),
            "end": WorkflowNode("end", NodeType.END, "Investigation Complete")
        }
        
        workflow.nodes = nodes
        
        # Define edges with loops
        edges = {
            "start_to_evidence": WorkflowEdge("start_to_evidence", "start", "evidence_collection", EdgeType.SEQUENTIAL),
            "evidence_to_analysis": WorkflowEdge("evidence_to_analysis", "evidence_collection", "evidence_analysis", EdgeType.SEQUENTIAL),
            "analysis_to_timeline": WorkflowEdge("analysis_to_timeline", "evidence_analysis", "timeline_construction", EdgeType.SEQUENTIAL),
            "timeline_to_hypothesis": WorkflowEdge("timeline_to_hypothesis", "timeline_construction", "hypothesis_generation", EdgeType.SEQUENTIAL),
            "hypothesis_to_testing": WorkflowEdge("hypothesis_to_testing", "hypothesis_generation", "hypothesis_testing", EdgeType.SEQUENTIAL),
            "testing_to_gap_check": WorkflowEdge("testing_to_gap_check", "hypothesis_testing", "evidence_gap_check", EdgeType.SEQUENTIAL),
            "gap_to_additional": WorkflowEdge(
                "gap_to_additional", "evidence_gap_check", "additional_evidence", 
                EdgeType.CONDITIONAL, condition="evidence_insufficient"
            ),
            "additional_to_analysis": WorkflowEdge(
                "additional_to_analysis", "additional_evidence", "evidence_analysis", 
                EdgeType.LOOP_BACK  # Loop back for iterative evidence gathering
            ),
            "gap_to_final": WorkflowEdge(
                "gap_to_final", "evidence_gap_check", "final_analysis", 
                EdgeType.CONDITIONAL, condition="evidence_sufficient"
            ),
            "final_to_report": WorkflowEdge("final_to_report", "final_analysis", "investigation_report", EdgeType.SEQUENTIAL),
            "report_to_end": WorkflowEdge("report_to_end", "investigation_report", "end", EdgeType.SEQUENTIAL)
        }
        
        workflow.edges = edges
        
        return workflow
    
    def _create_forensics_workflow(self) -> WorkflowDefinition:
        """Create digital forensics workflow"""
        workflow = WorkflowDefinition(
            workflow_id="digital_forensics_v2",
            name="Digital Forensics Analysis",
            description="Comprehensive digital forensics with timeline reconstruction",
            version="2.0",
            timeout_minutes=240
        )
        
        # Forensics workflow nodes
        nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start Forensics Analysis"),
            "evidence_acquisition": WorkflowNode(
                "evidence_acquisition", NodeType.TASK, "Evidence Acquisition",
                agent_type="forensics", action="acquire_evidence", timeout_seconds=3600
            ),
            "evidence_validation": WorkflowNode(
                "evidence_validation", NodeType.TASK, "Evidence Validation",
                agent_type="forensics", action="validate_evidence", timeout_seconds=900
            ),
            "metadata_extraction": WorkflowNode(
                "metadata_extraction", NodeType.TASK, "Metadata Extraction",
                agent_type="metadata", action="extract_metadata", timeout_seconds=1800
            ),
            "timeline_reconstruction": WorkflowNode(
                "timeline_reconstruction", NodeType.TASK, "Timeline Reconstruction",
                agent_type="forensics", action="reconstruct_timeline", timeout_seconds=2400
            ),
            "artifact_analysis": WorkflowNode(
                "artifact_analysis", NodeType.TASK, "Artifact Analysis",
                agent_type="forensics", action="analyze_artifacts", timeout_seconds=3600
            ),
            "correlation_analysis": WorkflowNode(
                "correlation_analysis", NodeType.TASK, "Correlation Analysis",
                agent_type="investigation", action="correlate_findings", timeout_seconds=1800
            ),
            "forensics_report": WorkflowNode(
                "forensics_report", NodeType.TASK, "Forensics Report Generation",
                agent_type="reporting", action="generate_forensics_report", timeout_seconds=1200
            ),
            "end": WorkflowNode("end", NodeType.END, "Forensics Analysis Complete")
        }
        
        workflow.nodes = nodes
        
        # Sequential forensics workflow
        edges = {
            "start_to_acquisition": WorkflowEdge("start_to_acquisition", "start", "evidence_acquisition", EdgeType.SEQUENTIAL),
            "acquisition_to_validation": WorkflowEdge("acquisition_to_validation", "evidence_acquisition", "evidence_validation", EdgeType.SEQUENTIAL),
            "validation_to_metadata": WorkflowEdge("validation_to_metadata", "evidence_validation", "metadata_extraction", EdgeType.SEQUENTIAL),
            "metadata_to_timeline": WorkflowEdge("metadata_to_timeline", "metadata_extraction", "timeline_reconstruction", EdgeType.SEQUENTIAL),
            "timeline_to_artifacts": WorkflowEdge("timeline_to_artifacts", "timeline_reconstruction", "artifact_analysis", EdgeType.SEQUENTIAL),
            "artifacts_to_correlation": WorkflowEdge("artifacts_to_correlation", "artifact_analysis", "correlation_analysis", EdgeType.SEQUENTIAL),
            "correlation_to_report": WorkflowEdge("correlation_to_report", "correlation_analysis", "forensics_report", EdgeType.SEQUENTIAL),
            "report_to_end": WorkflowEdge("report_to_end", "forensics_report", "end", EdgeType.SEQUENTIAL)
        }
        
        workflow.edges = edges
        
        return workflow
    
    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a workflow definition"""
        try:
            # Validate workflow
            if not self._validate_workflow(workflow):
                logger.error(f"Workflow validation failed: {workflow.workflow_id}")
                return False
            
            self.workflow_definitions[workflow.workflow_id] = workflow
            logger.info(f"Workflow registered: {workflow.workflow_id} ({workflow.name})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering workflow: {e}")
            return False
    
    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        try:
            # Check for start and end nodes
            start_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.START]
            end_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.END]
            
            if len(start_nodes) != 1:
                logger.error(f"Workflow must have exactly one START node, found {len(start_nodes)}")
                return False
            
            if len(end_nodes) < 1:
                logger.error(f"Workflow must have at least one END node, found {len(end_nodes)}")
                return False
            
            # Check edge connectivity
            for edge in workflow.edges.values():
                if edge.from_node not in workflow.nodes:
                    logger.error(f"Edge references unknown from_node: {edge.from_node}")
                    return False
                
                if edge.to_node not in workflow.nodes:
                    logger.error(f"Edge references unknown to_node: {edge.to_node}")
                    return False
            
            # Check for graph connectivity using NetworkX
            G = nx.DiGraph()
            
            # Add nodes
            for node_id in workflow.nodes.keys():
                G.add_node(node_id)
            
            # Add edges
            for edge in workflow.edges.values():
                G.add_edge(edge.from_node, edge.to_node)
            
            # Check if all nodes are reachable from start
            start_node = start_nodes[0].node_id
            reachable = nx.descendants(G, start_node)
            reachable.add(start_node)
            
            unreachable_nodes = set(workflow.nodes.keys()) - reachable
            if unreachable_nodes:
                logger.warning(f"Unreachable nodes in workflow: {unreachable_nodes}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            return False
    
    async def execute_workflow(
        self,
        workflow_id: str,
        execution_context: Dict[str, Any],
        initiated_by: str,
        priority: int = 2
    ) -> str:
        """
        Execute a workflow with given context.
        
        Args:
            workflow_id: ID of workflow to execute
            execution_context: Context and parameters for execution
            initiated_by: User/agent initiating the workflow
            priority: Execution priority (1-5)
            
        Returns:
            Execution ID
        """
        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflow_definitions[workflow_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution instance
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.CREATED,
                execution_context=execution_context,
                initiated_by=initiated_by,
                priority=priority
            )
            
            # Initialize node statuses
            for node_id in workflow.nodes.keys():
                if workflow.nodes[node_id].node_type == NodeType.START:
                    execution.current_nodes.add(node_id)
                    workflow.nodes[node_id].status = NodeStatus.READY
                else:
                    workflow.nodes[node_id].status = NodeStatus.PENDING
            
            # Store execution
            self.active_executions[execution_id] = execution
            
            # Add to execution queue
            await self.execution_queue.put((priority, time.time(), execution_id))
            
            # Update metrics
            self.workflow_metrics['total_workflows'] += 1
            self.workflow_metrics['active_executions'] = len(self.active_executions)
            
            logger.info(f"Workflow execution started: {execution_id} ({workflow.name})")
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise
    
    async def _execution_processor(self):
        """Background task to process workflow executions"""
        while self._running:
            try:
                # Get next execution from queue
                try:
                    priority, timestamp, execution_id = await asyncio.wait_for(
                        self.execution_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                if execution_id not in self.active_executions:
                    continue
                
                execution = self.active_executions[execution_id]
                workflow = self.workflow_definitions[execution.workflow_id]
                
                # Update execution status
                if execution.status == WorkflowStatus.CREATED:
                    execution.status = WorkflowStatus.RUNNING
                
                # Process ready nodes
                await self._process_ready_nodes(execution, workflow)
                
                # Check if workflow is complete
                if await self._is_workflow_complete(execution, workflow):
                    await self._complete_workflow_execution(execution_id)
                elif execution.status == WorkflowStatus.RUNNING:
                    # Re-queue for continued processing
                    await self.execution_queue.put((priority, time.time(), execution_id))
                
            except Exception as e:
                logger.error(f"Error in execution processor: {e}")
                await asyncio.sleep(1)
    
    async def _process_ready_nodes(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition
    ):
        """Process nodes that are ready for execution"""
        try:
            ready_nodes = []
            
            for node_id in execution.current_nodes:
                node = workflow.nodes[node_id]
                if node.status == NodeStatus.READY:
                    ready_nodes.append(node)
            
            if not ready_nodes:
                return
            
            # Execute ready nodes (potentially in parallel)
            execution_tasks = []
            for node in ready_nodes:
                if node.node_type in [NodeType.TASK, NodeType.DECISION, NodeType.CONDITION]:
                    task = asyncio.create_task(
                        self._execute_node(execution, workflow, node)
                    )
                    execution_tasks.append(task)
                elif node.node_type == NodeType.PARALLEL:
                    await self._handle_parallel_node(execution, workflow, node)
                elif node.node_type == NodeType.MERGE:
                    await self._handle_merge_node(execution, workflow, node)
                elif node.node_type in [NodeType.START, NodeType.END]:
                    await self._handle_control_node(execution, workflow, node)
            
            # Wait for task nodes to complete
            if execution_tasks:
                await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Update workflow state after node execution
            await self._update_workflow_state(execution, workflow)
            
        except Exception as e:
            logger.error(f"Error processing ready nodes: {e}")
    
    async def _execute_node(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ):
        """Execute a single workflow node"""
        try:
            node.status = NodeStatus.RUNNING
            node.started_at = datetime.utcnow()
            start_time = time.time()
            
            logger.info(f"Executing node {node.node_id} ({node.name}) in workflow {execution.execution_id}")
            
            if node.node_type == NodeType.TASK:
                result = await self._execute_task_node(execution, node)
            elif node.node_type == NodeType.DECISION:
                result = await self._execute_decision_node(execution, node)
            elif node.node_type == NodeType.CONDITION:
                result = await self._execute_condition_node(execution, node)
            else:
                result = {'success': True, 'message': f'Node {node.node_id} processed'}
            
            # Update node status
            node.result = result
            node.completed_at = datetime.utcnow()
            node.execution_time = time.time() - start_time
            
            if result.get('success', False):
                node.status = NodeStatus.COMPLETED
                execution.completed_nodes.add(node.node_id)
                execution.node_results[node.node_id] = result
            else:
                node.status = NodeStatus.FAILED
                node.error = result.get('error', 'Unknown error')
                execution.failed_nodes.add(node.node_id)
                
                # Handle node failure
                await self._handle_node_failure(execution, workflow, node)
            
            # Remove from current nodes
            execution.current_nodes.discard(node.node_id)
            
            # Update metrics
            await self._update_node_metrics(node)
            
        except Exception as e:
            logger.error(f"Error executing node {node.node_id}: {e}")
            node.status = NodeStatus.FAILED
            node.error = str(e)
            execution.failed_nodes.add(node.node_id)
            execution.current_nodes.discard(node.node_id)
    
    async def _execute_task_node(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a task node using appropriate agent"""
        try:
            if not self.amas_system:
                return {'success': False, 'error': 'AMAS system not available'}
            
            agent_type = node.agent_type
            if not agent_type:
                return {'success': False, 'error': 'No agent type specified for task node'}
            
            # Find appropriate agent
            suitable_agent = None
            for agent_id, agent in self.amas_system.agents.items():
                if agent_type in agent.capabilities or any(
                    agent_type in cap.lower() for cap in agent.capabilities
                ):
                    suitable_agent = agent
                    break
            
            if not suitable_agent:
                return {'success': False, 'error': f'No suitable agent found for type: {agent_type}'}
            
            # Prepare task data
            task_data = {
                'id': f"{execution.execution_id}_{node.node_id}",
                'type': agent_type,
                'description': node.description or f"Execute {node.name}",
                'parameters': {
                    **node.parameters,
                    **execution.execution_context,
                    'workflow_context': {
                        'execution_id': execution.execution_id,
                        'node_id': node.node_id,
                        'workflow_id': execution.workflow_id
                    }
                }
            }
            
            # Execute task with timeout
            if node.timeout_seconds:
                result = await asyncio.wait_for(
                    suitable_agent.process_task(task_data),
                    timeout=node.timeout_seconds
                )
            else:
                result = await suitable_agent.process_task(task_data)
            
            return result
            
        except asyncio.TimeoutError:
            return {'success': False, 'error': f'Task timeout after {node.timeout_seconds} seconds'}
        except Exception as e:
            logger.error(f"Error executing task node {node.node_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_decision_node(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a decision node with condition evaluation"""
        try:
            # Evaluate conditions based on previous results
            decision_result = await self._evaluate_node_conditions(execution, node)
            
            return {
                'success': True,
                'decision': decision_result,
                'conditions_met': decision_result,
                'evaluation_details': node.conditions
            }
            
        except Exception as e:
            logger.error(f"Error executing decision node {node.node_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _evaluate_node_conditions(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> bool:
        """Evaluate conditions for decision nodes"""
        try:
            conditions = node.conditions
            if not conditions:
                return True
            
            # Get previous results for evaluation
            previous_results = execution.node_results
            
            # Evaluate each condition
            for condition_key, condition_value in conditions.items():
                if condition_key == "min_confidence":
                    # Check if minimum confidence is met
                    confidences = []
                    for result in previous_results.values():
                        if isinstance(result, dict) and 'confidence' in result:
                            confidences.append(result['confidence'])
                    
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        if avg_confidence < condition_value:
                            return False
                
                elif condition_key == "min_sources":
                    # Check if minimum number of sources
                    source_count = 0
                    for result in previous_results.values():
                        if isinstance(result, dict) and 'sources' in result:
                            source_count += len(result['sources'])
                    
                    if source_count < condition_value:
                        return False
                
                elif condition_key == "completeness_threshold":
                    # Check data completeness
                    completeness_scores = []
                    for result in previous_results.values():
                        if isinstance(result, dict) and 'completeness' in result:
                            completeness_scores.append(result['completeness'])
                    
                    if completeness_scores:
                        avg_completeness = sum(completeness_scores) / len(completeness_scores)
                        if avg_completeness < condition_value:
                            return False
            
            return True  # All conditions met
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    async def _update_workflow_state(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition
    ):
        """Update workflow state after node execution"""
        try:
            # Find next nodes to execute based on completed nodes
            next_nodes = set()
            
            for completed_node_id in list(execution.current_nodes):
                node = workflow.nodes.get(completed_node_id)
                if not node or node.status != NodeStatus.COMPLETED:
                    continue
                
                # Find outgoing edges
                for edge in workflow.edges.values():
                    if edge.from_node == completed_node_id:
                        # Check edge conditions
                        if await self._should_traverse_edge(execution, workflow, edge):
                            target_node = workflow.nodes[edge.to_node]
                            
                            # Check if target node is ready
                            if await self._is_node_ready(execution, workflow, target_node):
                                target_node.status = NodeStatus.READY
                                next_nodes.add(edge.to_node)
            
            # Update current nodes
            execution.current_nodes.update(next_nodes)
            
        except Exception as e:
            logger.error(f"Error updating workflow state: {e}")
    
    async def _should_traverse_edge(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        edge: WorkflowEdge
    ) -> bool:
        """Determine if an edge should be traversed"""
        try:
            if edge.edge_type == EdgeType.SEQUENTIAL:
                return True
            elif edge.edge_type == EdgeType.CONDITIONAL:
                return await self._evaluate_edge_condition(execution, edge)
            elif edge.edge_type == EdgeType.PARALLEL:
                return True
            elif edge.edge_type == EdgeType.LOOP_BACK:
                return await self._evaluate_loop_condition(execution, edge)
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error evaluating edge traversal: {e}")
            return False
    
    async def _evaluate_edge_condition(
        self,
        execution: WorkflowExecution,
        edge: WorkflowEdge
    ) -> bool:
        """Evaluate condition for conditional edges"""
        try:
            condition = edge.condition
            if not condition:
                return True
            
            # Built-in condition evaluators
            if condition == "quality_sufficient":
                return await self._evaluate_quality_condition(execution, edge)
            elif condition == "quality_insufficient":
                return not await self._evaluate_quality_condition(execution, edge)
            elif condition == "high_confidence":
                return await self._evaluate_confidence_condition(execution, edge, threshold=0.8)
            elif condition == "low_confidence":
                return not await self._evaluate_confidence_condition(execution, edge, threshold=0.8)
            elif condition == "evidence_sufficient":
                return await self._evaluate_evidence_condition(execution, edge)
            elif condition == "evidence_insufficient":
                return not await self._evaluate_evidence_condition(execution, edge)
            else:
                # Custom condition evaluator
                evaluator = self.condition_evaluators.get(condition)
                if evaluator:
                    return await evaluator(execution, edge)
                else:
                    logger.warning(f"Unknown condition: {condition}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error evaluating edge condition: {e}")
            return False
    
    async def _evaluate_quality_condition(
        self,
        execution: WorkflowExecution,
        edge: WorkflowEdge
    ) -> bool:
        """Evaluate quality-based conditions"""
        try:
            # Check confidence and completeness from previous results
            confidences = []
            completeness_scores = []
            
            for result in execution.node_results.values():
                if isinstance(result, dict):
                    if 'confidence' in result:
                        confidences.append(result['confidence'])
                    if 'completeness' in result:
                        completeness_scores.append(result['completeness'])
            
            # Quality is sufficient if both confidence and completeness are high
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
            avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.5
            
            quality_score = (avg_confidence + avg_completeness) / 2
            return quality_score >= 0.7
            
        except Exception as e:
            logger.error(f"Error evaluating quality condition: {e}")
            return False
    
    async def _evaluate_confidence_condition(
        self,
        execution: WorkflowExecution,
        edge: WorkflowEdge,
        threshold: float
    ) -> bool:
        """Evaluate confidence-based conditions"""
        try:
            confidences = []
            
            for result in execution.node_results.values():
                if isinstance(result, dict) and 'confidence' in result:
                    confidences.append(result['confidence'])
            
            if not confidences:
                return False
            
            avg_confidence = sum(confidences) / len(confidences)
            return avg_confidence >= threshold
            
        except Exception as e:
            logger.error(f"Error evaluating confidence condition: {e}")
            return False
    
    async def _evaluate_evidence_condition(
        self,
        execution: WorkflowExecution,
        edge: WorkflowEdge
    ) -> bool:
        """Evaluate evidence sufficiency conditions"""
        try:
            evidence_count = 0
            evidence_quality = 0.0
            
            for result in execution.node_results.values():
                if isinstance(result, dict):
                    if 'evidence' in result:
                        evidence_items = result['evidence']
                        if isinstance(evidence_items, list):
                            evidence_count += len(evidence_items)
                    if 'evidence_quality' in result:
                        evidence_quality = max(evidence_quality, result['evidence_quality'])
            
            # Evidence is sufficient if we have enough items with good quality
            return evidence_count >= 3 and evidence_quality >= 0.6
            
        except Exception as e:
            logger.error(f"Error evaluating evidence condition: {e}")
            return False
    
    async def _is_node_ready(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ) -> bool:
        """Check if a node is ready for execution"""
        try:
            if node.node_type in [NodeType.START]:
                return True
            
            # Check if all prerequisite nodes are completed
            prerequisite_edges = [
                edge for edge in workflow.edges.values()
                if edge.to_node == node.node_id
            ]
            
            for edge in prerequisite_edges:
                from_node = workflow.nodes[edge.from_node]
                
                # For sequential edges, from_node must be completed
                if edge.edge_type == EdgeType.SEQUENTIAL:
                    if from_node.status != NodeStatus.COMPLETED:
                        return False
                
                # For parallel edges, check merge conditions
                elif edge.edge_type == EdgeType.PARALLEL:
                    # Parallel nodes can start immediately
                    continue
                
                # For conditional edges, evaluate conditions
                elif edge.edge_type == EdgeType.CONDITIONAL:
                    if from_node.status != NodeStatus.COMPLETED:
                        return False
                    # Condition evaluation happens in edge traversal
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking node readiness: {e}")
            return False
    
    async def _handle_parallel_node(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ):
        """Handle parallel execution node"""
        try:
            # Find all outgoing parallel edges
            parallel_edges = [
                edge for edge in workflow.edges.values()
                if edge.from_node == node.node_id and edge.edge_type == EdgeType.PARALLEL
            ]
            
            # Mark target nodes as ready
            for edge in parallel_edges:
                target_node = workflow.nodes[edge.to_node]
                target_node.status = NodeStatus.READY
                execution.current_nodes.add(edge.to_node)
            
            # Mark parallel node as completed
            node.status = NodeStatus.COMPLETED
            execution.completed_nodes.add(node.node_id)
            execution.current_nodes.discard(node.node_id)
            
            logger.info(f"Parallel node {node.node_id} initiated {len(parallel_edges)} parallel branches")
            
        except Exception as e:
            logger.error(f"Error handling parallel node: {e}")
    
    async def _handle_merge_node(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ):
        """Handle merge node (synchronization point)"""
        try:
            # Find all incoming edges
            incoming_edges = [
                edge for edge in workflow.edges.values()
                if edge.to_node == node.node_id
            ]
            
            # Check if all prerequisite nodes are completed
            all_completed = True
            for edge in incoming_edges:
                from_node = workflow.nodes[edge.from_node]
                if from_node.status != NodeStatus.COMPLETED:
                    all_completed = False
                    break
            
            if all_completed:
                # Merge results from all incoming nodes
                merged_result = {}
                for edge in incoming_edges:
                    from_node_id = edge.from_node
                    if from_node_id in execution.node_results:
                        merged_result[from_node_id] = execution.node_results[from_node_id]
                
                node.result = {
                    'success': True,
                    'merged_results': merged_result,
                    'merge_count': len(merged_result)
                }
                node.status = NodeStatus.COMPLETED
                execution.completed_nodes.add(node.node_id)
                execution.node_results[node.node_id] = node.result
                execution.current_nodes.discard(node.node_id)
                
                logger.info(f"Merge node {node.node_id} synchronized {len(incoming_edges)} branches")
            else:
                # Not ready yet, keep waiting
                node.status = NodeStatus.WAITING
            
        except Exception as e:
            logger.error(f"Error handling merge node: {e}")
    
    async def _handle_control_node(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ):
        """Handle control nodes (START, END)"""
        try:
            if node.node_type == NodeType.START:
                node.status = NodeStatus.COMPLETED
                execution.completed_nodes.add(node.node_id)
                execution.current_nodes.discard(node.node_id)
                
                # Find next nodes
                next_edges = [
                    edge for edge in workflow.edges.values()
                    if edge.from_node == node.node_id
                ]
                
                for edge in next_edges:
                    target_node = workflow.nodes[edge.to_node]
                    target_node.status = NodeStatus.READY
                    execution.current_nodes.add(edge.to_node)
                
            elif node.node_type == NodeType.END:
                node.status = NodeStatus.COMPLETED
                execution.completed_nodes.add(node.node_id)
                execution.current_nodes.discard(node.node_id)
                
                # Mark workflow as completed
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                
                logger.info(f"Workflow {execution.execution_id} reached end node")
            
        except Exception as e:
            logger.error(f"Error handling control node: {e}")
    
    async def _is_workflow_complete(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition
    ) -> bool:
        """Check if workflow execution is complete"""
        try:
            # Check if any END node is reached
            for node_id in execution.completed_nodes:
                node = workflow.nodes[node_id]
                if node.node_type == NodeType.END:
                    return True
            
            # Check if no more nodes to execute
            if not execution.current_nodes:
                # No more nodes to execute - check if this is normal completion
                end_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.END]
                if any(n.node_id in execution.completed_nodes for n in end_nodes):
                    return True
                else:
                    # Workflow stuck - mark as failed
                    execution.status = WorkflowStatus.FAILED
                    execution.error = "Workflow execution stuck with no ready nodes"
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking workflow completion: {e}")
            return True  # Assume complete on error to prevent infinite execution
    
    async def _complete_workflow_execution(self, execution_id: str):
        """Complete a workflow execution"""
        try:
            if execution_id not in self.active_executions:
                return
            
            execution = self.active_executions[execution_id]
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - execution.started_at).total_seconds()
            
            # Update metrics
            if execution.status == WorkflowStatus.COMPLETED:
                self.workflow_metrics['successful_executions'] += 1
            else:
                self.workflow_metrics['failed_executions'] += 1
            
            # Update average execution time
            current_avg = self.workflow_metrics['average_execution_time']
            total_executions = (self.workflow_metrics['successful_executions'] + 
                             self.workflow_metrics['failed_executions'])
            
            self.workflow_metrics['average_execution_time'] = (
                (current_avg * (total_executions - 1) + execution_time) / total_executions
            )
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            # Update active executions count
            self.workflow_metrics['active_executions'] = len(self.active_executions)
            
            # Maintain history size
            if len(self.execution_history) > self.max_execution_history:
                self.execution_history = self.execution_history[-self.max_execution_history:]
            
            logger.info(f"Workflow execution completed: {execution_id} "
                       f"(status: {execution.status.value}, time: {execution_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"Error completing workflow execution: {e}")
    
    def _initialize_node_executors(self):
        """Initialize node executors for different node types"""
        self.node_executors = {
            NodeType.TASK.value: self._execute_task_node,
            NodeType.DECISION.value: self._execute_decision_node,
            NodeType.CONDITION.value: self._execute_condition_node,
            NodeType.DELAY.value: self._execute_delay_node,
            NodeType.SUBPROCESS.value: self._execute_subprocess_node
        }
    
    def _initialize_condition_evaluators(self):
        """Initialize condition evaluators"""
        self.condition_evaluators = {
            'quality_sufficient': self._evaluate_quality_condition,
            'confidence_high': lambda exec, edge: self._evaluate_confidence_condition(exec, edge, 0.8),
            'confidence_low': lambda exec, edge: not self._evaluate_confidence_condition(exec, edge, 0.8),
            'evidence_sufficient': self._evaluate_evidence_condition
        }
    
    async def _execute_condition_node(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a condition node"""
        # Similar to decision node but with different semantics
        return await self._execute_decision_node(execution, node)
    
    async def _execute_delay_node(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a delay node"""
        try:
            delay_seconds = node.parameters.get('delay_seconds', 60)
            await asyncio.sleep(delay_seconds)
            
            return {
                'success': True,
                'delay_seconds': delay_seconds,
                'message': f'Delayed execution for {delay_seconds} seconds'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_subprocess_node(
        self,
        execution: WorkflowExecution,
        node: WorkflowNode
    ) -> Dict[str, Any]:
        """Execute a subprocess node (nested workflow)"""
        try:
            subprocess_workflow_id = node.parameters.get('workflow_id')
            if not subprocess_workflow_id:
                return {'success': False, 'error': 'No subprocess workflow_id specified'}
            
            # Execute nested workflow
            subprocess_execution_id = await self.execute_workflow(
                workflow_id=subprocess_workflow_id,
                execution_context=execution.execution_context,
                initiated_by=f"subprocess_{execution.execution_id}",
                priority=execution.priority
            )
            
            # Wait for subprocess completion (simplified)
            subprocess_result = await self._wait_for_execution(subprocess_execution_id, timeout=3600)
            
            return {
                'success': True,
                'subprocess_execution_id': subprocess_execution_id,
                'subprocess_result': subprocess_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _wait_for_execution(
        self,
        execution_id: str,
        timeout: int = 3600
    ) -> Dict[str, Any]:
        """Wait for workflow execution to complete"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if execution_id in self.active_executions:
                    execution = self.active_executions[execution_id]
                    if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                        return {
                            'status': execution.status.value,
                            'results': execution.node_results,
                            'error': execution.error
                        }
                else:
                    # Execution moved to history
                    for historical_execution in reversed(self.execution_history):
                        if historical_execution.execution_id == execution_id:
                            return {
                                'status': historical_execution.status.value,
                                'results': historical_execution.node_results,
                                'error': historical_execution.error
                            }
                
                await asyncio.sleep(1)
            
            return {'status': 'timeout', 'error': f'Execution timeout after {timeout} seconds'}
            
        except Exception as e:
            logger.error(f"Error waiting for execution: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow execution"""
        try:
            # Check active executions
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                workflow = self.workflow_definitions[execution.workflow_id]
                
                return {
                    'execution_id': execution_id,
                    'workflow_id': execution.workflow_id,
                    'workflow_name': workflow.name,
                    'status': execution.status.value,
                    'progress': {
                        'total_nodes': len(workflow.nodes),
                        'completed_nodes': len(execution.completed_nodes),
                        'failed_nodes': len(execution.failed_nodes),
                        'current_nodes': list(execution.current_nodes),
                        'completion_percentage': (len(execution.completed_nodes) / len(workflow.nodes)) * 100
                    },
                    'started_at': execution.started_at.isoformat(),
                    'execution_time': (datetime.utcnow() - execution.started_at).total_seconds(),
                    'initiated_by': execution.initiated_by,
                    'error': execution.error,
                    'node_results': execution.node_results
                }
            
            # Check execution history
            for historical_execution in reversed(self.execution_history):
                if historical_execution.execution_id == execution_id:
                    workflow = self.workflow_definitions[historical_execution.workflow_id]
                    execution_time = 0.0
                    if historical_execution.completed_at:
                        execution_time = (historical_execution.completed_at - historical_execution.started_at).total_seconds()
                    
                    return {
                        'execution_id': execution_id,
                        'workflow_id': historical_execution.workflow_id,
                        'workflow_name': workflow.name,
                        'status': historical_execution.status.value,
                        'progress': {
                            'total_nodes': len(workflow.nodes),
                            'completed_nodes': len(historical_execution.completed_nodes),
                            'failed_nodes': len(historical_execution.failed_nodes),
                            'completion_percentage': (len(historical_execution.completed_nodes) / len(workflow.nodes)) * 100
                        },
                        'started_at': historical_execution.started_at.isoformat(),
                        'completed_at': historical_execution.completed_at.isoformat() if historical_execution.completed_at else None,
                        'execution_time': execution_time,
                        'initiated_by': historical_execution.initiated_by,
                        'error': historical_execution.error,
                        'node_results': historical_execution.node_results
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return None
    
    async def cancel_execution(
        self,
        execution_id: str,
        reason: str = "User cancellation"
    ) -> bool:
        """Cancel an active workflow execution"""
        try:
            if execution_id not in self.active_executions:
                logger.warning(f"Execution {execution_id} not found for cancellation")
                return False
            
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.error = f"Cancelled: {reason}"
            execution.completed_at = datetime.utcnow()
            
            # Cancel any running nodes
            workflow = self.workflow_definitions[execution.workflow_id]
            for node_id in execution.current_nodes:
                node = workflow.nodes[node_id]
                if node.status == NodeStatus.RUNNING:
                    node.status = NodeStatus.CANCELLED
            
            logger.info(f"Workflow execution cancelled: {execution_id} ({reason})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling execution: {e}")
            return False
    
    # Background monitoring tasks
    async def _timeout_monitor(self):
        """Monitor for workflow and node timeouts"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                
                for execution_id, execution in list(self.active_executions.items()):
                    workflow = self.workflow_definitions[execution.workflow_id]
                    
                    # Check workflow timeout
                    if workflow.timeout_minutes:
                        timeout_threshold = execution.started_at + timedelta(minutes=workflow.timeout_minutes)
                        if current_time > timeout_threshold:
                            execution.status = WorkflowStatus.TIMEOUT
                            execution.error = f"Workflow timeout after {workflow.timeout_minutes} minutes"
                            await self._complete_workflow_execution(execution_id)
                            continue
                    
                    # Check node timeouts
                    for node_id in execution.current_nodes:
                        node = workflow.nodes[node_id]
                        if (node.status == NodeStatus.RUNNING and 
                            node.timeout_seconds and 
                            node.started_at):
                            
                            timeout_threshold = node.started_at + timedelta(seconds=node.timeout_seconds)
                            if current_time > timeout_threshold:
                                node.status = NodeStatus.FAILED
                                node.error = f"Node timeout after {node.timeout_seconds} seconds"
                                execution.failed_nodes.add(node_id)
                                execution.current_nodes.discard(node_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in timeout monitor: {e}")
                await asyncio.sleep(60)
    
    async def _performance_monitor(self):
        """Monitor workflow performance metrics"""
        while self._running:
            try:
                # Log performance metrics
                metrics = self.workflow_metrics
                logger.info(f"Workflow Engine Performance: {metrics['active_executions']} active, "
                          f"{metrics['successful_executions']} successful, "
                          f"{metrics['failed_executions']} failed, "
                          f"{metrics['average_execution_time']:.2f}s avg time")
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_completed_executions(self):
        """Clean up old completed executions"""
        while self._running:
            try:
                # Move old active executions to history if they're stuck
                current_time = datetime.utcnow()
                stuck_executions = []
                
                for execution_id, execution in self.active_executions.items():
                    # If execution has been running for more than 4 hours, consider it stuck
                    if current_time - execution.started_at > timedelta(hours=4):
                        if execution.status == WorkflowStatus.RUNNING:
                            execution.status = WorkflowStatus.FAILED
                            execution.error = "Execution appears stuck, moved to history"
                            stuck_executions.append(execution_id)
                
                for execution_id in stuck_executions:
                    await self._complete_workflow_execution(execution_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(3600)
    
    async def _update_node_metrics(self, node: WorkflowNode):
        """Update performance metrics for node execution"""
        try:
            node_type = node.node_type.value
            stats = self.workflow_metrics['node_execution_stats'][node_type]
            
            # Update count
            stats['count'] += 1
            
            # Update average time
            if node.execution_time > 0:
                current_avg = stats['avg_time']
                count = stats['count']
                stats['avg_time'] = ((current_avg * (count - 1)) + node.execution_time) / count
            
            # Update success rate
            if node.status == NodeStatus.COMPLETED:
                current_success_rate = stats['success_rate']
                stats['success_rate'] = ((current_success_rate * (stats['count'] - 1)) + 1.0) / stats['count']
            else:
                current_success_rate = stats['success_rate']
                stats['success_rate'] = (current_success_rate * (stats['count'] - 1)) / stats['count']
            
        except Exception as e:
            logger.error(f"Error updating node metrics: {e}")
    
    async def _handle_node_failure(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition,
        node: WorkflowNode
    ):
        """Handle node execution failure"""
        try:
            # Check if node has retry attempts left
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                node.status = NodeStatus.READY
                execution.current_nodes.add(node.node_id)
                execution.failed_nodes.discard(node.node_id)
                
                logger.info(f"Retrying failed node {node.node_id} (attempt {node.retry_count}/{node.max_retries})")
                return
            
            # Check for error handler edges
            error_edges = [
                edge for edge in workflow.edges.values()
                if edge.from_node == node.node_id and edge.edge_type == EdgeType.ERROR_HANDLER
            ]
            
            if error_edges:
                # Route to error handler
                for edge in error_edges:
                    target_node = workflow.nodes[edge.to_node]
                    target_node.status = NodeStatus.READY
                    execution.current_nodes.add(edge.to_node)
                
                logger.info(f"Node {node.node_id} failure routed to error handler")
            else:
                # No error handler - workflow fails
                execution.status = WorkflowStatus.FAILED
                execution.error = f"Node {node.node_id} failed: {node.error}"
                
                logger.error(f"Workflow {execution.execution_id} failed due to node {node.node_id}")
            
        except Exception as e:
            logger.error(f"Error handling node failure: {e}")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow engine status"""
        try:
            return {
                'engine_status': 'active' if self._running else 'inactive',
                'registered_workflows': len(self.workflow_definitions),
                'active_executions': len(self.active_executions),
                'execution_history_size': len(self.execution_history),
                'metrics': self.workflow_metrics,
                'configuration': {
                    'max_concurrent_executions': self.max_concurrent_executions,
                    'default_timeout_minutes': self.default_timeout_minutes,
                    'max_execution_history': self.max_execution_history
                },
                'workflows': [
                    {
                        'workflow_id': wf.workflow_id,
                        'name': wf.name,
                        'version': wf.version,
                        'node_count': len(wf.nodes),
                        'edge_count': len(wf.edges)
                    }
                    for wf in self.workflow_definitions.values()
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting engine status: {e}")
            return {'error': str(e)}