#!/usr/bin/env python3
"""
AI Comprehensive Analyzer - Advanced project analysis using multiple AI providers
Part of the AI-Powered Project Upgrade System

Security-enhanced version with comprehensive input validation,
error handling, and AMAS integration.
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from standalone_universal_ai_manager import get_manager
from ai_security_utils import (
    AISecurityValidator, AILogger, AIConfigManager,
    validate_ai_response, sanitize_prompt
)


class AIComprehensiveAnalyzer:
    """
    Advanced project analyzer using multiple AI providers
    
    Security-enhanced version with comprehensive input validation,
    error handling, and AMAS integration.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize the AI comprehensive analyzer with security validation"""
        self.manager = get_manager()
        self.analysis_results = {}
        self.config = AIConfigManager(config_file)
        self.validator = AISecurityValidator()
        self.logger = AILogger(__name__)
        
        # Configuration from config manager
        self.max_files = self.config.get_max_files()
        self.max_file_size = self.config.get_max_file_size()
        self.allowed_extensions = set(self.config.get_allowed_extensions())
        
        self.logger.info("AI Comprehensive Analyzer initialized with security validation")
        self.project_context = {}
        
    async def analyze_project_structure(self) -> Dict[str, Any]:
        """
        Analyze project structure and architecture with security validation
        
        Returns:
            Dict containing analysis results and metadata
            
        Raises:
            RuntimeError: If analysis fails
        """
        try:
            self.logger.info("🔍 Analyzing project structure...")
            
            # Get safe project files
            project_files = self._get_safe_project_files()
            
            if not project_files:
                self.logger.warning("No safe project files found for analysis")
                return {
                    "structure_analysis": "No safe project files found for analysis",
                    "provider_used": "none",
                    "response_time": 0,
                    "warnings": ["No safe project files found"]
                }
            
            # Create secure analysis prompt
            prompt = self._create_secure_analysis_prompt("structure", project_files)
            
            # Generate analysis with retry logic
            result = await self._generate_analysis_with_retry(prompt, "project structure")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Project structure analysis failed: {e}")
            raise RuntimeError(f"Project structure analysis failed: {e}")
    
    def _get_safe_project_files(self) -> List[str]:
        """Get safe project files with security validation"""
        try:
            safe_files = self.validator.get_safe_file_list("all", self.max_files)
            return [str(f.relative_to(self.validator.project_root)) for f in safe_files]
        except Exception as e:
            self.logger.error(f"Failed to get safe project files: {e}")
            return []
    
    def _create_secure_analysis_prompt(self, analysis_type: str, files: List[str]) -> str:
        """Create secure analysis prompt with sanitized inputs"""
        files_content = "\n".join(files[:50])  # Limit to 50 files
        
        prompt = f"""
        Analyze the project {analysis_type}:
        
        Project Files:
        {files_content}
        
        Please provide:
        1. Project architecture overview
        2. Technology stack analysis
        3. Code organization assessment
        4. Potential improvements
        5. Best practices recommendations
        """
        
        return sanitize_prompt(prompt)
    
    async def _generate_analysis_with_retry(self, prompt: str, analysis_type: str, max_retries: int = 3) -> Dict[str, Any]:
        """Generate analysis with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                result = await self.manager.generate(
                    prompt=prompt,
                    system_prompt=f"You are a senior software architect. Analyze {analysis_type} and provide comprehensive insights.",
                    strategy="intelligent",
                    max_tokens=4000
                )
                
                # Validate response
                if validate_ai_response(result, ['content', 'provider_name', 'response_time']):
                    return {
                        "structure_analysis": result.get("content", ""),
                        "provider_used": result.get("provider_name", ""),
                        "response_time": result.get("response_time", 0),
                        "attempt": attempt + 1
                    }
                else:
                    self.logger.warning(f"Invalid AI response for {analysis_type}, attempt {attempt + 1}")
                    
            except Exception as e:
                self.logger.error(f"AI analysis failed for {analysis_type}, attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All attempts failed for {analysis_type}")
                    return {
                        "structure_analysis": f"Analysis failed for {analysis_type}",
                        "provider_used": "none",
                        "response_time": 0,
                        "error": str(e)
                    }
        
        return {
            "structure_analysis": f"Analysis failed for {analysis_type} after {max_retries} attempts",
            "provider_used": "none",
            "response_time": 0
        }
    
    async def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality and best practices"""
        print("📊 Analyzing code quality...")
        
        # Get code files
        code_files = self._get_code_files()
        
        prompt = f"""
        Analyze the code quality of this project:
        
        Code Files: {code_files}
        
        Please provide:
        1. Code quality score (1-10)
        2. Best practices compliance
        3. Code smells and issues
        4. Refactoring suggestions
        5. Performance bottlenecks
        6. Security vulnerabilities
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a senior code reviewer and quality assurance expert. Provide detailed code quality analysis.",
            strategy="intelligent",
            max_tokens=3000
        )
        
        return {
            "quality_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies and security"""
        print("📦 Analyzing dependencies...")
        
        # Get dependency files
        dependency_files = self._get_dependency_files()
        
        prompt = f"""
        Analyze the project dependencies:
        
        Dependency Files: {dependency_files}
        
        Please provide:
        1. Dependency health status
        2. Security vulnerabilities
        3. Outdated packages
        4. License compliance
        5. Performance impact
        6. Recommendations
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a security expert and dependency analyst. Provide comprehensive dependency analysis.",
            strategy="intelligent",
            max_tokens=2500
        )
        
        return {
            "dependency_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def analyze_user_requirements(self, user_message: str) -> Dict[str, Any]:
        """Analyze user requirements and provide recommendations"""
        print("💬 Analyzing user requirements...")
        
        prompt = f"""
        Analyze the user requirements and provide recommendations:
        
        User Message: {user_message}
        
        Please provide:
        1. Requirements understanding
        2. Feasibility assessment
        3. Implementation approach
        4. Potential challenges
        5. Alternative solutions
        6. Timeline estimation
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a project manager and technical consultant. Provide detailed requirements analysis and recommendations.",
            strategy="intelligent",
            max_tokens=3000
        )
        
        return {
            "requirements_analysis": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    async def generate_upgrade_recommendations(self, mode: str, scope: str) -> Dict[str, Any]:
        """Generate comprehensive upgrade recommendations"""
        print("🚀 Generating upgrade recommendations...")
        
        prompt = f"""
        Generate comprehensive upgrade recommendations for this project:
        
        Upgrade Mode: {mode}
        Target Scope: {scope}
        
        Please provide:
        1. Priority-based upgrade plan
        2. Implementation strategy
        3. Risk assessment
        4. Resource requirements
        5. Timeline and milestones
        6. Success metrics
        """
        
        result = await self.manager.generate(
            prompt=prompt,
            system_prompt="You are a senior technical architect and project manager. Provide comprehensive upgrade recommendations.",
            strategy="intelligent",
            max_tokens=4000
        )
        
        return {
            "upgrade_recommendations": result.get("content", ""),
            "provider_used": result.get("provider_name", ""),
            "response_time": result.get("response_time", 0)
        }
    
    def _get_project_files(self) -> List[str]:
        """Get list of project files"""
        project_root = Path(__file__).parent.parent.parent
        files = []
        
        for ext in ['.py', '.js', '.ts', '.yaml', '.yml', '.json', '.md']:
            files.extend(list(project_root.rglob(f'*{ext}')))
        
        return [str(f.relative_to(project_root)) for f in files[:50]]  # Limit to 50 files
    
    def _get_code_files(self) -> List[str]:
        """Get list of code files"""
        project_root = Path(__file__).parent.parent.parent
        files = []
        
        for ext in ['.py', '.js', '.ts']:
            files.extend(list(project_root.rglob(f'*{ext}')))
        
        return [str(f.relative_to(project_root)) for f in files[:30]]  # Limit to 30 files
    
    def _get_dependency_files(self) -> List[str]:
        """Get list of dependency files"""
        project_root = Path(__file__).parent.parent.parent
        files = []
        
        for filename in ['requirements.txt', 'package.json', 'pyproject.toml', 'setup.py', 'Pipfile']:
            file_path = project_root / filename
            if file_path.exists():
                files.append(str(file_path.relative_to(project_root)))
        
        return files
    
    async def run_comprehensive_analysis(self, mode: str, scope: str, user_message: str, priority: str) -> Dict[str, Any]:
        """Run comprehensive project analysis"""
        print("🧠 Starting comprehensive project analysis...")
        print(f"📊 Mode: {mode}")
        print(f"🎯 Scope: {scope}")
        print(f"💬 User Message: {user_message}")
        print(f"⚡ Priority: {priority}")
        print()
        
        # Run all analysis tasks
        tasks = [
            self.analyze_project_structure(),
            self.analyze_code_quality(),
            self.analyze_dependencies(),
        ]
        
        if user_message:
            tasks.append(self.analyze_user_requirements(user_message))
        
        tasks.append(self.generate_upgrade_recommendations(mode, scope))
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "scope": scope,
            "user_message": user_message,
            "priority": priority,
            "structure_analysis": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "quality_analysis": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "dependency_analysis": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "requirements_analysis": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else None,
            "upgrade_recommendations": results[-1] if not isinstance(results[-1], Exception) else {"error": str(results[-1])},
            "ai_stats": self.manager.get_stats(),
            "provider_health": self.manager.get_provider_health()
        }
        
        return analysis_results


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Comprehensive Analyzer')
    parser.add_argument('--mode', default='comprehensive', help='Analysis mode')
    parser.add_argument('--scope', default='all', help='Target scope')
    parser.add_argument('--user-message', default='', help='User message')
    parser.add_argument('--priority', default='normal', help='Priority level')
    parser.add_argument('--output', default='analysis_results.json', help='Output file')
    
    args = parser.parse_args()
    
    analyzer = AIComprehensiveAnalyzer()
    
    try:
        results = await analyzer.run_comprehensive_analysis(
            mode=args.mode,
            scope=args.scope,
            user_message=args.user_message,
            priority=args.priority
        )
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Analysis complete! Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*80)
        print("📊 ANALYSIS SUMMARY")
        print("="*80)
        print(f"Mode: {results['mode']}")
        print(f"Scope: {results['scope']}")
        print(f"User Message: {results['user_message']}")
        print(f"Priority: {results['priority']}")
        print(f"Timestamp: {results['timestamp']}")
        print("\nAI Stats:")
        for key, value in results['ai_stats'].items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())