"""
ReAct Agent Implementation

This module implements the ReAct (Reasoning and Acting) framework for intelligence agents.
ReAct combines reasoning traces with task-specific actions for adaptive decision-making.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .intelligence_agent import IntelligenceAgent, AgentStatus


class ReasoningStep(Enum):
    """Reasoning step types in ReAct framework"""
    OBSERVE = "observe"
    THINK = "think"
    ACT = "act"
    REFLECT = "reflect"


class ReactAgent(IntelligenceAgent):
    """
    ReAct-based intelligence agent implementation.
    
    This agent follows the ReAct framework for adaptive reasoning and decision-making
    in intelligence operations.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reasoning_trace = []
        self.current_step = ReasoningStep.OBSERVE
        self.max_reasoning_steps = 10
        self.reasoning_timeout = 300  # 5 minutes
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the ReAct framework.
        
        Args:
            task: Task definition with parameters and context
            
        Returns:
            Task execution results with reasoning trace
        """
        self.logger.info(f"Starting ReAct execution for task: {task.get('id', 'unknown')}")
        
        # Initialize reasoning trace
        self.reasoning_trace = []
        self.current_step = ReasoningStep.OBSERVE
        
        # Start ReAct cycle
        start_time = datetime.utcnow()
        timeout = asyncio.create_task(asyncio.sleep(self.reasoning_timeout))
        
        try:
            while len(self.reasoning_trace) < self.max_reasoning_steps:
                # Check for timeout
                if timeout.done():
                    raise TimeoutError("ReAct reasoning timeout exceeded")
                
                # Execute current reasoning step
                step_result = await self._execute_reasoning_step(task)
                
                # Add to reasoning trace
                self.reasoning_trace.append({
                    'step': self.current_step.value,
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': step_result
                })
                
                # Check if task is complete
                if step_result.get('task_complete', False):
                    break
                
                # Move to next reasoning step
                self.current_step = self._get_next_step(step_result)
            
            # Cancel timeout
            timeout.cancel()
            
            # Compile final result
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result = {
                'task_id': task.get('id'),
                'status': 'completed',
                'execution_time': execution_time,
                'reasoning_trace': self.reasoning_trace,
                'final_result': self.reasoning_trace[-1]['result'] if self.reasoning_trace else None
            }
            
            self.logger.info(f"ReAct execution completed for task: {task.get('id', 'unknown')}")
            return result
            
        except Exception as e:
            # Cancel timeout
            timeout.cancel()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result = {
                'task_id': task.get('id'),
                'status': 'failed',
                'execution_time': execution_time,
                'reasoning_trace': self.reasoning_trace,
                'error': str(e)
            }
            
            self.logger.error(f"ReAct execution failed for task: {task.get('id', 'unknown')}: {e}")
            return result
    
    async def _execute_reasoning_step(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single reasoning step.
        
        Args:
            task: Current task context
            
        Returns:
            Step execution result
        """
        if self.current_step == ReasoningStep.OBSERVE:
            return await self._observe(task)
        elif self.current_step == ReasoningStep.THINK:
            return await self._think(task)
        elif self.current_step == ReasoningStep.ACT:
            return await self._act(task)
        elif self.current_step == ReasoningStep.REFLECT:
            return await self._reflect(task)
        else:
            raise ValueError(f"Unknown reasoning step: {self.current_step}")
    
    async def _observe(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe the current state and gather information.
        
        Args:
            task: Current task context
            
        Returns:
            Observation results
        """
        self.logger.debug(f"Observing for task: {task.get('id', 'unknown')}")
        
        # Gather relevant information
        observations = {
            'task_context': task,
            'agent_status': self.status.value,
            'available_capabilities': self.capabilities,
            'current_time': datetime.utcnow().isoformat()
        }
        
        # Query knowledge sources if available
        if self.vector_service:
            try:
                # Search for relevant information
                search_query = task.get('description', '')
                if search_query:
                    search_results = await self.vector_service.search(
                        query=search_query,
                        limit=5
                    )
                    observations['vector_search_results'] = search_results
            except Exception as e:
                self.logger.warning(f"Vector search failed during observation: {e}")
        
        if self.knowledge_graph:
            try:
                # Query knowledge graph for relevant entities
                entities = task.get('entities', [])
                if entities:
                    graph_results = await self.knowledge_graph.query_entities(entities)
                    observations['knowledge_graph_results'] = graph_results
            except Exception as e:
                self.logger.warning(f"Knowledge graph query failed during observation: {e}")
        
        return {
            'step': 'observe',
            'observations': observations,
            'next_action': 'think'
        }
    
    async def _think(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Think about the observations and plan next actions.
        
        Args:
            task: Current task context
            
        Returns:
            Thinking results
        """
        self.logger.debug(f"Thinking for task: {task.get('id', 'unknown')}")
        
        # Get the latest observations
        latest_observations = self.reasoning_trace[-1]['result']['observations'] if self.reasoning_trace else {}
        
        # Use LLM for reasoning if available
        if self.llm_service:
            try:
                # Create reasoning prompt
                reasoning_prompt = self._create_reasoning_prompt(task, latest_observations)
                
                # Get LLM reasoning
                reasoning_result = await self.llm_service.generate(
                    prompt=reasoning_prompt,
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Parse reasoning result
                reasoning = self._parse_reasoning_result(reasoning_result)
                
                return {
                    'step': 'think',
                    'reasoning': reasoning,
                    'next_action': reasoning.get('next_action', 'act')
                }
                
            except Exception as e:
                self.logger.warning(f"LLM reasoning failed: {e}")
                # Fallback to simple reasoning
                return self._simple_reasoning(task, latest_observations)
        else:
            # Fallback to simple reasoning
            return self._simple_reasoning(task, latest_observations)
    
    async def _act(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute actions based on reasoning.
        
        Args:
            task: Current task context
            
        Returns:
            Action execution results
        """
        self.logger.debug(f"Acting for task: {task.get('id', 'unknown')}")
        
        # Get the latest reasoning
        latest_reasoning = self.reasoning_trace[-1]['result'] if self.reasoning_trace else {}
        
        # Determine actions to take
        actions = latest_reasoning.get('reasoning', {}).get('actions', [])
        
        if not actions:
            # Default action based on task type
            actions = self._get_default_actions(task)
        
        # Execute actions
        action_results = []
        for action in actions:
            try:
                result = await self._execute_action(action, task)
                action_results.append({
                    'action': action,
                    'result': result,
                    'status': 'success'
                })
            except Exception as e:
                self.logger.error(f"Action execution failed: {e}")
                action_results.append({
                    'action': action,
                    'result': None,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Determine if task is complete
        task_complete = self._evaluate_task_completion(task, action_results)
        
        return {
            'step': 'act',
            'actions': action_results,
            'task_complete': task_complete,
            'next_action': 'reflect' if task_complete else 'observe'
        }
    
    async def _reflect(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect on the results and determine next steps.
        
        Args:
            task: Current task context
            
        Returns:
            Reflection results
        """
        self.logger.debug(f"Reflecting for task: {task.get('id', 'unknown')}")
        
        # Get the latest action results
        latest_actions = self.reasoning_trace[-1]['result'] if self.reasoning_trace else {}
        
        # Use LLM for reflection if available
        if self.llm_service:
            try:
                # Create reflection prompt
                reflection_prompt = self._create_reflection_prompt(task, latest_actions)
                
                # Get LLM reflection
                reflection_result = await self.llm_service.generate(
                    prompt=reflection_prompt,
                    max_tokens=300,
                    temperature=0.5
                )
                
                # Parse reflection result
                reflection = self._parse_reflection_result(reflection_result)
                
                return {
                    'step': 'reflect',
                    'reflection': reflection,
                    'next_action': reflection.get('next_action', 'observe')
                }
                
            except Exception as e:
                self.logger.warning(f"LLM reflection failed: {e}")
                # Fallback to simple reflection
                return self._simple_reflection(task, latest_actions)
        else:
            # Fallback to simple reflection
            return self._simple_reflection(task, latest_actions)
    
    def _get_next_step(self, step_result: Dict[str, Any]) -> ReasoningStep:
        """Determine the next reasoning step based on current result."""
        next_action = step_result.get('next_action', 'observe')
        
        if next_action == 'think':
            return ReasoningStep.THINK
        elif next_action == 'act':
            return ReasoningStep.ACT
        elif next_action == 'reflect':
            return ReasoningStep.REFLECT
        else:
            return ReasoningStep.OBSERVE
    
    def _create_reasoning_prompt(self, task: Dict[str, Any], observations: Dict[str, Any]) -> str:
        """Create a reasoning prompt for the LLM."""
        return f"""
You are an intelligence agent analyzing a task. Based on the observations, think about what actions to take.

Task: {task.get('description', 'No description')}
Task Type: {task.get('type', 'unknown')}
Agent Capabilities: {', '.join(self.capabilities)}

Observations:
{self._format_observations(observations)}

Think about:
1. What information do you need to complete this task?
2. What actions can you take with your current capabilities?
3. What is the best approach to solve this task?

Provide your reasoning in JSON format:
{{
    "analysis": "Your analysis of the situation",
    "actions": ["action1", "action2", "action3"],
    "next_action": "think|act|observe|reflect"
}}
"""
    
    def _create_reflection_prompt(self, task: Dict[str, Any], actions: Dict[str, Any]) -> str:
        """Create a reflection prompt for the LLM."""
        return f"""
You are an intelligence agent reflecting on completed actions. Analyze the results and determine next steps.

Task: {task.get('description', 'No description')}
Actions Taken: {actions.get('actions', [])}

Reflect on:
1. Were the actions successful?
2. What did you learn from the results?
3. What should you do next?

Provide your reflection in JSON format:
{{
    "evaluation": "Your evaluation of the actions",
    "lessons_learned": "What you learned",
    "next_action": "think|act|observe|reflect|complete"
}}
"""
    
    def _parse_reasoning_result(self, result: str) -> Dict[str, Any]:
        """Parse LLM reasoning result."""
        try:
            import json
            return json.loads(result)
        except:
            return {
                "analysis": result,
                "actions": [],
                "next_action": "act"
            }
    
    def _parse_reflection_result(self, result: str) -> Dict[str, Any]:
        """Parse LLM reflection result."""
        try:
            import json
            return json.loads(result)
        except:
            return {
                "evaluation": result,
                "lessons_learned": "",
                "next_action": "observe"
            }
    
    def _format_observations(self, observations: Dict[str, Any]) -> str:
        """Format observations for display."""
        formatted = []
        for key, value in observations.items():
            if isinstance(value, (dict, list)):
                formatted.append(f"{key}: {str(value)[:200]}...")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
    
    def _simple_reasoning(self, task: Dict[str, Any], observations: Dict[str, Any]) -> Dict[str, Any]:
        """Simple reasoning fallback when LLM is not available."""
        return {
            'step': 'think',
            'reasoning': {
                'analysis': f"Analyzing task: {task.get('description', 'No description')}",
                'actions': ['execute_task'],
                'next_action': 'act'
            },
            'next_action': 'act'
        }
    
    def _simple_reflection(self, task: Dict[str, Any], actions: Dict[str, Any]) -> Dict[str, Any]:
        """Simple reflection fallback when LLM is not available."""
        return {
            'step': 'reflect',
            'reflection': {
                'evaluation': "Actions completed",
                'lessons_learned': "Task processing completed",
                'next_action': 'complete'
            },
            'next_action': 'complete'
        }
    
    def _get_default_actions(self, task: Dict[str, Any]) -> List[str]:
        """Get default actions based on task type."""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'osint':
            return ['collect_data', 'analyze_data', 'generate_report']
        elif task_type == 'investigation':
            return ['gather_evidence', 'analyze_connections', 'build_timeline']
        elif task_type == 'forensics':
            return ['acquire_evidence', 'extract_artifacts', 'analyze_timeline']
        else:
            return ['process_task']
    
    async def _execute_action(self, action: str, task: Dict[str, Any]) -> Any:
        """Execute a specific action."""
        # This is a placeholder - subclasses should override this method
        self.logger.info(f"Executing action: {action}")
        return {"action": action, "status": "completed"}
    
    def _evaluate_task_completion(self, task: Dict[str, Any], action_results: List[Dict[str, Any]]) -> bool:
        """Evaluate if the task is complete based on action results."""
        # Simple completion logic - subclasses should override this
        return len(action_results) > 0 and all(
            result.get('status') == 'success' for result in action_results
        )