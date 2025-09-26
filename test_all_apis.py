#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all AI API keys for authentication and functionality
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

def test_deepseek_api() -> Dict[str, Any]:
    """Test DeepSeek API authentication and functionality"""
    print("🔑 Testing DeepSeek API...")
    
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    if not deepseek_key:
        return {
            'status': 'error',
            'message': 'DEEPSEEK_API_KEY not found in environment',
            'fix': 'Set DEEPSEEK_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test DeepSeek API models endpoint
    url = "https://api.deepseek.com/v1/models"
    headers = {
        'Authorization': f'Bearer {deepseek_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            available_models = [model.get('id', 'unknown') for model in models_data.get('data', [])[:5]]
            
            return {
                'status': 'success',
                'message': f'DeepSeek API is valid. Found {model_count} available models.',
                'models': available_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'DeepSeek API key is invalid or expired',
                'fix': 'Generate a new DeepSeek API key at https://deepseek.com'
            }
        else:
            return {
                'status': 'error',
                'message': f'DeepSeek API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'DeepSeek API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_glm_api() -> Dict[str, Any]:
    """Test GLM API authentication and functionality"""
    print("🔑 Testing GLM API...")
    
    glm_key = os.environ.get('GLM_API_KEY')
    if not glm_key:
        return {
            'status': 'error',
            'message': 'GLM_API_KEY not found in environment',
            'fix': 'Set GLM_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test GLM API through OpenRouter (common integration)
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        'Authorization': f'Bearer {glm_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            glm_models = [model.get('id', 'unknown') for model in models_data.get('data', []) if 'glm' in model.get('id', '').lower()][:3]
            
            return {
                'status': 'success',
                'message': f'GLM API is valid. Found {model_count} total models.',
                'models': glm_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'GLM API key is invalid or expired',
                'fix': 'Generate a new GLM API key or check OpenRouter integration'
            }
        else:
            return {
                'status': 'error',
                'message': f'GLM API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'GLM API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_grok_api() -> Dict[str, Any]:
    """Test Grok API authentication and functionality"""
    print("🔑 Testing Grok API...")
    
    grok_key = os.environ.get('GROK_API_KEY')
    if not grok_key:
        return {
            'status': 'error',
            'message': 'GROK_API_KEY not found in environment',
            'fix': 'Set GROK_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test Grok API through OpenRouter
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        'Authorization': f'Bearer {grok_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            grok_models = [model.get('id', 'unknown') for model in models_data.get('data', []) if 'grok' in model.get('id', '').lower()][:3]
            
            return {
                'status': 'success',
                'message': f'Grok API is valid. Found {model_count} total models.',
                'models': grok_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'Grok API key is invalid or expired',
                'fix': 'Generate a new Grok API key or check OpenRouter integration'
            }
        else:
            return {
                'status': 'error',
                'message': f'Grok API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Grok API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_kimi_api() -> Dict[str, Any]:
    """Test Kimi API authentication and functionality"""
    print("🔑 Testing Kimi API...")
    
    kimi_key = os.environ.get('KIMI_API_KEY')
    if not kimi_key:
        return {
            'status': 'error',
            'message': 'KIMI_API_KEY not found in environment',
            'fix': 'Set KIMI_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test Kimi API (Moonshot AI)
    url = "https://api.moonshot.cn/v1/models"
    headers = {
        'Authorization': f'Bearer {kimi_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            kimi_models = [model.get('id', 'unknown') for model in models_data.get('data', [])][:3]
            
            return {
                'status': 'success',
                'message': f'Kimi API is valid. Found {model_count} available models.',
                'models': kimi_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'Kimi API key is invalid or expired',
                'fix': 'Generate a new Kimi API key at https://platform.moonshot.cn'
            }
        else:
            return {
                'status': 'error',
                'message': f'Kimi API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Kimi API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_qwen_api() -> Dict[str, Any]:
    """Test Qwen API authentication and functionality"""
    print("🔑 Testing Qwen API...")
    
    qwen_key = os.environ.get('QWEN_API_KEY')
    if not qwen_key:
        return {
            'status': 'error',
            'message': 'QWEN_API_KEY not found in environment',
            'fix': 'Set QWEN_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test Qwen API through OpenRouter
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        'Authorization': f'Bearer {qwen_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            qwen_models = [model.get('id', 'unknown') for model in models_data.get('data', []) if 'qwen' in model.get('id', '').lower()][:3]
            
            return {
                'status': 'success',
                'message': f'Qwen API is valid. Found {model_count} total models.',
                'models': qwen_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'Qwen API key is invalid or expired',
                'fix': 'Generate a new Qwen API key or check OpenRouter integration'
            }
        else:
            return {
                'status': 'error',
                'message': f'Qwen API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Qwen API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_gptoss_api() -> Dict[str, Any]:
    """Test GPTOSS API authentication and functionality"""
    print("🔑 Testing GPTOSS API...")
    
    gptoss_key = os.environ.get('GPTOSS_API_KEY')
    if not gptoss_key:
        return {
            'status': 'error',
            'message': 'GPTOSS_API_KEY not found in environment',
            'fix': 'Set GPTOSS_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test GPTOSS API (OpenAI-compatible endpoint)
    url = "https://api.gptoss.com/v1/models"
    headers = {
        'Authorization': f'Bearer {gptoss_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            gptoss_models = [model.get('id', 'unknown') for model in models_data.get('data', [])][:3]
            
            return {
                'status': 'success',
                'message': f'GPTOSS API is valid. Found {model_count} available models.',
                'models': gptoss_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'GPTOSS API key is invalid or expired',
                'fix': 'Generate a new GPTOSS API key or check service availability'
            }
        else:
            return {
                'status': 'error',
                'message': f'GPTOSS API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'GPTOSS API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_openrouter_api() -> Dict[str, Any]:
    """Test OpenRouter API authentication and functionality"""
    print("🔑 Testing OpenRouter API...")
    
    openrouter_key = os.environ.get('OPENROUTER_API_KEY')
    if not openrouter_key:
        return {
            'status': 'error',
            'message': 'OPENROUTER_API_KEY not found in environment',
            'fix': 'Set OPENROUTER_API_KEY environment variable or configure in repository secrets'
        }
    
    # Test OpenRouter API
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        'Authorization': f'Bearer {openrouter_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            free_models = [model.get('id', 'unknown') for model in models_data.get('data', []) if model.get('pricing', {}).get('prompt', '0') == '0'][:5]
            
            return {
                'status': 'success',
                'message': f'OpenRouter API is valid. Found {model_count} total models.',
                'models': free_models,
                'permissions': 'API access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'OpenRouter API key is invalid or expired',
                'fix': 'Generate a new OpenRouter API key at https://openrouter.ai'
            }
        else:
            return {
                'status': 'error',
                'message': f'OpenRouter API returned status {response.status_code}',
                'fix': 'Check API key validity and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'OpenRouter API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def generate_comprehensive_report(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate comprehensive test report"""
    report = ["# 🔑 Comprehensive API Test Report\n"]
    report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary
    success_count = sum(1 for result in results.values() if result['status'] == 'success')
    total_count = len(results)
    
    report.append("## 📊 Summary")
    report.append(f"- **Total APIs Tested**: {total_count}")
    report.append(f"- **Successful**: {success_count}")
    report.append(f"- **Failed**: {total_count - success_count}")
    report.append(f"- **Success Rate**: {(success_count/total_count)*100:.1f}%")
    report.append("")
    
    # Detailed results
    report.append("## 🔍 Detailed Results")
    for api_name, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        report.append(f"\n### {status_emoji} {api_name}")
        report.append(f"- **Status**: {result['status'].upper()}")
        report.append(f"- **Message**: {result['message']}")
        
        if 'models' in result and result['models']:
            report.append(f"- **Available Models**: {', '.join(result['models'])}")
        
        if result['status'] == 'error':
            report.append(f"- **Fix Required**: {result['fix']}")
    
    # Recommendations
    report.append("\n## 💡 Recommendations")
    
    working_apis = [name for name, result in results.items() if result['status'] == 'success']
    failed_apis = [name for name, result in results.items() if result['status'] == 'error']
    
    if working_apis:
        report.append("### ✅ Working APIs")
        for api in working_apis:
            report.append(f"- **{api}**: Ready for use in auto-response system")
    
    if failed_apis:
        report.append("\n### ❌ APIs Needing Attention")
        for api in failed_apis:
            report.append(f"- **{api}**: {results[api]['fix']}")
    
    # Next steps
    report.append("\n## 🚀 Next Steps")
    if success_count > 0:
        report.append("1. ✅ **Configure working APIs** in your auto-response workflows")
        report.append("2. 🔧 **Fix failed APIs** using the recommendations above")
        report.append("3. 🧪 **Test auto-response** with working APIs")
        report.append("4. 📊 **Monitor performance** and adjust as needed")
    else:
        report.append("1. 🔧 **Fix all API keys** using the recommendations above")
        report.append("2. 🧪 **Re-run tests** to verify fixes")
        report.append("3. ✅ **Configure working APIs** in workflows")
        report.append("4. 🚀 **Test auto-response system**")
    
    return "\n".join(report)

def main():
    """Main testing function"""
    print("🧪 Comprehensive API Testing")
    print("="*60)
    print("Testing all AI API keys for authentication and functionality")
    print("="*60)
    
    # Test all APIs
    results = {
        'DeepSeek API': test_deepseek_api(),
        'GLM API': test_glm_api(),
        'Grok API': test_grok_api(),
        'Kimi API': test_kimi_api(),
        'Qwen API': test_qwen_api(),
        'GPTOSS API': test_gptoss_api(),
        'OpenRouter API': test_openrouter_api()
    }
    
    # Display results
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    for api_name, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"\n{status_emoji} **{api_name}**")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Message: {result['message']}")
        
        if 'models' in result and result['models']:
            print(f"   Available Models: {', '.join(result['models'])}")
        
        if result['status'] == 'error':
            print(f"   Fix Required: {result['fix']}")
    
    # Generate comprehensive report
    report = generate_comprehensive_report(results)
    
    # Save report to file
    with open('api-test-report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 **Report saved to**: api-test-report.md")
    
    # Summary
    success_count = sum(1 for result in results.values() if result['status'] == 'success')
    total_count = len(results)
    
    print(f"\n🎯 **SUMMARY**: {success_count}/{total_count} APIs working")
    
    if success_count > 0:
        print("🎉 At least some APIs are working! Auto-response can use these.")
        working_apis = [name for name, result in results.items() if result['status'] == 'success']
        print(f"✅ Working APIs: {', '.join(working_apis)}")
    else:
        print("⚠️ No APIs are working. Please fix the API keys.")
    
    return success_count > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)