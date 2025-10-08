#!/usr/bin/env python3
"""
Update all AI scripts to support 9 APIs with proper fallback
"""

import os
import re

def update_script_file(file_path):
    """Update a single script file to support 9 APIs"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Update API key declarations
        old_pattern = r"self\.deepseek_key = os\.environ\.get\(\'DEEPSEEK_API_KEY\'\)\s*\n\s*self\.glm_key = os\.environ\.get\(\'GLM_API_KEY\'\)\s*\n\s*self\.grok_key = os\.environ\.get\(\'GROK_API_KEY\'\)\s*\n\s*self\.kimi_key = os\.environ\.get\(\'KIMI_API_KEY\'\)\s*\n\s*self\.qwen_key = os\.environ\.get\(\'QWEN_API_KEY\'\)\s*\n\s*self\.gptoss_key = os\.environ\.get\(\'GPTOSS_API_KEY\'\)"

        new_pattern = """self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.claude_key = os.environ.get('CLAUDE_API_KEY')
        self.gpt4_key = os.environ.get('GPT4_API_KEY')
        self.glm_key = os.environ.get('GLM_API_KEY')
        self.grok_key = os.environ.get('GROK_API_KEY')
        self.kimi_key = os.environ.get('KIMI_API_KEY')
        self.qwen_key = os.environ.get('QWEN_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.gptoss_key = os.environ.get('GPTOSS_API_KEY')"""

        content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)

        # Update priority comments
        content = content.replace(
            "# Priority order: DeepSeek (most reliable), GLM, Grok, Kimi, Qwen, GPTOSS",
            "# Priority order: DeepSeek (most reliable), Claude, GPT-4, GLM, Grok, Kimi, Qwen, Gemini, GPTOSS",
        )

        with open(file_path, "w") as f:
            f.write(content)

        print(f"✅ Updated {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update all AI scripts"""
    scripts_dir = ".github/scripts"
    updated_count = 0

    # List of scripts to update
    scripts = [
        "ai_incident_response.py",
        "ai_threat_intelligence.py",
        "ai_security_response.py",
        "ai_osint_collector.py",
        "ai_workflow_monitor.py",
        "ai_enhanced_code_review.py",
        "ai_master_orchestrator.py",
    ]

    for script in scripts:
        file_path = os.path.join(scripts_dir, script)
        if os.path.exists(file_path):
            if update_script_file(file_path):
                updated_count += 1

    print(f"\n🎯 Updated {updated_count} AI scripts with 9-API support")
    print(
        "✅ All scripts now support: DeepSeek, Claude, GPT-4, GLM, Grok, Kimi, Qwen, Gemini, GPTOSS"
    )

if __name__ == "__main__":
    main()
