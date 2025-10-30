# 🚀 AI Agentic Integration Examples

## 🎯 **Practical Implementation Tutorials**

This comprehensive guide provides practical examples and tutorials for integrating the AI Agentic Workflow System into your projects. Learn how to leverage the revolutionary 4-layer AI agent architecture and 16 AI providers for maximum automation and intelligence.

---

## 🏗️ **Integration Architecture Overview**

### **System Components**
```
┌─────────────────────────────────────────────────────────────┐
│                    🧠 AI Agentic Workflow System            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Master          │ │ Self-Improver   │ │ Issue           │ │
│  │ Orchestrator    │ │                 │ │ Responder       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Audit & Docs    │ │ Build & Deploy  │ │ Security        │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│  ┌─────────────────┐ ┌─────────────────┐                   │
│  │ Code Quality    │ │ CI/CD Pipeline  │                   │
│  └─────────────────┘ └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### **Integration Points**
- **GitHub Actions**: Workflow automation
- **API Integration**: RESTful API endpoints
- **Webhook Integration**: Real-time notifications
- **CLI Integration**: Command-line interface
- **SDK Integration**: Software development kits

---

## 🚀 **Basic Integration Examples**

### **1. GitHub Actions Integration**

#### **Simple Workflow Integration**
```yaml
name: AI Agentic Workflow Integration
on:
  push:
    branches: [ main, develop ]
  pull_request:
    types: [ opened, synchronize, reopened ]

jobs:
  ai_orchestration:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Trigger AI Orchestrator
        uses: actions/github-script@v7
        with:
          script: |
            // Trigger Master AI Orchestrator
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: '00-master-ai-orchestrator.yml',
              ref: 'main',
              inputs: {
                orchestration_mode: 'intelligent',
                target_components: 'all',
                priority_level: 'normal'
              }
            });
```

#### **Advanced Workflow Integration**
```yaml
name: Advanced AI Agentic Integration
on:
  workflow_dispatch:
    inputs:
      workflow_type:
        description: 'Workflow Type'
        required: true
        type: choice
        options:
          - orchestrator
          - self_improver
          - issue_responder
          - audit_docs
          - build_deploy
          - security
          - code_quality
          - cicd_pipeline

jobs:
  ai_workflow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Configure AI Workflow
        id: config
        run: |
          case "${{ github.event.inputs.workflow_type }}" in
            "orchestrator")
              echo "workflow_file=00-master-ai-orchestrator.yml" >> $GITHUB_OUTPUT
              echo "mode=intelligent" >> $GITHUB_OUTPUT
              ;;
            "self_improver")
              echo "workflow_file=01-ai-agentic-project-self-improver.yml" >> $GITHUB_OUTPUT
              echo "mode=intelligent" >> $GITHUB_OUTPUT
              ;;
            "issue_responder")
              echo "workflow_file=02-ai-agentic-issue-auto-responder.yml" >> $GITHUB_OUTPUT
              echo "mode=intelligent" >> $GITHUB_OUTPUT
              ;;
            *)
              echo "workflow_file=00-master-ai-orchestrator.yml" >> $GITHUB_OUTPUT
              echo "mode=intelligent" >> $GITHUB_OUTPUT
              ;;
          esac
      
      - name: Trigger AI Workflow
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: '${{ steps.config.outputs.workflow_file }}',
              ref: 'main',
              inputs: {
                orchestration_mode: '${{ steps.config.outputs.mode }}',
                target_components: 'all',
                priority_level: 'normal'
              }
            });
```

### **2. API Integration Examples**

#### **RESTful API Integration**
```python
import requests
import json

class AIAgenticWorkflowClient:
    def __init__(self, github_token, repo_owner, repo_name):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def trigger_orchestrator(self, mode="intelligent", components="all", priority="normal"):
        """Trigger Master AI Orchestrator workflow"""
        url = f"{self.base_url}/actions/workflows/00-master-ai-orchestrator.yml/dispatches"
        data = {
            "ref": "main",
            "inputs": {
                "orchestration_mode": mode,
                "target_components": components,
                "priority_level": priority
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 204
    
    def trigger_self_improver(self, mode="intelligent", areas="all", depth="deep", auto_apply=False):
        """Trigger AI Agentic Project Self-Improver workflow"""
        url = f"{self.base_url}/actions/workflows/01-ai-agentic-project-self-improver.yml/dispatches"
        data = {
            "ref": "main",
            "inputs": {
                "improvement_mode": mode,
                "target_areas": areas,
                "learning_depth": depth,
                "auto_apply": str(auto_apply).lower()
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 204
    
    def trigger_issue_responder(self, mode="intelligent", depth="comprehensive", auto_fix=False, language="auto"):
        """Trigger AI Agentic Issue Auto-Responder workflow"""
        url = f"{self.base_url}/actions/workflows/02-ai-agentic-issue-auto-responder.yml/dispatches"
        data = {
            "ref": "main",
            "inputs": {
                "response_mode": mode,
                "response_depth": depth,
                "auto_fix": str(auto_fix).lower(),
                "language_preference": language
            }
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code == 204
    
    def get_workflow_status(self, workflow_id):
        """Get workflow run status"""
        url = f"{self.base_url}/actions/workflows/{workflow_id}/runs"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_workflow_logs(self, run_id):
        """Get workflow run logs"""
        url = f"{self.base_url}/actions/runs/{run_id}/logs"
        response = requests.get(url, headers=self.headers)
        return response.content

# Usage Example
client = AIAgenticWorkflowClient(
    github_token="your_github_token",
    repo_owner="your_username",
    repo_name="your_repository"
)

# Trigger Master Orchestrator
success = client.trigger_orchestrator(
    mode="intelligent",
    components="all",
    priority="normal"
)

# Trigger Self-Improver
success = client.trigger_self_improver(
    mode="aggressive",
    areas="performance,security",
    depth="comprehensive",
    auto_apply=True
)

# Trigger Issue Responder
success = client.trigger_issue_responder(
    mode="technical_focused",
    depth="expert",
    auto_fix=True,
    language="english"
)
```

#### **Async API Integration**
```python
import asyncio
import aiohttp
import json

class AsyncAIAgenticWorkflowClient:
    def __init__(self, github_token, repo_owner, repo_name):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def trigger_workflow(self, workflow_file, inputs):
        """Trigger any AI workflow asynchronously"""
        url = f"{self.base_url}/actions/workflows/{workflow_file}/dispatches"
        data = {
            "ref": "main",
            "inputs": inputs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                return response.status == 204
    
    async def trigger_multiple_workflows(self, workflows):
        """Trigger multiple workflows concurrently"""
        tasks = []
        for workflow in workflows:
            task = self.trigger_workflow(workflow['file'], workflow['inputs'])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# Usage Example
async def main():
    client = AsyncAIAgenticWorkflowClient(
        github_token="your_github_token",
        repo_owner="your_username",
        repo_name="your_repository"
    )
    
    # Define multiple workflows to trigger
    workflows = [
        {
            "file": "00-master-ai-orchestrator.yml",
            "inputs": {
                "orchestration_mode": "intelligent",
                "target_components": "all",
                "priority_level": "normal"
            }
        },
        {
            "file": "01-ai-agentic-project-self-improver.yml",
            "inputs": {
                "improvement_mode": "intelligent",
                "target_areas": "all",
                "learning_depth": "deep",
                "auto_apply": "false"
            }
        },
        {
            "file": "02-ai-agentic-issue-auto-responder.yml",
            "inputs": {
                "response_mode": "intelligent",
                "response_depth": "comprehensive",
                "auto_fix": "false",
                "language_preference": "auto"
            }
        }
    ]
    
    # Trigger all workflows concurrently
    results = await client.trigger_multiple_workflows(workflows)
    
    for i, result in enumerate(results):
        workflow_name = workflows[i]['file']
        if isinstance(result, Exception):
            print(f"❌ {workflow_name}: Failed - {result}")
        else:
            print(f"✅ {workflow_name}: Success")

# Run the async example
asyncio.run(main())
```

### **3. Webhook Integration Examples**

#### **GitHub Webhook Integration**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

class AIAgenticWebhookHandler:
    def __init__(self, webhook_secret, github_token, repo_owner, repo_name):
        self.webhook_secret = webhook_secret
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.client = AIAgenticWorkflowClient(github_token, repo_owner, repo_name)
    
    def verify_signature(self, payload, signature):
        """Verify GitHub webhook signature"""
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def handle_push_event(self, payload):
        """Handle push events"""
        ref = payload.get('ref', '')
        if ref.startswith('refs/heads/'):
            branch = ref.replace('refs/heads/', '')
            if branch in ['main', 'develop']:
                # Trigger Master Orchestrator
                self.client.trigger_orchestrator(
                    mode="intelligent",
                    components="all",
                    priority="normal"
                )
                return "Orchestrator triggered for push to main/develop"
        return "No action taken for push event"
    
    def handle_issue_event(self, payload):
        """Handle issue events"""
        action = payload.get('action', '')
        if action in ['opened', 'edited', 'reopened']:
            # Trigger Issue Responder
            self.client.trigger_issue_responder(
                mode="intelligent",
                depth="comprehensive",
                auto_fix=False,
                language="auto"
            )
            return "Issue Responder triggered for issue event"
        return "No action taken for issue event"
    
    def handle_pull_request_event(self, payload):
        """Handle pull request events"""
        action = payload.get('action', '')
        if action in ['opened', 'synchronize', 'reopened']:
            # Trigger multiple workflows
            self.client.trigger_orchestrator(
                mode="intelligent",
                components="all",
                priority="normal"
            )
            self.client.trigger_self_improver(
                mode="intelligent",
                areas="code_quality,performance",
                depth="deep",
                auto_apply=False
            )
            return "Multiple workflows triggered for PR event"
        return "No action taken for PR event"

# Initialize webhook handler
webhook_handler = AIAgenticWebhookHandler(
    webhook_secret="your_webhook_secret",
    github_token="your_github_token",
    repo_owner="your_username",
    repo_name="your_repository"
)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhooks"""
    signature = request.headers.get('X-Hub-Signature-256', '')
    payload = request.get_data()
    
    # Verify signature
    if not webhook_handler.verify_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse payload
    event = request.headers.get('X-GitHub-Event', '')
    payload_data = json.loads(payload)
    
    # Handle different events
    if event == 'push':
        result = webhook_handler.handle_push_event(payload_data)
    elif event == 'issues':
        result = webhook_handler.handle_issue_event(payload_data)
    elif event == 'pull_request':
        result = webhook_handler.handle_pull_request_event(payload_data)
    else:
        result = f"No handler for event: {event}"
    
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### **4. CLI Integration Examples**

#### **Command Line Interface**
```python
import click
import requests
import json
import time

@click.group()
def cli():
    """AI Agentic Workflow CLI"""
    pass

@cli.command()
@click.option('--mode', default='intelligent', help='Orchestration mode')
@click.option('--components', default='all', help='Target components')
@click.option('--priority', default='normal', help='Priority level')
def orchestrate(mode, components, priority):
    """Trigger Master AI Orchestrator"""
    client = AIAgenticWorkflowClient(
        github_token=click.prompt('GitHub Token', hide_input=True),
        repo_owner=click.prompt('Repository Owner'),
        repo_name=click.prompt('Repository Name')
    )
    
    success = client.trigger_orchestrator(mode, components, priority)
    if success:
        click.echo("✅ Master AI Orchestrator triggered successfully")
    else:
        click.echo("❌ Failed to trigger Master AI Orchestrator")

@cli.command()
@click.option('--mode', default='intelligent', help='Improvement mode')
@click.option('--areas', default='all', help='Target areas')
@click.option('--depth', default='deep', help='Learning depth')
@click.option('--auto-apply', is_flag=True, help='Auto-apply improvements')
def improve(mode, areas, depth, auto_apply):
    """Trigger AI Agentic Project Self-Improver"""
    client = AIAgenticWorkflowClient(
        github_token=click.prompt('GitHub Token', hide_input=True),
        repo_owner=click.prompt('Repository Owner'),
        repo_name=click.prompt('Repository Name')
    )
    
    success = client.trigger_self_improver(mode, areas, depth, auto_apply)
    if success:
        click.echo("✅ AI Agentic Project Self-Improver triggered successfully")
    else:
        click.echo("❌ Failed to trigger AI Agentic Project Self-Improver")

@cli.command()
@click.option('--mode', default='intelligent', help='Response mode')
@click.option('--depth', default='comprehensive', help='Response depth')
@click.option('--auto-fix', is_flag=True, help='Auto-fix issues')
@click.option('--language', default='auto', help='Language preference')
def respond(mode, depth, auto_fix, language):
    """Trigger AI Agentic Issue Auto-Responder"""
    client = AIAgenticWorkflowClient(
        github_token=click.prompt('GitHub Token', hide_input=True),
        repo_owner=click.prompt('Repository Owner'),
        repo_name=click.prompt('Repository Name')
    )
    
    success = client.trigger_issue_responder(mode, depth, auto_fix, language)
    if success:
        click.echo("✅ AI Agentic Issue Auto-Responder triggered successfully")
    else:
        click.echo("❌ Failed to trigger AI Agentic Issue Auto-Responder")

@cli.command()
@click.option('--workflow', help='Workflow file name')
def status(workflow):
    """Get workflow status"""
    client = AIAgenticWorkflowClient(
        github_token=click.prompt('GitHub Token', hide_input=True),
        repo_owner=click.prompt('Repository Owner'),
        repo_name=click.prompt('Repository Name')
    )
    
    if workflow:
        status_data = client.get_workflow_status(workflow)
        click.echo(json.dumps(status_data, indent=2))
    else:
        click.echo("Please specify a workflow file name")

if __name__ == '__main__':
    cli()
```

#### **Usage Examples**
```bash
# Trigger Master Orchestrator
python cli.py orchestrate --mode intelligent --components all --priority normal

# Trigger Self-Improver
python cli.py improve --mode aggressive --areas performance,security --depth comprehensive --auto-apply

# Trigger Issue Responder
python cli.py respond --mode technical_focused --depth expert --auto-fix --language english

# Check workflow status
python cli.py status --workflow 00-master-ai-orchestrator.yml
```

---

## 🔧 **Advanced Integration Examples**

### **1. Custom Workflow Integration**

#### **Custom Workflow Template**
```yaml
name: Custom AI Agentic Integration
on:
  workflow_dispatch:
    inputs:
      custom_mode:
        description: 'Custom Mode'
        required: true
        type: choice
        options:
          - intelligent
          - aggressive
          - conservative
      custom_areas:
        description: 'Custom Areas'
        required: false
        type: string
        default: 'all'
      custom_depth:
        description: 'Custom Depth'
        required: true
        type: choice
        options:
          - surface
          - medium
          - deep
          - comprehensive

jobs:
  custom_ai_workflow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install requests aiohttp click
      
      - name: Run Custom AI Logic
        env:
          CUSTOM_MODE: ${{ github.event.inputs.custom_mode }}
          CUSTOM_AREAS: ${{ github.event.inputs.custom_areas }}
          CUSTOM_DEPTH: ${{ github.event.inputs.custom_depth }}
        run: |
          python custom_ai_script.py \
            --mode $CUSTOM_MODE \
            --areas $CUSTOM_AREAS \
            --depth $CUSTOM_DEPTH
```

#### **Custom AI Script**
```python
import argparse
import requests
import json
import os

def main():
    parser = argparse.ArgumentParser(description='Custom AI Agentic Workflow')
    parser.add_argument('--mode', required=True, help='Custom mode')
    parser.add_argument('--areas', default='all', help='Custom areas')
    parser.add_argument('--depth', required=True, help='Custom depth')
    
    args = parser.parse_args()
    
    # Custom AI logic based on inputs
    if args.mode == 'intelligent':
        print("🧠 Running intelligent AI analysis...")
        # Implement intelligent analysis logic
    elif args.mode == 'aggressive':
        print("⚡ Running aggressive AI optimization...")
        # Implement aggressive optimization logic
    elif args.mode == 'conservative':
        print("🛡️ Running conservative AI improvements...")
        # Implement conservative improvement logic
    
    print(f"📊 Analyzing areas: {args.areas}")
    print(f"🔍 Using depth: {args.depth}")
    
    # Custom processing logic
    process_areas(args.areas, args.depth)
    
    print("✅ Custom AI workflow completed successfully")

def process_areas(areas, depth):
    """Process specified areas with given depth"""
    if areas == 'all':
        areas_list = ['code_quality', 'performance', 'security', 'documentation']
    else:
        areas_list = areas.split(',')
    
    for area in areas_list:
        print(f"🔧 Processing {area} with {depth} depth...")
        # Implement area-specific processing logic

if __name__ == '__main__':
    main()
```

### **2. Multi-Repository Integration**

#### **Multi-Repository Manager**
```python
import asyncio
import aiohttp
from typing import List, Dict

class MultiRepositoryAIManager:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def trigger_workflow_across_repos(self, repos: List[Dict], workflow_file: str, inputs: Dict):
        """Trigger workflow across multiple repositories"""
        tasks = []
        for repo in repos:
            task = self.trigger_workflow_in_repo(
                repo['owner'], 
                repo['name'], 
                workflow_file, 
                inputs
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def trigger_workflow_in_repo(self, owner: str, name: str, workflow_file: str, inputs: Dict):
        """Trigger workflow in specific repository"""
        url = f"https://api.github.com/repos/{owner}/{name}/actions/workflows/{workflow_file}/dispatches"
        data = {
            "ref": "main",
            "inputs": inputs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                return {
                    "repo": f"{owner}/{name}",
                    "status": response.status,
                    "success": response.status == 204
                }

# Usage Example
async def main():
    manager = MultiRepositoryAIManager("your_github_token")
    
    # Define repositories
    repos = [
        {"owner": "user1", "name": "project1"},
        {"owner": "user2", "name": "project2"},
        {"owner": "user3", "name": "project3"}
    ]
    
    # Define workflow inputs
    inputs = {
        "orchestration_mode": "intelligent",
        "target_components": "all",
        "priority_level": "normal"
    }
    
    # Trigger workflow across all repositories
    results = await manager.trigger_workflow_across_repos(
        repos, 
        "00-master-ai-orchestrator.yml", 
        inputs
    )
    
    # Print results
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Error: {result}")
        else:
            status = "✅ Success" if result['success'] else "❌ Failed"
            print(f"{status} - {result['repo']}")

asyncio.run(main())
```

### **3. Monitoring and Analytics Integration**

#### **Workflow Monitoring Dashboard**
```python
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

class AIWorkflowMonitor:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_workflow_runs(self, workflow_id: str, days: int = 7):
        """Get workflow runs for the last N days"""
        url = f"{self.base_url}/actions/workflows/{workflow_id}/runs"
        params = {
            "per_page": 100,
            "created": f">{(datetime.now() - timedelta(days=days)).isoformat()}"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    
    def get_workflow_metrics(self, workflow_id: str, days: int = 7):
        """Get workflow performance metrics"""
        runs = self.get_workflow_runs(workflow_id, days)
        
        if not runs.get('workflow_runs'):
            return None
        
        df = pd.DataFrame(runs['workflow_runs'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['conclusion'] = df['conclusion'].fillna('in_progress')
        
        metrics = {
            'total_runs': len(df),
            'success_rate': (df['conclusion'] == 'success').mean() * 100,
            'failure_rate': (df['conclusion'] == 'failure').mean() * 100,
            'avg_duration': df['run_duration_ms'].mean() / 1000 if 'run_duration_ms' in df.columns else 0,
            'runs_per_day': len(df) / days
        }
        
        return metrics, df

# Streamlit Dashboard
def main():
    st.set_page_config(page_title="AI Agentic Workflow Monitor", layout="wide")
    
    st.title("🚀 AI Agentic Workflow Monitor")
    
    # Configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        github_token = st.text_input("GitHub Token", type="password")
    with col2:
        repo_owner = st.text_input("Repository Owner")
    with col3:
        repo_name = st.text_input("Repository Name")
    
    if github_token and repo_owner and repo_name:
        monitor = AIWorkflowMonitor(github_token, repo_owner, repo_name)
        
        # Workflow selection
        workflow_id = st.selectbox(
            "Select Workflow",
            [
                "00-master-ai-orchestrator.yml",
                "01-ai-agentic-project-self-improver.yml",
                "02-ai-agentic-issue-auto-responder.yml",
                "03-ai-agent-project-audit-documentation.yml",
                "04-ai-enhanced-build-deploy.yml",
                "05-ai-security-threat-intelligence.yml",
                "06-ai-code-quality-performance.yml",
                "07-ai-enhanced-cicd-pipeline.yml"
            ]
        )
        
        # Time range
        days = st.slider("Days to analyze", 1, 30, 7)
        
        # Get metrics
        result = monitor.get_workflow_metrics(workflow_id, days)
        
        if result:
            metrics, df = result
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Runs", metrics['total_runs'])
            with col2:
                st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
            with col3:
                st.metric("Failure Rate", f"{metrics['failure_rate']:.1f}%")
            with col4:
                st.metric("Avg Duration", f"{metrics['avg_duration']:.1f}s")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Success/Failure pie chart
                fig = px.pie(
                    df, 
                    names='conclusion', 
                    title="Workflow Run Results"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Runs over time
                daily_runs = df.groupby(df['created_at'].dt.date).size().reset_index()
                daily_runs.columns = ['date', 'runs']
                
                fig = px.line(
                    daily_runs, 
                    x='date', 
                    y='runs',
                    title="Runs Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent runs table
            st.subheader("Recent Runs")
            st.dataframe(df[['created_at', 'conclusion', 'run_number']].head(10))
        else:
            st.warning("No data available for the selected workflow and time range")

if __name__ == "__main__":
    main()
```

---

## 🎯 **Best Practices for Integration**

### **1. Error Handling**
```python
import logging
from typing import Optional

class AIWorkflowIntegration:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.logger = logging.getLogger(__name__)
    
    def trigger_workflow_with_retry(self, workflow_file: str, inputs: Dict, max_retries: int = 3) -> bool:
        """Trigger workflow with retry logic"""
        for attempt in range(max_retries):
            try:
                success = self.trigger_workflow(workflow_file, inputs)
                if success:
                    self.logger.info(f"Workflow {workflow_file} triggered successfully on attempt {attempt + 1}")
                    return True
                else:
                    self.logger.warning(f"Workflow {workflow_file} failed on attempt {attempt + 1}")
            except Exception as e:
                self.logger.error(f"Error triggering workflow {workflow_file} on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.error(f"Failed to trigger workflow {workflow_file} after {max_retries} attempts")
        return False
```

### **2. Configuration Management**
```python
import yaml
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class WorkflowConfig:
    name: str
    file: str
    default_inputs: Dict
    triggers: List[str]
    enabled: bool = True

class AIWorkflowConfigManager:
    def __init__(self, config_file: str = "ai_workflow_config.yaml"):
        self.config_file = config_file
        self.configs = self.load_configs()
    
    def load_configs(self) -> Dict[str, WorkflowConfig]:
        """Load workflow configurations from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
            
            configs = {}
            for name, config_data in data['workflows'].items():
                configs[name] = WorkflowConfig(
                    name=name,
                    file=config_data['file'],
                    default_inputs=config_data['default_inputs'],
                    triggers=config_data['triggers'],
                    enabled=config_data.get('enabled', True)
                )
            
            return configs
        except FileNotFoundError:
            return self.create_default_configs()
    
    def create_default_configs(self) -> Dict[str, WorkflowConfig]:
        """Create default workflow configurations"""
        return {
            "orchestrator": WorkflowConfig(
                name="Master AI Orchestrator",
                file="00-master-ai-orchestrator.yml",
                default_inputs={
                    "orchestration_mode": "intelligent",
                    "target_components": "all",
                    "priority_level": "normal"
                },
                triggers=["push", "pull_request", "schedule"]
            ),
            "self_improver": WorkflowConfig(
                name="AI Agentic Project Self-Improver",
                file="01-ai-agentic-project-self-improver.yml",
                default_inputs={
                    "improvement_mode": "intelligent",
                    "target_areas": "all",
                    "learning_depth": "deep",
                    "auto_apply": "false"
                },
                triggers=["push", "pull_request", "schedule"]
            )
        }
    
    def get_workflow_config(self, name: str) -> Optional[WorkflowConfig]:
        """Get workflow configuration by name"""
        return self.configs.get(name)
    
    def save_configs(self):
        """Save configurations to YAML file"""
        data = {
            "workflows": {
                name: {
                    "file": config.file,
                    "default_inputs": config.default_inputs,
                    "triggers": config.triggers,
                    "enabled": config.enabled
                }
                for name, config in self.configs.items()
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
```

### **3. Testing Integration**
```python
import unittest
from unittest.mock import Mock, patch
import requests

class TestAIAgenticIntegration(unittest.TestCase):
    def setUp(self):
        self.client = AIAgenticWorkflowClient(
            github_token="test_token",
            repo_owner="test_owner",
            repo_name="test_repo"
        )
    
    @patch('requests.post')
    def test_trigger_orchestrator_success(self, mock_post):
        """Test successful orchestrator trigger"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        result = self.client.trigger_orchestrator()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_trigger_orchestrator_failure(self, mock_post):
        """Test failed orchestrator trigger"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = self.client.trigger_orchestrator()
        
        self.assertFalse(result)
        mock_post.assert_called_once()
    
    def test_workflow_config_loading(self):
        """Test workflow configuration loading"""
        config_manager = AIWorkflowConfigManager("test_config.yaml")
        
        orchestrator_config = config_manager.get_workflow_config("orchestrator")
        self.assertIsNotNone(orchestrator_config)
        self.assertEqual(orchestrator_config.name, "Master AI Orchestrator")
        self.assertEqual(orchestrator_config.file, "00-master-ai-orchestrator.yml")

if __name__ == '__main__':
    unittest.main()
```

---

## 🎉 **Conclusion**

This comprehensive integration guide provides practical examples and tutorials for integrating the AI Agentic Workflow System into your projects. The examples cover:

- **Basic Integration**: GitHub Actions, API, Webhook, and CLI integration
- **Advanced Integration**: Custom workflows, multi-repository management, and monitoring
- **Best Practices**: Error handling, configuration management, and testing

With these examples, you can:
- **Integrate AI workflows** into your existing projects
- **Automate development processes** with AI intelligence
- **Monitor and analyze** workflow performance
- **Scale across multiple repositories** and projects
- **Customize workflows** for your specific needs

**Start integrating the future of AI-powered development workflows today!** 🚀

---

*🎯 AI Agentic Integration Examples - Practical Implementation Tutorials*