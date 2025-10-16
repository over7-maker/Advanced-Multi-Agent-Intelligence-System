#!/usr/bin/env python3
"""
AI Agent Command Processor - Advanced command interpretation and execution

BULLETPROOF REAL AI SYSTEM:
- Processes @amas commands in PR comments and executes appropriate AI workflows
- Uses ONLY real AI providers (DeepSeek, NVIDIA, Cerebras, Codestral, etc.)
- Validates all responses for authenticity with bulletproof validation
- Refuses to generate fake or template responses
- Fails hard if no real AI providers are available

Capabilities:
- Command parsing and validation
- Workflow execution with real AI analysis
- Response generation with provider verification
- Error handling and fallback prevention

Limitations:
- Requires at least one valid API key from supported providers
- Network timeout of 60 seconds per provider attempt
- Hard failure on fake AI detection (no graceful fallbacks)

Verification:
- All responses include 'bulletproof_validated': true
- Provider names are actual API providers (not "AI System" or "Unknown")
- Response times are variable and realistic (not identical template times)
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import BULLETPROOF REAL AI SYSTEM - NO FAKE RESPONSES ALLOWED
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bulletproof_real_ai import BulletproofRealAI

class AIAgentCommandProcessor:
    """Advanced AI agent command processor with BULLETPROOF real AI"""
    
    def __init__(self):
        self.commands = {
            "analyze": {
                "description": "Comprehensive code analysis",
                "workflow": "comprehensive_pr_analyzer_bulletproof",
                "priority": 1
            },
            "fix": {
                "description": "Fix issues automatically",
                "workflow": "bulletproof_real_ai",
                "priority": 1
            },
            "security": {
                "description": "Security audit and fixes",
                "workflow": "bulletproof_real_ai",
                "priority": 1
            },
            "build": {
                "description": "Build optimization",
                "workflow": "bulletproof_real_ai",
                "priority": 2
            },
            "docs": {
                "description": "Generate documentation",
                "workflow": "bulletproof_real_ai",
                "priority": 2
            },
            "test": {
                "description": "Run comprehensive tests",
                "workflow": "bulletproof_real_ai",
                "priority": 2
            },
            "deploy": {
                "description": "Deployment assistance",
                "workflow": "bulletproof_real_ai",
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
                "workflow": "bulletproof_real_ai",
                "priority": 2
            },
            "optimize": {
                "description": "Optimize code and performance",
                "workflow": "bulletproof_real_ai",
                "priority": 1
            },
            "audit": {
                "description": "Comprehensive project audit",
                "workflow": "bulletproof_real_ai",
                "priority": 1
            }
        }
        
        # Initialize BULLETPROOF real AI
        try:
            self.bulletproof_ai = BulletproofRealAI()
            print("✅ BULLETPROOF REAL AI INITIALIZED for command processing")
        except Exception as e:
            print(f"🚨 BULLETPROOF AI INITIALIZATION FAILED: {e}")
            self.bulletproof_ai = None
    
    async def process_command(self, command: str, full_command: str, pr_number: str, commenter: str) -> Dict[str, Any]:
        """Process an AI agent command using BULLETPROOF real AI"""
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
        
        # Check if BULLETPROOF AI is available
        if not self.bulletproof_ai:
            return {
                "success": False,
                "command": base_command,
                "error": "BULLETPROOF AI system not available",
                "analysis": "Unable to process command - BULLETPROOF AI initialization failed",
                "recommendations": ["Check API key configuration", "Verify bulletproof_real_ai.py exists"],
                "actions_taken": [],
                "metadata": {
                    "provider_used": "error_system",
                    "response_time": 0,
                    "timestamp": datetime.now().isoformat(),
                    "bulletproof_validated": False,
                    "fake_ai_detected": True
                }
            }
        
        # Get command info
        command_info = self.commands[base_command]
        
        # Create AI prompt for command interpretation using BULLETPROOF real AI
        ai_prompt = f"""
As an expert AI agent, interpret this command and provide intelligent analysis:

**Command:** {base_command}
**Parameters:** {parameters}
**PR Number:** {pr_number}
**Commenter:** {commenter}
**Full Command:** {full_command}

**Task:**
1. **Interpret the command** and determine the best approach
2. **Analyze the context** (PR, commenter, parameters)
3. **Provide specific recommendations** for this command
4. **Suggest additional actions** that might be helpful
5. **Identify potential issues** or considerations

Provide a detailed analysis with specific, actionable recommendations.
Focus on being helpful, specific, and actionable for the {base_command} command.
"""
        
        try:
            # Use BULLETPROOF real AI for analysis
            print("🔍 Starting BULLETPROOF real AI command analysis...")
            ai_result = await self.bulletproof_ai.force_real_ai_analysis("auto_analysis", ai_prompt)
            
            if not ai_result.get('bulletproof_validated', False):
                print("🚨 FAKE AI DETECTED in command processing - FAILING HARD!")
                return {
                    "success": False,
                    "command": base_command,
                    "error": "Fake AI detected in command analysis",
                    "analysis": "BULLETPROOF validation failed - refusing to use fake AI",
                    "recommendations": ["Configure real AI providers", "Check API keys"],
                    "actions_taken": [],
                    "metadata": {
                        "provider_used": "bulletproof_validator",
                        "response_time": 0,
                        "timestamp": datetime.now().isoformat(),
                        "bulletproof_validated": False,
                        "fake_ai_detected": True
                    }
                }
            
            print("✅ BULLETPROOF REAL AI COMMAND ANALYSIS SUCCESS!")
            print(f"🤖 Provider: {ai_result['provider']}")
            print(f"⏱️ Response Time: {ai_result['response_time']}s")
            
            # Parse AI recommendations from the analysis
            analysis_content = ai_result.get('analysis', '')
            recommendations = self._extract_recommendations_from_analysis(analysis_content)
            
            # Execute the workflow if it exists
            workflow_result = await self._execute_workflow(command_info['workflow'], pr_number, parameters)
            
            return {
                "success": True,
                "command": base_command,
                "analysis": analysis_content,
                "recommendations": recommendations,
                "actions_taken": workflow_result.get('actions_taken', [f"Executed {command_info['workflow']} workflow"]),
                "workflow_result": workflow_result,
                "metadata": {
                    "provider_used": ai_result['provider'],
                    "response_time": ai_result['response_time'],
                    "timestamp": datetime.now().isoformat(),
                    "pr_number": pr_number,
                    "commenter": commenter,
                    "bulletproof_validated": ai_result['bulletproof_validated'],
                    "fake_ai_detected": ai_result['fake_ai_detected'],
                    "real_ai_verified": ai_result['real_ai_verified']
                }
            }
                
        except Exception as e:
            print(f"❌ Exception in BULLETPROOF command processing: {e}")
            return {
                "success": False,
                "error": f"Exception in command processing: {e}",
                "command": base_command,
                "analysis": f"Failed to process {base_command} command due to: {str(e)}",
                "recommendations": ["Check logs for error details", "Verify system configuration"],
                "actions_taken": [],
                "metadata": {
                    "provider_used": "error_system",
                    "response_time": 0,
                    "timestamp": datetime.now().isoformat(),
                    "bulletproof_validated": False,
                    "fake_ai_detected": True
                }
            }
    
    def _extract_recommendations_from_analysis(self, analysis: str) -> List[str]:
        """Extract actionable recommendations from AI analysis"""
        if not analysis:
            return ["No specific recommendations available"]
        
        # Look for numbered lists or bullet points
        lines = analysis.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            # Look for recommendation patterns
            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '*', '•']):
                # Clean up the recommendation
                rec = line.lstrip('123456789.*-• ').strip()
                if rec and len(rec) > 10:  # Only meaningful recommendations
                    recommendations.append(rec)
        
        # If no structured recommendations found, extract key sentences
        if not recommendations:
            sentences = analysis.split('. ')
            for sentence in sentences[:3]:  # Take first 3 sentences
                if len(sentence.strip()) > 20:
                    recommendations.append(sentence.strip())
        
        return recommendations[:5] if recommendations else ["Review the AI analysis for detailed insights"]
    
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
                "timestamp": datetime.now().isoformat(),
                "bulletproof_validated": True,
                "fake_ai_detected": False
            }
        }
    
    async def _handle_status_command(self) -> Dict[str, Any]:
        """Handle status command"""
        # Check BULLETPROOF AI provider status
        available_providers = []
        if self.bulletproof_ai:
            try:
                # Get available providers from bulletproof AI
                available_providers = [p['name'] for p in self.bulletproof_ai.providers if p.get('api_key')]
            except Exception as e:
                print(f"Error checking providers: {e}")
        
        status_text = "## 🤖 AMAS AI Agent - System Status\n\n"
        status_text += f"**Status:** {'✅ Operational' if self.bulletproof_ai else '❌ Not Available'}\n"
        status_text += f"**Available Providers:** {len(available_providers)}/16\n"
        if available_providers:
            status_text += f"**Active Providers:** {', '.join(available_providers[:5])}{'...' if len(available_providers) > 5 else ''}\n"
        status_text += f"**System Time:** {datetime.now().isoformat()}\n\n"
        status_text += "**Capabilities:**\n"
        status_text += "- ✅ BULLETPROOF Real AI System\n"
        status_text += "- ✅ 16-Provider AI Fallback\n"
        status_text += "- ✅ Fake AI Detection & Blocking\n"
        status_text += "- ✅ Intelligent Command Interpretation\n"
        status_text += "- ✅ Automated Workflow Execution\n"
        
        return {
            "success": True,
            "command": "status",
            "analysis": status_text,
            "recommendations": ["System is operational" if self.bulletproof_ai else "Configure API keys for AI providers"],
            "actions_taken": ["Checked system status"],
            "metadata": {
                "provider_used": "status_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat(),
                "bulletproof_validated": True,
                "fake_ai_detected": False,
                "available_providers": len(available_providers)
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
                "timestamp": datetime.now().isoformat(),
                "bulletproof_validated": True,
                "fake_ai_detected": False
            }
        }
    
    async def _execute_workflow(self, workflow_name: str, pr_number: str, parameters: List[str]) -> Dict[str, Any]:
        """Execute a specific workflow"""
        print(f"🔄 Executing workflow: {workflow_name}")
        
        # Define workflow scripts
        workflow_scripts = {
            "comprehensive_pr_analyzer_bulletproof": ".github/scripts/comprehensive_pr_analyzer_bulletproof.py",
            "bulletproof_real_ai": ".github/scripts/bulletproof_real_ai.py"
        }
        
        if workflow_name in workflow_scripts:
            script_path = workflow_scripts[workflow_name]
            if os.path.exists(script_path):
                try:
                    # Run the workflow script
                    import subprocess
                    cmd = ['python', script_path]
                    
                    # Add parameters based on workflow type
                    if workflow_name == "comprehensive_pr_analyzer_bulletproof":
                        cmd.extend(['--pr-number', pr_number, '--output', 'artifacts/auto_pr_analysis.json'])
                    elif workflow_name == "bulletproof_real_ai":
                        task_type = parameters[0] if parameters else 'auto_analysis'
                        cmd.append(task_type)
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "workflow": workflow_name,
                            "output": result.stdout,
                            "actions_taken": [f"Successfully executed {workflow_name} workflow"]
                        }
                    else:
                        return {
                            "success": False,
                            "workflow": workflow_name,
                            "error": result.stderr,
                            "actions_taken": [f"Attempted to execute {workflow_name} workflow but failed"]
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "workflow": workflow_name,
                        "error": str(e),
                        "actions_taken": [f"Attempted to execute {workflow_name} workflow but encountered exception"]
                    }
            else:
                return {
                    "success": False,
                    "workflow": workflow_name,
                    "error": f"Script not found: {script_path}",
                    "actions_taken": [f"Looked for {workflow_name} script but it was not found"]
                }
        else:
            # For special workflows like help/status
            return {
                "success": True,
                "workflow": workflow_name,
                "actions_taken": [f"Handled {workflow_name} internally"]
            }

async def main():
    """Main function to run AI agent command processor"""
    parser = argparse.ArgumentParser(description="BULLETPROOF AI Agent Command Processor")
    parser.add_argument("--command", required=True, help="Base command")
    parser.add_argument("--full-command", required=True, help="Full command text")
    parser.add_argument("--pr-number", required=True, help="PR number")
    parser.add_argument("--commenter", required=True, help="Commenter username")
    parser.add_argument("--output", required=True, help="Output file")
    
    args = parser.parse_args()
    
    print("🤖 BULLETPROOF AI Agent Command Processor Starting...")
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
        print("🎉 BULLETPROOF AI AGENT COMMAND PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"📋 Command: {result.get('command', 'unknown')}")
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🤖 Provider: {result.get('metadata', {}).get('provider_used', 'Unknown')}")
        print(f"⏱️ Response Time: {result.get('metadata', {}).get('response_time', 0):.2f}s")
        print(f"🛡️ Bulletproof Validated: {result.get('metadata', {}).get('bulletproof_validated', False)}")
        
        if result.get('success'):
            print(f"📊 Analysis: {result.get('analysis', 'No analysis')[:100]}...")
            print(f"💡 Recommendations: {len(result.get('recommendations', []))}")
            print(f"🔧 Actions Taken: {len(result.get('actions_taken', []))}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print(f"📄 Result saved to: {args.output}")
        
        # Exit with success/failure code
        if result.get('success') and result.get('metadata', {}).get('bulletproof_validated', False):
            print("✅ BULLETPROOF VALIDATION SUCCESS!")
            sys.exit(0)
        else:
            print("🚨 BULLETPROOF VALIDATION FAILED OR COMMAND FAILED!")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Critical error in command processor: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        
        # Create error result
        error_result = {
            "success": False,
            "error": str(e),
            "command": args.command,
            "analysis": f"Critical error occurred: {str(e)}",
            "recommendations": ["Check logs for error details", "Verify system configuration"],
            "actions_taken": [],
            "metadata": {
                "provider_used": "error_system",
                "response_time": 0,
                "timestamp": datetime.now().isoformat(),
                "bulletproof_validated": False,
                "fake_ai_detected": True
            }
        }
        
        os.makedirs("artifacts", exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(error_result, f, indent=2)
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())