#!/usr/bin/env python3
"""
Multi-API AI Issue Responder
Uses all 6 AI APIs with intelligent fallback for GitHub issue responses
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Tuple
from ai_service_manager import AIServiceManager

class MultiAPIResponder:
    def __init__(self):
        """Initialize the multi-API responder"""
        self.ai_manager = AIServiceManager()
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPOSITORY')
        self.issue_number = os.environ.get('ISSUE_NUMBER')
        
        if not all([self.github_token, self.repo, self.issue_number]):
            print("❌ Missing required environment variables")
            sys.exit(1)
    
    def get_issue_details(self) -> Tuple[Optional[str], Optional[str]]:
        """Get issue title and body from GitHub API"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                issue_data = response.json()
                return issue_data.get('title', ''), issue_data.get('body', '')
            else:
                print(f"❌ Failed to get issue details: {response.status_code}")
                return None, None
        except Exception as e:
            print(f"❌ Error getting issue details: {e}")
            return None, None
    
    def categorize_issue(self, title: str, body: str) -> str:
        """Categorize the issue type"""
        content = f"{title} {body}".lower()
        
        if any(word in content for word in ['bug', 'error', 'crash', 'broken', 'not working']):
            return 'bug'
        elif any(word in content for word in ['feature', 'enhancement', 'request', 'add', 'new']):
            return 'feature'
        elif any(word in content for word in ['question', 'how', 'what', 'why', 'help']):
            return 'question'
        elif any(word in content for word in ['security', 'vulnerability', 'exploit', 'hack']):
            return 'security'
        elif any(word in content for word in ['performance', 'slow', 'optimize', 'speed']):
            return 'performance'
        elif any(word in content for word in ['documentation', 'docs', 'readme', 'guide']):
            return 'documentation'
        else:
            return 'general'
    
    def generate_specialized_response(self, title: str, body: str, category: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate specialized response based on issue category"""
        
        if category == 'bug':
            system_prompt = """You are a bug triage expert. For bug reports, provide:
1. Acknowledgment of the issue
2. Steps to reproduce (if not provided)
3. Potential causes and solutions
4. Request for additional information if needed
5. Priority assessment
Be helpful and systematic in your approach."""
            
        elif category == 'feature':
            system_prompt = """You are a product manager. For feature requests, provide:
1. Acknowledgment of the request
2. Assessment of feasibility and impact
3. Questions about requirements and use cases
4. Timeline considerations
5. Alternative approaches if applicable
Be encouraging and ask clarifying questions."""
            
        elif category == 'security':
            system_prompt = """You are a security expert. For security issues, provide:
1. Immediate acknowledgment of the security concern
2. Assessment of severity and impact
3. Immediate mitigation steps if applicable
4. Request for responsible disclosure
5. Security best practices
Be thorough and prioritize security."""
            
        elif category == 'performance':
            system_prompt = """You are a performance optimization expert. For performance issues, provide:
1. Acknowledgment of the performance concern
2. Analysis of potential bottlenecks
3. Profiling and measurement suggestions
4. Optimization strategies
5. Performance monitoring recommendations
Be technical and solution-oriented."""
            
        elif category == 'documentation':
            system_prompt = """You are a technical writer. For documentation issues, provide:
1. Acknowledgment of the documentation need
2. Assessment of current documentation gaps
3. Suggestions for improvement
4. Offer to help with documentation
5. Documentation best practices
Be helpful and constructive."""
            
        else:  # general or question
            system_prompt = """You are a helpful technical assistant. For general questions, provide:
1. Acknowledgment of the question
2. Clear and helpful answer
3. Additional resources if relevant
4. Follow-up questions if needed
5. Offer further assistance
Be friendly and informative."""
        
        prompt = f"Issue Title: {title}\n\nIssue Description: {body}\n\nGenerate a helpful response:"
        return self.ai_manager.generate_response(prompt, system_prompt)
    
    def post_response(self, response: str, provider: str) -> bool:
        """Post response to GitHub issue"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/comments"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            comment_body = f"""## 🤖 AI Assistant Response (via {provider})

{response}

---
*This response was generated automatically using our multi-API AI system. If you need further assistance, please let us know!*"""
            
            comment_data = {'body': comment_body}
            
            response_req = requests.post(url, headers=headers, json=comment_data)
            if response_req.status_code == 201:
                print(f"✅ Response posted successfully using {provider}")
                return True
            else:
                print(f"❌ Failed to post response: {response_req.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting response: {e}")
            return False
    
    def add_labels(self, category: str) -> bool:
        """Add appropriate labels to the issue"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/labels"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Base labels
            labels = ['ai-analyzed', 'auto-response']
            
            # Category-specific labels
            if category == 'bug':
                labels.extend(['bug', 'needs-triage'])
            elif category == 'feature':
                labels.extend(['enhancement', 'feature-request'])
            elif category == 'security':
                labels.extend(['security', 'high-priority'])
            elif category == 'performance':
                labels.extend(['performance', 'optimization'])
            elif category == 'documentation':
                labels.extend(['documentation', 'docs'])
            elif category == 'question':
                labels.extend(['question', 'help-wanted'])
            
            label_data = {'labels': labels}
            
            response = requests.post(url, headers=headers, json=label_data)
            if response.status_code == 200:
                print(f"✅ Labels added: {', '.join(labels)}")
                return True
            else:
                print(f"❌ Failed to add labels: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding labels: {e}")
            return False
    
    def post_fallback_response(self) -> bool:
        """Post a fallback response when AI fails"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.issue_number}/comments"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            fallback_body = """## 🤖 AI Assistant

Thank you for creating this issue! Our AI system is currently processing your request and will provide a detailed analysis shortly.

In the meantime, please ensure you've provided:
- Clear description of the issue
- Steps to reproduce (if applicable)
- Expected vs actual behavior
- Environment details

We'll get back to you soon with a comprehensive response!

---
*This is an automated response from our multi-API AI system.*"""
            
            comment_data = {'body': fallback_body}
            
            response = requests.post(url, headers=headers, json=comment_data)
            if response.status_code == 201:
                print("✅ Fallback response posted")
                return True
            else:
                print(f"❌ Failed to post fallback response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error posting fallback response: {e}")
            return False
    
    def process_issue(self) -> bool:
        """Main processing function"""
        print(f"🚀 Processing issue #{self.issue_number} in {self.repo}")
        
        # Get issue details
        title, body = self.get_issue_details()
        if not title:
            print("❌ Could not retrieve issue details")
            return False
        
        print(f"📋 Issue: {title}")
        
        # Categorize issue
        category = self.categorize_issue(title, body)
        print(f"🏷️ Category: {category}")
        
        # Generate AI response
        print("🧠 Generating AI response...")
        response, provider, error = self.generate_specialized_response(title, body, category)
        
        if response:
            # Post response
            if self.post_response(response, provider):
                # Add labels
                self.add_labels(category)
                print("✅ Issue processing complete!")
                return True
            else:
                print("❌ Failed to post response")
                return False
        else:
            print(f"❌ AI response generation failed: {error}")
            # Post fallback response
            if self.post_fallback_response():
                self.add_labels(category)
                print("✅ Fallback response posted")
                return True
            else:
                print("❌ Failed to post fallback response")
                return False

def main():
    """Main function"""
    print("🤖 Multi-API AI Issue Responder")
    print("=" * 50)
    
    responder = MultiAPIResponder()
    success = responder.process_issue()
    
    # Show AI provider stats
    print("\n📊 AI Provider Statistics:")
    stats = responder.ai_manager.get_provider_stats()
    for name, stat in stats.items():
        status = "✅ Active" if stat['active'] and stat['has_key'] else "❌ Inactive"
        print(f"  {name}: {status} (Success: {stat['success_rate']})")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Responder failed: {e}")
        sys.exit(1)