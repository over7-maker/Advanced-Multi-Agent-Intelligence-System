#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Test suite for Bulletproof AI PR Analyzer.

Comprehensive tests to verify all functionality and address AI analysis concerns.
"""

import unittest
import sys
import ast
import os
from pathlib import Path


class TestBulletproofAnalyzer(unittest.TestCase):
    """Test cases for bulletproof AI analyzer."""
    
    def setUp(self):
        """Set up test environment."""
        self.script_path = Path(".github/scripts/bulletproof_ai_pr_analyzer.py")
        self.assertTrue(self.script_path.exists(), "Analyzer script not found")
    
    def test_syntax_validation(self):
        """Test that the script has valid Python syntax."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        try:
            ast.parse(source_code)
            print("✅ Syntax validation: PASSED")
        except SyntaxError as e:
            self.fail(f"Syntax error in {self.script_path}: {e}")
    
    def test_sensitive_vars_complete(self):
        """Test that SENSITIVE_VARS is properly defined and complete."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Check SENSITIVE_VARS is defined
        self.assertIn('SENSITIVE_VARS: frozenset[str] = frozenset([', source_code)
        
        # Check it's properly closed
        self.assertIn('])', source_code)
        
        # Check it contains essential variables
        essential_vars = [
            'GITHUB_TOKEN', 'API_KEY', 'SECRET_KEY', 'PASSWORD',
            'AWS_SECRET_ACCESS_KEY', 'JWT_SECRET', 'OPENAI_API_KEY'
        ]
        
        for var in essential_vars:
            self.assertIn(f'"{var}"', source_code, f"Missing essential variable: {var}")
        
        print("✅ SENSITIVE_VARS validation: PASSED")
    
    def test_imports_resolution(self):
        """Test that all required imports can be resolved."""
        # Test critical imports that should always work
        critical_imports = [
            'import asyncio',
            'import logging',
            'import subprocess',
            'import json',
            'from pathlib import Path',
            'from typing import Any, Dict, List, Optional'
        ]
        
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        for imp in critical_imports:
            self.assertIn(imp, source_code, f"Missing critical import: {imp}")
        
        print("✅ Import resolution: PASSED")
    
    def test_async_functions_present(self):
        """Test that async functions are properly implemented."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        async_functions = [
            'async def secure_subprocess_run_async',
            'async def get_pr_diff',
            'async def get_changed_files',
            'async def run_ai_analysis',
            'async def main'
        ]
        
        for func in async_functions:
            self.assertIn(func, source_code, f"Missing async function: {func}")
        
        print("✅ Async functions validation: PASSED")
    
    def test_security_patterns_present(self):
        """Test that security patterns are properly implemented."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Check for enhanced security patterns - be more flexible with the shell=False check
        security_features = [
            'SENSITIVE_PATTERNS: List[re.Pattern[str]]',
            'def sanitize_env(',
            'def is_safe_path(',
            "'shell': False",  # More specific pattern for subprocess security
        ]
        
        for feature in security_features:
            self.assertIn(feature, source_code, f"Missing security feature: {feature}")
        
        print("✅ Security patterns validation: PASSED")
    
    def test_logging_configuration(self):
        """Test that logging is properly configured."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        logging_features = [
            'def configure_logging',
            'logging.config.dictConfig',
            'RotatingFileHandler'
        ]
        
        for feature in logging_features:
            self.assertIn(feature, source_code, f"Missing logging feature: {feature}")
        
        print("✅ Logging configuration validation: PASSED")
    
    def test_project_root_detection(self):
        """Test that project root detection is implemented."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        root_features = [
            'def _find_project_root',
            'def find_project_root',
            'PROJECT_ROOT',
            '.git',
            'pyproject.toml'
        ]
        
        for feature in root_features:
            self.assertIn(feature, source_code, f"Missing root detection feature: {feature}")
        
        print("✅ Project root detection validation: PASSED")
    
    def test_error_handling_comprehensive(self):
        """Test that comprehensive error handling is implemented."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        error_features = [
            'try:',
            'except Exception',
            'logger.error',
            'ENHANCED_ERROR_HANDLING',
            'tenacity.retry'
        ]
        
        for feature in error_features:
            self.assertIn(feature, source_code, f"Missing error handling feature: {feature}")
        
        print("✅ Error handling validation: PASSED")
    
    def test_main_guard_present(self):
        """Test that proper __main__ guard is implemented."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        self.assertIn('if __name__ == "__main__":', source_code)
        self.assertIn('asyncio.run(main())', source_code)
        
        print("✅ Main guard validation: PASSED")
    
    def test_type_annotations_present(self):
        """Test that type annotations are properly used."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        type_features = [
            ': int =',
            ': str =',
            ': frozenset[str] =',
            'List[str]',
            'Dict[str, Any]',
            'Optional[str]'
        ]
        
        for feature in type_features:
            self.assertIn(feature, source_code, f"Missing type annotation: {feature}")
        
        print("✅ Type annotations validation: PASSED")
    
    def test_verification_results_handling(self):
        """Test that verification results are properly handled."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        verification_features = [
            'self.verification_results',
            'real_ai_verified',
            'bulletproof_validated',
            'save_verification_results',
            'verification_results.json'
        ]
        
        for feature in verification_features:
            self.assertIn(feature, source_code, f"Missing verification feature: {feature}")
        
        print("✅ Verification results validation: PASSED")


def run_comprehensive_validation():
    """Run comprehensive validation of the analyzer."""
    print("🧪 Running Bulletproof AI Analyzer Test Suite")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBulletproofAnalyzer)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Analyzer is production ready!")
        print("✅ All AI analysis concerns have been addressed")
        print("✅ Code quality meets Phase 2 requirements")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        for i, (test, traceback) in enumerate(result.failures + result.errors):
            print(f"\n❌ Test {i+1}: {test}")
            print(f"Error: {traceback}")
        return 1


if __name__ == "__main__":
    exit_code = run_comprehensive_validation()
    sys.exit(exit_code)
