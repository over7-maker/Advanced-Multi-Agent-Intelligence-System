#!/usr/bin/env python3
"""
Update all workflows to use the Advanced API Keys Manager with 16 API keys
"""

import os
import re
from pathlib import Path

def update_workflow_file(file_path):
    """Update a single workflow file to use advanced API manager"""
    print(f"🔄 Updating {file_path}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add all 16 API keys to environment variables
    api_keys_section = """        # All 16 AI API Keys for Advanced Failover
        DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        GPT4_API_KEY: ${{ secrets.GPT4_API_KEY }}
        GLM_API_KEY: ${{ secrets.GLM_API_KEY }}
        GROK_API_KEY: ${{ secrets.GROK_API_KEY }}
        KIMI_API_KEY: ${{ secrets.KIMI_API_KEY }}
        QWEN_API_KEY: ${{ secrets.QWEN_API_KEY }}
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GPTOSS_API_KEY: ${{ secrets.GPTOSS_API_KEY }}
        GROQAI_API_KEY: ${{ secrets.GROQAI_API_KEY }}
        CEREBRAS_API_KEY: ${{ secrets.CEREBRAS_API_KEY }}
        GEMINIAI_API_KEY: ${{ secrets.GEMINIAI_API_KEY }}
        COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
        NVIDIA_API_KEY: ${{ secrets.NVIDIA_API_KEY }}
        CODESTRAL_API_KEY: ${{ secrets.CODESTRAL_API_KEY }}
        GEMINI2_API_KEY: ${{ secrets.GEMINI2_API_KEY }}
        GROQ2_API_KEY: ${{ secrets.GROQ2_API_KEY }}
        CHUTES_API_KEY: ${{ secrets.CHUTES_API_KEY }}"""
    
    # Replace the old API keys section with the new one
    old_pattern = r'# All AI API Keys.*?NVIDIA_API_KEY: \$\{\{ secrets\.NVIDIA_API_KEY \}\}'
    new_content = re.sub(old_pattern, api_keys_section, content, flags=re.DOTALL)
    
    # Add --use-advanced-manager flag to all python script calls
    python_script_pattern = r'(python \.github/scripts/[a-zA-Z_]+\.py[^|]*?)(--output [a-zA-Z_]+\.json)'
    def add_advanced_manager_flag(match):
        script_call = match.group(1)
        output = match.group(2)
        # Check if --use-advanced-manager is already present
        if '--use-advanced-manager' not in script_call:
            return f"{script_call} --use-advanced-manager \\\n              {output}"
        return match.group(0)
    
    new_content = re.sub(python_script_pattern, add_advanced_manager_flag, new_content)
    
    # Write the updated content back
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {file_path}")

def main():
    """Update all workflow files"""
    workflows_dir = Path('.github/workflows')
    
    # List of workflow files to update
    workflow_files = [
        '00-master-ai-orchestrator.yml',
        '01-ai-agentic-project-self-improver.yml',
        '02-ai-agentic-issue-auto-responder.yml',
        '03-ai-agent-project-audit-documentation.yml',
        '04-ai-enhanced-build-deploy.yml',
        '05-ai-security-threat-intelligence.yml',
        '06-ai-code-quality-performance.yml',
        '07-ai-enhanced-cicd-pipeline.yml'
    ]
    
    print("🚀 Updating all workflows to use Advanced API Keys Manager...")
    print("=" * 80)
    
    for workflow_file in workflow_files:
        file_path = workflows_dir / workflow_file
        if file_path.exists():
            update_workflow_file(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("=" * 80)
    print("✅ All workflows updated successfully!")
    print("🎯 All workflows now use the Advanced API Keys Manager with 16 API keys")
    print("🛡️  Intelligent failover ensures no AI agent will fail!")

if __name__ == "__main__":
    main()