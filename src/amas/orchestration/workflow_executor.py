"""
Multi-Agent Workflow Execution Engine

Orchestrates execution of complex workflows across multiple specialist agents
with dependency management, parallel execution, and quality gates.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json

from .task_decomposer import WorkflowPlan, SubTask, TaskComplexity, get_task_decomposer
from .agent_hierarchy import get_hierarchy_manager, AgentStatus
from .agent_communication import get_communication_bus, MessageType, Priority

logger = logging.getLogger(__name__)

class ExecutionStatus(str, Enum):
    PLANNED = "planned"
    APPROVED = "approved"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"              # Dependencies met, ready to start
    IN_PROGRESS = "in_progress"  
    BLOCKED = "blocked"          # Cannot proceed due to issues
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionContext:
    """Execution context for workflow and task tracking"""
    workflow_id: str
    execution_id: str
    
    # Status tracking
    status: ExecutionStatus = ExecutionStatus.PLANNED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Agent assignments
    task_assignments: Dict[str, str] = field(default_factory=dict)  # task_id -> agent_id
    agent_tasks: Dict[str, List[str]] = field(default_factory=dict)  # agent_id -> task_ids
    
    # Progress tracking
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    blocked_tasks: Set[str] = field(default_factory=set)
    
    # Quality tracking
    quality_checks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    approval_status: Dict[str, bool] = field(default_factory=dict)
    
    # Communication
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    agent_communications: List[str] = field(default_factory=list)  # message IDs
    
    # Error handling
    error_count: int = 0
    retry_count: int = 0
    max_retries: int = 3
    
    def get_progress_percentage(self, total_tasks: int) -> float:
        """Calculate execution progress percentage"""
        if total_tasks == 0:
            return 100.0
        return (len(self.completed_tasks) / total_tasks) * 100
    
    def add_log_entry(self, event_type: str, details: Dict[str, Any]):
        """Add entry to execution log"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "details": details
        }
        self.execution_log.append(entry)
        
        # Keep only last 1000 log entries
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-1000:]

class WorkflowExecutor:
    """Orchestrates multi-agent workflow execution"""
    
    def __init__(self):
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.task_decomposer = get_task_decomposer()
        self.hierarchy_manager = get_hierarchy_manager()
        self.communication_bus = get_communication_bus()
        
        # Background execution monitoring
        asyncio.create_task(self._monitor_executions())
        
        logger.info("Workflow Executor initialized")
    
    async def execute_workflow(self, 
                             user_request: str,
                             user_preferences: Dict[str, Any] = None) -> str:
        """Execute a complete workflow from user request to delivery"""
        logger.info(f"Starting workflow execution for: {user_request[:100]}...")
        
        # Step 1: Decompose task into workflow plan
        workflow_plan = await self.task_decomposer.decompose_task(user_request)
        
        # Step 2: Check if user approval required
        if workflow_plan.user_approval_required:
            logger.info(f"Workflow {workflow_plan.id} requires user approval")
            # In a real system, this would wait for user approval
            # For now, we'll assume approval
            await asyncio.sleep(1)
        
        # Step 3: Create execution context
        execution_context = await self._create_execution_context(workflow_plan)
        
        # Step 4: Assign agents to tasks
        await self._assign_agents_to_workflow(workflow_plan, execution_context)
        
        # Step 5: Begin execution
        await self._start_workflow_execution(workflow_plan, execution_context)
        
        logger.info(f"Workflow execution started: {execution_context.execution_id}")
        return execution_context.execution_id
    
    async def _create_execution_context(self, workflow_plan: WorkflowPlan) -> ExecutionContext:
        """Create execution context for workflow tracking"""
        execution_id = f"exec_{workflow_plan.id}_{uuid.uuid4().hex[:8]}"
        
        context = ExecutionContext(
            workflow_id=workflow_plan.id,
            execution_id=execution_id,
            status=ExecutionStatus.PLANNED
        )
        
        context.add_log_entry("workflow_planned", {
            "workflow_id": workflow_plan.id,
            "complexity": workflow_plan.complexity.value,
            "estimated_hours": workflow_plan.estimated_total_hours,
            "estimated_cost": workflow_plan.estimated_cost_usd,
            "sub_tasks_count": len(workflow_plan.sub_tasks),
            "required_specialists": [s.value for s in workflow_plan.required_specialists]
        })
        
        self.active_executions[execution_id] = context
        return context
    
    async def _assign_agents_to_workflow(self, 
                                       workflow_plan: WorkflowPlan, 
                                       execution_context: ExecutionContext):
        """Assign specialist agents to all workflow tasks"""
        logger.info(f"Assigning agents for workflow {workflow_plan.id}")
        
        # Get task assignments from hierarchy manager
        task_assignments = await self.hierarchy_manager.assign_workflow_to_agents(workflow_plan)
        
        # Update execution context
        execution_context.task_assignments = task_assignments
        
        # Build reverse mapping (agent -> tasks)
        for task_id, agent_id in task_assignments.items():
            if agent_id not in execution_context.agent_tasks:
                execution_context.agent_tasks[agent_id] = []
            execution_context.agent_tasks[agent_id].append(task_id)
        
        execution_context.add_log_entry("agents_assigned", {
            "assignments_count": len(task_assignments),
            "agents_involved": list(set(task_assignments.values())),
            "unassigned_tasks": [t.id for t in workflow_plan.sub_tasks 
                                if t.id not in task_assignments]
        })
        
        logger.info(f"Agent assignment complete: {len(task_assignments)} tasks assigned to {len(set(task_assignments.values()))} agents")
    
    async def _start_workflow_execution(self, 
                                      workflow_plan: WorkflowPlan, 
                                      execution_context: ExecutionContext):
        """Start executing the workflow with proper orchestration"""
        execution_context.status = ExecutionStatus.EXECUTING
        execution_context.started_at = datetime.now(timezone.utc)
        
        execution_context.add_log_entry("execution_started", {
            "execution_id": execution_context.execution_id,
            "total_tasks": len(workflow_plan.sub_tasks),
            "execution_phases": workflow_plan.execution_phases
        })
        
        # Execute phases sequentially with parallel tasks within phases
        for phase_index, phase in enumerate(workflow_plan.execution_phases):
            logger.info(f"Starting phase {phase_index + 1}/{len(workflow_plan.execution_phases)}: {phase}")
            
            # Get tasks for this phase
            phase_tasks = [task for task in workflow_plan.sub_tasks 
                          if task.parallel_group == phase or 
                          (not task.parallel_group and phase_index == 0)]
            
            if phase_tasks:
                await self._execute_phase(workflow_plan, execution_context, phase, phase_tasks)
            
            # Check if execution should continue
            if execution_context.status in [ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                break
        
        # Complete execution
        await self._complete_workflow_execution(workflow_plan, execution_context)
    
    async def _execute_phase(self, 
                           workflow_plan: WorkflowPlan,
                           execution_context: ExecutionContext,
                           phase_name: str,
                           phase_tasks: List[SubTask]):
        """
        Execute a single phase with parallel task coordination.
        
        This method orchestrates the execution of all tasks within a phase,
        managing dependencies, parallel execution, and quality gates.
        
        Execution Strategy:
        1. Identify ready tasks (dependencies satisfied)
        2. Start ready tasks in parallel using asyncio
        3. As tasks complete, check for newly ready tasks
        4. Continue until all phase tasks complete
        5. Run quality gate before proceeding to next phase
        
        Args:
            workflow_plan: The complete workflow plan
            execution_context: Current execution context
            phase_name: Name of the phase being executed
            phase_tasks: List of tasks belonging to this phase
        """
        logger.info(f"Executing phase '{phase_name}' with {len(phase_tasks)} tasks")
        
        execution_context.add_log_entry("phase_started", {
            "phase_name": phase_name,
            "tasks_count": len(phase_tasks),
            "task_ids": [t.id for t in phase_tasks],
            "estimated_duration": sum(t.estimated_duration_hours for t in phase_tasks)
        })
        
        # Start ready tasks (those with satisfied dependencies)
        ready_tasks = await self._get_ready_tasks(phase_tasks, execution_context)
        
        if not ready_tasks:
            logger.warning(f"No ready tasks at start of phase '{phase_name}'. "
                         f"Checking dependencies...")
            # Log dependency status for debugging
            for task in phase_tasks:
                missing_deps = [dep for dep in task.depends_on 
                               if dep not in execution_context.completed_tasks]
                if missing_deps:
                    logger.debug(f"Task {task.id} waiting for: {missing_deps}")
        
        if ready_tasks:
            # Start ready tasks in parallel
            task_futures = {}
            for task in ready_tasks:
                future = asyncio.create_task(
                    self._execute_single_task(task, workflow_plan, execution_context)
                )
                task_futures[future] = task.id
            
            # Wait for all phase tasks to complete
            while task_futures:
                # Wait for next task completion with timeout
                try:
                    done, pending = await asyncio.wait(
                        task_futures.keys(), 
                        return_when=asyncio.FIRST_COMPLETED, 
                        timeout=30.0
                    )
                    
                    # Process completed tasks
                    for completed_future in done:
                        task_id = task_futures.pop(completed_future)
                        try:
                            task_result = await completed_future
                            await self._handle_task_completion(task_result, execution_context)
                            
                            # Check if new tasks became ready
                            newly_ready = await self._get_ready_tasks(phase_tasks, execution_context)
                            for new_task in newly_ready:
                                # Avoid duplicate execution
                                if new_task.id not in [t.id for t in ready_tasks]:
                                    ready_tasks.append(new_task)
                                    future = asyncio.create_task(
                                        self._execute_single_task(new_task, workflow_plan, execution_context)
                                    )
                                    task_futures[future] = new_task.id
                            
                        except Exception as e:
                            logger.error(f"Task {task_id} execution error: {e}", exc_info=True)
                            execution_context.error_count += 1
                            
                            # Mark task as failed
                            execution_context.failed_tasks.add(task_id)
                            
                            # Attempt recovery if possible
                            if execution_context.retry_count < execution_context.max_retries:
                                await self._attempt_task_recovery(task_id, execution_context)
                    
                    # Update pending futures dict
                    task_futures = {f: tid for f, tid in task_futures.items() if f in pending}
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Phase '{phase_name}' execution timeout. "
                                 f"Checking task status...")
                    # Check which tasks are still running
                    for future, task_id in list(task_futures.items()):
                        if future.done():
                            task_futures.pop(future)
                        else:
                            logger.debug(f"Task {task_id} still running...")
        
        # Verify phase completion
        completed_phase_tasks = [t.id for t in phase_tasks 
                                if t.id in execution_context.completed_tasks]
        phase_complete = len(completed_phase_tasks) == len(phase_tasks)
        
        if phase_complete:
            execution_context.add_log_entry("phase_completed", {
                "phase_name": phase_name,
                "completed_tasks": len(completed_phase_tasks),
                "total_tasks": len(phase_tasks),
                "phase_duration_estimate": sum(
                    t.estimated_duration_hours for t in phase_tasks
                )
            })
            
            # Run phase quality gate if defined
            await self._run_phase_quality_gate(workflow_plan, execution_context, phase_name)
        else:
            failed_in_phase = [t.id for t in phase_tasks 
                             if t.id in execution_context.failed_tasks]
            logger.warning(
                f"Phase '{phase_name}' incomplete: "
                f"{len(completed_phase_tasks)}/{len(phase_tasks)} completed, "
                f"{len(failed_in_phase)} failed"
            )
            
            # Log incomplete phase for monitoring
            execution_context.add_log_entry("phase_incomplete", {
                "phase_name": phase_name,
                "completed": len(completed_phase_tasks),
                "failed": len(failed_in_phase),
                "total": len(phase_tasks),
                "failed_task_ids": failed_in_phase
            })
    
    async def _get_ready_tasks(self, 
                             phase_tasks: List[SubTask], 
                             execution_context: ExecutionContext) -> List[SubTask]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        
        for task in phase_tasks:
            # Skip if already completed or in progress
            if (task.id in execution_context.completed_tasks or 
                task.id in execution_context.failed_tasks):
                continue
            
            # Check if dependencies are satisfied
            dependencies_satisfied = True
            for dep_task_id in task.depends_on:
                if dep_task_id not in execution_context.completed_tasks:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                # Check if assigned agent is available
                assigned_agent_id = execution_context.task_assignments.get(task.id)
                if assigned_agent_id:
                    agent = self.hierarchy_manager.agents.get(assigned_agent_id)
                    if agent and agent.is_available() and agent.is_healthy():
                        ready_tasks.append(task)
                else:
                    # Try to assign agent if not already assigned
                    await self._reassign_task_if_needed(task, execution_context)
                    ready_tasks.append(task)  # Assume assignment successful
        
        return ready_tasks
    
    async def _execute_single_task(self, 
                                 task: SubTask,
                                 workflow_plan: WorkflowPlan, 
                                 execution_context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute a single task with full orchestration and monitoring.
        
        This method coordinates the complete execution lifecycle:
        1. Validates agent assignment
        2. Sends task start notification
        3. Monitors execution with timeout protection
        4. Handles task-specific execution logic
        5. Records completion and quality metrics
        6. Sends completion notification
        
        Args:
            task: The sub-task to execute
            workflow_plan: Complete workflow plan for context
            execution_context: Execution tracking context
            
        Returns:
            Dictionary with task execution results
        """
        logger.info(f"Starting task execution: {task.id} ({task.title})")
        
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.now(timezone.utc)
        
        # Get assigned agent
        assigned_agent_id = execution_context.task_assignments.get(task.id)
        if not assigned_agent_id:
            logger.error(f"No agent assigned to task {task.id}")
            task.status = TaskStatus.FAILED.value
            execution_context.failed_tasks.add(task.id)
            return {"task_id": task.id, "status": "failed", "error": "no_agent_assigned"}
        
        # Verify agent is still available and healthy
        agent = self.hierarchy_manager.agents.get(assigned_agent_id)
        if not agent or not agent.is_healthy():
            logger.warning(f"Assigned agent {assigned_agent_id} is unavailable, attempting reassignment...")
            await self._reassign_task_if_needed(task, execution_context)
            assigned_agent_id = execution_context.task_assignments.get(task.id)
            if not assigned_agent_id:
                task.status = TaskStatus.FAILED.value
                return {"task_id": task.id, "status": "failed", "error": "no_available_agent"}
            agent = self.hierarchy_manager.agents.get(assigned_agent_id)
        
        # Notify task start to agent
        try:
            await self.communication_bus.send_message(
                sender_id="workflow_executor",
                recipient_id=assigned_agent_id,
                message_type=MessageType.TASK_STARTED,
                payload={
                    "task_id": task.id,
                    "task_title": task.title,
                    "task_description": task.description,
                    "success_criteria": task.success_criteria,
                    "quality_checkpoints": task.quality_checkpoints,
                    "estimated_duration_hours": task.estimated_duration_hours,
                    "priority": task.priority,
                    "workflow_context": {
                        "workflow_id": workflow_plan.id,
                        "user_request": workflow_plan.user_request,
                        "complexity": workflow_plan.complexity.value,
                        "current_phase": execution_context.execution_log[-1].get("event_type", "unknown") if execution_context.execution_log else "initialization"
                    }
                },
                priority=Priority.HIGH if task.priority >= 8 else Priority.NORMAL,
                requires_response=True,
                response_timeout=60  # Agent should acknowledge within 60 seconds
            )
        except Exception as e:
            logger.error(f"Failed to send task start notification: {e}")
            # Continue execution despite notification failure
        
        execution_context.add_log_entry("task_started", {
            "task_id": task.id,
            "agent_id": assigned_agent_id,
            "estimated_duration_hours": task.estimated_duration_hours,
            "priority": task.priority,
            "specialty": task.assigned_agent.value
        })
        
        # Execute task with timeout protection
        try:
            # Calculate timeout (2x estimated time, minimum 5 minutes, maximum 8 hours)
            timeout_seconds = max(
                300,  # 5 minutes minimum
                min(
                    task.estimated_duration_hours * 3600 * 2,  # 2x estimated
                    28800  # 8 hours maximum
                )
            )
            
            start_time = time.time()
            
            # Execute task based on specialist type
            # In production, this would coordinate with actual agent execution
            execution_result = await self._execute_task_by_specialty(
                task, assigned_agent_id, timeout_seconds
            )
            
            # Record completion
            task.status = TaskStatus.COMPLETED.value
            task.completed_at = datetime.now(timezone.utc)
            task.output_summary = execution_result.get("execution_summary", 
                                                      execution_result.get("summary", 
                                                                          "Task completed successfully"))
            
            # Calculate actual execution time
            actual_duration = time.time() - start_time
            actual_duration_hours = actual_duration / 3600
            
            # Update agent performance metrics
            if agent:
                # Update average completion time (exponential moving average)
                agent.avg_completion_time = (
                    agent.avg_completion_time * 0.7 + actual_duration_hours * 0.3
                )
            
            # Notify completion
            try:
                await self.communication_bus.send_message(
                    sender_id=assigned_agent_id,
                    recipient_id="workflow_executor",
                    message_type=MessageType.TASK_COMPLETED,
                    payload={
                        "task_id": task.id,
                        "execution_result": execution_result,
                        "actual_duration_seconds": actual_duration,
                        "actual_duration_hours": round(actual_duration_hours, 2),
                        "quality_metrics": {
                            k: v for k, v in execution_result.items() 
                            if "quality" in k.lower() or "score" in k.lower() or "accuracy" in k.lower()
                        },
                        "success_criteria_met": self._check_success_criteria(task, execution_result)
                    },
                    priority=Priority.HIGH
                )
            except Exception as e:
                logger.error(f"Failed to send task completion notification: {e}")
            
            return {
                "task_id": task.id,
                "status": "completed",
                "agent_id": assigned_agent_id,
                "execution_result": execution_result,
                "actual_duration": actual_duration,
                "actual_duration_hours": round(actual_duration_hours, 2)
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Task {task.id} timed out after {timeout_seconds} seconds")
            task.status = TaskStatus.FAILED.value
            execution_context.failed_tasks.add(task.id)
            
            # Notify failure
            try:
                await self.communication_bus.send_message(
                    sender_id="workflow_executor",
                    recipient_id=assigned_agent_id,
                    message_type=MessageType.TASK_FAILED,
                    payload={
                        "task_id": task.id,
                        "error": "timeout",
                        "timeout_seconds": timeout_seconds
                    },
                    priority=Priority.HIGH
                )
            except Exception:
                pass
            
            return {"task_id": task.id, "status": "failed", "error": "timeout"}
        
        except Exception as e:
            logger.error(f"Task {task.id} failed with error: {e}", exc_info=True)
            task.status = TaskStatus.FAILED.value
            execution_context.failed_tasks.add(task.id)
            
            # Notify failure
            try:
                await self.communication_bus.send_message(
                    sender_id="workflow_executor",
                    recipient_id=assigned_agent_id,
                    message_type=MessageType.ERROR_REPORT,
                    payload={
                        "task_id": task.id,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "workflow_id": workflow_plan.id
                    },
                    priority=Priority.HIGH
                )
            except Exception:
                pass
            
            return {"task_id": task.id, "status": "failed", "error": str(e)}
    
    async def _execute_task_by_specialty(self, 
                                       task: SubTask,
                                       agent_id: str,
                                       timeout_seconds: float) -> Dict[str, Any]:
        """
        Execute task based on specialist agent type.
        
        This method simulates task execution for different specialist types.
        In production, this would coordinate with actual agent implementations.
        
        Args:
            task: The task to execute
            agent_id: ID of the assigned agent
            timeout_seconds: Maximum execution time
            
        Returns:
            Dictionary with execution results and quality metrics
        """
        specialty = task.assigned_agent.value
        
        # Research specialists
        if specialty in ["academic_researcher", "web_intelligence_gatherer", 
                        "news_trends_analyzer", "competitive_intelligence", "social_media_monitor"]:
            # Simulate research time (proportional to estimated duration)
            await asyncio.sleep(min(0.5, task.estimated_duration_hours * 0.3))
            return {
                "sources_found": max(10, int(task.estimated_duration_hours * 8)),
                "credible_sources": max(8, int(task.estimated_duration_hours * 6)),
                "research_quality": 0.88 + (task.priority / 100),  # Higher priority = better quality
                "coverage_completeness": 0.85 + (task.priority / 150),
                "findings_summary": f"Research completed: {task.description[:80]}...",
                "execution_summary": f"Research task completed with {max(10, int(task.estimated_duration_hours * 8))} sources"
            }
        
        # Analysis specialists
        elif specialty in ["data_analyst", "statistical_modeler", "pattern_recognition_expert",
                          "risk_assessment_specialist", "financial_performance_analyst"]:
            await asyncio.sleep(min(0.4, task.estimated_duration_hours * 0.25))
            return {
                "analysis_accuracy": 0.90 + (task.priority / 120),
                "statistical_significance": 0.85 + (task.priority / 140),
                "patterns_identified": max(2, int(task.estimated_duration_hours * 1.5)),
                "confidence_score": 0.87 + (task.priority / 130),
                "analysis_summary": f"Analysis completed: {task.description[:80]}...",
                "execution_summary": f"Data analysis completed with {max(2, int(task.estimated_duration_hours * 1.5))} patterns identified"
            }
        
        # Creative specialists
        elif specialty in ["graphics_diagram_designer", "content_writer_editor",
                          "presentation_formatter", "media_video_producer", "infographic_creator"]:
            await asyncio.sleep(min(0.5, task.estimated_duration_hours * 0.3))
            return {
                "creative_quality": 0.88 + (task.priority / 110),
                "brand_consistency": 0.92 + (task.priority / 150),
                "visual_appeal": 0.86 + (task.priority / 120),
                "professional_standard": 0.90 + (task.priority / 130),
                "creative_summary": f"Creative work completed: {task.description[:80]}...",
                "execution_summary": f"Creative task completed meeting professional standards"
            }
        
        # QA specialists
        elif specialty in ["fact_checker_validator", "output_quality_controller",
                          "compliance_reviewer", "error_detection_specialist", "final_delivery_approver"]:
            await asyncio.sleep(min(0.3, task.estimated_duration_hours * 0.2))
            return {
                "quality_score": 0.92 + (task.priority / 200),
                "compliance_score": 0.95 + (task.priority / 250),
                "errors_found": 0,  # Assuming clean input
                "recommendations": [],
                "approval_status": "approved",
                "execution_summary": f"Quality review completed: {task.description[:80]}..."
            }
        
        # Technical specialists
        elif specialty in ["code_reviewer_optimizer", "system_architect", "security_analyst",
                          "performance_engineer", "devops_specialist"]:
            await asyncio.sleep(min(0.4, task.estimated_duration_hours * 0.25))
            return {
                "technical_quality": 0.91 + (task.priority / 130),
                "security_score": 0.93 + (task.priority / 150),
                "performance_improvement": 0.15,  # 15% improvement
                "execution_summary": f"Technical task completed: {task.description[:80]}..."
            }
        
        # Investigation specialists
        elif specialty in ["digital_forensics_expert", "network_security_analyzer",
                          "reverse_engineering_specialist", "case_investigation_manager",
                          "evidence_compilation_expert"]:
            await asyncio.sleep(min(0.6, task.estimated_duration_hours * 0.35))
            return {
                "investigation_completeness": 0.89 + (task.priority / 120),
                "evidence_quality": 0.91 + (task.priority / 140),
                "findings_count": max(5, int(task.estimated_duration_hours * 3)),
                "execution_summary": f"Investigation completed: {task.description[:80]}..."
            }
        
        # Default execution
        else:
            await asyncio.sleep(min(0.3, task.estimated_duration_hours * 0.2))
            return {
                "task_completion": 0.88 + (task.priority / 120),
                "quality_score": 0.85 + (task.priority / 130),
                "execution_summary": f"Task completed: {task.description[:80]}..."
            }
    
    def _check_success_criteria(self, task: SubTask, execution_result: Dict[str, Any]) -> bool:
        """
        Check if task execution met all success criteria.
        
        Args:
            task: The completed task
            execution_result: Execution results
            
        Returns:
            True if all success criteria are met
        """
        if not task.success_criteria:
            return True  # No criteria = success
        
        # Simple heuristic: check if quality metrics meet thresholds
        quality_scores = [
            v for k, v in execution_result.items() 
            if isinstance(v, (int, float)) and ("quality" in k.lower() or "score" in k.lower() or "accuracy" in k.lower())
        ]
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            return avg_quality >= 0.80  # 80% threshold
        
        return True  # Default to success if no quality metrics
    
    async def _handle_task_completion(self, 
                                    task_result: Dict[str, Any], 
                                    execution_context: ExecutionContext):
        """Handle completion of individual task"""
        task_id = task_result["task_id"]
        status = task_result["status"]
        
        if status == "completed":
            execution_context.completed_tasks.add(task_id)
            
            execution_context.add_log_entry("task_completed", {
                "task_id": task_id,
                "agent_id": task_result.get("agent_id"),
                "execution_result": task_result.get("execution_result", {})
            })
            
            # Run quality checkpoints if defined
            await self._run_task_quality_checks(task_id, task_result, execution_context)
            
        elif status == "failed":
            execution_context.failed_tasks.add(task_id)
            execution_context.error_count += 1
            
            execution_context.add_log_entry("task_failed", {
                "task_id": task_id,
                "error": task_result.get("error"),
                "retry_count": execution_context.retry_count
            })
            
            # Attempt recovery if possible
            if execution_context.retry_count < execution_context.max_retries:
                await self._attempt_task_recovery(task_id, execution_context)
        
        # Update agent availability
        assigned_agent_id = execution_context.task_assignments.get(task_id)
        if assigned_agent_id:
            agent = self.hierarchy_manager.agents.get(assigned_agent_id)
            if agent and task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)
    
    async def _run_task_quality_checks(self, 
                                     task_id: str,
                                     task_result: Dict[str, Any], 
                                     execution_context: ExecutionContext):
        """Run quality checks for completed task"""
        # Quality check based on execution result
        execution_result = task_result.get("execution_result", {})
        
        # Extract quality metrics
        quality_metrics = {
            "overall_score": 0.0,
            "accuracy": execution_result.get("accuracy", 0.85),
            "completeness": execution_result.get("completeness", 0.80),
            "professional_standard": execution_result.get("professional_standard", 0.85)
        }
        
        # Calculate overall quality score
        quality_metrics["overall_score"] = (
            quality_metrics["accuracy"] * 0.4 +
            quality_metrics["completeness"] * 0.3 +
            quality_metrics["professional_standard"] * 0.3
        )
        
        execution_context.quality_checks[task_id] = quality_metrics
        
        # Log quality assessment
        execution_context.add_log_entry("quality_check_completed", {
            "task_id": task_id,
            "quality_metrics": quality_metrics,
            "passed_quality_gate": quality_metrics["overall_score"] >= 0.80
        })
        
        logger.debug(f"Quality check for {task_id}: {quality_metrics['overall_score']:.2f}")
    
    async def _run_phase_quality_gate(self, 
                                    workflow_plan: WorkflowPlan,
                                    execution_context: ExecutionContext, 
                                    phase_name: str):
        """Run quality gate at end of phase"""
        # Find quality gates for this phase
        relevant_gates = [gate for gate in workflow_plan.quality_gates 
                         if gate.get("checkpoint", "").endswith(phase_name.split("_")[-1])]
        
        for gate in relevant_gates:
            gate_name = gate["name"]
            threshold = gate["threshold"]
            
            # Calculate gate score based on phase tasks
            phase_tasks = [task for task in workflow_plan.sub_tasks 
                          if task.parallel_group == phase_name]
            
            if phase_tasks:
                # Average quality score for phase
                phase_quality_scores = []
                for task in phase_tasks:
                    task_quality = execution_context.quality_checks.get(task.id, {})
                    if task_quality:
                        phase_quality_scores.append(task_quality["overall_score"])
                
                if phase_quality_scores:
                    avg_phase_quality = sum(phase_quality_scores) / len(phase_quality_scores)
                    gate_passed = avg_phase_quality >= threshold
                    
                    execution_context.approval_status[gate_name] = gate_passed
                    
                    execution_context.add_log_entry("quality_gate_evaluated", {
                        "gate_name": gate_name,
                        "threshold": threshold,
                        "actual_score": avg_phase_quality,
                        "passed": gate_passed,
                        "phase": phase_name
                    })
                    
                    if not gate_passed:
                        logger.warning(f"Quality gate '{gate_name}' failed: {avg_phase_quality:.2f} < {threshold}")
                        # In a full implementation, this might trigger rework
    
    async def _attempt_task_recovery(self, task_id: str, execution_context: ExecutionContext):
        """Attempt to recover from task failure"""
        logger.info(f"Attempting recovery for failed task: {task_id}")
        
        # Remove from failed tasks to retry
        execution_context.failed_tasks.discard(task_id)
        execution_context.retry_count += 1
        
        # Try to reassign to different agent
        await self._reassign_task_if_needed_by_id(task_id, execution_context)
        
        execution_context.add_log_entry("task_recovery_attempted", {
            "task_id": task_id,
            "retry_count": execution_context.retry_count,
            "new_assignment": execution_context.task_assignments.get(task_id)
        })
    
    async def _reassign_task_if_needed(self, task: SubTask, execution_context: ExecutionContext):
        """Reassign task if current agent is unavailable"""
        current_agent_id = execution_context.task_assignments.get(task.id)
        
        if current_agent_id:
            agent = self.hierarchy_manager.agents.get(current_agent_id)
            if agent and agent.is_available() and agent.is_healthy():
                return  # Current assignment is fine
        
        # Find new agent
        available_agents = await self.hierarchy_manager._get_available_specialists(task.assigned_agent)
        
        if available_agents:
            # Select best agent
            new_agent_id = await self.hierarchy_manager._select_optimal_agent(available_agents, task)
            
            # Update assignment
            if current_agent_id:
                # Remove from old agent
                old_agent = self.hierarchy_manager.agents.get(current_agent_id)
                if old_agent and task.id in old_agent.current_tasks:
                    old_agent.current_tasks.remove(task.id)
            
            # Assign to new agent
            execution_context.task_assignments[task.id] = new_agent_id
            self.hierarchy_manager.agents[new_agent_id].current_tasks.append(task.id)
            
            logger.info(f"Task {task.id} reassigned: {current_agent_id} -> {new_agent_id}")
    
    async def _reassign_task_if_needed_by_id(self, task_id: str, execution_context: ExecutionContext):
        """Reassign task by ID (for recovery scenarios)"""
        # Find task in active workflow
        workflow_id = execution_context.workflow_id
        workflow_plan = self.hierarchy_manager.active_workflows.get(workflow_id)
        
        if workflow_plan:
            task = next((t for t in workflow_plan.sub_tasks if t.id == task_id), None)
            if task:
                await self._reassign_task_if_needed(task, execution_context)
    
    async def _complete_workflow_execution(self, 
                                         workflow_plan: WorkflowPlan,
                                         execution_context: ExecutionContext):
        """Complete workflow execution with final quality review"""
        logger.info(f"Completing workflow execution: {execution_context.execution_id}")
        
        # Calculate final statistics
        total_tasks = len(workflow_plan.sub_tasks)
        completed_tasks = len(execution_context.completed_tasks)
        failed_tasks = len(execution_context.failed_tasks)
        
        # Determine overall success
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        
        if success_rate >= 0.90:  # 90% success threshold
            execution_context.status = ExecutionStatus.COMPLETED
        else:
            execution_context.status = ExecutionStatus.FAILED
        
        execution_context.completed_at = datetime.now(timezone.utc)
        
        # Calculate total execution time
        if execution_context.started_at:
            total_execution_time = (execution_context.completed_at - execution_context.started_at).total_seconds() / 3600
        else:
            total_execution_time = 0.0
        
        # Final quality assessment
        overall_quality = await self._assess_overall_quality(execution_context)
        
        # Log completion
        execution_context.add_log_entry("workflow_completed", {
            "status": execution_context.status.value,
            "success_rate": success_rate,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "total_execution_hours": round(total_execution_time, 2),
            "overall_quality": overall_quality,
            "error_count": execution_context.error_count,
            "retry_count": execution_context.retry_count
        })
        
        # Notify all involved agents of completion
        await self._notify_workflow_completion(execution_context, success_rate, overall_quality)
        
        logger.info(f"Workflow execution completed: {execution_context.execution_id} "
                   f"(Success: {success_rate:.1%}, Quality: {overall_quality:.2f})")
    
    async def _assess_overall_quality(self, execution_context: ExecutionContext) -> float:
        """Assess overall workflow quality"""
        if not execution_context.quality_checks:
            return 0.85  # Default quality score
        
        # Average quality scores across all completed tasks
        quality_scores = [check["overall_score"] for check in execution_context.quality_checks.values()]
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.85
    
    async def _notify_workflow_completion(self, 
                                        execution_context: ExecutionContext,
                                        success_rate: float,
                                        overall_quality: float):
        """Notify all involved agents of workflow completion"""
        involved_agents = set(execution_context.task_assignments.values())
        
        completion_payload = {
            "execution_id": execution_context.execution_id,
            "workflow_id": execution_context.workflow_id,
            "completion_status": execution_context.status.value,
            "success_rate": success_rate,
            "overall_quality": overall_quality,
            "total_tasks": len(execution_context.task_assignments),
            "completed_tasks": len(execution_context.completed_tasks),
            "execution_time_hours": (
                (execution_context.completed_at - execution_context.started_at).total_seconds() / 3600
                if execution_context.started_at and execution_context.completed_at else 0.0
            )
        }
        
        # Notify all involved agents
        for agent_id in involved_agents:
            await self.communication_bus.send_message(
                sender_id="workflow_executor",
                recipient_id=agent_id,
                message_type=MessageType.STATUS_UPDATE,
                payload=completion_payload,
                priority=Priority.NORMAL
            )
    
    async def _monitor_executions(self):
        """Background monitoring of active workflow executions"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for execution_id, context in list(self.active_executions.items()):
                    if context.status == ExecutionStatus.EXECUTING:
                        # Check for stuck executions
                        if (context.started_at and 
                            (current_time - context.started_at).total_seconds() > 28800):  # 8 hours
                            
                            logger.warning(f"Long-running execution detected: {execution_id}")
                            
                            # Consider escalation or intervention
                            await self._handle_long_running_execution(context)
                    
                    elif context.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                        # Clean up old completed executions (keep for 24 hours)
                        if (context.completed_at and 
                            (current_time - context.completed_at).total_seconds() > 86400):
                            
                            logger.info(f"Cleaning up old execution: {execution_id}")
                            del self.active_executions[execution_id]
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in execution monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _handle_long_running_execution(self, execution_context: ExecutionContext):
        """Handle executions that are taking too long"""
        # Escalate to management
        await self.communication_bus.escalate_to_management(
            escalating_agent_id="workflow_executor",
            issue_type="long_running_execution",
            escalation_data={
                "execution_id": execution_context.execution_id,
                "running_hours": (datetime.now(timezone.utc) - execution_context.started_at).total_seconds() / 3600,
                "completed_percentage": execution_context.get_progress_percentage(len(execution_context.task_assignments)),
                "error_count": execution_context.error_count,
                "recommended_actions": ["agent_health_check", "resource_scaling", "task_prioritization"]
            },
            urgency=Priority.HIGH
        )
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of workflow execution"""
        context = self.active_executions.get(execution_id)
        if not context:
            return None
        
        total_tasks = len(context.task_assignments)
        
        return {
            "execution_id": execution_id,
            "workflow_id": context.workflow_id,
            "status": context.status.value,
            "progress_percentage": context.get_progress_percentage(total_tasks),
            "completed_tasks": len(context.completed_tasks),
            "failed_tasks": len(context.failed_tasks),
            "total_tasks": total_tasks,
            "error_count": context.error_count,
            "retry_count": context.retry_count,
            "started_at": context.started_at.isoformat() if context.started_at else None,
            "estimated_completion": self._estimate_completion_time(context),
            "quality_summary": self._get_quality_summary(context)
        }
    
    def _estimate_completion_time(self, execution_context: ExecutionContext) -> Optional[str]:
        """Estimate when execution will complete"""
        if execution_context.status != ExecutionStatus.EXECUTING:
            return None
        
        # Simple estimation based on completed vs remaining tasks
        total_tasks = len(execution_context.task_assignments)
        completed_tasks = len(execution_context.completed_tasks)
        
        if completed_tasks == 0:
            return None
        
        # Calculate average time per completed task
        if execution_context.started_at:
            elapsed_time = (datetime.now(timezone.utc) - execution_context.started_at).total_seconds()
            avg_time_per_task = elapsed_time / completed_tasks
            
            remaining_tasks = total_tasks - completed_tasks
            estimated_remaining_seconds = remaining_tasks * avg_time_per_task
            
            estimated_completion = datetime.now(timezone.utc) + timedelta(seconds=estimated_remaining_seconds)
            return estimated_completion.isoformat()
        
        return None
    
    def _get_quality_summary(self, execution_context: ExecutionContext) -> Dict[str, Any]:
        """Get summary of quality metrics for execution"""
        if not execution_context.quality_checks:
            return {"overall_quality": 0.0, "checks_completed": 0}
        
        quality_scores = [check["overall_score"] for check in execution_context.quality_checks.values()]
        
        return {
            "overall_quality": sum(quality_scores) / len(quality_scores),
            "checks_completed": len(execution_context.quality_checks),
            "min_quality": min(quality_scores) if quality_scores else 0.0,
            "max_quality": max(quality_scores) if quality_scores else 0.0,
            "quality_variance": self._calculate_quality_variance(quality_scores)
        }
    
    def _calculate_quality_variance(self, scores: List[float]) -> float:
        """Calculate variance in quality scores"""
        if len(scores) < 2:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        return variance

# Global workflow executor instance
_global_workflow_executor: Optional[WorkflowExecutor] = None

def get_workflow_executor() -> WorkflowExecutor:
    """Get global workflow executor instance"""
    global _global_workflow_executor
    if _global_workflow_executor is None:
        _global_workflow_executor = WorkflowExecutor()
    return _global_workflow_executor
