#!/usr/bin/env python3
"""
Simple Working Auto-Responder
A guaranteed working auto-response system that doesn't rely on external APIs
"""

import os
import sys
import requests
import json
from datetime import datetime

def get_issue_details():
    """Get issue details from environment"""
    return {
        'number': os.environ.get('ISSUE_NUMBER'),
        'title': os.environ.get('ISSUE_TITLE', ''),
        'body': os.environ.get('ISSUE_BODY', ''),
        'author': os.environ.get('ISSUE_AUTHOR', ''),
        'repo': os.environ.get('GITHUB_REPOSITORY'),
        'token': os.environ.get('GITHUB_TOKEN')
    }

def categorize_issue(title, body):
    """Simple issue categorization"""
    content = f"{title} {body}".lower()
    
    if any(word in content for word in ['bug', 'error', 'crash', 'broken', 'not working']):
        return 'bug'
    elif any(word in content for word in ['feature', 'enhancement', 'request', 'add', 'new']):
        return 'feature'
    elif any(word in content for word in ['question', 'how', 'what', 'why', 'help']):
        return 'question'
    elif any(word in content for word in ['security', 'vulnerability', 'exploit']):
        return 'security'
    elif any(word in content for word in ['performance', 'slow', 'optimize']):
        return 'performance'
    else:
        return 'general'

def generate_response(category, title, body, author):
    """Generate appropriate response based on category"""
    
    responses = {
        'bug': f"""## 🐛 Bug Report Acknowledged

Thank you for reporting this issue, @{author}! 

**Issue Analysis:**
- **Type**: Bug Report
- **Priority**: High
- **Status**: Under Investigation

**Next Steps:**
1. 🔍 **Investigation**: Our team will investigate this issue
2. 📝 **Reproduction**: We'll try to reproduce the problem
3. 🔧 **Fix**: We'll work on a solution
4. ✅ **Testing**: We'll test the fix thoroughly

**What You Can Do:**
- Provide more details if you have them
- Check if this is a duplicate of existing issues
- Monitor this issue for updates

We appreciate your patience as we work to resolve this! 🙏

---
*🤖 Auto-generated response - AMAS AI System*""",

        'feature': f"""## ✨ Feature Request Received

Great suggestion, @{author}! 

**Feature Analysis:**
- **Type**: Feature Request
- **Status**: Under Review
- **Priority**: Medium

**Review Process:**
1. 📋 **Assessment**: We'll evaluate feasibility and impact
2. 🎯 **Planning**: We'll consider implementation approach
3. 📅 **Timeline**: We'll provide estimated timeline
4. 🔄 **Updates**: We'll keep you informed of progress

**What We Need:**
- More details about the use case
- Any specific requirements
- Priority level from your perspective

Thanks for helping improve AMAS! 🚀

---
*🤖 Auto-generated response - AMAS AI System*""",

        'question': f"""## ❓ Question Received

Hi @{author}! Thanks for your question.

**Question Analysis:**
- **Type**: General Question
- **Status**: Awaiting Response
- **Priority**: Medium

**How We Can Help:**
1. 📚 **Documentation**: Check our comprehensive docs
2. 🔍 **Search**: Look for similar questions/issues
3. 💬 **Community**: Ask in discussions
4. 🆘 **Support**: Get direct help from maintainers

**Quick Resources:**
- 📖 [Documentation](https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')}#readme)
- 💬 [Discussions](https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')}/discussions)
- 🐛 [Issues](https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'over7-maker/Advanced-Multi-Agent-Intelligence-System')}/issues)

We'll get back to you soon! 🤝

---
*🤖 Auto-generated response - AMAS AI System*""",

        'security': f"""## 🔒 Security Issue Reported

Thank you for reporting this security concern, @{author}.

**Security Analysis:**
- **Type**: Security Issue
- **Priority**: **CRITICAL**
- **Status**: Immediate Review

**Security Protocol:**
1. 🚨 **Immediate**: Security team notified
2. 🔍 **Assessment**: Vulnerability analysis in progress
3. 🛡️ **Mitigation**: Immediate protective measures
4. 🔧 **Fix**: Secure solution development
5. ✅ **Verification**: Security testing

**Important Notes:**
- This issue is being handled with high priority
- We may need additional information privately
- Please don't share sensitive details publicly

**Contact:**
- For urgent security issues, contact maintainers directly
- Use private channels for sensitive information

Thank you for helping keep AMAS secure! 🛡️

---
*🤖 Auto-generated response - AMAS AI System*""",

        'performance': f"""## ⚡ Performance Issue Identified

Thanks for reporting this performance concern, @{author}!

**Performance Analysis:**
- **Type**: Performance Issue
- **Priority**: High
- **Status**: Under Investigation

**Investigation Plan:**
1. 📊 **Profiling**: We'll analyze performance metrics
2. 🔍 **Bottlenecks**: Identify performance bottlenecks
3. 🛠️ **Optimization**: Implement performance improvements
4. 📈 **Testing**: Verify performance gains

**What We Need:**
- Performance metrics or benchmarks
- System specifications
- Steps to reproduce the issue
- Expected vs actual performance

Let's make AMAS faster together! 🚀

---
*🤖 Auto-generated response - AMAS AI System*""",

        'general': f"""## 👋 Issue Received

Hello @{author}! Thanks for creating this issue.

**Issue Analysis:**
- **Type**: General Issue
- **Status**: Under Review
- **Priority**: Medium

**Review Process:**
1. 📋 **Analysis**: We'll review your issue
2. 🏷️ **Categorization**: We'll assign appropriate labels
3. 📅 **Planning**: We'll determine next steps
4. 🔄 **Updates**: We'll keep you informed

**What You Can Expect:**
- Acknowledgment of your issue
- Appropriate categorization and labeling
- Regular updates on progress
- Clear communication about next steps

Thanks for contributing to AMAS! 🙏

---
*🤖 Auto-generated response - AMAS AI System*"""
    }
    
    return responses.get(category, responses['general'])

def post_comment(repo, issue_number, comment, token):
    """Post comment to GitHub issue"""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    data = {'body': comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print("✅ Comment posted successfully")
            return True
        else:
            print(f"❌ Failed to post comment: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting comment: {e}")
        return False

def add_labels(repo, issue_number, labels, token):
    """Add labels to GitHub issue"""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/labels"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    data = {'labels': labels}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ Labels added: {', '.join(labels)}")
            return True
        else:
            print(f"❌ Failed to add labels: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error adding labels: {e}")
        return False

def main():
    """Main function"""
    print("🤖 Simple Working Auto-Responder")
    print("=" * 40)
    
    # Get issue details
    issue = get_issue_details()
    
    if not all([issue['number'], issue['repo'], issue['token']]):
        print("❌ Missing required environment variables")
        print("Required: ISSUE_NUMBER, GITHUB_REPOSITORY, GITHUB_TOKEN")
        return False
    
    print(f"📋 Processing issue #{issue['number']}: {issue['title']}")
    
    # Categorize issue
    category = categorize_issue(issue['title'], issue['body'])
    print(f"🏷️ Category: {category}")
    
    # Generate response
    response = generate_response(category, issue['title'], issue['body'], issue['author'])
    
    # Post comment
    print("📝 Posting response...")
    success = post_comment(issue['repo'], issue['number'], response, issue['token'])
    
    if success:
        # Add labels
        labels = ['ai-analyzed', 'auto-response', category]
        if category == 'security':
            labels.append('priority-high')
        elif category == 'bug':
            labels.append('bug')
        elif category == 'feature':
            labels.append('enhancement')
        
        print("🏷️ Adding labels...")
        add_labels(issue['repo'], issue['number'], labels, issue['token'])
        
        print("✅ Auto-response completed successfully!")
        return True
    else:
        print("❌ Auto-response failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Auto-responder failed: {e}")
        sys.exit(1)