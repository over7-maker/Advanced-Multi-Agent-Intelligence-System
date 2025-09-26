#!/usr/bin/env python3
"""
Debug Auto-Responder
Comprehensive debugging script with detailed logging
"""

import os
import sys
import requests
import json
from datetime import datetime

def debug_environment():
    """Debug environment variables"""
    print("🔍 DEBUGGING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    required_vars = {
        'GITHUB_TOKEN': 'GitHub authentication token',
        'GITHUB_REPOSITORY': 'Repository name',
        'ISSUE_NUMBER': 'Issue number',
        'ISSUE_TITLE': 'Issue title',
        'ISSUE_BODY': 'Issue body',
        'ISSUE_AUTHOR': 'Issue author'
    }
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                masked_value = value
            print(f"✅ {var}: {masked_value} ({description})")
        else:
            print(f"❌ {var}: MISSING ({description})")
    
    return all(os.environ.get(var) for var in required_vars.keys())

def debug_github_auth():
    """Debug GitHub authentication"""
    print("\n🔐 DEBUGGING GITHUB AUTHENTICATION")
    print("=" * 50)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    
    if not github_token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    if not repo:
        print("❌ GITHUB_REPOSITORY not found")
        return False
    
    print(f"✅ GITHUB_TOKEN: Found (length: {len(github_token)})")
    print(f"✅ GITHUB_REPOSITORY: {repo}")
    
    # Test GitHub API access
    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AMAS-Auto-Responder/1.0'
        }
        
        print(f"🧪 Testing GitHub API access...")
        print(f"   URL: {url}")
        print(f"   Headers: {dict(headers)}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ GitHub API access: SUCCESS")
            return True
        else:
            print(f"❌ GitHub API access: FAILED")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def debug_issue_access():
    """Debug issue access"""
    print("\n📋 DEBUGGING ISSUE ACCESS")
    print("=" * 50)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    issue_number = os.environ.get('ISSUE_NUMBER')
    
    if not all([github_token, repo, issue_number]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AMAS-Auto-Responder/1.0'
        }
        
        print(f"🧪 Testing issue access...")
        print(f"   URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            issue_data = response.json()
            print(f"✅ Issue access: SUCCESS")
            print(f"   Issue #{issue_data['number']}: {issue_data['title']}")
            print(f"   State: {issue_data['state']}")
            print(f"   Author: {issue_data['user']['login']}")
            return True
        else:
            print(f"❌ Issue access: FAILED")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Issue access test failed: {e}")
        return False

def debug_comment_posting():
    """Debug comment posting"""
    print("\n💬 DEBUGGING COMMENT POSTING")
    print("=" * 50)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    issue_number = os.environ.get('ISSUE_NUMBER')
    
    if not all([github_token, repo, issue_number]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'AMAS-Auto-Responder/1.0'
        }
        
        # Test comment data
        test_comment = {
            'body': f"""## 🧪 Debug Test Comment

This is a test comment from the AMAS Auto-Responder debug system.

**Debug Information:**
- Timestamp: {datetime.now().isoformat()}
- Repository: {repo}
- Issue: #{issue_number}
- Test: Authentication and posting

---
*🤖 AMAS Auto-Responder Debug System*"""
        }
        
        print(f"🧪 Testing comment posting...")
        print(f"   URL: {url}")
        print(f"   Headers: {dict(headers)}")
        print(f"   Comment length: {len(test_comment['body'])} characters")
        
        response = requests.post(url, headers=headers, json=test_comment, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("✅ Comment posting: SUCCESS")
            comment_data = response.json()
            print(f"   Comment ID: {comment_data.get('id')}")
            print(f"   Comment URL: {comment_data.get('html_url')}")
            return True
        else:
            print(f"❌ Comment posting: FAILED")
            print(f"   Response: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Comment posting test failed: {e}")
        return False

def debug_label_posting():
    """Debug label posting"""
    print("\n🏷️ DEBUGGING LABEL POSTING")
    print("=" * 50)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    issue_number = os.environ.get('ISSUE_NUMBER')
    
    if not all([github_token, repo, issue_number]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'AMAS-Auto-Responder/1.0'
        }
        
        # Test label data
        test_labels = {
            'labels': ['debug-test', 'auto-response', 'ai-analyzed']
        }
        
        print(f"🧪 Testing label posting...")
        print(f"   URL: {url}")
        print(f"   Labels: {test_labels['labels']}")
        
        response = requests.post(url, headers=headers, json=test_labels, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Label posting: SUCCESS")
            return True
        else:
            print(f"❌ Label posting: FAILED")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Label posting test failed: {e}")
        return False

def main():
    """Main debugging function"""
    print("🐛 AMAS AUTO-RESPONDER DEBUG SYSTEM")
    print("=" * 60)
    print(f"Debug started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run all debug tests
    tests = [
        ("Environment Variables", debug_environment),
        ("GitHub Authentication", debug_github_auth),
        ("Issue Access", debug_issue_access),
        ("Comment Posting", debug_comment_posting),
        ("Label Posting", debug_label_posting)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All debug tests passed! Auto-responder should work!")
    else:
        print("⚠️ Some debug tests failed. Check the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Verify GitHub token has correct permissions")
        print("2. Check repository settings")
        print("3. Ensure workflow permissions are enabled")
        print("4. Verify issue is open and accessible")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Debug system failed: {e}")
        sys.exit(1)
