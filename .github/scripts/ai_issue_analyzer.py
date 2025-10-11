#!/usr/bin/env python3
"""
AI Issue Analyzer with Advanced API Manager Integration
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
from universal_ai_workflow_integration import UniversalAIWorkflowIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AIIssueAnalyzer:
    """AI Issue Analyzer with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the analyzer"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = UniversalAIWorkflowIntegration() if use_advanced_manager else None
        self.results = {
            "issue_analysis": {},
            "ai_insights": {},
            "recommendations": [],
            "labels": [],
            "statistics": {},
            "integration_stats": {}
        }
    
    async def analyze_issue(
        self, 
        issue_number: str, 
        response_mode: str, 
        auto_fix: bool, 
        language: str
    ) -> Dict[str, Any]:
        """Analyze GitHub issue using AI"""
        logger.info(f"🔍 Analyzing issue #{issue_number}")
        
        try:
            # Get issue data (simplified for this example)
            issue_data = await self._get_issue_data(issue_number)
            
            # Analyze issue with AI
            ai_analysis = await self._analyze_with_ai(
                issue_data, response_mode, auto_fix, language
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                issue_data, ai_analysis
            )
            
            # Generate labels
            labels = await self._generate_labels(issue_data, ai_analysis)
            
            return {
                "issue_data": issue_data,
                "ai_analysis": ai_analysis,
                "recommendations": recommendations,
                "labels": labels,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Issue analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_issue_data(self, issue_number: str) -> Dict[str, Any]:
        """Get issue data (simplified)"""
        return {
            "number": issue_number,
            "title": f"Issue #{issue_number}",
            "body": "Sample issue content",
            "labels": [],
            "state": "open",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def _analyze_with_ai(
        self, 
        issue_data: Dict[str, Any], 
        response_mode: str, 
        auto_fix: bool, 
        language: str
    ) -> Dict[str, Any]:
        """Analyze issue with AI"""
        if not self.use_advanced_manager:
            return {"error": "Advanced API manager not enabled"}
        
        try:
            prompt = f"""
            Analyze this GitHub issue and provide insights:
            
            Issue #{issue_data['number']}: {issue_data['title']}
            Content: {issue_data['body']}
            Labels: {issue_data['labels']}
            State: {issue_data['state']}
            
            Please provide:
            1. Issue type classification
            2. Priority level (low/medium/high/critical)
            3. Complexity score (1-10)
            4. Suggested response approach
            5. Auto-fix feasibility: {auto_fix}
            6. Language preference: {language}
            """
            
            system_prompt = """You are an expert GitHub issue analyst. Provide detailed, actionable insights about issue classification, priority, and response strategies."""
            
            result = await integration.generate_with_fallback(
                prompt=prompt,
                system_prompt=system_prompt,
                strategy="intelligent"
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "provider": result.get("provider_name", "Unknown"),
                    "response_time": result.get("response_time", 0),
                    "analysis": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_recommendations(
        self, 
        issue_data: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if ai_analysis.get("success"):
            # Parse AI analysis for recommendations
            analysis_text = ai_analysis.get("analysis", "")
            if "bug" in analysis_text.lower():
                recommendations.append("Assign to bug fix team")
            if "feature" in analysis_text.lower():
                recommendations.append("Add to feature backlog")
            if "urgent" in analysis_text.lower():
                recommendations.append("Escalate to senior developer")
        
        return recommendations
    
    async def _generate_labels(
        self, 
        issue_data: Dict[str, Any], 
        ai_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate labels based on analysis"""
        labels = []
        
        if ai_analysis.get("success"):
            analysis_text = ai_analysis.get("analysis", "").lower()
            
            if "bug" in analysis_text:
                labels.append("bug")
            if "feature" in analysis_text:
                labels.append("enhancement")
            if "urgent" in analysis_text:
                labels.append("priority:high")
            if "documentation" in analysis_text:
                labels.append("documentation")
        
        return labels
    
    async def run_analysis(
        self, 
        issue_number: str, 
        response_mode: str, 
        auto_fix: bool, 
        language: str, 
        output_file: str
    ) -> Dict[str, Any]:
        """Run complete issue analysis"""
        logger.info(f"🚀 Starting AI issue analysis...")
        
        try:
            # Run analysis
            analysis_results = await self.analyze_issue(
                issue_number, response_mode, auto_fix, language
            )
            
            # Compile final results
            self.results.update({
                "issue_analysis": analysis_results,
                "analysis_metadata": {
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
            integration.save_results(self.results, output_file)
            
            logger.info(f"✅ Issue analysis completed successfully!")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            error_results = {
                "error": str(e),
                "success": False
            }
            integration.save_results(error_results, output_file)
            return error_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Issue Analyzer")
    parser.add_argument("--issue-number", required=True, help="Issue number to analyze")
    parser.add_argument("--response-mode", default="intelligent", help="Response mode")
    parser.add_argument("--auto-fix", action="store_true", help="Enable auto-fix")
    parser.add_argument("--language", default="auto", help="Response language")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="issue_analysis_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = AIIssueAnalyzer(use_advanced_manager=args.use_advanced_manager)
    
    # Run analysis
    results = await analyzer.run_analysis(
        issue_number=args.issue_number,
        response_mode=args.response_mode,
        auto_fix=args.auto_fix,
        language=args.language,
        output_file=args.output
    )
    
    # Print summary
    if results.get("success", True):
        print("\n" + "=" * 80)
        print("📊 ISSUE ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Issue #{args.issue_number} analyzed successfully")
        print(f"Response Mode: {args.response_mode}")
        print(f"Auto-Fix: {args.auto_fix}")
        print(f"Language: {args.language}")
        print("=" * 80)
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())