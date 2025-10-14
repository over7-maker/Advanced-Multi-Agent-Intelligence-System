#!/usr/bin/env python3
"""
AI Output Processor - Fixes truncated and malformed AI responses
Post-processes AI text output to ensure clean, valid commands
"""

import re
import json
import os
from typing import List, Dict, Any

class AIOutputProcessor:
    def __init__(self):
        self.valid_commands = [
            'pip install', 'pip uninstall', 'pip freeze', 'pip list',
            'python -m pip', 'conda install', 'apt install', 'yum install',
            'npm install', 'yarn add', 'composer install', 'gem install'
        ]
        
    def clean_ai_response(self, raw_text: str) -> str:
        """Clean and sanitize raw AI response text"""
        if not raw_text:
            return ""
            
        # Remove incomplete lines and truncation markers
        lines = raw_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip incomplete lines (ending with ... or ,)
            if line.strip().endswith('...') or line.strip().endswith(','):
                continue
                
            # Skip lines that look truncated
            if len(line.strip()) < 3:
                continue
                
            # Skip lines that are clearly incomplete commands
            if line.strip().endswith('pip install') or line.strip().endswith('python -m'):
                continue
                
            # Clean up the line
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        # Join lines and remove excessive whitespace
        result = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive empty lines
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
        
        # Limit total length to prevent extremely long responses
        if len(result) > 5000:
            result = result[:5000] + "\n\n... (truncated for readability)"
        
        return result
    
    def extract_shell_commands(self, text: str) -> List[str]:
        """Extract valid shell commands from AI response"""
        commands = []
        
        # Look for command patterns
        command_patterns = [
            r'```bash\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'`([^`]+)`',
            r'^\s*([a-zA-Z][a-zA-Z0-9\s\-_/\.]+)$'
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # Clean the command
                command = match.strip()
                if self.is_valid_command(command):
                    commands.append(command)
        
        # Also look for pip install patterns in the text
        pip_patterns = [
            r'pip install[^`\n]*',
            r'python -m pip install[^`\n]*',
            r'conda install[^`\n]*'
        ]
        
        for pattern in pip_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                command = match.strip()
                if self.is_valid_command(command):
                    commands.append(command)
        
        # Clean and validate commands
        cleaned_commands = []
        for cmd in commands:
            # Remove incomplete commands
            if not cmd.endswith('install') and not cmd.endswith('upgrade') and not cmd.endswith('uninstall'):
                # Check if command has proper arguments
                parts = cmd.split()
                if len(parts) >= 2:  # At least command + argument
                    cleaned_commands.append(cmd)
        
        return list(set(cleaned_commands))  # Remove duplicates
    
    def is_valid_command(self, command: str) -> bool:
        """Check if command is valid and safe"""
        if not command or len(command) < 5:
            return False
            
        # Check if it starts with a valid command
        command_lower = command.lower()
        for valid_cmd in self.valid_commands:
            if command_lower.startswith(valid_cmd.lower()):
                return True
                
        return False
    
    def process_ai_analysis(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI analysis response and clean up recommendations"""
        processed = ai_response.copy()
        
        # Clean the main analysis text
        if 'analysis' in processed:
            processed['analysis'] = self.clean_ai_response(processed['analysis'])
        
        # Process recommendations
        if 'recommendations' in processed:
            if isinstance(processed['recommendations'], dict):
                # Handle structured recommendations
                if 'immediate_actions' in processed['recommendations']:
                    actions = processed['recommendations']['immediate_actions']
                    if isinstance(actions, list):
                        cleaned_actions = []
                        for action in actions:
                            if isinstance(action, str):
                                cleaned = self.clean_ai_response(action)
                                if cleaned:
                                    cleaned_actions.append(cleaned)
                        processed['recommendations']['immediate_actions'] = cleaned_actions
                        
                        # Extract shell commands
                        commands = []
                        for action in cleaned_actions:
                            commands.extend(self.extract_shell_commands(action))
                        processed['shell_commands'] = commands
            elif isinstance(processed['recommendations'], list):
                # Handle simple list of recommendations
                cleaned_recommendations = []
                for rec in processed['recommendations']:
                    if isinstance(rec, str):
                        cleaned = self.clean_ai_response(rec)
                        if cleaned:
                            cleaned_recommendations.append(cleaned)
                processed['recommendations'] = cleaned_recommendations
                
                # Extract shell commands
                commands = []
                for rec in cleaned_recommendations:
                    commands.extend(self.extract_shell_commands(rec))
                processed['shell_commands'] = commands
        
        # Clean any other text fields
        text_fields = ['root_cause', 'analysis', 'response']
        for field in text_fields:
            if field in processed and isinstance(processed[field], str):
                processed[field] = self.clean_ai_response(processed[field])
        
        return processed
    
    def generate_clean_pr_comment(self, processed_analysis: Dict[str, Any]) -> str:
        """Generate a clean PR comment from processed analysis"""
        comment_lines = []
        
        # Header
        comment_lines.append("## 🤖 AI Dependency & Code-Fix Analysis")
        comment_lines.append("")
        
        # Status
        status = "✅ Completed" if processed_analysis.get('success', True) else "❌ Failed"
        comment_lines.append(f"**Status:** {status}")
        
        # Provider info
        provider = processed_analysis.get('metadata', {}).get('provider_used', 'Unknown')
        response_time = processed_analysis.get('metadata', {}).get('response_time', 0)
        comment_lines.append(f"**🤖 AI Provider:** {provider}")
        comment_lines.append(f"**⏱️ Response Time:** {response_time:.2f}s")
        comment_lines.append("")
        
        # Analysis
        if 'analysis' in processed_analysis:
            comment_lines.append("### 🔍 Analysis")
            comment_lines.append(f"**Root Cause:** {processed_analysis.get('root_cause', 'Unknown')}")
            comment_lines.append(f"**Priority:** {processed_analysis.get('priority', 'Unknown')}")
            comment_lines.append(f"**Confidence:** {processed_analysis.get('confidence', 0) * 100:.0f}%")
            comment_lines.append("")
            comment_lines.append(f"**Analysis:** {processed_analysis['analysis']}")
            comment_lines.append("")
        
        # Shell commands
        if 'shell_commands' in processed_analysis and processed_analysis['shell_commands']:
            comment_lines.append("### 📦 Immediate Actions")
            comment_lines.append("```bash")
            for cmd in processed_analysis['shell_commands'][:5]:  # Limit to 5 commands
                comment_lines.append(cmd)
            comment_lines.append("```")
            comment_lines.append("")
        
        # Recommendations
        if 'recommendations' in processed_analysis:
            if isinstance(processed_analysis['recommendations'], list):
                comment_lines.append("### 💡 Recommendations")
                for rec in processed_analysis['recommendations'][:5]:  # Limit to 5 recommendations
                    comment_lines.append(f"- {rec}")
                comment_lines.append("")
            elif isinstance(processed_analysis['recommendations'], dict):
                if 'immediate_actions' in processed_analysis['recommendations']:
                    comment_lines.append("### 💡 Immediate Actions")
                    for action in processed_analysis['recommendations']['immediate_actions'][:5]:
                        comment_lines.append(f"- {action}")
                    comment_lines.append("")
        
        # Footer
        comment_lines.append("---")
        comment_lines.append("")
        comment_lines.append("*🤖 Generated by AI Output Processor*")
        comment_lines.append("*Advanced Multi-Agent Intelligence System v3.0*")
        
        return '\n'.join(comment_lines)

def main():
    """Main function for testing"""
    processor = AIOutputProcessor()
    
    # Test with a sample AI response
    sample_response = {
        "metadata": {
            "provider_used": "nvidia",
            "response_time": 5.2
        },
        "analysis": "The error logs indicate missing modules, but the installed packages list doesn't show any obvious conflicts or versioning issues. However, upon closer inspection, I've found potential issues with version compatibility and missing dependencies.",
        "root_cause": "Incompatible versioning and missing dependencies",
        "priority": "high",
        "confidence": 0.7,
        "recommendations": {
            "immediate_actions": [
                "pip install httpx[http2]==0.28.1",
                "pip install datasets==2.10.1",
                "Update requirements.txt with pinned versions"
            ]
        }
    }
    
    # Process the response
    processed = processor.process_ai_analysis(sample_response)
    
    # Generate clean PR comment
    comment = processor.generate_clean_pr_comment(processed)
    
    print("Processed Analysis:")
    print(json.dumps(processed, indent=2))
    print("\n" + "="*50 + "\n")
    print("Clean PR Comment:")
    print(comment)

if __name__ == "__main__":
    main()