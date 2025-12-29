"""
Collaboration Patterns for Multi-Agent Systems
Implements various collaboration patterns for agent coordination
"""

import asyncio
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CollaborationPattern(str, Enum):
    """Types of collaboration patterns"""
    
    SEQUENTIAL = "sequential"  # Agent1 → Agent2 → Agent3
    PARALLEL = "parallel"  # Agent1, Agent2, Agent3 (parallel)
    HIERARCHICAL = "hierarchical"  # Coordinator → Workers
    PEER_TO_PEER = "peer_to_peer"  # Direct agent communication


class CollaborationManager:
    """
    Manager for agent collaboration patterns
    
    Implements:
    - Sequential: Agents execute one after another
    - Parallel: Agents execute concurrently
    - Hierarchical: Coordinator distributes work to workers
    - Peer-to-Peer: Agents communicate directly
    """
    
    def __init__(self):
        self._collaboration_history: List[Dict[str, Any]] = []
        logger.info("CollaborationManager initialized")
    
    async def execute_sequential(
        self,
        agents: List[Any],  # List of agent instances
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially
        Each agent receives the output of the previous agent
        
        Args:
            agents: List of agent instances to execute
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            
        Returns:
            Final result from last agent
        """
        logger.info(f"Sequential collaboration started: {len(agents)} agents")
        
        results = []
        current_input = parameters.copy()
        
        for i, agent in enumerate(agents):
            try:
                logger.info(f"Executing agent {i+1}/{len(agents)}: {agent.name}")
                
                # Execute agent with current input
                result = await agent.execute(
                    task_id=f"{task_id}_seq_{i}",
                    target=target,
                    parameters=current_input,
                )
                
                results.append({
                    "agent": agent.name,
                    "agent_id": agent.id,
                    "result": result,
                    "success": result.get("success", False),
                })
                
                # If agent failed, stop sequential execution
                if not result.get("success", False):
                    logger.warning(f"Agent {agent.name} failed, stopping sequential execution")
                    break
                
                # Prepare input for next agent (use output from current agent)
                if "output" in result:
                    current_input = {
                        **parameters,
                        "previous_output": result["output"],
                        "previous_agent": agent.name,
                    }
                
            except Exception as e:
                logger.error(f"Error executing agent {agent.name}: {e}", exc_info=True)
                results.append({
                    "agent": agent.name,
                    "agent_id": agent.id,
                    "error": str(e),
                    "success": False,
                })
                break
        
        # Aggregate results
        aggregated_result = self._aggregate_sequential_results(results)
        
        # Record collaboration
        self._record_collaboration(
            pattern=CollaborationPattern.SEQUENTIAL,
            task_id=task_id,
            agents=[agent.name for agent in agents],
            results=aggregated_result,
        )
        
        logger.info(f"Sequential collaboration completed: {aggregated_result.get('success_count', 0)}/{len(agents)} successful")
        
        return aggregated_result
    
    async def execute_parallel(
        self,
        agents: List[Any],
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute agents in parallel
        All agents work concurrently
        
        Args:
            agents: List of agent instances to execute
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            
        Returns:
            Aggregated results from all agents
        """
        logger.info(f"Parallel collaboration started: {len(agents)} agents")
        
        # Create tasks for all agents
        tasks = []
        for i, agent in enumerate(agents):
            task = agent.execute(
                task_id=f"{task_id}_par_{i}",
                target=target,
                parameters=parameters.copy(),
            )
            tasks.append((agent, task))
        
        # Execute all tasks concurrently
        results = []
        agent_results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        # Process results
        for (agent, _), result in zip(tasks, agent_results):
            if isinstance(result, Exception):
                logger.error(f"Agent {agent.name} raised exception: {result}")
                results.append({
                    "agent": agent.name,
                    "agent_id": agent.id,
                    "error": str(result),
                    "success": False,
                })
            else:
                results.append({
                    "agent": agent.name,
                    "agent_id": agent.id,
                    "result": result,
                    "success": result.get("success", False),
                })
        
        # Aggregate results
        aggregated_result = self._aggregate_parallel_results(results)
        
        # Record collaboration
        self._record_collaboration(
            pattern=CollaborationPattern.PARALLEL,
            task_id=task_id,
            agents=[agent.name for agent in agents],
            results=aggregated_result,
        )
        
        logger.info(f"Parallel collaboration completed: {aggregated_result.get('success_count', 0)}/{len(agents)} successful")
        
        return aggregated_result
    
    async def execute_hierarchical(
        self,
        coordinator: Any,
        workers: List[Any],
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute hierarchical collaboration
        Coordinator distributes subtasks to workers
        
        Args:
            coordinator: Coordinator agent
            workers: List of worker agents
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            
        Returns:
            Aggregated results
        """
        logger.info(f"Hierarchical collaboration started: 1 coordinator, {len(workers)} workers")
        
        # Step 1: Coordinator analyzes task and creates subtasks
        try:
            coord_result = await coordinator.execute(
                task_id=f"{task_id}_coord",
                target=target,
                parameters={
                    **parameters,
                    "mode": "coordination",
                    "workers": [w.name for w in workers],
                },
            )
            
            # Extract subtasks from coordinator result
            subtasks = coord_result.get("output", {}).get("subtasks", [])
            
            if not subtasks:
                # Fallback: create subtask for each worker
                subtasks = [
                    {"worker_id": i, "parameters": parameters}
                    for i in range(len(workers))
                ]
            
        except Exception as e:
            logger.error(f"Coordinator {coordinator.name} failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Coordinator failed: {str(e)}",
                "pattern": "hierarchical",
            }
        
        # Step 2: Distribute subtasks to workers
        worker_tasks = []
        for i, (worker, subtask) in enumerate(zip(workers, subtasks)):
            task = worker.execute(
                task_id=f"{task_id}_worker_{i}",
                target=target,
                parameters=subtask.get("parameters", parameters),
            )
            worker_tasks.append((worker, task))
        
        # Execute all worker tasks concurrently
        worker_results = await asyncio.gather(
            *[task for _, task in worker_tasks],
            return_exceptions=True
        )
        
        # Process worker results
        results = []
        for (worker, _), result in zip(worker_tasks, worker_results):
            if isinstance(result, Exception):
                logger.error(f"Worker {worker.name} raised exception: {result}")
                results.append({
                    "agent": worker.name,
                    "agent_id": worker.id,
                    "error": str(result),
                    "success": False,
                })
            else:
                results.append({
                    "agent": worker.name,
                    "agent_id": worker.id,
                    "result": result,
                    "success": result.get("success", False),
                })
        
        # Step 3: Coordinator aggregates results
        try:
            final_result = await coordinator.execute(
                task_id=f"{task_id}_aggregate",
                target=target,
                parameters={
                    **parameters,
                    "mode": "aggregation",
                    "worker_results": results,
                },
            )
        except Exception as e:
            logger.error(f"Coordinator aggregation failed: {e}")
            # Fallback aggregation
            final_result = self._aggregate_parallel_results(results)
        
        # Record collaboration
        self._record_collaboration(
            pattern=CollaborationPattern.HIERARCHICAL,
            task_id=task_id,
            agents=[coordinator.name] + [w.name for w in workers],
            results=final_result,
        )
        
        logger.info(f"Hierarchical collaboration completed")
        
        return final_result
    
    async def execute_peer_to_peer(
        self,
        agents: List[Any],
        task_id: str,
        target: str,
        parameters: Dict[str, Any],
        communication_rounds: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute peer-to-peer collaboration
        Agents communicate directly with each other
        
        Args:
            agents: List of agent instances
            task_id: Task identifier
            target: Target of the task
            parameters: Task parameters
            communication_rounds: Number of communication rounds
            
        Returns:
            Aggregated results
        """
        logger.info(f"Peer-to-peer collaboration started: {len(agents)} agents, {communication_rounds} rounds")
        
        results = []
        shared_knowledge = {}
        
        for round_num in range(communication_rounds):
            logger.info(f"P2P Round {round_num + 1}/{communication_rounds}")
            
            # Each agent executes with shared knowledge
            round_results = []
            tasks = []
            
            for i, agent in enumerate(agents):
                task = agent.execute(
                    task_id=f"{task_id}_p2p_r{round_num}_a{i}",
                    target=target,
                    parameters={
                        **parameters,
                        "shared_knowledge": shared_knowledge.copy(),
                        "round": round_num,
                    },
                )
                tasks.append((agent, task))
            
            # Execute all agents concurrently
            agent_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            # Process results and update shared knowledge
            for (agent, _), result in zip(tasks, agent_results):
                if isinstance(result, Exception):
                    logger.error(f"Agent {agent.name} raised exception: {result}")
                    round_results.append({
                        "agent": agent.name,
                        "agent_id": agent.id,
                        "error": str(result),
                        "success": False,
                    })
                else:
                    round_results.append({
                        "agent": agent.name,
                        "agent_id": agent.id,
                        "result": result,
                        "success": result.get("success", False),
                    })
                    
                    # Share agent's findings
                    if result.get("success") and "output" in result:
                        shared_knowledge[agent.id] = result["output"]
            
            results.append({
                "round": round_num + 1,
                "results": round_results,
            })
        
        # Aggregate all results
        all_agent_results = []
        for round_data in results:
            all_agent_results.extend(round_data["results"])
        
        aggregated_result = self._aggregate_parallel_results(all_agent_results)
        aggregated_result["communication_rounds"] = communication_rounds
        aggregated_result["shared_knowledge"] = shared_knowledge
        
        # Record collaboration
        self._record_collaboration(
            pattern=CollaborationPattern.PEER_TO_PEER,
            task_id=task_id,
            agents=[agent.name for agent in agents],
            results=aggregated_result,
        )
        
        logger.info(f"Peer-to-peer collaboration completed after {communication_rounds} rounds")
        
        return aggregated_result
    
    def _aggregate_sequential_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from sequential execution"""
        success_count = sum(1 for r in results if r.get("success", False))
        
        # Get final result (from last successful agent)
        final_output = None
        for r in reversed(results):
            if r.get("success") and "result" in r:
                final_output = r["result"].get("output")
                break
        
        return {
            "success": success_count > 0,
            "pattern": "sequential",
            "agent_results": results,
            "success_count": success_count,
            "total_agents": len(results),
            "final_output": final_output,
        }
    
    def _aggregate_parallel_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from parallel execution"""
        success_count = sum(1 for r in results if r.get("success", False))
        
        # Collect all outputs
        all_outputs = {}
        for r in results:
            if r.get("success") and "result" in r:
                agent_name = r.get("agent", "unknown")
                all_outputs[agent_name] = r["result"].get("output")
        
        return {
            "success": success_count > 0,
            "pattern": "parallel",
            "agent_results": results,
            "success_count": success_count,
            "total_agents": len(results),
            "all_outputs": all_outputs,
        }
    
    def _record_collaboration(
        self,
        pattern: CollaborationPattern,
        task_id: str,
        agents: List[str],
        results: Dict[str, Any],
    ) -> None:
        """Record collaboration in history"""
        self._collaboration_history.append({
            "pattern": pattern.value,
            "task_id": task_id,
            "agents": agents,
            "results": results,
            "timestamp": asyncio.get_event_loop().time(),
        })
        
        # Limit history size
        if len(self._collaboration_history) > 1000:
            self._collaboration_history = self._collaboration_history[-1000:]
    
    def get_collaboration_history(
        self,
        pattern: Optional[CollaborationPattern] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get collaboration history"""
        history = self._collaboration_history.copy()
        
        if pattern:
            history = [h for h in history if h["pattern"] == pattern.value]
        
        return history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        total = len(self._collaboration_history)
        
        pattern_counts = {}
        for h in self._collaboration_history:
            pattern = h["pattern"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return {
            "total_collaborations": total,
            "pattern_counts": pattern_counts,
            "history_size": total,
        }


# Global collaboration manager instance
_collaboration_manager: Optional[CollaborationManager] = None


def get_collaboration_manager() -> CollaborationManager:
    """Get or create global collaboration manager"""
    global _collaboration_manager
    
    if _collaboration_manager is None:
        _collaboration_manager = CollaborationManager()
    
    return _collaboration_manager

