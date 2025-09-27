#!/usr/bin/env python3
"""
Enhanced Workflow Orchestrator Script
Orchestrates all AI workflows and handles integration issues
"""

import os
import json
import requests
import subprocess
from openai import OpenAI
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class EnhancedWorkflowOrchestrator:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER')
        
        # Initialize AI clients
        self.ai_clients = {}
        if self.openrouter_key:
            self.ai_clients['openrouter'] = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
            )
        if self.deepseek_key:
            self.ai_clients['deepseek'] = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=self.deepseek_key,
            )
    
    def check_workflow_health(self) -> Dict[str, Any]:
        """Check the health of all workflows"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'api_keys_available': {},
            'workflow_status': {},
            'recommendations': []
        }
        
        # Check API key availability
        health_status['api_keys_available'] = {
            'github_token': bool(self.github_token),
            'openrouter_key': bool(self.openrouter_key),
            'deepseek_key': bool(self.deepseek_key),
            'glm_key': bool(self.glm_key),
            'grok_key': bool(self.grok_key)
        }
        
        # Check workflow files
        workflow_files = [
            '.github/workflows/ai-code-analysis.yml',
            '.github/workflows/ai-issue-responder.yml',
            '.github/workflows/enhanced-ai-integration.yml',
            '.github/workflows/comprehensive-ai-workflow.yml',
            '.github/workflows/multi-agent-workflow.yml',
            '.github/workflows/workflow-status-monitor.yml'
        ]
        
        for workflow_file in workflow_files:
            if os.path.exists(workflow_file):
                health_status['workflow_status'][workflow_file] = 'exists'
            else:
                health_status['workflow_status'][workflow_file] = 'missing'
                health_status['recommendations'].append(f"Create missing workflow: {workflow_file}")
        
        # Check script files
        script_files = [
            '.github/scripts/ai_code_analyzer.py',
            '.github/scripts/ai_issue_responder.py',
            '.github/scripts/ai_security_scanner.py',
            '.github/scripts/comprehensive_security_scanner.py',
            '.github/scripts/performance_analyzer.py',
            '.github/scripts/issue_resolution_integrator.py',
            '.github/scripts/workflow_status_checker.py',
            '.github/scripts/multi_agent_orchestrator.py'
        ]
        
        for script_file in script_files:
            if os.path.exists(script_file):
                health_status['workflow_status'][script_file] = 'exists'
            else:
                health_status['workflow_status'][script_file] = 'missing'
                health_status['recommendations'].append(f"Create missing script: {script_file}")
        
        # Generate recommendations
        if not any(health_status['api_keys_available'].values()):
            health_status['recommendations'].append("Configure at least one API key for AI functionality")
        
        if not health_status['api_keys_available']['github_token']:
            health_status['recommendations'].append("Configure GITHUB_TOKEN for GitHub API access")
        
        return health_status
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis using all available tools"""
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'issue_analysis': None,
            'code_analysis': None,
            'security_analysis': None,
            'performance_analysis': None,
            'multi_agent_analysis': None,
            'integration_status': {}
        }
        
        print("🔍 Running comprehensive analysis...")
        
        # Issue Analysis
        if self.issue_number:
            print("📝 Running issue analysis...")
            try:
                result = subprocess.run([
                    'python', '.github/scripts/ai_issue_responder.py'
                ], capture_output=True, text=True, timeout=60)
                analysis_results['issue_analysis'] = {
                    'status': 'completed' if result.returncode == 0 else 'failed',
                    'output': result.stdout,
                    'error': result.stderr
                }
            except Exception as e:
                analysis_results['issue_analysis'] = {'status': 'error', 'error': str(e)}
        
        # Code Analysis
        print("🔍 Running code analysis...")
        try:
            result = subprocess.run([
                'python', '.github/scripts/ai_code_analyzer.py'
            ], capture_output=True, text=True, timeout=60)
            analysis_results['code_analysis'] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            analysis_results['code_analysis'] = {'status': 'error', 'error': str(e)}
        
        # Security Analysis
        print("🔒 Running security analysis...")
        try:
            result = subprocess.run([
                'python', '.github/scripts/comprehensive_security_scanner.py'
            ], capture_output=True, text=True, timeout=120)
            analysis_results['security_analysis'] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            analysis_results['security_analysis'] = {'status': 'error', 'error': str(e)}
        
        # Performance Analysis
        print("⚡ Running performance analysis...")
        try:
            result = subprocess.run([
                'python', '.github/scripts/performance_analyzer.py'
            ], capture_output=True, text=True, timeout=60)
            analysis_results['performance_analysis'] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            analysis_results['performance_analysis'] = {'status': 'error', 'error': str(e)}
        
        # Multi-Agent Analysis
        print("🤖 Running multi-agent analysis...")
        try:
            result = subprocess.run([
                'python', '.github/scripts/multi_agent_orchestrator.py'
            ], capture_output=True, text=True, timeout=120)
            analysis_results['multi_agent_analysis'] = {
                'status': 'completed' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            analysis_results['multi_agent_analysis'] = {'status': 'error', 'error': str(e)}
        
        return analysis_results
    
    def generate_integration_report(self, health_status: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive integration report"""
        report = ["# 🚀 Enhanced Workflow Integration Report\n"]
        
        # Header
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Repository**: {self.repo_name}")
        report.append("")
        
        # Health Status
        report.append("## 🔍 Workflow Health Status")
        report.append("### API Keys Available")
        for key, available in health_status['api_keys_available'].items():
            status = "✅" if available else "❌"
            report.append(f"- {status} {key}")
        report.append("")
        
        # Workflow Status
        report.append("### Workflow Files Status")
        for file, status in health_status['workflow_status'].items():
            status_emoji = "✅" if status == 'exists' else "❌"
            report.append(f"- {status_emoji} {file}")
        report.append("")
        
        # Analysis Results
        report.append("## 📊 Analysis Results")
        for analysis_type, result in analysis_results.items():
            if analysis_type == 'timestamp':
                continue
            
            if isinstance(result, dict) and 'status' in result:
                status_emoji = "✅" if result['status'] == 'completed' else "❌"
                report.append(f"- {status_emoji} {analysis_type.replace('_', ' ').title()}: {result['status']}")
            else:
                report.append(f"- ℹ️ {analysis_type.replace('_', ' ').title()}: {type(result).__name__}")
        report.append("")
        
        # Recommendations
        if health_status['recommendations']:
            report.append("## 💡 Recommendations")
            for i, recommendation in enumerate(health_status['recommendations'], 1):
                report.append(f"{i}. {recommendation}")
            report.append("")
        
        # Integration Status
        report.append("## 🔗 Integration Status")
        
        # Check if all components are working
        all_working = all(
            result.get('status') == 'completed' 
            for result in analysis_results.values() 
            if isinstance(result, dict) and 'status' in result
        )
        
        if all_working:
            report.append("✅ **All AI workflows are integrated and functioning correctly**")
        else:
            report.append("⚠️ **Some workflows need attention**")
            report.append("- Review failed analyses above")
            report.append("- Check error messages for troubleshooting")
            report.append("- Ensure all dependencies are installed")
        
        # Next Steps
        report.append("\n## 🎯 Next Steps")
        report.append("1. **Review Analysis Results**: Check all generated reports")
        report.append("2. **Address Issues**: Fix any problems identified in the analysis")
        report.append("3. **Monitor Performance**: Use the workflow status monitor")
        report.append("4. **Update Configuration**: Adjust settings based on results")
        report.append("5. **Test Integration**: Create test issues and PRs to verify functionality")
        
        return "\n".join(report)
    
    def post_integration_summary(self, report: str) -> bool:
        """Post integration summary to GitHub"""
        if not self.issue_number or not self.github_token:
            print("No issue number or GitHub token available, skipping post")
            return False
        
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/comments"
        
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        # Add AI signature
        ai_comment = f"""{report}

---
🤖 **AMAS Enhanced Workflow Orchestrator**
🔗 *Comprehensive AI workflow integration*
📊 *All systems analyzed and integrated*
"""
        
        data = {'body': ai_comment}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Posted integration summary to issue #{self.issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post integration summary: {e}")
            return False
    
    def run(self):
        """Main execution function"""
        print("🚀 Starting Enhanced Workflow Orchestrator...")
        
        # Check workflow health
        print("🔍 Checking workflow health...")
        health_status = self.check_workflow_health()
        
        # Run comprehensive analysis
        print("📊 Running comprehensive analysis...")
        analysis_results = self.run_comprehensive_analysis()
        
        # Generate integration report
        print("📝 Generating integration report...")
        report = self.generate_integration_report(health_status, analysis_results)
        
        # Save report
        with open('enhanced-integration-report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("📋 Enhanced Integration Report:")
        print(report)
        
        # Post summary if issue number is available
        if self.issue_number:
            self.post_integration_summary(report)
        
        print("✅ Enhanced Workflow Orchestrator completed successfully!")
        
        return {
            'health_status': health_status,
            'analysis_results': analysis_results,
            'report': report
        }

if __name__ == "__main__":
    orchestrator = EnhancedWorkflowOrchestrator()
    orchestrator.run()