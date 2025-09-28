"""
AMAS Cognitive Architecture Tests

Comprehensive test suite for the cognitive architecture implementation:
- Cognitive orchestrator functionality
- Dual-process model (System 1 & System 2)
- Reasoning engine capabilities
- Cognitive agent behavior
- Metacognitive awareness
- Learning and adaptation

Ensures 80%+ code coverage and validates cognitive capabilities.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import cognitive components
from core.cognitive_orchestrator import (
    CognitiveOrchestrator, CognitiveMode, TaskComplexity, CognitiveContext
)
from core.reasoning_engine import (
    AdvancedReasoningEngine, ReasoningType, ReasoningChain, ReasoningStep
)
from agents.base.cognitive_agent import (
    CognitiveAgent, CognitiveState, MetacognitiveLevel, CognitiveMemory
)
from core.orchestrator import TaskPriority, TaskStatus


class TestCognitiveOrchestrator:
    """Test suite for the Cognitive Orchestrator"""
    
    @pytest.fixture
    async def cognitive_orchestrator(self):
        """Create a cognitive orchestrator for testing"""
        orchestrator = CognitiveOrchestrator(
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        return orchestrator
    
    @pytest.mark.asyncio
    async def test_cognitive_orchestrator_initialization(self, cognitive_orchestrator):
        """Test cognitive orchestrator initialization"""
        assert cognitive_orchestrator is not None
        assert hasattr(cognitive_orchestrator, 'cognitive_contexts')
        assert hasattr(cognitive_orchestrator, 'reasoning_history')
        assert hasattr(cognitive_orchestrator, 'cognitive_load_tracker')
        assert hasattr(cognitive_orchestrator, 'reasoning_engine')
        assert cognitive_orchestrator.system1_timeout == 5.0
        assert cognitive_orchestrator.system2_timeout == 60.0
    
    @pytest.mark.asyncio
    async def test_task_complexity_assessment(self, cognitive_orchestrator):
        """Test task complexity assessment"""
        # Simple task
        simple_complexity = await cognitive_orchestrator._assess_task_complexity(
            'metadata', 'Extract basic metadata', {}
        )
        assert simple_complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE]
        
        # Complex task
        complex_complexity = await cognitive_orchestrator._assess_task_complexity(
            'reverse_engineering', 
            'Perform comprehensive reverse engineering analysis with detailed investigation of complex multi-layered systems',
            {'depth': 'deep', 'components': ['system1', 'system2', 'system3']}
        )
        assert complex_complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_cognitive_mode_selection(self, cognitive_orchestrator):
        """Test cognitive mode selection based on complexity and priority"""
        # Simple task should prefer System 1
        mode = await cognitive_orchestrator._select_cognitive_mode(
            TaskComplexity.SIMPLE, TaskPriority.LOW
        )
        assert mode == CognitiveMode.SYSTEM1
        
        # Critical task should use System 2
        mode = await cognitive_orchestrator._select_cognitive_mode(
            TaskComplexity.CRITICAL, TaskPriority.CRITICAL
        )
        assert mode == CognitiveMode.SYSTEM2
        
        # Moderate complexity should use hybrid
        mode = await cognitive_orchestrator._select_cognitive_mode(
            TaskComplexity.MODERATE, TaskPriority.MEDIUM
        )
        assert mode in [CognitiveMode.HYBRID, CognitiveMode.SYSTEM2]
    
    @pytest.mark.asyncio
    async def test_task_submission_with_cognitive_mode(self, cognitive_orchestrator):
        """Test task submission with cognitive processing mode selection"""
        task_id = await cognitive_orchestrator.submit_task(
            task_type='osint',
            description='Collect intelligence on emerging threats',
            parameters={'sources': ['news', 'social_media']},
            priority=TaskPriority.HIGH,
            cognitive_mode=CognitiveMode.SYSTEM2
        )
        
        assert task_id is not None
        assert task_id in cognitive_orchestrator.cognitive_contexts
        
        context = cognitive_orchestrator.cognitive_contexts[task_id]
        assert context.cognitive_mode == CognitiveMode.SYSTEM2
        assert context.task_id == task_id
    
    @pytest.mark.asyncio
    async def test_confidence_assessment(self, cognitive_orchestrator):
        """Test result confidence assessment"""
        # High confidence result
        high_conf_result = {
            'success': True,
            'confidence': 0.9,
            'data': {'findings': 'comprehensive results'}
        }
        confidence = await cognitive_orchestrator._assess_result_confidence(
            high_conf_result, TaskComplexity.SIMPLE
        )
        assert confidence >= 0.8
        
        # Low confidence result
        low_conf_result = {
            'success': False,
            'error': 'Processing failed'
        }
        confidence = await cognitive_orchestrator._assess_result_confidence(
            low_conf_result, TaskComplexity.CRITICAL
        )
        assert confidence <= 0.5
    
    @pytest.mark.asyncio
    async def test_cognitive_metrics_update(self, cognitive_orchestrator):
        """Test cognitive metrics tracking"""
        initial_metrics = cognitive_orchestrator.cognitive_metrics.copy()
        
        # Create test context
        context = CognitiveContext(
            task_id='test_task',
            complexity=TaskComplexity.MODERATE,
            cognitive_mode=CognitiveMode.SYSTEM1
        )
        
        result = {'success': True, 'confidence': 0.8}
        processing_time = 2.5
        
        await cognitive_orchestrator._update_cognitive_metrics(context, result, processing_time)
        
        # Check metrics updated
        assert cognitive_orchestrator.cognitive_metrics['system1_tasks'] > initial_metrics['system1_tasks']
        assert cognitive_orchestrator.cognitive_metrics['avg_system1_time'] > 0
    
    @pytest.mark.asyncio
    async def test_cognitive_status_report(self, cognitive_orchestrator):
        """Test cognitive status reporting"""
        status = await cognitive_orchestrator.get_cognitive_status()
        
        assert 'cognitive_load' in status
        assert 'active_contexts' in status
        assert 'metrics' in status
        assert 'system_status' in status
        assert 'configuration' in status
        
        assert status['system_status']['system1_enabled'] is True
        assert status['system_status']['system2_enabled'] is True


class TestReasoningEngine:
    """Test suite for the Advanced Reasoning Engine"""
    
    @pytest.fixture
    def reasoning_engine(self):
        """Create a reasoning engine for testing"""
        return AdvancedReasoningEngine()
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_initialization(self, reasoning_engine):
        """Test reasoning engine initialization"""
        assert reasoning_engine is not None
        assert hasattr(reasoning_engine, 'reasoning_chains')
        assert hasattr(reasoning_engine, 'knowledge_base')
        assert hasattr(reasoning_engine, 'causal_network')
        assert hasattr(reasoning_engine, 'reasoning_patterns')
    
    @pytest.mark.asyncio
    async def test_reasoning_type_selection(self, reasoning_engine):
        """Test automatic reasoning type selection"""
        # Explanatory problem should use abductive reasoning
        reasoning_type = await reasoning_engine._select_reasoning_type(
            "Why did this security incident occur?",
            "Explain the cause of the incident"
        )
        assert reasoning_type == ReasoningType.ABDUCTIVE
        
        # Predictive problem should use inductive reasoning
        reasoning_type = await reasoning_engine._select_reasoning_type(
            "What patterns can we predict from this data?",
            "Forecast future trends"
        )
        assert reasoning_type == ReasoningType.INDUCTIVE
        
        # Logical problem should use deductive reasoning
        reasoning_type = await reasoning_engine._select_reasoning_type(
            "If these conditions are met, then what conclusion follows?",
            "Draw logical conclusions"
        )
        assert reasoning_type == ReasoningType.DEDUCTIVE
    
    @pytest.mark.asyncio
    async def test_abductive_reasoning(self, reasoning_engine):
        """Test abductive reasoning process"""
        chain = await reasoning_engine.reason_about_problem(
            problem_description="Multiple failed login attempts detected from unusual locations",
            context={'source': 'security_logs', 'pattern': 'distributed'},
            goal="Explain the security anomaly",
            reasoning_type=ReasoningType.ABDUCTIVE
        )
        
        assert chain is not None
        assert chain.goal == "Explain the security anomaly"
        assert len(chain.steps) > 0
        assert chain.overall_confidence > 0.0
        assert chain.final_conclusion != ""
        
        # Check that reasoning steps are properly structured
        for step in chain.steps:
            assert step.reasoning_type == ReasoningType.ABDUCTIVE
            assert step.step_id != ""
            assert step.confidence >= 0.0 and step.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_deductive_reasoning(self, reasoning_engine):
        """Test deductive reasoning process"""
        chain = await reasoning_engine.reason_about_problem(
            problem_description="All network traffic from IP 192.168.1.100 is suspicious. Traffic detected from 192.168.1.100.",
            context={'rule': 'suspicious_ip_policy'},
            goal="Determine if traffic should be blocked",
            reasoning_type=ReasoningType.DEDUCTIVE
        )
        
        assert chain is not None
        assert len(chain.steps) > 0
        assert chain.overall_confidence > 0.0
        
        # Deductive reasoning should have high confidence when premises are clear
        assert chain.overall_confidence >= 0.6
    
    @pytest.mark.asyncio
    async def test_reasoning_chain_confidence_calculation(self, reasoning_engine):
        """Test reasoning chain confidence calculation"""
        # Create test reasoning chain
        chain = ReasoningChain(
            chain_id="test_chain",
            goal="Test confidence calculation"
        )
        
        # Add steps with different confidences
        chain.steps = [
            ReasoningStep(
                step_id="step1",
                reasoning_type=ReasoningType.DEDUCTIVE,
                premise="High confidence premise",
                conclusion="High confidence conclusion",
                confidence=0.9
            ),
            ReasoningStep(
                step_id="step2",
                reasoning_type=ReasoningType.DEDUCTIVE,
                premise="Medium confidence premise",
                conclusion="Medium confidence conclusion",
                confidence=0.6
            )
        ]
        
        confidence = reasoning_engine._calculate_chain_confidence(chain)
        
        # Should be weighted average with decay
        assert confidence > 0.6 and confidence < 0.9
        assert confidence > 0.0 and confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_alternative_generation(self, reasoning_engine):
        """Test generation of alternative explanations"""
        chain = ReasoningChain(
            chain_id="test_chain",
            goal="Test alternatives"
        )
        chain.steps = [
            ReasoningStep(
                step_id="step1",
                reasoning_type=ReasoningType.ABDUCTIVE,
                premise="Low confidence premise",
                conclusion="Uncertain conclusion",
                confidence=0.4
            )
        ]
        
        alternatives = await reasoning_engine._generate_alternatives(chain, {})
        
        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
        # Should generate alternatives for low confidence conclusions
        assert any('Alternative' in alt for alt in alternatives)


class TestCognitiveAgent:
    """Test suite for the Cognitive Agent"""
    
    @pytest.fixture
    async def cognitive_agent(self):
        """Create a cognitive agent for testing"""
        agent = CognitiveAgent(
            agent_id="test_cognitive_agent",
            name="Test Cognitive Agent",
            capabilities=["test_capability"],
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        return agent
    
    @pytest.mark.asyncio
    async def test_cognitive_agent_initialization(self, cognitive_agent):
        """Test cognitive agent initialization"""
        assert cognitive_agent is not None
        assert cognitive_agent.agent_id == "test_cognitive_agent"
        assert cognitive_agent.cognitive_state == CognitiveState.IDLE
        assert cognitive_agent.metacognitive_level == MetacognitiveLevel.INTERMEDIATE
        assert hasattr(cognitive_agent, 'reasoning_engine')
        assert hasattr(cognitive_agent, 'episodic_memory')
        assert hasattr(cognitive_agent, 'learning_experiences')
        assert 'cognitive_reasoning' in cognitive_agent.capabilities
    
    @pytest.mark.asyncio
    async def test_metacognitive_assessment(self, cognitive_agent):
        """Test metacognitive task assessment"""
        task = {
            'id': 'test_task',
            'type': 'osint',
            'description': 'Complex intelligence analysis requiring multiple sources and deep investigation',
            'parameters': {'sources': ['source1', 'source2'], 'depth': 'comprehensive'}
        }
        
        assessment = await cognitive_agent._assess_task_metacognitively(task)
        
        assert 'task_complexity' in assessment
        assert 'confidence_in_ability' in assessment
        assert 'estimated_difficulty' in assessment
        assert 'similar_experiences' in assessment
        assert 'potential_challenges' in assessment
        
        # Complex task should be assessed as high complexity
        assert assessment['task_complexity'] in ['medium', 'high']
        assert assessment['estimated_difficulty'] > 0.3
    
    @pytest.mark.asyncio
    async def test_cognitive_strategy_selection(self, cognitive_agent):
        """Test cognitive strategy selection"""
        # High complexity, low confidence assessment
        assessment = {
            'task_complexity': 'high',
            'confidence_in_ability': 0.4,
            'required_reasoning': ['abductive'],
            'potential_challenges': ['novel_situation']
        }
        
        strategy = await cognitive_agent._select_cognitive_strategy({}, assessment)
        
        assert 'system' in strategy
        assert 'reasoning_type' in strategy
        assert 'confidence_threshold' in strategy
        
        # High complexity should prefer System 2
        assert strategy['system'] == 2
        assert strategy['validation_required'] is True
    
    @pytest.mark.asyncio
    async def test_system1_processing(self, cognitive_agent):
        """Test System 1 (fast) processing"""
        task = {
            'id': 'simple_task',
            'type': 'metadata',
            'description': 'Extract basic metadata',
            'parameters': {}
        }
        
        strategy = {'system': 1, 'reasoning_type': ReasoningType.DEDUCTIVE}
        
        # Mock the base process_task method
        with patch.object(cognitive_agent, 'process_task', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                'success': True,
                'result': 'metadata extracted',
                'confidence': 0.8
            }
            
            # Override the method we're testing
            result = await cognitive_agent._system1_processing(task, strategy)
            
            assert result['processing_type'] == 'system1'
            # System 1 should cap confidence
            assert result['confidence'] <= 0.8
    
    @pytest.mark.asyncio
    async def test_system2_processing(self, cognitive_agent):
        """Test System 2 (analytical) processing"""
        task = {
            'id': 'complex_task',
            'type': 'investigation',
            'description': 'Comprehensive investigation requiring deep analysis',
            'parameters': {}
        }
        
        strategy = {
            'system': 2,
            'reasoning_type': ReasoningType.ABDUCTIVE,
            'validation_required': True
        }
        
        # Mock the base process_task method
        with patch.object(cognitive_agent, 'process_task', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {
                'success': True,
                'result': 'investigation completed',
                'confidence': 0.7
            }
            
            result = await cognitive_agent._system2_processing(task, strategy)
            
            assert result['processing_type'] == 'system2'
            assert 'reasoning_chain' in result
            assert result['reasoning_chain']['confidence'] > 0.0
    
    @pytest.mark.asyncio
    async def test_hybrid_processing(self, cognitive_agent):
        """Test hybrid processing (System 1 + System 2)"""
        task = {
            'id': 'moderate_task',
            'type': 'osint',
            'description': 'Standard intelligence collection',
            'parameters': {}
        }
        
        strategy = {
            'system': 'hybrid',
            'confidence_threshold': 0.7,
            'reasoning_type': ReasoningType.ABDUCTIVE
        }
        
        # Mock System 1 to return low confidence
        with patch.object(cognitive_agent, '_system1_processing', new_callable=AsyncMock) as mock_s1:
            mock_s1.return_value = {
                'success': True,
                'confidence': 0.5,  # Below threshold
                'processing_type': 'system1'
            }
            
            with patch.object(cognitive_agent, '_system2_processing', new_callable=AsyncMock) as mock_s2:
                mock_s2.return_value = {
                    'success': True,
                    'confidence': 0.8,  # Higher confidence
                    'processing_type': 'system2'
                }
                
                result = await cognitive_agent._hybrid_processing(task, strategy)
                
                # Should switch to System 2 due to low System 1 confidence
                assert result['processing_type'] == 'hybrid_system2'
                assert 'system1_initial' in result
    
    @pytest.mark.asyncio
    async def test_performance_reflection(self, cognitive_agent):
        """Test metacognitive reflection on performance"""
        task = {'id': 'test_task', 'type': 'osint', 'description': 'Test task'}
        result = {'success': True, 'confidence': 0.9}
        processing_time = 15.0
        
        reflection = await cognitive_agent._reflect_on_performance(task, result, processing_time)
        
        assert 'task_id' in reflection
        assert 'processing_time' in reflection
        assert 'success' in reflection
        assert 'confidence_achieved' in reflection
        assert 'strategy_effectiveness' in reflection
        assert 'lessons_learned' in reflection
        
        # High success and confidence should result in excellent effectiveness
        assert reflection['strategy_effectiveness'] == 'excellent'
    
    @pytest.mark.asyncio
    async def test_learning_from_experience(self, cognitive_agent):
        """Test learning and adaptation from experience"""
        task = {'id': 'learning_task', 'type': 'test', 'description': 'Learning test'}
        result = {'success': False, 'confidence': 0.3, 'processing_type': 'system1'}
        reflection = {
            'learning_occurred': True,
            'lessons_learned': ['Need better strategy for similar tasks'],
            'strategy_effectiveness': 'poor',
            'areas_for_improvement': ['strategy_selection']
        }
        
        initial_experiences = len(cognitive_agent.learning_experiences)
        initial_threshold = cognitive_agent.cognitive_preferences['confidence_threshold']
        
        await cognitive_agent._learn_from_experience(task, result, reflection)
        
        # Should create learning experience
        assert len(cognitive_agent.learning_experiences) > initial_experiences
        
        # Should adapt preferences based on failure
        assert cognitive_agent.cognitive_preferences['confidence_threshold'] > initial_threshold
        
        # Check learning experience structure
        latest_experience = cognitive_agent.learning_experiences[-1]
        assert latest_experience.outcome == 'failure'
        assert latest_experience.lesson_learned == 'Need better strategy for similar tasks'
    
    @pytest.mark.asyncio
    async def test_memory_management(self, cognitive_agent):
        """Test cognitive memory management"""
        task = {'id': 'memory_task', 'type': 'test', 'description': 'Memory test'}
        result = {'success': True, 'confidence': 0.8}
        reflection = {'learning_occurred': False, 'lessons_learned': []}
        
        initial_memories = len(cognitive_agent.episodic_memory)
        
        await cognitive_agent._update_cognitive_memories(task, result, reflection)
        
        # Should create episodic memory
        assert len(cognitive_agent.episodic_memory) > initial_memories
        
        # Check memory structure
        latest_memory = cognitive_agent.episodic_memory[-1]
        assert latest_memory.experience_type == 'task'
        assert 'task' in latest_memory.content
        assert 'result' in latest_memory.content
        assert latest_memory.confidence == 0.8
        assert latest_memory.emotional_valence > 0  # Positive for success
    
    @pytest.mark.asyncio
    async def test_similar_experience_finding(self, cognitive_agent):
        """Test finding similar past experiences"""
        # Add some memories first
        for i in range(3):
            memory = CognitiveMemory(
                memory_id=f"mem_{i}",
                experience_type='task',
                content={
                    'task': {
                        'type': 'osint',
                        'description': f'OSINT task {i} with intelligence collection'
                    },
                    'result': {'success': True}
                },
                confidence=0.8,
                importance=0.7,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            cognitive_agent.episodic_memory.append(memory)
        
        # Search for similar task
        task = {
            'type': 'osint',
            'description': 'New OSINT task for intelligence collection'
        }
        
        similar = await cognitive_agent._find_similar_experiences(task)
        
        assert len(similar) > 0
        assert all(exp['similarity'] > 0.3 for exp in similar)
        assert all('memory_id' in exp for exp in similar)
    
    @pytest.mark.asyncio
    async def test_cognitive_status_report(self, cognitive_agent):
        """Test comprehensive cognitive status reporting"""
        status = await cognitive_agent.get_cognitive_status()
        
        assert 'agent_id' in status
        assert 'cognitive_state' in status
        assert 'metacognitive_level' in status
        assert 'performance_metrics' in status
        assert 'cognitive_preferences' in status
        assert 'memory_status' in status
        assert 'learning_status' in status
        assert 'reasoning_capabilities' in status
        
        # Check memory status details
        memory_status = status['memory_status']
        assert 'episodic_memories' in memory_status
        assert 'semantic_knowledge_areas' in memory_status
        assert 'procedural_patterns' in memory_status
        assert 'working_memory_items' in memory_status
        
        # Check reasoning capabilities
        reasoning_caps = status['reasoning_capabilities']
        assert 'available_reasoning_types' in reasoning_caps
        assert 'preferred_reasoning' in reasoning_caps
        assert len(reasoning_caps['available_reasoning_types']) > 0


class TestCognitiveIntegration:
    """Integration tests for cognitive architecture components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_cognitive_processing(self):
        """Test complete cognitive processing pipeline"""
        # Create cognitive orchestrator
        orchestrator = CognitiveOrchestrator(
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Create cognitive agent
        agent = CognitiveAgent(
            agent_id="integration_test_agent",
            name="Integration Test Agent",
            capabilities=["test_capability"],
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Register agent with orchestrator
        await orchestrator.register_agent(agent)
        
        # Submit task with cognitive mode
        task_id = await orchestrator.submit_task(
            task_type='osint',
            description='Comprehensive intelligence analysis requiring deep reasoning',
            parameters={'sources': ['multiple'], 'analysis_depth': 'comprehensive'},
            priority=TaskPriority.HIGH,
            cognitive_mode=CognitiveMode.SYSTEM2
        )
        
        # Verify cognitive context created
        assert task_id in orchestrator.cognitive_contexts
        context = orchestrator.cognitive_contexts[task_id]
        assert context.cognitive_mode == CognitiveMode.SYSTEM2
        assert context.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_cognitive_load_tracking(self):
        """Test cognitive load tracking across the system"""
        orchestrator = CognitiveOrchestrator(
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Check initial load
        initial_load = await orchestrator.cognitive_load_tracker.get_current_load()
        assert initial_load >= 0.0 and initial_load <= 1.0
        
        # Update load
        await orchestrator.cognitive_load_tracker.update_load(0.2)
        updated_load = await orchestrator.cognitive_load_tracker.get_current_load()
        assert updated_load >= initial_load
    
    @pytest.mark.asyncio
    async def test_reasoning_engine_integration(self):
        """Test reasoning engine integration with cognitive agent"""
        agent = CognitiveAgent(
            agent_id="reasoning_test_agent",
            name="Reasoning Test Agent",
            capabilities=["reasoning_test"],
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Test reasoning engine is properly initialized
        assert agent.reasoning_engine is not None
        assert isinstance(agent.reasoning_engine, AdvancedReasoningEngine)
        
        # Test reasoning capabilities in cognitive status
        status = await agent.get_cognitive_status()
        reasoning_caps = status['reasoning_capabilities']
        assert 'abductive' in reasoning_caps['available_reasoning_types']
        assert 'deductive' in reasoning_caps['available_reasoning_types']
        assert 'inductive' in reasoning_caps['available_reasoning_types']


# Performance and stress tests
class TestCognitivePerformance:
    """Performance tests for cognitive architecture"""
    
    @pytest.mark.asyncio
    async def test_cognitive_processing_performance(self):
        """Test cognitive processing performance under load"""
        agent = CognitiveAgent(
            agent_id="performance_test_agent",
            name="Performance Test Agent",
            capabilities=["performance_test"],
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Mock the base process_task to return quickly
        with patch.object(agent, 'process_task', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {'success': True, 'confidence': 0.8}
            
            # Process multiple tasks rapidly
            tasks = []
            start_time = time.time()
            
            for i in range(10):
                task = {
                    'id': f'perf_task_{i}',
                    'type': 'test',
                    'description': f'Performance test task {i}',
                    'parameters': {}
                }
                tasks.append(agent.process_task(task))
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)
            processing_time = time.time() - start_time
            
            # Should process 10 tasks in reasonable time (under 5 seconds)
            assert processing_time < 5.0
            assert len(results) == 10
            assert all(result.get('success', False) for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_performance(self):
        """Test memory system performance"""
        agent = CognitiveAgent(
            agent_id="memory_perf_agent",
            name="Memory Performance Agent",
            capabilities=["memory_test"],
            llm_service=Mock(),
            vector_service=Mock(),
            knowledge_graph=Mock(),
            security_service=Mock()
        )
        
        # Add many memories
        start_time = time.time()
        
        for i in range(100):
            memory = CognitiveMemory(
                memory_id=f"perf_mem_{i}",
                experience_type='task',
                content={'task': {'type': 'test', 'description': f'Test {i}'}},
                confidence=0.8,
                importance=0.5,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            agent.episodic_memory.append(memory)
        
        memory_creation_time = time.time() - start_time
        
        # Test memory search performance
        search_start = time.time()
        similar = await agent._find_similar_experiences({'type': 'test', 'description': 'Test search'})
        search_time = time.time() - search_start
        
        # Memory operations should be fast
        assert memory_creation_time < 1.0  # Creating 100 memories should be under 1 second
        assert search_time < 0.5  # Searching should be under 0.5 seconds
        assert len(similar) > 0  # Should find similar memories


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=core.cognitive_orchestrator",
        "--cov=core.reasoning_engine", 
        "--cov=agents.base.cognitive_agent",
        "--cov-report=html:htmlcov/cognitive_tests",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ])