#!/usr/bin/env python3
"""
AI Code Improver - Advanced code improvement using multiple AI providers
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


class AICodeImprover:
    """Advanced code improver using multiple AI providers"""
    
    def __init__(self):
        self.manager = get_manager()
        self.improvements = {}
        
    async def improve_code(self, mode: str, scope: str, user_input: str) -> Dict[str, Any]:
        """Improve code based on mode and scope"""
        print(f"🔧 Improving code...")
        print(f"Mode: {mode}")
        print(f"Scope: {scope}")
        print(f"User Input: {user_input}")
        
        # Get code files to improve
        code_files = self._get_code_files(scope)
        
        # Run improvements
        improvements = await self._run_improvements(code_files, mode, user_input)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "scope": scope,
            "user_input": user_input,
            "code_files": code_files,
            "improvements": improvements,
            "ai_stats": self.manager.get_stats()
        }
    
    def _get_code_files(self, scope: str) -> List[str]:
        """Get code files based on scope"""
        project_root = Path(__file__).parent.parent.parent
        
        if scope == "all":
            # Get all code files
            files = []
            for ext in ['.py', '.js', '.ts']:
                files.extend(list(project_root.rglob(f'*{ext}')))
            return [str(f.relative_to(project_root)) for f in files[:20]]
        elif scope == "changed_files":
            # Get changed files (would need git integration)
            return ["main.py", "requirements.txt"]  # Placeholder
        else:
            # Specific directory
            target_dir = project_root / scope
            if target_dir.exists():
                files = []
                for ext in ['.py', '.js', '.ts']:
                    files.extend(list(target_dir.rglob(f'*{ext}')))
                return [str(f.relative_to(project_root)) for f in files[:20]]
            return []
    
    async def _run_improvements(self, code_files: List[str], mode: str, user_input: str) -> Dict[str, Any]:
        """Run code improvements"""
        improvements = {}
        
        for file_path in code_files[:5]:  # Limit to 5 files for demo
            print(f"🔧 Improving {file_path}...")
            
            # Read file content
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
            except Exception as e:
                print(f"❌ Could not read {file_path}: {e}")
                continue
            
            # Generate improvements
            improvement = await self._generate_improvements(file_path, content, mode, user_input)
            improvements[file_path] = improvement
        
        return improvements
    
    async def _generate_improvements(self, file_path: str, content: str, mode: str, user_input: str) -> Dict[str, Any]:
        """Generate improvements for a specific file"""
        prompt = f"""
        Improve this code file based on the requirements:
        
        File: {file_path}
        Mode: {mode}
        User Input: {user_input}
        
        Code Content:
        {content[:2000]}...
        
        Please provide:
        1. Code quality improvements
        2. Performance optimizations
        3. Security enhancements
        4. Best practices implementation
        5. Refactoring suggestions
        6. Improved code version
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a senior software engineer and code reviewer. Provide comprehensive code improvements.",
            strategy="intelligent",
            max_tokens=4000
        )
        
        return {
            "improvements": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Code Improver')
    parser.add_argument('--mode', required=True, help='Improvement mode')
    parser.add_argument('--scope', required=True, help='Target scope')
    parser.add_argument('--user-input', default='', help='User input')
    parser.add_argument('--output', default='improved_code/', help='Output directory')
    
    args = parser.parse_args()
    
    improver = AICodeImprover()
    
    try:
        result = await improver.improve_code(
            mode=args.mode,
            scope=args.scope,
            user_input=args.user_input
        )
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save results
        with open(output_dir / 'improvements.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Code improvements completed! Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print("🔧 CODE IMPROVEMENT SUMMARY")
        print("="*80)
        print(f"Mode: {result['mode']}")
        print(f"Scope: {result['scope']}")
        print(f"User Input: {result['user_input']}")
        print(f"Files Processed: {len(result['code_files'])}")
        print(f"Improvements: {len(result['improvements'])}")
        print(f"Timestamp: {result['timestamp']}")
        print("\nAI Stats:")
        for key, value in result['ai_stats'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Code improvement failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())