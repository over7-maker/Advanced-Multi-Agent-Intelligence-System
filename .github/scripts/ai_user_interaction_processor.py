#!/usr/bin/env python3
"""
AI User Interaction Processor - Process user interactions and provide responses
Part of the AI-Powered Project Upgrade System
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from standalone_universal_ai_manager import get_manager


class AIUserInteractionProcessor:
    """Process user interactions and provide intelligent responses"""
    
    def __init__(self):
        self.manager = get_manager()
        self.interaction_data = {}
        
    async def process_user_interaction(self, user_message: str, upgrade_mode: str, 
                                     target_scope: str, priority: str) -> Dict[str, Any]:
        """Process user interaction and generate response"""
        print(f"💬 Processing user interaction...")
        print(f"User Message: {user_message}")
        print(f"Upgrade Mode: {upgrade_mode}")
        print(f"Target Scope: {target_scope}")
        print(f"Priority: {priority}")
        
        # Analyze user intent
        intent_analysis = await self._analyze_user_intent(user_message, upgrade_mode, target_scope, priority)
        
        # Generate response
        response = await self._generate_response(user_message, intent_analysis, upgrade_mode, target_scope, priority)
        
        # Create action plan
        action_plan = await self._create_action_plan(user_message, intent_analysis, upgrade_mode, target_scope, priority)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "upgrade_mode": upgrade_mode,
            "target_scope": target_scope,
            "priority": priority,
            "intent_analysis": intent_analysis,
            "response": response,
            "action_plan": action_plan,
            "ai_stats": self.manager.get_stats()
        }
    
    async def _analyze_user_intent(self, user_message: str, upgrade_mode: str, target_scope: str, priority: str) -> Dict[str, Any]:
        """Analyze user intent and requirements"""
        prompt = f"""
        Analyze the user's message and determine their intent and requirements:
        
        User Message: {user_message}
        Upgrade Mode: {upgrade_mode}
        Target Scope: {target_scope}
        Priority: {priority}
        
        Please provide:
        1. Primary intent (question, request, feedback, etc.)
        2. Technical requirements
        3. Priority level
        4. Urgency assessment
        5. Expected outcome
        6. Context understanding
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are an expert user experience analyst. Analyze user intent and requirements.",
            strategy="intelligent",
            max_tokens=2000
        )
        
        return {
            "intent_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _generate_response(self, user_message: str, intent_analysis: Dict[str, Any], 
                                upgrade_mode: str, target_scope: str, priority: str) -> Dict[str, Any]:
        """Generate intelligent response to user message"""
        prompt = f"""
        Generate a helpful and intelligent response to the user:
        
        User Message: {user_message}
        Intent Analysis: {intent_analysis.get('intent_analysis', '')}
        Upgrade Mode: {upgrade_mode}
        Target Scope: {target_scope}
        Priority: {priority}
        
        Please provide:
        1. Acknowledgment of their message
        2. Understanding of their needs
        3. Proposed solution or approach
        4. Next steps
        5. Timeline if applicable
        6. Any questions for clarification
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a helpful AI assistant. Provide clear, actionable responses to user messages.",
            strategy="intelligent",
            max_tokens=3000
        )
        
        return {
            "response": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _create_action_plan(self, user_message: str, intent_analysis: Dict[str, Any], 
                                 upgrade_mode: str, target_scope: str, priority: str) -> Dict[str, Any]:
        """Create action plan based on user message"""
        prompt = f"""
        Create a detailed action plan based on the user's message:
        
        User Message: {user_message}
        Intent Analysis: {intent_analysis.get('intent_analysis', '')}
        Upgrade Mode: {upgrade_mode}
        Target Scope: {target_scope}
        Priority: {priority}
        
        Please provide:
        1. Action items
        2. Priority order
        3. Dependencies
        4. Timeline
        5. Resources needed
        6. Success criteria
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a project manager. Create detailed action plans for user requests.",
            strategy="intelligent",
            max_tokens=2500
        )
        
        return {
            "action_plan": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI User Interaction Processor')
    parser.add_argument('--user-message', required=True, help='User message')
    parser.add_argument('--upgrade-mode', required=True, help='Upgrade mode')
    parser.add_argument('--target-scope', required=True, help='Target scope')
    parser.add_argument('--priority', required=True, help='Priority level')
    parser.add_argument('--output', default='user_interaction_response.json', help='Output file')
    
    args = parser.parse_args()
    
    processor = AIUserInteractionProcessor()
    
    try:
        result = await processor.process_user_interaction(
            user_message=args.user_message,
            upgrade_mode=args.upgrade_mode,
            target_scope=args.target_scope,
            priority=args.priority
        )
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ User interaction processed! Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print("💬 USER INTERACTION SUMMARY")
        print("="*80)
        print(f"User Message: {result['user_message']}")
        print(f"Upgrade Mode: {result['upgrade_mode']}")
        print(f"Target Scope: {result['target_scope']}")
        print(f"Priority: {result['priority']}")
        print(f"Timestamp: {result['timestamp']}")
        print("\nAI Stats:")
        for key, value in result['ai_stats'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ User interaction processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())