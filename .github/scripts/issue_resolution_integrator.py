#!/usr/bin/env python3
"""
Issue Resolution Integrator Script
Combines AI analysis results to provide comprehensive issue resolution
"""

import os
import json
import requests
from openai import OpenAI
from typing import Dict, Any, Optional
import time

class IssueResolutionIntegrator:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        self.issue_number = os.environ.get('ISSUE_NUMBER')
        
        # Initialize AI clients
        self.ai_client = None
        if self.openrouter_key:
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
            )
        elif self.deepseek_key:
            self.ai_client = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=self.deepseek_key,
            )
    
    def get_issue_details(self) -> Optional[Dict[str, Any]]:
        """Get issue details from GitHub API"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issue details: {e}")
            return None
    
    def get_issue_comments(self) -> list:
        """Get all comments for the issue"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/comments"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issue comments: {e}")
            return []
    
    def analyze_resolution_status(self, issue_data: Dict[str, Any], comments: list) -> str:
        """Analyze the current resolution status of the issue"""
        if not self.ai_client:
            return "AI analysis unavailable - manual review required"
        
        # Prepare context for AI analysis
        issue_context = f"""
Issue Title: {issue_data.get('title', '')}
Issue Body: {issue_data.get('body', '')}
Issue State: {issue_data.get('state', '')}
Issue Labels: {[label['name'] for label in issue_data.get('labels', [])]}

Recent Comments:
"""
        
        # Add recent AI-generated comments
        ai_comments = [comment for comment in comments if 'AMAS AI' in comment.get('body', '')]
        for comment in ai_comments[-3:]:  # Last 3 AI comments
            issue_context += f"- {comment['body'][:200]}...\n"
        
        system_prompt = """
You are an AI resolution coordinator for the AMAS Intelligence System.
Your role is to analyze issue resolution status and provide next steps.

Analyze:
1. Current resolution progress
2. What's been done by AI systems
3. What still needs human intervention
4. Recommended next steps
5. Priority level for resolution

Provide a concise but comprehensive resolution status.
"""
        
        user_prompt = f"""
Based on this issue context, provide a resolution status analysis:

{issue_context}

Please provide:
1. **Resolution Status** (In Progress/Needs Human Review/Ready for Testing/etc.)
2. **AI Contributions** (What AI has already analyzed/responded)
3. **Next Steps** (What needs to be done next)
4. **Priority Level** (High/Medium/Low)
5. **Estimated Resolution Time** (if possible)

Keep it concise but actionable.
"""
        
        try:
            model = "deepseek/deepseek-chat-v3.1:free" if self.openrouter_key else "deepseek-chat"
            
            extra_headers = {}
            if self.openrouter_key:
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Issue Resolution Analysis",
                }
            
            response = self.ai_client.chat.completions.create(
                extra_headers=extra_headers if self.openrouter_key else None,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return "AI analysis failed - manual review required"
    
    def generate_resolution_summary(self, resolution_analysis: str) -> str:
        """Generate a comprehensive resolution summary"""
        summary = f"""# 🔧 Issue Resolution Summary

## 📊 Current Status
{resolution_analysis}

## 🤖 AI Systems Engaged
- ✅ **AI Issue Analyzer**: Analyzed issue type and provided initial response
- ✅ **Multi-Agent Intelligence**: Performed deep analysis using multiple AI models
- ✅ **Resolution Coordinator**: Assessed current status and next steps

## 📋 Resolution Checklist
- [ ] Review AI analysis and recommendations
- [ ] Implement suggested solutions (if applicable)
- [ ] Test proposed fixes
- [ ] Update documentation if needed
- [ ] Close issue when resolved

## 🎯 Next Actions
Based on the AI analysis above, please review and take appropriate action.

---
🤖 *AMAS AI Resolution Coordinator*
📈 *Powered by integrated multi-agent intelligence*
"""
        
        return summary
    
    def post_resolution_summary(self, summary: str) -> bool:
        """Post resolution summary to the issue"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/comments"
        
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {'body': summary}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Posted resolution summary to issue #{self.issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post resolution summary: {e}")
            return False
    
    def update_issue_labels(self, labels: list) -> bool:
        """Update issue labels based on resolution status"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/labels"
        
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {'labels': labels}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Updated labels for issue #{self.issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to update labels: {e}")
            return False
    
    def run(self):
        """Main execution function"""
        print(f"🔧 Processing issue resolution for #{self.issue_number}")
        
        # Get issue details
        issue_data = self.get_issue_details()
        if not issue_data:
            print("❌ Failed to fetch issue details")
            return
        
        # Get issue comments
        comments = self.get_issue_comments()
        print(f"📝 Found {len(comments)} comments")
        
        # Analyze resolution status
        print("🧠 Analyzing resolution status...")
        resolution_analysis = self.analyze_resolution_status(issue_data, comments)
        
        # Generate comprehensive summary
        summary = self.generate_resolution_summary(resolution_analysis)
        
        # Post summary
        success = self.post_resolution_summary(summary)
        
        if success:
            # Update labels
            labels = ['ai-analyzed', 'auto-response', 'ai-resolution-ready']
            self.update_issue_labels(labels)
            print("✅ Issue resolution integration completed!")
        else:
            print("❌ Failed to post resolution summary")

if __name__ == "__main__":
    integrator = IssueResolutionIntegrator()
    integrator.run()