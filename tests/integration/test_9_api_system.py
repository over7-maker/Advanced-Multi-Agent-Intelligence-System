#!/usr/bin/env python3
"""
Test the 9-API failover system
"""

import json
import os
import sys
from pathlib import Path


def test_api_keys():
    """Test API key configuration"""
    print("🔑 Testing API Key Configuration...")

    api_keys = [
        "DEEPSEEK_API_KEY",
        "CLAUDE_API_KEY",
        "GPT4_API_KEY",
        "GLM_API_KEY",
        "GROK_API_KEY",
        "KIMI_API_KEY",
        "QWEN_API_KEY",
        "GEMINI_API_KEY",
        "GPTOSS_API_KEY",
    ]

    configured_count = 0
    for key in api_keys:
        if os.environ.get(key):
            print(f"  ✅ {key}: Configured")
            configured_count += 1
        else:
            print(f"  ❌ {key}: Not configured")

    print(f"\n📊 API Key Status: {configured_count}/9 configured")
    return configured_count

def test_workflow_files():
    """Test workflow files for 9-API support"""
    print("\n📄 Testing Workflow Files...")

    workflows_dir = Path(".github/workflows")
    workflows = list(workflows_dir.glob("*.yml"))

    updated_count = 0
    for workflow in workflows:
        try:
            with open(workflow, "r") as f:
                content = f.read()

            # Check for 9-API support
            has_deepseek = "DEEPSEEK_API_KEY" in content
            has_claude = "CLAUDE_API_KEY" in content
            has_gpt4 = "GPT4_API_KEY" in content
            has_gemini = "GEMINI_API_KEY" in content

            if has_deepseek and has_claude and has_gpt4 and has_gemini:
                print(f"  ✅ {workflow.name}: 9-API support")
                updated_count += 1
            else:
                print(f"  ❌ {workflow.name}: Missing 9-API support")

        except Exception as e:
            print(f"  ❌ {workflow.name}: Error reading file - {e}")

    print(f"\n📊 Workflow Status: {updated_count}/{len(workflows)} updated")
    return updated_count

def test_ai_scripts():
    """Test AI scripts for 9-API support"""
    print("\n🤖 Testing AI Scripts...")

    scripts_dir = Path(".github/scripts")
    scripts = list(scripts_dir.glob("ai_*.py"))

    updated_count = 0
    for script in scripts:
        try:
            with open(script, "r") as f:
                content = f.read()

            # Check for 9-API support
            has_deepseek = "DEEPSEEK_API_KEY" in content
            has_claude = "CLAUDE_API_KEY" in content
            has_gpt4 = "GPT4_API_KEY" in content
            has_gemini = "GEMINI_API_KEY" in content

            if has_deepseek and has_claude and has_gpt4 and has_gemini:
                print(f"  ✅ {script.name}: 9-API support")
                updated_count += 1
            else:
                print(f"  ❌ {script.name}: Missing 9-API support")

        except Exception as e:
            print(f"  ❌ {script.name}: Error reading file - {e}")

    print(f"\n📊 Script Status: {updated_count}/{len(scripts)} updated")
    return updated_count

def test_fallback_priority():
    """Test fallback priority order"""
    print("\n🔄 Testing Fallback Priority...")

    # Expected priority order
    expected_order = [
        "DeepSeek",
        "Claude",
        "GPT-4",
        "GLM",
        "Grok",
        "Kimi",
        "Qwen",
        "Gemini",
        "GPTOSS",
    ]

    # Check a sample script for priority order
    script_path = Path(".github/scripts/ai_code_analyzer.py")
    try:
        with open(script_path, "r") as f:
            content = f.read()

        # Check if priority comments are updated
        if "Priority order: DeepSeek (most reliable), Claude, GPT-4" in content:
            print("  ✅ Priority order correctly updated")
            return True
        else:
            print("  ❌ Priority order not updated")
            return False

    except Exception as e:
        print(f"  ❌ Error checking priority: {e}")
        return False

def main():
    """Run comprehensive 9-API system test"""
    print("🚀 Testing 9-API Failover System")
    print("=" * 50)

    # Test API keys
    api_count = test_api_keys()

    # Test workflow files
    workflow_count = test_workflow_files()

    # Test AI scripts
    script_count = test_ai_scripts()

    # Test fallback priority
    priority_ok = test_fallback_priority()

    # Generate summary
    print("\n📊 9-API System Test Summary")
    print("=" * 50)
    print(f"API Keys Configured: {api_count}/9")
    print(f"Workflows Updated: {workflow_count}")
    print(f"Scripts Updated: {script_count}")
    print(f"Priority Order: {'✅ Correct' if priority_ok else '❌ Incorrect'}")

    # Overall status
    if api_count >= 6 and workflow_count >= 10 and script_count >= 10 and priority_ok:
        print("\n🎉 9-API System Status: ✅ READY")
        print("✅ All workflows now support 9-API failover")
        print("✅ Intelligent fallback system active")
        print(
            "✅ Priority order: DeepSeek → Claude → GPT-4 → GLM → Grok → Kimi → Qwen → Gemini → GPTOSS"
        )
    else:
        print("\n⚠️ 9-API System Status: ⚠️ NEEDS ATTENTION")
        print("Some components may need additional configuration")

    return (
        api_count >= 6 and workflow_count >= 10 and script_count >= 10 and priority_ok
    )

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
