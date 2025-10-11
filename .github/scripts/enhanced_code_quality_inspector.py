#!/usr/bin/env python3
"""
Enhanced Code Quality Inspector with Advanced API Manager Integration
Uses standalone_universal_ai_manager.py for intelligent failover
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
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

class EnhancedCodeQualityInspector:
    """Enhanced Code Quality Inspector with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the inspector"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = UniversalAIWorkflowIntegration() if use_advanced_manager else None
        self.results = {
            "code_quality_analysis": {},
            "ai_insights": {},
            "recommendations": [],
            "statistics": {},
            "integration_stats": {}
        }
    
    async def analyze_code_quality(self, directory: str, extensions: List[str]) -> Dict[str, Any]:
        """Analyze code quality using flake8 and AI insights"""
        logger.info(f"🔍 Analyzing code quality in {directory}")
        
        # Run flake8 analysis
        flake8_results = await self._run_flake8_analysis(directory, extensions)
        
        # Run bandit security analysis
        bandit_results = await self._run_bandit_analysis(directory, extensions)
        
        # Get AI insights
        ai_insights = await self._get_ai_insights(flake8_results, bandit_results, directory)
        
        return {
            "flake8_results": flake8_results,
            "bandit_results": bandit_results,
            "ai_insights": ai_insights,
            "timestamp": str(asyncio.get_event_loop().time())
        }
    
    async def _run_flake8_analysis(self, directory: str, extensions: List[str]) -> Dict[str, Any]:
        """Run flake8 code quality analysis"""
        try:
            logger.info("🔍 Running flake8 analysis...")
            
            # Build flake8 command
            cmd = ["flake8", directory, "--format=json", "--statistics"]
            
            # Add extension filters
            for ext in extensions:
                cmd.extend(["--include", f"*{ext}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "issues": [],
                    "statistics": {},
                    "output": result.stdout
                }
            else:
                # Parse JSON output even if there are issues
                try:
                    issues = json.loads(result.stdout) if result.stdout else []
                    return {
                        "success": True,
                        "issues": issues,
                        "statistics": self._parse_flake8_stats(result.stderr),
                        "output": result.stdout
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "issues": [],
                        "statistics": {},
                        "error": result.stderr,
                        "output": result.stdout
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "issues": [],
                "statistics": {},
                "error": "flake8 analysis timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "issues": [],
                "statistics": {},
                "error": str(e)
            }
    
    async def _run_bandit_analysis(self, directory: str, extensions: List[str]) -> Dict[str, Any]:
        """Run bandit security analysis"""
        try:
            logger.info("🔍 Running bandit security analysis...")
            
            cmd = ["bandit", "-r", directory, "-f", "json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "issues": [],
                    "statistics": {},
                    "output": result.stdout
                }
            else:
                try:
                    issues = json.loads(result.stdout) if result.stdout else []
                    return {
                        "success": True,
                        "issues": issues,
                        "statistics": self._parse_bandit_stats(result.stderr),
                        "output": result.stdout
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "issues": [],
                        "statistics": {},
                        "error": result.stderr,
                        "output": result.stdout
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "issues": [],
                "statistics": {},
                "error": "bandit analysis timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "issues": [],
                "statistics": {},
                "error": str(e)
            }
    
    def _parse_flake8_stats(self, stderr: str) -> Dict[str, Any]:
        """Parse flake8 statistics from stderr"""
        stats = {}
        for line in stderr.split('\n'):
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if value.isdigit():
                        stats[key] = int(value)
        return stats
    
    def _parse_bandit_stats(self, stderr: str) -> Dict[str, Any]:
        """Parse bandit statistics from stderr"""
        stats = {}
        for line in stderr.split('\n'):
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if value.isdigit():
                        stats[key] = int(value)
        return stats
    
    async def _get_ai_insights(
        self, 
        flake8_results: Dict[str, Any], 
        bandit_results: Dict[str, Any], 
        directory: str
    ) -> Dict[str, Any]:
        """Get AI insights using the advanced API manager"""
        if not self.use_advanced_manager:
            return {"error": "Advanced API manager not enabled"}
        
        try:
            logger.info("🧠 Getting AI insights with advanced API manager...")
            
            # Prepare analysis data for AI
            analysis_data = {
                "directory": directory,
                "flake8_issues": len(flake8_results.get("issues", [])),
                "bandit_issues": len(bandit_results.get("issues", [])),
                "flake8_stats": flake8_results.get("statistics", {}),
                "bandit_stats": bandit_results.get("statistics", {}),
                "flake8_success": flake8_results.get("success", False),
                "bandit_success": bandit_results.get("success", False)
            }
            
            # Create AI prompt
            prompt = f"""
            Analyze the following code quality data and provide insights:
            
            Directory: {analysis_data['directory']}
            Flake8 Issues: {analysis_data['flake8_issues']}
            Bandit Security Issues: {analysis_data['bandit_issues']}
            Flake8 Statistics: {analysis_data['flake8_stats']}
            Bandit Statistics: {analysis_data['bandit_stats']}
            Flake8 Success: {analysis_data['flake8_success']}
            Bandit Success: {analysis_data['bandit_success']}
            
            Please provide:
            1. Overall code quality assessment
            2. Priority issues to address
            3. Security concerns
            4. Improvement recommendations
            5. Code quality score (0-100)
            """
            
            system_prompt = """You are an expert code quality analyst. Provide detailed, actionable insights about code quality, security, and best practices. Be specific and practical in your recommendations."""
            
            # Generate AI response with advanced failover
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
                    "insights": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider_name", "Failed")
                }
                
        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "Exception"
            }
    
    async def run_analysis(
        self, 
        directory: str, 
        extensions: List[str], 
        output_file: str
    ) -> Dict[str, Any]:
        """Run complete code quality analysis"""
        logger.info(f"🚀 Starting enhanced code quality analysis...")
        logger.info(f"   Directory: {directory}")
        logger.info(f"   Extensions: {extensions}")
        logger.info(f"   Advanced API Manager: {self.use_advanced_manager}")
        
        try:
            # Run code quality analysis
            analysis_results = await self.analyze_code_quality(directory, extensions)
            
            # Compile final results
            self.results.update({
                "code_quality_analysis": analysis_results,
                "analysis_metadata": {
                    "directory": directory,
                    "extensions": extensions,
                    "use_advanced_manager": self.use_advanced_manager,
                    "timestamp": str(asyncio.get_event_loop().time())
                }
            })
            
            # Add integration stats if using advanced manager
            if self.use_advanced_manager:
                self.results["integration_stats"] = self.integration.get_integration_stats()
            
            # Save results
            integration.save_results(self.results, output_file)
            
            logger.info(f"✅ Analysis completed successfully!")
            logger.info(f"   Results saved to: {output_file}")
            
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            error_results = {
                "error": str(e),
                "success": False,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            integration.save_results(error_results, output_file)
            return error_results

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Enhanced Code Quality Inspector")
    parser.add_argument("--directory", default=".", help="Directory to analyze")
    parser.add_argument("--extensions", nargs="+", default=[".py"], help="File extensions to analyze")
    parser.add_argument("--output", default="code_quality_results.json", help="Output file")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--mode", default="comprehensive", help="Analysis mode")
    parser.add_argument("--priority", default="normal", help="Priority level")
    parser.add_argument("--target", default="all", help="Target components")
    parser.add_argument("--providers", default="all", help="AI providers to use")
    
    args = parser.parse_args()
    
    # Create inspector
    inspector = EnhancedCodeQualityInspector(use_advanced_manager=args.use_advanced_manager)
    
    # Run analysis
    results = await inspector.run_analysis(
        directory=args.directory,
        extensions=args.extensions,
        output_file=args.output
    )
    
    # Print summary
    if results.get("success", True):
        print("\n" + "=" * 80)
        print("📊 CODE QUALITY ANALYSIS SUMMARY")
        print("=" * 80)
        
        if "code_quality_analysis" in results:
            analysis = results["code_quality_analysis"]
            print(f"Flake8 Issues: {len(analysis.get('flake8_results', {}).get('issues', []))}")
            print(f"Bandit Issues: {len(analysis.get('bandit_results', {}).get('issues', []))}")
            
            if "ai_insights" in analysis and analysis["ai_insights"].get("success"):
                print(f"AI Provider: {analysis['ai_insights'].get('provider', 'Unknown')}")
                print(f"Response Time: {analysis['ai_insights'].get('response_time', 0):.2f}s")
        
        if "integration_stats" in results:
            stats = results["integration_stats"]
            print(f"Total Requests: {stats.get('total_requests', 0)}")
            print(f"Success Rate: {stats.get('success_rate', '0%')}")
            print(f"Active Providers: {len(stats.get('active_providers', []))}")
        
        print("=" * 80)
    else:
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())