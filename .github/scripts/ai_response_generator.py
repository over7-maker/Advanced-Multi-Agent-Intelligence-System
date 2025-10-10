#!/usr/bin/env python3
"""
AI Response Generator with Advanced API Manager Integration
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the universal AI workflow integration
from .github.scripts.universal_ai_workflow_integration import (
    get_integration, 
    generate_workflow_ai_response, 
    save_workflow_results
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AIResponseGenerator:
    """AI Response Generator with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the generator"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = get_integration() if use_advanced_manager else None
        self.results = {
            "response_generation": {},
            "ai_insights": {},
            "response_metadata": {},
            "statistics": {},
            "integration_stats": {}
        }
    
    async def generate_response(
        self, 
        issue_number: str, 
        response_mode: str, 
        auto_fix: bool, 
        language: str
    ) -> Dict[str, Any]:
        """Generate AI response for issue"""
        logger.info(f"🤖 Generating AI response for issue #{issue_number}")
        
        try:
            # Get issue context
            issue_context = await self._get_issue_context(issue_number)
            
            # Generate response with AI
            ai_response = await self._generate_with_ai(
                issue_context, response_mode, auto_fix, language
            )
            
            # Format response
            formatted_response = await self._format_response(
                ai_response, response_mode, language
            )
            
            return {
                "issue_context": issue_context,
                "ai_response": ai_response,
                "formatted_response": formatted_response,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_issue_context(self, issue_number: str) -> Dict[str, Any]:
        """Get issue context (simplified)"""
        return {
            "number": issue_number,
            "title": f"Issue #{issue_number}",
            "body": "Sample issue content",
            "labels": ["bug", "priority:high"],
            "state": "open"
        }
    
    async def _generate_with_ai(
        self, 
        issue_context: Dict[str, Any], 
        response_mode: str, 
        auto_fix: bool, 
        language: str
    ) -> Dict[str, Any]:
        """Generate response with AI"""
        if not self.use_advanced_manager:
            return {"error": "Advanced API manager not enabled"}
        
        try:
            prompt = f"""
            Generate a professional GitHub issue response:
            
            Issue #{issue_context['number']}: {issue_context['title']}
            Content: {issue_context['body']}
            Labels: {issue_context['labels']}
            State: {issue_context['state']}
            
            Response Requirements:
            - Mode: {response_mode}
            - Auto-fix: {auto_fix}
            - Language: {language}
            - Be professional and helpful
            - Provide actionable next steps
            - Include relevant code examples if applicable
            """
            
            system_prompt = """You are an expert GitHub issue responder. Generate professional, helpful, and actionable responses that provide clear next steps and solutions."""
            
            result = await generate_workflow_ai_response(
                prompt=prompt,
                system_prompt=system_prompt,
                strategy="intelligent"
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "provider": result.get("provider_name", "Unknown"),
                    "response_time": result.get("response_time", 0),
                    "content": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ AI response generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _format_response(
        self, 
        ai_response: Dict[str, Any], 
        response_mode: str, 
        language: str
    ) -> str:
        """Format the AI response"""
        if not ai_response.get("success"):
            return f"❌ Error generating response: {ai_response.get('error', 'Unknown error')}"
        
        content = ai_response.get("content", "")
        
        # Add response metadata
        formatted = f"""## 🤖 AI Response

{content}

---
*Generated by AI Agentic Issue Auto-Responder v2.0*
*Provider: {ai_response.get('provider', 'Unknown')} | Response Time: {ai_response.get('response_time', 0):.2f}s*
"""
        
        return formatted
    
    async def run_generation(
        self, 
        issue_number: str, 
        response_mode: str, 
        auto_fix: bool, 
        language: str, 
        output_file: str
    ) -> Dict[str, Any]:
        """Run complete response generation"""
        logger.info(f"🚀 Starting AI response generation...")
        
        try:
            # Run generation
            generation_results = await self.generate_response(
                issue_number, response_mode, auto_fix, language
            )
            
            # Compile final results
            self.results.update({
                "response_generation": generation_results,
                "generation_metadata": {
                    "issue_number": issue_number,
                    "response_mode": response_mode,
                    "auto_fix": auto_fix,
                    "language": language,
                    "use_advanced_manager": self.use_advanced_manager
                }
            })
            
            # Add integration stats if using advanced manager
            if self.use_advanced_manager:
                self.results["integration_stats"] = self.integration.get_integration_stats()
            
            # Save results
            save_workflow_results(self.results, output_file)
            
            logger.info(f"✅ Response generation completed successfully!")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {e}")
            error_results = {
                "error": str(e),
                "success": False
            }
            save_workflow_results(error_results, output_file)
            return error_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Response Generator")
    parser.add_argument("--issue-number", required=True, help="Issue number")
    parser.add_argument("--response-mode", default="intelligent", help="Response mode")
    parser.add_argument("--auto-fix", action="store_true", help="Enable auto-fix")
    parser.add_argument("--language", default="auto", help="Response language")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="ai_response_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create generator
    generator = AIResponseGenerator(use_advanced_manager=args.use_advanced_manager)
    
    # Run generation
    results = await generator.run_generation(
        issue_number=args.issue_number,
        response_mode=args.response_mode,
        auto_fix=args.auto_fix,
        language=args.language,
        output_file=args.output
    )
    
    # Print summary
    if results.get("success", True):
        print("\n" + "=" * 80)
        print("🤖 RESPONSE GENERATION SUMMARY")
        print("=" * 80)
        print(f"Issue #{args.issue_number} response generated")
        print(f"Response Mode: {args.response_mode}")
        print(f"Auto-Fix: {args.auto_fix}")
        print(f"Language: {args.language}")
        print("=" * 80)
    else:
        print(f"❌ Generation failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())