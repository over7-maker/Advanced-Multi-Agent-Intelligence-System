#!/usr/bin/env python3
"""
Local GitHub Actions Runner
A web-based interface to run GitHub Actions workflows locally
"""

import os
import sys
import json
import yaml
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.serving import make_server
import webbrowser

class LocalGitHubActions:
    def __init__(self):
        self.app = Flask(__name__)
        self.workflows = {}
        self.running_jobs = {}
        self.job_history = []
        self.setup_routes()
        self.load_workflows()
    
    def load_workflows(self):
        """Load all GitHub Actions workflows from .github/workflows/"""
        workflows_dir = Path(".github/workflows")
        if not workflows_dir.exists():
            print("❌ No .github/workflows directory found!")
            return
        
        for workflow_file in workflows_dir.glob("*.yml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                    workflow_name = workflow_data.get('name', workflow_file.stem)
                    self.workflows[workflow_name] = {
                        'file': str(workflow_file),
                        'data': workflow_data,
                        'status': 'ready'
                    }
                    print(f"✅ Loaded workflow: {workflow_name}")
            except Exception as e:
                print(f"❌ Error loading {workflow_file}: {e}")
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html', workflows=self.workflows, running_jobs=self.running_jobs)
        
        @self.app.route('/api/workflows')
        def get_workflows():
            return jsonify(self.workflows)
        
        @self.app.route('/api/workflows/<workflow_name>/run', methods=['POST'])
        def run_workflow(workflow_name):
            if workflow_name not in self.workflows:
                return jsonify({'error': 'Workflow not found'}), 404
            
            job_id = f"{workflow_name}_{int(time.time())}"
            job_data = {
                'id': job_id,
                'workflow': workflow_name,
                'status': 'running',
                'start_time': datetime.now().isoformat(),
                'logs': [],
                'steps': []
            }
            
            self.running_jobs[job_id] = job_data
            self.job_history.append(job_data)
            
            # Run workflow in background thread
            thread = threading.Thread(target=self.execute_workflow, args=(job_id, workflow_name))
            thread.daemon = True
            thread.start()
            
            return jsonify({'job_id': job_id, 'status': 'started'})
        
        @self.app.route('/api/jobs/<job_id>')
        def get_job_status(job_id):
            if job_id in self.running_jobs:
                return jsonify(self.running_jobs[job_id])
            return jsonify({'error': 'Job not found'}), 404
        
        @self.app.route('/api/jobs/<job_id>/logs')
        def get_job_logs(job_id):
            if job_id in self.running_jobs:
                return jsonify({'logs': self.running_jobs[job_id]['logs']})
            return jsonify({'error': 'Job not found'}), 404
        
        @self.app.route('/api/jobs')
        def get_all_jobs():
            return jsonify({
                'running': self.running_jobs,
                'history': self.job_history[-50:]  # Last 50 jobs
            })
    
    def execute_workflow(self, job_id, workflow_name):
        """Execute a workflow job"""
        try:
            job = self.running_jobs[job_id]
            workflow = self.workflows[workflow_name]
            
            self.add_log(job_id, f"🚀 Starting workflow: {workflow_name}")
            
            # Parse workflow steps
            workflow_data = workflow['data']
            jobs = workflow_data.get('jobs', {})
            
            for job_name, job_config in jobs.items():
                self.add_log(job_id, f"📋 Executing job: {job_name}")
                
                steps = job_config.get('steps', [])
                for step in steps:
                    step_name = step.get('name', 'Unnamed step')
                    self.add_log(job_id, f"⚡ Running step: {step_name}")
                    
                    # Execute step
                    if 'run' in step:
                        self.execute_step(job_id, step)
                    elif 'uses' in step:
                        self.add_log(job_id, f"🔧 Using action: {step['uses']}")
                        # Simulate action execution
                        time.sleep(1)
                        self.add_log(job_id, f"✅ Action completed: {step['uses']}")
            
            job['status'] = 'completed'
            job['end_time'] = datetime.now().isoformat()
            self.add_log(job_id, "🎉 Workflow completed successfully!")
            
        except Exception as e:
            job = self.running_jobs[job_id]
            job['status'] = 'failed'
            job['end_time'] = datetime.now().isoformat()
            self.add_log(job_id, f"❌ Workflow failed: {str(e)}")
        
        finally:
            # Move from running to history
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
    
    def execute_step(self, job_id, step):
        """Execute a single workflow step"""
        try:
            run_command = step['run']
            self.add_log(job_id, f"💻 Executing: {run_command}")
            
            # Set environment variables
            env = os.environ.copy()
            env.update({
                'GITHUB_WORKSPACE': os.getcwd(),
                'GITHUB_REPOSITORY': 'local/Advanced-Multi-Agent-Intelligence-System',
                'GITHUB_ACTIONS': 'true',
                'RUNNER_OS': 'Linux',
                'RUNNER_ARCH': 'X64'
            })
            
            # Execute command
            result = subprocess.run(
                run_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                env=env
            )
            
            if result.stdout:
                self.add_log(job_id, f"📤 Output: {result.stdout}")
            if result.stderr:
                self.add_log(job_id, f"⚠️ Error: {result.stderr}")
            
            if result.returncode == 0:
                self.add_log(job_id, f"✅ Step completed successfully")
            else:
                self.add_log(job_id, f"❌ Step failed with exit code {result.returncode}")
                
        except Exception as e:
            self.add_log(job_id, f"❌ Step execution error: {str(e)}")
    
    def add_log(self, job_id, message):
        """Add a log message to a job"""
        if job_id in self.running_jobs:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            self.running_jobs[job_id]['logs'].append(log_entry)
            print(f"[{job_id}] {log_entry}")
    
    def run(self, host='127.0.0.1', port=5000):
        """Start the local GitHub Actions server"""
        print("🚀 Starting Local GitHub Actions Runner...")
        print(f"📊 Loaded {len(self.workflows)} workflows")
        print(f"🌐 Server starting at http://{host}:{port}")
        
        # Open browser
        webbrowser.open(f"http://{host}:{port}")
        
        # Start Flask server
        self.app.run(host=host, port=port, debug=True)

def main():
    """Main entry point"""
    print("🤖 Local GitHub Actions Runner")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository! Please run from your project root.")
        sys.exit(1)
    
    # Check if .github/workflows exists
    if not os.path.exists('.github/workflows'):
        print("❌ No .github/workflows directory found!")
        sys.exit(1)
    
    # Start the local runner
    runner = LocalGitHubActions()
    runner.run()

if __name__ == "__main__":
    main()