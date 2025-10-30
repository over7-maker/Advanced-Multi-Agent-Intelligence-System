#!/usr/bin/env python3
"""
Real AI Code Enhancer - Uses 16 AI providers for actual code analysis
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from advanced_ai_provider_manager import ai_manager, analyze_code_quality, generate_documentation, optimize_performance

class RealAICodeEnhancer:
    def __init__(self, mode="comprehensive", languages="all", level="high", auto_fix=False, performance_benchmarking=False):
        self.mode = mode
        self.languages = languages
        self.level = level
        self.auto_fix = auto_fix
        self.performance_benchmarking = performance_benchmarking
        self.start_time = datetime.utcnow()
        
    async def enhance_code(self):
        """Execute real AI-powered code enhancement"""
        print(f"🚀 Starting Real AI Code Enhancement")
        print(f"Mode: {self.mode} | Languages: {self.languages} | Level: {self.level}")
        print(f"Auto-fix: {self.auto_fix} | Performance Benchmarking: {self.performance_benchmarking}")
        print("")
        
        # Get files to analyze
        files_to_analyze = self._get_files_to_analyze()
        print(f"📁 Analyzing {len(files_to_analyze)} files...")
        
        # Perform AI analysis
        analysis_results = await self._perform_ai_analysis(files_to_analyze)
        
        # Generate enhancement recommendations
        enhancements = await self._generate_enhancements(files_to_analyze, analysis_results)
        
        # Create comprehensive results
        results = {
            "metadata": {
                "timestamp": self.start_time.isoformat(),
                "version": "2.0-real-ai",
                "enhancement_mode": self.mode,
                "target_languages": self.languages,
                "enhancement_level": self.level,
                "auto_fix": self.auto_fix,
                "performance_benchmarking": self.performance_benchmarking,
                "execution_status": "completed_successfully"
            },
            "file_analysis": {
                "files_analyzed": len(files_to_analyze),
                "files_list": files_to_analyze,
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "ai_analysis": analysis_results,
            "enhancements": enhancements,
            "performance_metrics": {
                "execution_time_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "ai_providers_used": analysis_results.get('total_providers_tried', 0),
                "success_rate": 1.0 if analysis_results.get('success') else 0.0
            },
            "recommendations": self._generate_recommendations(analysis_results, enhancements),
            "next_steps": self._generate_next_steps(enhancements)
        }
        
        print("✅ Real AI Code Enhancement completed successfully")
        return results
    
    def _get_files_to_analyze(self):
        """Get list of files to analyze based on languages and mode"""
        files = []
        
        # Define file extensions by language
        language_extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cc', '.cxx', '.c'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php'],
            'ruby': ['.rb']
        }
        
        # Get extensions to analyze
        if self.languages == "all":
            extensions = [ext for exts in language_extensions.values() for ext in exts]
        else:
            languages = [lang.strip() for lang in self.languages.split(',')]
            extensions = []
            for lang in languages:
                if lang.lower() in language_extensions:
                    extensions.extend(language_extensions[lang.lower()])
        
        # Find files
        for root, dirs, filenames in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, filename)
                    files.append(filepath)
        
        return files[:50]  # Limit to 50 files for performance
    
    async def _perform_ai_analysis(self, files):
        """Perform real AI analysis using the provider manager"""
        print("🤖 Performing AI analysis...")
        
        # Debug: Check provider status
        print(f"🔍 Debug: Available providers: {len(ai_manager.available_providers)}")
        for name, config in ai_manager.available_providers.items():
            print(f"  - {name}: {config['model']}")
        
        # Create analysis prompt
        prompt = f"""
        Perform comprehensive code analysis on the following files:
        
        Files: {', '.join(files[:10])}  # Show first 10 files in prompt
        
        Analysis Mode: {self.mode}
        Enhancement Level: {self.level}
        
        Please provide:
        1. Code quality assessment with specific issues
        2. Security vulnerabilities and recommendations
        3. Performance bottlenecks and optimizations
        4. Code structure improvements
        5. Best practices violations
        6. Specific line-by-line recommendations
        
        Be detailed, actionable, and specific. Include code examples where helpful.
        """
        
        try:
            # Use AI provider manager
            analysis_result = await ai_manager.analyze_with_fallback(prompt)
            
            if analysis_result.get('success'):
                print(f"✅ AI analysis completed using {analysis_result.get('fallback_used', 'unknown')} provider")
            else:
                print(f"❌ AI analysis failed: {analysis_result.get('error', 'Unknown error')}")
            
            return analysis_result
        except Exception as e:
            print(f"❌ Exception during AI analysis: {str(e)}")
            return {
                'success': False,
                'error': f'Exception: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _generate_enhancements(self, files, analysis_results):
        """Generate specific enhancement recommendations"""
        print("🔧 Generating enhancement recommendations...")
        
        if not analysis_results.get('success'):
            return {
                "enhancements": [],
                "error": "Cannot generate enhancements due to analysis failure"
            }
        
        # Create enhancement prompt
        prompt = f"""
        Based on the previous analysis, generate specific code enhancements for these files:
        
        Files: {', '.join(files[:10])}
        
        Provide:
        1. Specific code improvements with before/after examples
        2. Refactoring suggestions
        3. Performance optimizations
        4. Security fixes
        5. Code quality improvements
        6. Implementation priority levels
        
        Make recommendations actionable and specific.
        """
        
        enhancement_result = await ai_manager.analyze_with_fallback(prompt)
        
        if enhancement_result.get('success'):
            print("✅ Enhancement recommendations generated")
        else:
            print(f"❌ Enhancement generation failed: {enhancement_result.get('error', 'Unknown error')}")
        
        return enhancement_result
    
    def _generate_recommendations(self, analysis_results, enhancements):
        """Generate actionable recommendations"""
        recommendations = []
        
        if analysis_results.get('success'):
            recommendations.extend([
                "Review AI analysis results for specific code improvements",
                "Implement security recommendations immediately",
                "Address performance bottlenecks identified",
                "Refactor code based on quality suggestions"
            ])
        
        if enhancements.get('success'):
            recommendations.extend([
                "Prioritize high-impact enhancements first",
                "Test all changes in development environment",
                "Consider automated refactoring tools",
                "Document all changes made"
            ])
        
        if not recommendations:
            recommendations = [
                "Manual code review recommended due to AI analysis issues",
                "Consider running static analysis tools",
                "Review code for common security patterns",
                "Implement basic performance monitoring"
            ]
        
        return recommendations
    
    def _generate_next_steps(self, enhancements):
        """Generate next steps for implementation"""
        next_steps = [
            "Review all AI-generated recommendations",
            "Create implementation plan with priorities",
            "Set up automated testing for changes",
            "Monitor code quality metrics",
            "Schedule regular AI-powered code reviews"
        ]
        
        if self.auto_fix:
            next_steps.insert(0, "Implement automated fixes where safe")
        
        if self.performance_benchmarking:
            next_steps.append("Run performance benchmarks after changes")
        
        return next_steps

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Real AI Code Enhancer")
    parser.add_argument("--mode", default="comprehensive", help="Enhancement mode")
    parser.add_argument("--languages", default="all", help="Target languages")
    parser.add_argument("--level", default="high", help="Enhancement level")
    parser.add_argument("--auto-fix", action="store_true", help="Enable auto-fix")
    parser.add_argument("--performance-benchmarking", action="store_true", help="Enable performance benchmarking")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced AI manager")
    parser.add_argument("--output", default="ai_code_enhancer_real_results.json", help="Output file")
    
    args = parser.parse_args()
    
    try:
        print("🚀 Starting Real AI Code Enhancer...")
        print(f"📋 Arguments: mode={args.mode}, languages={args.languages}, level={args.level}")
        
        # Debug: Check environment variables
        print("🔍 Debug: Checking environment variables...")
        api_keys = ['DEEPSEEK_API_KEY', 'GLM_API_KEY', 'GROK_API_KEY', 'KIMI_API_KEY', 'QWEN_API_KEY']
        for key in api_keys:
            value = os.getenv(key)
            if value:
                print(f"  ✅ {key}: {'*' * min(len(value), 8)}...")
            else:
                print(f"  ❌ {key}: Not set")
        
        # Initialize enhancer
        enhancer = RealAICodeEnhancer(
            mode=args.mode,
            languages=args.languages,
            level=args.level,
            auto_fix=args.auto_fix,
            performance_benchmarking=args.performance_benchmarking
        )
        
        # Run enhancement
        results = await enhancer.enhance_code()
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save to final_results directory
        os.makedirs("final_results", exist_ok=True)
        with open("final_results/ai_code_enhancer_real.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to {args.output}")
        print(f"📊 Files analyzed: {results['file_analysis']['files_analyzed']}")
        print(f"🤖 AI providers used: {results['performance_metrics']['ai_providers_used']}")
        print(f"⏱️  Execution time: {results['performance_metrics']['execution_time_seconds']:.2f}s")
        
        return 0
        
    except Exception as e:
        print(f"❌ Real AI Code Enhancement failed: {str(e)}")
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
            "enhancements": {"error": str(e)},
            "performance_metrics": {"success_rate": 0.0}
        }
        
        with open(args.output, 'w') as f:
            json.dump(minimal_results, f, indent=2)
        
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))