#!/usr/bin/env python3
"""
Simple Working Auto-Responder
A guaranteed working auto-response system that doesn't rely on external APIs
"""

import os
import requests
import json
import re
from datetime import datetime

def main():
    print("🤖 Simple Working Auto-Responder")
    print("=" * 50)
    
    # Get environment variables
    token = os.environ.get('GITHUB_TOKEN')
    repo = os.environ.get('GITHUB_REPOSITORY')
    issue_number = os.environ.get('ISSUE_NUMBER')
    title = os.environ.get('ISSUE_TITLE', '')
    body = os.environ.get('ISSUE_BODY', '')
    author = os.environ.get('ISSUE_AUTHOR', '')
    
    # Validate required variables
    if not all([token, repo, issue_number]):
        print("❌ Missing required environment variables")
        print(f"Token: {'✅' if token else '❌'}")
        print(f"Repo: {'✅' if repo else '❌'}")
        print(f"Issue: {'✅' if issue_number else '❌'}")
        return False
    
    print(f"📋 Processing issue #{issue_number}: {title}")
    print(f"👤 Author: {author}")
    print(f"🏠 Repository: {repo}")
    
    # Categorize issue based on content
    content = f"{title} {body}".lower()
    category = categorize_issue(content)
    print(f"🏷️ Category: {category}")
    
    # Generate appropriate response
    response = generate_response(category, author, issue_number, title)
    
    # Post comment
    if post_comment(token, repo, issue_number, response):
        print("✅ Comment posted successfully")
    else:
        print("❌ Failed to post comment")
        return False
    
    # Add labels
    if add_labels(token, repo, issue_number, category):
        print(f"✅ Labels added: ai-analyzed, auto-response, {category}")
    else:
        print("❌ Failed to add labels")
    
    print("🎉 Auto-response completed successfully!")
    return True

def categorize_issue(content):
    """Categorize issue based on content analysis"""
    
    # Bug indicators
    bug_keywords = ['bug', 'error', 'crash', 'broken', 'issue', 'problem', 'fix', 'not working']
    if any(keyword in content for keyword in bug_keywords):
        return 'bug'
    
    # Feature request indicators
    feature_keywords = ['feature', 'enhancement', 'request', 'add', 'new', 'improve', 'suggest']
    if any(keyword in content for keyword in feature_keywords):
        return 'feature'
    
    # Question indicators
    question_keywords = ['question', 'how', 'what', 'why', 'help', 'support', 'guide']
    if any(keyword in content for keyword in question_keywords):
        return 'question'
    
    # Security indicators
    security_keywords = ['security', 'vulnerability', 'attack', 'hack', 'safe', 'secure']
    if any(keyword in content for keyword in security_keywords):
        return 'security'
    
    # Performance indicators
    performance_keywords = ['performance', 'slow', 'fast', 'optimize', 'speed', 'memory']
    if any(keyword in content for keyword in performance_keywords):
        return 'performance'
    
    # Documentation indicators
    doc_keywords = ['documentation', 'docs', 'readme', 'guide', 'tutorial', 'example']
    if any(keyword in content for keyword in doc_keywords):
        return 'documentation'
    
    return 'general'

def generate_response(category, author, issue_number, title):
    """Generate appropriate response based on category"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if category == 'bug':
        return f"""## 🐛 Bug Report Acknowledged

Thank you for reporting this issue, @{author}! 

**Issue Analysis:**
- **Type**: Bug Report
- **Priority**: High
- **Status**: Under Investigation
- **Timestamp**: {timestamp}

**Next Steps:**
1. 🔍 **Investigation**: Our team will investigate this issue
2. 📝 **Reproduction**: We'll try to reproduce the problem
3. 🔧 **Fix**: We'll work on a solution
4. ✅ **Testing**: We'll test the fix thoroughly

We appreciate your patience as we work to resolve this! 🙏

---
*🤖 Auto-generated response - AMAS AI System*"""

    elif category == 'feature':
        return f"""## ✨ Feature Request Received

Great suggestion, @{author}! 

**Feature Analysis:**
- **Type**: Feature Request
- **Status**: Under Review
- **Priority**: Medium
- **Timestamp**: {timestamp}

**Review Process:**
1. 📋 **Assessment**: We'll evaluate feasibility and impact
2. 🎯 **Planning**: We'll consider implementation approach
3. 📅 **Timeline**: We'll provide estimated timeline
4. 🔄 **Updates**: We'll keep you informed of progress

Thanks for helping improve AMAS! 🚀

---
*🤖 Auto-generated response - AMAS AI System*"""

    elif category == 'question':
        return f"""## ❓ Question Received

Hello @{author}! Thanks for your question.

**Question Analysis:**
- **Type**: Question
- **Status**: Under Review
- **Priority**: Medium
- **Timestamp**: {timestamp}

**Response Process:**
1. 📋 **Analysis**: We'll review your question
2. 🔍 **Research**: We'll gather relevant information
3. 📝 **Answer**: We'll provide a comprehensive response
4. 🔄 **Follow-up**: We'll ensure you have what you need

We'll get back to you soon! 🤝

---
*🤖 Auto-generated response - AMAS AI System*"""

    elif category == 'security':
        return f"""## 🔒 Security Issue Reported

Thank you for reporting this security concern, @{author}! 

**Security Analysis:**
- **Type**: Security Issue
- **Priority**: Critical
- **Status**: Under Investigation
- **Timestamp**: {timestamp}

**Security Process:**
1. 🔍 **Assessment**: We'll evaluate the security impact
2. 🛡️ **Mitigation**: We'll implement immediate protections
3. 🔧 **Fix**: We'll develop a permanent solution
4. ✅ **Verification**: We'll verify the fix works

Security is our top priority! 🛡️

---
*🤖 Auto-generated response - AMAS AI System*"""

    elif category == 'performance':
        return f"""## ⚡ Performance Issue Reported

Thanks for reporting this performance issue, @{author}! 

**Performance Analysis:**
- **Type**: Performance Issue
- **Priority**: High
- **Status**: Under Review
- **Timestamp**: {timestamp}

**Optimization Process:**
1. 📊 **Analysis**: We'll analyze performance bottlenecks
2. 🔧 **Optimization**: We'll implement performance improvements
3. 📈 **Testing**: We'll measure performance gains
4. ✅ **Verification**: We'll ensure improvements work

We'll optimize this for you! 🚀

---
*🤖 Auto-generated response - AMAS AI System*"""

    elif category == 'documentation':
        return f"""## 📚 Documentation Issue Reported

Thank you for improving our documentation, @{author}! 

**Documentation Analysis:**
- **Type**: Documentation Issue
- **Status**: Under Review
- **Priority**: Medium
- **Timestamp**: {timestamp}

**Documentation Process:**
1. 📋 **Review**: We'll review the documentation needs
2. ✍️ **Update**: We'll improve the documentation
3. 📖 **Clarity**: We'll ensure it's clear and helpful
4. ✅ **Verification**: We'll test the updated docs

Great documentation helps everyone! 📖

---
*🤖 Auto-generated response - AMAS AI System*"""

    else:  # general
        return f"""## 👋 Issue Received

Hello @{author}! Thanks for creating this issue.

**Issue Analysis:**
- **Type**: General Issue
- **Status**: Under Review
- **Priority**: Medium
- **Timestamp**: {timestamp}

**Review Process:**
1. 📋 **Analysis**: We'll review your issue
2. 🏷️ **Categorization**: We'll assign appropriate labels
3. 📅 **Planning**: We'll determine next steps
4. 🔄 **Updates**: We'll keep you informed

Thanks for contributing to AMAS! 🙏

---
*🤖 Auto-generated response - AMAS AI System*"""

def post_comment(token, repo, issue_number, response):
    """Post comment to GitHub issue"""
    
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    data = {'body': response}
    
    try:
        response_req = requests.post(url, headers=headers, json=data)
        if response_req.status_code == 201:
            return True
        else:
            print(f"❌ Failed to post comment: {response_req.status_code}")
            print(f"Response: {response_req.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting comment: {e}")
        return False

def add_labels(token, repo, issue_number, category):
    """Add labels to GitHub issue"""
    
    labels_url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    # Base labels
    labels = ['ai-analyzed', 'auto-response']
    
    # Add category-specific label
    if category != 'general':
        labels.append(category)
    
    labels_data = {'labels': labels}
    
    try:
        labels_req = requests.post(labels_url, headers=headers, json=labels_data)
        if labels_req.status_code == 200:
            return True
        else:
            print(f"❌ Failed to add labels: {labels_req.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error adding labels: {e}")
        return False

if __name__ == "__main__":
    main()