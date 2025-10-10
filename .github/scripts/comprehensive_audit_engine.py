#!/usr/bin/env python3
"""
Comprehensive Audit Engine - Advanced System Health Monitoring
"""

import argparse
import json
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

class ComprehensiveAuditEngine:
    """Advanced comprehensive audit engine"""
    
    def __init__(self):
        """Initialize the audit engine"""
        self.results = {
            "audit_metadata": {},
            "workflow_audit": {},
            "api_key_audit": {},
            "legacy_audit": {},
            "security_audit": {},
            "performance_audit": {},
            "recommendations": [],
            "critical_issues": [],
            "statistics": {}
        }
    
    def run_comprehensive_audit(
        self, 
        audit_type: str, 
        create_issues: bool, 
        notify_on_failure: bool
    ) -> Dict[str, Any]:
        """Run comprehensive audit based on type"""
        print(f"🔍 Starting {audit_type} audit...")
        
        # Set audit metadata
        self.results["audit_metadata"] = {
            "audit_type": audit_type,
            "create_issues": create_issues,
            "notify_on_failure": notify_on_failure,
            "timestamp": str(os.popen('date').read().strip())
        }
        
        # Run audit based on type
        if audit_type in ["comprehensive", "triggers-only"]:
            self._audit_workflow_triggers()
        
        if audit_type in ["comprehensive", "api-keys-only"]:
            self._audit_api_key_usage()
        
        if audit_type in ["comprehensive", "legacy-only"]:
            self._audit_legacy_workflows()
        
        if audit_type in ["comprehensive", "security-only"]:
            self._audit_security_issues()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Calculate statistics
        self._calculate_statistics()
        
        return self.results
    
    def _audit_workflow_triggers(self):
        """Audit workflow triggers for duplicates and conflicts"""
        print("🔍 Auditing workflow triggers...")
        
        workflows_dir = Path('.github/workflows')
        all_workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        trigger_audit = {
            "total_workflows": len(all_workflows),
            "workflow_triggers": {},
            "duplicate_triggers": [],
            "conflicting_triggers": [],
            "trigger_statistics": {}
        }
        
        # Extract triggers from each workflow
        for workflow in all_workflows:
            try:
                with open(workflow, 'r') as f:
                    content = f.read()
                    yaml_data = yaml.safe_load(content)
                
                if yaml_data and 'on' in yaml_data:
                    triggers = yaml_data['on']
                    trigger_audit["workflow_triggers"][workflow.name] = triggers
                    
                    # Check for problematic patterns
                    if isinstance(triggers, dict):
                        for trigger_type, trigger_config in triggers.items():
                            if trigger_type == 'schedule' and isinstance(trigger_config, list):
                                for schedule in trigger_config:
                                    if 'cron' in schedule:
                                        cron = schedule['cron']
                                        # Check for frequent schedules that might conflict
                                        if cron.startswith('*/5') or cron.startswith('*/10'):
                                            trigger_audit["conflicting_triggers"].append({
                                                "workflow": workflow.name,
                                                "trigger": trigger_type,
                                                "schedule": cron,
                                                "issue": "Very frequent schedule may cause conflicts"
                                            })
            
            except Exception as e:
                print(f"❌ Error processing {workflow.name}: {e}")
                trigger_audit["conflicting_triggers"].append({
                    "workflow": workflow.name,
                    "trigger": "parse_error",
                    "issue": f"YAML parsing error: {e}"
                })
        
        # Find duplicate triggers
        all_trigger_events = []
        for workflow, triggers in trigger_audit["workflow_triggers"].items():
            if isinstance(triggers, dict):
                for trigger_type in triggers.keys():
                    all_trigger_events.append(f"{workflow}:{trigger_type}")
            elif isinstance(triggers, list):
                for trigger in triggers:
                    all_trigger_events.append(f"{workflow}:{trigger}")
            else:
                all_trigger_events.append(f"{workflow}:{triggers}")
        
        # Count duplicates
        from collections import Counter
        trigger_counts = Counter(all_trigger_events)
        duplicates = {k: v for k, v in trigger_counts.items() if v > 1}
        
        for trigger, count in duplicates.items():
            trigger_audit["duplicate_triggers"].append({
                "trigger": trigger,
                "count": count,
                "workflows": [t for t in all_trigger_events if t == trigger]
            })
        
        # Calculate statistics
        trigger_audit["trigger_statistics"] = {
            "total_triggers": len(all_trigger_events),
            "unique_triggers": len(set(all_trigger_events)),
            "duplicate_count": len(duplicates),
            "conflict_count": len(trigger_audit["conflicting_triggers"])
        }
        
        self.results["workflow_audit"] = trigger_audit
        print(f"✅ Workflow trigger audit completed: {len(duplicates)} duplicates, {len(trigger_audit['conflicting_triggers'])} conflicts")
    
    def _audit_api_key_usage(self):
        """Audit API key usage for direct access bypassing manager"""
        print("🔍 Auditing API key usage...")
        
        api_audit = {
            "direct_usage": [],
            "manager_usage": [],
            "missing_manager": [],
            "security_issues": [],
            "statistics": {}
        }
        
        # API key patterns to search for
        api_key_patterns = [
            r'os\.environ\[[\'"]?(DEEPSEEK|CLAUDE|GPT4|GLM|GROK|KIMI|QWEN|GEMINI|GPTOSS|GROQAI|CEREBRAS|GEMINIAI|COHERE|NVIDIA|CODESTRAL|GEMINI2|GROQ2|CHUTES)_API_KEY[\'"]?\]',
            r'getenv\([\'"]?(DEEPSEEK|CLAUDE|GPT4|GLM|GROK|KIMI|QWEN|GEMINI|GPTOSS|GROQAI|CEREBRAS|GEMINIAI|COHERE|NVIDIA|CODESTRAL|GEMINI2|GROQ2|CHUTES)_API_KEY[\'"]?\)',
            r'secrets\.(DEEPSEEK|CLAUDE|GPT4|GLM|GROK|KIMI|QWEN|GEMINI|GPTOSS|GROQAI|CEREBRAS|GEMINIAI|COHERE|NVIDIA|CODESTRAL|GEMINI2|GROQ2|CHUTES)_API_KEY'
        ]
        
        # Directories to search
        search_dirs = ['.github/scripts', '.github/workflows', 'scripts', 'src', 'app']
        
        for search_dir in search_dirs:
            if Path(search_dir).exists():
                for file_path in Path(search_dir).rglob('*.py'):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Check for direct API key usage
                        for pattern in api_key_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                api_audit["direct_usage"].append({
                                    "file": str(file_path),
                                    "pattern": pattern,
                                    "matches": matches,
                                    "line_numbers": self._get_line_numbers(content, pattern)
                                })
                        
                        # Check for manager usage
                        if any(indicator in content for indicator in [
                            'universal_ai_workflow_integration',
                            'standalone_universal_ai_manager',
                            'get_integration',
                            'generate_workflow_ai_response',
                            '--use-advanced-manager'
                        ]):
                            api_audit["manager_usage"].append(str(file_path))
                    
                    except Exception as e:
                        print(f"❌ Error processing {file_path}: {e}")
        
        # Check workflows for API key usage
        workflows_dir = Path('.github/workflows')
        for workflow in workflows_dir.glob("*.yml"):
            try:
                with open(workflow, 'r') as f:
                    content = f.read()
                
                # Check for API key environment variables
                api_key_vars = re.findall(r'(\w+_API_KEY):', content)
                if api_key_vars:
                    if '--use-advanced-manager' not in content:
                        api_audit["missing_manager"].append({
                            "workflow": workflow.name,
                            "api_keys": api_key_vars,
                            "issue": "Uses API keys but not advanced manager"
                        })
                    else:
                        api_audit["manager_usage"].append(str(workflow))
            
            except Exception as e:
                print(f"❌ Error processing {workflow}: {e}")
        
        # Calculate statistics
        api_audit["statistics"] = {
            "direct_usage_count": len(api_audit["direct_usage"]),
            "manager_usage_count": len(api_audit["manager_usage"]),
            "missing_manager_count": len(api_audit["missing_manager"]),
            "security_issues_count": len(api_audit["security_issues"])
        }
        
        self.results["api_key_audit"] = api_audit
        print(f"✅ API key audit completed: {len(api_audit['direct_usage'])} direct usage, {len(api_audit['missing_manager'])} missing manager")
    
    def _audit_legacy_workflows(self):
        """Audit for legacy and stub workflows"""
        print("🔍 Auditing legacy workflows...")
        
        legacy_audit = {
            "stub_workflows": [],
            "legacy_workflows": [],
            "minimal_workflows": [],
            "broken_workflows": [],
            "statistics": {}
        }
        
        workflows_dir = Path('.github/workflows')
        all_workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        for workflow in all_workflows:
            try:
                with open(workflow, 'r') as f:
                    content = f.read()
                    yaml_data = yaml.safe_load(content)
                
                if not yaml_data:
                    legacy_audit["broken_workflows"].append({
                        "workflow": workflow.name,
                        "issue": "Empty or invalid YAML"
                    })
                    continue
                
                # Check for stub workflows (minimal jobs/steps)
                if 'jobs' in yaml_data:
                    job_count = len(yaml_data['jobs'])
                    if job_count <= 1:
                        # Check steps in the job
                        for job_name, job_config in yaml_data['jobs'].items():
                            if 'steps' in job_config:
                                step_count = len(job_config['steps'])
                                if step_count <= 2:
                                    legacy_audit["stub_workflows"].append({
                                        "workflow": workflow.name,
                                        "job": job_name,
                                        "job_count": job_count,
                                        "step_count": step_count,
                                        "issue": "Minimal workflow with very few steps"
                                    })
                
                # Check for legacy patterns
                legacy_patterns = [
                    'enhanced-ai', 'universal-ai', 'multi-agent', 'comprehensive-ai',
                    'ultimate', 'simple', 'minimal', 'test-ai', 'old-', 'deprecated-'
                ]
                
                if any(pattern in workflow.name.lower() for pattern in legacy_patterns):
                    legacy_audit["legacy_workflows"].append({
                        "workflow": workflow.name,
                        "pattern": next(p for p in legacy_patterns if p in workflow.name.lower()),
                        "issue": "Contains legacy naming pattern"
                    })
                
                # Check for minimal content
                if len(content) < 500:  # Very small workflow file
                    legacy_audit["minimal_workflows"].append({
                        "workflow": workflow.name,
                        "size": len(content),
                        "issue": "Very small workflow file"
                    })
            
            except Exception as e:
                legacy_audit["broken_workflows"].append({
                    "workflow": workflow.name,
                    "error": str(e),
                    "issue": "YAML parsing error"
                })
        
        # Calculate statistics
        legacy_audit["statistics"] = {
            "total_workflows": len(all_workflows),
            "stub_count": len(legacy_audit["stub_workflows"]),
            "legacy_count": len(legacy_audit["legacy_workflows"]),
            "minimal_count": len(legacy_audit["minimal_workflows"]),
            "broken_count": len(legacy_audit["broken_workflows"])
        }
        
        self.results["legacy_audit"] = legacy_audit
        print(f"✅ Legacy audit completed: {len(legacy_audit['stub_workflows'])} stubs, {len(legacy_audit['legacy_workflows'])} legacy")
    
    def _audit_security_issues(self):
        """Audit for security issues"""
        print("🔍 Auditing security issues...")
        
        security_audit = {
            "exposed_secrets": [],
            "insecure_patterns": [],
            "vulnerable_dependencies": [],
            "permission_issues": [],
            "statistics": {}
        }
        
        # Check for exposed secrets in code
        secret_patterns = [
            r'["\'](sk-[a-zA-Z0-9]{20,})["\']',  # OpenAI API keys
            r'["\'](pk_[a-zA-Z0-9]{20,})["\']',  # OpenAI API keys
            r'["\']([a-zA-Z0-9]{32,})["\']',     # Generic long keys
            r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
            r'token\s*=\s*["\'][^"\']+["\']'     # Hardcoded tokens
        ]
        
        for file_path in Path('.').rglob('*.py'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_audit["exposed_secrets"].append({
                            "file": str(file_path),
                            "pattern": pattern,
                            "matches": matches[:3],  # Limit to first 3 matches
                            "line_numbers": self._get_line_numbers(content, pattern)
                        })
            
            except Exception as e:
                print(f"❌ Error checking {file_path}: {e}")
        
        # Check for insecure patterns
        insecure_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'pickle\.loads?\s*\('
        ]
        
        for file_path in Path('.').rglob('*.py'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for pattern in insecure_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        security_audit["insecure_patterns"].append({
                            "file": str(file_path),
                            "pattern": pattern,
                            "matches": matches,
                            "line_numbers": self._get_line_numbers(content, pattern)
                        })
            
            except Exception as e:
                print(f"❌ Error checking {file_path}: {e}")
        
        # Calculate statistics
        security_audit["statistics"] = {
            "exposed_secrets_count": len(security_audit["exposed_secrets"]),
            "insecure_patterns_count": len(security_audit["insecure_patterns"]),
            "vulnerable_dependencies_count": len(security_audit["vulnerable_dependencies"]),
            "permission_issues_count": len(security_audit["permission_issues"])
        }
        
        self.results["security_audit"] = security_audit
        print(f"✅ Security audit completed: {len(security_audit['exposed_secrets'])} exposed secrets, {len(security_audit['insecure_patterns'])} insecure patterns")
    
    def _get_line_numbers(self, content: str, pattern: str) -> List[int]:
        """Get line numbers where pattern matches"""
        lines = content.split('\n')
        line_numbers = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                line_numbers.append(i)
        return line_numbers
    
    def _generate_recommendations(self):
        """Generate recommendations based on audit findings"""
        recommendations = []
        
        # Workflow recommendations
        if self.results["workflow_audit"].get("duplicate_triggers"):
            recommendations.append({
                "category": "workflow",
                "priority": "high",
                "title": "Consolidate Duplicate Workflow Triggers",
                "description": f"Found {len(self.results['workflow_audit']['duplicate_triggers'])} duplicate triggers that may cause conflicts",
                "action": "Review and consolidate duplicate triggers to prevent resource conflicts"
            })
        
        # API key recommendations
        if self.results["api_key_audit"].get("direct_usage"):
            recommendations.append({
                "category": "api_keys",
                "priority": "critical",
                "title": "Migrate Direct API Key Usage to Manager",
                "description": f"Found {len(self.results['api_key_audit']['direct_usage'])} instances of direct API key usage",
                "action": "Replace direct API key usage with centralized manager for better failover"
            })
        
        # Legacy workflow recommendations
        if self.results["legacy_audit"].get("stub_workflows"):
            recommendations.append({
                "category": "legacy",
                "priority": "medium",
                "title": "Remove Stub Workflows",
                "description": f"Found {len(self.results['legacy_audit']['stub_workflows'])} stub workflows",
                "action": "Remove or consolidate stub workflows to reduce maintenance overhead"
            })
        
        # Security recommendations
        if self.results["security_audit"].get("exposed_secrets"):
            recommendations.append({
                "category": "security",
                "priority": "critical",
                "title": "Remove Exposed Secrets",
                "description": f"Found {len(self.results['security_audit']['exposed_secrets'])} exposed secrets",
                "action": "Remove hardcoded secrets and use environment variables or secrets management"
            })
        
        self.results["recommendations"] = recommendations
        
        # Identify critical issues
        critical_issues = [r for r in recommendations if r["priority"] == "critical"]
        self.results["critical_issues"] = critical_issues
    
    def _calculate_statistics(self):
        """Calculate overall audit statistics"""
        stats = {
            "total_issues": 0,
            "critical_issues": len(self.results["critical_issues"]),
            "high_priority_issues": 0,
            "medium_priority_issues": 0,
            "low_priority_issues": 0,
            "workflow_issues": 0,
            "api_key_issues": 0,
            "legacy_issues": 0,
            "security_issues": 0
        }
        
        # Count issues by priority
        for rec in self.results["recommendations"]:
            stats["total_issues"] += 1
            if rec["priority"] == "high":
                stats["high_priority_issues"] += 1
            elif rec["priority"] == "medium":
                stats["medium_priority_issues"] += 1
            elif rec["priority"] == "low":
                stats["low_priority_issues"] += 1
            
            # Count by category
            if rec["category"] == "workflow":
                stats["workflow_issues"] += 1
            elif rec["category"] == "api_keys":
                stats["api_key_issues"] += 1
            elif rec["category"] == "legacy":
                stats["legacy_issues"] += 1
            elif rec["category"] == "security":
                stats["security_issues"] += 1
        
        self.results["statistics"] = stats

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive Audit Engine")
    parser.add_argument("--audit-type", default="comprehensive", help="Audit type")
    parser.add_argument("--create-issues", default="true", help="Create issues for problems")
    parser.add_argument("--notify-on-failure", default="true", help="Notify on critical failures")
    parser.add_argument("--output", default="comprehensive_audit_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Convert string booleans
    create_issues = args.create_issues.lower() == 'true'
    notify_on_failure = args.notify_on_failure.lower() == 'true'
    
    # Create audit engine
    engine = ComprehensiveAuditEngine()
    
    # Run audit
    results = engine.run_comprehensive_audit(
        audit_type=args.audit_type,
        create_issues=create_issues,
        notify_on_failure=notify_on_failure
    )
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 80)
    
    stats = results["statistics"]
    print(f"Total Issues: {stats['total_issues']}")
    print(f"Critical Issues: {stats['critical_issues']}")
    print(f"High Priority: {stats['high_priority_issues']}")
    print(f"Medium Priority: {stats['medium_priority_issues']}")
    print(f"Low Priority: {stats['low_priority_issues']}")
    print()
    
    print("📋 ISSUES BY CATEGORY:")
    print(f"  Workflow: {stats['workflow_issues']}")
    print(f"  API Keys: {stats['api_key_issues']}")
    print(f"  Legacy: {stats['legacy_issues']}")
    print(f"  Security: {stats['security_issues']}")
    print()
    
    if results["recommendations"]:
        print("🎯 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"][:5], 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['title']}")
    
    print("=" * 80)
    
    # Exit with error code if critical issues found
    if stats['critical_issues'] > 0:
        print("❌ CRITICAL ISSUES FOUND - Review required!")
        return 1
    else:
        print("✅ Audit completed successfully!")
        return 0

if __name__ == "__main__":
    exit(main())