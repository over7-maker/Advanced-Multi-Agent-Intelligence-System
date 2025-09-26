#!/usr/bin/env python3
"""
Workflow Status Checker Script
Monitors and reports on GitHub Actions workflow status
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class WorkflowStatusChecker:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo_name = os.environ.get('REPO_NAME', 'your-username/your-repo')
        
    def get_workflow_runs(self, workflow_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow runs"""
        url = f"https://api.github.com/repos/{self.repo_name}/actions/runs"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        params = {
            'per_page': limit,
            'status': 'all'  # Get all statuses
        }
        
        if workflow_name:
            params['event'] = workflow_name
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get('workflow_runs', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow runs: {e}")
            return []
    
    def get_workflow_details(self, run_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific workflow run"""
        url = f"https://api.github.com/repos/{self.repo_name}/actions/runs/{run_id}"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow details: {e}")
            return None
    
    def get_workflow_jobs(self, run_id: int) -> List[Dict[str, Any]]:
        """Get jobs for a specific workflow run"""
        url = f"https://api.github.com/repos/{self.repo_name}/actions/runs/{run_id}/jobs"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('jobs', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow jobs: {e}")
            return []
    
    def analyze_workflow_health(self, workflow_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workflow health and performance"""
        if not workflow_runs:
            return {"status": "no_data", "message": "No workflow runs found"}
        
        # Analyze recent runs
        recent_runs = workflow_runs[:5]  # Last 5 runs
        success_count = sum(1 for run in recent_runs if run['conclusion'] == 'success')
        failure_count = sum(1 for run in recent_runs if run['conclusion'] == 'failure')
        cancelled_count = sum(1 for run in recent_runs if run['conclusion'] == 'cancelled')
        
        # Calculate success rate
        total_completed = success_count + failure_count + cancelled_count
        success_rate = (success_count / total_completed * 100) if total_completed > 0 else 0
        
        # Check for recent failures
        recent_failures = [run for run in recent_runs if run['conclusion'] == 'failure']
        
        # Analyze timing
        run_times = []
        for run in recent_runs:
            if run['conclusion'] == 'success' and run['created_at'] and run['updated_at']:
                created = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                duration = (updated - created).total_seconds()
                run_times.append(duration)
        
        avg_duration = sum(run_times) / len(run_times) if run_times else 0
        
        return {
            "status": "healthy" if success_rate >= 80 else "needs_attention",
            "success_rate": round(success_rate, 1),
            "total_runs": len(recent_runs),
            "success_count": success_count,
            "failure_count": failure_count,
            "cancelled_count": cancelled_count,
            "avg_duration_seconds": round(avg_duration, 1),
            "recent_failures": recent_failures[:3]  # Last 3 failures
        }
    
    def generate_status_report(self, workflow_health: Dict[str, Any], workflow_runs: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive status report"""
        report = ["# 📊 GitHub Actions Workflow Status Report\n"]
        
        # Overall health
        status_emoji = "✅" if workflow_health["status"] == "healthy" else "⚠️"
        report.append(f"## {status_emoji} Overall Status: {workflow_health['status'].upper()}\n")
        
        # Statistics
        report.append("### 📈 Statistics")
        report.append(f"- **Success Rate**: {workflow_health['success_rate']}%")
        report.append(f"- **Total Recent Runs**: {workflow_health['total_runs']}")
        report.append(f"- **Successful**: {workflow_health['success_count']}")
        report.append(f"- **Failed**: {workflow_health['failure_count']}")
        report.append(f"- **Cancelled**: {workflow_health['cancelled_count']}")
        report.append(f"- **Average Duration**: {workflow_health['avg_duration_seconds']}s\n")
        
        # Recent failures
        if workflow_health['recent_failures']:
            report.append("### ❌ Recent Failures")
            for failure in workflow_health['recent_failures']:
                created_at = failure['created_at'][:19].replace('T', ' ')
                report.append(f"- **Run #{failure['run_number']}** ({created_at}): {failure['conclusion']}")
                report.append(f"  - Workflow: {failure['name']}")
                report.append(f"  - Trigger: {failure['event']}")
                report.append(f"  - URL: {failure['html_url']}")
            report.append("")
        
        # Recent successful runs
        recent_successes = [run for run in workflow_runs[:3] if run['conclusion'] == 'success']
        if recent_successes:
            report.append("### ✅ Recent Successes")
            for success in recent_successes:
                created_at = success['created_at'][:19].replace('T', ' ')
                report.append(f"- **Run #{success['run_number']}** ({created_at}): {success['name']}")
            report.append("")
        
        # Recommendations
        report.append("### 💡 Recommendations")
        if workflow_health['success_rate'] < 80:
            report.append("- ⚠️ **Low success rate detected** - Review recent failures")
            report.append("- 🔍 **Check workflow logs** for error patterns")
            report.append("- 🛠️ **Update dependencies** if needed")
        else:
            report.append("- ✅ **Workflows are running well**")
            report.append("- 📊 **Monitor performance** for optimization opportunities")
        
        report.append("- 🔄 **Regular monitoring** recommended")
        report.append("- 📝 **Update documentation** if workflow changes")
        
        return "\n".join(report)
    
    def check_specific_workflows(self) -> Dict[str, Any]:
        """Check status of specific AI workflows"""
        workflows_to_check = [
            'ai-code-analysis.yml',
            'ai-issue-responder.yml', 
            'enhanced-ai-integration.yml',
            'multi-agent-workflow.yml'
        ]
        
        results = {}
        
        for workflow_name in workflows_to_check:
            print(f"Checking {workflow_name}...")
            runs = self.get_workflow_runs(workflow_name, limit=5)
            health = self.analyze_workflow_health(runs)
            results[workflow_name] = {
                'health': health,
                'recent_runs': runs[:3]  # Last 3 runs
            }
        
        return results
    
    def run(self):
        """Main execution function"""
        print("🔍 Checking GitHub Actions workflow status...")
        
        # Get recent workflow runs
        all_runs = self.get_workflow_runs(limit=20)
        
        if not all_runs:
            print("❌ No workflow runs found or API access denied")
            return
        
        # Analyze overall health
        overall_health = self.analyze_workflow_health(all_runs)
        
        # Generate status report
        report = self.generate_status_report(overall_health, all_runs)
        
        # Check specific workflows
        specific_results = self.check_specific_workflows()
        
        # Add specific workflow results to report
        report += "\n## 🔧 Specific Workflow Status\n"
        for workflow_name, result in specific_results.items():
            status_emoji = "✅" if result['health']['status'] == 'healthy' else "⚠️"
            report += f"\n### {status_emoji} {workflow_name}\n"
            report += f"- Status: {result['health']['status']}\n"
            report += f"- Success Rate: {result['health']['success_rate']}%\n"
            report += f"- Recent Runs: {len(result['recent_runs'])}\n"
        
        # Output report
        print("\n" + "="*60)
        print(report)
        print("="*60)
        
        # Save report to file
        with open('workflow_status_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: workflow_status_report.md")
        
        return overall_health

if __name__ == "__main__":
    checker = WorkflowStatusChecker()
    checker.run()