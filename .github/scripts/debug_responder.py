#!/usr/bin/env python3
"""
Debug Auto-Responder - Comprehensive debugging script with detailed logging
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def debug_environment():
    """Debug environment variables and configuration"""
    print("🔍 DEBUGGING AI ISSUE RESPONDER ENVIRONMENT")
    print("=" * 60)

    # Check environment variables
    env_vars = [
        "GITHUB_TOKEN",
        "GITHUB_REPOSITORY",
        "ISSUE_NUMBER",
        "ISSUE_TITLE",
        "ISSUE_BODY",
        "ISSUE_ACTION",
        "ISSUE_AUTHOR",
    ]

    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Truncate long values for security
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")

    # Check API keys
    api_keys = [
        "DEEPSEEK_API_KEY",
        "GLM_API_KEY",
        "GROK_API_KEY",
        "KIMI_API_KEY",
        "QWEN_API_KEY",
        "GPTOSS_API_KEY",
        "GROQAI_API_KEY",
        "CEREBRAS_API_KEY",
        "GEMINIAI_API_KEY",
    ]

    print("\n🔑 API Keys Status:")
    active_keys = 0
    for key in api_keys:
        value = os.getenv(key)
        if value and value.strip():
            active_keys += 1
            print(f"  ✅ {key}: Available")
        else:
            print(f"  ❌ {key}: Not available")

    print(f"\n📊 Summary: {active_keys}/9 API keys available")

    # Check Python environment
    print("\n🐍 Python Environment:")
    print(f"  Python Version: {sys.version}")
    print(f"  Python Path: {sys.executable}")

    # Check if required modules are available
    print("\n📦 Required Modules:")
    modules = ["openai", "aiohttp", "requests", "PyGithub"]
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}: Available")
        except ImportError:
            print(f"  ❌ {module}: Not available")

    print("\n✅ Debug completed successfully!")
    return True


def debug_github_auth():
    """Debug GitHub authentication"""
    print("\n🔐 DEBUGGING GITHUB AUTHENTICATION")
    print("=" * 50)

    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")

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
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AMAS-Auto-Responder/1.0",
        }

        print(f"🧪 Testing GitHub API access...")
        print(f"   URL: {url}")

        response = requests.get(url, headers=headers, timeout=10)

        print(f"   Status Code: {response.status_code}")

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

    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    issue_number = os.environ.get("ISSUE_NUMBER")

    if not all([github_token, repo, issue_number]):
        print("❌ Missing required environment variables")
        return False

    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AMAS-Auto-Responder/1.0",
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

    github_token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    issue_number = os.environ.get("ISSUE_NUMBER")

    if not all([github_token, repo, issue_number]):
        print("❌ Missing required environment variables")
        return False

    try:
        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "AMAS-Auto-Responder/1.0",
        }

        # Test comment data
        test_comment = {
            "body": f"""## 🧪 Debug Test Comment

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
        print(f"   Comment length: {len(test_comment['body'])} characters")

        response = requests.post(url, headers=headers, json=test_comment, timeout=10)

        print(f"   Status Code: {response.status_code}")

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
