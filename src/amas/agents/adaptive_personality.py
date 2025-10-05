#!/usr/bin/env python3
"""
Adaptive Agent Personality System
Dynamic personality adaptation based on user preferences and task context
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging

@dataclass
class PersonalityTrait:
    name: str
    current_value: float  # 0.0 to 1.0
    default_value: float
    adaptation_rate: float  # How quickly this trait adapts
    context_modifiers: Dict[str, float]  # Task-specific modifiers

@dataclass
class UserInteractionPattern:
    user_id: str
    interaction_type: str
    preference_indicators: Dict[str, float]
    feedback_score: float
    context: Dict[str, Any]
    timestamp: str

@dataclass
class AdaptationRule:
    rule_id: str
    trigger_condition: str
    trait_adjustments: Dict[str, float]
    confidence: float
    success_rate: float
    usage_count: int

class AdaptiveAgentPersonality:
    """Adaptive personality system for individual agents"""
    
    def __init__(self, agent_id: str, base_personality: Optional[Dict[str, float]] = None):
        self.agent_id = agent_id
        self.personality_traits = self._initialize_personality_traits(base_personality)
        self.interaction_history: List[UserInteractionPattern] = []
        self.adaptation_rules: Dict[str, AdaptationRule] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.context_memory: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load persisted data
        self._load_personality_data()
    
    def _initialize_personality_traits(self, base_personality: Optional[Dict[str, float]] = None) -> Dict[str, PersonalityTrait]:
        """Initialize personality traits with defaults"""
        
        # Default personality configurations per agent type
        default_personalities = {
            "security_expert": {
                "confidence": 0.85,
                "precision": 0.9,
                "communication_style": 0.7,  # 0 = technical, 1 = conversational
                "risk_tolerance": 0.2,  # Lower = more cautious
                "collaboration": 0.75,
                "creativity": 0.4,
                "empathy": 0.6,
                "assertiveness": 0.8
            },
            "code_analysis": {
                "confidence": 0.8,
                "precision": 0.95,
                "communication_style": 0.6,
                "risk_tolerance": 0.3,
                "collaboration": 0.8,
                "creativity": 0.7,
                "empathy": 0.7,
                "assertiveness": 0.6
            },
            "intelligence_gathering": {
                "confidence": 0.75,
                "precision": 0.8,
                "communication_style": 0.8,
                "risk_tolerance": 0.6,
                "collaboration": 0.85,
                "creativity": 0.8,
                "empathy": 0.8,
                "assertiveness": 0.5
            },
            "performance_monitor": {
                "confidence": 0.9,
                "precision": 0.9,
                "communication_style": 0.5,
                "risk_tolerance": 0.4,
                "collaboration": 0.7,
                "creativity": 0.3,
                "empathy": 0.5,
                "assertiveness": 0.7
            }
        }
        
        # Get base personality or use agent-specific defaults
        if base_personality:
            personality_values = base_personality
        else:
            personality_values = default_personalities.get(
                self.agent_id, 
                default_personalities["code_analysis"]  # Default fallback
            )
        
        traits = {}
        for trait_name, default_value in personality_values.items():
            traits[trait_name] = PersonalityTrait(
                name=trait_name,
                current_value=default_value,
                default_value=default_value,
                adaptation_rate=0.1,  # 10% adaptation rate by default
                context_modifiers={}
            )
        
        return traits
    
    def _load_personality_data(self):
        """Load persisted personality data"""
        try:
            data_file = f"data/personalities/{self.agent_id}_personality.pkl"
            with open(data_file, 'rb') as f:
                data = pickle.load(f)
                self.personality_traits = data.get('traits', self.personality_traits)
                self.interaction_history = data.get('history', [])
                self.adaptation_rules = data.get('rules', {})
                self.user_profiles = data.get('profiles', {})
            
            self.logger.info(f"✅ Loaded personality data for {self.agent_id}")
        except FileNotFoundError:
            self.logger.info(f"📝 Creating new personality profile for {self.agent_id}")
        except Exception as e:
            self.logger.warning(f"⚠️ Error loading personality data: {e}")
    
    def _save_personality_data(self):
        """Save personality data to persistent storage"""
        try:
            import os
            os.makedirs("data/personalities", exist_ok=True)
            
            data = {
                'traits': self.personality_traits,
                'history': self.interaction_history[-1000:],  # Keep last 1000 interactions
                'rules': self.adaptation_rules,
                'profiles': self.user_profiles
            }
            
            data_file = f"data/personalities/{self.agent_id}_personality.pkl"
            with open(data_file, 'wb') as f:
                pickle.dump(data, f)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving personality data: {e}")
    
    async def record_user_interaction(self, user_id: str, interaction_type: str, 
                                    user_feedback: Optional[Dict[str, Any]] = None,
                                    task_context: Optional[Dict[str, Any]] = None):
        """Record a user interaction for personality adaptation"""
        
        # Extract preference indicators from feedback
        preference_indicators = {}
        feedback_score = 0.5  # Neutral default
        
        if user_feedback:
            # Analyze feedback for personality preferences
            feedback_text = str(user_feedback).lower()
            
            # Communication style preferences
            if any(word in feedback_text for word in ['detailed', 'thorough', 'complete']):
                preference_indicators['prefers_detailed'] = 1.0
            elif any(word in feedback_text for word in ['brief', 'summary', 'quick']):
                preference_indicators['prefers_brief'] = 1.0
            
            # Technical level preferences  
            if any(word in feedback_text for word in ['technical', 'deep', 'advanced']):
                preference_indicators['prefers_technical'] = 1.0
            elif any(word in feedback_text for word in ['simple', 'basic', 'easy']):
                preference_indicators['prefers_simple'] = 1.0
            
            # Confidence level preferences
            if any(word in feedback_text for word in ['confident', 'certain', 'sure']):
                preference_indicators['appreciates_confidence'] = 1.0
            elif any(word in feedback_text for word in ['uncertain', 'maybe', 'possible']):
                preference_indicators['prefers_uncertainty'] = 1.0
            
            # Extract numerical feedback score if available
            if 'rating' in user_feedback:
                feedback_score = float(user_feedback['rating']) / 5.0  # Normalize to 0-1
            elif 'satisfaction' in user_feedback:
                feedback_score = float(user_feedback['satisfaction'])
        
        # Create interaction pattern
        interaction = UserInteractionPattern(
            user_id=user_id,
            interaction_type=interaction_type,
            preference_indicators=preference_indicators,
            feedback_score=feedback_score,
            context=task_context or {},
            timestamp=datetime.now().isoformat()
        )
        
        self.interaction_history.append(interaction)
        
        # Update user profile
        await self._update_user_profile(user_id, interaction)
        
        # Adapt personality based on this interaction
        await self._adapt_personality_from_interaction(interaction)
        
        # Save updated data
        self._save_personality_data()
        
        self.logger.info(f"📝 Recorded interaction for {user_id} with {self.agent_id}")
    
    async def _update_user_profile(self, user_id: str, interaction: UserInteractionPattern):
        """Update user profile based on interaction"""
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'interaction_count': 0,
                'avg_satisfaction': 0.5,
                'preferences': {},
                'common_contexts': [],
                'last_interaction': None
            }
        
        profile = self.user_profiles[user_id]
        
        # Update interaction count and satisfaction
        profile['interaction_count'] += 1
        current_avg = profile['avg_satisfaction']
        new_avg = (current_avg * (profile['interaction_count'] - 1) + interaction.feedback_score) / profile['interaction_count']
        profile['avg_satisfaction'] = new_avg
        
        # Update preferences
        for pref, value in interaction.preference_indicators.items():
            if pref in profile['preferences']:
                # Exponential moving average
                profile['preferences'][pref] = 0.7 * profile['preferences'][pref] + 0.3 * value
            else:
                profile['preferences'][pref] = value
        
        # Update common contexts
        context_str = str(interaction.context)
        if context_str not in profile['common_contexts']:
            profile['common_contexts'].append(context_str)
            if len(profile['common_contexts']) > 10:  # Keep only last 10 contexts
                profile['common_contexts'] = profile['common_contexts'][-10:]
        
        profile['last_interaction'] = interaction.timestamp
    
    async def _adapt_personality_from_interaction(self, interaction: UserInteractionPattern):
        """Adapt personality traits based on user interaction"""
        
        adaptation_strength = 0.05  # Base adaptation strength
        
        # Increase adaptation strength for repeated feedback patterns
        user_profile = self.user_profiles.get(interaction.user_id, {})
        if user_profile.get('interaction_count', 0) > 5:
            adaptation_strength = 0.1  # Stronger adaptation for established users
        
        # Adapt based on preference indicators
        for preference, strength in interaction.preference_indicators.items():
            if preference == 'prefers_detailed':
                await self._adjust_trait('communication_style', -0.1 * strength * adaptation_strength)
                await self._adjust_trait('precision', 0.05 * strength * adaptation_strength)
            
            elif preference == 'prefers_brief':
                await self._adjust_trait('communication_style', 0.1 * strength * adaptation_strength)
                await self._adjust_trait('precision', -0.05 * strength * adaptation_strength)
            
            elif preference == 'prefers_technical':
                await self._adjust_trait('communication_style', -0.15 * strength * adaptation_strength)
                await self._adjust_trait('precision', 0.1 * strength * adaptation_strength)
            
            elif preference == 'prefers_simple':
                await self._adjust_trait('communication_style', 0.15 * strength * adaptation_strength)
                await self._adjust_trait('empathy', 0.05 * strength * adaptation_strength)
            
            elif preference == 'appreciates_confidence':
                await self._adjust_trait('confidence', 0.1 * strength * adaptation_strength)
                await self._adjust_trait('assertiveness', 0.05 * strength * adaptation_strength)
            
            elif preference == 'prefers_uncertainty':
                await self._adjust_trait('confidence', -0.05 * strength * adaptation_strength)
                await self._adjust_trait('empathy', 0.05 * strength * adaptation_strength)
        
        # Adapt based on feedback score
        if interaction.feedback_score > 0.8:
            # Reinforce current personality
            for trait in self.personality_traits.values():
                trait.current_value = trait.current_value * 1.01  # Slight reinforcement
        elif interaction.feedback_score < 0.3:
            # Move slightly toward default personality
            for trait in self.personality_traits.values():
                diff = trait.default_value - trait.current_value
                trait.current_value += diff * 0.05  # Small move toward default
    
    async def _adjust_trait(self, trait_name: str, adjustment: float):
        """Adjust a specific personality trait"""
        
        if trait_name in self.personality_traits:
            trait = self.personality_traits[trait_name]
            new_value = trait.current_value + adjustment
            
            # Clamp to valid range [0, 1]
            trait.current_value = max(0.0, min(1.0, new_value))
    
    async def adapt_to_context(self, task_context: Dict[str, Any]) -> Dict[str, float]:
        """Adapt personality for specific task context"""
        
        adapted_traits = {}
        
        for trait_name, trait in self.personality_traits.items():
            base_value = trait.current_value
            
            # Apply context modifiers
            context_adjustment = 0.0
            
            # Task type adjustments
            task_type = task_context.get('task_type', '')
            
            if task_type == 'security_scan':
                if trait_name == 'precision':
                    context_adjustment += 0.1  # More precise for security
                elif trait_name == 'risk_tolerance':
                    context_adjustment -= 0.2  # More cautious for security
            
            elif task_type == 'intelligence_gathering':
                if trait_name == 'creativity':
                    context_adjustment += 0.15  # More creative for research
                elif trait_name == 'empathy':
                    context_adjustment += 0.1  # More empathetic for investigation
            
            elif task_type == 'code_analysis':
                if trait_name == 'precision':
                    context_adjustment += 0.15  # Very precise for code
                elif trait_name == 'communication_style':
                    context_adjustment -= 0.1  # More technical for code
            
            # Urgency adjustments
            urgency = task_context.get('urgency', 'normal')
            if urgency == 'high':
                if trait_name == 'confidence':
                    context_adjustment += 0.1  # More confident under pressure
                elif trait_name == 'assertiveness':
                    context_adjustment += 0.15  # More assertive when urgent
            
            # User preference adjustments
            user_id = task_context.get('user_id')
            if user_id and user_id in self.user_profiles:
                user_prefs = self.user_profiles[user_id]['preferences']
                
                if 'prefers_detailed' in user_prefs and trait_name == 'precision':
                    context_adjustment += 0.1 * user_prefs['prefers_detailed']
                
                if 'prefers_technical' in user_prefs and trait_name == 'communication_style':
                    context_adjustment -= 0.1 * user_prefs['prefers_technical']
            
            # Apply adjustment and clamp
            adapted_value = max(0.0, min(1.0, base_value + context_adjustment))
            adapted_traits[trait_name] = adapted_value
        
        return adapted_traits
    
    def generate_personality_prompt(self, adapted_traits: Dict[str, float]) -> str:
        """Generate a personality prompt for the agent"""
        
        confidence = adapted_traits.get('confidence', 0.5)
        precision = adapted_traits.get('precision', 0.5)
        communication_style = adapted_traits.get('communication_style', 0.5)
        creativity = adapted_traits.get('creativity', 0.5)
        empathy = adapted_traits.get('empathy', 0.5)
        assertiveness = adapted_traits.get('assertiveness', 0.5)
        
        prompt_parts = []
        
        # Base agent identity
        prompt_parts.append(f"You are {self.agent_id.replace('_', ' ').title()}, a specialized AI agent.")
        
        # Confidence level
        if confidence > 0.8:
            prompt_parts.append("You are highly confident in your expertise and provide definitive answers.")
        elif confidence > 0.6:
            prompt_parts.append("You are confident but acknowledge limitations when appropriate.")
        else:
            prompt_parts.append("You are careful to express uncertainty and provide qualified answers.")
        
        # Precision level
        if precision > 0.8:
            prompt_parts.append("You provide extremely detailed and precise information.")
        elif precision > 0.6:
            prompt_parts.append("You balance detail with clarity in your responses.")
        else:
            prompt_parts.append("You focus on key points and avoid overwhelming detail.")
        
        # Communication style
        if communication_style > 0.7:
            prompt_parts.append("You communicate in a conversational, accessible manner.")
        elif communication_style > 0.3:
            prompt_parts.append("You balance technical accuracy with clear communication.")
        else:
            prompt_parts.append("You use precise technical language and terminology.")
        
        # Creativity
        if creativity > 0.7:
            prompt_parts.append("You approach problems creatively and suggest innovative solutions.")
        elif creativity > 0.3:
            prompt_parts.append("You combine established methods with creative insights.")
        else:
            prompt_parts.append("You rely on proven methods and established best practices.")
        
        # Empathy
        if empathy > 0.7:
            prompt_parts.append("You are understanding and considerate of user needs and concerns.")
        elif empathy > 0.3:
            prompt_parts.append("You acknowledge user perspectives while maintaining objectivity.")
        else:
            prompt_parts.append("You focus on technical requirements and objective analysis.")
        
        # Assertiveness
        if assertiveness > 0.7:
            prompt_parts.append("You provide strong recommendations and clear guidance.")
        else:
            prompt_parts.append("You present options and allow users to make their own decisions.")
        
        return " ".join(prompt_parts)
    
    async def get_personality_summary(self) -> Dict[str, Any]:
        """Get a summary of current personality state"""
        
        return {
            "agent_id": self.agent_id,
            "current_traits": {
                name: trait.current_value 
                for name, trait in self.personality_traits.items()
            },
            "default_traits": {
                name: trait.default_value 
                for name, trait in self.personality_traits.items()
            },
            "adaptation_level": sum(
                abs(trait.current_value - trait.default_value) 
                for trait in self.personality_traits.values()
            ) / len(self.personality_traits),
            "interaction_count": len(self.interaction_history),
            "user_count": len(self.user_profiles),
            "avg_user_satisfaction": sum(
                profile['avg_satisfaction'] 
                for profile in self.user_profiles.values()
            ) / len(self.user_profiles) if self.user_profiles else 0.5
        }

class PersonalityOrchestrator:
    """Orchestrator for managing multiple agent personalities"""
    
    def __init__(self):
        self.agent_personalities: Dict[str, AdaptiveAgentPersonality] = {}
        self.global_adaptation_patterns: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent_id: str, base_personality: Optional[Dict[str, float]] = None):
        """Register an agent with the personality system"""
        
        self.agent_personalities[agent_id] = AdaptiveAgentPersonality(agent_id, base_personality)
        self.logger.info(f"✅ Registered personality for agent: {agent_id}")
    
    async def adapt_agent_for_task(self, agent_id: str, task_context: Dict[str, Any]) -> str:
        """Adapt agent personality for a specific task and return personality prompt"""
        
        if agent_id not in self.agent_personalities:
            self.logger.warning(f"⚠️ Agent {agent_id} not registered for personality adaptation")
            return f"You are {agent_id.replace('_', ' ').title()}, a specialized AI agent."
        
        personality = self.agent_personalities[agent_id]
        adapted_traits = await personality.adapt_to_context(task_context)
        prompt = personality.generate_personality_prompt(adapted_traits)
        
        return prompt
    
    async def record_task_feedback(self, agent_id: str, user_id: str, 
                                 feedback: Dict[str, Any], task_context: Dict[str, Any]):
        """Record user feedback for personality adaptation"""
        
        if agent_id in self.agent_personalities:
            await self.agent_personalities[agent_id].record_user_interaction(
                user_id, "task_completion", feedback, task_context
            )
    
    async def get_system_personality_report(self) -> Dict[str, Any]:
        """Get comprehensive personality adaptation report"""
        
        agent_summaries = {}
        total_interactions = 0
        total_satisfaction = 0
        
        for agent_id, personality in self.agent_personalities.items():
            summary = await personality.get_personality_summary()
            agent_summaries[agent_id] = summary
            total_interactions += summary['interaction_count']
            total_satisfaction += summary['avg_user_satisfaction'] * summary['interaction_count']
        
        avg_satisfaction = total_satisfaction / total_interactions if total_interactions > 0 else 0.5
        
        return {
            "total_agents": len(self.agent_personalities),
            "total_interactions": total_interactions,
            "average_satisfaction": avg_satisfaction,
            "agent_details": agent_summaries,
            "adaptation_active": True
        }

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AMAS Adaptive Personality System")
    parser.add_argument("--test", action="store_true", help="Run test scenario")
    parser.add_argument("--agent", default="security_expert", help="Agent to test")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def test_personality_adaptation():
        """Test personality adaptation"""
        
        print(f"🧪 Testing personality adaptation for {args.agent}...")
        
        orchestrator = PersonalityOrchestrator()
        orchestrator.register_agent(args.agent)
        
        # Test task adaptation
        task_context = {
            "task_type": "security_scan",
            "urgency": "high",
            "user_id": "test_user"
        }
        
        prompt = await orchestrator.adapt_agent_for_task(args.agent, task_context)
        print(f"🎭 Adapted personality prompt:\n{prompt}\n")
        
        # Simulate user feedback
        feedback = {
            "rating": 4,
            "comments": "Great work but could be more detailed",
            "prefers_detailed": True
        }
        
        await orchestrator.record_task_feedback(args.agent, "test_user", feedback, task_context)
        
        # Test adaptation after feedback
        prompt2 = await orchestrator.adapt_agent_for_task(args.agent, task_context)
        print(f"🎭 Post-feedback personality prompt:\n{prompt2}\n")
        
        # Generate report
        report = await orchestrator.get_system_personality_report()
        print(f"📊 Personality Report: {json.dumps(report, indent=2)}")
        
        print("✅ Personality adaptation test completed!")
    
    if args.test:
        asyncio.run(test_personality_adaptation())
    else:
        print("Use --test to run personality adaptation test")