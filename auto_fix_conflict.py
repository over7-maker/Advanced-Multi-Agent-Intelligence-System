#!/usr/bin/env python3
"""
Automatic conflict resolver for orchestrator.py
This script will fix the merge conflict by applying the correct imports
"""

import re
import sys

def fix_orchestrator_conflict(file_path):
    """
    Automatically fix merge conflicts in orchestrator.py
    """
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found!")
        return False
    
    # Check if there are conflict markers
    if '<<<<<<<' not in content:
        print("No merge conflicts found in the file.")
        return True
    
    print("Merge conflict detected! Fixing...")
    
    # The correct imports that should replace the conflicted section
    correct_imports = """from amas.agents.base.intelligence_agent import IntelligenceAgent, AgentStatus
from amas.agents.osint.osint_agent import OSINTAgent
from amas.agents.investigation.investigation_agent import InvestigationAgent
from amas.agents.forensics.forensics_agent import ForensicsAgent
from amas.agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from amas.agents.reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from amas.agents.metadata.metadata_agent import MetadataAgent
from amas.agents.reporting.reporting_agent import ReportingAgent"""
    
    # Pattern to match the entire conflict block for imports
    conflict_pattern = r'<<<<<<< .*?\n(.*?)=======(.*?)>>>>>>> .*?\n'
    
    # Function to replace conflict blocks
    def replace_import_conflicts(match):
        conflict_text = match.group(0)
        
        # Check if this conflict contains agent imports
        if 'agents' in conflict_text and 'import' in conflict_text:
            print("Found import conflict block, replacing with correct imports...")
            return correct_imports + '\n'
        else:
            # If it's not an import conflict, leave it as is
            return conflict_text
    
    # Replace import conflicts
    fixed_content = re.sub(conflict_pattern, replace_import_conflicts, content, flags=re.DOTALL)
    
    # Also handle case where the entire import section might be in conflict
    # Look for a larger pattern that includes the imports
    import_section_pattern = r'<<<<<<< HEAD\n(?:from agents\..*?\n)+=======[^>]+>>>>>>> .*?\n'
    
    if re.search(import_section_pattern, fixed_content, re.MULTILINE | re.DOTALL):
        print("Found import section conflict, replacing entire section...")
        fixed_content = re.sub(import_section_pattern, correct_imports + '\n\n', fixed_content, flags=re.MULTILINE | re.DOTALL)
    
    # Final check: ensure no old import patterns remain
    old_import_pattern = r'^from agents\.'
    if re.search(old_import_pattern, fixed_content, re.MULTILINE):
        print("Fixing remaining old import paths...")
        fixed_content = re.sub(r'^from agents\.', 'from amas.agents.', fixed_content, flags=re.MULTILINE)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Conflict resolved successfully!")
    print("\nThe following imports have been set:")
    print(correct_imports)
    
    # Check if any conflict markers remain
    if '<<<<<<<' in fixed_content or '=======' in fixed_content or '>>>>>>>' in fixed_content:
        print("\n⚠️  Warning: Some conflict markers may still remain. Please check the file manually.")
        return False
    
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'src/amas/core/orchestrator.py'
    
    print(f"Fixing conflicts in: {file_path}")
    print("=" * 60)
    
    if fix_orchestrator_conflict(file_path):
        print("\n" + "=" * 60)
        print("Success! Next steps:")
        print("1. Review the changes: git diff")
        print("2. Add the file: git add " + file_path)
        print("3. Complete merge: git commit")
        print("4. Push changes: git push")
    else:
        print("\nPlease review the file manually to ensure all conflicts are resolved.")
        sys.exit(1)

if __name__ == "__main__":
    main()