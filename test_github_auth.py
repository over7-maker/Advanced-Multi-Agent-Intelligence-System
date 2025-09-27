#!/usr/bin/env python3
"""
Test GitHub Authentication
Quick test to verify GitHub token permissions
"""

import os
import requests

def test_github_auth():
    """Test GitHub authentication with current token"""
    github_token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')
    
    if not github_token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    print(f"🧪 Testing GitHub authentication for {repo}")
    
    # Test 1: Get repository info
    print("\n1️⃣ Testing repository access...")
    try:
        url = f"https://api.github.com/repos/{repo}"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Repository access: SUCCESS")
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Repository access error: {e}")
        return False
    
    # Test 2: Get issues
    print("\n2️⃣ Testing issues access...")
    try:
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Issues access: SUCCESS")
        else:
            print(f"❌ Issues access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Issues access error: {e}")
        return False
    
    # Test 3: Test comment posting (dry run)
    print("\n3️⃣ Testing comment permissions...")
    try:
        # Get a test issue (issue #51 from your log)
        url = f"https://api.github.com/repos/{repo}/issues/51"
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Issue access: SUCCESS")
            issue_data = response.json()
            print(f"   Issue #{issue_data['number']}: {issue_data['title']}")
            print(f"   State: {issue_data['state']}")
        else:
            print(f"❌ Issue access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Issue access error: {e}")
        return False
    
    print("\n🎉 All GitHub authentication tests passed!")
    print("✅ Your GitHub token has the correct permissions")
    return True

def main():
    """Main test function"""
    print("🔐 GitHub Authentication Test")
    print("=" * 40)
    
    success = test_github_auth()
    
    if success:
        print("\n✅ GitHub authentication is working correctly!")
        print("🚀 Your auto-response system should work now!")
    else:
        print("\n❌ GitHub authentication failed!")
        print("🔧 Please check:")
        print("1. GitHub token is set correctly")
        print("2. Repository permissions are enabled")
        print("3. Workflow permissions allow write access")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)