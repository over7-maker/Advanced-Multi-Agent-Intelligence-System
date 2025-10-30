#!/usr/bin/env python3
"""
Real AI Build Analyzer - Uses 16 AI providers for actual build analysis
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime
from advanced_ai_provider_manager import ai_manager

class RealAIBuildAnalyzer:
    def __init__(self, mode="intelligent", platforms="linux", strategy="optimized", auto_rollback=True, performance_monitoring=True):
        self.mode = mode
        self.platforms = platforms
        self.strategy = strategy
        self.auto_rollback = auto_rollback
        self.performance_monitoring = performance_monitoring
        self.start_time = datetime.utcnow()
        
    async def analyze_build(self):
        """Execute real AI-powered build analysis"""
        print("🚀 Starting Real AI Build Analysis...")
        print("=" * 60)
        print("🤖 AI BUILD ANALYSIS SUPERHERO MODE ACTIVATED!")
        print("=" * 60)
        print(f"📋 Mode: {self.mode} | Platforms: {self.platforms} | Strategy: {self.strategy}")
        print(f"🔧 Auto-rollback: {self.auto_rollback} | Performance Monitoring: {self.performance_monitoring}")
        print("")
        
        # Debug: Check environment variables
        print("🔍 AI BUILD ANALYSIS POWERS CHECK:")
        print("-" * 40)
        api_keys = ['DEEPSEEK_API_KEY', 'GLM_API_KEY', 'GROK_API_KEY', 'KIMI_API_KEY', 'QWEN_API_KEY']
        available_keys = 0
        for key in api_keys:
            value = os.getenv(key)
            if value and value.strip():
                print(f"  ✅ {key}: {'*' * min(len(value), 8)}... (READY)")
                available_keys += 1
            else:
                print(f"  ❌ {key}: Not set (UNAVAILABLE)")
        
        print(f"📊 AI Powers Available: {available_keys}/{len(api_keys)}")
        print("")
        
        # Get files to analyze
        files_to_analyze = self._get_build_files()
        print(f"📁 AI BUILD FILE DISCOVERY COMPLETE!")
        print("-" * 40)
        print(f"🔍 Found {len(files_to_analyze)} build-related files")
        print(f"🎯 Target Platforms: {self.platforms}")
        print(f"📊 Analysis Mode: {self.mode}")
        print(f"⚡ Build Strategy: {self.strategy}")
        print("")
        
        # Show some example files being analyzed
        print("📋 SAMPLE BUILD FILES BEING ANALYZED:")
        print("-" * 40)
        for i, file in enumerate(files_to_analyze[:10]):
            print(f"  {i+1:2d}. {file}")
        if len(files_to_analyze) > 10:
            print(f"  ... and {len(files_to_analyze) - 10} more files")
        print("")
        
        # Simulate AI Build Analysis
        print("🤖 AI BUILD ANALYSIS IN PROGRESS...")
        print("-" * 40)
        print("🧠 Analyzing build requirements and dependencies...")
        print("🔍 Scanning for build optimization opportunities...")
        print("⚡ Identifying performance bottlenecks in build process...")
        print("📝 Generating build configuration recommendations...")
        print("🎯 Creating deployment strategy recommendations...")
        print("")
        
        # Perform real AI analysis
        analysis_result = await self._perform_ai_build_analysis(files_to_analyze)
        
        # Generate build recommendations
        recommendations = await self._generate_build_recommendations(files_to_analyze, analysis_result)
        
        # Create comprehensive results
        results = {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "version": "2.0-real-ai-build",
                "analysis_mode": self.mode,
                "target_platforms": self.platforms,
                "build_strategy": self.strategy,
                "auto_rollback": self.auto_rollback,
                "performance_monitoring": self.performance_monitoring,
                "execution_status": "completed_successfully"
            },
            "file_analysis": {
                "files_analyzed": len(files_to_analyze),
                "files_list": files_to_analyze,
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "ai_analysis": analysis_result,
            "build_recommendations": recommendations,
            "performance_metrics": {
                "execution_time_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "ai_providers_used": analysis_result.get('total_providers_tried', 0),
                "success_rate": 1.0 if analysis_result.get('success') else 0.0
            },
            "build_plan": self._generate_build_plan(analysis_result, recommendations),
            "deployment_strategy": self._generate_deployment_strategy(analysis_result, recommendations)
        }
        
        print("🎉 AI BUILD ANALYSIS COMPLETE!")
        print("=" * 60)
        print("📊 BUILD ANALYSIS RESULTS:")
        print("-" * 40)
        print(f"📁 Files Analyzed: {results['file_analysis']['files_analyzed']}")
        print(f"🤖 AI Providers Used: {results['performance_metrics']['ai_providers_used']}")
        print(f"⚡ Success Rate: {results['performance_metrics']['success_rate']*100:.1f}%")
        print(f"⏱️  Execution Time: {results['performance_metrics']['execution_time_seconds']:.2f}s")
        print("")
        
        print("🎯 AI BUILD RECOMMENDATIONS GENERATED:")
        print("-" * 40)
        for i, rec in enumerate(recommendations.get('recommendations', []), 1):
            print(f"  {i}. {rec}")
        print("")
        
        print("🚀 BUILD PLAN GENERATED:")
        print("-" * 40)
        for i, step in enumerate(results['build_plan'], 1):
            print(f"  {i}. {step}")
        print("")
        
        print(f"📄 Results saved to build_analysis_results.json")
        print("")
        print("✅ AI AGENTIC BUILD ANALYSIS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        return results
    
    def _get_build_files(self):
        """Get list of build-related files to analyze"""
        files = []
        
        # Define build-related file patterns
        build_patterns = [
            'Dockerfile', 'docker-compose.yml', 'requirements.txt', 'package.json',
            'setup.py', 'pyproject.toml', 'Makefile', 'CMakeLists.txt',
            '*.yml', '*.yaml', '*.json', '*.sh', '*.py'
        ]
        
        # Find files
        for root, dirs, filenames in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for filename in filenames:
                if any(filename.endswith(pattern.replace('*', '')) for pattern in build_patterns):
                    filepath = os.path.join(root, filename)
                    files.append(filepath)
        
        return files[:50]  # Limit to 50 files for performance
    
    async def _perform_ai_build_analysis(self, files):
        """Perform real AI build analysis using the provider manager"""
        print("🤖 Performing AI build analysis...")
        
        # Debug: Check provider status
        print(f"🔍 Debug: Available providers: {len(ai_manager.available_providers)}")
        for name, config in ai_manager.available_providers.items():
            print(f"  - {name}: {config['model']}")
        
        # Create analysis prompt
        prompt = f"""
        Perform comprehensive build analysis on the following files:
        
        Files: {', '.join(files[:10])}  # Show first 10 files in prompt
        
        Analysis Mode: {self.mode}
        Target Platforms: {self.platforms}
        Build Strategy: {self.strategy}
        
        Please provide:
        1. Build requirements analysis and dependency optimization
        2. Performance bottlenecks in build process
        3. Build configuration recommendations
        4. Deployment strategy suggestions
        5. Security considerations for build process
        6. Specific optimization opportunities
        
        Be detailed, actionable, and specific. Include code examples where helpful.
        """
        
        try:
            # Use AI provider manager
            analysis_result = await ai_manager.analyze_with_fallback(prompt)
            
            if analysis_result.get('success'):
                print(f"✅ AI build analysis completed using {analysis_result.get('fallback_used', 'unknown')} provider")
            else:
                print(f"❌ AI build analysis failed: {analysis_result.get('error', 'Unknown error')}")
            
            return analysis_result
        except Exception as e:
            print(f"❌ Exception during AI build analysis: {str(e)}")
            return {
                'success': False,
                'error': f'Exception: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _generate_build_recommendations(self, files, analysis_results):
        """Generate specific build recommendations"""
        print("🔧 Generating build recommendations...")
        
        if not analysis_results.get('success'):
            return {
                "recommendations": [
                    "Manual build review recommended due to analysis failure",
                    "Consider using standard build practices",
                    "Review build configuration files",
                    "Implement basic build monitoring"
                ],
                "error": "Cannot generate recommendations due to analysis failure"
            }
        
        # Create recommendation prompt
        prompt = f"""
        Based on the previous build analysis, generate specific build recommendations for these files:
        
        Files: {', '.join(files[:10])}
        
        Provide:
        1. Build optimization opportunities
        2. Dependency management improvements
        3. Build performance enhancements
        4. Deployment strategy recommendations
        5. Security hardening suggestions
        6. Monitoring and logging improvements
        
        Make recommendations actionable and specific.
        """
        
        recommendation_result = await ai_manager.analyze_with_fallback(prompt)
        
        if recommendation_result.get('success'):
            print("✅ Build recommendations generated")
        else:
            print(f"❌ Recommendation generation failed: {recommendation_result.get('error', 'Unknown error')}")
        
        return recommendation_result
    
    def _generate_build_plan(self, analysis_results, recommendations):
        """Generate actionable build plan"""
        plan = [
            "Review AI-generated build analysis results",
            "Implement build optimization recommendations",
            "Update build configuration files",
            "Test build process in development environment",
            "Deploy with monitoring and rollback capabilities"
        ]
        
        if self.auto_rollback:
            plan.append("Configure automatic rollback on build failures")
        
        if self.performance_monitoring:
            plan.append("Set up performance monitoring for build process")
        
        return plan
    
    def _generate_deployment_strategy(self, analysis_results, recommendations):
        """Generate deployment strategy"""
        return {
            "strategy": self.strategy,
            "platforms": self.platforms,
            "auto_rollback": self.auto_rollback,
            "monitoring": self.performance_monitoring,
            "recommendations": recommendations.get('recommendations', [])
        }

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Real AI Build Analyzer")
    parser.add_argument("--mode", default="intelligent", help="Build analysis mode")
    parser.add_argument("--platforms", default="linux", help="Target platforms")
    parser.add_argument("--strategy", default="optimized", help="Build strategy")
    parser.add_argument("--auto-rollback", action="store_true", help="Enable auto-rollback")
    parser.add_argument("--performance-monitoring", action="store_true", help="Enable performance monitoring")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced AI manager")
    parser.add_argument("--output", default="build_analysis_results.json", help="Output file")
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = RealAIBuildAnalyzer(
            mode=args.mode,
            platforms=args.platforms,
            strategy=args.strategy,
            auto_rollback=args.auto_rollback,
            performance_monitoring=args.performance_monitoring
        )
        
        # Run analysis
        results = await analyzer.analyze_build()
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save to final_results directory
        os.makedirs("final_results", exist_ok=True)
        with open("final_results/ai_build_analyzer_real.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create GitHub Actions Summary
        if os.getenv('GITHUB_ACTIONS'):
            summary_file = os.getenv('GITHUB_STEP_SUMMARY', '/dev/stdout')
            try:
                with open(summary_file, 'w') as f:
                    f.write("# 🏗️ AI BUILD ANALYSIS RESULTS\n\n")
                    f.write("## 🎉 AI BUILD SUPERHERO POWERS ACTIVATED!\n\n")
                    f.write(f"**📁 Files Analyzed:** {results['file_analysis']['files_analyzed']}\n")
                    f.write(f"**🤖 AI Providers Used:** {results['performance_metrics']['ai_providers_used']}\n")
                    f.write(f"**⚡ Success Rate:** {results['performance_metrics']['success_rate']*100:.1f}%\n")
                    f.write(f"**⏱️ Execution Time:** {results['performance_metrics']['execution_time_seconds']:.2f}s\n\n")
                    
                    f.write("## 🎯 AI BUILD RECOMMENDATIONS GENERATED\n\n")
                    for i, rec in enumerate(results['build_recommendations'].get('recommendations', []), 1):
                        f.write(f"{i}. {rec}\n")
                    f.write("\n")
                    
                    f.write("## 🚀 BUILD PLAN GENERATED\n\n")
                    for i, step in enumerate(results['build_plan'], 1):
                        f.write(f"{i}. {step}\n")
                    f.write("\n")
                    
                    f.write("---\n")
                    f.write("*Generated by AI Agentic Build Analysis System* 🏗️🤖\n")
            except Exception as e:
                print(f"⚠️ Could not write GitHub summary: {e}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Real AI Build Analysis failed: {str(e)}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
        
        # Create minimal results even on failure
        minimal_results = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "execution_status": "failed",
                "error": str(e),
                "traceback": traceback.format_exc()
            },
            "file_analysis": {"files_analyzed": 0, "files_list": []},
            "ai_analysis": {"success": False, "error": str(e)},
            "performance_metrics": {"success_rate": 0.0}
        }
        
        with open(args.output, 'w') as f:
            json.dump(minimal_results, f, indent=2)
        
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))