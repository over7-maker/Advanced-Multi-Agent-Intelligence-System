#!/usr/bin/env python3
"""
Run API Key Tests
Comprehensive testing of all API keys and permissions
"""

import os
import sys
import subprocess
import requests
from typing import Dict, Any

def test_github_token_locally() -> Dict[str, Any]:
    """Test GitHub token locally"""
    print("🔑 Testing GitHub Token Locally...")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        return {
            'status': 'error',
            'message': 'GITHUB_TOKEN not found in environment',
            'fix': 'Set GITHUB_TOKEN environment variable'
        }
    
    # Test GitHub API
    url = "https://api.github.com/user"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            return {
                'status': 'success',
                'message': f'GitHub token is valid for user: {user_data.get("login", "unknown")}',
                'permissions': 'User access confirmed'
            }
        else:
            return {
                'status': 'error',
                'message': f'GitHub API returned status {response.status_code}',
                'fix': 'Check GitHub token permissions'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'GitHub API request failed: {e}',
            'fix': 'Check network connection and token validity'
        }

def test_openrouter_api_locally() -> Dict[str, Any]:
    """Test OpenRouter API locally"""
    print("🔑 Testing OpenRouter API Locally...")
    
    openrouter_key = os.environ.get('OPENROUTER_API_KEY')
    if not openrouter_key:
        return {
            'status': 'error',
            'message': 'OPENROUTER_API_KEY not found in environment',
            'fix': 'Set OPENROUTER_API_KEY environment variable'
        }
    
    # Test OpenRouter API
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        'Authorization': f'Bearer {openrouter_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            return {
                'status': 'success',
                'message': f'OpenRouter API is valid. Found {model_count} models.',
                'permissions': 'API access confirmed'
            }
        else:
            return {
                'status': 'error',
                'message': f'OpenRouter API returned status {response.status_code}',
                'fix': 'Check OpenRouter API key and account status'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'OpenRouter API request failed: {e}',
            'fix': 'Check network connection and API key validity'
        }

def test_deepseek_api_locally() -> Dict[str, Any]:
    """Test DeepSeek API locally"""
    print("🔑 Testing DeepSeek API Locally...")
    
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    if not deepseek_key:
        return {
            'status': 'error',
            'message': 'DEEPSEEK_API_KEY not found in environment',
            'fix': 'Set DEEPSEEK_API_KEY environment variable'
        }
    
    # Test DeepSeek API
    url = "https://api.deepseek.com/v1/models"
    headers = {
        'Authorization': f'Bearer {deepseek_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('data', []))
            return {
                'status': 'success',
                'message': f'DeepSeek API is valid. Found {model_count} models.',
                'permissions': 'API access confirmed'
            }
        else:
            return {
                'status': 'error',
                'message': f'DeepSeek API returned status {response.status_code}',
                'fix': 'Check DeepSeek API key and account status'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'DeepSeek API request failed: {e}',
            'fix': 'Check network connection and API key validity'
        }

def test_no_api_responder() -> Dict[str, Any]:
    """Test the no-API responder script"""
    print("🧪 Testing No-API Responder...")
    
    # Set test environment
    test_env = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN', 'test_token'),
        'ISSUE_NUMBER': '1',
        'ISSUE_TITLE': 'Test Performance Issue',
        'ISSUE_BODY': 'The application is running very slowly and needs optimization.',
        'ISSUE_AUTHOR': 'testuser',
        'REPO_NAME': 'test/repo'
    }
    
    try:
        result = subprocess.run([
            sys.executable, '.github/scripts/no_api_responder.py'
        ], env=test_env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                'status': 'success',
                'message': 'No-API responder works correctly',
                'output': result.stdout
            }
        else:
            return {
                'status': 'error',
                'message': f'No-API responder failed: {result.stderr}',
                'fix': 'Check script syntax and dependencies'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'No-API responder test failed: {e}',
            'fix': 'Check script execution and environment'
        }

def main():
    """Main testing function"""
    print("🧪 Comprehensive API Key Testing")
    print("="*60)
    
    # Test all APIs
    results = {
        'GitHub Token': test_github_token_locally(),
        'OpenRouter API': test_openrouter_api_locally(),
        'DeepSeek API': test_deepseek_api_locally(),
        'No-API Responder': test_no_api_responder()
    }
    
    # Display results
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    for service, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"\n{status_emoji} **{service}**")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Message: {result['message']}")
        if 'permissions' in result:
            print(f"   Permissions: {result['permissions']}")
        if 'output' in result and result['output']:
            print(f"   Output: {result['output'][:100]}...")
    
    # Generate recommendations
    print("\n" + "="*60)
    print("🔧 RECOMMENDATIONS")
    print("="*60)
    
    success_count = sum(1 for result in results.values() if result['status'] == 'success')
    total_count = len(results)
    
    if success_count == total_count:
        print("🎉 All tests passed! Your auto-response system should work perfectly!")
    elif results['No-API Responder']['status'] == 'success':
        print("✅ No-API responder works! You can use this as a fallback.")
        print("🔧 Fix the API key issues for enhanced AI responses.")
    else:
        print("⚠️ Multiple issues detected. Here are the fixes needed:")
        
        for service, result in results.items():
            if result['status'] == 'error':
                print(f"\n**{service}**: {result['fix']}")
    
    print(f"\n🎯 **SUMMARY**: {success_count}/{total_count} tests passed")
    
    # Specific recommendations
    if results['GitHub Token']['status'] == 'error':
        print("\n🚨 **CRITICAL**: GitHub token is required for auto-response to work!")
        print("   Fix: Configure GITHUB_TOKEN in repository secrets")
    
    if results['No-API Responder']['status'] == 'success':
        print("\n✅ **FALLBACK AVAILABLE**: No-API responder works as backup!")
        print("   This ensures auto-response works even without AI keys")
    
    return success_count >= 1  # At least one method should work

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)