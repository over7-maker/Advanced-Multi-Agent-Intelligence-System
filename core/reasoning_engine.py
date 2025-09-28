"""
AMAS Reasoning Engine - Advanced Cognitive Reasoning Implementation

This module implements advanced reasoning capabilities for the AMAS cognitive architecture:
- Deductive reasoning (general to specific)
- Inductive reasoning (specific to general)  
- Abductive reasoning (best explanation)
- Causal reasoning and commonsense knowledge
- Explainable AI with reasoning traces
- Confidence scoring and uncertainty handling

Based on cognitive science research and explainable AI principles.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning processes"""
    DEDUCTIVE = "deductive"      # General principles to specific conclusions
    INDUCTIVE = "inductive"      # Specific observations to general patterns
    ABDUCTIVE = "abductive"      # Best explanation for observations
    CAUSAL = "causal"           # Cause and effect relationships
    ANALOGICAL = "analogical"    # Reasoning by analogy
    TEMPORAL = "temporal"        # Time-based reasoning


class ConfidenceLevel(Enum):
    """Confidence levels for reasoning outcomes"""
    VERY_LOW = (0.0, 0.2, "Very Low")
    LOW = (0.2, 0.4, "Low")
    MEDIUM = (0.4, 0.6, "Medium")
    HIGH = (0.6, 0.8, "High")
    VERY_HIGH = (0.8, 1.0, "Very High")
    
    def __init__(self, min_val, max_val, label):
        self.min_val = min_val
        self.max_val = max_val
        self.label = label


@dataclass
class ReasoningStep:
    """Individual step in a reasoning process"""
    step_id: str
    reasoning_type: ReasoningType
    premise: str
    conclusion: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    explanation: str = ""


@dataclass
class ReasoningChain:
    """Chain of reasoning steps leading to a conclusion"""
    chain_id: str
    goal: str
    steps: List[ReasoningStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0
    reasoning_path: List[str] = field(default_factory=list)
    alternative_explanations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class KnowledgeItem:
    """Item in the commonsense knowledge base"""
    item_id: str
    category: str
    statement: str
    confidence: float
    source: str
    examples: List[str] = field(default_factory=list)
    related_items: List[str] = field(default_factory=list)


class AdvancedReasoningEngine:
    """
    Advanced reasoning engine implementing multiple reasoning paradigms
    with explainable AI capabilities and commonsense knowledge integration.
    """
    
    def __init__(self):
        self.reasoning_chains: Dict[str, ReasoningChain] = {}
        self.knowledge_base = CommonsenseKnowledgeBase()
        self.causal_network = CausalNetwork()
        self.reasoning_patterns = ReasoningPatterns()
        
        # Reasoning performance metrics
        self.reasoning_metrics = {
            'total_reasoning_chains': 0,
            'successful_conclusions': 0,
            'average_confidence': 0.0,
            'reasoning_type_usage': defaultdict(int),
            'average_chain_length': 0.0
        }
        
        logger.info("Advanced Reasoning Engine initialized")
    
    async def reason_about_problem(
        self,
        problem_description: str,
        context: Dict[str, Any],
        goal: str,
        reasoning_type: Optional[ReasoningType] = None
    ) -> ReasoningChain:
        """
        Main reasoning method that analyzes a problem and generates a reasoning chain.
        
        Args:
            problem_description: Description of the problem to reason about
            context: Additional context and evidence
            goal: The reasoning goal or question to answer
            reasoning_type: Preferred reasoning type (auto-selected if None)
            
        Returns:
            ReasoningChain with steps and conclusions
        """
        try:
            chain_id = f"reasoning_chain_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Create reasoning chain
            chain = ReasoningChain(
                chain_id=chain_id,
                goal=goal
            )
            
            # Auto-select reasoning type if not specified
            if reasoning_type is None:
                reasoning_type = await self._select_reasoning_type(problem_description, goal)
            
            logger.info(f"Starting {reasoning_type.value} reasoning for: {goal}")
            
            # Execute reasoning based on type
            if reasoning_type == ReasoningType.DEDUCTIVE:
                await self._deductive_reasoning(chain, problem_description, context)
            elif reasoning_type == ReasoningType.INDUCTIVE:
                await self._inductive_reasoning(chain, problem_description, context)
            elif reasoning_type == ReasoningType.ABDUCTIVE:
                await self._abductive_reasoning(chain, problem_description, context)
            elif reasoning_type == ReasoningType.CAUSAL:
                await self._causal_reasoning(chain, problem_description, context)
            elif reasoning_type == ReasoningType.ANALOGICAL:
                await self._analogical_reasoning(chain, problem_description, context)
            elif reasoning_type == ReasoningType.TEMPORAL:
                await self._temporal_reasoning(chain, problem_description, context)
            else:
                # Default to abductive reasoning
                await self._abductive_reasoning(chain, problem_description, context)
            
            # Calculate overall confidence
            chain.overall_confidence = self._calculate_chain_confidence(chain)
            
            # Generate alternative explanations
            chain.alternative_explanations = await self._generate_alternatives(chain, context)
            
            # Store reasoning chain
            self.reasoning_chains[chain_id] = chain
            
            # Update metrics
            await self._update_reasoning_metrics(chain, reasoning_type)
            
            logger.info(f"Reasoning chain completed with confidence {chain.overall_confidence:.2f}")
            
            return chain
            
        except Exception as e:
            logger.error(f"Error in reasoning process: {e}")
            raise
    
    async def _select_reasoning_type(
        self,
        problem_description: str,
        goal: str
    ) -> ReasoningType:
        """Select the most appropriate reasoning type for the problem"""
        try:
            description_lower = problem_description.lower()
            goal_lower = goal.lower()
            
            # Pattern matching for reasoning type selection
            if any(word in description_lower for word in ['why', 'explain', 'cause', 'because']):
                return ReasoningType.ABDUCTIVE
            
            if any(word in description_lower for word in ['predict', 'forecast', 'pattern', 'trend']):
                return ReasoningType.INDUCTIVE
            
            if any(word in description_lower for word in ['if', 'then', 'therefore', 'conclude']):
                return ReasoningType.DEDUCTIVE
            
            if any(word in description_lower for word in ['timeline', 'sequence', 'before', 'after']):
                return ReasoningType.TEMPORAL
            
            if any(word in description_lower for word in ['similar', 'like', 'compare', 'analogy']):
                return ReasoningType.ANALOGICAL
            
            if any(word in description_lower for word in ['leads to', 'results in', 'impact', 'effect']):
                return ReasoningType.CAUSAL
            
            # Default to abductive reasoning for explanatory problems
            return ReasoningType.ABDUCTIVE
            
        except Exception as e:
            logger.error(f"Error selecting reasoning type: {e}")
            return ReasoningType.ABDUCTIVE
    
    async def _deductive_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Deductive reasoning: Apply general principles to reach specific conclusions.
        
        Structure: Major premise → Minor premise → Conclusion
        """
        try:
            # Step 1: Identify general principles/rules
            principles = await self._extract_principles(problem_description, context)
            
            for i, principle in enumerate(principles):
                step = ReasoningStep(
                    step_id=f"{chain.chain_id}_deductive_{i+1}",
                    reasoning_type=ReasoningType.DEDUCTIVE,
                    premise=principle['statement'],
                    conclusion="",
                    confidence=principle['confidence'],
                    evidence=principle.get('evidence', []),
                    explanation=f"General principle: {principle['statement']}"
                )
                chain.steps.append(step)
            
            # Step 2: Apply principles to specific case
            if principles:
                application_step = ReasoningStep(
                    step_id=f"{chain.chain_id}_deductive_application",
                    reasoning_type=ReasoningType.DEDUCTIVE,
                    premise=f"Applying principles to: {problem_description}",
                    conclusion="",
                    confidence=0.7,
                    explanation="Applying general principles to specific case"
                )
                
                # Generate specific conclusion
                conclusion = await self._apply_deductive_logic(principles, problem_description, context)
                application_step.conclusion = conclusion
                chain.steps.append(application_step)
                chain.final_conclusion = conclusion
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in deductive reasoning: {e}")
            chain.final_conclusion = "Deductive reasoning process encountered an error"
    
    async def _inductive_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Inductive reasoning: Generalize from specific observations to broader patterns.
        """
        try:
            # Step 1: Collect specific observations
            observations = await self._extract_observations(problem_description, context)
            
            for i, obs in enumerate(observations):
                step = ReasoningStep(
                    step_id=f"{chain.chain_id}_inductive_obs_{i+1}",
                    reasoning_type=ReasoningType.INDUCTIVE,
                    premise=obs['observation'],
                    conclusion="",
                    confidence=obs['reliability'],
                    evidence=[obs['observation']],
                    explanation=f"Observation {i+1}: {obs['observation']}"
                )
                chain.steps.append(step)
            
            # Step 2: Identify patterns
            if observations:
                patterns = await self._identify_patterns(observations)
                
                pattern_step = ReasoningStep(
                    step_id=f"{chain.chain_id}_inductive_pattern",
                    reasoning_type=ReasoningType.INDUCTIVE,
                    premise="Pattern analysis of observations",
                    conclusion="",
                    confidence=0.6,
                    explanation="Identifying patterns in observations"
                )
                
                # Step 3: Generalize to broader principle
                generalization = await self._generalize_pattern(patterns, context)
                pattern_step.conclusion = generalization
                chain.steps.append(pattern_step)
                chain.final_conclusion = generalization
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in inductive reasoning: {e}")
            chain.final_conclusion = "Inductive reasoning process encountered an error"
    
    async def _abductive_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Abductive reasoning: Find the best explanation for observations.
        
        This is the core of explanatory AI - finding plausible explanations.
        """
        try:
            # Step 1: Identify phenomena to explain
            phenomena = await self._extract_phenomena(problem_description, context)
            
            phenomena_step = ReasoningStep(
                step_id=f"{chain.chain_id}_abductive_phenomena",
                reasoning_type=ReasoningType.ABDUCTIVE,
                premise=f"Phenomena to explain: {phenomena}",
                conclusion="",
                confidence=0.8,
                evidence=phenomena,
                explanation="Identifying phenomena requiring explanation"
            )
            chain.steps.append(phenomena_step)
            
            # Step 2: Generate possible explanations
            explanations = await self._generate_explanations(phenomena, context)
            
            for i, explanation in enumerate(explanations):
                exp_step = ReasoningStep(
                    step_id=f"{chain.chain_id}_abductive_exp_{i+1}",
                    reasoning_type=ReasoningType.ABDUCTIVE,
                    premise=f"Possible explanation: {explanation['hypothesis']}",
                    conclusion="",
                    confidence=explanation['plausibility'],
                    evidence=explanation.get('supporting_evidence', []),
                    explanation=f"Hypothesis {i+1}: {explanation['hypothesis']}"
                )
                chain.steps.append(exp_step)
            
            # Step 3: Select best explanation
            if explanations:
                best_explanation = await self._select_best_explanation(explanations, context)
                
                conclusion_step = ReasoningStep(
                    step_id=f"{chain.chain_id}_abductive_conclusion",
                    reasoning_type=ReasoningType.ABDUCTIVE,
                    premise="Selecting best explanation based on criteria",
                    conclusion=best_explanation['explanation'],
                    confidence=best_explanation['confidence'],
                    evidence=best_explanation.get('evidence', []),
                    explanation=f"Best explanation: {best_explanation['explanation']}"
                )
                chain.steps.append(conclusion_step)
                chain.final_conclusion = best_explanation['explanation']
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in abductive reasoning: {e}")
            chain.final_conclusion = "Abductive reasoning process encountered an error"
    
    async def _causal_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Causal reasoning: Understand cause-and-effect relationships.
        """
        try:
            # Step 1: Identify potential causes and effects
            causal_elements = await self._extract_causal_elements(problem_description, context)
            
            # Step 2: Build causal chain
            causal_chain = await self.causal_network.build_causal_chain(
                causal_elements['causes'],
                causal_elements['effects']
            )
            
            for i, link in enumerate(causal_chain):
                step = ReasoningStep(
                    step_id=f"{chain.chain_id}_causal_{i+1}",
                    reasoning_type=ReasoningType.CAUSAL,
                    premise=link['cause'],
                    conclusion=link['effect'],
                    confidence=link['strength'],
                    evidence=link.get('evidence', []),
                    explanation=f"Causal link: {link['cause']} → {link['effect']}"
                )
                chain.steps.append(step)
            
            # Step 3: Draw causal conclusion
            if causal_chain:
                final_effect = causal_chain[-1]['effect']
                chain.final_conclusion = f"Causal analysis indicates: {final_effect}"
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in causal reasoning: {e}")
            chain.final_conclusion = "Causal reasoning process encountered an error"
    
    async def _analogical_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Analogical reasoning: Reason by analogy to similar situations.
        """
        try:
            # Step 1: Find analogous situations
            analogies = await self._find_analogies(problem_description, context)
            
            for i, analogy in enumerate(analogies):
                step = ReasoningStep(
                    step_id=f"{chain.chain_id}_analogical_{i+1}",
                    reasoning_type=ReasoningType.ANALOGICAL,
                    premise=f"Analogy to: {analogy['source_situation']}",
                    conclusion=analogy['inference'],
                    confidence=analogy['similarity_score'],
                    evidence=analogy.get('similarities', []),
                    explanation=f"Analogy {i+1}: {analogy['source_situation']} → {analogy['inference']}"
                )
                chain.steps.append(step)
            
            # Step 2: Synthesize analogical insights
            if analogies:
                synthesis = await self._synthesize_analogies(analogies)
                chain.final_conclusion = synthesis
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in analogical reasoning: {e}")
            chain.final_conclusion = "Analogical reasoning process encountered an error"
    
    async def _temporal_reasoning(
        self,
        chain: ReasoningChain,
        problem_description: str,
        context: Dict[str, Any]
    ):
        """
        Temporal reasoning: Reason about time-based sequences and relationships.
        """
        try:
            # Step 1: Extract temporal elements
            temporal_elements = await self._extract_temporal_elements(problem_description, context)
            
            # Step 2: Build temporal sequence
            timeline = await self._build_timeline(temporal_elements)
            
            for i, event in enumerate(timeline):
                step = ReasoningStep(
                    step_id=f"{chain.chain_id}_temporal_{i+1}",
                    reasoning_type=ReasoningType.TEMPORAL,
                    premise=f"Time: {event['time']}",
                    conclusion=event['event'],
                    confidence=event['certainty'],
                    evidence=event.get('evidence', []),
                    explanation=f"Temporal event {i+1}: {event['event']} at {event['time']}"
                )
                chain.steps.append(step)
            
            # Step 3: Draw temporal conclusions
            if timeline:
                temporal_conclusion = await self._analyze_temporal_patterns(timeline)
                chain.final_conclusion = temporal_conclusion
            
            chain.reasoning_path = [step.explanation for step in chain.steps]
            
        except Exception as e:
            logger.error(f"Error in temporal reasoning: {e}")
            chain.final_conclusion = "Temporal reasoning process encountered an error"
    
    def _calculate_chain_confidence(self, chain: ReasoningChain) -> float:
        """Calculate overall confidence for the reasoning chain"""
        if not chain.steps:
            return 0.0
        
        # Weighted average with decay for longer chains
        total_confidence = 0.0
        total_weight = 0.0
        
        for i, step in enumerate(chain.steps):
            # Later steps have slightly less weight due to error propagation
            weight = 1.0 / (1.0 + i * 0.1)
            total_confidence += step.confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    async def _generate_alternatives(
        self,
        chain: ReasoningChain,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate alternative explanations or conclusions"""
        try:
            alternatives = []
            
            # Generate alternatives based on different reasoning approaches
            if chain.steps:
                last_step = chain.steps[-1]
                
                # Alternative based on uncertainty
                if last_step.confidence < 0.7:
                    alternatives.append(f"Alternative: {last_step.conclusion} (with lower confidence)")
                
                # Alternative based on different assumptions
                alternatives.append("Alternative: Consider different underlying assumptions")
                
                # Alternative based on incomplete information
                alternatives.append("Alternative: Additional information may change conclusion")
            
            return alternatives[:3]  # Limit to top 3 alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternatives: {e}")
            return []
    
    async def _update_reasoning_metrics(
        self,
        chain: ReasoningChain,
        reasoning_type: ReasoningType
    ):
        """Update reasoning performance metrics"""
        try:
            self.reasoning_metrics['total_reasoning_chains'] += 1
            
            if chain.final_conclusion and chain.overall_confidence > 0.5:
                self.reasoning_metrics['successful_conclusions'] += 1
            
            # Update average confidence
            current_avg = self.reasoning_metrics['average_confidence']
            total_chains = self.reasoning_metrics['total_reasoning_chains']
            self.reasoning_metrics['average_confidence'] = (
                (current_avg * (total_chains - 1) + chain.overall_confidence) / total_chains
            )
            
            # Update reasoning type usage
            self.reasoning_metrics['reasoning_type_usage'][reasoning_type.value] += 1
            
            # Update average chain length
            current_avg_length = self.reasoning_metrics['average_chain_length']
            chain_length = len(chain.steps)
            self.reasoning_metrics['average_chain_length'] = (
                (current_avg_length * (total_chains - 1) + chain_length) / total_chains
            )
            
        except Exception as e:
            logger.error(f"Error updating reasoning metrics: {e}")
    
    # Placeholder methods for complex reasoning operations
    # In a full implementation, these would contain sophisticated logic
    
    async def _extract_principles(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract general principles applicable to the problem"""
        # Simplified implementation
        return [
            {
                'statement': 'General principle extracted from problem context',
                'confidence': 0.7,
                'evidence': ['Context analysis']
            }
        ]
    
    async def _apply_deductive_logic(self, principles: List[Dict[str, Any]], description: str, context: Dict[str, Any]) -> str:
        """Apply deductive logic to reach conclusion"""
        return f"Based on principles, conclusion: {description}"
    
    async def _extract_observations(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific observations from the problem"""
        return [
            {
                'observation': f'Observation from: {description}',
                'reliability': 0.8
            }
        ]
    
    async def _identify_patterns(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns in observations"""
        return [{'pattern': 'Common pattern identified', 'strength': 0.7}]
    
    async def _generalize_pattern(self, patterns: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Generalize patterns to broader principle"""
        return "Generalized principle based on observed patterns"
    
    async def _extract_phenomena(self, description: str, context: Dict[str, Any]) -> List[str]:
        """Extract phenomena that need explanation"""
        return [description]
    
    async def _generate_explanations(self, phenomena: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate possible explanations for phenomena"""
        return [
            {
                'hypothesis': f'Possible explanation for: {phenomena[0] if phenomena else "phenomenon"}',
                'plausibility': 0.7,
                'supporting_evidence': ['Evidence 1', 'Evidence 2']
            }
        ]
    
    async def _select_best_explanation(self, explanations: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best explanation based on criteria"""
        if explanations:
            best = max(explanations, key=lambda x: x['plausibility'])
            return {
                'explanation': best['hypothesis'],
                'confidence': best['plausibility'],
                'evidence': best.get('supporting_evidence', [])
            }
        return {'explanation': 'No explanation found', 'confidence': 0.0, 'evidence': []}
    
    async def _extract_causal_elements(self, description: str, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract potential causes and effects"""
        return {
            'causes': ['Potential cause 1', 'Potential cause 2'],
            'effects': ['Potential effect 1', 'Potential effect 2']
        }
    
    async def _find_analogies(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find analogous situations"""
        return [
            {
                'source_situation': 'Similar situation',
                'inference': 'Inference from analogy',
                'similarity_score': 0.6,
                'similarities': ['Similarity 1', 'Similarity 2']
            }
        ]
    
    async def _synthesize_analogies(self, analogies: List[Dict[str, Any]]) -> str:
        """Synthesize insights from analogies"""
        return "Synthesized insight from analogical reasoning"
    
    async def _extract_temporal_elements(self, description: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract temporal elements"""
        return [
            {
                'event': 'Temporal event',
                'time': 'Time reference',
                'certainty': 0.7
            }
        ]
    
    async def _build_timeline(self, temporal_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build chronological timeline"""
        return temporal_elements  # Simplified
    
    async def _analyze_temporal_patterns(self, timeline: List[Dict[str, Any]]) -> str:
        """Analyze patterns in temporal sequence"""
        return "Temporal pattern analysis conclusion"


class CommonsenseKnowledgeBase:
    """Commonsense knowledge base for reasoning support"""
    
    def __init__(self):
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self._initialize_basic_knowledge()
    
    def _initialize_basic_knowledge(self):
        """Initialize with basic commonsense knowledge"""
        # This would be populated with extensive commonsense knowledge
        basic_items = [
            {
                'item_id': 'causality_001',
                'category': 'causality',
                'statement': 'Actions have consequences',
                'confidence': 0.9,
                'source': 'commonsense',
                'examples': ['Dropping something causes it to fall']
            }
        ]
        
        for item_data in basic_items:
            item = KnowledgeItem(**item_data)
            self.knowledge_items[item.item_id] = item


class CausalNetwork:
    """Causal network for understanding cause-effect relationships"""
    
    async def build_causal_chain(
        self,
        causes: List[str],
        effects: List[str]
    ) -> List[Dict[str, Any]]:
        """Build causal chain linking causes to effects"""
        causal_links = []
        
        # Simplified causal chain building
        for i, (cause, effect) in enumerate(zip(causes, effects)):
            causal_links.append({
                'cause': cause,
                'effect': effect,
                'strength': 0.7,  # Causal strength
                'evidence': [f'Evidence for {cause} → {effect}']
            })
        
        return causal_links


class ReasoningPatterns:
    """Common reasoning patterns and heuristics"""
    
    def __init__(self):
        self.patterns = {
            'modus_ponens': 'If P then Q; P; therefore Q',
            'modus_tollens': 'If P then Q; not Q; therefore not P',
            'hypothetical_syllogism': 'If P then Q; if Q then R; therefore if P then R'
        }
    
    def get_pattern(self, pattern_name: str) -> Optional[str]:
        """Get reasoning pattern by name"""
        return self.patterns.get(pattern_name)