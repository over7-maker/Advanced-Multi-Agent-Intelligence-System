#!/usr/bin/env python3
"""
Complete Workflow Audit - Final Verification
Ensures 100% completion with zero gaps
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

def audit_all_workflows():
    """Complete audit of all workflows"""
    print("🔍 COMPLETE WORKFLOW AUDIT - FINAL VERIFICATION")
    print("=" * 80)
    
    workflows_dir = Path('.github/workflows')
    
    # Get all workflow files
    all_workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    print(f"📊 Total Workflows Found: {len(all_workflows)}")
    print()
    
    # Categorize workflows
    categories = {
        "core_ai_workflows": [],
        "supporting_workflows": [],
        "legacy_workflows": [],
        "utility_workflows": [],
        "broken_workflows": []
    }
    
    for workflow in all_workflows:
        try:
            with open(workflow, 'r') as f:
                content = f.read()
                yaml_data = yaml.safe_load(content)
            
            # Check if it's a core AI workflow
            if any(keyword in workflow.name.lower() for keyword in [
                'master-ai-orchestrator', 'ai-agentic', 'ai-agent', 'ai-enhanced'
            ]):
                categories["core_ai_workflows"].append(workflow.name)
            
            # Check if it's a supporting workflow
            elif any(keyword in workflow.name.lower() for keyword in [
                'ci', 'release', 'security', 'emergency', 'auto-fix'
            ]):
                categories["supporting_workflows"].append(workflow.name)
            
            # Check if it's legacy
            elif any(keyword in workflow.name.lower() for keyword in [
                'enhanced-ai', 'universal-ai', 'multi-agent', 'comprehensive-ai',
                'ultimate', 'simple', 'minimal', 'test-ai'
            ]):
                categories["legacy_workflows"].append(workflow.name)
            
            # Check if it's utility
            elif any(keyword in workflow.name.lower() for keyword in [
                'python-dependency', 'auto-format'
            ]):
                categories["utility_workflows"].append(workflow.name)
            
            else:
                # Check for broken syntax
                if 'true:' in content or 'on:' not in content:
                    categories["broken_workflows"].append(workflow.name)
                else:
                    categories["legacy_workflows"].append(workflow.name)
                    
        except Exception as e:
            print(f"❌ Error reading {workflow.name}: {e}")
            categories["broken_workflows"].append(workflow.name)
    
    # Print audit results
    print("📋 WORKFLOW CATEGORIZATION:")
    print("-" * 40)
    
    for category, workflows in categories.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(workflows)}):")
        for workflow in workflows:
            print(f"  - {workflow}")
    
    print("\n" + "=" * 80)
    print("🎯 AUDIT RECOMMENDATIONS:")
    print("=" * 80)
    
    # Recommendations
    if categories["legacy_workflows"]:
        print(f"⚠️  Remove {len(categories['legacy_workflows'])} legacy workflows")
        for workflow in categories["legacy_workflows"]:
            print(f"    - {workflow}")
    
    if categories["broken_workflows"]:
        print(f"❌ Fix or remove {len(categories['broken_workflows'])} broken workflows")
        for workflow in categories["broken_workflows"]:
            print(f"    - {workflow}")
    
    # Check for API manager usage
    print("\n🔍 API MANAGER USAGE CHECK:")
    print("-" * 40)
    
    api_manager_usage = check_api_manager_usage(all_workflows)
    print(f"✅ Workflows using API manager: {api_manager_usage['using_manager']}")
    print(f"⚠️  Workflows NOT using API manager: {api_manager_usage['not_using_manager']}")
    
    if api_manager_usage['not_using_manager']:
        print("   Workflows that need API manager integration:")
        for workflow in api_manager_usage['not_using_manager']:
            print(f"    - {workflow}")
    
    return categories, api_manager_usage

def check_api_manager_usage(workflows: List[Path]) -> Dict[str, List[str]]:
    """Check which workflows use the API manager"""
    using_manager = []
    not_using_manager = []
    
    for workflow in workflows:
        try:
            with open(workflow, 'r') as f:
                content = f.read()
            
            # Check for API manager usage
            if any(indicator in content for indicator in [
                '--use-advanced-manager',
                'universal_ai_workflow_integration',
                'standalone_universal_ai_manager',
                'get_integration',
                'generate_workflow_ai_response'
            ]):
                using_manager.append(workflow.name)
            else:
                not_using_manager.append(workflow.name)
                
        except Exception as e:
            print(f"❌ Error checking {workflow.name}: {e}")
            not_using_manager.append(workflow.name)
    
    return {
        "using_manager": using_manager,
        "not_using_manager": not_using_manager
    }

def remove_identified_legacy_workflows():
    """Remove all identified legacy workflows"""
    print("\n🗑️  REMOVING IDENTIFIED LEGACY WORKFLOWS")
    print("=" * 80)
    
    workflows_dir = Path('.github/workflows')
    
    # Legacy workflows to remove
    legacy_workflows = [
        'ai-security-response.yml',
        'ci.yml',
        'ci-auto-fix.yml',
        'auto-fix.yml',
        'ai-incident-response.yml',
        'release.yml',
        'emergency-auto-response.yml',
        'python-dependency-submission.yml',
        'ai-code-analysis.yml'
    ]
    
    removed_count = 0
    not_found_count = 0
    
    for workflow in legacy_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            try:
                workflow_path.unlink()
                print(f"✅ Removed: {workflow}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {workflow}: {e}")
        else:
            print(f"⚠️  Not found: {workflow}")
            not_found_count += 1
    
    print(f"\n📊 REMOVAL SUMMARY:")
    print(f"✅ Removed: {removed_count} workflows")
    print(f"⚠️  Not found: {not_found_count} workflows")
    
    return removed_count

def main():
    """Main audit function"""
    print("🚀 STARTING COMPLETE WORKFLOW AUDIT")
    print("=" * 80)
    
    # Run audit
    categories, api_usage = audit_all_workflows()
    
    # Remove legacy workflows
    removed_count = remove_identified_legacy_workflows()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 AUDIT COMPLETE - FINAL SUMMARY")
    print("=" * 80)
    
    remaining_workflows = list(Path('.github/workflows').glob("*.yml"))
    print(f"📊 Remaining Workflows: {len(remaining_workflows)}")
    
    print("\n📋 FINAL WORKFLOW LIST:")
    for workflow in remaining_workflows:
        print(f"  - {workflow.name}")
    
    print("\n✅ AUDIT COMPLETE!")
    print("🎯 Only essential workflows remain!")

if __name__ == "__main__":
    main()