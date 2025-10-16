#!/usr/bin/env python3
"""
Script to disable workflows that are generating fake AI responses
This script identifies and disables workflows that use old fake AI scripts
"""

import os
import re
from pathlib import Path

def find_fake_ai_workflows():
    """Find workflows that are using fake AI scripts"""
    workflows_dir = Path(".github/workflows")
    fake_workflows = []
    
    # Scripts that generate fake AI responses
    fake_scripts = [
        "ai_agent_fallback.py",
        "ai_parallel_provider.py", 
        "generate_fallback_comment.py",
        "process_ai_output.py",
        "ai_auto_commit_fixer.py",
        "ai_human_approval.py"
    ]
    
    for workflow_file in workflows_dir.glob("*.yml"):
        if workflow_file.name.startswith("."):
            continue
            
        try:
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Check if workflow uses any fake AI scripts
            for script in fake_scripts:
                if script in content:
                    fake_workflows.append({
                        'file': workflow_file,
                        'script': script,
                        'reason': f'Uses fake AI script: {script}'
                    })
                    break
                    
        except Exception as e:
            print(f"Error reading {workflow_file}: {e}")
    
    return fake_workflows

def disable_workflow(workflow_path):
    """Disable a workflow by renaming it"""
    try:
        new_name = workflow_path.name.replace('.yml', '.yml.disabled')
        new_path = workflow_path.parent / new_name
        workflow_path.rename(new_path)
        print(f"✅ Disabled: {workflow_path.name} -> {new_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to disable {workflow_path.name}: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Scanning for workflows using fake AI scripts...")
    
    fake_workflows = find_fake_ai_workflows()
    
    if not fake_workflows:
        print("✅ No workflows found using fake AI scripts")
        return
    
    print(f"🚨 Found {len(fake_workflows)} workflows using fake AI scripts:")
    for workflow in fake_workflows:
        print(f"  - {workflow['file'].name}: {workflow['reason']}")
    
    print("\n🛑 Disabling fake AI workflows...")
    disabled_count = 0
    
    for workflow in fake_workflows:
        if disable_workflow(workflow['file']):
            disabled_count += 1
    
    print(f"\n✅ Disabled {disabled_count}/{len(fake_workflows)} workflows")
    print("🎯 Only real AI workflows should remain active")

if __name__ == "__main__":
    main()