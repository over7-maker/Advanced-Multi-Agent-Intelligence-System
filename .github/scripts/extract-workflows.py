#!/usr/bin/env python3
"""Professional Workflow Extraction Script - Phase 2"""

import os
import yaml
import json
import sys
from datetime import datetime

class WorkflowExtractor:
    """Extract and analyze workflows for consolidation"""
    
    CONSOLIDATION_MAP = {
        "00-master-orchestrator": [
            "00-ai-master-orchestrator.yml",
            "00-master-ai-orchestrator.yml",
        ],
        "01-ai-agents": [
            "01-ai-agentic-project-self-improver.yml",
            "02-ai-agentic-issue-auto-responder.yml",
            "ai-agentic-issue-auto-responder.yml",
        ],
        "02-audit-documentation": [
            "03-ai-agent-project-audit-documentation.yml",
            "ai-agent-project-audit-documentation.yml",
        ],
        "03-build-deploy": [
            "04-ai-enhanced-build-deploy.yml",
            "production-cicd.yml",
            "production-cicd-secure.yml",
        ],
        "04-security": ["05-ai-security-threat-intelligence.yml"],
        "05-quality": ["06-ai-code-quality-performance.yml"],
        "06-cicd-pipeline": ["07-ai-enhanced-cicd-pipeline.yml"],
        "07-governance": [
            "governance-ci.yml",
            "comprehensive-audit.yml",
            "workflow-audit-monitor.yml",
        ],
    }
    
    def __init__(self):
        self.workflows_dir = ".github/workflows"
        self.analysis_dir = ".github/analysis"
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def get_file_size(self, filename: str) -> float:
        """Get file size in KB"""
        try:
            path = os.path.join(self.workflows_dir, filename)
            return os.path.getsize(path) / 1024
        except:
            return 0
    
    def read_yaml_file(self, filename: str) -> dict:
        """Read YAML file safely"""
        try:
            path = os.path.join(self.workflows_dir, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
        except:
            pass
        return None
    
    def extract_jobs(self, workflow_files: list) -> tuple:
        """Extract all jobs from workflow files"""
        jobs = {}
        sources = []
        
        for wf_file in workflow_files:
            content = self.read_yaml_file(wf_file)
            if content and 'jobs' in content:
                jobs.update(content['jobs'])
                sources.append(wf_file)
        
        return jobs, sources
    
    def extract_env_vars(self, workflow_files: list) -> dict:
        """Extract environment variables"""
        env_vars = {}
        
        for wf_file in workflow_files:
            content = self.read_yaml_file(wf_file)
            if content and 'env' in content:
                env_vars.update(content['env'])
        
        return env_vars
    
    def analyze_consolidation_target(self, target_name: str, source_files: list) -> dict:
        """Analyze a consolidation target"""
        
        print(f"Processing: {target_name}")
        
        original_size = sum(self.get_file_size(f) for f in source_files)
        jobs, found_sources = self.extract_jobs(source_files)
        env_vars = self.extract_env_vars(source_files)
        
        print(f"  Size: {original_size:.1f} KB | Jobs: {len(jobs)} | Env: {len(env_vars)}")
        
        return {
            'name': target_name,
            'source_files': found_sources,
            'original_size_kb': original_size,
            'job_count': len(jobs),
            'jobs': list(jobs.keys()),
            'env_var_count': len(env_vars),
            'env_vars': list(env_vars.keys()),
        }
    
    def run_analysis(self):
        """Run complete analysis"""
        
        print("\n🔍 WORKFLOW EXTRACTION & ANALYSIS")
        print("=" * 60)
        print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target Workflows: 46")
        print(f"Consolidation Targets: 8\n")
        
        total_size = 0
        report = {}
        total_jobs = 0
        
        for target_name, source_files in self.CONSOLIDATION_MAP.items():
            analysis = self.analyze_consolidation_target(target_name, source_files)
            report[target_name] = analysis
            total_size += analysis['original_size_kb']
            total_jobs += analysis['job_count']
        
        # Save report
        with open(f"{self.analysis_dir}/workflow-extraction-report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"✅ EXTRACTION COMPLETE")
        print(f"Total size: {total_size:.1f} KB")
        print(f"Total jobs: {total_jobs}")
        print(f"Report saved to: .github/analysis/workflow-extraction-report.json")
        
        return report

if __name__ == "__main__":
    try:
        extractor = WorkflowExtractor()
        extractor.run_analysis()
        print("\n✅ Analysis complete!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
