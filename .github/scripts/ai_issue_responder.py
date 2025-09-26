#!/usr/bin/env python3
"""
AI Issue Responder Script
Automatically analyzes GitHub issues and provides intelligent responses
using your AI APIs (OpenRouter, DeepSeek, etc.)
"""

import os
import json
import requests
from openai import OpenAI
from typing import Dict, Any, Optional
import time

class AIIssueResponder:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        
        # Issue details
        self.issue_number = os.environ.get('ISSUE_NUMBER')
        self.issue_title = os.environ.get('ISSUE_TITLE')
        self.issue_body = os.environ.get('ISSUE_BODY', '')
        self.issue_author = os.environ.get('ISSUE_AUTHOR')
        
        # Initialize AI clients with intelligent fallback priority
        self.ai_clients = []
        
        # Priority order: DeepSeek (most reliable), GLM, Grok, Kimi, Qwen, GPTOSS
        if self.deepseek_key:
            try:
                self.ai_clients.append({
                    'name': 'DeepSeek',
                    'client': OpenAI(
                        base_url="https://api.deepseek.com/v1",
                        api_key=self.deepseek_key,
                    ),
                    'model': 'deepseek-chat',
                    'priority': 1
                })
            except Exception as e:
                print(f"Failed to initialize DeepSeek client: {e}")
        
        if self.glm_key:
            try:
                self.ai_clients.append({
                    'name': 'GLM',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.glm_key,
                    ),
                    'model': 'z-ai/glm-4.5-air:free',
                    'priority': 2
                })
            except Exception as e:
                print(f"Failed to initialize GLM client: {e}")
        
        if self.grok_key:
            try:
                self.ai_clients.append({
                    'name': 'Grok',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.grok_key,
                    ),
                    'model': 'x-ai/grok-4-fast:free',
                    'priority': 3
                })
            except Exception as e:
                print(f"Failed to initialize Grok client: {e}")
        
        if self.kimi_key:
            try:
                self.ai_clients.append({
                    'name': 'Kimi',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.kimi_key,
                    ),
                    'model': 'moonshot/moonshot-v1-8k:free',
                    'priority': 4
                })
            except Exception as e:
                print(f"Failed to initialize Kimi client: {e}")
        
        if self.qwen_key:
            try:
                self.ai_clients.append({
                    'name': 'Qwen',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.qwen_key,
                    ),
                    'model': 'qwen/qwen-2.5-7b-instruct:free',
                    'priority': 5
                })
            except Exception as e:
                print(f"Failed to initialize Qwen client: {e}")
        
        if self.gptoss_key:
            try:
                self.ai_clients.append({
                    'name': 'GPTOSS',
                    'client': OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=self.gptoss_key,
                    ),
                    'model': 'openai/gpt-3.5-turbo:free',
                    'priority': 6
                })
            except Exception as e:
                print(f"Failed to initialize GPTOSS client: {e}")
        
        # Sort by priority
        self.ai_clients.sort(key=lambda x: x['priority'])
        
        if not self.ai_clients:
            print("⚠️ No AI clients available - will use fallback response")
        else:
            print(f"🤖 Initialized {len(self.ai_clients)} AI clients for issue response")
    
    def analyze_issue_type(self, title: str, body: str) -> str:
        """Analyze the type of issue based on content"""
        title_lower = title.lower()
        body_lower = body.lower()
        
        # Define issue types based on keywords
        if any(word in title_lower or word in body_lower for word in ['bug', 'error', 'broken', 'crash', 'fail']):
            return 'bug'
        elif any(word in title_lower or word in body_lower for word in ['feature', 'enhancement', 'add', 'implement']):
            return 'feature_request'
        elif any(word in title_lower or word in body_lower for word in ['question', 'how to', 'help', '?']):
            return 'question'
        elif any(word in title_lower or word in body_lower for word in ['security', 'vulnerability', 'exploit']):
            return 'security'
        elif any(word in title_lower or word in body_lower for word in ['performance', 'slow', 'optimization']):
            return 'performance'
        elif any(word in title_lower or word in body_lower for word in ['documentation', 'docs', 'readme']):
            return 'documentation'
        else:
            return 'general'
    
    def create_system_prompt(self, issue_type: str) -> str:
        """Create system prompt based on issue type"""
        base_prompt = f"""
You are an AI assistant for the AMAS (Advanced Multi-Agent Intelligence System) project.
This is a sophisticated multi-agent AI system for intelligence analysis and automation.

Project Context:
- Multi-agent orchestration with ReAct patterns
- OSINT collection and analysis
- Digital forensics and investigation
- AI-powered code generation
- Enterprise security features

Your role is to provide helpful, technical, and actionable responses to GitHub issues.
"""
        
        type_specific_prompts = {
            'bug': """
For bug reports:
1. Acknowledge the issue professionally
2. Ask for reproduction steps if missing
3. Suggest potential workarounds
4. Provide debugging guidance
5. Mention if this relates to known issues
""",
            'feature_request': """
For feature requests:
1. Thank the user for the suggestion
2. Assess feasibility within AMAS architecture
3. Suggest implementation approach
4. Ask for clarification if needed
5. Mention related existing features
""",
            'question': """
For questions:
1. Provide clear, helpful answers
2. Reference documentation when relevant
3. Offer code examples if applicable
4. Suggest additional resources
5. Be encouraging and supportive
""",
            'security': """
For security issues:
1. Take security concerns seriously
2. Provide secure coding recommendations
3. Reference security best practices
4. Suggest immediate mitigation steps
5. Recommend proper reporting channels for vulnerabilities
"""
        }
        
        return base_prompt + type_specific_prompts.get(issue_type, type_specific_prompts['question'])
    
    def generate_ai_response(self, issue_type: str, title: str, body: str) -> Optional[str]:
        """Generate AI response using available APIs with fallback"""
        if not self.ai_clients:
            return None
            
        system_prompt = self.create_system_prompt(issue_type)
        
        user_prompt = f"""
Issue Title: {title}

Issue Description:
{body}

Issue Type: {issue_type}
Author: {self.issue_author}

Please provide a helpful, professional response that addresses this issue.
Be specific to the AMAS project context and provide actionable guidance.
"""
        
        # Try each AI client in order of preference
        for client_info in self.ai_clients:
            try:
                print(f"🤖 Trying {client_info['name']} for issue response...")
                
                extra_headers = {}
                if 'openrouter.ai' in str(client_info['client'].base_url):
                    extra_headers = {
                        "HTTP-Referer": f"https://github.com/{self.repo_name}",
                        "X-Title": "AMAS Intelligence System",
                    }
                
                response = client_info['client'].chat.completions.create(
                    extra_headers=extra_headers if extra_headers else None,
                    model=client_info['model'],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                print(f"✅ Successfully generated response with {client_info['name']}")
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"❌ {client_info['name']} failed: {e}")
                continue
        
        print("❌ All AI clients failed")
        return None
    
    def post_github_comment(self, comment: str) -> bool:
        """Post comment to GitHub issue"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/comments"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        # Add AI signature to comment
        ai_comment = f"""{comment}

---
🤖 *This response was generated by AMAS AI Assistant*
💡 *Powered by your integrated AI models*
📚 *For more help, check the [project documentation](https://github.com/{self.repo_name}#readme)*
"""
        
        data = {'body': ai_comment}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Posted AI response to issue #{self.issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post comment: {e}")
            return False
    
    def add_issue_labels(self, labels: list) -> bool:
        """Add labels to the issue"""
        url = f"https://api.github.com/repos/{self.repo_name}/issues/{self.issue_number}/labels"
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {'labels': labels}
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print(f"✅ Added labels {labels} to issue #{self.issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to add labels: {e}")
            return False
    
    def run(self):
        """Main execution function"""
        print(f"🚀 Processing issue #{self.issue_number}: {self.issue_title}")
        
        # Analyze issue type
        issue_type = self.analyze_issue_type(self.issue_title, self.issue_body)
        print(f"📋 Issue type detected: {issue_type}")
        
        # Generate AI response
        print("🧠 Generating AI response...")
        ai_response = self.generate_ai_response(issue_type, self.issue_title, self.issue_body)
        
        if ai_response:
            # Post the response
            success = self.post_github_comment(ai_response)
            
            if success:
                # Add appropriate labels
                labels = ['ai-analyzed', issue_type]
                if issue_type == 'security':
                    labels.append('priority-high')
                elif issue_type == 'bug':
                    labels.append('bug')
                elif issue_type == 'feature_request':
                    labels.append('enhancement')
                
                self.add_issue_labels(labels)
                print("✅ Issue processing completed successfully!")
            else:
                print("❌ Failed to post AI response")
        else:
            print("❌ Failed to generate AI response")
            # Post a fallback message
            fallback_message = f"""
Thank you for opening this issue! 🙏

I'm the AMAS AI Assistant, and I'll help analyze your issue. However, I'm currently experiencing some technical difficulties with my AI models.

In the meantime, here are some helpful resources:
- 📚 [Project Documentation](https://github.com/{self.repo_name}#readme)
- 🔧 [Setup Guide](https://github.com/{self.repo_name}/blob/main/SETUP_GUIDE.md)
- 💬 [Discussions](https://github.com/{self.repo_name}/discussions)

A human maintainer will review your issue soon. Thank you for your patience!

---
🤖 *AMAS AI Assistant - Currently in fallback mode*
"""
            self.post_github_comment(fallback_message)
            self.add_issue_labels(['ai-analyzed', 'needs-human-review'])

if __name__ == "__main__":
    responder = AIIssueResponder()
    responder.run()
