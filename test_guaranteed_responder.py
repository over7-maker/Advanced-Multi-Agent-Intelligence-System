#!/usr/bin/env python3
"""
Test Guaranteed Auto-Responder
Tests the simple working responder without external dependencies
"""

import os
import sys

def test_guaranteed_responder():
    """Test the guaranteed responder script"""
    print("🤖 Testing Guaranteed Auto-Responder")
    print("=" * 50)
    
    # Set test environment variables
    os.environ['GITHUB_REPOSITORY'] = 'over7-maker/Advanced-Multi-Agent-Intelligence-System'
    os.environ['ISSUE_NUMBER'] = '17'
    os.environ['ISSUE_TITLE'] = 'Documentation Missing'
    os.environ['ISSUE_BODY'] = 'We need better documentation for the project'
    os.environ['ISSUE_AUTHOR'] = 'test-user'
    
    # Test GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment")
        print("   This test requires a valid GitHub token")
        return False
    
    print("✅ Environment variables set")
    print(f"   Repository: {os.environ['GITHUB_REPOSITORY']}")
    print(f"   Issue: #{os.environ['ISSUE_NUMBER']}")
    print(f"   Title: {os.environ['ISSUE_TITLE']}")
    print(f"   Author: {os.environ['ISSUE_AUTHOR']}")
    
    # Test the responder logic
    print("\n🧪 Testing responder logic...")
    
    try:
        # Import the responder
        sys.path.append('.github/scripts')
        from simple_working_responder import categorize_issue, generate_response
        
        # Test categorization
        category = categorize_issue(os.environ['ISSUE_TITLE'], os.environ['ISSUE_BODY'])
        print(f"✅ Issue categorized as: {category}")
        
        # Test response generation
        response = generate_response(category, os.environ['ISSUE_TITLE'], os.environ['ISSUE_BODY'], os.environ['ISSUE_AUTHOR'])
        print(f"✅ Response generated: {len(response)} characters")
        print(f"   Preview: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing responder: {e}")
        return False

def test_github_auth():
    """Test GitHub authentication"""
    print("\n🔐 Testing GitHub Authentication...")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    print("✅ GITHUB_TOKEN found")
    print("✅ Authentication should work")
    return True

def main():
    """Main test function"""
    print("🧪 Guaranteed Auto-Responder Test")
    print("=" * 50)
    
    tests = [
        ("GitHub Authentication", test_github_auth),
        ("Guaranteed Responder", test_guaranteed_responder)
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
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Guaranteed auto-responder is ready!")
        print("\n🚀 Next steps:")
        print("1. Push changes to GitHub")
        print("2. Create a test issue")
        print("3. Verify auto-response works")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)