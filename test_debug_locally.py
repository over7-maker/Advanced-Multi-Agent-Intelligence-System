#!/usr/bin/env python3
"""
Test Debug Script Locally
Test the debug responder script without GitHub Actions
"""

import os
import sys

def setup_test_environment():
    """Set up test environment variables"""
    print("🔧 Setting up test environment...")
    
    # Set test environment variables
    test_env = {
        'GITHUB_REPOSITORY': 'over7-maker/Advanced-Multi-Agent-Intelligence-System',
        'ISSUE_NUMBER': '53',
        'ISSUE_TITLE': 'Documentation Missing',
        'ISSUE_BODY': 'The documentation for this feature is incomplete and needs updating.',
        'ISSUE_AUTHOR': 'over7-maker'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
        print(f"  ✅ {key}: {value}")
    
    # Check for GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        print(f"  ✅ GITHUB_TOKEN: Found (length: {len(github_token)})")
        return True
    else:
        print("  ❌ GITHUB_TOKEN: Not found")
        print("     This test requires a valid GitHub token")
        print("     Set it with: export GITHUB_TOKEN=your_token_here")
        return False

def test_debug_script():
    """Test the debug script"""
    print("\n🧪 Testing debug script...")
    
    try:
        # Import and run the debug script
        sys.path.append('.github/scripts')
        from debug_responder import main as debug_main
        
        print("✅ Debug script imported successfully")
        
        # Run the debug script
        result = debug_main()
        
        if result:
            print("✅ Debug script completed successfully")
        else:
            print("❌ Debug script failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error running debug script: {e}")
        return False

def test_simple_responder():
    """Test the simple responder script"""
    print("\n🤖 Testing simple responder...")
    
    try:
        # Import and test the simple responder
        sys.path.append('.github/scripts')
        from simple_working_responder import categorize_issue, generate_response
        
        print("✅ Simple responder imported successfully")
        
        # Test categorization
        title = os.environ.get('ISSUE_TITLE', '')
        body = os.environ.get('ISSUE_BODY', '')
        author = os.environ.get('ISSUE_AUTHOR', '')
        
        category = categorize_issue(title, body)
        print(f"✅ Issue categorized as: {category}")
        
        # Test response generation
        response = generate_response(category, title, body, author)
        print(f"✅ Response generated: {len(response)} characters")
        print(f"   Preview: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple responder: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 LOCAL DEBUG TEST")
    print("=" * 50)
    
    # Setup environment
    if not setup_test_environment():
        print("\n❌ Test environment setup failed")
        print("Please set GITHUB_TOKEN environment variable")
        return False
    
    # Run tests
    tests = [
        ("Debug Script", test_debug_script),
        ("Simple Responder", test_simple_responder)
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
    print("📊 LOCAL TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All local tests passed!")
        print("🚀 The auto-responder system should work in GitHub Actions")
    else:
        print("⚠️ Some local tests failed.")
        print("🔧 Please check the issues above before deploying")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        sys.exit(1)