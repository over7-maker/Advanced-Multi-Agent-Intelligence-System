"""
AMAS Cognitive Agent Base Class

Enhanced base class for agents with cognitive capabilities:
- Dual-process thinking (System 1 & System 2)
- Metacognitive awareness
- Learning and adaptation
- Explainable decision-making
- Confidence assessment

This extends the base IntelligenceAgent with cognitive processing capabilities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import time

from agents.base.intelligence_agent import IntelligenceAgent, AgentStatus
from core.reasoning_engine import AdvancedReasoningEngine, ReasoningType, ReasoningChain

logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """Cognitive states of the agent"""
    IDLE = "idle"
    THINKING = "thinking"
    FAST_PROCESSING = "fast_processing"  # System 1
    DEEP_ANALYSIS = "deep_analysis"      # System 2
    LEARNING = "learning"
    REFLECTING = "reflecting"


class MetacognitiveLevel(Enum):
    """Levels of metacognitive awareness"""
    BASIC = 1       # Basic awareness of own processes
    INTERMEDIATE = 2 # Understanding of thinking strategies
    ADVANCED = 3    # Self-monitoring and regulation
    EXPERT = 4      # Meta-meta-cognition


@dataclass
class CognitiveMemory:
    """Memory structure for cognitive experiences"""
    memory_id: str
    experience_type: str  # 'task', 'reasoning', 'learning', 'error'
    content: Dict[str, Any]
    confidence: float
    importance: float  # 0.0 to 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)


@dataclass
class LearningExperience:
    """Structure for learning from experiences"""
    experience_id: str
    situation: str
    action_taken: str
    outcome: str
    feedback: str
    lesson_learned: str
    confidence_change: float
    timestamp: datetime


class CognitiveAgent(IntelligenceAgent):
    """
    Enhanced agent with cognitive capabilities including dual-process thinking,
    metacognition, learning, and explainable decision-making.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cognitive components
        self.reasoning_engine = AdvancedReasoningEngine()
        self.cognitive_state = CognitiveState.IDLE
        self.metacognitive_level = MetacognitiveLevel.INTERMEDIATE
        
        # Memory systems
        self.working_memory: Dict[str, Any] = {}
        self.episodic_memory: List[CognitiveMemory] = []
        self.semantic_memory: Dict[str, Any] = {}
        self.procedural_memory: Dict[str, Any] = {}
        
        # Learning and adaptation
        self.learning_experiences: List[LearningExperience] = []
        self.confidence_history: List[Tuple[datetime, float]] = []
        self.performance_metrics: Dict[str, float] = {
            'task_success_rate': 0.0,
            'average_confidence': 0.5,
            'learning_rate': 0.0,
            'adaptation_speed': 0.0
        }
        
        # Cognitive preferences and biases
        self.cognitive_preferences = {
            'preferred_reasoning_type': ReasoningType.ABDUCTIVE,
            'risk_tolerance': 0.5,
            'exploration_vs_exploitation': 0.6,  # Favor exploration
            'confidence_threshold': 0.7,
            'reflection_frequency': 0.3
        }
        
        # Metacognitive awareness
        self.thinking_strategies: List[str] = []
        self.known_biases: List[str] = []
        self.strengths: List[str] = []
        self.weaknesses: List[str] = []
        
        # Enhanced capabilities
        self.capabilities.extend([
            'cognitive_reasoning',
            'metacognitive_awareness',
            'adaptive_learning',
            'explainable_decisions',
            'confidence_assessment'
        ])
        
        logger.info(f"Cognitive Agent {self.agent_id} initialized with metacognitive level {self.metacognitive_level.name}")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced task processing with cognitive capabilities.
        
        Integrates dual-process thinking, reasoning, and metacognitive awareness.
        """
        try:
            task_id = task.get('id', 'unknown')
            start_time = time.time()
            
            logger.info(f"Cognitive Agent {self.agent_id} processing task {task_id}")
            
            # Phase 1: Metacognitive assessment
            metacognitive_assessment = await self._assess_task_metacognitively(task)
            
            # Phase 2: Select cognitive strategy
            cognitive_strategy = await self._select_cognitive_strategy(task, metacognitive_assessment)
            
            # Phase 3: Execute cognitive processing
            if cognitive_strategy['system'] == 1:
                result = await self._system1_processing(task, cognitive_strategy)
            elif cognitive_strategy['system'] == 2:
                result = await self._system2_processing(task, cognitive_strategy)
            else:
                result = await self._hybrid_processing(task, cognitive_strategy)
            
            # Phase 4: Metacognitive reflection
            reflection = await self._reflect_on_performance(task, result, time.time() - start_time)
            
            # Phase 5: Learning and adaptation
            await self._learn_from_experience(task, result, reflection)
            
            # Phase 6: Update cognitive state and memories
            await self._update_cognitive_memories(task, result, reflection)
            
            # Enhanced result with cognitive information
            enhanced_result = {
                **result,
                'cognitive_info': {
                    'reasoning_used': cognitive_strategy.get('reasoning_type', 'unknown'),
                    'confidence': result.get('confidence', 0.5),
                    'processing_system': cognitive_strategy['system'],
                    'metacognitive_assessment': metacognitive_assessment,
                    'reflection': reflection,
                    'learning_occurred': reflection.get('learning_occurred', False)
                }
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in cognitive task processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'cognitive_info': {
                    'error_type': 'cognitive_processing_error',
                    'recovery_attempted': True
                }
            }
    
    async def _assess_task_metacognitively(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Metacognitive assessment of the task.
        
        "Thinking about thinking" - assess what cognitive resources and strategies
        will be needed for this task.
        """
        try:
            self.cognitive_state = CognitiveState.THINKING
            
            assessment = {
                'task_complexity': 'unknown',
                'required_reasoning': [],
                'confidence_in_ability': 0.5,
                'estimated_difficulty': 0.5,
                'similar_experiences': [],
                'potential_challenges': [],
                'recommended_approach': 'systematic'
            }
            
            # Analyze task complexity
            task_description = task.get('description', '')
            task_type = task.get('type', '')
            
            # Complexity assessment based on description
            if len(task_description) > 200 or 'complex' in task_description.lower():
                assessment['task_complexity'] = 'high'
                assessment['estimated_difficulty'] = 0.8
            elif len(task_description) < 50 and task_type in ['simple', 'basic', 'routine']:
                assessment['task_complexity'] = 'low'
                assessment['estimated_difficulty'] = 0.3
            else:
                assessment['task_complexity'] = 'medium'
                assessment['estimated_difficulty'] = 0.5
            
            # Check for similar past experiences
            similar_tasks = await self._find_similar_experiences(task)
            assessment['similar_experiences'] = similar_tasks
            
            if similar_tasks:
                # Adjust confidence based on past performance
                past_success_rate = sum(exp.get('success', 0) for exp in similar_tasks) / len(similar_tasks)
                assessment['confidence_in_ability'] = min(0.9, past_success_rate + 0.1)
            
            # Identify required reasoning types
            description_lower = task_description.lower()
            if 'why' in description_lower or 'explain' in description_lower:
                assessment['required_reasoning'].append('abductive')
            if 'analyze' in description_lower or 'investigate' in description_lower:
                assessment['required_reasoning'].append('deductive')
            if 'predict' in description_lower or 'forecast' in description_lower:
                assessment['required_reasoning'].append('inductive')
            
            # Identify potential challenges
            if assessment['task_complexity'] == 'high':
                assessment['potential_challenges'].append('high_cognitive_load')
            if not assessment['similar_experiences']:
                assessment['potential_challenges'].append('novel_situation')
            if task.get('priority', 0) > 3:
                assessment['potential_challenges'].append('high_pressure')
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in metacognitive assessment: {e}")
            return {'error': str(e)}
    
    async def _select_cognitive_strategy(
        self,
        task: Dict[str, Any],
        assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select the appropriate cognitive strategy based on metacognitive assessment.
        """
        try:
            strategy = {
                'system': 2,  # Default to System 2
                'reasoning_type': ReasoningType.ABDUCTIVE,
                'confidence_threshold': 0.7,
                'validation_required': True,
                'explanation_depth': 'detailed'
            }
            
            # System selection based on complexity and confidence
            complexity = assessment.get('task_complexity', 'medium')
            confidence = assessment.get('confidence_in_ability', 0.5)
            
            if complexity == 'low' and confidence > 0.8:
                strategy['system'] = 1  # Fast System 1 processing
                strategy['validation_required'] = False
                strategy['explanation_depth'] = 'basic'
            elif complexity == 'high' or confidence < 0.5:
                strategy['system'] = 2  # Careful System 2 processing
                strategy['validation_required'] = True
                strategy['explanation_depth'] = 'detailed'
            else:
                strategy['system'] = 'hybrid'  # Hybrid approach
                strategy['validation_required'] = True
                strategy['explanation_depth'] = 'moderate'
            
            # Reasoning type selection
            required_reasoning = assessment.get('required_reasoning', [])
            if 'abductive' in required_reasoning:
                strategy['reasoning_type'] = ReasoningType.ABDUCTIVE
            elif 'deductive' in required_reasoning:
                strategy['reasoning_type'] = ReasoningType.DEDUCTIVE
            elif 'inductive' in required_reasoning:
                strategy['reasoning_type'] = ReasoningType.INDUCTIVE
            else:
                strategy['reasoning_type'] = self.cognitive_preferences['preferred_reasoning_type']
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error selecting cognitive strategy: {e}")
            return {'system': 2, 'reasoning_type': ReasoningType.ABDUCTIVE}
    
    async def _system1_processing(
        self,
        task: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        System 1: Fast, intuitive processing.
        
        Characteristics:
        - Quick pattern recognition
        - Heuristic-based decisions
        - Minimal conscious deliberation
        - High speed, moderate accuracy
        """
        try:
            self.cognitive_state = CognitiveState.FAST_PROCESSING
            
            # Quick pattern matching
            pattern_match = await self._quick_pattern_match(task)
            
            if pattern_match:
                return {
                    'success': True,
                    'result': pattern_match['result'],
                    'confidence': pattern_match['confidence'],
                    'processing_type': 'system1',
                    'reasoning': 'Pattern matching and heuristics',
                    'explanation': pattern_match.get('explanation', 'Fast intuitive processing')
                }
            
            # Fallback to base processing with fast parameters
            base_result = await super().process_task(task)
            
            return {
                **base_result,
                'processing_type': 'system1',
                'confidence': min(base_result.get('confidence', 0.7), 0.8)  # Cap confidence for System 1
            }
            
        except Exception as e:
            logger.error(f"Error in System 1 processing: {e}")
            return {'success': False, 'error': str(e), 'processing_type': 'system1'}
    
    async def _system2_processing(
        self,
        task: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        System 2: Slow, deliberate, analytical processing.
        
        Characteristics:
        - Step-by-step analysis
        - Explicit reasoning
        - High accuracy, slower speed
        - Conscious deliberation
        """
        try:
            self.cognitive_state = CognitiveState.DEEP_ANALYSIS
            
            # Deep reasoning using the reasoning engine
            reasoning_chain = await self.reasoning_engine.reason_about_problem(
                problem_description=task.get('description', ''),
                context=task.get('parameters', {}),
                goal=f"Process {task.get('type', 'unknown')} task",
                reasoning_type=strategy.get('reasoning_type')
            )
            
            # Execute base task processing with analytical parameters
            analytical_params = {
                **task.get('parameters', {}),
                'processing_mode': 'analytical',
                'depth': 'deep',
                'validation': strategy.get('validation_required', True)
            }
            
            base_result = await super().process_task({
                **task,
                'parameters': analytical_params
            })
            
            # Combine reasoning with base result
            return {
                **base_result,
                'processing_type': 'system2',
                'reasoning_chain': {
                    'chain_id': reasoning_chain.chain_id,
                    'steps': len(reasoning_chain.steps),
                    'confidence': reasoning_chain.overall_confidence,
                    'conclusion': reasoning_chain.final_conclusion,
                    'reasoning_path': reasoning_chain.reasoning_path
                },
                'confidence': max(base_result.get('confidence', 0.5), reasoning_chain.overall_confidence),
                'explanation': self._generate_detailed_explanation(reasoning_chain, base_result)
            }
            
        except Exception as e:
            logger.error(f"Error in System 2 processing: {e}")
            return {'success': False, 'error': str(e), 'processing_type': 'system2'}
    
    async def _hybrid_processing(
        self,
        task: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Hybrid processing: Combines System 1 and System 2.
        
        Uses System 1 for initial assessment, System 2 for validation and refinement.
        """
        try:
            # Phase 1: Quick System 1 assessment
            system1_result = await self._system1_processing(task, strategy)
            
            # Phase 2: Confidence check
            confidence = system1_result.get('confidence', 0.5)
            
            if confidence >= strategy.get('confidence_threshold', 0.7):
                # High confidence - use System 1 result
                return {
                    **system1_result,
                    'processing_type': 'hybrid_system1',
                    'explanation': f"Hybrid processing: System 1 result accepted (confidence: {confidence:.2f})"
                }
            else:
                # Low confidence - engage System 2
                system2_result = await self._system2_processing(task, strategy)
                
                return {
                    **system2_result,
                    'processing_type': 'hybrid_system2',
                    'system1_initial': system1_result,
                    'explanation': f"Hybrid processing: System 2 engaged due to low initial confidence ({confidence:.2f})"
                }
                
        except Exception as e:
            logger.error(f"Error in hybrid processing: {e}")
            return {'success': False, 'error': str(e), 'processing_type': 'hybrid'}
    
    async def _reflect_on_performance(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Metacognitive reflection on performance.
        
        Analyze how well the cognitive strategy worked and what can be learned.
        """
        try:
            self.cognitive_state = CognitiveState.REFLECTING
            
            reflection = {
                'task_id': task.get('id', 'unknown'),
                'processing_time': processing_time,
                'success': result.get('success', False),
                'confidence_achieved': result.get('confidence', 0.5),
                'strategy_effectiveness': 'unknown',
                'lessons_learned': [],
                'areas_for_improvement': [],
                'strengths_demonstrated': [],
                'learning_occurred': False
            }
            
            # Assess strategy effectiveness
            success = result.get('success', False)
            confidence = result.get('confidence', 0.5)
            
            if success and confidence > 0.8:
                reflection['strategy_effectiveness'] = 'excellent'
                reflection['strengths_demonstrated'].append('effective_strategy_selection')
            elif success and confidence > 0.6:
                reflection['strategy_effectiveness'] = 'good'
            elif success:
                reflection['strategy_effectiveness'] = 'adequate'
                reflection['areas_for_improvement'].append('increase_confidence')
            else:
                reflection['strategy_effectiveness'] = 'poor'
                reflection['areas_for_improvement'].append('strategy_selection')
                reflection['areas_for_improvement'].append('task_analysis')
            
            # Learning opportunities
            if not success or confidence < 0.6:
                reflection['lessons_learned'].append('Need better strategy for similar tasks')
                reflection['learning_occurred'] = True
            
            if processing_time > 60:  # If task took more than 1 minute
                reflection['lessons_learned'].append('Consider more efficient processing approach')
                reflection['areas_for_improvement'].append('processing_efficiency')
            
            return reflection
            
        except Exception as e:
            logger.error(f"Error in performance reflection: {e}")
            return {'error': str(e)}
    
    async def _learn_from_experience(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        reflection: Dict[str, Any]
    ):
        """
        Learn and adapt based on the experience.
        
        Updates cognitive preferences, biases awareness, and strategies.
        """
        try:
            if not reflection.get('learning_occurred', False):
                return
            
            self.cognitive_state = CognitiveState.LEARNING
            
            # Create learning experience
            experience = LearningExperience(
                experience_id=f"exp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                situation=task.get('description', ''),
                action_taken=result.get('processing_type', 'unknown'),
                outcome='success' if result.get('success', False) else 'failure',
                feedback=reflection.get('strategy_effectiveness', 'unknown'),
                lesson_learned='; '.join(reflection.get('lessons_learned', [])),
                confidence_change=result.get('confidence', 0.5) - 0.5,  # Change from baseline
                timestamp=datetime.utcnow()
            )
            
            self.learning_experiences.append(experience)
            
            # Adapt cognitive preferences based on experience
            if experience.outcome == 'success':
                # Reinforce successful strategies
                processing_type = result.get('processing_type', '')
                if 'system1' in processing_type and experience.confidence_change > 0:
                    self.cognitive_preferences['exploration_vs_exploitation'] *= 0.95  # Slightly favor exploitation
                elif 'system2' in processing_type and experience.confidence_change > 0:
                    self.cognitive_preferences['confidence_threshold'] *= 0.98  # Slightly lower threshold
            else:
                # Learn from failures
                self.cognitive_preferences['confidence_threshold'] *= 1.02  # Raise threshold
                if 'strategy_selection' in reflection.get('areas_for_improvement', []):
                    self.cognitive_preferences['exploration_vs_exploitation'] *= 1.05  # Favor exploration
            
            # Update performance metrics
            await self._update_performance_metrics(experience)
            
            logger.info(f"Agent {self.agent_id} learned from experience: {experience.lesson_learned}")
            
        except Exception as e:
            logger.error(f"Error in learning from experience: {e}")
    
    async def _update_cognitive_memories(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        reflection: Dict[str, Any]
    ):
        """Update various memory systems with the experience."""
        try:
            # Create episodic memory
            memory = CognitiveMemory(
                memory_id=f"mem_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                experience_type='task',
                content={
                    'task': task,
                    'result': result,
                    'reflection': reflection
                },
                confidence=result.get('confidence', 0.5),
                importance=self._calculate_memory_importance(task, result, reflection),
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                emotional_valence=1.0 if result.get('success', False) else -0.5
            )
            
            self.episodic_memory.append(memory)
            
            # Limit memory size
            if len(self.episodic_memory) > 1000:
                # Remove least important memories
                self.episodic_memory.sort(key=lambda m: m.importance, reverse=True)
                self.episodic_memory = self.episodic_memory[:800]
            
            # Update semantic memory with generalizable knowledge
            if reflection.get('lessons_learned'):
                task_type = task.get('type', 'unknown')
                if task_type not in self.semantic_memory:
                    self.semantic_memory[task_type] = []
                
                self.semantic_memory[task_type].extend(reflection['lessons_learned'])
            
        except Exception as e:
            logger.error(f"Error updating cognitive memories: {e}")
    
    def _calculate_memory_importance(
        self,
        task: Dict[str, Any],
        result: Dict[str, Any],
        reflection: Dict[str, Any]
    ) -> float:
        """Calculate importance score for memory storage."""
        importance = 0.5  # Base importance
        
        # High importance for failures (learning opportunities)
        if not result.get('success', True):
            importance += 0.3
        
        # High importance for novel situations
        if not reflection.get('similar_experiences'):
            importance += 0.2
        
        # High importance for high-priority tasks
        priority = task.get('priority', 2)
        importance += (priority - 2) * 0.1
        
        # High importance for learning experiences
        if reflection.get('learning_occurred', False):
            importance += 0.2
        
        return min(1.0, importance)
    
    async def _find_similar_experiences(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar past experiences for metacognitive assessment."""
        try:
            task_type = task.get('type', '')
            task_description = task.get('description', '').lower()
            
            similar_experiences = []
            
            # Search episodic memory for similar tasks
            for memory in self.episodic_memory:
                if memory.experience_type == 'task':
                    stored_task = memory.content.get('task', {})
                    stored_type = stored_task.get('type', '')
                    stored_description = stored_task.get('description', '').lower()
                    
                    # Simple similarity based on task type and description overlap
                    similarity = 0.0
                    if stored_type == task_type:
                        similarity += 0.5
                    
                    # Check for common words in description
                    task_words = set(task_description.split())
                    stored_words = set(stored_description.split())
                    if task_words and stored_words:
                        word_overlap = len(task_words.intersection(stored_words))
                        similarity += (word_overlap / len(task_words.union(stored_words))) * 0.5
                    
                    if similarity > 0.3:  # Threshold for similarity
                        similar_experiences.append({
                            'memory_id': memory.memory_id,
                            'similarity': similarity,
                            'success': memory.content.get('result', {}).get('success', False),
                            'confidence': memory.confidence
                        })
            
            # Sort by similarity and return top 5
            similar_experiences.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_experiences[:5]
            
        except Exception as e:
            logger.error(f"Error finding similar experiences: {e}")
            return []
    
    async def _quick_pattern_match(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Quick pattern matching for System 1 processing."""
        try:
            task_type = task.get('type', '')
            
            # Check procedural memory for known patterns
            if task_type in self.procedural_memory:
                pattern = self.procedural_memory[task_type]
                return {
                    'result': pattern.get('typical_result', 'Pattern-based result'),
                    'confidence': pattern.get('confidence', 0.7),
                    'explanation': f"Pattern match for {task_type} tasks"
                }
            
            # Check for very similar recent tasks
            for memory in self.episodic_memory[-10:]:  # Check last 10 memories
                if (memory.experience_type == 'task' and 
                    memory.content.get('task', {}).get('type') == task_type):
                    
                    past_result = memory.content.get('result', {})
                    if past_result.get('success', False):
                        return {
                            'result': past_result,
                            'confidence': min(memory.confidence, 0.8),
                            'explanation': 'Similar recent successful task'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pattern matching: {e}")
            return None
    
    def _generate_detailed_explanation(
        self,
        reasoning_chain: ReasoningChain,
        base_result: Dict[str, Any]
    ) -> str:
        """Generate detailed explanation combining reasoning and results."""
        try:
            explanation_parts = [
                f"System 2 Analytical Processing completed:",
                f"",
                f"Reasoning Chain ({reasoning_chain.chain_id}):",
                f"- Goal: {reasoning_chain.goal}",
                f"- Steps: {len(reasoning_chain.steps)}",
                f"- Confidence: {reasoning_chain.overall_confidence:.2f}",
                f"- Conclusion: {reasoning_chain.final_conclusion}",
                f"",
                f"Reasoning Path:"
            ]
            
            for i, step in enumerate(reasoning_chain.reasoning_path, 1):
                explanation_parts.append(f"{i}. {step}")
            
            explanation_parts.extend([
                f"",
                f"Final Result: {base_result.get('success', 'Unknown')}",
                f"Overall Confidence: {base_result.get('confidence', 0.5):.2f}"
            ])
            
            return "\n".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Detailed analytical processing completed"
    
    async def _update_performance_metrics(self, experience: LearningExperience):
        """Update performance metrics based on learning experience."""
        try:
            # Update success rate
            total_experiences = len(self.learning_experiences)
            successful_experiences = sum(1 for exp in self.learning_experiences if exp.outcome == 'success')
            
            if total_experiences > 0:
                self.performance_metrics['task_success_rate'] = successful_experiences / total_experiences
            
            # Update average confidence
            confidences = [exp.confidence_change + 0.5 for exp in self.learning_experiences]  # Convert to absolute
            if confidences:
                self.performance_metrics['average_confidence'] = sum(confidences) / len(confidences)
            
            # Update learning rate (how often agent learns something new)
            recent_experiences = [exp for exp in self.learning_experiences 
                               if exp.timestamp > datetime.utcnow() - timedelta(hours=24)]
            self.performance_metrics['learning_rate'] = len(recent_experiences) / max(1, len(self.learning_experiences))
            
            # Store confidence history
            self.confidence_history.append((datetime.utcnow(), experience.confidence_change + 0.5))
            
            # Keep history manageable
            if len(self.confidence_history) > 1000:
                self.confidence_history = self.confidence_history[-800:]
                
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    async def get_cognitive_status(self) -> Dict[str, Any]:
        """Get comprehensive cognitive status of the agent."""
        try:
            return {
                'agent_id': self.agent_id,
                'cognitive_state': self.cognitive_state.value,
                'metacognitive_level': self.metacognitive_level.value,
                'performance_metrics': self.performance_metrics,
                'cognitive_preferences': self.cognitive_preferences,
                'memory_status': {
                    'episodic_memories': len(self.episodic_memory),
                    'semantic_knowledge_areas': len(self.semantic_memory),
                    'procedural_patterns': len(self.procedural_memory),
                    'working_memory_items': len(self.working_memory)
                },
                'learning_status': {
                    'total_experiences': len(self.learning_experiences),
                    'recent_learning_rate': self.performance_metrics['learning_rate'],
                    'adaptation_indicators': {
                        'confidence_trend': 'stable',  # Would calculate from history
                        'strategy_effectiveness': 'improving'  # Would calculate from recent performance
                    }
                },
                'reasoning_capabilities': {
                    'available_reasoning_types': [rt.value for rt in ReasoningType],
                    'preferred_reasoning': self.cognitive_preferences['preferred_reasoning_type'].value,
                    'reasoning_engine_status': 'active'
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting cognitive status: {e}")
            return {'error': str(e)}
    
    def __repr__(self):
        return (f"CognitiveAgent(id={self.agent_id}, state={self.cognitive_state.value}, "
                f"metacognitive_level={self.metacognitive_level.value}, "
                f"success_rate={self.performance_metrics['task_success_rate']:.2f})")