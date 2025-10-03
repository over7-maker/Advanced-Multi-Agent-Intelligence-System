#!/usr/bin/env python3
"""
AI Test Generator - Advanced test generation using AI
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


class AITestGenerator:
    """Advanced test generator using AI"""
    
    def __init__(self):
        self.manager = get_manager()
        self.tests = {}
        
    async def generate_tests(self, mode: str, scope: str, user_input: str) -> Dict[str, Any]:
        """Generate tests based on mode and scope"""
        print(f"🧪 Generating tests...")
        print(f"Mode: {mode}")
        print(f"Scope: {scope}")
        print(f"User Input: {user_input}")
        
        # Analyze project structure
        project_analysis = await self._analyze_project_structure(scope)
        
        # Generate tests
        tests = await self._generate_test_content(project_analysis, mode, user_input)
        
        # Create implementation plan
        implementation_plan = await self._create_implementation_plan(tests, mode)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "scope": scope,
            "user_input": user_input,
            "project_analysis": project_analysis,
            "tests": tests,
            "implementation_plan": implementation_plan,
            "ai_stats": self.manager.get_stats()
        }
    
    async def _analyze_project_structure(self, scope: str) -> Dict[str, Any]:
        """Analyze project structure for test generation"""
        prompt = f"""
        Analyze the project structure for test generation:
        
        Scope: {scope}
        
        Please provide:
        1. Key functions and methods
        2. API endpoints and interfaces
        3. Data models and schemas
        4. Business logic components
        5. Integration points
        6. Error handling patterns
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a test engineer. Analyze project structure for test generation.",
            strategy="intelligent",
            max_tokens=2500
        )
        
        return {
            "project_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _generate_test_content(self, project_analysis: Dict[str, Any], mode: str, user_input: str) -> Dict[str, Any]:
        """Generate test content"""
        prompt = f"""
        Generate comprehensive tests based on the project analysis:
        
        Project Analysis: {project_analysis.get('project_analysis', '')}
        Mode: {mode}
        User Input: {user_input}
        
        Please provide:
        1. Unit tests
        2. Integration tests
        3. End-to-end tests
        4. Performance tests
        5. Security tests
        6. Test utilities and fixtures
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a test engineer. Generate comprehensive test suites.",
            strategy="intelligent",
            max_tokens=4000
        )
        
        return {
            "tests": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _create_implementation_plan(self, tests: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Create implementation plan for tests"""
        prompt = f"""
        Create an implementation plan for tests:
        
        Tests: {tests.get('tests', '')}
        Mode: {mode}
        
        Please provide:
        1. Test organization
        2. File structure
        3. Naming conventions
        4. Test execution strategy
        5. CI/CD integration
        6. Quality metrics
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a project manager. Create detailed implementation plans.",
            strategy="intelligent",
            max_tokens=2000
        )
        
        return {
            "implementation_plan": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Test Generator')
    parser.add_argument('--mode', required=True, help='Generation mode')
    parser.add_argument('--scope', required=True, help='Target scope')
    parser.add_argument('--user-input', default='', help='User input')
    parser.add_argument('--output', default='tests/generated/', help='Output directory')
    
    args = parser.parse_args()
    
    generator = AITestGenerator()
    
    try:
        result = await generator.generate_tests(
            mode=args.mode,
            scope=args.scope,
            user_input=args.user_input
        )
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save results
        with open(output_dir / 'tests.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Test generation completed! Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print("🧪 TEST GENERATION SUMMARY")
        print("="*80)
        print(f"Mode: {result['mode']}")
        print(f"Scope: {result['scope']}")
        print(f"User Input: {result['user_input']}")
        print(f"Timestamp: {result['timestamp']}")
        print("\nAI Stats:")
        for key, value in result['ai_stats'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Test generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())