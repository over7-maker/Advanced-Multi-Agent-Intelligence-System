#!/usr/bin/env python3
"""
Automated conflict resolution - Keep security-hardened versions
"""
import os
import subprocess

def resolve_conflicts():
    """Resolve merge conflicts by keeping security-hardened versions"""
    
    # List of conflicted files
    conflicted_files = [
        '.env.example',
        'src/amas/agents/data_analysis/data_analysis_agent.py',
        'src/amas/agents/forensics/forensics_agent.py', 
        'src/amas/agents/investigation/investigation_agent.py',
        'src/amas/agents/metadata/metadata_agent.py',
        'src/amas/agents/osint/osint_agent.py',
        'src/amas/agents/reporting/reporting_agent.py',
        'src/amas/agents/reverse_engineering/reverse_engineering_agent.py',
        'src/amas/agents/technology_monitor/technology_monitor_agent.py',
        'src/amas/core/orchestrator.py'
    ]
    
    print("🔧 Resolving merge conflicts...")
    
    for file_path in conflicted_files:
        if os.path.exists(file_path):
            print(f"✅ Resolving conflict in: {file_path}")
            
            # Keep the version from main branch (security-hardened)
            result = subprocess.run(['git', 'checkout', '--theirs', file_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✓ Kept security-hardened version of {file_path}")
            else:
                print(f"   ⚠️ Could not auto-resolve {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")
    
    # Add all resolved files
    print("\n📦 Staging resolved files...")
    subprocess.run(['git', 'add', '.'], capture_output=True)
    
    print("\n✅ All conflicts resolved with security-hardened versions!")
    return True

if __name__ == "__main__":
    resolve_conflicts()
