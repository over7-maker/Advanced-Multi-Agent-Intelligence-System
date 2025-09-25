"""
Base Intelligence Agent Class

This module contains the base class for all intelligence agents in the AMAS system.
It provides common functionality and interfaces that all specialized agents inherit.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

from ..base.agent_communication import AgentCommunication


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class IntelligenceAgent(ABC):
    """
    Base class for all intelligence agents in the AMAS system.
    
    This class provides the foundation for specialized intelligence agents,
    implementing common functionality and interfaces.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None
    ):
        """
        Initialize the intelligence agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            capabilities: List of capabilities this agent provides
            llm_service: LLM service for AI operations
            vector_service: Vector service for semantic search
            knowledge_graph: Knowledge graph service
            security_service: Security service for access control
        """
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        # Service dependencies
        self.llm_service = llm_service
        self.vector_service = vector_service
        self.knowledge_graph = knowledge_graph
        self.security_service = security_service
        
        # Communication
        self.communication = AgentCommunication(self.agent_id)
        
        # Logging
        self.logger = logging.getLogger(f"amas.intelligence.{self.agent_id}")
        
        # Task management
        self.current_task = None
        self.task_history = []
        
        # Performance metrics
        self.metrics = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_response_time': 0.0,
            'last_activity': self.last_activity
        }
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task specific to this agent's capabilities.
        
        Args:
            task: Task definition with parameters and context
            
        Returns:
            Task execution results
        """
        pass
    
    @abstractmethod
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate if this agent can handle the given task.
        
        Args:
            task: Task definition to validate
            
        Returns:
            True if agent can handle the task, False otherwise
        """
        pass
    
    async def start(self) -> bool:
        """
        Start the agent and initialize resources.
        
        Returns:
            True if agent started successfully, False otherwise
        """
        try:
            self.logger.info(f"Starting agent {self.agent_id}")
            self.status = AgentStatus.ACTIVE
            await self._initialize_resources()
            self.logger.info(f"Agent {self.agent_id} started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start agent {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """
        Stop the agent and cleanup resources.
        
        Returns:
            True if agent stopped successfully, False otherwise
        """
        try:
            self.logger.info(f"Stopping agent {self.agent_id}")
            await self._cleanup_resources()
            self.status = AgentStatus.OFFLINE
            self.logger.info(f"Agent {self.agent_id} stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop agent {self.agent_id}: {e}")
            return False
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task through the agent's workflow.
        
        Args:
            task: Task definition to process
            
        Returns:
            Task execution results
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate task
            if not await self.validate_task(task):
                raise ValueError(f"Agent {self.agent_id} cannot handle task: {task}")
            
            # Update status
            self.status = AgentStatus.BUSY
            self.current_task = task
            
            # Execute task
            self.logger.info(f"Processing task {task.get('id', 'unknown')} with agent {self.agent_id}")
            result = await self.execute_task(task)
            
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(execution_time, success=True)
            
            # Update status
            self.status = AgentStatus.ACTIVE
            self.current_task = None
            self.last_activity = datetime.utcnow()
            
            # Add to task history
            self.task_history.append({
                'task_id': task.get('id'),
                'execution_time': execution_time,
                'status': 'completed',
                'timestamp': datetime.utcnow()
            })
            
            self.logger.info(f"Task {task.get('id', 'unknown')} completed successfully")
            return result
            
        except Exception as e:
            # Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_metrics(execution_time, success=False)
            
            # Update status
            self.status = AgentStatus.ERROR
            self.current_task = None
            
            # Add to task history
            self.task_history.append({
                'task_id': task.get('id'),
                'execution_time': execution_time,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow()
            })
            
            self.logger.error(f"Task {task.get('id', 'unknown')} failed: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metrics.
        
        Returns:
            Agent status information
        """
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'status': self.status.value,
            'capabilities': self.capabilities,
            'current_task': self.current_task,
            'metrics': self.metrics,
            'last_activity': self.last_activity.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    async def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities.
        
        Returns:
            List of agent capabilities
        """
        return self.capabilities
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent.
        
        Returns:
            Health check results
        """
        try:
            # Check service dependencies
            health_status = {
                'agent_id': self.agent_id,
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'dependencies': {}
            }
            
            # Check LLM service
            if self.llm_service:
                try:
                    await self.llm_service.health_check()
                    health_status['dependencies']['llm_service'] = 'healthy'
                except Exception as e:
                    health_status['dependencies']['llm_service'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'
            
            # Check vector service
            if self.vector_service:
                try:
                    await self.vector_service.health_check()
                    health_status['dependencies']['vector_service'] = 'healthy'
                except Exception as e:
                    health_status['dependencies']['vector_service'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'
            
            # Check knowledge graph
            if self.knowledge_graph:
                try:
                    await self.knowledge_graph.health_check()
                    health_status['dependencies']['knowledge_graph'] = 'healthy'
                except Exception as e:
                    health_status['dependencies']['knowledge_graph'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed for agent {self.agent_id}: {e}")
            return {
                'agent_id': self.agent_id,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _initialize_resources(self):
        """Initialize agent-specific resources."""
        pass
    
    async def _cleanup_resources(self):
        """Cleanup agent-specific resources."""
        pass
    
    def _update_metrics(self, execution_time: float, success: bool):
        """Update agent performance metrics."""
        if success:
            self.metrics['tasks_completed'] += 1
        else:
            self.metrics['tasks_failed'] += 1
        
        # Update average response time
        total_tasks = self.metrics['tasks_completed'] + self.metrics['tasks_failed']
        if total_tasks > 0:
            current_avg = self.metrics['average_response_time']
            self.metrics['average_response_time'] = (
                (current_avg * (total_tasks - 1) + execution_time) / total_tasks
            )
        
        self.metrics['last_activity'] = self.last_activity