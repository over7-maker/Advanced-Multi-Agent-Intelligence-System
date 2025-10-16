#!/usr/bin/env python3
"""
Universal PR Commenter - Standardized AI workflow comment posting
Creates consistent, rich PR comments for all AI workflows
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class UniversalPRCommenter:
    """Universal PR commenter for all AI workflows"""
    
    def __init__(self):
        self.artifacts_dir = Path("artifacts")
        self.comment_templates = {
            "dependency_analysis": {
                "title": "🤖 AI Dependency & Code-Fix Analysis",
                "icon": "🔧",
                "description": "Intelligent dependency resolution and code enhancement"
            },
            "security_audit": {
                "title": "🛡️ AI Security & Threat Intelligence",
                "icon": "🔒",
                "description": "Comprehensive security vulnerability scanning and threat analysis"
            },
            "build_analysis": {
                "title": "🚀 AI Build & Deploy Insights",
                "icon": "🏗️",
                "description": "Intelligent build optimization and deployment analysis"
            },
            "code_quality": {
                "title": "📊 AI Code Quality & Performance",
                "icon": "⚡",
                "description": "Advanced code quality analysis and performance optimization"
            },
            "project_audit": {
                "title": "📚 AI Project Audit & Documentation",
                "icon": "📖",
                "description": "Comprehensive project analysis and documentation generation"
            },
            "issue_responder": {
                "title": "🤖 AI Issue Auto-Responder",
                "icon": "💬",
                "description": "Intelligent issue analysis and automated response generation"
            },
            "self_improver": {
                "title": "🧠 AI Project Self-Improver",
                "icon": "🔄",
                "description": "Continuous learning and project enhancement system"
            },
            "parallel_analysis": {
                "title": "⚡ AI Parallel Analysis",
                "icon": "🚀",
                "description": "Multi-provider parallel analysis for maximum reliability"
            },
            "master_integration": {
                "title": "🎯 AI Master Integration System",
                "icon": "🌟",
                "description": "Comprehensive AI system orchestration and analysis"
            }
        }
    
    def load_ai_results(self, workflow_type: str) -> Dict[str, Any]:
        """Load AI analysis results for a specific workflow type"""
        result_files = {
            "dependency_analysis": "dependency_resolution.json",
            "security_audit": "security_audit_report.json",
            "build_analysis": "build_analysis_results.json",
            "code_quality": "code_enhancement_results.json",
            "project_audit": "project_audit_results.json",
            "issue_responder": "issue_response_results.json",
            "self_improver": "self_improvement_results.json",
            "parallel_analysis": "parallel_provider_report.json",
            "master_integration": "master_ai_summary.json"
        }
        
        result_file = result_files.get(workflow_type)
        if not result_file:
            return {"error": f"Unknown workflow type: {workflow_type}"}
        
        result_path = self.artifacts_dir / result_file
        if not result_path.exists():
            return {"error": f"Result file not found: {result_file}"}
        
        try:
            with open(result_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to load results: {e}"}
    
    def extract_ai_metadata(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract AI metadata from results"""
        metadata = {
            "success": False,
            "provider_used": "Unknown",
            "response_time": 0,
            "confidence": 0,
            "analysis_type": "Unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        # Try different result structures
        if "metadata" in results:
            meta = results["metadata"]
            metadata.update({
                "success": meta.get("ai_success", meta.get("success", False)),
                "provider_used": meta.get("provider_used", "Unknown"),
                "response_time": meta.get("response_time", 0),
                "timestamp": meta.get("timestamp", metadata["timestamp"])
            })
        
        if "ai_analysis" in results:
            analysis = results["ai_analysis"]
            if isinstance(analysis, dict):
                metadata["confidence"] = analysis.get("confidence", 0)
                metadata["analysis_type"] = analysis.get("type", "analysis")
        
        if "summary" in results:
            summary = results["summary"]
            metadata["success"] = summary.get("ai_analysis_success", summary.get("success", False))
        
        return metadata
    
    def extract_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from results"""
        recommendations = []
        
        # Try different recommendation structures
        if "recommendations" in results:
            recs = results["recommendations"]
            if isinstance(recs, dict):
                # Handle structured recommendations
                for key, value in recs.items():
                    if isinstance(value, list):
                        recommendations.extend(value[:3])  # Limit to 3 per category
                    elif isinstance(value, str):
                        recommendations.append(value)
            elif isinstance(recs, list):
                recommendations.extend(recs[:5])  # Limit to 5 total
        
        if "ai_analysis" in results:
            analysis = results["ai_analysis"]
            if isinstance(analysis, dict):
                # Extract from analysis
                for key in ["immediate_actions", "long_term_improvements", "workflow_changes"]:
                    if key in analysis and isinstance(analysis[key], list):
                        recommendations.extend(analysis[key][:2])  # Limit to 2 per category
        
        if "fixes_applied" in results:
            fixes = results["fixes_applied"]
            if isinstance(fixes, dict):
                applied = fixes.get("applied_fixes", [])
                if isinstance(applied, list):
                    recommendations.extend([f"Applied: {fix.get('description', 'Fix')}" for fix in applied[:3]])
        
        # Remove duplicates and limit total
        unique_recs = list(dict.fromkeys(recommendations))[:8]
        return unique_recs
    
    def extract_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from results"""
        metrics = {
            "issues_found": 0,
            "fixes_applied": 0,
            "success_rate": 0,
            "total_time": 0
        }
        
        # Try different metric structures
        if "issues_detected" in results:
            issues = results["issues_detected"]
            if isinstance(issues, dict):
                metrics["issues_found"] = issues.get("missing_modules", [])
                if isinstance(metrics["issues_found"], list):
                    metrics["issues_found"] = len(metrics["issues_found"])
        
        if "fixes_applied" in results:
            fixes = results["fixes_applied"]
            if isinstance(fixes, dict):
                metrics["fixes_applied"] = fixes.get("total_applied", 0)
        
        if "summary" in results:
            summary = results["summary"]
            metrics["success_rate"] = summary.get("overall_success_rate", 0)
            metrics["total_time"] = summary.get("total_time", 0)
        
        return metrics
    
    def generate_comment(self, workflow_type: str, results: Dict[str, Any]) -> str:
        """Generate a rich PR comment for the workflow"""
        template = self.comment_templates.get(workflow_type, {
            "title": "🤖 AI Analysis",
            "icon": "🔍",
            "description": "AI-powered analysis and recommendations"
        })
        
        metadata = self.extract_ai_metadata(results)
        recommendations = self.extract_recommendations(results)
        metrics = self.extract_metrics(results)
        
        # Build comment
        comment = f"""## {template['title']}

**Status:** {'✅ Completed' if metadata['success'] else '❌ Failed'}
**Provider:** {metadata['provider_used']}
**Response Time:** {metadata['response_time']:.2f}s
**Confidence:** {metadata['confidence']:.1%}

---

### 📊 Analysis Summary
{template['description']}

"""
        
        # Add metrics if available
        if metrics['issues_found'] > 0 or metrics['fixes_applied'] > 0:
            comment += f"""**Issues Detected:** {metrics['issues_found']}
**Fixes Applied:** {metrics['fixes_applied']}
**Success Rate:** {metrics['success_rate']:.1f}%

---

"""
        
        # Add recommendations
        if recommendations:
            comment += f"""### 💡 Key Recommendations
{chr(10).join([f"- {rec}" for rec in recommendations[:5]])}

---

"""
        
        # Add specific analysis content if available
        if "ai_analysis" in results:
            analysis = results["ai_analysis"]
            if isinstance(analysis, dict) and "analysis" in analysis:
                analysis_text = analysis["analysis"]
                if len(analysis_text) > 200:
                    analysis_text = analysis_text[:200] + "..."
                comment += f"""### 🔍 Analysis Details
{analysis_text}

---

"""
        
        # Add footer
        comment += f"""### 🚀 AI Capabilities
- **16-Provider Fallback**: Maximum reliability and speed
- **Intelligent Analysis**: Advanced pattern recognition
- **Automated Fixes**: Self-healing system capabilities
- **Continuous Learning**: Improves over time

---

*{template['icon']} Generated by {template['title']} at {metadata['timestamp']}*
*Advanced Multi-Agent Intelligence System v3.0*
"""
        
        return comment
    
    async def post_comment(self, workflow_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Post comment to PR using GitHub API"""
        try:
            comment = self.generate_comment(workflow_type, results)
            
            # For GitHub Actions, we'll return the comment content
            # The actual posting will be done by the workflow
            return {
                "success": True,
                "comment": comment,
                "workflow_type": workflow_type,
                "metadata": self.extract_ai_metadata(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_type": workflow_type
            }

async def main():
    """Main function to run universal PR commenter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal PR Commenter")
    parser.add_argument("--workflow-type", required=True, help="Type of workflow")
    parser.add_argument("--output-file", default="pr_comment.md", help="Output file for comment")
    
    args = parser.parse_args()
    
    print(f"🤖 Universal PR Commenter - {args.workflow_type}")
    print("=" * 60)
    
    commenter = UniversalPRCommenter()
    
    # Load results
    results = commenter.load_ai_results(args.workflow_type)
    
    if "error" in results:
        print(f"❌ Error loading results: {results['error']}")
        return
    
    # Generate comment
    comment_result = await commenter.post_comment(args.workflow_type, results)
    
    if comment_result["success"]:
        # Save comment to file
        with open(args.output_file, 'w') as f:
            f.write(comment_result["comment"])
        
        print(f"✅ Comment generated successfully")
        print(f"📄 Saved to: {args.output_file}")
        print(f"🤖 Provider: {comment_result['metadata']['provider_used']}")
        print(f"⏱️ Response Time: {comment_result['metadata']['response_time']:.2f}s")
    else:
        print(f"❌ Failed to generate comment: {comment_result['error']}")

if __name__ == "__main__":
    asyncio.run(main())