#!/usr/bin/env python3
"""
AI Issues Responder - Automatically responds to GitHub issues using AI
"""

import asyncio
import argparse
import logging
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.ai_service_manager import AIServiceManager, AIProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIIssuesResponder:
    """AI-powered GitHub issues responder"""
    
    def __init__(self):
        self.ai_service = None
        self.github_token = None
        self.repository = None
    
    async def initialize(self):
        """Initialize the issues responder"""
        try:
            config = {
                'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
                'glm_api_key': os.getenv('GLM_API_KEY'),
                'grok_api_key': os.getenv('GROK_API_KEY'),
                'kimi_api_key': os.getenv('KIMI_API_KEY'),
                'qwen_api_key': os.getenv('QWEN_API_KEY'),
                'gptoss_api_key': os.getenv('GPTOSS_API_KEY')
            }
            
            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            
            self.github_token = os.getenv('GITHUB_TOKEN')
            self.repository = os.getenv('GITHUB_REPOSITORY')
            
            logger.info("AI Issues Responder initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Issues Responder: {e}")
            raise
    
    async def analyze_issue(self, issue_title: str, issue_body: str, issue_number: int) -> Dict[str, Any]:
        """Analyze an issue and generate a response"""
        try:
            # Create analysis prompt
            analysis_prompt = f"""Analyze this GitHub issue and provide a comprehensive response:

**Issue #{issue_number}: {issue_title}**

**Description:**
{issue_body}

Please provide:
1. Issue type classification (bug, feature request, question, documentation, etc.)
2. Priority level (low, medium, high, critical)
3. Complexity assessment (simple, moderate, complex)
4. Suggested solution approach
5. Required resources and time estimate
6. Related files or components that might be affected
7. Steps to reproduce (if it's a bug)
8. Suggested labels and assignees
9. Follow-up questions if needed
10. A helpful and professional response to the issue author

Format the response as a structured analysis with clear sections."""
            
            response = await self.ai_service.generate_response(analysis_prompt)
            
            if response.success:
                return {
                    'analysis': response.content,
                    'provider': response.provider,
                    'response_time': response.response_time,
                    'success': True
                }
            else:
                return {
                    'error': response.error,
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Error analyzing issue: {e}")
            return {'error': str(e), 'success': False}
    
    async def generate_issue_response(self, issue_title: str, issue_body: str, issue_number: int) -> Dict[str, Any]:
        """Generate a response for an issue"""
        try:
            # Create response prompt
            response_prompt = f"""Generate a helpful and professional response to this GitHub issue:

**Issue #{issue_number}: {issue_title}**

**Description:**
{issue_body}

Please provide:
1. Acknowledgment of the issue
2. Initial assessment
3. Next steps or solution approach
4. Timeline if applicable
5. Any questions for clarification
6. Relevant resources or documentation links
7. Encouragement and support

Make the response:
- Professional and helpful
- Specific to the issue
- Actionable
- Encouraging
- Include relevant emojis for engagement
- Keep it concise but comprehensive"""
            
            response = await self.ai_service.generate_response(response_prompt)
            
            if response.success:
                return {
                    'response': response.content,
                    'provider': response.provider,
                    'response_time': response.response_time,
                    'success': True
                }
            else:
                return {
                    'error': response.error,
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Error generating issue response: {e}")
            return {'error': str(e), 'success': False}
    
    async def suggest_labels(self, issue_title: str, issue_body: str) -> List[str]:
        """Suggest labels for an issue"""
        try:
            prompt = f"""Analyze this GitHub issue and suggest appropriate labels:

**Title:** {issue_title}
**Description:** {issue_body}

Suggest labels from these categories:
- Type: bug, enhancement, feature, question, documentation, help-wanted, good-first-issue
- Priority: low, medium, high, critical
- Status: triage, in-progress, needs-review, blocked
- Area: frontend, backend, api, database, security, performance, testing
- Complexity: easy, medium, hard

Return only the label names, one per line, without explanations."""
            
            response = await self.ai_service.generate_response(prompt)
            
            if response.success:
                # Parse labels from response
                labels = []
                for line in response.content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('-'):
                        # Clean up the label
                        label = re.sub(r'[^\w-]', '', line.lower())
                        if label:
                            labels.append(label)
                
                return labels[:10]  # Limit to 10 labels
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error suggesting labels: {e}")
            return []
    
    async def suggest_assignees(self, issue_title: str, issue_body: str) -> List[str]:
        """Suggest assignees for an issue"""
        try:
            prompt = f"""Analyze this GitHub issue and suggest potential assignees based on the content:

**Title:** {issue_title}
**Description:** {issue_body}

Consider:
1. Technical skills required
2. Component expertise
3. Issue complexity
4. Team member availability

Suggest 1-3 potential assignees with brief reasoning."""
            
            response = await self.ai_service.generate_response(prompt)
            
            if response.success:
                # Extract assignee suggestions from response
                assignees = []
                lines = response.content.split('\n')
                for line in lines:
                    if 'assignee' in line.lower() or 'developer' in line.lower() or 'engineer' in line.lower():
                        # Extract potential assignee names
                        words = line.split()
                        for word in words:
                            if word.isalpha() and len(word) > 2:
                                assignees.append(word.lower())
                
                return assignees[:3]  # Limit to 3 assignees
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error suggesting assignees: {e}")
            return []
    
    def post_github_comment(self, issue_number: int, comment: str) -> bool:
        """Post a comment to a GitHub issue"""
        try:
            if not self.github_token or not self.repository:
                logger.error("GitHub token or repository not set")
                return False
            
            url = f"https://api.github.com/repos/{self.repository}/issues/{issue_number}/comments"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'AMAS-AI-Issues-Responder'
            }
            
            data = {
                'body': comment
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                logger.info(f"Successfully posted comment to issue #{issue_number}")
                return True
            else:
                logger.error(f"Failed to post comment: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting GitHub comment: {e}")
            return False
    
    def add_issue_labels(self, issue_number: int, labels: List[str]) -> bool:
        """Add labels to a GitHub issue"""
        try:
            if not self.github_token or not self.repository:
                logger.error("GitHub token or repository not set")
                return False
            
            url = f"https://api.github.com/repos/{self.repository}/issues/{issue_number}/labels"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'AMAS-AI-Issues-Responder'
            }
            
            data = {
                'labels': labels
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Successfully added labels to issue #{issue_number}: {labels}")
                return True
            else:
                logger.error(f"Failed to add labels: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding issue labels: {e}")
            return False
    
    async def process_issue(self, issue_number: int, issue_title: str, issue_body: str, action: str) -> Dict[str, Any]:
        """Process a GitHub issue"""
        try:
            logger.info(f"Processing issue #{issue_number}: {issue_title}")
            
            # Analyze the issue
            analysis = await self.analyze_issue(issue_title, issue_body, issue_number)
            
            if not analysis.get('success'):
                return {
                    'success': False,
                    'error': analysis.get('error', 'Analysis failed'),
                    'issue_number': issue_number
                }
            
            # Generate response
            response = await self.generate_issue_response(issue_title, issue_body, issue_number)
            
            if not response.get('success'):
                return {
                    'success': False,
                    'error': response.get('error', 'Response generation failed'),
                    'issue_number': issue_number
                }
            
            # Suggest labels
            suggested_labels = await self.suggest_labels(issue_title, issue_body)
            
            # Suggest assignees
            suggested_assignees = await self.suggest_assignees(issue_title, issue_body)
            
            # Create comprehensive comment
            comment = f"""## 🤖 AI Analysis and Response

{response['response']}

### 📋 Suggested Labels
{', '.join([f'`{label}`' for label in suggested_labels]) if suggested_labels else 'No specific labels suggested'}

### 👥 Suggested Assignees
{', '.join(suggested_assignees) if suggested_assignees else 'No specific assignees suggested'}

### 🔍 Detailed Analysis
{analysis['analysis']}

---
*This response was generated by AMAS AI Issues Responder using {response['provider']}*"""
            
            # Post comment to GitHub
            comment_posted = self.post_github_comment(issue_number, comment)
            
            # Add labels if suggested
            labels_added = False
            if suggested_labels:
                labels_added = self.add_issue_labels(issue_number, suggested_labels)
            
            return {
                'success': True,
                'issue_number': issue_number,
                'comment_posted': comment_posted,
                'labels_added': labels_added,
                'suggested_labels': suggested_labels,
                'suggested_assignees': suggested_assignees,
                'analysis_provider': analysis.get('provider'),
                'response_provider': response.get('provider'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing issue #{issue_number}: {e}")
            return {
                'success': False,
                'error': str(e),
                'issue_number': issue_number
            }
    
    async def shutdown(self):
        """Shutdown the issues responder"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Issues Responder')
    parser.add_argument('--issue-number', type=int, required=True, help='GitHub issue number')
    parser.add_argument('--issue-title', required=True, help='Issue title')
    parser.add_argument('--issue-body', required=True, help='Issue body')
    parser.add_argument('--repository', required=True, help='GitHub repository (owner/repo)')
    parser.add_argument('--action', required=True, help='GitHub action (opened, edited, etc.)')
    parser.add_argument('--output', default='issue_response.json', help='Output file for response')
    
    args = parser.parse_args()
    
    responder = AIIssuesResponder()
    
    try:
        await responder.initialize()
        
        # Process the issue
        result = await responder.process_issue(
            args.issue_number,
            args.issue_title,
            args.issue_body,
            args.action
        )
        
        # Save result
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Print result
        if result.get('success'):
            print(f"✅ Successfully processed issue #{args.issue_number}")
            print(f"Comment posted: {result.get('comment_posted', False)}")
            print(f"Labels added: {result.get('labels_added', False)}")
            if result.get('suggested_labels'):
                print(f"Suggested labels: {', '.join(result['suggested_labels'])}")
            if result.get('suggested_assignees'):
                print(f"Suggested assignees: {', '.join(result['suggested_assignees'])}")
        else:
            print(f"❌ Failed to process issue #{args.issue_number}: {result.get('error', 'Unknown error')}")
        
        logger.info(f"Issue processing complete for issue #{args.issue_number}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    
    finally:
        await responder.shutdown()

if __name__ == "__main__":
    asyncio.run(main())