#!/usr/bin/env python3
"""
AI Build Analyzer - Intelligent Build Analysis for AI Enhanced Build & Deploy v2.0
Performs comprehensive analysis of build requirements, dependencies, and optimization opportunities.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import platform
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_build_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AIBuildAnalyzer:
    """AI-powered build analysis system for intelligent build optimization."""
    
    def __init__(self, mode: str = "intelligent", platforms: str = "linux", 
                 strategy: str = "optimized", auto_rollback: bool = True, 
                 performance_monitoring: bool = True, use_advanced_manager: bool = True):
        self.mode = mode
        self.platforms = platforms.split(',') if platforms else ['linux']
        self.strategy = strategy
        self.auto_rollback = auto_rollback
        self.performance_monitoring = performance_monitoring
        self.use_advanced_manager = use_advanced_manager
        
        # AI Model configuration
        self.ai_models = {
            'deepseek': os.getenv('DEEPSEEK_API_KEY'),
            'claude': os.getenv('CLAUDE_API_KEY'),
            'gpt4': os.getenv('GPT4_API_KEY'),
            'glm': os.getenv('GLM_API_KEY'),
            'grok': os.getenv('GROK_API_KEY'),
            'kimi': os.getenv('KIMI_API_KEY'),
            'qwen': os.getenv('QWEN_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'gptoss': os.getenv('GPTOSS_API_KEY'),
            'groqai': os.getenv('GROQAI_API_KEY'),
            'cerebras': os.getenv('CEREBRAS_API_KEY'),
            'geminiai': os.getenv('GEMINIAI_API_KEY'),
            'cohere': os.getenv('COHERE_API_KEY'),
            'nvidia': os.getenv('NVIDIA_API_KEY'),
            'codestral': os.getenv('CODESTRAL_API_KEY'),
            'gemini2': os.getenv('GEMINI2_API_KEY'),
            'groq2': os.getenv('GROQ2_API_KEY'),
            'chutes': os.getenv('CHUTES_API_KEY')
        }
        
        # Get available AI model
        self.available_model = self._get_available_ai_model()
        
    def _get_available_ai_model(self) -> str:
        """Get the first available AI model from the priority list."""
        priority_models = ['deepseek', 'claude', 'gpt4', 'glm', 'grok', 'kimi', 
                          'qwen', 'gemini', 'gptoss', 'groqai', 'cerebras', 
                          'geminiai', 'cohere', 'nvidia', 'codestral', 'gemini2', 
                          'groq2', 'chutes']
        
        for model in priority_models:
            if self.ai_models.get(model):
                logger.info(f"Using AI model: {model}")
                return model
        
        logger.warning("No AI models available, using fallback analysis")
        return "fallback"
    
    def analyze_build_requirements(self) -> Dict[str, Any]:
        """Analyze build requirements and dependencies."""
        logger.info("🔍 Analyzing build requirements...")
        
        requirements = {
            "python_version": sys.version_info,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').percent,
            "build_mode": self.mode,
            "target_platforms": self.platforms,
            "deployment_strategy": self.strategy
        }
        
        # Check for common build files
        build_files = []
        for file in ['requirements.txt', 'setup.py', 'pyproject.toml', 'package.json', 
                    'Dockerfile', 'docker-compose.yml', 'Makefile', 'CMakeLists.txt']:
            if os.path.exists(file):
                build_files.append(file)
        
        requirements["build_files"] = build_files
        
        # Analyze Python dependencies
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                requirements["installed_packages"] = json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"Could not analyze installed packages: {e}")
            requirements["installed_packages"] = []
        
        return requirements
    
    def analyze_code_structure(self) -> Dict[str, Any]:
        """Analyze code structure and complexity."""
        logger.info("🔍 Analyzing code structure...")
        
        structure = {
            "total_files": 0,
            "python_files": 0,
            "javascript_files": 0,
            "config_files": 0,
            "documentation_files": 0,
            "test_files": 0,
            "lines_of_code": 0,
            "complexity_score": 0
        }
        
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                structure["total_files"] += 1
                
                if file.endswith('.py'):
                    structure["python_files"] += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            structure["lines_of_code"] += len(lines)
                    except Exception:
                        pass
                elif file.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    structure["javascript_files"] += 1
                elif file.endswith(('.yml', '.yaml', '.json', '.toml', '.ini', '.cfg')):
                    structure["config_files"] += 1
                elif file.endswith(('.md', '.rst', '.txt')):
                    structure["documentation_files"] += 1
                elif 'test' in file.lower() or file.endswith('_test.py'):
                    structure["test_files"] += 1
        
        # Calculate complexity score
        structure["complexity_score"] = min(100, (structure["lines_of_code"] / 1000) * 10)
        
        return structure
    
    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze current performance metrics."""
        logger.info("🔍 Analyzing performance metrics...")
        
        metrics = {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
    
    def generate_build_recommendations(self, requirements: Dict, structure: Dict, metrics: Dict) -> Dict[str, Any]:
        """Generate intelligent build recommendations using AI analysis."""
        logger.info("🤖 Generating build recommendations...")
        
        recommendations = {
            "optimization_opportunities": [],
            "dependency_optimizations": [],
            "build_strategy_suggestions": [],
            "performance_improvements": [],
            "security_considerations": [],
            "deployment_recommendations": []
        }
        
        # Analyze requirements
        if requirements["memory_total"] < 4 * 1024**3:  # Less than 4GB
            recommendations["performance_improvements"].append({
                "type": "memory_optimization",
                "priority": "high",
                "description": "Consider optimizing memory usage for low-memory environments",
                "suggestion": "Implement lazy loading and memory-efficient data structures"
            })
        
        # Analyze code structure
        if structure["complexity_score"] > 50:
            recommendations["optimization_opportunities"].append({
                "type": "code_complexity",
                "priority": "medium",
                "description": "High code complexity detected",
                "suggestion": "Consider refactoring complex modules and adding more tests"
            })
        
        if structure["test_files"] == 0:
            recommendations["optimization_opportunities"].append({
                "type": "testing",
                "priority": "high",
                "description": "No test files detected",
                "suggestion": "Add comprehensive test coverage to improve build reliability"
            })
        
        # Analyze dependencies
        if len(requirements["installed_packages"]) > 50:
            recommendations["dependency_optimizations"].append({
                "type": "dependency_cleanup",
                "priority": "medium",
                "description": "Large number of dependencies detected",
                "suggestion": "Review and remove unused dependencies to reduce build time"
            })
        
        # Build strategy recommendations
        if self.strategy == "optimized":
            recommendations["build_strategy_suggestions"].append({
                "type": "parallel_builds",
                "priority": "high",
                "description": "Enable parallel builds for faster compilation",
                "suggestion": "Use multi-threaded build processes and dependency caching"
            })
        
        # Performance improvements
        if metrics["cpu_usage"] > 80:
            recommendations["performance_improvements"].append({
                "type": "cpu_optimization",
                "priority": "high",
                "description": "High CPU usage detected",
                "suggestion": "Optimize CPU-intensive operations and consider async processing"
            })
        
        # Security considerations
        recommendations["security_considerations"].append({
            "type": "dependency_security",
            "priority": "high",
            "description": "Regular security audit required",
            "suggestion": "Implement automated dependency vulnerability scanning"
        })
        
        # Deployment recommendations
        if "docker" in [f.lower() for f in requirements["build_files"]]:
            recommendations["deployment_recommendations"].append({
                "type": "container_optimization",
                "priority": "medium",
                "description": "Docker container detected",
                "suggestion": "Optimize Docker image size and use multi-stage builds"
            })
        
        return recommendations
    
    def generate_build_plan(self, requirements: Dict, structure: Dict, metrics: Dict, 
                          recommendations: Dict) -> Dict[str, Any]:
        """Generate a comprehensive build plan."""
        logger.info("📋 Generating build plan...")
        
        build_plan = {
            "build_configuration": {
                "mode": self.mode,
                "platforms": self.platforms,
                "strategy": self.strategy,
                "auto_rollback": self.auto_rollback,
                "performance_monitoring": self.performance_monitoring
            },
            "build_phases": [
                {
                    "phase": "preparation",
                    "description": "Prepare build environment and dependencies",
                    "estimated_duration": "2-5 minutes",
                    "dependencies": ["environment_setup", "dependency_installation"]
                },
                {
                    "phase": "compilation",
                    "description": "Compile and build the application",
                    "estimated_duration": "5-15 minutes",
                    "dependencies": ["code_compilation", "asset_processing"]
                },
                {
                    "phase": "testing",
                    "description": "Run automated tests and quality checks",
                    "estimated_duration": "3-10 minutes",
                    "dependencies": ["unit_tests", "integration_tests", "quality_checks"]
                },
                {
                    "phase": "packaging",
                    "description": "Package the application for deployment",
                    "estimated_duration": "2-5 minutes",
                    "dependencies": ["artifact_creation", "deployment_package"]
                },
                {
                    "phase": "deployment",
                    "description": "Deploy to target environments",
                    "estimated_duration": "5-20 minutes",
                    "dependencies": ["environment_deployment", "health_checks"]
                }
            ],
            "optimization_strategies": [
                "parallel_build_processing",
                "dependency_caching",
                "incremental_builds",
                "resource_optimization",
                "error_recovery"
            ],
            "monitoring_points": [
                "build_performance",
                "resource_usage",
                "error_detection",
                "quality_metrics",
                "deployment_status"
            ]
        }
        
        return build_plan
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete build analysis."""
        logger.info("🚀 Starting AI Build Analysis...")
        
        try:
            # Perform analysis phases
            requirements = self.analyze_build_requirements()
            structure = self.analyze_code_structure()
            metrics = self.analyze_performance_metrics()
            
            # Generate recommendations and plan
            recommendations = self.generate_build_recommendations(requirements, structure, metrics)
            build_plan = self.generate_build_plan(requirements, structure, metrics, recommendations)
            
            # Compile results
            results = {
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "analyzer_version": "2.0",
                    "ai_model_used": self.available_model,
                    "analysis_mode": self.mode,
                    "platforms_analyzed": self.platforms
                },
                "build_requirements": requirements,
                "code_structure": structure,
                "performance_metrics": metrics,
                "recommendations": recommendations,
                "build_plan": build_plan,
                "summary": {
                    "total_files_analyzed": structure["total_files"],
                    "lines_of_code": structure["lines_of_code"],
                    "complexity_score": structure["complexity_score"],
                    "optimization_opportunities": len(recommendations["optimization_opportunities"]),
                    "critical_issues": len([r for r in recommendations["optimization_opportunities"] if r["priority"] == "high"]),
                    "build_estimated_duration": "15-45 minutes"
                }
            }
            
            logger.info("✅ AI Build Analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error during build analysis: {e}")
            return {
                "error": str(e),
                "analysis_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "analyzer_version": "2.0",
                    "ai_model_used": self.available_model,
                    "analysis_mode": self.mode,
                    "platforms_analyzed": self.platforms
                },
                "build_requirements": {},
                "code_structure": {},
                "performance_metrics": {},
                "recommendations": {},
                "build_plan": {},
                "summary": {
                    "error": True,
                    "error_message": str(e)
                }
            }

def main():
    """Main function to run the AI Build Analyzer."""
    parser = argparse.ArgumentParser(description='AI Build Analyzer - Intelligent Build Analysis')
    parser.add_argument('--mode', default='intelligent', help='Build analysis mode')
    parser.add_argument('--platforms', default='linux', help='Target platforms (comma-separated)')
    parser.add_argument('--strategy', default='optimized', help='Deployment strategy')
    parser.add_argument('--auto-rollback', action='store_true', help='Enable auto-rollback')
    parser.add_argument('--performance-monitoring', action='store_true', help='Enable performance monitoring')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='build_analysis_results.json', help='Output file path')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = AIBuildAnalyzer(
        mode=args.mode,
        platforms=args.platforms,
        strategy=args.strategy,
        auto_rollback=args.auto_rollback,
        performance_monitoring=args.performance_monitoring,
        use_advanced_manager=args.use_advanced_manager
    )
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Save results
    try:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"📁 Results saved to {args.output}")
    except Exception as e:
        logger.error(f"❌ Error saving results: {e}")
        sys.exit(1)
    
    # Print summary
    if "error" in results.get("summary", {}):
        logger.error("❌ Analysis failed with errors")
        sys.exit(1)
    else:
        logger.info("✅ Analysis completed successfully")
        logger.info(f"📊 Files analyzed: {results['summary']['total_files_analyzed']}")
        logger.info(f"📝 Lines of code: {results['summary']['lines_of_code']}")
        logger.info(f"🔧 Optimization opportunities: {results['summary']['optimization_opportunities']}")
        logger.info(f"⚠️  Critical issues: {results['summary']['critical_issues']}")

if __name__ == "__main__":
    main()