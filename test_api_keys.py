#!/usr/bin/env python3
"""
API Key Testing Script
Tests all API keys and GitHub token to identify authentication issues
"""

import os
import sys
import requests
import json
from typing import Dict, Any, Optional

def test_github_token() -> Dict[str, Any]:
    """Test GitHub token authentication"""
    print("🔑 Testing GitHub Token...")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('REPO_NAME', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')
    
    if not github_token:
        return {
            'status': 'error',
            'message': 'GITHUB_TOKEN not found in environment',
            'fix': 'Configure GITHUB_TOKEN in repository secrets'
        }
    
    # Test GitHub API access
    url = f"https://api.github.com/repos/{repo_name}"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repo_data = response.json()
            return {
                'status': 'success',
                'message': f'GitHub token is valid for repository: {repo_data.get("full_name", "unknown")}',
                'permissions': 'Repository access confirmed'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'GitHub token is invalid or expired',
                'fix': 'Generate a new GitHub Personal Access Token with repo permissions'
            }
        elif response.status_code == 403:
            return {
                'status': 'error',
                'message': 'GitHub token lacks required permissions',
                'fix': 'Update token permissions to include: repo, workflow, write:packages'
            }
        else:
            return {
                'status': 'error',
                'message': f'GitHub API returned status {response.status_code}',
                'fix': 'Check repository name and token permissions'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'GitHub API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_openrouter_api() -> Dict[str, Any]:
    """Test OpenRouter API authentication"""
    print("🔑 Testing OpenRouter API...")
    
    openrouter_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not openrouter_key:
        return {
            'status': 'error',
            'message': 'OPENROUTER_API_KEY not found in environment',
            'fix': 'Configure OPENROUTER_API_KEY in repository secrets'
        }
    
    # Test OpenRouter API access
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
                'message': f'OpenRouter API is valid. Found {model_count} available models.',
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
                'fix': 'Check API key and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'OpenRouter API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_deepseek_api() -> Dict[str, Any]:
    """Test DeepSeek API authentication"""
    print("🔑 Testing DeepSeek API...")
    
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    
    if not deepseek_key:
        return {
            'status': 'error',
            'message': 'DEEPSEEK_API_KEY not found in environment',
            'fix': 'Configure DEEPSEEK_API_KEY in repository secrets'
        }
    
    # Test DeepSeek API access
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
                'message': f'DeepSeek API is valid. Found {model_count} available models.',
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
                'fix': 'Check API key and account status'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'DeepSeek API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def test_github_issue_permissions() -> Dict[str, Any]:
    """Test GitHub issue write permissions"""
    print("🔑 Testing GitHub Issue Permissions...")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('REPO_NAME', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')
    
    if not github_token:
        return {
            'status': 'error',
            'message': 'GITHUB_TOKEN not found',
            'fix': 'Configure GITHUB_TOKEN in repository secrets'
        }
    
    # Test issue permissions by trying to get issues
    url = f"https://api.github.com/repos/{repo_name}/issues"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {
                'status': 'success',
                'message': 'GitHub issue read permissions confirmed',
                'permissions': 'Can read issues'
            }
        elif response.status_code == 401:
            return {
                'status': 'error',
                'message': 'GitHub token authentication failed',
                'fix': 'Generate a new GitHub Personal Access Token'
            }
        elif response.status_code == 403:
            return {
                'status': 'error',
                'message': 'GitHub token lacks issue permissions',
                'fix': 'Update token permissions to include: repo (Full control)'
            }
        else:
            return {
                'status': 'error',
                'message': f'GitHub issues API returned status {response.status_code}',
                'fix': 'Check repository access and permissions'
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'GitHub issues API request failed: {e}',
            'fix': 'Check network connection and API endpoint'
        }

def generate_fix_instructions(results: Dict[str, Dict[str, Any]]) -> str:
    """Generate fix instructions based on test results"""
    fixes = []
    
    for service, result in results.items():
        if result['status'] == 'error':
            fixes.append(f"**{service.upper()}**: {result['fix']}")
    
    if not fixes:
        return "✅ All API keys and permissions are working correctly!"
    
    return "🔧 **REQUIRED FIXES:**\n\n" + "\n\n".join(fixes)

def main():
    """Main testing function"""
    print("🧪 API Key and Permission Testing")
    print("="*50)
    
    # Set default environment variables for testing
    if not os.environ.get('REPO_NAME'):
        os.environ['REPO_NAME'] = 'over7-maker/Advanced-Multi-Agent-Intelligence-System'
    
    # Test all APIs
    results = {
        'GitHub Token': test_github_token(),
        'OpenRouter API': test_openrouter_api(),
        'DeepSeek API': test_deepseek_api(),
        'GitHub Issues': test_github_issue_permissions()
    }
    
    # Display results
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    for service, result in results.items():
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"\n{status_emoji} **{service}**")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Message: {result['message']}")
        if 'permissions' in result:
            print(f"   Permissions: {result['permissions']}")
    
    # Generate fix instructions
    print("\n" + "="*50)
    print("🔧 FIX INSTRUCTIONS")
    print("="*50)
    
    fix_instructions = generate_fix_instructions(results)
    print(fix_instructions)
    
    # Summary
    success_count = sum(1 for result in results.values() if result['status'] == 'success')
    total_count = len(results)
    
    print(f"\n🎯 **SUMMARY**: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All API keys and permissions are working correctly!")
        print("✅ Auto-response should work without issues!")
    else:
        print("⚠️ Some API keys or permissions need to be fixed.")
        print("🔧 Please follow the fix instructions above.")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)