#!/usr/bin/env python3
"""
AI Fallback Integration - Integrate fallback system with all AI scripts
"""

import os
import sys
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from ai_fallback_manager import generate_ai_response, get_fallback_stats, reset_fallback_order

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIFallbackIntegration:
    """Integrate fallback system with all AI scripts"""
    
    def __init__(self):
        self.fallback_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'script_usage': {},
            'provider_performance': {}
        }
    
    async def analyze_code_with_fallback(self, code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze code with intelligent fallback"""
        prompt = f"""
        Analyze the following code for {analysis_type} analysis:
        
        Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Code quality assessment
        2. Potential issues and improvements
        3. Performance recommendations
        4. Security considerations
        5. Best practices suggestions
        
        Format the response as a structured analysis report.
        """
        
        result = await generate_ai_response(prompt, max_tokens=3000)
        self._update_stats('code_analysis', result)
        return result
    
    async def improve_code_with_fallback(self, code: str, improvement_type: str = "performance") -> Dict[str, Any]:
        """Improve code with intelligent fallback"""
        prompt = f"""
        Improve the following code for {improvement_type} optimization:
        
        Original Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Improved version of the code
        2. Explanation of improvements made
        3. Performance benefits
        4. Best practices applied
        5. Additional recommendations
        
        Format the response with the improved code and detailed explanations.
        """
        
        result = await generate_ai_response(prompt, max_tokens=4000)
        self._update_stats('code_improvement', result)
        return result
    
    async def generate_tests_with_fallback(self, code: str, test_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate tests with intelligent fallback"""
        prompt = f"""
        Generate {test_type} tests for the following code:
        
        Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Unit tests with pytest
        2. Integration tests
        3. Edge case tests
        4. Performance tests
        5. Test documentation
        
        Format the response with complete test code and explanations.
        """
        
        result = await generate_ai_response(prompt, max_tokens=4000)
        self._update_stats('test_generation', result)
        return result
    
    async def generate_documentation_with_fallback(self, code: str, doc_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate documentation with intelligent fallback"""
        prompt = f"""
        Generate {doc_type} documentation for the following code:
        
        Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Function/class documentation
        2. API documentation
        3. Usage examples
        4. Installation instructions
        5. Configuration guide
        
        Format the response as structured documentation.
        """
        
        result = await generate_ai_response(prompt, max_tokens=3000)
        self._update_stats('documentation_generation', result)
        return result
    
    async def audit_security_with_fallback(self, code: str, audit_type: str = "comprehensive") -> Dict[str, Any]:
        """Audit security with intelligent fallback"""
        prompt = f"""
        Perform {audit_type} security audit on the following code:
        
        Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Security vulnerabilities found
        2. Risk assessment
        3. Remediation recommendations
        4. Security best practices
        5. Compliance considerations
        
        Format the response as a security audit report.
        """
        
        result = await generate_ai_response(prompt, max_tokens=3000)
        self._update_stats('security_audit', result)
        return result
    
    async def analyze_performance_with_fallback(self, code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze performance with intelligent fallback"""
        prompt = f"""
        Perform {analysis_type} performance analysis on the following code:
        
        Code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Performance bottlenecks
        2. Optimization opportunities
        3. Memory usage analysis
        4. Time complexity analysis
        5. Performance recommendations
        
        Format the response as a performance analysis report.
        """
        
        result = await generate_ai_response(prompt, max_tokens=3000)
        self._update_stats('performance_analysis', result)
        return result
    
    async def respond_to_issue_with_fallback(self, issue_title: str, issue_body: str, action: str = "opened") -> Dict[str, Any]:
        """Respond to GitHub issue with intelligent fallback"""
        prompt = f"""
        Respond to this GitHub issue as an AI assistant:
        
        Title: {issue_title}
        Body: {issue_body}
        Action: {action}
        
        Please provide:
        1. Acknowledgment of the issue
        2. Initial analysis or suggestions
        3. Next steps or recommendations
        4. Helpful resources or links
        5. Professional and helpful tone
        
        Format the response as a GitHub issue comment.
        """
        
        result = await generate_ai_response(prompt, max_tokens=2000)
        self._update_stats('issue_response', result)
        return result
    
    async def continuous_development_with_fallback(self, project_path: str, mode: str = "full_analysis") -> Dict[str, Any]:
        """Continuous development with intelligent fallback"""
        prompt = f"""
        Perform {mode} continuous development analysis for the project at {project_path}:
        
        Please provide:
        1. Project structure analysis
        2. Code quality assessment
        3. Improvement recommendations
        4. Best practices suggestions
        5. Future development roadmap
        
        Format the response as a comprehensive development report.
        """
        
        result = await generate_ai_response(prompt, max_tokens=4000)
        self._update_stats('continuous_development', result)
        return result
    
    def _update_stats(self, script_type: str, result: Dict[str, Any]):
        """Update fallback statistics"""
        self.fallback_stats['total_requests'] += 1
        
        if result['success']:
            self.fallback_stats['successful_requests'] += 1
            provider = result['provider']
            if provider not in self.fallback_stats['provider_performance']:
                self.fallback_stats['provider_performance'][provider] = 0
            self.fallback_stats['provider_performance'][provider] += 1
        else:
            self.fallback_stats['failed_requests'] += 1
        
        if script_type not in self.fallback_stats['script_usage']:
            self.fallback_stats['script_usage'][script_type] = 0
        self.fallback_stats['script_usage'][script_type] += 1
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        total = self.fallback_stats['total_requests']
        success_rate = (self.fallback_stats['successful_requests'] / total * 100) if total > 0 else 0
        
        return {
            'integration_stats': self.fallback_stats,
            'fallback_stats': get_fallback_stats(),
            'success_rate': f"{success_rate:.1f}%",
            'total_requests': total,
            'successful_requests': self.fallback_stats['successful_requests'],
            'failed_requests': self.fallback_stats['failed_requests']
        }

# Global integration instance
fallback_integration = AIFallbackIntegration()

# Convenience functions for all AI scripts
async def analyze_code(code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Analyze code with fallback"""
    return await fallback_integration.analyze_code_with_fallback(code, analysis_type)

async def improve_code(code: str, improvement_type: str = "performance") -> Dict[str, Any]:
    """Improve code with fallback"""
    return await fallback_integration.improve_code_with_fallback(code, improvement_type)

async def generate_tests(code: str, test_type: str = "comprehensive") -> Dict[str, Any]:
    """Generate tests with fallback"""
    return await fallback_integration.generate_tests_with_fallback(code, test_type)

async def generate_documentation(code: str, doc_type: str = "comprehensive") -> Dict[str, Any]:
    """Generate documentation with fallback"""
    return await fallback_integration.generate_documentation_with_fallback(code, doc_type)

async def audit_security(code: str, audit_type: str = "comprehensive") -> Dict[str, Any]:
    """Audit security with fallback"""
    return await fallback_integration.audit_security_with_fallback(code, audit_type)

async def analyze_performance(code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Analyze performance with fallback"""
    return await fallback_integration.analyze_performance_with_fallback(code, analysis_type)

async def respond_to_issue(issue_title: str, issue_body: str, action: str = "opened") -> Dict[str, Any]:
    """Respond to issue with fallback"""
    return await fallback_integration.respond_to_issue_with_fallback(issue_title, issue_body, action)

async def continuous_development(project_path: str, mode: str = "full_analysis") -> Dict[str, Any]:
    """Continuous development with fallback"""
    return await fallback_integration.continuous_development_with_fallback(project_path, mode)

def get_integration_stats() -> Dict[str, Any]:
    """Get integration statistics"""
    return fallback_integration.get_integration_stats()

# Test function
async def test_fallback_integration():
    """Test the fallback integration"""
    print("🧪 Testing AI Fallback Integration...")
    print("="*60)
    
    # Test code
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    # Test all functions
    tests = [
        ("Code Analysis", lambda: analyze_code(test_code)),
        ("Code Improvement", lambda: improve_code(test_code)),
        ("Test Generation", lambda: generate_tests(test_code)),
        ("Documentation", lambda: generate_documentation(test_code)),
        ("Security Audit", lambda: audit_security(test_code)),
        ("Performance Analysis", lambda: analyze_performance(test_code))
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            if result['success']:
                print(f"✅ {test_name} successful with {result['provider']}")
            else:
                print(f"❌ {test_name} failed: {result['error']}")
        except Exception as e:
            print(f"❌ {test_name} exception: {e}")
    
    # Show stats
    stats = get_integration_stats()
    print(f"\n📊 Integration Statistics:")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Success Rate: {stats['success_rate']}")
    print(f"Successful Requests: {stats['successful_requests']}")
    print(f"Failed Requests: {stats['failed_requests']}")

if __name__ == "__main__":
    asyncio.run(test_fallback_integration())