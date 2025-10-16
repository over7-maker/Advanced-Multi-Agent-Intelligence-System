#!/usr/bin/env python3
"""
Workflow Audit Monitor - Meta-workflow for future audits
"""

import argparse
import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

def audit_workflows(audit_type: str) -> Dict[str, Any]:
    """Comprehensive workflow audit"""
    print(f"🔍 Starting {audit_type} workflow audit...")
    
    workflows_dir = Path('.github/workflows')
    all_workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    audit_results = {
        "audit_type": audit_type,
        "total_workflows": len(all_workflows),
        "valid_workflows": [],
        "broken_workflows": [],
        "legacy_workflows": [],
        "api_manager_usage": [],
        "recommendations": [],
        "statistics": {}
    }
    
    for workflow in all_workflows:
        try:
            with open(workflow, 'r') as f:
                content = f.read()
                yaml_data = yaml.safe_load(content)
            
            # Check if workflow is valid
            if yaml_data and 'name' in yaml_data:
                audit_results["valid_workflows"].append(workflow.name)
                
                # Check for API manager usage
                if any(indicator in content for indicator in [
                    '--use-advanced-manager',
                    'universal_ai_workflow_integration',
                    'standalone_universal_ai_manager'
                ]):
                    audit_results["api_manager_usage"].append(workflow.name)
                
                # Check for legacy patterns
                if any(pattern in workflow.name.lower() for pattern in [
                    'enhanced-ai', 'universal-ai', 'multi-agent', 'comprehensive-ai',
                    'ultimate', 'simple', 'minimal', 'test-ai'
                ]):
                    audit_results["legacy_workflows"].append(workflow.name)
            
        except Exception as e:
            audit_results["broken_workflows"].append({
                "file": workflow.name,
                "error": str(e)
            })
    
    # Generate recommendations
    if audit_results["broken_workflows"]:
        audit_results["recommendations"].append("Fix broken workflows with YAML syntax errors")
    
    if len(audit_results["legacy_workflows"]) > 0:
        audit_results["recommendations"].append("Remove legacy workflows")
    
    non_api_workflows = [w for w in audit_results["valid_workflows"] 
                        if w not in audit_results["api_manager_usage"]]
    if non_api_workflows:
        audit_results["recommendations"].append("Integrate API manager in remaining workflows")
    
    # Calculate statistics
    audit_results["statistics"] = {
        "valid_percentage": (len(audit_results["valid_workflows"]) / len(all_workflows)) * 100,
        "api_manager_percentage": (len(audit_results["api_manager_usage"]) / len(all_workflows)) * 100,
        "broken_count": len(audit_results["broken_workflows"]),
        "legacy_count": len(audit_results["legacy_workflows"])
    }
    
    return audit_results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Workflow Audit Monitor")
    parser.add_argument("--audit-type", default="comprehensive", help="Audit type")
    parser.add_argument("--output", default="workflow_audit_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Run audit
    results = audit_workflows(args.audit_type)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 WORKFLOW AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Workflows: {results['total_workflows']}")
    print(f"Valid Workflows: {len(results['valid_workflows'])}")
    print(f"Broken Workflows: {len(results['broken_workflows'])}")
    print(f"Legacy Workflows: {len(results['legacy_workflows'])}")
    print(f"API Manager Usage: {len(results['api_manager_usage'])}")
    print(f"Valid Percentage: {results['statistics']['valid_percentage']:.1f}%")
    print(f"API Manager Percentage: {results['statistics']['api_manager_percentage']:.1f}%")
    
    if results["recommendations"]:
        print("\n🎯 RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()