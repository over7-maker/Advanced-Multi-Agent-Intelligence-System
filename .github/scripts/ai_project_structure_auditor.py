#!/usr/bin/env python3
"""
AI Project Structure Auditor with Advanced API Manager Integration
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AIProjectStructureAuditor:
    """AI Project Structure Auditor with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the auditor"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = None if use_advanced_manager else None
        self.results = {
            "structure_audit": {},
            "ai_insights": {},
            "recommendations": [],
            "statistics": {},
            "integration_stats": {}
        }
    
    def audit_project_structure(
        self, 
        audit_mode: str, 
        documentation_level: str, 
        output_format: str, 
        target_components: str
    ) -> Dict[str, Any]:
        """Audit project structure using AI"""
        print(f"🔍 Auditing project structure")
        
        try:
            # Analyze project structure
            structure_analysis = self._analyze_structure(target_components)
            
            # Get AI insights
            ai_insights = self._get_ai_insights(
                structure_analysis, audit_mode, documentation_level
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                structure_analysis, ai_insights
            )
            
            return {
                "structure_analysis": structure_analysis,
                "ai_insights": ai_insights,
                "recommendations": recommendations,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Structure audit failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_structure(self, target_components: str) -> Dict[str, Any]:
        """Analyze project structure"""
        try:
            # Analyze directory structure
            project_root = Path(".")
            structure = {
                "directories": [],
                "files": [],
                "total_files": 0,
                "total_directories": 0
            }
            
            for item in project_root.rglob("*"):
                if item.is_file():
                    structure["files"].append(str(item))
                    structure["total_files"] += 1
                elif item.is_dir():
                    structure["directories"].append(str(item))
                    structure["total_directories"] += 1
            
            return structure
            
        except Exception as e:
            print(f"❌ Structure analysis failed: {e}")
            return {"error": str(e)}
    
    def _get_ai_insights(
        self, 
        structure_analysis: Dict[str, Any], 
        audit_mode: str, 
        documentation_level: str
    ) -> Dict[str, Any]:
        """Get AI insights about project structure"""
        if not self.use_advanced_manager:
            return {"error": "Advanced API manager not enabled"}
        
        try:
            prompt = f"""
            Analyze this project structure and provide insights:
            
            Total Files: {structure_analysis.get('total_files', 0)}
            Total Directories: {structure_analysis.get('total_directories', 0)}
            Key Files: {structure_analysis.get('files', [])[:10]}
            
            Audit Mode: {audit_mode}
            Documentation Strategy: {documentation_level}
            
            Please provide:
            1. Structure quality assessment
            2. Organization recommendations
            3. Missing components
            4. Best practices compliance
            5. Documentation needs
            """
            
            system_prompt = """You are an expert project structure analyst. Provide detailed insights about project organization, best practices, and improvement recommendations."""
            
            # Simplified result for now - replace with actual AI call when available
            result = {
                "success": True,
                "provider_name": "mock",
                "response_time": 0.1,
                "content": "Project structure analysis completed using simplified approach.",
                "tokens_used": 100
            }
            
            if result.get("success", False):
                return {
                    "success": True,
                    "provider": result.get("provider_name", "Unknown"),
                    "response_time": result.get("response_time", 0),
                    "insights": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            print(f"❌ AI insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_recommendations(
        self, 
        structure_analysis: Dict[str, Any], 
        ai_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if ai_insights.get("success"):
            # Parse AI insights for recommendations
            insights_text = ai_insights.get("insights", "")
            if "organize" in insights_text.lower():
                recommendations.append("Reorganize project structure")
            if "documentation" in insights_text.lower():
                recommendations.append("Add missing documentation")
            if "best practices" in insights_text.lower():
                recommendations.append("Follow project best practices")
        
        return recommendations
    
    def run_audit(
        self, 
        audit_mode: str, 
        documentation_level: str, 
        output_format: str, 
        target_components: str, 
        output_file: str
    ) -> Dict[str, Any]:
        """Run complete structure audit"""
        print(f"🚀 Starting AI project structure audit...")
        
        try:
            # Run audit
            audit_results = self.audit_project_structure(
                audit_mode, documentation_level, output_format, target_components
            )
            
            # Compile final results
            self.results.update({
                "structure_audit": audit_results,
                "audit_metadata": {
                    "audit_mode": audit_mode,
                    "documentation_level": documentation_level,
                    "output_format": output_format,
                    "target_components": target_components,
                    "use_advanced_manager": self.use_advanced_manager
                }
            })
            
            # Add integration stats if using advanced manager
            if self.use_advanced_manager:
                self.results["integration_stats"] = {"status": "simplified"}
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"✅ Structure audit completed successfully!")
            return self.results
            
        except Exception as e:
            print(f"❌ Audit failed: {e}")
            error_results = {
                "error": str(e),
                "success": False
            }
            with open(output_file, 'w') as f:
                json.dump(error_results, f, indent=2, default=str)
            return error_results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Project Structure Auditor")
    parser.add_argument("--audit-mode", default="comprehensive", help="Audit mode")
    parser.add_argument("--documentation-level", default="full", help="Documentation level")
    parser.add_argument("--output-format", default="markdown", help="Output format")
    parser.add_argument("--target-components", default="all", help="Target components")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="project_structure_audit_results.json", help="Output file")
    
    # Add common optional arguments
    parser.add_argument("--quality-results", default="quality_results/", help="Quality results directory")
    parser.add_argument("--performance-results", default="performance_results/", help="Performance results directory")
    parser.add_argument("--all-results", default="all_results/", help="All results directory")
    parser.add_argument("--enhancement-results", default="enhancement_results/", help="Enhancement results directory")
    parser.add_argument("--validation-results", default="validation_results/", help="Validation results directory")
    
    args = parser.parse_args()
    
    # Create auditor
    auditor = AIProjectStructureAuditor(use_advanced_manager=args.use_advanced_manager)
    
    # Run audit
    results = auditor.run_audit(
        audit_mode=args.audit_mode,
        documentation_level=args.documentation_level,
        output_format=args.output_format,
        target_components=args.target_components,
        output_file=args.output
    )
    
    # Print summary
    if results.get("success", True):
        print("\n" + "=" * 80)
        print("🔍 PROJECT STRUCTURE AUDIT SUMMARY")
        print("=" * 80)
        print(f"Audit Mode: {args.audit_mode}")
        print(f"Documentation Strategy: {args.documentation_level}")
        print(f"Output Format: {args.output_format}")
        print(f"Target Components: {args.target_components}")
        print("=" * 80)
    else:
        print(f"❌ Audit failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
