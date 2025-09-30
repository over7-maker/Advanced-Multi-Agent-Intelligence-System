#!/usr/bin/env python3
"""
Test runner for AMAS system
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run the test suite"""
    print("🧪 Running AMAS Test Suite")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        return False
    
    # Run tests
    print("\n🚀 Running tests...")
    test_commands = [
        # Unit tests
        ["python", "-m", "pytest", "tests/test_core.py", "-v", "--tb=short"],
        ["python", "-m", "pytest", "tests/test_agents.py", "-v", "--tb=short"],
        ["python", "-m", "pytest", "tests/test_services.py", "-v", "--tb=short"],
        
        # API tests (requires running API server)
        # ["python", "-m", "pytest", "tests/test_api.py", "-v", "--tb=short"],
        
        # Integration tests
        # ["python", "-m", "pytest", "tests/test_integration.py", "-v", "--tb=short"],
    ]
    
    all_passed = True
    for cmd in test_commands:
        print(f"\n🔍 Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True)
            print(f"✅ Test passed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Test failed: {e}")
            all_passed = False
    
    # Run all tests together
    print(f"\n🔍 Running all tests...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", "tests/", 
            "-v", "--tb=short", "--disable-warnings"
        ], check=True)
        print(f"✅ All tests passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Some tests failed: {e}")
        all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)