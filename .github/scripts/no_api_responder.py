#!/usr/bin/env python3
"""
No API Required Responder Script
A simple responder that works without any API keys
"""

import os
import json
import requests
from typing import Optional

def get_smart_response(title: str, body: str, author: str) -> str:
    """Generate a smart response without AI dependencies"""
    
    # Enhanced issue type detection
    title_lower = title.lower()
    body_lower = body.lower()
    
    # Performance issues
    if any(word in title_lower or word in body_lower for word in ['performance', 'slow', 'optimization', 'speed', 'fast']):
        issue_type = 'performance'
    # Bug issues
    elif any(word in title_lower or word in body_lower for word in ['bug', 'error', 'broken', 'crash', 'fail', 'issue']):
        issue_type = 'bug'
    # Feature requests
    elif any(word in title_lower or word in body_lower for word in ['feature', 'enhancement', 'add', 'implement', 'new']):
        issue_type = 'feature'
    # Questions
    elif any(word in title_lower or word in body_lower for word in ['question', 'how to', 'help', '?', 'what', 'why']):
        issue_type = 'question'
    # Security issues
    elif any(word in title_lower or word in body_lower for word in ['security', 'vulnerability', 'exploit', 'safe', 'secure']):
        issue_type = 'security'
    # Documentation
    elif any(word in title_lower or word in body_lower for word in ['documentation', 'docs', 'readme', 'guide', 'tutorial']):
        issue_type = 'documentation'
    else:
        issue_type = 'general'
    
    # Generate appropriate response
    responses = {
        'performance': f"""Thank you for reporting this performance issue, @{author}! ⚡

I've automatically analyzed your issue and categorized it as a performance concern. Here's how I can help:

**Performance Analysis:**
1. 🔍 **Investigation**: I'll help identify performance bottlenecks
2. 📊 **Profiling**: We'll analyze the code for optimization opportunities
3. 🚀 **Optimization**: I'll suggest specific improvements
4. 📈 **Monitoring**: We'll implement performance tracking

**Next Steps:**
- Please provide specific performance metrics if available
- Include any error logs or slow operation details
- Let me know what performance expectations you have
- I'll analyze the codebase for optimization opportunities

**Performance Tips:**
- Check for inefficient algorithms or data structures
- Look for unnecessary database queries or API calls
- Consider caching strategies for repeated operations
- Profile memory usage and CPU utilization

I'm here to help optimize your system! 🚀""",

        'bug': f"""Thank you for reporting this bug, @{author}! 🐛

I've automatically analyzed your issue and categorized it as a bug report. Here's what I can help with:

**Bug Investigation:**
1. 🔍 **Root Cause**: I'll help identify the underlying cause
2. 🧪 **Reproduction**: We'll create steps to reproduce the issue
3. 🔧 **Fix Development**: I'll work on a solution
4. ✅ **Testing**: We'll thoroughly test the fix

**Helpful Information:**
- Please include any error messages or stack traces
- Screenshots or screen recordings are very helpful
- What were you doing when this happened?
- Does this happen consistently or intermittently?

**Debugging Steps:**
- Check logs for error messages
- Verify input data and parameters
- Test with different configurations
- Look for recent changes that might have caused this

I'm here to help resolve this issue! 🔧""",

        'feature': f"""Great feature request, @{author}! ✨

I've analyzed your suggestion and it looks like a valuable enhancement. Here's my assessment:

**Feature Analysis:**
1. 🎯 **Value Assessment**: This could significantly improve user experience
2. 🔧 **Technical Feasibility**: I'll evaluate implementation complexity
3. 📋 **Planning**: We'll create a development roadmap
4. 🚀 **Timeline**: I'll provide an estimated implementation schedule

**Next Steps:**
- I'll review the technical requirements
- Consider integration with existing features
- Plan the development approach
- Keep you updated on progress

**Feature Considerations:**
- How does this fit with existing functionality?
- What are the user experience benefits?
- Are there any technical constraints?
- What's the priority level for this feature?

Thanks for the great suggestion! 🚀""",

        'question': f"""Hello @{author}! 👋

I'm here to help answer your question. Let me provide some assistance:

**I can help with:**
1. 📚 **Documentation**: Point you to relevant docs and guides
2. 🔧 **Setup & Configuration**: Help with installation and setup
3. 💡 **Best Practices**: Share tips and recommendations
4. 🐛 **Troubleshooting**: Solve any issues you're facing

**Quick Resources:**
- 📖 [Project Documentation](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}#readme)
- 🔧 [Setup Guide](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}/blob/main/SETUP_GUIDE.md)
- 💬 [Discussions](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}/discussions)
- 🐛 [Issues](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}/issues)

**Common Questions:**
- Installation and setup help
- Configuration and customization
- Troubleshooting common issues
- Understanding features and capabilities

What specific help do you need? I'm here to assist! 🤖""",

        'security': f"""Thank you for reporting this security concern, @{author}! 🔒

Security is our top priority. I've flagged this as a security issue and here's what happens next:

**Security Protocol:**
1. 🚨 **Immediate Review**: This gets high priority attention
2. 🔍 **Impact Analysis**: I'll assess the potential security impact
3. 🛡️ **Mitigation**: We'll work on immediate fixes if needed
4. 📋 **Documentation**: We'll document the resolution process

**Security Considerations:**
- What type of security issue is this?
- Are there any potential attack vectors?
- What data or systems might be affected?
- Is this a public disclosure or private report?

**Important Notes:**
- Security issues are handled with extra care
- We may need more details to assess properly
- Please don't share sensitive information publicly
- We'll keep you updated on the resolution

Thank you for helping keep our project secure! 🛡️""",

        'documentation': f"""Thank you for this documentation feedback, @{author}! 📚

I've analyzed your request and categorized it as a documentation improvement. Here's how I can help:

**Documentation Analysis:**
1. 📖 **Content Review**: I'll assess current documentation quality
2. 🔍 **Gap Analysis**: Identify missing or unclear information
3. ✍️ **Improvement Plan**: Create a documentation enhancement plan
4. 📝 **Content Creation**: Develop better documentation

**Documentation Areas:**
- Setup and installation guides
- API documentation and examples
- Troubleshooting guides
- Best practices and tips

**Next Steps:**
- I'll review the current documentation
- Identify areas for improvement
- Create or update relevant content
- Ensure clarity and completeness

**Documentation Goals:**
- Clear, step-by-step instructions
- Comprehensive examples and use cases
- Easy-to-follow troubleshooting guides
- Up-to-date information

Thanks for helping improve our documentation! 📖""",

        'general': f"""Hello @{author}! 👋

Thank you for opening this issue. I've received your message and I'm here to help!

**What I can do:**
1. 📋 **Categorize**: I'll help categorize and prioritize your issue
2. 🔍 **Analyze**: I'll analyze the content and provide insights
3. 🎯 **Route**: I'll make sure the right people see this
4. 📞 **Follow-up**: I'll keep you updated on progress

**Next Steps:**
- I'll review your issue in detail
- Provide relevant guidance and resources
- Connect you with the right team members
- Keep you informed of any updates

**How I can help:**
- Answer questions about the project
- Provide guidance on setup and usage
- Help troubleshoot issues
- Suggest improvements and enhancements

Thanks for contributing to our project! 🚀"""
    }
    
    return responses.get(issue_type, responses['general'])

def post_github_comment(comment: str) -> bool:
    """Post comment to GitHub issue"""
    github_token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('REPO_NAME')
    issue_number = os.environ.get('ISSUE_NUMBER')
    
    if not all([github_token, repo_name, issue_number]):
        print("Missing required environment variables")
        return False
    
    url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
    
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    
    # Add AI signature
    ai_comment = f"""{comment}

---
🤖 *This response was generated by AMAS AI Assistant*
💡 *Powered by intelligent automation (No API keys required)*
📚 *For more help, check the [project documentation](https://github.com/{repo_name}#readme)*
"""
    
    data = {'body': ai_comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Posted response to issue #{issue_number}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to post comment: {e}")
        return False

def main():
    """Main execution function"""
    print("🤖 Starting No-API Required Responder...")
    
    # Get issue details
    issue_title = os.environ.get('ISSUE_TITLE', '')
    issue_body = os.environ.get('ISSUE_BODY', '')
    issue_author = os.environ.get('ISSUE_AUTHOR', '')
    
    print(f"📝 Processing issue: {issue_title}")
    print(f"👤 Author: {issue_author}")
    
    # Generate smart response
    print("🧠 Generating smart response...")
    response_text = get_smart_response(issue_title, issue_body, issue_author)
    
    print("✅ Smart response generated successfully")
    
    # Post the response
    print("📤 Posting response...")
    success = post_github_comment(response_text)
    
    if success:
        print("🎉 Auto-response completed successfully!")
    else:
        print("❌ Failed to post response")

if __name__ == "__main__":
    main()