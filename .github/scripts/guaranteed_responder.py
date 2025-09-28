#!/usr/bin/env python3
"""
Guaranteed Auto Responder Script
A simple, reliable auto-responder that always works
"""

import os
import json
import requests
from typing import Optional

def get_simple_response(title: str, body: str, author: str) -> str:
    """Generate a simple response without AI dependencies"""
    
    # Basic issue type detection
    title_lower = title.lower()
    body_lower = body.lower()
    
    if any(word in title_lower or word in body_lower for word in ['bug', 'error', 'broken', 'crash', 'fail']):
        issue_type = 'bug'
    elif any(word in title_lower or word in body_lower for word in ['feature', 'enhancement', 'add', 'implement']):
        issue_type = 'feature'
    elif any(word in title_lower or word in body_lower for word in ['question', 'how to', 'help', '?']):
        issue_type = 'question'
    elif any(word in title_lower or word in body_lower for word in ['security', 'vulnerability', 'exploit']):
        issue_type = 'security'
    else:
        issue_type = 'general'
    
    # Generate appropriate response
    responses = {
        'bug': f"""Thank you for reporting this bug, @{author}! 🐛

I've automatically analyzed your issue and categorized it as a bug report. Here's what I can help with:

**Next Steps:**
1. 🔍 **Investigation**: I'll help investigate the root cause
2. 🧪 **Reproduction**: Can you provide steps to reproduce this issue?
3. 🔧 **Fix**: Once identified, I'll work on a solution
4. ✅ **Testing**: We'll test the fix thoroughly

**Helpful Information:**
- Please include any error messages or logs
- Screenshots are very helpful
- What were you doing when this happened?

I'm here to help resolve this issue! 🤖""",

        'feature': f"""Great feature request, @{author}! ✨

I've analyzed your suggestion and it looks like a valuable enhancement. Here's my assessment:

**Feature Analysis:**
1. 🎯 **Value**: This could significantly improve the user experience
2. 🔧 **Implementation**: I'll evaluate the technical feasibility
3. 📋 **Planning**: We'll need to plan the development approach
4. 🚀 **Timeline**: I'll provide an estimated timeline

**Next Steps:**
- I'll review the technical requirements
- Consider integration with existing features
- Plan the development roadmap
- Keep you updated on progress

Thanks for the great suggestion! 🚀""",

        'question': f"""Hello @{author}! 👋

I'm here to help answer your question. Let me provide some assistance:

**I can help with:**
1. 📚 **Documentation**: Point you to relevant docs
2. 🔧 **Setup**: Help with installation and configuration
3. 💡 **Best Practices**: Share tips and recommendations
4. 🐛 **Troubleshooting**: Solve any issues you're facing

**Quick Resources:**
- 📖 [Project Documentation](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}#readme)
- 🔧 [Setup Guide](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}/blob/main/SETUP_GUIDE.md)
- 💬 [Discussions](https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}/discussions)

What specific help do you need? I'm here to assist! 🤖""",

        'security': f"""Thank you for reporting this security concern, @{author}! 🔒

Security is our top priority. I've flagged this as a security issue and here's what happens next:

**Security Protocol:**
1. 🚨 **Immediate Review**: This gets high priority attention
2. 🔍 **Analysis**: I'll analyze the potential impact
3. 🛡️ **Mitigation**: We'll work on immediate fixes if needed
4. 📋 **Documentation**: We'll document the resolution

**Important Notes:**
- Security issues are handled with extra care
- We may need more details to assess properly
- Please don't share sensitive information publicly
- We'll keep you updated on the resolution

Thank you for helping keep our project secure! 🛡️""",

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

Thanks for contributing to our project! 🚀"""
    }
    
    return responses.get(issue_type, responses['general'])

def try_ai_response(title: str, body: str, author: str) -> Optional[str]:
    """Try to get AI response if API keys are available"""
    try:
        import openai
        
        # Try OpenRouter first
        openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        if openrouter_key:
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
            )
            
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": f"https://github.com/{os.environ.get('REPO_NAME', 'unknown/repo')}",
                    "X-Title": "AMAS AI Assistant",
                },
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for the AMAS project. Provide concise, helpful responses to GitHub issues."},
                    {"role": "user", "content": f"Issue: {title}\n\nDescription: {body}\n\nAuthor: {author}\n\nPlease provide a helpful response."}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        # Try DeepSeek direct API
        deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        if deepseek_key:
            client = openai.OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=deepseek_key,
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for the AMAS project. Provide concise, helpful responses to GitHub issues."},
                    {"role": "user", "content": f"Issue: {title}\n\nDescription: {body}\n\nAuthor: {author}\n\nPlease provide a helpful response."}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
            
    except Exception as e:
        print(f"AI response failed: {e}")
        return None
    
    return None

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
💡 *Powered by intelligent automation*
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
    print("🤖 Starting Guaranteed Auto Responder...")
    
    # Get issue details
    issue_title = os.environ.get('ISSUE_TITLE', '')
    issue_body = os.environ.get('ISSUE_BODY', '')
    issue_author = os.environ.get('ISSUE_AUTHOR', '')
    
    print(f"📝 Processing issue: {issue_title}")
    print(f"👤 Author: {issue_author}")
    
    # Try AI response first
    print("🧠 Attempting AI response...")
    ai_response = try_ai_response(issue_title, issue_body, issue_author)
    
    if ai_response:
        print("✅ AI response generated successfully")
        response_text = ai_response
    else:
        print("⚠️ AI response failed, using simple response")
        response_text = get_simple_response(issue_title, issue_body, issue_author)
    
    # Post the response
    print("📤 Posting response...")
    success = post_github_comment(response_text)
    
    if success:
        print("🎉 Auto-response completed successfully!")
    else:
        print("❌ Failed to post response")

if __name__ == "__main__":
    main()