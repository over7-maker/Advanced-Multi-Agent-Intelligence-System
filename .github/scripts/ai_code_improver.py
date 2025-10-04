#!/usr/bin/env python3
"""
AI Code Improver - Advanced code improvement using multiple AI providers
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


class AICodeImprover:
    """
    Advanced code improver using multiple AI providers
    
    Security-enhanced version with comprehensive input validation,
    error handling, and AMAS integration.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize the AI code improver with security validation"""
        self.manager = get_manager()
        self.improvements = {}
        self.config = AIConfigManager(config_file)
        self.validator = AISecurityValidator()
        self.logger = AILogger(__name__)
        
        # Configuration from config manager
        self.max_files = self.config.get_max_files()
        self.max_file_size = self.config.get_max_file_size()
        self.allowed_extensions = set(self.config.get_allowed_extensions())
        
        self.logger.info("AI Code Improver initialized with security validation")
        
    async def improve_code(self, mode: str, scope: str, user_input: str) -> Dict[str, Any]:
        """
        Improve code based on mode and scope with comprehensive security validation
        
        Args:
            mode: Improvement mode (comprehensive, security_focused, performance_focused)
            scope: Target scope (all, changed_files, specific_directory)
            user_input: User input for customization
            
        Returns:
            Dict containing improvement results and metadata
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If improvement process fails
        """
        try:
            # Validate inputs
            self._validate_inputs(mode, scope, user_input)
            
            self.logger.info(f"🔧 Improving code - Mode: {mode}, Scope: {scope}")
            
            # Get safe code files to improve
            code_files = self._get_safe_code_files(scope)
            
            if not code_files:
                self.logger.warning("No safe code files found for improvement")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "mode": mode,
                    "scope": scope,
                    "user_input": user_input,
                    "code_files": [],
                    "improvements": {},
                    "ai_stats": self.manager.get_stats(),
                    "warnings": ["No safe code files found"]
                }
            
            # Run improvements with error handling
            improvements = await self._run_improvements_safely(code_files, mode, user_input)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "mode": mode,
                "scope": scope,
                "user_input": user_input,
                "code_files": [str(f) for f in code_files],
                "improvements": improvements,
                "ai_stats": self.manager.get_stats()
            }
            
        except Exception as e:
            self.logger.error(f"Code improvement failed: {e}")
            raise RuntimeError(f"Code improvement failed: {e}")
    
    def _validate_inputs(self, mode: str, scope: str, user_input: str) -> None:
        """Validate and sanitize inputs"""
        # Validate mode
        valid_modes = ['comprehensive', 'security_focused', 'performance_focused', 'documentation_focused']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: {valid_modes}")
        
        # Validate and sanitize scope
        scope = self.validator.validate_scope(scope)
        
        # Validate and sanitize user input
        user_input = self.validator.validate_input(user_input)
        
        self.logger.info(f"Input validation passed - Mode: {mode}, Scope: {scope}")
    
    def _get_safe_code_files(self, scope: str) -> List[Path]:
        """Get safe code files based on scope with security validation"""
        try:
            return self.validator.get_safe_file_list(scope, self.max_files)
        except Exception as e:
            self.logger.error(f"Failed to get safe code files: {e}")
            return []
    
    async def _run_improvements_safely(self, code_files: List[Path], mode: str, user_input: str) -> Dict[str, Any]:
        """Run code improvements with comprehensive error handling and security"""
        improvements = {}
        processed_count = 0
        error_count = 0
        
        for file_path in code_files:
            try:
                self.logger.info(f"🔧 Processing {file_path}...")
                
                # Validate file access
                if not self.validator.validate_file_access(file_path):
                    self.logger.warning(f"Skipping {file_path} - access validation failed")
                    continue
                
                # Read file content safely
                content = self._read_file_safely(file_path)
                if content is None:
                    continue
                
                # Generate improvements with retry logic
                improvement = await self._generate_improvements_with_retry(
                    file_path, content, mode, user_input
                )
                
                if improvement:
                    improvements[str(file_path)] = improvement
                    processed_count += 1
                else:
                    error_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                error_count += 1
                continue
        
        self.logger.info(f"Improvements completed - Processed: {processed_count}, Errors: {error_count}")
        return improvements
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Read file content safely with validation"""
        try:
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                self.logger.warning(f"File {file_path} too large, skipping")
                return None
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Sanitize content to remove sensitive information
            content = self.validator.sanitize_file_content(content, file_path)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read {file_path}: {e}")
            return None
    
    async def _generate_improvements_with_retry(self, file_path: Path, content: str, mode: str, user_input: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Generate improvements with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                # Sanitize inputs
                sanitized_user_input = sanitize_prompt(user_input)
                sanitized_content = content[:2000]  # Limit content size
                
                # Create secure prompt
                prompt = self._create_secure_prompt(file_path, sanitized_content, mode, sanitized_user_input)
                
                # Generate improvements
                result = await self.manager.generate(
                    prompt=prompt,
                    system_prompt="You are a senior software engineer and code reviewer. Provide comprehensive code improvements.",
                    strategy="intelligent",
                    max_tokens=4000
                )
                
                # Validate response
                if validate_ai_response(result, ['content', 'provider_name', 'response_time']):
                    return {
                        "improvements": result.get("content", ""),
                        "provider_used": result.get("provider_name", ""),
                        "response_time": result.get("response_time", 0),
                        "attempt": attempt + 1
                    }
                else:
                    self.logger.warning(f"Invalid AI response for {file_path}, attempt {attempt + 1}")
                    
            except Exception as e:
                self.logger.error(f"AI generation failed for {file_path}, attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All attempts failed for {file_path}")
                    return None
        
        return None
    
    def _create_secure_prompt(self, file_path: Path, content: str, mode: str, user_input: str) -> str:
        """Create a secure prompt with sanitized inputs"""
        prompt = f"""
        Improve this code file based on the requirements:
        
        File: {file_path.name}
        Mode: {mode}
        User Input: {user_input}
        
        Code Content:
        {content}
        
        Please provide:
        1. Code quality improvements
        2. Performance optimizations
        3. Security enhancements
        4. Best practices implementation
        5. Refactoring suggestions
        6. Improved code version
        """
        
        return sanitize_prompt(prompt)


async def main():
    """Main function with comprehensive error handling and security validation"""
    parser = argparse.ArgumentParser(
        description='AI Code Improver - Security-enhanced code improvement using multiple AI providers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ai_code_improver.py --mode comprehensive --scope all
  python ai_code_improver.py --mode security_focused --scope src --user-input "Focus on security"
  python ai_code_improver.py --mode performance_focused --scope tests --output /tmp/improvements
        """
    )
    
    parser.add_argument('--mode', required=True, 
                       choices=['comprehensive', 'security_focused', 'performance_focused', 'documentation_focused'],
                       help='Improvement mode')
    parser.add_argument('--scope', required=True, 
                       help='Target scope (all, changed_files, or specific directory)')
    parser.add_argument('--user-input', default='', 
                       help='User input for customization (max 10000 characters)')
    parser.add_argument('--output', default='improved_code/', 
                       help='Output directory for results')
    parser.add_argument('--config', 
                       help='Path to configuration file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = AILogger(__name__, log_level)
    
    try:
        # Initialize improver with security validation
        config_file = Path(args.config) if args.config else None
        improver = AICodeImprover(config_file)
        
        # Validate output directory
        output_dir = Path(args.output)
        if not improver.validator.validate_output_directory(output_dir):
            raise ValueError(f"Invalid output directory: {output_dir}")
        
        logger.info("Starting AI code improvement process")
        
        # Run improvements
        result = await improver.improve_code(
            mode=args.mode,
            scope=args.scope,
            user_input=args.user_input
        )
        
        # Save results with security validation
        output_file = output_dir / 'improvements.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Code improvements completed! Results saved to {output_dir}")
        
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
        
        if 'warnings' in result:
            print(f"Warnings: {', '.join(result['warnings'])}")
        
        print("\nAI Stats:")
        for key, value in result['ai_stats'].items():
            print(f"  {key}: {value}")
        
        print(f"\nResults saved to: {output_file}")
        
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        print(f"❌ Input validation failed: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(f"❌ Code improvement failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())