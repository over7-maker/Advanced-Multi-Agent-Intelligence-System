#!/usr/bin/env python3
"""
AI Audit Final Summary Script
Generates final summary and integration for audit documentation workflow
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
from universal_ai_workflow_integration import get_integration, generate_workflow_ai_response, save_workflow_results

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AIAuditFinalSummary:
    """AI Audit Final Summary Generator with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the summary generator"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = get_integration() if use_advanced_manager else None
        self.results = {
            "final_summary": {},
            "integration_stats": {},
            "audit_performance": {},
            "recommendations": [],
            "next_steps": [],
            "success_metrics": {},
            "documentation_plan": {}
        }
    
    async def generate_final_summary(
        self, 
        mode: str, 
        components: str, 
        level: str, 
        formats: str,
        all_results_dir: str
    ) -> Dict[str, Any]:
        """Generate final summary and integration"""
        logger.info("📊 Generating Final Summary & Integration")
        logger.info(f"Mode: {mode} | Components: {components} | Strategy: {level}")
        logger.info(f"Output Formats: {formats}")
        
        try:
            # Load all results from the results directory
            all_results = await self._load_all_results(all_results_dir)
            
            # Generate AI-powered final summary
            summary_prompt = self._create_summary_prompt(all_results, mode, components, level, formats)
            
            if self.use_advanced_manager and self.integration:
                # Use advanced API manager
                ai_response = await self.integration.generate_with_fallback(
                    prompt=summary_prompt,
                    system_prompt="You are an expert project audit analyst. Generate comprehensive final summaries and integration reports.",
                    strategy="intelligent"
                )
                
                if ai_response.get("success", False):
                    self.results["final_summary"] = {
                        "ai_generated": True,
                        "content": ai_response.get("content", ""),
                        "provider": ai_response.get("provider_name", "Unknown"),
                        "response_time": ai_response.get("response_time", 0)
                    }
                else:
                    logger.error(f"AI generation failed: {ai_response.get('error', 'Unknown error')}")
                    self.results["final_summary"] = self._generate_fallback_summary(all_results)
            else:
                # Fallback summary
                self.results["final_summary"] = self._generate_fallback_summary(all_results)
            
            # Generate integration statistics
            self.results["integration_stats"] = await self._generate_integration_stats()
            
            # Generate audit performance metrics
            self.results["audit_performance"] = self._generate_performance_metrics(all_results)
            
            # Generate recommendations
            self.results["recommendations"] = self._generate_recommendations(all_results)
            
            # Generate next steps
            self.results["next_steps"] = self._generate_next_steps(all_results)
            
            # Generate success metrics
            self.results["success_metrics"] = self._generate_success_metrics(all_results)
            
            # Generate documentation plan
            self.results["documentation_plan"] = self._generate_documentation_plan(all_results)
            
            logger.info("✅ Final Summary & Integration completed successfully")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Error generating final summary: {e}")
            return self._generate_error_summary(str(e))
    
    async def _load_all_results(self, results_dir: str) -> Dict[str, Any]:
        """Load all results from the results directory"""
        all_results = {}
        
        try:
            results_path = Path(results_dir)
            if results_path.exists():
                for result_file in results_path.glob("*.json"):
                    try:
                        with open(result_file, 'r') as f:
                            data = json.load(f)
                            all_results[result_file.stem] = data
                    except Exception as e:
                        logger.warning(f"Could not load {result_file}: {e}")
            else:
                logger.warning(f"Results directory {results_dir} does not exist")
        except Exception as e:
            logger.error(f"Error loading results: {e}")
        
        return all_results
    
    def _create_summary_prompt(
        self, 
        all_results: Dict[str, Any], 
        mode: str, 
        components: str, 
        level: str, 
        formats: str
    ) -> str:
        """Create AI prompt for final summary generation"""
        return f"""
Generate a comprehensive final summary and integration report for the AI Project Audit & Documentation workflow.

## WORKFLOW CONTEXT:
- Mode: {mode}
- Components: {components}
- Strategy: {level}
- Formats: {formats}

## AVAILABLE RESULTS:
{json.dumps(all_results, indent=2, default=str)}

## REQUIREMENTS:
1. Provide a comprehensive overview of all audit activities
2. Analyze the effectiveness of each audit phase
3. Identify key insights and patterns from the audit
4. Generate actionable recommendations for project improvement
5. Suggest next steps for documentation and development
6. Calculate success metrics and performance indicators
7. Create a documentation improvement plan

## OUTPUT FORMAT:
- Executive Summary
- Detailed Audit Analysis
- Key Findings and Insights
- Priority Recommendations
- Next Steps and Action Items
- Performance Metrics
- Documentation Plan
- Integration Status

Please provide a detailed, professional summary suitable for stakeholders and development teams.
"""
    
    def _generate_fallback_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary when AI is not available"""
        return {
            "ai_generated": False,
            "content": f"Fallback summary generated for {len(all_results)} audit result files",
            "provider": "Fallback",
            "response_time": 0,
            "results_count": len(all_results),
            "available_results": list(all_results.keys())
        }
    
    async def _generate_integration_stats(self) -> Dict[str, Any]:
        """Generate integration statistics"""
        if self.use_advanced_manager and self.integration:
            return self.integration.get_integration_stats()
        else:
            return {
                "integration_available": False,
                "message": "Advanced API manager not available"
            }
    
    def _generate_performance_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audit performance metrics"""
        return {
            "total_audits": len(all_results),
            "successful_audits": len([r for r in all_results.values() if r.get("success", False)]),
            "failed_audits": len([r for r in all_results.values() if not r.get("success", False)]),
            "average_processing_time": self._calculate_average_time(all_results),
            "audit_efficiency": self._calculate_efficiency(all_results)
        }
    
    def _generate_recommendations(self, all_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Analyze results and generate recommendations
        if len(all_results) == 0:
            recommendations.append("No audit results available - check workflow configuration")
        else:
            successful = len([r for r in all_results.values() if r.get("success", False)])
            total = len(all_results)
            
            if successful == total:
                recommendations.append("All audit phases completed successfully")
                recommendations.append("Consider implementing suggested improvements")
                recommendations.append("Update documentation based on findings")
            elif successful > total * 0.8:
                recommendations.append("Most audit phases successful - investigate failures")
                recommendations.append("Address identified issues before proceeding")
            else:
                recommendations.append("Multiple audit phases failed - review configuration")
                recommendations.append("Check API key availability and network connectivity")
                recommendations.append("Fix critical issues before continuing")
        
        return recommendations
    
    def _generate_next_steps(self, all_results: Dict[str, Any]) -> List[str]:
        """Generate next steps based on audit results"""
        next_steps = []
        
        if len(all_results) == 0:
            next_steps.append("Investigate audit workflow configuration issues")
            next_steps.append("Check GitHub Actions logs for errors")
        else:
            next_steps.append("Review generated audit recommendations")
            next_steps.append("Implement priority improvements")
            next_steps.append("Update project documentation")
            next_steps.append("Monitor project health metrics")
            next_steps.append("Schedule follow-up audits")
        
        return next_steps
    
    def _generate_success_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate success metrics"""
        total = len(all_results)
        successful = len([r for r in all_results.values() if r.get("success", False)])
        
        return {
            "total_audits": total,
            "successful_audits": successful,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "audit_status": "SUCCESS" if successful == total else "PARTIAL" if successful > 0 else "FAILED"
        }
    
    def _generate_documentation_plan(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation improvement plan"""
        return {
            "priority_areas": [
                "API documentation",
                "Code comments and docstrings",
                "README files",
                "Architecture documentation",
                "Deployment guides"
            ],
            "recommended_actions": [
                "Update existing documentation",
                "Add missing documentation",
                "Improve code comments",
                "Create user guides",
                "Document API endpoints"
            ],
            "timeline": "2-4 weeks",
            "resources_needed": ["Technical writers", "Developer time", "Review process"]
        }
    
    def _calculate_average_time(self, all_results: Dict[str, Any]) -> float:
        """Calculate average processing time"""
        times = []
        for result in all_results.values():
            if "processing_time" in result:
                times.append(result["processing_time"])
        return sum(times) / len(times) if times else 0
    
    def _calculate_efficiency(self, all_results: Dict[str, Any]) -> str:
        """Calculate audit efficiency"""
        total = len(all_results)
        successful = len([r for r in all_results.values() if r.get("success", False)])
        
        if total == 0:
            return "Unknown"
        elif successful == total:
            return "Excellent"
        elif successful >= total * 0.8:
            return "Good"
        elif successful >= total * 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def _generate_error_summary(self, error: str) -> Dict[str, Any]:
        """Generate error summary"""
        return {
            "final_summary": {
                "ai_generated": False,
                "content": f"Error generating summary: {error}",
                "provider": "Error",
                "response_time": 0
            },
            "integration_stats": {"error": error},
            "audit_performance": {"error": error},
            "recommendations": ["Fix the error and retry"],
            "next_steps": ["Debug the issue", "Check logs"],
            "success_metrics": {"audit_status": "ERROR"},
            "documentation_plan": {"error": error}
        }

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Audit Final Summary Generator")
    parser.add_argument("--mode", default="comprehensive", help="Audit mode")
    parser.add_argument("--components", default="all", help="Target components")
    parser.add_argument("--level", default="detailed", help="Documentation level")
    parser.add_argument("--formats", default="json", help="Output formats")
    parser.add_argument("--all-results", default="final_results/", help="All results directory")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="final_summary_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create summary generator
    summary_generator = AIAuditFinalSummary(use_advanced_manager=args.use_advanced_manager)
    
    # Generate final summary
    results = await summary_generator.generate_final_summary(
        mode=args.mode,
        components=args.components,
        level=args.level,
        formats=args.formats,
        all_results_dir=args.all_results
    )
    
    # Save results
    if args.use_advanced_manager and summary_generator.integration:
        summary_generator.integration.save_results(results, args.output)
    else:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    logger.info(f"✅ Final summary saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())