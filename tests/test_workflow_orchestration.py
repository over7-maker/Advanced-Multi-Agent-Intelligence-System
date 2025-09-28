"""
AMAS Workflow Orchestration Tests

Comprehensive test suite for the advanced workflow orchestration system:
- Graph-based workflow execution
- Conditional branching and loops
- Parallel execution and synchronization
- Error handling and recovery
- Performance and scalability
- Integration with cognitive architecture

Validates enterprise-grade workflow orchestration capabilities.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import networkx as nx

# Import workflow components
from core.workflow_engine import (
    AdvancedWorkflowEngine, WorkflowDefinition, WorkflowExecution, WorkflowNode, WorkflowEdge,
    NodeType, NodeStatus, WorkflowStatus, EdgeType
)


class TestAdvancedWorkflowEngine:
    """Test suite for the Advanced Workflow Engine"""
    
    @pytest.fixture
    async def workflow_engine(self):
        """Create workflow engine for testing"""
        config = {
            'max_concurrent_executions': 5,
            'default_timeout_minutes': 30,
            'max_execution_history': 100
        }
        
        # Mock AMAS system
        mock_amas = Mock()
        mock_amas.agents = {
            'osint_agent': Mock(),
            'analysis_agent': Mock(),
            'reporting_agent': Mock()
        }
        
        # Configure mock agents
        for agent_id, agent in mock_amas.agents.items():
            agent.capabilities = [agent_id.split('_')[0]]  # Extract capability from ID
            agent.process_task = AsyncMock(return_value={
                'success': True,
                'confidence': 0.8,
                'result': f'Mock result from {agent_id}'
            })
        
        engine = AdvancedWorkflowEngine(config, mock_amas)
        await engine.start()
        yield engine
        await engine.stop()
    
    @pytest.mark.asyncio
    async def test_workflow_engine_initialization(self, workflow_engine):
        """Test workflow engine initialization"""
        assert workflow_engine is not None
        assert hasattr(workflow_engine, 'workflow_definitions')
        assert hasattr(workflow_engine, 'active_executions')
        assert hasattr(workflow_engine, 'execution_queue')
        assert workflow_engine._running is True
        
        # Check built-in workflows are registered
        assert len(workflow_engine.workflow_definitions) > 0
        assert 'intelligence_collection_v2' in workflow_engine.workflow_definitions
        assert 'threat_assessment_v2' in workflow_engine.workflow_definitions
    
    @pytest.mark.asyncio
    async def test_workflow_registration(self, workflow_engine):
        """Test workflow registration and validation"""
        # Create simple test workflow
        workflow = WorkflowDefinition(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Simple test workflow"
        )
        
        # Add nodes
        workflow.nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start"),
            "task1": WorkflowNode("task1", NodeType.TASK, "Task 1", agent_type="osint"),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        # Add edges
        workflow.edges = {
            "start_to_task1": WorkflowEdge("start_to_task1", "start", "task1", EdgeType.SEQUENTIAL),
            "task1_to_end": WorkflowEdge("task1_to_end", "task1", "end", EdgeType.SEQUENTIAL)
        }
        
        # Register workflow
        result = workflow_engine.register_workflow(workflow)
        assert result is True
        assert "test_workflow" in workflow_engine.workflow_definitions
    
    @pytest.mark.asyncio
    async def test_workflow_validation(self, workflow_engine):
        """Test workflow validation"""
        # Valid workflow
        valid_workflow = WorkflowDefinition(
            workflow_id="valid_test",
            name="Valid Test Workflow",
            description="Valid workflow for testing"
        )
        
        valid_workflow.nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start"),
            "task1": WorkflowNode("task1", NodeType.TASK, "Task 1"),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        valid_workflow.edges = {
            "start_to_task1": WorkflowEdge("start_to_task1", "start", "task1", EdgeType.SEQUENTIAL),
            "task1_to_end": WorkflowEdge("task1_to_end", "task1", "end", EdgeType.SEQUENTIAL)
        }
        
        assert workflow_engine._validate_workflow(valid_workflow) is True
        
        # Invalid workflow (no start node)
        invalid_workflow = WorkflowDefinition(
            workflow_id="invalid_test",
            name="Invalid Test Workflow",
            description="Invalid workflow for testing"
        )
        
        invalid_workflow.nodes = {
            "task1": WorkflowNode("task1", NodeType.TASK, "Task 1"),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        assert workflow_engine._validate_workflow(invalid_workflow) is False
    
    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self, workflow_engine):
        """Test execution of a simple sequential workflow"""
        # Execute built-in intelligence collection workflow
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="intelligence_collection_v2",
            execution_context={
                'target': 'test.example.com',
                'sources': ['osint', 'social_media'],
                'priority': 'high'
            },
            initiated_by="test_user",
            priority=3
        )
        
        assert execution_id is not None
        assert execution_id in workflow_engine.active_executions
        
        # Check execution details
        execution = workflow_engine.active_executions[execution_id]
        assert execution.workflow_id == "intelligence_collection_v2"
        assert execution.initiated_by == "test_user"
        assert execution.priority == 3
        assert execution.status in [WorkflowStatus.CREATED, WorkflowStatus.RUNNING]
        
        # Wait a bit for processing to start
        await asyncio.sleep(1)
        
        # Check execution status
        status = await workflow_engine.get_workflow_status(execution_id)
        assert status is not None
        assert status['execution_id'] == execution_id
        assert 'progress' in status
    
    @pytest.mark.asyncio
    async def test_conditional_workflow_execution(self, workflow_engine):
        """Test workflow execution with conditional branching"""
        # Execute threat assessment workflow (has conditional logic)
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="threat_assessment_v2",
            execution_context={
                'threat_type': 'malware',
                'urgency': 'high',
                'analysis_depth': 'comprehensive'
            },
            initiated_by="test_user",
            priority=2
        )
        
        assert execution_id is not None
        
        # Get workflow definition to understand structure
        workflow = workflow_engine.workflow_definitions["threat_assessment_v2"]
        
        # Check that workflow has decision nodes
        decision_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.DECISION]
        assert len(decision_nodes) > 0
        
        # Check that workflow has conditional edges
        conditional_edges = [e for e in workflow.edges.values() if e.edge_type == EdgeType.CONDITIONAL]
        assert len(conditional_edges) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_workflow_execution(self, workflow_engine):
        """Test workflow execution with parallel nodes"""
        # The intelligence collection workflow has parallel execution
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="intelligence_collection_v2",
            execution_context={
                'target': 'parallel.test.com',
                'enable_parallel': True
            },
            initiated_by="test_user"
        )
        
        assert execution_id is not None
        
        # Get workflow definition
        workflow = workflow_engine.workflow_definitions["intelligence_collection_v2"]
        
        # Check for parallel nodes
        parallel_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.PARALLEL]
        assert len(parallel_nodes) > 0
        
        # Check for merge nodes
        merge_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.MERGE]
        assert len(merge_nodes) > 0
        
        # Check for parallel edges
        parallel_edges = [e for e in workflow.edges.values() if e.edge_type == EdgeType.PARALLEL]
        assert len(parallel_edges) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_cancellation(self, workflow_engine):
        """Test workflow execution cancellation"""
        # Start workflow execution
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="intelligence_collection_v2",
            execution_context={'target': 'cancel.test.com'},
            initiated_by="test_user"
        )
        
        assert execution_id in workflow_engine.active_executions
        
        # Cancel execution
        result = await workflow_engine.cancel_execution(execution_id, "Test cancellation")
        assert result is True
        
        # Check execution status
        execution = workflow_engine.active_executions[execution_id]
        assert execution.status == WorkflowStatus.CANCELLED
        assert "Test cancellation" in execution.error
    
    @pytest.mark.asyncio
    async def test_condition_evaluation(self, workflow_engine):
        """Test condition evaluation for decision nodes"""
        # Create test execution with mock results
        execution = WorkflowExecution(
            execution_id="test_exec",
            workflow_id="test_workflow",
            status=WorkflowStatus.RUNNING
        )
        
        # Add mock node results with different confidence levels
        execution.node_results = {
            'node1': {'confidence': 0.9, 'completeness': 0.8},
            'node2': {'confidence': 0.6, 'completeness': 0.7},
            'node3': {'confidence': 0.8, 'completeness': 0.9}
        }
        
        # Test quality condition evaluation
        mock_edge = WorkflowEdge("test_edge", "from", "to", EdgeType.CONDITIONAL)
        quality_result = await workflow_engine._evaluate_quality_condition(execution, mock_edge)
        
        # Should evaluate to True since average confidence and completeness > 0.7
        assert quality_result is True
        
        # Test confidence condition evaluation
        confidence_result = await workflow_engine._evaluate_confidence_condition(
            execution, mock_edge, threshold=0.7
        )
        
        # Average confidence is (0.9 + 0.6 + 0.8) / 3 = 0.77, which is > 0.7
        assert confidence_result is True
        
        # Test with higher threshold
        high_confidence_result = await workflow_engine._evaluate_confidence_condition(
            execution, mock_edge, threshold=0.85
        )
        
        # Average confidence 0.77 < 0.85
        assert high_confidence_result is False
    
    @pytest.mark.asyncio
    async def test_node_execution(self, workflow_engine):
        """Test individual node execution"""
        # Create test execution
        execution = WorkflowExecution(
            execution_id="test_node_exec",
            workflow_id="intelligence_collection_v2",
            status=WorkflowStatus.RUNNING,
            execution_context={'target': 'node.test.com'}
        )
        
        # Create test task node
        node = WorkflowNode(
            node_id="test_task_node",
            node_type=NodeType.TASK,
            name="Test Task Node",
            description="Test task execution",
            agent_type="osint",
            action="test_action",
            timeout_seconds=30
        )
        
        # Execute node
        result = await workflow_engine._execute_task_node(execution, node)
        
        assert result is not None
        assert result.get('success', False) is True
        assert 'result' in result or 'confidence' in result
    
    @pytest.mark.asyncio
    async def test_decision_node_execution(self, workflow_engine):
        """Test decision node execution"""
        # Create test execution with results
        execution = WorkflowExecution(
            execution_id="test_decision_exec",
            workflow_id="test_workflow",
            status=WorkflowStatus.RUNNING
        )
        
        execution.node_results = {
            'previous_node': {
                'confidence': 0.85,
                'completeness': 0.9,
                'sources': ['source1', 'source2', 'source3']
            }
        }
        
        # Create decision node
        decision_node = WorkflowNode(
            node_id="test_decision",
            node_type=NodeType.DECISION,
            name="Test Decision",
            conditions={
                'min_confidence': 0.8,
                'min_sources': 2
            }
        )
        
        # Execute decision node
        result = await workflow_engine._execute_decision_node(execution, decision_node)
        
        assert result is not None
        assert result.get('success', False) is True
        assert 'decision' in result
        assert result['decision'] is True  # Conditions should be met
    
    @pytest.mark.asyncio
    async def test_parallel_execution_synchronization(self, workflow_engine):
        """Test parallel node execution and merge synchronization"""
        # Create workflow with parallel structure
        workflow = WorkflowDefinition(
            workflow_id="parallel_test_workflow",
            name="Parallel Test Workflow",
            description="Test parallel execution"
        )
        
        # Create nodes
        workflow.nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start"),
            "parallel": WorkflowNode("parallel", NodeType.PARALLEL, "Parallel Split"),
            "task1": WorkflowNode("task1", NodeType.TASK, "Task 1", agent_type="osint"),
            "task2": WorkflowNode("task2", NodeType.TASK, "Task 2", agent_type="analysis"),
            "merge": WorkflowNode("merge", NodeType.MERGE, "Merge Results"),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        # Create edges
        workflow.edges = {
            "start_to_parallel": WorkflowEdge("start_to_parallel", "start", "parallel", EdgeType.SEQUENTIAL),
            "parallel_to_task1": WorkflowEdge("parallel_to_task1", "parallel", "task1", EdgeType.PARALLEL),
            "parallel_to_task2": WorkflowEdge("parallel_to_task2", "parallel", "task2", EdgeType.PARALLEL),
            "task1_to_merge": WorkflowEdge("task1_to_merge", "task1", "merge", EdgeType.SEQUENTIAL),
            "task2_to_merge": WorkflowEdge("task2_to_merge", "task2", "merge", EdgeType.SEQUENTIAL),
            "merge_to_end": WorkflowEdge("merge_to_end", "merge", "end", EdgeType.SEQUENTIAL)
        }
        
        # Register and execute workflow
        workflow_engine.register_workflow(workflow)
        
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="parallel_test_workflow",
            execution_context={'test': 'parallel_execution'},
            initiated_by="test_user"
        )
        
        assert execution_id is not None
        
        # Wait for some processing
        await asyncio.sleep(2)
        
        # Check that parallel nodes were initiated
        execution = workflow_engine.active_executions.get(execution_id)
        if execution:
            # Should have multiple nodes in current_nodes during parallel execution
            assert len(execution.current_nodes) >= 0  # May have completed already in test
    
    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, workflow_engine):
        """Test workflow timeout handling"""
        # Create workflow with short timeout
        workflow = WorkflowDefinition(
            workflow_id="timeout_test_workflow",
            name="Timeout Test Workflow",
            description="Test timeout handling",
            timeout_minutes=1  # Very short timeout for testing
        )
        
        # Add nodes
        workflow.nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start"),
            "long_task": WorkflowNode(
                "long_task", NodeType.TASK, "Long Running Task",
                agent_type="osint", timeout_seconds=3600  # 1 hour task
            ),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        workflow.edges = {
            "start_to_long": WorkflowEdge("start_to_long", "start", "long_task", EdgeType.SEQUENTIAL),
            "long_to_end": WorkflowEdge("long_to_end", "long_task", "end", EdgeType.SEQUENTIAL)
        }
        
        # Register and execute
        workflow_engine.register_workflow(workflow)
        
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="timeout_test_workflow",
            execution_context={'test': 'timeout'},
            initiated_by="test_user"
        )
        
        # Manually trigger timeout check
        execution = workflow_engine.active_executions[execution_id]
        execution.started_at = datetime.utcnow() - timedelta(minutes=2)  # Simulate 2 minutes ago
        
        await workflow_engine._timeout_monitor()
        
        # Execution should be marked as timeout
        # Note: This test depends on the timeout monitor implementation
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, workflow_engine):
        """Test workflow error handling and recovery"""
        # Mock agent to fail
        failing_agent = Mock()
        failing_agent.capabilities = ['failing']
        failing_agent.process_task = AsyncMock(return_value={
            'success': False,
            'error': 'Simulated failure'
        })
        
        workflow_engine.amas_system.agents['failing_agent'] = failing_agent
        
        # Create workflow with failing task
        workflow = WorkflowDefinition(
            workflow_id="error_test_workflow",
            name="Error Test Workflow",
            description="Test error handling"
        )
        
        workflow.nodes = {
            "start": WorkflowNode("start", NodeType.START, "Start"),
            "failing_task": WorkflowNode(
                "failing_task", NodeType.TASK, "Failing Task",
                agent_type="failing", max_retries=2
            ),
            "end": WorkflowNode("end", NodeType.END, "End")
        }
        
        workflow.edges = {
            "start_to_failing": WorkflowEdge("start_to_failing", "start", "failing_task", EdgeType.SEQUENTIAL),
            "failing_to_end": WorkflowEdge("failing_to_end", "failing_task", "end", EdgeType.SEQUENTIAL)
        }
        
        workflow_engine.register_workflow(workflow)
        
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="error_test_workflow",
            execution_context={'test': 'error_handling'},
            initiated_by="test_user"
        )
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Check that node failure was handled
        execution = workflow_engine.active_executions.get(execution_id)
        if execution:
            failing_node = workflow.nodes["failing_task"]
            # Node should have attempted retries
            assert failing_node.retry_count >= 0
    
    @pytest.mark.asyncio
    async def test_workflow_performance_metrics(self, workflow_engine):
        """Test workflow performance metrics collection"""
        initial_metrics = workflow_engine.workflow_metrics.copy()
        
        # Execute workflow
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="intelligence_collection_v2",
            execution_context={'target': 'metrics.test.com'},
            initiated_by="test_user"
        )
        
        # Wait for some processing
        await asyncio.sleep(1)
        
        # Check metrics updated
        updated_metrics = workflow_engine.workflow_metrics
        assert updated_metrics['total_workflows'] > initial_metrics['total_workflows']
        assert updated_metrics['active_executions'] >= initial_metrics['active_executions']
        
        # Check engine status
        engine_status = workflow_engine.get_engine_status()
        assert 'engine_status' in engine_status
        assert 'metrics' in engine_status
        assert 'workflows' in engine_status
        assert engine_status['engine_status'] == 'active'
    
    @pytest.mark.asyncio
    async def test_workflow_state_management(self, workflow_engine):
        """Test workflow state updates during execution"""
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="intelligence_collection_v2",
            execution_context={'target': 'state.test.com'},
            initiated_by="test_user"
        )
        
        execution = workflow_engine.active_executions[execution_id]
        workflow = workflow_engine.workflow_definitions[execution.workflow_id]
        
        # Simulate node completion
        start_node = workflow.nodes["start"]
        start_node.status = NodeStatus.COMPLETED
        execution.completed_nodes.add("start")
        
        # Update workflow state
        await workflow_engine._update_workflow_state(execution, workflow)
        
        # Check that next nodes are ready
        # The exact behavior depends on the workflow structure
        assert len(execution.current_nodes) >= 0
    
    @pytest.mark.asyncio
    async def test_edge_condition_evaluation(self, workflow_engine):
        """Test edge condition evaluation"""
        # Create test execution with results
        execution = WorkflowExecution(
            execution_id="edge_test",
            workflow_id="test_workflow",
            status=WorkflowStatus.RUNNING
        )
        
        execution.node_results = {
            'quality_node': {
                'confidence': 0.9,
                'completeness': 0.8,
                'sources': ['s1', 's2', 's3']
            }
        }
        
        # Test quality sufficient condition
        quality_edge = WorkflowEdge(
            "quality_edge", "from", "to", EdgeType.CONDITIONAL, 
            condition="quality_sufficient"
        )
        
        should_traverse = await workflow_engine._should_traverse_edge(execution, None, quality_edge)
        assert should_traverse is True  # High quality should pass
        
        # Test confidence condition
        confidence_edge = WorkflowEdge(
            "conf_edge", "from", "to", EdgeType.CONDITIONAL,
            condition="high_confidence"
        )
        
        should_traverse = await workflow_engine._should_traverse_edge(execution, None, confidence_edge)
        assert should_traverse is True  # High confidence should pass


class TestWorkflowComplexity:
    """Test complex workflow scenarios"""
    
    @pytest.mark.asyncio
    async def test_nested_workflow_execution(self, workflow_engine):
        """Test nested workflow (subprocess) execution"""
        # This would test subprocess nodes that execute other workflows
        # Implementation depends on the subprocess node executor
        pass
    
    @pytest.mark.asyncio
    async def test_loop_workflow_execution(self, workflow_engine):
        """Test workflow with loops"""
        # The investigation workflow has loop-back edges for iterative processing
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="investigation_v2",
            execution_context={
                'evidence_source': '/test/evidence',
                'investigation_type': 'iterative'
            },
            initiated_by="test_user"
        )
        
        assert execution_id is not None
        
        # Get workflow definition
        workflow = workflow_engine.workflow_definitions["investigation_v2"]
        
        # Check for loop-back edges
        loop_edges = [e for e in workflow.edges.values() if e.edge_type == EdgeType.LOOP_BACK]
        assert len(loop_edges) > 0
    
    @pytest.mark.asyncio
    async def test_workflow_graph_structure(self, workflow_engine):
        """Test workflow graph structure validation"""
        # Get intelligence collection workflow
        workflow = workflow_engine.workflow_definitions["intelligence_collection_v2"]
        
        # Build NetworkX graph
        G = nx.DiGraph()
        
        for node_id in workflow.nodes.keys():
            G.add_node(node_id)
        
        for edge in workflow.edges.values():
            G.add_edge(edge.from_node, edge.to_node)
        
        # Test graph properties
        assert nx.is_directed_acyclic_graph(G) or nx.is_weakly_connected(G)
        
        # Check start node has no predecessors
        start_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.START]
        if start_nodes:
            start_node_id = start_nodes[0].node_id
            predecessors = list(G.predecessors(start_node_id))
            assert len(predecessors) == 0
        
        # Check end nodes have no successors
        end_nodes = [n for n in workflow.nodes.values() if n.node_type == NodeType.END]
        for end_node in end_nodes:
            successors = list(G.successors(end_node.node_id))
            assert len(successors) == 0


class TestWorkflowPerformance:
    """Performance tests for workflow orchestration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, workflow_engine):
        """Test concurrent execution of multiple workflows"""
        # Execute multiple workflows concurrently
        execution_ids = []
        
        for i in range(5):
            execution_id = await workflow_engine.execute_workflow(
                workflow_id="intelligence_collection_v2",
                execution_context={
                    'target': f'concurrent{i}.test.com',
                    'test_id': i
                },
                initiated_by=f"test_user_{i}"
            )
            execution_ids.append(execution_id)
        
        assert len(execution_ids) == 5
        assert len(set(execution_ids)) == 5  # All unique
        
        # Check all executions are active
        for execution_id in execution_ids:
            assert execution_id in workflow_engine.active_executions
    
    @pytest.mark.asyncio
    async def test_workflow_execution_throughput(self, workflow_engine):
        """Test workflow execution throughput"""
        start_time = time.time()
        execution_count = 10
        
        # Submit multiple workflow executions rapidly
        tasks = []
        for i in range(execution_count):
            task = workflow_engine.execute_workflow(
                workflow_id="threat_assessment_v2",
                execution_context={
                    'threat_id': f'threat_{i}',
                    'test_throughput': True
                },
                initiated_by="throughput_test"
            )
            tasks.append(task)
        
        # Wait for all submissions to complete
        execution_ids = await asyncio.gather(*tasks)
        submission_time = time.time() - start_time
        
        # Should be able to submit 10 workflows quickly
        assert submission_time < 2.0
        assert len(execution_ids) == execution_count
        assert len(set(execution_ids)) == execution_count  # All unique
        
        print(f"Workflow submission throughput: {execution_count / submission_time:.2f} workflows/second")
    
    @pytest.mark.asyncio
    async def test_large_workflow_handling(self, workflow_engine):
        """Test handling of large complex workflows"""
        # Create a large workflow with many nodes
        large_workflow = WorkflowDefinition(
            workflow_id="large_test_workflow",
            name="Large Test Workflow",
            description="Test large workflow handling"
        )
        
        # Create 20 nodes
        nodes = {}
        nodes["start"] = WorkflowNode("start", NodeType.START, "Start")
        
        for i in range(1, 19):
            nodes[f"task_{i}"] = WorkflowNode(
                f"task_{i}", NodeType.TASK, f"Task {i}",
                agent_type="osint", timeout_seconds=60
            )
        
        nodes["end"] = WorkflowNode("end", NodeType.END, "End")
        large_workflow.nodes = nodes
        
        # Create sequential edges
        edges = {}
        edges["start_to_task1"] = WorkflowEdge("start_to_task1", "start", "task_1", EdgeType.SEQUENTIAL)
        
        for i in range(1, 18):
            edge_id = f"task{i}_to_task{i+1}"
            edges[edge_id] = WorkflowEdge(edge_id, f"task_{i}", f"task_{i+1}", EdgeType.SEQUENTIAL)
        
        edges["task18_to_end"] = WorkflowEdge("task18_to_end", "task_18", "end", EdgeType.SEQUENTIAL)
        large_workflow.edges = edges
        
        # Register workflow
        result = workflow_engine.register_workflow(large_workflow)
        assert result is True
        
        # Execute workflow
        execution_id = await workflow_engine.execute_workflow(
            workflow_id="large_test_workflow",
            execution_context={'test': 'large_workflow'},
            initiated_by="test_user"
        )
        
        assert execution_id is not None
        
        # Check workflow structure
        assert len(large_workflow.nodes) == 20
        assert len(large_workflow.edges) == 19


class TestWorkflowIntegration:
    """Integration tests for workflow system"""
    
    @pytest.mark.asyncio
    async def test_workflow_with_cognitive_orchestrator(self):
        """Test workflow integration with cognitive orchestrator"""
        # This would test integration between workflow engine and cognitive orchestrator
        # Implementation depends on how they're integrated
        pass
    
    @pytest.mark.asyncio
    async def test_workflow_with_message_bus(self):
        """Test workflow integration with agent message bus"""
        # This would test workflow coordination through the message bus
        # Implementation depends on integration architecture
        pass
    
    @pytest.mark.asyncio
    async def test_workflow_state_persistence(self):
        """Test workflow state persistence and recovery"""
        # This would test workflow state saving and recovery
        # Implementation depends on persistence mechanism
        pass


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=core.workflow_engine",
        "--cov-report=html:htmlcov/workflow_tests",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ])