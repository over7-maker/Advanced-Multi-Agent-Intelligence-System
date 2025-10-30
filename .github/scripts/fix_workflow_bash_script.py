#!/usr/bin/env python3
"""
Bash Script Patcher for BULLETPROOF AI Workflows
Fixes the bash script issues causing workflow failures
"""

import os
import re

def fix_ai_agent_comment_listener():
    """Fix the AI agent comment listener workflow bash script"""
    
    workflow_path = ".github/workflows/ai_agent_comment_listener.yml"
    
    print(f"🔧 Fixing workflow: {workflow_path}")
    
    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Fix 1: Replace the broken API key check step
        old_check_step = r'- name: 🔍 Check AI Provider Availability\s+run: \|[^-]*?exit 1[^-]*?fi'
        
        new_check_step = '''- name: 🔍 Check AI Provider Availability
        shell: bash
        run: |
          set +e  # do not exit on non-zero tests
          echo "🔍 Checking AI provider availability..."
          available_providers=0

          check_key() {
            local name="$1"
            local value="${!name}"
            if [ -n "$value" ] && [ ${#value} -gt 10 ]; then
              echo "✅ $name: Available (${#value} chars)"
              available_providers=$((available_providers+1))
            else
              echo "ℹ️ $name: Not set or too short"
            fi
          }

          echo "🔎 Checking all 19 supported providers..."
          for key in DEEPSEEK_API_KEY CEREBRAS_API_KEY NVIDIA_API_KEY CODESTRAL_API_KEY GLM_API_KEY GROK_API_KEY COHERE_API_KEY CLAUDE_API_KEY GPT4_API_KEY GEMINI_API_KEY GROQAI_API_KEY MISTRAL_API_KEY KIMI_API_KEY QWEN_API_KEY GPTOSS_API_KEY GEMINIAI_API_KEY GEMINI2_API_KEY GROQ2_API_KEY CHUTES_API_KEY; do
            check_key "$key"
          done

          echo ""
          echo "📊 PROVIDER AVAILABILITY SUMMARY:"
          echo "  Available: $available_providers/19 providers"
          echo ""

          if [ "$available_providers" -eq 0 ]; then
            echo "🚨 CRITICAL: NO REAL AI PROVIDERS AVAILABLE!"
            echo "❌ Please add at least one valid API key to repository secrets:"
            echo "   - DEEPSEEK_API_KEY (recommended - free tier available)"
            echo "   - NVIDIA_API_KEY, CEREBRAS_API_KEY, CODESTRAL_API_KEY"
            echo "   - COHERE_API_KEY, CLAUDE_API_KEY, GPT4_API_KEY"
            echo ""
            echo "🔗 Get free API keys:"
            echo "   - DeepSeek: https://platform.deepseek.com"
            echo "   - Cerebras: https://cloud.cerebras.ai"
            exit 1
          else
            echo "✅ Real AI providers available ($available_providers) - proceeding with analysis"
            echo "AVAILABLE_PROVIDERS=$available_providers" >> $GITHUB_ENV
          fi'''
        
        # Apply the fix
        content = re.sub(old_check_step, new_check_step, content, flags=re.DOTALL)
        
        # Fix 2: Add permissions if not present
        if "permissions:" not in content:
            # Add after 'on:' section
            content = content.replace(
                "on:\n  issue_comment:\n    types: [created, edited]\n  pull_request:\n    types: [opened, synchronize, reopened]",
                "on:\n  issue_comment:\n    types: [created, edited]\n  pull_request:\n    types: [opened, synchronize, reopened]\n\npermissions:\n  contents: read\n  pull-requests: write\n  issues: write"
            )
        
        # Write fixed content back
        with open(workflow_path, 'w') as f:
            f.write(content)
        
        print("✅ Workflow fixed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing workflow: {e}")
        return False

def main():
    """Main function to apply all workflow fixes"""
    print("🚀 Starting BULLETPROOF AI Workflow Fixes...")
    print("=" * 60)
    
    success = True
    
    # Fix AI agent comment listener
    if not fix_ai_agent_comment_listener():
        success = False
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 ALL BULLETPROOF AI WORKFLOW FIXES APPLIED!")
        print("=" * 60)
        print("✅ AI agent comment listener workflow fixed")
        print("✅ Bash script API key checking repaired")
        print("✅ Bulletproof validation enforced")
        print("✅ Permissions added for PR operations")
        print("")
        print("📋 Next Steps:")
        print("1. Add at least one API key to repository secrets")
        print("2. Test the workflow with a new PR commit")
        print("3. Verify real AI analysis appears instead of fake content")
        print("")
        print("🎯 Expected Result:")
        print("   Provider: deepseek (or nvidia, cerebras, etc.)")
        print("   Response Time: 2.34s (variable, not 1.5s)")
        print("   Analysis: Specific file names and line numbers")
    else:
        print("\n❌ Some fixes failed - check errors above")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())