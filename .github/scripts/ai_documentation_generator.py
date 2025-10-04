#!/usr/bin/env python3
"""
AI Documentation Generator - Advanced documentation generation using AI
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


class AIDocumentationGenerator:
    """Advanced documentation generator using AI"""
    
    def __init__(self):
        self.manager = get_manager()
        self.documentation = {}
        
    async def generate_documentation(self, mode: str, scope: str, user_input: str) -> Dict[str, Any]:
        """Generate documentation based on mode and scope"""
        print(f"📝 Generating documentation...")
        print(f"Mode: {mode}")
        print(f"Scope: {scope}")
        print(f"User Input: {user_input}")
        
        # Analyze project structure
        project_analysis = await self._analyze_project_structure(scope)
        
        # Generate documentation
        documentation = await self._generate_documentation_content(project_analysis, mode, user_input)
        
        # Create implementation plan
        implementation_plan = await self._create_implementation_plan(documentation, mode)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "scope": scope,
            "user_input": user_input,
            "project_analysis": project_analysis,
            "documentation": documentation,
            "implementation_plan": implementation_plan,
            "ai_stats": self.manager.get_stats()
        }
    
    async def _analyze_project_structure(self, scope: str) -> Dict[str, Any]:
        """Analyze project structure for documentation"""
        prompt = f"""
        Analyze the project structure for documentation generation:
        
        Scope: {scope}
        
        Please provide:
        1. Project architecture overview
        2. Key components and modules
        3. API endpoints and interfaces
        4. Data models and schemas
        5. Configuration options
        6. Usage patterns and examples
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a technical writer. Analyze project structure for documentation.",
            strategy="intelligent",
            max_tokens=2500
        )
        
        return {
            "project_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _generate_documentation_content(self, project_analysis: Dict[str, Any], mode: str, user_input: str) -> Dict[str, Any]:
        """Generate documentation content"""
        prompt = f"""
        Generate comprehensive documentation based on the project analysis:
        
        Project Analysis: {project_analysis.get('project_analysis', '')}
        Mode: {mode}
        User Input: {user_input}
        
        Please provide:
        1. API documentation
        2. User guides
        3. Developer documentation
        4. Code examples
        5. Configuration guides
        6. Troubleshooting sections
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a technical writer. Generate comprehensive documentation.",
            strategy="intelligent",
            max_tokens=4000
        )
        
        return {
            "documentation": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def _create_implementation_plan(self, documentation: Dict[str, Any], mode: str) -> Dict[str, Any]:
        """Create implementation plan for documentation"""
        prompt = f"""
        Create an implementation plan for documentation:
        
        Documentation: {documentation.get('documentation', '')}
        Mode: {mode}
        
        Please provide:
        1. Documentation structure
        2. File organization
        3. Formatting standards
        4. Review process
        5. Maintenance schedule
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
    parser = argparse.ArgumentParser(description='AI Documentation Generator')
    parser.add_argument('--mode', required=True, help='Generation mode')
    parser.add_argument('--scope', required=True, help='Target scope')
    parser.add_argument('--user-input', default='', help='User input')
    parser.add_argument('--output', default='docs/generated/', help='Output directory')
    
    args = parser.parse_args()
    
    generator = AIDocumentationGenerator()
    
    try:
        result = await generator.generate_documentation(
            mode=args.mode,
            scope=args.scope,
            user_input=args.user_input
        )
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save results
        with open(output_dir / 'documentation.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Documentation generation completed! Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print("📝 DOCUMENTATION GENERATION SUMMARY")
        print("="*80)
        print(f"Mode: {result['mode']}")
        print(f"Scope: {result['scope']}")
        print(f"User Input: {result['user_input']}")
        print(f"Timestamp: {result['timestamp']}")
        print("\nAI Stats:")
        for key, value in result['ai_stats'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Documentation generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())