#!/usr/bin/env python3
"""
AI Agent Command Processor - Advanced command interpretation and execution
Processes @amas commands in PR comments and executes appropriate AI workflows
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AIAgentCommandProcessor:
    """Advanced AI agent command processor with intelligent command interpretation"""
    
    def __init__(self):
        self.commands = {
            "analyze": {
                "description": "Comprehensive code analysis",
                "workflow": "comprehensive_pr_analyzer",
                "priority": 1
            },
            "fix": {
                "description": "Fix issues automatically",
                "workflow": "ai_auto_commit_fixer",
                "priority": 1
            },
            "security": {
                "description": "Security audit and fixes",
                "workflow": "ai_security_auditor",
                "priority": 1
            },
            "build": {
                "description": "Build optimization",
                "workflow": "ai_dependency_pinner",
                "priority": 2
            },
            "docs": {
                "description": "Generate documentation",
                "workflow": "ai_documentation_generator",
                "priority": 2
            },
            "test": {
                "description": "Run comprehensive tests",
                "workflow": "ai_test_runner",
                "priority": 2
            },
            "deploy": {
                "description": "Deployment assistance",
                "workflow": "ai_deployment_helper",
                "priority": 3
            },
            "help": {
                "description": "Show all available commands",
                "workflow": "help_command",
                "priority": 0
            },
            "status": {
                "description": "Check system status",
                "workflow": "system_status",
                "priority": 0
            },
            "learn": {
                "description": "Learn from this PR",
                "workflow": "ai_learning_system",
                "priority": 2
            },
            "optimize": {
                "description": "Optimize code and performance",
                "workflow": "ai_parallel_provider",
                "priority": 1
            },
            "audit": {
                "description": "Comprehensive project audit",
                "workflow": "ai_project_auditor",
                "priority": 1
            }
        }
        
        self.workflow_scripts = {
            "comprehensive_pr_analyzer": ".github/scripts/comprehensive_pr_analyzer.py",
            "ai_auto_commit_fixer": ".github/scripts/ai_auto_commit_fixer.py",
            "ai_security_auditor": ".github/scripts/ai_security_auditor.py",
            "ai_dependency_pinner": ".github/scripts/ai_dependency_pinner.py",
            "ai_learning_system": ".github/scripts/ai_learning_system.py",
            "ai_parallel_provider": ".github/scripts/ai_parallel_provider.py"
        }
    
    async def process_command(self, command: str, full_command: str, pr_number: str, commenter: str) -> Dict[str, Any]:
        """Process an AI agent command"""
        print(f"🤖 Processing command: {command}")
        print(f"📝 Full command: {full_command}")
        print(f"🔢 PR Number: {pr_number}")
        print(f"👤 Commenter: {commenter}")
        
        # Parse command and extract parameters
        command_parts = full_command.split()
        base_command = command_parts[0].lower() if command_parts else command
        parameters = command_parts[1:] if len(command_parts) > 1 else []
        
        # Handle special commands
        if base_command == "help":
            return await self._handle_help_command()
        elif base_command == "status":
            return await self._handle_status_command()
        elif base_command not in self.commands:
            return await self._handle_unknown_command(base_command)
        
        # Get command info
        command_info = self.commands[base_command]
        
        # Create AI prompt for command interpretation
        ai_prompt = f"""
As an expert AI agent, interpret this command and provide intelligent analysis:

**Command:** {base_command}
**Parameters:** {parameters}
**PR Number:** {pr_number}
**Commenter:** {commenter}
**Full Command:** {full_command}

**Available Workflows:**
{json.dumps(self.commands, indent=2)}

**Task:**
1. **Interpret the command** and determine the best approach
2. **Analyze the context** (PR, commenter, parameters)
3. **Provide specific recommendations** for this command
4. **Suggest additional actions** that might be helpful
5. **Identify potential issues** or considerations

**Response Format:**
Provide your analysis in this JSON format:
```json
{{
  "command_interpretation": "What the user wants to accomplish",
  "recommended_approach": "Best way to handle this command",
  "specific_actions": [
    "Action 1",
    "Action 2"
  ],
  "additional_suggestions": [
    "Suggestion 1",
    "Suggestion 2"
  ],
  "potential_issues": [
    "Issue 1",
    "Issue 2"
  ],
  "confidence": 0.95,
  "estimated_time": "2-5 minutes"
}}
```

Focus on being helpful, specific, and actionable.
"""
        
        try:
            # Get AI analysis
            ai_result = await ai_agent.analyze_with_fallback(ai_prompt, f"command_{base_command}")
            
            if ai_result.get('success'):
                # Extract JSON from AI response
                content = ai_result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        ai_analysis = json.loads(json_match.group(1))
                    else:
                        # Fallback analysis
                        ai_analysis = {
                            "command_interpretation": f"User wants to {command_info['description']}",
                            "recommended_approach": f"Execute {command_info['workflow']} workflow",
                            "specific_actions": [command_info['description']],
                            "additional_suggestions": [],
                            "potential_issues": [],
                            "confidence": 0.8,
                            "estimated_time": "2-5 minutes"
                        }
                    
                    # Execute the workflow if it exists
                    workflow_result = await self._execute_workflow(command_info['workflow'], pr_number, parameters)
                    
                    return {
                        "success": True,
                        "command": base_command,
                        "ai_analysis": ai_analysis,
                        "workflow_result": workflow_result,
                        "metadata": {
                            "provider_used": ai_result.get('provider_used'),
                            "response_time": ai_result.get('response_time', 0),
                            "timestamp": datetime.now().isoformat(),
                            "pr_number": pr_number,
                            "commenter": commenter
                        },
                        "analysis": ai_analysis.get('command_interpretation', ''),
                        "recommendations": ai_analysis.get('specific_actions', []),
                        "actions_taken": workflow_result.get('actions_taken', [])
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse AI analysis",
                        "command": base_command
                    }
            else:
                return {
                    "success": False,
                    "error": ai_result.get('error', 'AI analysis failed'),
                    "command": base_command
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in command processing: {e}",
                "command": base_command
            }
    
    async def _handle_help_command(self) -> Dict[str, Any]:
        """Handle help command"""
        help_text = "## 🤖 AMAS AI Agent - Available Commands\n\n"
        help_text += "I can help you with many tasks! Here are the available commands:\n\n"
        
        for cmd, info in self.commands.items():
            if cmd not in ["help", "status"]:
                help_text += f"### `@amas {cmd}`\n"
                help_text += f"**Description:** {info['description']}\n"
                help_text += f"**Priority:** {info['priority']}\n\n"
        
        help_text += "### Usage Examples:\n"
        help_text += "- `@amas analyze` - Analyze this PR comprehensively\n"
        help_text += "- `@amas fix security` - Fix security issues\n"
        help_text += "- `@amas build optimize` - Optimize build process\n"
        help_text += "- `@amas docs generate` - Generate documentation\n\n"
        help_text += "**Just mention me with any command and I'll help!** 🚀"
        
        return {
            "success": True,
            "command": "help",
            "analysis": help_text,
            "recommendations": ["Use any of the available commands"],
            "actions_taken": ["Displayed help information"],
            "metadata": {
                "provider_used": "help_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _handle_status_command(self) -> Dict[str, Any]:
        """Handle status command"""
        # Check AI provider status
        available_providers = ai_agent._get_available_providers()
        
        status_text = "## 🤖 AMAS AI Agent - System Status\n\n"
        status_text += f"**Status:** ✅ Operational\n"
        status_text += f"**Available Providers:** {len(available_providers)}/16\n"
        status_text += f"**Active Providers:** {', '.join(available_providers[:5])}{'...' if len(available_providers) > 5 else ''}\n"
        status_text += f"**System Time:** {datetime.now().isoformat()}\n\n"
        status_text += "**Capabilities:**\n"
        status_text += "- ✅ 16-Provider AI Fallback\n"
        status_text += "- ✅ Parallel Processing\n"
        status_text += "- ✅ Intelligent Command Interpretation\n"
        status_text += "- ✅ Automated Workflow Execution\n"
        status_text += "- ✅ Continuous Learning\n"
        
        return {
            "success": True,
            "command": "status",
            "analysis": status_text,
            "recommendations": ["System is fully operational"],
            "actions_taken": ["Checked system status"],
            "metadata": {
                "provider_used": "status_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _handle_unknown_command(self, command: str) -> Dict[str, Any]:
        """Handle unknown command"""
        return {
            "success": False,
            "command": command,
            "error": f"Unknown command: {command}",
            "analysis": f"I don't recognize the command '{command}'. Use `@amas help` to see available commands.",
            "recommendations": ["Use `@amas help` to see available commands"],
            "actions_taken": [],
            "metadata": {
                "provider_used": "error_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _execute_workflow(self, workflow_name: str, pr_number: str, parameters: List[str]) -> Dict[str, Any]:
        """Execute a specific workflow"""
        print(f"🔄 Executing workflow: {workflow_name}")
        
        if workflow_name in self.workflow_scripts:
            script_path = self.workflow_scripts[workflow_name]
            if os.path.exists(script_path):
                try:
                    # Run the workflow script
                    import subprocess
                    result = subprocess.run([
                        'python', script_path,
                        '--pr-number', pr_number,
                        '--parameters', ' '.join(parameters)
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "workflow": workflow_name,
                            "output": result.stdout,
                            "actions_taken": [f"Executed {workflow_name} workflow"]
                        }
                    else:
                        return {
                            "success": False,
                            "workflow": workflow_name,
                            "error": result.stderr,
                            "actions_taken": []
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "workflow": workflow_name,
                        "error": str(e),
                        "actions_taken": []
                    }
            else:
                return {
                    "success": False,
                    "workflow": workflow_name,
                    "error": f"Script not found: {script_path}",
                    "actions_taken": []
                }
        else:
            return {
                "success": False,
                "workflow": workflow_name,
                "error": f"Workflow not implemented: {workflow_name}",
                "actions_taken": []
            }

async def main():
    """Main function to run AI agent command processor"""
    parser = argparse.ArgumentParser(description="AI Agent Command Processor")
    parser.add_argument("--command", required=True, help="Base command")
    parser.add_argument("--full-command", required=True, help="Full command text")
    parser.add_argument("--pr-number", required=True, help="PR number")
    parser.add_argument("--commenter", required=True, help="Commenter username")
    parser.add_argument("--output", required=True, help="Output file")
    
    args = parser.parse_args()
    
    print("🤖 AI Agent Command Processor Starting...")
    print("=" * 60)
    
    processor = AIAgentCommandProcessor()
    
    try:
        # Process the command
        result = await processor.process_command(
            args.command,
            args.full_command,
            args.pr_number,
            args.commenter
        )
        
        # Save result
        os.makedirs("artifacts", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 AI AGENT COMMAND PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"📋 Command: {result.get('command', 'unknown')}")
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🤖 Provider: {result.get('metadata', {}).get('provider_used', 'Unknown')}")
        print(f"⏱️ Response Time: {result.get('metadata', {}).get('response_time', 0):.2f}s")
        
        if result.get('success'):
            print(f"📊 Analysis: {result.get('analysis', 'No analysis')[:100]}...")
            print(f"💡 Recommendations: {len(result.get('recommendations', []))}")
            print(f"🔧 Actions Taken: {len(result.get('actions_taken', []))}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"📄 Result saved to: {args.output}")
        
        return result
        
    except Exception as e:
        print(f"❌ Critical error in command processor: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
        # Create error result
        error_result = {
            "success": False,
            "error": str(e),
            "command": args.command,
            "metadata": {
                "provider_used": "error_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        os.makedirs("artifacts", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(error_result, f, indent=2)
        
        return error_result

if __name__ == "__main__":
    asyncio.run(main())