#!/usr/bin/env python3
"""
Comprehensive API Testing System
Tests all 6 AI APIs with detailed analysis and recommendations
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from ai_service_manager import AIServiceManager

def test_individual_apis() -> Dict[str, Any]:
    """Test each API individually with detailed analysis"""
    print("🧪 Testing Individual APIs")
    print("=" * 60)
    
    manager = AIServiceManager()
    results = {}
    
    # Test each provider individually
    for provider in manager.get_available_providers():
        print(f"\n🔍 Testing {provider.name}...")
        
        # Test basic functionality
        test_prompt = f"Hello! Please respond with 'API test successful' and confirm you are {provider.name}."
        response, error = manager._try_provider(provider, test_prompt)
        
        if response:
            print(f"✅ {provider.name}: Basic test passed")
            
            # Test specialized capabilities
            capabilities = test_provider_capabilities(provider, manager)
            results[provider.name] = {
                'status': 'success',
                'basic_test': True,
                'response': response[:100] + "..." if len(response) > 100 else response,
                'capabilities': capabilities,
                'provider_info': {
                    'model': provider.model,
                    'priority': provider.priority,
                    'max_tokens': provider.max_tokens
                }
            }
        else:
            print(f"❌ {provider.name}: Basic test failed - {error}")
            results[provider.name] = {
                'status': 'error',
                'basic_test': False,
                'error': error,
                'capabilities': {}
            }
    
    return results

def test_provider_capabilities(provider, manager) -> Dict[str, Any]:
    """Test specialized capabilities of a provider"""
    capabilities = {}
    
    # Test code analysis
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    try:
        analysis, error = manager._try_provider(provider, 
            f"Analyze this Python code for performance issues:\n\n```python\n{test_code}\n```",
            "You are a code analysis expert. Identify performance issues and suggest optimizations.")
        
        capabilities['code_analysis'] = {
            'success': analysis is not None,
            'response_length': len(analysis) if analysis else 0,
            'error': error
        }
    except Exception as e:
        capabilities['code_analysis'] = {'success': False, 'error': str(e)}
    
    # Test security analysis
    security_code = """
import os
password = "hardcoded_password_123"
user_input = input("Enter data: ")
query = f"SELECT * FROM users WHERE name = '{user_input}'"
"""
    
    try:
        security_analysis, error = manager._try_provider(provider,
            f"Analyze this code for security vulnerabilities:\n\n```python\n{security_code}\n```",
            "You are a security expert. Identify security vulnerabilities and suggest fixes.")
        
        capabilities['security_analysis'] = {
            'success': security_analysis is not None,
            'response_length': len(security_analysis) if security_analysis else 0,
            'error': error
        }
    except Exception as e:
        capabilities['security_analysis'] = {'success': False, 'error': str(e)}
    
    # Test issue response generation
    try:
        issue_response, error = manager._try_provider(provider,
            "Issue: App crashes when user clicks button\nDescription: The application crashes every time I click the submit button. This happens on both Windows and Mac.",
            "You are a helpful technical support assistant. Generate a professional response to this bug report.")
        
        capabilities['issue_response'] = {
            'success': issue_response is not None,
            'response_length': len(issue_response) if issue_response else 0,
            'error': error
        }
    except Exception as e:
        capabilities['issue_response'] = {'success': False, 'error': str(e)}
    
    return capabilities

def test_load_balancing() -> Dict[str, Any]:
    """Test load balancing and fallback mechanisms"""
    print("\n⚖️ Testing Load Balancing and Fallback")
    print("=" * 60)
    
    manager = AIServiceManager()
    results = {
        'round_robin': [],
        'fallback': [],
        'performance': {}
    }
    
    # Test round-robin selection
    print("🔄 Testing round-robin selection...")
    for i in range(10):
        provider = manager.get_next_provider()
        if provider:
            results['round_robin'].append(provider.name)
            print(f"  Request {i+1}: {provider.name}")
        else:
            print(f"  Request {i+1}: No provider available")
    
    # Test fallback mechanism
    print("\n🔄 Testing fallback mechanism...")
    test_prompt = "Generate a simple hello message."
    
    for i in range(5):
        response, provider, error = manager.generate_response(test_prompt, use_fallback=True)
        if response:
            results['fallback'].append({
                'attempt': i+1,
                'provider': provider,
                'success': True,
                'response_length': len(response)
            })
            print(f"  Attempt {i+1}: Success with {provider}")
        else:
            results['fallback'].append({
                'attempt': i+1,
                'provider': None,
                'success': False,
                'error': error
            })
            print(f"  Attempt {i+1}: Failed - {error}")
    
    # Test performance
    print("\n⚡ Testing performance...")
    performance_tests = []
    
    for provider in manager.get_available_providers():
        start_time = time.time()
        response, error = manager._try_provider(provider, "Say hello in one word.")
        end_time = time.time()
        
        performance_tests.append({
            'provider': provider.name,
            'response_time': end_time - start_time,
            'success': response is not None,
            'response_length': len(response) if response else 0
        })
        
        print(f"  {provider.name}: {end_time - start_time:.2f}s ({'Success' if response else 'Failed'})")
    
    results['performance'] = performance_tests
    return results

def test_error_handling() -> Dict[str, Any]:
    """Test error handling and recovery"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 60)
    
    manager = AIServiceManager()
    results = {
        'invalid_requests': [],
        'timeout_handling': [],
        'provider_disabling': []
    }
    
    # Test invalid requests
    print("❌ Testing invalid requests...")
    invalid_prompts = [
        "",  # Empty prompt
        "x" * 10000,  # Very long prompt
        "🚀" * 1000,  # Unicode heavy prompt
    ]
    
    for i, prompt in enumerate(invalid_prompts):
        response, provider, error = manager.generate_response(prompt)
        results['invalid_requests'].append({
            'test': f"Invalid prompt {i+1}",
            'success': response is not None,
            'error': error,
            'provider': provider
        })
        print(f"  Invalid prompt {i+1}: {'Success' if response else 'Failed'}")
    
    # Test provider disabling/enabling
    print("\n🔧 Testing provider management...")
    available_providers = manager.get_available_providers()
    if available_providers:
        test_provider = available_providers[0]
        
        # Disable provider
        manager.disable_provider(test_provider.name)
        disabled_providers = [p for p in manager.get_available_providers() if p.name == test_provider.name]
        results['provider_disabling'].append({
            'action': 'disable',
            'provider': test_provider.name,
            'success': len(disabled_providers) == 0
        })
        print(f"  Disabled {test_provider.name}: {len(disabled_providers) == 0}")
        
        # Re-enable provider
        manager.enable_provider(test_provider.name)
        enabled_providers = [p for p in manager.get_available_providers() if p.name == test_provider.name]
        results['provider_disabling'].append({
            'action': 'enable',
            'provider': test_provider.name,
            'success': len(enabled_providers) > 0
        })
        print(f"  Enabled {test_provider.name}: {len(enabled_providers) > 0}")
    
    return results

def generate_comprehensive_report(individual_results: Dict, load_balancing_results: Dict, error_handling_results: Dict) -> str:
    """Generate comprehensive test report"""
    report = ["# 🧪 Comprehensive API Test Report\n"]
    report.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    total_providers = len(individual_results)
    working_providers = sum(1 for result in individual_results.values() if result['status'] == 'success')
    
    report.append("## 📊 Executive Summary")
    report.append(f"- **Total APIs Tested**: {total_providers}")
    report.append(f"- **Working APIs**: {working_providers}")
    report.append(f"- **Success Rate**: {(working_providers/total_providers)*100:.1f}%")
    report.append("")
    
    # Individual API Results
    report.append("## 🔍 Individual API Analysis")
    for name, result in individual_results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        report.append(f"\n### {status_emoji} {name}")
        
        if result['status'] == 'success':
            report.append(f"- **Status**: Working")
            report.append(f"- **Model**: {result['provider_info']['model']}")
            report.append(f"- **Priority**: {result['provider_info']['priority']}")
            report.append(f"- **Max Tokens**: {result['provider_info']['max_tokens']}")
            
            # Capabilities
            capabilities = result['capabilities']
            report.append("\n**Capabilities:**")
            for cap_name, cap_result in capabilities.items():
                cap_status = "✅" if cap_result['success'] else "❌"
                report.append(f"  - {cap_status} {cap_name.replace('_', ' ').title()}")
                if cap_result['success']:
                    report.append(f"    - Response Length: {cap_result['response_length']} chars")
                else:
                    report.append(f"    - Error: {cap_result['error']}")
        else:
            report.append(f"- **Status**: Failed")
            report.append(f"- **Error**: {result['error']}")
    
    # Load Balancing Results
    report.append("\n## ⚖️ Load Balancing Analysis")
    round_robin = load_balancing_results['round_robin']
    if round_robin:
        from collections import Counter
        distribution = Counter(round_robin)
        report.append("**Round-Robin Distribution:**")
        for provider, count in distribution.items():
            percentage = (count / len(round_robin)) * 100
            report.append(f"- {provider}: {count} requests ({percentage:.1f}%)")
    
    # Performance Analysis
    performance = load_balancing_results['performance']
    if performance:
        report.append("\n**Performance Metrics:**")
        for test in performance:
            status = "✅" if test['success'] else "❌"
            report.append(f"- {status} {test['provider']}: {test['response_time']:.2f}s")
    
    # Error Handling Results
    report.append("\n## 🛡️ Error Handling Analysis")
    invalid_requests = error_handling_results['invalid_requests']
    if invalid_requests:
        report.append("**Invalid Request Handling:**")
        for test in invalid_requests:
            status = "✅" if test['success'] else "❌"
            report.append(f"- {status} {test['test']}: {test['error'] or 'Handled gracefully'}")
    
    # Recommendations
    report.append("\n## 💡 Recommendations")
    
    if working_providers > 0:
        working_list = [name for name, result in individual_results.items() if result['status'] == 'success']
        report.append("### ✅ Working APIs")
        for api in working_list:
            report.append(f"- **{api}**: Ready for production use")
        
        # Best practices
        report.append("\n### 🚀 Best Practices")
        report.append("1. **Load Balancing**: Use round-robin for even distribution")
        report.append("2. **Fallback Strategy**: Always enable fallback for reliability")
        report.append("3. **Monitoring**: Track success rates and response times")
        report.append("4. **Error Handling**: Implement graceful degradation")
        
        # Performance optimization
        if performance:
            fastest = min(performance, key=lambda x: x['response_time'])
            report.append(f"5. **Performance**: {fastest['provider']} is fastest ({fastest['response_time']:.2f}s)")
    else:
        report.append("### ❌ Critical Issues")
        report.append("1. **No Working APIs**: All API keys need to be verified")
        report.append("2. **Authentication**: Check API key validity and permissions")
        report.append("3. **Network**: Verify internet connectivity and firewall settings")
        report.append("4. **Configuration**: Ensure all environment variables are set correctly")
    
    # Next Steps
    report.append("\n## 🎯 Next Steps")
    if working_providers > 0:
        report.append("1. ✅ **Deploy Working APIs** in production workflows")
        report.append("2. 🔧 **Fix Failed APIs** using the recommendations above")
        report.append("3. 📊 **Monitor Performance** and adjust priorities")
        report.append("4. 🧪 **Run Regular Tests** to ensure reliability")
    else:
        report.append("1. 🔧 **Fix All API Keys** before deployment")
        report.append("2. 🧪 **Re-run Tests** after fixing keys")
        report.append("3. ✅ **Verify Configuration** in GitHub Secrets")
        report.append("4. 🚀 **Deploy Gradually** starting with working APIs")
    
    return "\n".join(report)

def main():
    """Main testing function"""
    print("🧪 Comprehensive API Testing System")
    print("=" * 60)
    print("Testing all 6 AI APIs with detailed analysis")
    print("=" * 60)
    
    # Run all tests
    print("\n🔍 Phase 1: Individual API Testing")
    individual_results = test_individual_apis()
    
    print("\n⚖️ Phase 2: Load Balancing Testing")
    load_balancing_results = test_load_balancing()
    
    print("\n🛡️ Phase 3: Error Handling Testing")
    error_handling_results = test_error_handling()
    
    # Generate comprehensive report
    print("\n📊 Generating Comprehensive Report...")
    report = generate_comprehensive_report(individual_results, load_balancing_results, error_handling_results)
    
    # Save report
    with open('comprehensive-api-test-report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Report saved to: comprehensive-api-test-report.md")
    
    # Summary
    working_count = sum(1 for result in individual_results.values() if result['status'] == 'success')
    total_count = len(individual_results)
    
    print(f"\n🎯 FINAL SUMMARY: {working_count}/{total_count} APIs working")
    
    if working_count > 0:
        working_apis = [name for name, result in individual_results.items() if result['status'] == 'success']
        print(f"✅ Working APIs: {', '.join(working_apis)}")
        print("🎉 Your multi-API system is ready for deployment!")
    else:
        print("⚠️ No APIs are working. Please check your API keys and configuration.")
    
    return working_count > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test system failed: {e}")
        sys.exit(1)