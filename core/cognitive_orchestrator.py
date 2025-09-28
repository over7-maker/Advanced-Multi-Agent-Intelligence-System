"""
AMAS Cognitive Orchestrator - Advanced Dual-Process Model Implementation

This module implements the cognitive architecture enhancement for AMAS, featuring:
- System 1: Fast, intuitive, heuristic-based processing for routine tasks
- System 2: Slow, deliberate, analytical reasoning for complex problems
- Cognitive load balancing and task complexity assessment
- Explainable reasoning with decision transparency

Based on cognitive science research and the Advanced Multi-Agent Intelligence System Blueprint.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from core.orchestrator import IntelligenceOrchestrator, TaskPriority, TaskStatus, IntelligenceTask
from agents.base.intelligence_agent import IntelligenceAgent, AgentStatus

logger = logging.getLogger(__name__)


class CognitiveMode(Enum):
    """Cognitive processing modes"""
    SYSTEM1 = "system1"  # Fast, intuitive processing
    SYSTEM2 = "system2"  # Slow, deliberate reasoning
    HYBRID = "hybrid"    # Combined approach
    AUTO = "auto"        # Automatic selection


class TaskComplexity(Enum):
    """Task complexity levels for cognitive mode selection"""
    SIMPLE = 1      # Routine, well-defined tasks
    MODERATE = 2    # Standard tasks with some ambiguity
    COMPLEX = 3     # Multi-step tasks requiring analysis
    CRITICAL = 4    # High-stakes tasks requiring deep reasoning


@dataclass
class CognitiveContext:
    """Context information for cognitive processing"""
    task_id: str
    complexity: TaskComplexity
    cognitive_mode: CognitiveMode
    confidence_threshold: float = 0.8
    reasoning_steps: List[str] = field(default_factory=list)
    decision_factors: Dict[str, float] = field(default_factory=dict)
    processing_time: float = 0.0
    system1_result: Optional[Dict[str, Any]] = None
    system2_result: Optional[Dict[str, Any]] = None
    final_decision: Optional[Dict[str, Any]] = None
    explanation: str = ""


@dataclass
class ReasoningStep:
    """Individual reasoning step with explanation"""
    step_id: str
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    reasoning_type: str  # 'deductive', 'inductive', 'abductive'
    timestamp: datetime
    duration: float


class CognitiveOrchestrator(IntelligenceOrchestrator):
    """
    Advanced orchestrator with dual-process cognitive model.
    
    Implements System 1 (fast, intuitive) and System 2 (slow, analytical)
    processing modes based on task complexity and cognitive load.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cognitive processing components
        self.cognitive_contexts: Dict[str, CognitiveContext] = {}
        self.reasoning_history: List[ReasoningStep] = []
        self.cognitive_load_tracker = CognitiveLoadTracker()
        self.reasoning_engine = ReasoningEngine()
        
        # Performance metrics for cognitive processing
        self.cognitive_metrics = {
            'system1_tasks': 0,
            'system2_tasks': 0,
            'hybrid_tasks': 0,
            'avg_system1_time': 0.0,
            'avg_system2_time': 0.0,
            'cognitive_accuracy': 0.0,
            'reasoning_quality': 0.0
        }
        
        # Configuration
        self.system1_timeout = 5.0  # Max time for System 1 processing
        self.system2_timeout = 60.0  # Max time for System 2 processing
        self.confidence_threshold = 0.8
        self.complexity_threshold = TaskComplexity.MODERATE
        
        logger.info("Cognitive Orchestrator initialized with dual-process model")
    
    async def submit_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        workflow_id: Optional[str] = None,
        cognitive_mode: CognitiveMode = CognitiveMode.AUTO
    ) -> str:
        """
        Enhanced task submission with cognitive processing mode selection.
        
        Args:
            task_type: Type of task
            description: Task description
            parameters: Task parameters
            priority: Task priority
            workflow_id: Optional workflow ID
            cognitive_mode: Preferred cognitive processing mode
            
        Returns:
            Task ID
        """
        try:
            # Create base task
            task_id = await super().submit_task(task_type, description, parameters, priority, workflow_id)
            
            # Assess task complexity
            complexity = await self._assess_task_complexity(task_type, description, parameters)
            
            # Determine cognitive processing mode
            if cognitive_mode == CognitiveMode.AUTO:
                cognitive_mode = await self._select_cognitive_mode(complexity, priority)
            
            # Create cognitive context
            context = CognitiveContext(
                task_id=task_id,
                complexity=complexity,
                cognitive_mode=cognitive_mode,
                confidence_threshold=self.confidence_threshold
            )
            
            self.cognitive_contexts[task_id] = context
            
            logger.info(f"Task {task_id} submitted with cognitive mode: {cognitive_mode.value}, complexity: {complexity.value}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error in cognitive task submission: {e}")
            raise
    
    async def _assess_task_complexity(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> TaskComplexity:
        """
        Assess task complexity to determine appropriate cognitive processing mode.
        
        Uses multiple factors:
        - Task type complexity mapping
        - Description analysis (keywords, length, ambiguity)
        - Parameter complexity
        - Historical performance data
        """
        try:
            complexity_score = 0.0
            
            # Task type complexity mapping
            task_complexity_map = {
                'osint': 2.0,
                'investigation': 3.0,
                'forensics': 3.5,
                'data_analysis': 2.5,
                'reverse_engineering': 4.0,
                'metadata': 1.5,
                'reporting': 2.0,
                'technology_monitor': 1.5
            }
            
            complexity_score += task_complexity_map.get(task_type.lower(), 2.0)
            
            # Description analysis
            description_factors = await self._analyze_description_complexity(description)
            complexity_score += description_factors
            
            # Parameter complexity
            param_complexity = len(parameters) * 0.2 + sum(
                0.5 if isinstance(v, (dict, list)) else 0.1 
                for v in parameters.values()
            )
            complexity_score += min(param_complexity, 2.0)
            
            # Map score to complexity level
            if complexity_score <= 2.0:
                return TaskComplexity.SIMPLE
            elif complexity_score <= 3.0:
                return TaskComplexity.MODERATE
            elif complexity_score <= 4.0:
                return TaskComplexity.COMPLEX
            else:
                return TaskComplexity.CRITICAL
                
        except Exception as e:
            logger.error(f"Error assessing task complexity: {e}")
            return TaskComplexity.MODERATE  # Default to moderate
    
    async def _analyze_description_complexity(self, description: str) -> float:
        """Analyze description text for complexity indicators"""
        try:
            complexity_score = 0.0
            
            # Length factor
            if len(description) > 200:
                complexity_score += 1.0
            elif len(description) > 100:
                complexity_score += 0.5
            
            # Complexity keywords
            complex_keywords = [
                'analyze', 'investigate', 'correlate', 'comprehensive', 'detailed',
                'multi-step', 'complex', 'advanced', 'deep', 'thorough'
            ]
            
            simple_keywords = [
                'simple', 'basic', 'quick', 'standard', 'routine', 'straightforward'
            ]
            
            description_lower = description.lower()
            
            for keyword in complex_keywords:
                if keyword in description_lower:
                    complexity_score += 0.3
            
            for keyword in simple_keywords:
                if keyword in description_lower:
                    complexity_score -= 0.2
            
            # Question marks indicate uncertainty/complexity
            complexity_score += description.count('?') * 0.2
            
            return max(0.0, min(complexity_score, 2.0))
            
        except Exception as e:
            logger.error(f"Error analyzing description complexity: {e}")
            return 1.0
    
    async def _select_cognitive_mode(
        self,
        complexity: TaskComplexity,
        priority: TaskPriority
    ) -> CognitiveMode:
        """
        Select appropriate cognitive processing mode based on complexity and priority.
        
        System 1 (Fast): Simple tasks, low cognitive load
        System 2 (Slow): Complex tasks, high priority
        Hybrid: Moderate complexity, balanced approach
        """
        try:
            current_load = await self.cognitive_load_tracker.get_current_load()
            
            # High priority tasks with complexity get System 2
            if priority.value >= 3 and complexity.value >= 3:
                return CognitiveMode.SYSTEM2
            
            # Simple tasks or high load situations use System 1
            if complexity == TaskComplexity.SIMPLE or current_load > 0.8:
                return CognitiveMode.SYSTEM1
            
            # Critical tasks always use System 2
            if complexity == TaskComplexity.CRITICAL:
                return CognitiveMode.SYSTEM2
            
            # Moderate complexity uses hybrid approach
            if complexity == TaskComplexity.MODERATE:
                return CognitiveMode.HYBRID
            
            # Default to System 2 for complex tasks
            return CognitiveMode.SYSTEM2
            
        except Exception as e:
            logger.error(f"Error selecting cognitive mode: {e}")
            return CognitiveMode.SYSTEM2  # Default to careful processing
    
    async def _execute_task(self, task_id: str, agent_id: str):
        """
        Enhanced task execution with cognitive processing.
        
        Overrides the base implementation to add cognitive processing modes.
        """
        try:
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            context = self.cognitive_contexts.get(task_id)
            
            if not context:
                # Fallback to base implementation if no cognitive context
                return await super()._execute_task(task_id, agent_id)
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            
            # Execute based on cognitive mode
            start_time = time.time()
            
            if context.cognitive_mode == CognitiveMode.SYSTEM1:
                result = await self._execute_system1_processing(task, agent, context)
            elif context.cognitive_mode == CognitiveMode.SYSTEM2:
                result = await self._execute_system2_processing(task, agent, context)
            elif context.cognitive_mode == CognitiveMode.HYBRID:
                result = await self._execute_hybrid_processing(task, agent, context)
            else:
                result = await self._execute_system2_processing(task, agent, context)
            
            processing_time = time.time() - start_time
            context.processing_time = processing_time
            
            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # Update metrics
            await self._update_cognitive_metrics(context, result, processing_time)
            
            logger.info(f"Cognitive task {task_id} completed in {processing_time:.2f}s using {context.cognitive_mode.value}")
            
        except Exception as e:
            # Handle errors
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            logger.error(f"Cognitive task {task_id} failed: {e}")
    
    async def _execute_system1_processing(
        self,
        task: IntelligenceTask,
        agent: IntelligenceAgent,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """
        System 1: Fast, intuitive processing for routine tasks.
        
        Characteristics:
        - Quick heuristic-based decisions
        - Pattern matching
        - Cached responses for similar tasks
        - Minimal deliberation
        """
        try:
            logger.info(f"Executing System 1 processing for task {task.id}")
            
            # Quick pattern matching against known task types
            cached_response = await self._check_cached_responses(task)
            if cached_response:
                context.reasoning_steps.append("Used cached response from similar task")
                context.system1_result = cached_response
                context.final_decision = cached_response
                context.explanation = "Fast processing using pattern matching and cached knowledge"
                return cached_response
            
            # Fast heuristic processing
            heuristic_params = {
                'processing_mode': 'fast',
                'depth': 'shallow',
                'timeout': self.system1_timeout
            }
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    agent.process_task({
                        'id': task.id,
                        'type': task.type,
                        'description': task.description,
                        'parameters': {**task.parameters, **heuristic_params}
                    }),
                    timeout=self.system1_timeout
                )
                
                context.system1_result = result
                context.final_decision = result
                context.reasoning_steps.append("Fast heuristic processing completed")
                context.explanation = "Quick intuitive processing based on established patterns"
                
                return result
                
            except asyncio.TimeoutError:
                logger.warning(f"System 1 processing timeout for task {task.id}, falling back to System 2")
                return await self._execute_system2_processing(task, agent, context)
                
        except Exception as e:
            logger.error(f"Error in System 1 processing: {e}")
            # Fallback to System 2 on error
            return await self._execute_system2_processing(task, agent, context)
    
    async def _execute_system2_processing(
        self,
        task: IntelligenceTask,
        agent: IntelligenceAgent,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """
        System 2: Slow, deliberate, analytical reasoning for complex problems.
        
        Characteristics:
        - Step-by-step analysis
        - Multiple validation steps
        - Confidence assessment
        - Detailed reasoning trace
        """
        try:
            logger.info(f"Executing System 2 processing for task {task.id}")
            
            # Multi-step analytical processing
            reasoning_steps = []
            
            # Step 1: Problem decomposition
            decomposition = await self.reasoning_engine.decompose_problem(
                task.type, task.description, task.parameters
            )
            reasoning_steps.append(f"Problem decomposed into {len(decomposition)} sub-components")
            
            # Step 2: Analytical processing
            analytical_params = {
                'processing_mode': 'analytical',
                'depth': 'deep',
                'validation': True,
                'confidence_scoring': True,
                'timeout': self.system2_timeout
            }
            
            result = await agent.process_task({
                'id': task.id,
                'type': task.type,
                'description': task.description,
                'parameters': {**task.parameters, **analytical_params}
            })
            
            reasoning_steps.append("Deep analytical processing completed")
            
            # Step 3: Confidence assessment
            confidence = await self._assess_result_confidence(result, context.complexity)
            reasoning_steps.append(f"Confidence assessment: {confidence:.2f}")
            
            # Step 4: Validation if confidence is low
            if confidence < context.confidence_threshold:
                validation_result = await self._validate_result(result, task, agent)
                if validation_result:
                    result = validation_result
                    confidence = await self._assess_result_confidence(result, context.complexity)
                reasoning_steps.append(f"Result validated, new confidence: {confidence:.2f}")
            
            context.system2_result = result
            context.final_decision = result
            context.reasoning_steps = reasoning_steps
            context.decision_factors['confidence'] = confidence
            context.explanation = self._generate_system2_explanation(reasoning_steps, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in System 2 processing: {e}")
            raise
    
    async def _execute_hybrid_processing(
        self,
        task: IntelligenceTask,
        agent: IntelligenceAgent,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """
        Hybrid processing: Combines System 1 and System 2 approaches.
        
        Uses System 1 for initial assessment, then System 2 for validation
        and refinement if needed.
        """
        try:
            logger.info(f"Executing hybrid processing for task {task.id}")
            
            # Phase 1: System 1 initial processing
            system1_result = await self._execute_system1_processing(task, agent, context)
            
            # Phase 2: Confidence check
            confidence = await self._assess_result_confidence(system1_result, context.complexity)
            
            if confidence >= context.confidence_threshold:
                # High confidence System 1 result - use it
                context.final_decision = system1_result
                context.explanation = f"Hybrid processing: System 1 result accepted (confidence: {confidence:.2f})"
                return system1_result
            else:
                # Low confidence - switch to System 2
                logger.info(f"System 1 confidence {confidence:.2f} below threshold, switching to System 2")
                context.reasoning_steps.append(f"Switched to System 2 due to low confidence ({confidence:.2f})")
                
                system2_result = await self._execute_system2_processing(task, agent, context)
                
                context.final_decision = system2_result
                context.explanation = f"Hybrid processing: System 2 validation used (initial confidence: {confidence:.2f})"
                return system2_result
                
        except Exception as e:
            logger.error(f"Error in hybrid processing: {e}")
            raise
    
    async def _check_cached_responses(self, task: IntelligenceTask) -> Optional[Dict[str, Any]]:
        """Check for cached responses from similar tasks"""
        try:
            # Simple cache based on task type and description hash
            cache_key = f"{task.type}:{hash(task.description)}"
            
            # In a real implementation, this would check a persistent cache
            # For now, return None to indicate no cache hit
            return None
            
        except Exception as e:
            logger.error(f"Error checking cached responses: {e}")
            return None
    
    async def _assess_result_confidence(
        self,
        result: Dict[str, Any],
        complexity: TaskComplexity
    ) -> float:
        """Assess confidence in the result based on various factors"""
        try:
            confidence = 0.5  # Base confidence
            
            # Check if result has explicit confidence score
            if isinstance(result, dict) and 'confidence' in result:
                return min(1.0, max(0.0, result['confidence']))
            
            # Assess based on result completeness
            if result.get('success', False):
                confidence += 0.3
            
            if result.get('data') or result.get('intelligence'):
                confidence += 0.2
            
            # Adjust for complexity
            complexity_adjustment = {
                TaskComplexity.SIMPLE: 0.1,
                TaskComplexity.MODERATE: 0.0,
                TaskComplexity.COMPLEX: -0.1,
                TaskComplexity.CRITICAL: -0.2
            }
            
            confidence += complexity_adjustment.get(complexity, 0.0)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error assessing result confidence: {e}")
            return 0.5
    
    async def _validate_result(
        self,
        result: Dict[str, Any],
        task: IntelligenceTask,
        agent: IntelligenceAgent
    ) -> Optional[Dict[str, Any]]:
        """Validate result through additional processing"""
        try:
            # Simple validation - in practice, this could involve:
            # - Cross-checking with other agents
            # - Fact verification
            # - Logical consistency checks
            
            validation_params = {
                'validation_mode': True,
                'cross_check': True
            }
            
            # Re-process with validation
            validated_result = await agent.process_task({
                'id': f"{task.id}_validation",
                'type': task.type,
                'description': f"Validate: {task.description}",
                'parameters': {**task.parameters, **validation_params}
            })
            
            return validated_result
            
        except Exception as e:
            logger.error(f"Error validating result: {e}")
            return None
    
    def _generate_system2_explanation(
        self,
        reasoning_steps: List[str],
        result: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for System 2 processing"""
        try:
            explanation_parts = [
                "System 2 Analytical Processing:",
                "",
                "Reasoning Steps:"
            ]
            
            for i, step in enumerate(reasoning_steps, 1):
                explanation_parts.append(f"{i}. {step}")
            
            explanation_parts.extend([
                "",
                f"Final Result: {result.get('success', 'Unknown')} - {result.get('summary', 'No summary available')}"
            ])
            
            return "\n".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "System 2 processing completed with analytical approach"
    
    async def _update_cognitive_metrics(
        self,
        context: CognitiveContext,
        result: Dict[str, Any],
        processing_time: float
    ):
        """Update cognitive processing metrics"""
        try:
            # Update mode-specific metrics
            if context.cognitive_mode == CognitiveMode.SYSTEM1:
                self.cognitive_metrics['system1_tasks'] += 1
                current_avg = self.cognitive_metrics['avg_system1_time']
                count = self.cognitive_metrics['system1_tasks']
                self.cognitive_metrics['avg_system1_time'] = (
                    (current_avg * (count - 1) + processing_time) / count
                )
            elif context.cognitive_mode == CognitiveMode.SYSTEM2:
                self.cognitive_metrics['system2_tasks'] += 1
                current_avg = self.cognitive_metrics['avg_system2_time']
                count = self.cognitive_metrics['system2_tasks']
                self.cognitive_metrics['avg_system2_time'] = (
                    (current_avg * (count - 1) + processing_time) / count
                )
            elif context.cognitive_mode == CognitiveMode.HYBRID:
                self.cognitive_metrics['hybrid_tasks'] += 1
            
            # Update overall accuracy
            success = result.get('success', False)
            if success:
                current_accuracy = self.cognitive_metrics['cognitive_accuracy']
                total_tasks = sum([
                    self.cognitive_metrics['system1_tasks'],
                    self.cognitive_metrics['system2_tasks'],
                    self.cognitive_metrics['hybrid_tasks']
                ])
                
                if total_tasks > 0:
                    self.cognitive_metrics['cognitive_accuracy'] = (
                        (current_accuracy * (total_tasks - 1) + 1.0) / total_tasks
                    )
            
        except Exception as e:
            logger.error(f"Error updating cognitive metrics: {e}")
    
    async def get_cognitive_status(self) -> Dict[str, Any]:
        """Get cognitive processing status and metrics"""
        try:
            current_load = await self.cognitive_load_tracker.get_current_load()
            
            return {
                'cognitive_load': current_load,
                'active_contexts': len(self.cognitive_contexts),
                'metrics': self.cognitive_metrics,
                'reasoning_history_count': len(self.reasoning_history),
                'system_status': {
                    'system1_enabled': True,
                    'system2_enabled': True,
                    'hybrid_mode_available': True
                },
                'configuration': {
                    'system1_timeout': self.system1_timeout,
                    'system2_timeout': self.system2_timeout,
                    'confidence_threshold': self.confidence_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cognitive status: {e}")
            return {'error': str(e)}


class CognitiveLoadTracker:
    """Tracks cognitive load across the system"""
    
    def __init__(self):
        self.current_load = 0.0
        self.load_history = []
        self.max_history = 1000
    
    async def get_current_load(self) -> float:
        """Get current cognitive load (0.0 to 1.0)"""
        # Simple implementation based on active tasks
        # In practice, this could consider CPU, memory, response times, etc.
        return min(1.0, self.current_load)
    
    async def update_load(self, load_change: float):
        """Update cognitive load"""
        self.current_load = max(0.0, min(1.0, self.current_load + load_change))
        
        self.load_history.append({
            'timestamp': datetime.utcnow(),
            'load': self.current_load
        })
        
        # Keep history size manageable
        if len(self.load_history) > self.max_history:
            self.load_history = self.load_history[-self.max_history:]


class ReasoningEngine:
    """Advanced reasoning engine for System 2 processing"""
    
    async def decompose_problem(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Decompose complex problems into manageable components"""
        try:
            # Basic problem decomposition
            components = []
            
            # Task type specific decomposition
            if task_type == 'osint':
                components = [
                    {'component': 'source_identification', 'description': 'Identify relevant intelligence sources'},
                    {'component': 'data_collection', 'description': 'Collect data from identified sources'},
                    {'component': 'analysis', 'description': 'Analyze collected intelligence'},
                    {'component': 'correlation', 'description': 'Correlate findings across sources'},
                    {'component': 'reporting', 'description': 'Generate intelligence report'}
                ]
            elif task_type == 'investigation':
                components = [
                    {'component': 'evidence_gathering', 'description': 'Gather available evidence'},
                    {'component': 'timeline_construction', 'description': 'Construct event timeline'},
                    {'component': 'hypothesis_formation', 'description': 'Form investigative hypotheses'},
                    {'component': 'hypothesis_testing', 'description': 'Test hypotheses against evidence'},
                    {'component': 'conclusion', 'description': 'Draw conclusions from analysis'}
                ]
            else:
                # Generic decomposition
                components = [
                    {'component': 'analysis', 'description': 'Analyze the problem'},
                    {'component': 'solution', 'description': 'Develop solution approach'},
                    {'component': 'validation', 'description': 'Validate solution'}
                ]
            
            return components
            
        except Exception as e:
            logger.error(f"Error decomposing problem: {e}")
            return [{'component': 'analysis', 'description': 'Analyze and solve the problem'}]