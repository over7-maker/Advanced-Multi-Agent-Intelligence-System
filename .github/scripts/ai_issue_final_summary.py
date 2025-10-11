#!/usr/bin/env python3
    """
    AI Issue Final Summary Script
Generates final summary and integration for issue responder workflow
    """

    import argparse
    import json
    import os
    import sys
    from pathlib import Path
    from typing import Any, Dict, List, Optional

# Add the project root to the Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# Import the universal AI workflow integration

# Configure logging
    logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
    )

class AIIssueFinalSummary:
    """AI Issue Final Summary Generator with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the summary generator"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = None if use_advanced_manager else None
        self.results = {
            "final_summary": {},
            "integration_stats": {},
            "workflow_performance": {},
            "recommendations": [],
            "next_steps": [],
            "success_metrics": {}
        }
    
    def generate_final_summary(
        self, 
        mode: str, 
        depth: str, 
        language: str, 
        auto_fix: bool, 
        target_issues: str,
        all_results_dir: str
    ) -> Dict[str, Any]:
        """Generate final summary and integration"""
        print("📊 Generating Final Summary & Integration")
        print(f"Mode: {mode} | Depth: {depth} | Language: {language}")
        print(f"Auto-fix: {auto_fix} | Target Issues: {target_issues}")
        
        try:
            # Load all results from the results directory
            all_results = self._load_all_results(all_results_dir)
            
            # Generate AI-powered final summary
            summary_prompt = self._create_summary_prompt(all_results, mode, depth, language, auto_fix, target_issues)
            
            if self.use_advanced_manager and self.integration:
                # Use advanced API manager
                ai_response =                     prompt=summary_prompt,
                    system_prompt="You are an expert AI workflow analyst. Generate comprehensive final summaries and integration reports.",
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
                    print(f"AI generation failed: {ai_response.get('error', 'Unknown error')}")
                    self.results["final_summary"] = self._generate_fallback_summary(all_results)
            else:
                # Fallback summary
                self.results["final_summary"] = self._generate_fallback_summary(all_results)
            
            # Generate integration statistics
            self.results["integration_stats"] = self._generate_integration_stats()
            
            # Generate workflow performance metrics
            self.results["workflow_performance"] = self._generate_performance_metrics(all_results)
            
            # Generate recommendations
            self.results["recommendations"] = self._generate_recommendations(all_results)
            
            # Generate next steps
            self.results["next_steps"] = self._generate_next_steps(all_results)
            
            # Generate success metrics
            self.results["success_metrics"] = self._generate_success_metrics(all_results)
            
            print("✅ Final Summary & Integration completed successfully")
            return self.results
            
        except Exception as e:
            print(f"❌ Error generating final summary: {e}")
            return self._generate_error_summary(str(e))
    
    def _load_all_results(self, results_dir: str) -> Dict[str, Any]:
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
                        print(f"Could not load {result_file}: {e}")
            else:
                print(f"Results directory {results_dir} does not exist")
        except Exception as e:
            print(f"Error loading results: {e}")
        
        return all_results
    
    def _create_summary_prompt(
        self, 
        all_results: Dict[str, Any], 
        mode: str, 
        depth: str, 
        language: str, 
        auto_fix: bool, 
        target_issues: str
    ) -> str:
        """Create AI prompt for final summary generation"""
        return f"""
Generate a comprehensive final summary and integration report for the AI Issue Auto-Responder workflow.

## WORKFLOW CONTEXT:
    - Mode: {mode}
    - Depth: {depth}
    - Language: {language}
    - Auto-fix: {auto_fix}
    - Target Issues: {target_issues}

## AVAILABLE RESULTS:
    {json.dumps(all_results, indent=2, default=str)}

## REQUIREMENTS:
    1. Provide a comprehensive overview of all workflow activities
    2. Analyze the effectiveness of each phase
    3. Identify key insights and patterns
    4. Generate actionable recommendations
5. Suggest next steps for improvement
    6. Calculate success metrics and performance indicators

## OUTPUT FORMAT:
    - Executive Summary
    - Detailed Analysis
    - Key Findings
    - Recommendations
    - Next Steps
    - Performance Metrics
    - Integration Status

Please provide a detailed, professional summary suitable for stakeholders and technical teams.
    """
    
    def _generate_fallback_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary when AI is not available"""
        return {
            "ai_generated": False,
            "content": f"Fallback summary generated for {len(all_results)} result files",
            "provider": "Fallback",
            "response_time": 0,
            "results_count": len(all_results),
            "available_results": list(all_results.keys())
        }
    
    def _generate_integration_stats(self) -> Dict[str, Any]:
        """Generate integration statistics"""
        if self.use_advanced_manager and self.integration:
            return         else:
            return {
                "integration_available": False,
                "message": "Advanced API manager not available"
            }
    
    def _generate_performance_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow performance metrics"""
        return {
            "total_results": len(all_results),
            "successful_phases": len([r for r in all_results.values() if r.get("success", False)]),
            "failed_phases": len([r for r in all_results.values() if not r.get("success", False)]),
            "average_processing_time": self._calculate_average_time(all_results),
            "workflow_efficiency": self._calculate_efficiency(all_results)
        }
    
    def _generate_recommendations(self, all_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Analyze results and generate recommendations
        if len(all_results) == 0:
            recommendations.append("No results available - check workflow configuration")
        else:
            successful = len([r for r in all_results.values() if r.get("success", False)])
            total = len(all_results)
            
            if successful == total:
                recommendations.append("All workflow phases completed successfully")
                recommendations.append("Consider increasing automation scope")
            elif successful > total * 0.8:
                recommendations.append("Most workflow phases successful - investigate failures")
            else:
                recommendations.append("Multiple workflow phases failed - review configuration")
                recommendations.append("Check API key availability and network connectivity")
        
        return recommendations
    
    def _generate_next_steps(self, all_results: Dict[str, Any]) -> List[str]:
        """Generate next steps based on results"""
        next_steps = []
        
        if len(all_results) == 0:
            next_steps.append("Investigate workflow configuration issues")
            next_steps.append("Check GitHub Actions logs for errors")
        else:
            next_steps.append("Review generated recommendations")
            next_steps.append("Implement suggested improvements")
            next_steps.append("Monitor workflow performance")
            next_steps.append("Update documentation as needed")
        
        return next_steps
    
    def _generate_success_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate success metrics"""
        total = len(all_results)
        successful = len([r for r in all_results.values() if r.get("success", False)])
        
        return {
            "total_phases": total,
            "successful_phases": successful,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "workflow_status": "SUCCESS" if successful == total else "PARTIAL" if successful > 0 else "FAILED"
        }
    
    def _calculate_average_time(self, all_results: Dict[str, Any]) -> float:
        """Calculate average processing time"""
        times = []
        for result in all_results.values():
            if "processing_time" in result:
                times.append(result["processing_time"])
        return sum(times) / len(times) if times else 0
    
    def _calculate_efficiency(self, all_results: Dict[str, Any]) -> str:
        """Calculate workflow efficiency"""
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
            "workflow_performance": {"error": error},
            "recommendations": ["Fix the error and retry"],
            "next_steps": ["Debug the issue", "Check logs"],
            "success_metrics": {"workflow_status": "ERROR"}
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Issue Final Summary Generator")
    parser.add_argument("--mode", default="intelligent", help="Response mode")
    parser.add_argument("--depth", default="comprehensive", help="Analysis depth")
    parser.add_argument("--language", default="auto", help="Response language")
    parser.add_argument("--auto-fix", action="store_true", help="Enable auto-fix")
    parser.add_argument("--target-issues", default="all", help="Target issues")
    parser.add_argument("--all-results", default="final_results/", help="All results directory")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="final_summary_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create summary generator
    summary_generator = AIIssueFinalSummary(use_advanced_manager=args.use_advanced_manager)
    
    # Generate final summary
    results = summary_generator.generate_final_summary(
        mode=args.mode,
        depth=args.depth,
        language=args.language,
        auto_fix=args.auto_fix,
        target_issues=args.target_issues,
        all_results_dir=args.all_results
    )
    
    # Save results
    if args.use_advanced_manager and summary_generator.integration:
        summary_generator.with open(output_file, 'w') as f:
    json.dump(self.results, f, indent=2, default=str)
    else:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Final summary saved to {args.output}")

if __name__ == "__main__":
    main()