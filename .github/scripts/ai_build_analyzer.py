#!/usr/bin/env python3
"""
AI Build Analyzer with Advanced API Manager Integration
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

class AIBuildAnalyzer:
    """AI Build Analyzer with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the analyzer"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = get_integration() if use_advanced_manager else None
        self.results = {
            "build_analysis": {},
            "ai_insights": {},
            "recommendations": [],
            "statistics": {},
            "integration_stats": {}
        }
    
    async def analyze_build(
        self, 
        build_mode: str, 
        version_strategy: str, 
        package_format: str, 
        target_platforms: str
    ) -> Dict[str, Any]:
        """Analyze build requirements using AI"""
        logger.info(f"🔍 Analyzing build requirements")
        
        try:
            # Analyze project files
            project_analysis = await self._analyze_project_files()
            
            # Get AI insights
            ai_insights = await self._get_ai_insights(
                project_analysis, build_mode, version_strategy, package_format
            )
            
            # Generate build recommendations
            recommendations = await self._generate_build_recommendations(
                project_analysis, ai_insights
            )
            
            return {
                "project_analysis": project_analysis,
                "ai_insights": ai_insights,
                "recommendations": recommendations,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Build analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_project_files(self) -> Dict[str, Any]:
        """Analyze project files for build requirements"""
        try:
            project_root = Path(".")
            analysis = {
                "python_files": [],
                "requirements_files": [],
                "config_files": [],
                "docker_files": [],
                "total_files": 0
            }
            
            # Find Python files
            for py_file in project_root.rglob("*.py"):
                analysis["python_files"].append(str(py_file))
                analysis["total_files"] += 1
            
            # Find requirements files
            for req_file in project_root.rglob("requirements*.txt"):
                analysis["requirements_files"].append(str(req_file))
            
            # Find config files
            for config_file in project_root.rglob("*.toml"):
                analysis["config_files"].append(str(config_file))
            
            # Find Docker files
            for docker_file in project_root.rglob("Dockerfile*"):
                analysis["docker_files"].append(str(docker_file))
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Project file analysis failed: {e}")
            return {"error": str(e)}
    
    async def _get_ai_insights(
        self, 
        project_analysis: Dict[str, Any], 
        build_mode: str, 
        version_strategy: str, 
        package_format: str
    ) -> Dict[str, Any]:
        """Get AI insights about build requirements"""
        if not self.use_advanced_manager:
            return {"error": "Advanced API manager not enabled"}
        
        try:
            prompt = f"""
            Analyze this project for build requirements and provide insights:
            
            Python Files: {len(project_analysis.get('python_files', []))}
            Requirements Files: {project_analysis.get('requirements_files', [])}
            Config Files: {project_analysis.get('config_files', [])}
            Docker Files: {project_analysis.get('docker_files', [])}
            
            Build Mode: {build_mode}
            Version Strategy: {version_strategy}
            Package Format: {package_format}
            
            Please provide:
            1. Build complexity assessment
            2. Dependencies analysis
            3. Version management recommendations
            4. Package format optimization
            5. Build process improvements
            """
            
            system_prompt = """You are an expert build system analyst. Provide detailed insights about build requirements, dependencies, and optimization strategies."""
            
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
                    "insights": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_build_recommendations(
        self, 
        project_analysis: Dict[str, Any], 
        ai_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate build recommendations based on analysis"""
        recommendations = []
        
        if ai_insights.get("success"):
            # Parse AI insights for recommendations
            insights_text = ai_insights.get("insights", "")
            if "dependencies" in insights_text.lower():
                recommendations.append("Optimize dependency management")
            if "version" in insights_text.lower():
                recommendations.append("Implement semantic versioning")
            if "docker" in insights_text.lower():
                recommendations.append("Optimize Docker build process")
        
        return recommendations
    
    async def run_analysis(
        self, 
        build_mode: str, 
        version_strategy: str, 
        package_format: str, 
        target_platforms: str, 
        output_file: str
    ) -> Dict[str, Any]:
        """Run complete build analysis"""
        logger.info(f"🚀 Starting AI build analysis...")
        
        try:
            # Run analysis
            analysis_results = await self.analyze_build(
                build_mode, version_strategy, package_format, target_platforms
            )
            
            # Compile final results
            self.results.update({
                "build_analysis": analysis_results,
                "analysis_metadata": {
                    "build_mode": build_mode,
                    "version_strategy": version_strategy,
                    "package_format": package_format,
                    "target_platforms": target_platforms,
                    "use_advanced_manager": self.use_advanced_manager
                }
            })
            
            # Add integration stats if using advanced manager
            if self.use_advanced_manager:
                self.results["integration_stats"] = self.integration.get_integration_stats()
            
            # Save results
            save_workflow_results(self.results, output_file)
            
            logger.info(f"✅ Build analysis completed successfully!")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            error_results = {
                "error": str(e),
                "success": False
            }
            save_workflow_results(error_results, output_file)
            return error_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Build Analyzer")
    parser.add_argument("--build-mode", default="intelligent", help="Build mode")
    parser.add_argument("--version-strategy", default="semantic", help="Version strategy")
    parser.add_argument("--package-format", default="all", help="Package format")
    parser.add_argument("--target-platforms", default="all", help="Target platforms")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="build_analysis_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = AIBuildAnalyzer(use_advanced_manager=args.use_advanced_manager)
    
    # Run analysis
    results = await analyzer.run_analysis(
        build_mode=args.build_mode,
        version_strategy=args.version_strategy,
        package_format=args.package_format,
        target_platforms=args.target_platforms,
        output_file=args.output
    )
    
    # Print summary
    if results.get("success", True):
        print("\n" + "=" * 80)
        print("🔍 BUILD ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Build Mode: {args.build_mode}")
        print(f"Version Strategy: {args.version_strategy}")
        print(f"Package Format: {args.package_format}")
        print(f"Target Platforms: {args.target_platforms}")
        print("=" * 80)
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())