#!/usr/bin/env python3
"""
AI Project Auditor Script
Comprehensive project audit and analysis with Advanced API Manager Integration
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

class AIProjectAuditor:
    """AI Project Auditor with Advanced API Manager"""
    
    def __init__(self, use_advanced_manager: bool = True):
        """Initialize the auditor"""
        self.use_advanced_manager = use_advanced_manager
        self.integration = get_integration() if use_advanced_manager else None
        self.results = {
            "project_audit": {},
            "ai_insights": {},
            "recommendations": [],
            "documentation_status": {},
            "code_quality_metrics": {},
            "security_analysis": {},
            "performance_analysis": {},
            "integration_stats": {}
        }
    
    async def audit_project(
        self, 
        mode: str, 
        components: str, 
        level: str, 
        formats: str
    ) -> Dict[str, Any]:
        """Perform comprehensive project audit"""
        logger.info("🔍 Starting Comprehensive Project Audit")
        logger.info(f"Mode: {mode} | Components: {components} | Strategy: {level}")
        logger.info(f"Output Formats: {formats}")
        
        try:
            # Perform project structure analysis
            structure_analysis = await self._analyze_project_structure()
            
            # Perform code quality analysis
            code_quality = await self._analyze_code_quality()
            
            # Perform security analysis
            security_analysis = await self._analyze_security()
            
            # Perform performance analysis
            performance_analysis = await self._analyze_performance()
            
            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(
                structure_analysis, code_quality, security_analysis, performance_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                structure_analysis, code_quality, security_analysis, performance_analysis
            )
            
            # Generate documentation status
            doc_status = await self._analyze_documentation_status()
            
            # Compile results
            self.results["project_audit"] = {
                "structure_analysis": structure_analysis,
                "code_quality": code_quality,
                "security_analysis": security_analysis,
                "performance_analysis": performance_analysis,
                "audit_mode": mode,
                "target_components": components,
                "documentation_level": level,
                "output_formats": formats
            }
            
            self.results["ai_insights"] = ai_insights
            self.results["recommendations"] = recommendations
            self.results["documentation_status"] = doc_status
            self.results["code_quality_metrics"] = code_quality
            self.results["security_analysis"] = security_analysis
            self.results["performance_analysis"] = performance_analysis
            
            # Add integration statistics
            if self.use_advanced_manager and self.integration:
                self.results["integration_stats"] = self.integration.get_integration_stats()
            
            logger.info("✅ Comprehensive Project Audit completed successfully")
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Error during project audit: {e}")
            return self._generate_error_results(str(e))
    
    async def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure"""
        logger.info("📁 Analyzing project structure...")
        
        structure = {
            "total_files": 0,
            "file_types": {},
            "directories": [],
            "main_components": [],
            "configuration_files": [],
            "documentation_files": [],
            "test_files": [],
            "workflow_files": []
        }
        
        try:
            # Analyze project root
            project_root = Path(".")
            
            for item in project_root.rglob("*"):
                if item.is_file():
                    structure["total_files"] += 1
                    
                    # Categorize by file type
                    ext = item.suffix.lower()
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                    
                    # Categorize by purpose
                    if item.name in ["requirements.txt", "pyproject.toml", "setup.py", "package.json"]:
                        structure["configuration_files"].append(str(item))
                    elif item.suffix in [".md", ".rst", ".txt"] and "readme" in item.name.lower():
                        structure["documentation_files"].append(str(item))
                    elif "test" in item.name.lower() or item.parent.name == "tests":
                        structure["test_files"].append(str(item))
                    elif item.suffix == ".yml" and ".github" in str(item):
                        structure["workflow_files"].append(str(item))
                
                elif item.is_dir() and not item.name.startswith("."):
                    structure["directories"].append(str(item))
            
            # Identify main components
            structure["main_components"] = [
                "Python scripts", "GitHub Actions workflows", 
                "Configuration files", "Documentation files"
            ]
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            structure["error"] = str(e)
        
        return structure
    
    async def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality"""
        logger.info("🔍 Analyzing code quality...")
        
        quality_metrics = {
            "python_files": 0,
            "total_lines": 0,
            "average_file_size": 0,
            "complexity_score": 0,
            "documentation_coverage": 0,
            "test_coverage": 0,
            "issues_found": []
        }
        
        try:
            # Count Python files and lines
            python_files = list(Path(".").rglob("*.py"))
            quality_metrics["python_files"] = len(python_files)
            
            total_lines = 0
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except Exception:
                    continue
            
            quality_metrics["total_lines"] = total_lines
            quality_metrics["average_file_size"] = total_lines / len(python_files) if python_files else 0
            
            # Basic complexity analysis
            quality_metrics["complexity_score"] = min(100, max(0, 100 - (total_lines / 1000)))
            
            # Documentation coverage (basic)
            doc_files = len(list(Path(".").rglob("*.md")))
            quality_metrics["documentation_coverage"] = min(100, (doc_files * 10))
            
            # Test coverage (basic)
            test_files = len([f for f in python_files if "test" in f.name.lower()])
            quality_metrics["test_coverage"] = min(100, (test_files * 5))
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            quality_metrics["error"] = str(e)
        
        return quality_metrics
    
    async def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security aspects"""
        logger.info("🔒 Analyzing security...")
        
        security_analysis = {
            "api_keys_found": 0,
            "secrets_detected": 0,
            "vulnerable_dependencies": 0,
            "security_issues": [],
            "recommendations": []
        }
        
        try:
            # Check for potential API keys in code
            for py_file in Path(".").rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "api_key" in content.lower() or "secret" in content.lower():
                            security_analysis["api_keys_found"] += 1
                            security_analysis["security_issues"].append(f"Potential API key in {py_file}")
                except Exception:
                    continue
            
            # Check for hardcoded secrets
            for py_file in Path(".").rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "password" in content.lower() or "token" in content.lower():
                            security_analysis["secrets_detected"] += 1
                            security_analysis["security_issues"].append(f"Potential secret in {py_file}")
                except Exception:
                    continue
            
            # Generate security recommendations
            if security_analysis["api_keys_found"] > 0:
                security_analysis["recommendations"].append("Use environment variables for API keys")
            if security_analysis["secrets_detected"] > 0:
                security_analysis["recommendations"].append("Use secure secret management")
            
        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            security_analysis["error"] = str(e)
        
        return security_analysis
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance aspects"""
        logger.info("⚡ Analyzing performance...")
        
        performance_analysis = {
            "file_count": 0,
            "total_size_mb": 0,
            "largest_files": [],
            "performance_issues": [],
            "recommendations": []
        }
        
        try:
            # Analyze file sizes
            total_size = 0
            file_sizes = []
            
            for item in Path(".").rglob("*"):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        total_size += size
                        file_sizes.append((str(item), size))
                    except Exception:
                        continue
            
            performance_analysis["file_count"] = len(file_sizes)
            performance_analysis["total_size_mb"] = total_size / (1024 * 1024)
            
            # Find largest files
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            performance_analysis["largest_files"] = file_sizes[:10]
            
            # Generate performance recommendations
            if performance_analysis["total_size_mb"] > 100:
                performance_analysis["recommendations"].append("Consider reducing repository size")
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            performance_analysis["error"] = str(e)
        
        return performance_analysis
    
    async def _generate_ai_insights(
        self, 
        structure: Dict[str, Any], 
        quality: Dict[str, Any], 
        security: Dict[str, Any], 
        performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered insights"""
        logger.info("🤖 Generating AI insights...")
        
        if not self.use_advanced_manager or not self.integration:
            return {"ai_generated": False, "message": "AI integration not available"}
        
        try:
            # Create comprehensive prompt for AI analysis
            prompt = f"""
            Analyze this project audit data and provide comprehensive insights:
            
            PROJECT STRUCTURE:
            - Total files: {structure.get('total_files', 0)}
            - File types: {structure.get('file_types', {})}
            - Main components: {structure.get('main_components', [])}
            
            CODE QUALITY:
            - Python files: {quality.get('python_files', 0)}
            - Total lines: {quality.get('total_lines', 0)}
            - Complexity score: {quality.get('complexity_score', 0)}
            - Documentation coverage: {quality.get('documentation_coverage', 0)}%
            
            SECURITY:
            - API keys found: {security.get('api_keys_found', 0)}
            - Secrets detected: {security.get('secrets_detected', 0)}
            - Security issues: {len(security.get('security_issues', []))}
            
            PERFORMANCE:
            - File count: {performance.get('file_count', 0)}
            - Total size: {performance.get('total_size_mb', 0):.2f} MB
            
            Provide:
            1. Overall project health assessment
            2. Key strengths and weaknesses
            3. Priority recommendations
            4. Risk assessment
            5. Improvement roadmap
            """
            
            ai_response = await self.integration.generate_with_fallback(
                prompt=prompt,
                system_prompt="You are an expert software project auditor. Provide detailed, actionable insights.",
                strategy="intelligent"
            )
            
            if ai_response.get("success", False):
                return {
                    "ai_generated": True,
                    "content": ai_response.get("content", ""),
                    "provider": ai_response.get("provider_name", "Unknown"),
                    "response_time": ai_response.get("response_time", 0)
                }
            else:
                return {
                    "ai_generated": False,
                    "error": ai_response.get("error", "Unknown error"),
                    "fallback_insights": "Project audit completed with basic analysis"
                }
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                "ai_generated": False,
                "error": str(e),
                "fallback_insights": "Project audit completed with basic analysis"
            }
    
    async def _generate_recommendations(
        self, 
        structure: Dict[str, Any], 
        quality: Dict[str, Any], 
        security: Dict[str, Any], 
        performance: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        # Structure recommendations
        if structure.get("total_files", 0) > 1000:
            recommendations.append("Consider organizing files into better directory structure")
        
        # Quality recommendations
        if quality.get("documentation_coverage", 0) < 50:
            recommendations.append("Improve documentation coverage")
        if quality.get("test_coverage", 0) < 30:
            recommendations.append("Increase test coverage")
        
        # Security recommendations
        if security.get("api_keys_found", 0) > 0:
            recommendations.append("Move API keys to environment variables")
        if security.get("secrets_detected", 0) > 0:
            recommendations.append("Implement secure secret management")
        
        # Performance recommendations
        if performance.get("total_size_mb", 0) > 100:
            recommendations.append("Optimize repository size")
        
        return recommendations
    
    async def _analyze_documentation_status(self) -> Dict[str, Any]:
        """Analyze documentation status"""
        logger.info("📚 Analyzing documentation status...")
        
        doc_status = {
            "readme_files": 0,
            "doc_files": 0,
            "api_docs": 0,
            "tutorials": 0,
            "coverage": 0
        }
        
        try:
            # Count documentation files
            doc_files = list(Path(".").rglob("*.md"))
            doc_status["doc_files"] = len(doc_files)
            
            readme_files = [f for f in doc_files if "readme" in f.name.lower()]
            doc_status["readme_files"] = len(readme_files)
            
            # Calculate coverage
            total_files = len(list(Path(".").rglob("*.py")))
            doc_status["coverage"] = min(100, (len(doc_files) * 10))
            
        except Exception as e:
            logger.error(f"Error analyzing documentation: {e}")
            doc_status["error"] = str(e)
        
        return doc_status
    
    def _generate_error_results(self, error: str) -> Dict[str, Any]:
        """Generate error results"""
        return {
            "project_audit": {"error": error},
            "ai_insights": {"error": error},
            "recommendations": ["Fix the error and retry"],
            "documentation_status": {"error": error},
            "code_quality_metrics": {"error": error},
            "security_analysis": {"error": error},
            "performance_analysis": {"error": error},
            "integration_stats": {"error": error}
        }

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Project Auditor")
    parser.add_argument("--mode", default="comprehensive", help="Audit mode")
    parser.add_argument("--components", default="all", help="Target components")
    parser.add_argument("--level", default="detailed", help="Documentation level")
    parser.add_argument("--formats", default="json", help="Output formats")
    parser.add_argument("--use-advanced-manager", action="store_true", help="Use advanced API manager")
    parser.add_argument("--output", default="project_audit_results.json", help="Output file")
    
    # Add common optional arguments
    parser.add_argument("--quality-results", default="quality_results/", help="Quality results directory")
    parser.add_argument("--performance-results", default="performance_results/", help="Performance results directory")
    parser.add_argument("--all-results", default="all_results/", help="All results directory")
    parser.add_argument("--enhancement-results", default="enhancement_results/", help="Enhancement results directory")
    parser.add_argument("--validation-results", default="validation_results/", help="Validation results directory")
    
    args = parser.parse_args()
    
    # Create auditor
    auditor = AIProjectAuditor(use_advanced_manager=args.use_advanced_manager)
    
    # Perform audit
    results = await auditor.audit_project(
        mode=args.mode,
        components=args.components,
        level=args.level,
        formats=args.formats
    )
    
    # Save results
    if args.use_advanced_manager and auditor.integration:
        auditor.integration.save_results(results, args.output)
    else:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    logger.info(f"✅ Project audit results saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())