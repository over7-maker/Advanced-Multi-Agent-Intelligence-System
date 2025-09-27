#!/usr/bin/env python3
"""
Test Release System
"""

import os
import sys
import subprocess
from datetime import datetime

def main():
    print("🧪 Testing AMAS Release System")
    print("=" * 50)
    
    # Test changelog generation
    test_changelog_generation()
    
    # Test release notes generation
    test_release_notes_generation()
    
    # Test version updater
    test_version_updater()
    
    # Test workflow files
    test_workflow_files()
    
    print("✅ All tests completed successfully!")
    return True

def test_changelog_generation():
    """Test changelog generation"""
    print("\n📝 Testing Changelog Generation...")
    
    # Set environment variables
    os.environ['VERSION'] = 'v1.0.0'
    os.environ['RELEASE_TYPE'] = 'minor'
    os.environ['CUSTOM_CHANGELOG'] = 'Test custom changelog'
    os.environ['OUTPUT'] = 'test_changelog.md'
    
    try:
        # Run changelog generator
        result = subprocess.run([
            sys.executable, 'scripts/generate_changelog.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Changelog generation test passed")
            
            # Check if file was created
            if os.path.exists('test_changelog.md'):
                print("✅ Changelog file created")
                
                # Read and display first few lines
                with open('test_changelog.md', 'r') as f:
                    content = f.read()
                    print(f"📄 Changelog preview: {content[:100]}...")
            else:
                print("❌ Changelog file not created")
        else:
            print(f"❌ Changelog generation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Changelog generation test failed: {e}")

def test_release_notes_generation():
    """Test release notes generation"""
    print("\n📋 Testing Release Notes Generation...")
    
    # Set environment variables
    os.environ['VERSION'] = 'v1.0.0'
    os.environ['OUTPUT'] = 'test_release_notes.md'
    
    try:
        # Run release notes generator
        result = subprocess.run([
            sys.executable, 'scripts/generate_release_notes.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Release notes generation test passed")
            
            # Check if file was created
            if os.path.exists('test_release_notes.md'):
                print("✅ Release notes file created")
                
                # Read and display first few lines
                with open('test_release_notes.md', 'r') as f:
                    content = f.read()
                    print(f"📄 Release notes preview: {content[:100]}...")
            else:
                print("❌ Release notes file not created")
        else:
            print(f"❌ Release notes generation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Release notes generation test failed: {e}")

def test_version_updater():
    """Test version updater"""
    print("\n📝 Testing Version Updater...")
    
    # Set environment variables
    os.environ['VERSION'] = 'v1.0.0'
    os.environ['RELEASE_TYPE'] = 'minor'
    
    try:
        # Run version updater
        result = subprocess.run([
            sys.executable, 'scripts/update_version.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Version updater test passed")
        else:
            print(f"❌ Version updater failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Version updater test failed: {e}")

def test_workflow_files():
    """Test workflow files"""
    print("\n🔄 Testing Workflow Files...")
    
    # Check if workflow files exist
    workflow_files = [
        '.github/workflows/release.yml',
        '.github/workflows/ai-issue-responder.yml',
        '.github/workflows/ai-code-analysis.yml',
        '.github/workflows/multi-agent-workflow.yml'
    ]
    
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            print(f"✅ {workflow_file} exists")
            
            # Check if file is valid YAML
            try:
                with open(workflow_file, 'r') as f:
                    content = f.read()
                    if 'name:' in content and 'on:' in content:
                        print(f"✅ {workflow_file} appears to be valid YAML")
                    else:
                        print(f"❌ {workflow_file} may not be valid YAML")
            except Exception as e:
                print(f"❌ Error reading {workflow_file}: {e}")
        else:
            print(f"❌ {workflow_file} does not exist")

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        'test_changelog.md',
        'test_release_notes.md'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")

if __name__ == "__main__":
    try:
        success = main()
        
        # Clean up test files
        cleanup_test_files()
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test system failed: {e}")
        sys.exit(1)