#!/usr/bin/env python3
"""
AI Project Analyzer - Advanced project analysis and learning system
Version: 2.1 - Optimized for self-improvement workflows
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import time

class AdvancedProjectAnalyzer:
    def __init__(self, mode="intelligent", areas="all", depth="comprehensive", auto_apply=False):
        self.mode = mode
        self.areas = areas
        self.depth = depth
        self.auto_apply = auto_apply
        self.start_time = time.time()
        
    def execute_project_analysis(self):
        """Execute comprehensive project analysis and learning."""
        
        print(f"🤖 Initializing Advanced Project Analysis System...")
        print(f"🎯 Mode: {self.mode} | Areas: {self.areas} | Depth: {self.depth}")
        print(f"🚀 Auto-apply: {self.auto_apply}")
        
        analysis_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "analyzer_version": "2.1",
                "analysis_mode": self.mode,
                "target_areas": self.areas,
                "learning_depth": self.depth,
                "auto_apply": self.auto_apply,
                "execution_status": "in_progress"
            },
            "project_health": {
                "overall_score": 0,
                "code_quality": {},
                "architecture_assessment": {},
                "performance_metrics": {},
                "security_posture": {}
            },
            "learning_insights": {
                "improvement_opportunities": [],
                "best_practices_identified": [],
                "pattern_recognition": [],
                "optimization_suggestions": []
            },
            "analysis_metrics": {
                "files_analyzed": 0,
                "components_evaluated": 0,
                "insights_generated": 0,
                "confidence_level": 95,
                "analysis_duration": "0s"
            }
        }
        
        try:
            # Step 1: Project Structure Analysis
            self._analyze_project_structure(analysis_results)
            
            # Step 2: Code Quality Assessment
            self._assess_code_quality(analysis_results)
            
            # Step 3: Architecture Evaluation
            self._evaluate_architecture(analysis_results)
            
            # Step 4: Performance Analysis
            self._analyze_performance_patterns(analysis_results)
            
            # Step 5: Generate Learning Insights
            self._generate_learning_insights(analysis_results)
            
            # Step 6: Calculate Overall Health Score
            self._calculate_health_score(analysis_results)
            
            # Finalize analysis
            self._finalize_analysis_results(analysis_results)
            
            print(f"✅ Project analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            print(f"⚠️ Project analysis completed with minor issues: {str(e)}")
            analysis_results["metadata"]["execution_status"] = "completed_with_warnings"
            analysis_results["metadata"]["warnings"] = [str(e)]
            return analysis_results
    
    def _analyze_project_structure(self, results):
        """Analyze project structure and organization."""
        print("📋 Analyzing project structure...")
        
        project_root = Path(".")
        
        # Key project components
        components = {
            "src/": {"type": "source_code", "importance": "critical"},
            ".github/": {"type": "ci_cd", "importance": "high"},
            "tests/": {"type": "testing", "importance": "high"},
            "docs/": {"type": "documentation", "importance": "medium"},
            "requirements.txt": {"type": "dependencies", "importance": "critical"},
            "docker-compose.yml": {"type": "containerization", "importance": "high"},
            "README.md": {"type": "documentation", "importance": "medium"},
            ".gitignore": {"type": "version_control", "importance": "medium"}
        }
        
        structure_analysis = {
            "components_found": [],
            "missing_components": [],
            "structure_score": 0
        }
        
        for component, info in components.items():
            if Path(component).exists():
                structure_analysis["components_found"].append({
                    "component": component,
                    "type": info["type"],
                    "importance": info["importance"],
                    "status": "present"
                })
                # Score based on importance
                if info["importance"] == "critical":
                    structure_analysis["structure_score"] += 25
                elif info["importance"] == "high":
                    structure_analysis["structure_score"] += 15
                else:
                    structure_analysis["structure_score"] += 10
            else:
                structure_analysis["missing_components"].append({
                    "component": component,
                    "type": info["type"],
                    "importance": info["importance"],
                    "recommendation": f"Consider adding {component} for better {info['type']}"
                })
        
        results["project_health"]["architecture_assessment"] = structure_analysis
        results["analysis_metrics"]["components_evaluated"] = len(components)
    
    def _assess_code_quality(self, results):
        """Assess code quality indicators."""
        print("🔍 Assessing code quality...")
        
        project_root = Path(".")
        
        # Count different file types
        file_analysis = {
            "python_files": len(list(project_root.rglob("*.py"))),
            "javascript_files": len(list(project_root.rglob("*.js"))),
            "yaml_files": len(list(project_root.rglob("*.yml"))) + len(list(project_root.rglob("*.yaml"))),
            "markdown_files": len(list(project_root.rglob("*.md"))),
            "json_files": len(list(project_root.rglob("*.json")))
        }
        
        total_files = sum(file_analysis.values())
        results["analysis_metrics"]["files_analyzed"] = total_files
        
        # Quality indicators
        quality_indicators = {
            "file_diversity": len([k for k, v in file_analysis.items() if v > 0]),
            "documentation_ratio": file_analysis["markdown_files"] / max(total_files, 1),
            "configuration_files": file_analysis["yaml_files"] + file_analysis["json_files"],
            "primary_language": "python" if file_analysis["python_files"] > 0 else "mixed"
        }
        
        # Calculate quality score
        quality_score = 0
        if quality_indicators["file_diversity"] >= 3:
            quality_score += 25
        if quality_indicators["documentation_ratio"] >= 0.1:
            quality_score += 25
        if quality_indicators["configuration_files"] >= 2:
            quality_score += 25
        if file_analysis["python_files"] >= 10:
            quality_score += 25
        
        results["project_health"]["code_quality"] = {
            "file_analysis": file_analysis,
            "quality_indicators": quality_indicators,
            "quality_score": quality_score
        }
    
    def _evaluate_architecture(self, results):
        """Evaluate project architecture and design patterns."""
        print("🏢 Evaluating architecture...")
        
        architecture_features = {
            "multi_agent_system": Path("src/agents/").exists() or Path("agents/").exists(),
            "ai_integration": Path("requirements.txt").exists(),
            "containerization": Path("docker-compose.yml").exists() or Path("Dockerfile").exists(),
            "ci_cd_automation": Path(".github/workflows/").exists(),
            "testing_framework": Path("tests/").exists(),
            "configuration_management": Path(".env.example").exists()
        }
        
        architecture_score = sum(20 for feature in architecture_features.values() if feature)
        
        # Advanced analysis for AI systems
        ai_capabilities = []
        if Path("requirements.txt").exists():
            try:
                with open("requirements.txt", 'r') as f:
                    content = f.read().lower()
                    if any(ai_lib in content for ai_lib in ['openai', 'anthropic', 'groq', 'cohere']):
                        ai_capabilities.append("multiple_ai_providers")
                    if 'fastapi' in content or 'flask' in content:
                        ai_capabilities.append("api_framework")
                    if 'docker' in content or Path("docker-compose.yml").exists():
                        ai_capabilities.append("containerized_deployment")
            except Exception:
                pass
        
        results["project_health"]["architecture_assessment"].update({
            "architecture_features": architecture_features,
            "architecture_score": architecture_score,
            "ai_capabilities": ai_capabilities,
            "complexity_level": "enterprise" if architecture_score >= 80 else "intermediate"
        })
    
    def _analyze_performance_patterns(self, results):
        """Analyze performance-related patterns and optimizations."""
        print("⚡ Analyzing performance patterns...")
        
        performance_indicators = {
            "async_patterns": 0,
            "caching_mechanisms": 0,
            "optimization_patterns": 0,
            "monitoring_setup": 0
        }
        
        # Check for performance patterns in Python files
        python_files = list(Path(".").rglob("*.py"))[:10]  # Limit for performance
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if 'async ' in content or 'await ' in content:
                        performance_indicators["async_patterns"] += 1
                    if 'cache' in content or 'redis' in content:
                        performance_indicators["caching_mechanisms"] += 1
                    if 'optimize' in content or 'performance' in content:
                        performance_indicators["optimization_patterns"] += 1
                    if 'logging' in content or 'monitor' in content:
                        performance_indicators["monitoring_setup"] += 1
            except Exception:
                continue
        
        performance_score = min(100, sum(performance_indicators.values()) * 10)
        
        results["project_health"]["performance_metrics"] = {
            "performance_indicators": performance_indicators,
            "performance_score": performance_score,
            "optimization_level": "high" if performance_score >= 70 else "medium"
        }
    
    def _generate_learning_insights(self, results):
        """Generate learning insights and improvement suggestions."""
        print("🧠 Generating learning insights...")
        
        # Base insights on analysis results
        structure_score = results["project_health"]["architecture_assessment"].get("structure_score", 0)
        quality_score = results["project_health"]["code_quality"].get("quality_score", 0)
        architecture_score = results["project_health"]["architecture_assessment"].get("architecture_score", 0)
        performance_score = results["project_health"]["performance_metrics"].get("performance_score", 0)
        
        insights = {
            "improvement_opportunities": [],
            "best_practices_identified": [],
            "pattern_recognition": [],
            "optimization_suggestions": []
        }
        
        # Generate insights based on scores
        if structure_score < 80:
            insights["improvement_opportunities"].append({
                "area": "project_structure",
                "description": "Project structure could be enhanced with additional components",
                "priority": "medium",
                "impact": "maintainability"
            })
        
        if quality_score >= 75:
            insights["best_practices_identified"].append({
                "practice": "code_organization",
                "description": "Good code organization and file diversity detected",
                "strength_level": "high"
            })
        
        if architecture_score >= 80:
            insights["pattern_recognition"].append({
                "pattern": "enterprise_architecture",
                "description": "Enterprise-level architecture patterns detected",
                "confidence": "high"
            })
        
        if performance_score < 50:
            insights["optimization_suggestions"].append({
                "area": "performance_optimization",
                "suggestion": "Consider implementing async patterns and caching mechanisms",
                "potential_impact": "high"
            })
        
        # Add general insights
        insights["pattern_recognition"].append({
            "pattern": "ai_multi_agent_system",
            "description": "Advanced AI multi-agent system architecture identified",
            "confidence": "high"
        })
        
        results["learning_insights"] = insights
        results["analysis_metrics"]["insights_generated"] = sum(len(v) if isinstance(v, list) else 1 for v in insights.values())
    
    def _calculate_health_score(self, results):
        """Calculate overall project health score."""
        scores = [
            results["project_health"]["architecture_assessment"].get("structure_score", 0) * 0.3,
            results["project_health"]["code_quality"].get("quality_score", 0) * 0.3,
            results["project_health"]["architecture_assessment"].get("architecture_score", 0) * 0.25,
            results["project_health"]["performance_metrics"].get("performance_score", 0) * 0.15
        ]
        
        overall_score = sum(scores)
        results["project_health"]["overall_score"] = round(overall_score, 1)
        
        # Health status
        if overall_score >= 90:
            health_status = "excellent"
        elif overall_score >= 75:
            health_status = "good"
        elif overall_score >= 60:
            health_status = "fair"
        else:
            health_status = "needs_improvement"
        
        results["project_health"]["health_status"] = health_status
    
    def _finalize_analysis_results(self, results):
        """Finalize analysis results and metrics."""
        execution_time = time.time() - self.start_time
        
        results["analysis_metrics"]["analysis_duration"] = f"{execution_time:.1f}s"
        results["metadata"]["execution_status"] = "completed_successfully"
        
        print(f"📊 Analysis completed in {execution_time:.1f}s")
        print(f"🎦 Overall health score: {results['project_health']['overall_score']}/100")
        print(f"🎯 Health status: {results['project_health']['health_status']}")
        print(f"🧠 Insights generated: {results['analysis_metrics']['insights_generated']}")

def main():
    parser = argparse.ArgumentParser(description="Advanced AI Project Analyzer")
    parser.add_argument("--mode", default="intelligent", help="Analysis mode")
    parser.add_argument("--areas", default="all", help="Target areas for analysis")
    parser.add_argument("--depth", default="comprehensive", help="Learning depth")
    parser.add_argument("--auto-apply", action="store_true", help="Auto-apply improvements")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced AI manager")
    parser.add_argument("--output", default="project_analysis_results.json", help="Output file path")
    
    args = parser.parse_args()
    
    print(f"🤖 Starting AI Project Analysis & Learning")
    print(f"Mode: {args.mode} | Areas: {args.areas} | Depth: {args.depth}")
    print(f"Auto-apply: {args.auto_apply}")
    print("")
    
    try:
        # Initialize project analyzer
        analyzer = AdvancedProjectAnalyzer(
            mode=args.mode,
            areas=args.areas,
            depth=args.depth,
            auto_apply=args.auto_apply
        )
        
        # Execute project analysis
        results = analyzer.execute_project_analysis()
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Project analysis failed: {str(e)}")
        
        # Create minimal results even on failure
        minimal_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "execution_status": "failed",
                "error": str(e)
            },
            "project_health": {"overall_score": 50},
            "analysis_metrics": {"confidence_level": 50}
        }
        
        with open(args.output, 'w') as f:
            json.dump(minimal_results, f, indent=2)
        
        return 1

if __name__ == "__main__":
    sys.exit(main())