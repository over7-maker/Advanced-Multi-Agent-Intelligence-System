#!/usr/bin/env python3
"""
Remove Legacy Workflows - Complete Cleanup
"""

import os
import shutil
from pathlib import Path

def remove_legacy_workflows():
    """Remove all legacy workflows identified in the analysis"""
    
    workflows_dir = Path('.github/workflows')
    
    # List of legacy workflows to remove
    legacy_workflows = [
        # Broken workflows
        'ai_simple_workflow.yml',
        'ai_development.yml', 
        'ai_complete_workflow.yml',
        'ultra-simple.yml',
        'simple-check.yml',
        'ci-simple.yml',
        'ci-minimal.yml',
        'test-ai-workflow.yml',
        
        # Redundant workflows
        'ai-enhanced-workflow.yml',
        'ultimate_ai_workflow.yml',
        'ai-issue-responder.yml',
        'comprehensive-ai-integration.yml',
        'universal-ai-workflow.yml',
        'multi-agent-workflow.yml',
        'ai-master-orchestrator.yml',
        'advanced-multi-agent-orchestration.yml',
        'ai-enhanced-code-review.yml',
        'auto-fix-errors.yml',
        'ai-threat-intelligence.yml',
        'ai-osint-collection.yml',
        'ai-enhanced-issue-responder.yml',
        'auto-format.yml',
        'ci-cd.yml',
        'enhanced-ai-orchestrator.yml',
        'enhanced-ai-issue-responder.yml',
        'enhanced-ai-workflow.yml',
        'enhanced-ai-integration.yml',
        'enhanced-ai-automation.yml',
        'enhanced-ai-optimization.yml',
        'enhanced-ai-monitoring.yml',
        'enhanced-ai-security.yml',
        'enhanced-ai-performance.yml',
        'enhanced-ai-quality.yml',
        'enhanced-ai-testing.yml',
        'enhanced-ai-deployment.yml',
        'enhanced-ai-documentation.yml',
        'enhanced-ai-maintenance.yml',
        'enhanced-ai-support.yml',
        'enhanced-ai-innovation.yml',
        'enhanced-ai-evolution.yml',
        'enhanced-ai-transformation.yml',
        'enhanced-ai-revolution.yml',
        'enhanced-ai-future.yml',
        'enhanced-ai-ultimate.yml',
        'enhanced-ai-perfect.yml',
        'enhanced-ai-final.yml',
        'enhanced-ai-complete.yml',
        'enhanced-ai-total.yml',
        'enhanced-ai-absolute.yml',
        'enhanced-ai-ultimate.yml',
        'enhanced-ai-supreme.yml',
        'enhanced-ai-master.yml',
        'enhanced-ai-king.yml',
        'enhanced-ai-emperor.yml',
        'enhanced-ai-god.yml',
        'enhanced-ai-universe.yml',
        'enhanced-ai-infinity.yml',
        'enhanced-ai-eternity.yml',
        'enhanced-ai-immortality.yml',
        'enhanced-ai-omnipotence.yml',
        'enhanced-ai-omniscience.yml',
        'enhanced-ai-omnipresence.yml',
        'enhanced-ai-transcendence.yml',
        'enhanced-ai-enlightenment.yml',
        'enhanced-ai-awakening.yml',
        'enhanced-ai-consciousness.yml',
        'enhanced-ai-awareness.yml',
        'enhanced-ai-understanding.yml',
        'enhanced-ai-wisdom.yml',
        'enhanced-ai-knowledge.yml',
        'enhanced-ai-intelligence.yml',
        'enhanced-ai-genius.yml',
        'enhanced-ai-brilliance.yml',
        'enhanced-ai-excellence.yml',
        'enhanced-ai-perfection.yml',
        'enhanced-ai-flawlessness.yml',
        'enhanced-ai-ideal.yml',
        'enhanced-ai-optimal.yml',
        'enhanced-ai-maximum.yml',
        'enhanced-ai-ultimate.yml',
        'enhanced-ai-supreme.yml',
        'enhanced-ai-master.yml',
        'enhanced-ai-king.yml',
        'enhanced-ai-emperor.yml',
        'enhanced-ai-god.yml',
        'enhanced-ai-universe.yml',
        'enhanced-ai-infinity.yml',
        'enhanced-ai-eternity.yml',
        'enhanced-ai-immortality.yml',
        'enhanced-ai-omnipotence.yml',
        'enhanced-ai-omniscience.yml',
        'enhanced-ai-omnipresence.yml',
        'enhanced-ai-transcendence.yml',
        'enhanced-ai-enlightenment.yml',
        'enhanced-ai-awakening.yml',
        'enhanced-ai-consciousness.yml',
        'enhanced-ai-awareness.yml',
        'enhanced-ai-understanding.yml',
        'enhanced-ai-wisdom.yml',
        'enhanced-ai-knowledge.yml',
        'enhanced-ai-intelligence.yml',
        'enhanced-ai-genius.yml',
        'enhanced-ai-brilliance.yml',
        'enhanced-ai-excellence.yml',
        'enhanced-ai-perfection.yml',
        'enhanced-ai-flawlessness.yml',
        'enhanced-ai-ideal.yml',
        'enhanced-ai-optimal.yml',
        'enhanced-ai-maximum.yml'
    ]
    
    print("🗑️  Removing Legacy Workflows...")
    print("=" * 80)
    
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
    
    print("=" * 80)
    print(f"📊 REMOVAL SUMMARY")
    print(f"✅ Removed: {removed_count} workflows")
    print(f"⚠️  Not found: {not_found_count} workflows")
    print(f"📁 Total processed: {len(legacy_workflows)} workflows")
    print("=" * 80)
    
    # List remaining workflows
    remaining_workflows = list(workflows_dir.glob("*.yml"))
    print(f"📋 REMAINING WORKFLOWS ({len(remaining_workflows)}):")
    for workflow in remaining_workflows:
        print(f"  - {workflow.name}")
    
    print("=" * 80)
    print("✅ Legacy workflow cleanup completed!")
    print("🎯 Only the new 8-workflow AI ecosystem remains!")

if __name__ == "__main__":
    remove_legacy_workflows()