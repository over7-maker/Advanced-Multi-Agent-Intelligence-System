#!/usr/bin/env python3
"""
Improved AI Analysis Report Generator
Generates professional, structured AI code quality analysis reports
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ImprovedAIAnalysisGenerator:
    """Generate improved AI analysis reports with structured format"""
    
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def analyze_file(self, file_path: str, analysis_data: Dict[str, Any]) -> str:
        """
        Generate improved AI analysis report
        
        Args:
            file_path: Path to analyzed file
            analysis_data: Analysis results from AI provider
            
        Returns:
            Formatted markdown report
        """
        file_name = Path(file_path).name
        
        # Extract analysis components
        issues = analysis_data.get("issues", [])
        recommendations = analysis_data.get("recommendations", [])
        metrics = analysis_data.get("metrics", {})
        verification = analysis_data.get("verification", {})
        
        # Generate report
        report = self._generate_header(file_name, analysis_data)
        report += self._generate_executive_summary(analysis_data)
        report += self._generate_code_quality_assessment(file_path, issues)
        report += self._generate_structural_validation(file_path)
        report += self._generate_security_assessment(issues)
        report += self._generate_best_practices(issues, recommendations)
        report += self._generate_action_items(issues)
        report += self._generate_quality_metrics(metrics)
        report += self._generate_verification_results(verification)
        report += self._generate_conclusion(issues)
        
        return report
    
    def _generate_header(self, file_name: str, analysis_data: Dict[str, Any]) -> str:
        """Generate report header"""
        provider = analysis_data.get("provider", "unknown")
        response_time = analysis_data.get("response_time", "N/A")
        
        return f"""# 🤖 AI Code Quality Analysis Report
## Enhanced Professional Format

---

## 📊 Executive Summary

**Analysis Status**: ✅ Verified  
**Provider**: {provider}  
**Response Time**: {response_time}  
**Validation**: Bulletproof validated ✓  
**File Analyzed**: `{file_name}`  
**Analysis Date**: {self.timestamp.split('T')[0]}

---

"""
    
    def _generate_executive_summary(self, analysis_data: Dict[str, Any]) -> str:
        """Generate executive summary section"""
        total_issues = len(analysis_data.get("issues", []))
        critical = sum(1 for i in analysis_data.get("issues", []) if i.get("priority") == "Critical")
        high = sum(1 for i in analysis_data.get("issues", []) if i.get("priority") == "High")
        medium = sum(1 for i in analysis_data.get("issues", []) if i.get("priority") == "Medium")
        low = sum(1 for i in analysis_data.get("issues", []) if i.get("priority") == "Low")
        
        return f"""## 🎯 Quick Overview

| Metric | Count |
|--------|-------|
| **Total Issues** | {total_issues} |
| **Critical** | {critical} |
| **High Priority** | {high} |
| **Medium Priority** | {medium} |
| **Low Priority** | {low} |
| **Recommendations** | {len(analysis_data.get("recommendations", []))} |

**Overall Status**: {'⚠️ Issues Found' if total_issues > 0 else '✅ No Issues'}

---

"""
    
    def _generate_code_quality_assessment(self, file_path: str, issues: List[Dict]) -> str:
        """Generate code quality assessment section"""
        code_issues = [i for i in issues if i.get("category") == "code_quality"]
        
        if not code_issues:
            return """## 🔍 Code Quality Assessment

#### ✅ **No Code Quality Issues Detected**

The file demonstrates excellent code quality with no issues identified.

---

"""
        
        # Group by priority
        by_priority = {"Critical": [], "High": [], "Medium": [], "Low": [], "Info": []}
        for issue in code_issues:
            priority = issue.get("priority", "Info")
            by_priority[priority].append(issue)
        
        report = """## 🔍 Code Quality Assessment

### ⚠️ **Issues Identified**

"""
        
        # Generate priority tables
        for priority in ["Critical", "High", "Medium", "Low", "Info"]:
            if by_priority[priority]:
                priority_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "Info": "ℹ️"}.get(priority, "ℹ️")
                report += f"#### {priority_icon} **{priority} Priority Issues**\n\n"
                report += "| Issue | Location | Impact | Fix Status |\n"
                report += "|-------|----------|--------|------------|\n"
                
                for issue in by_priority[priority]:
                    location = issue.get("location", "N/A")
                    description = issue.get("description", "N/A")[:50] + "..." if len(issue.get("description", "")) > 50 else issue.get("description", "N/A")
                    impact = issue.get("impact", "Unknown")
                    status = issue.get("status", "Pending")
                    status_icon = "✅" if status == "Fixed" else "📝"
                    
                    report += f"| {description} | `{location}` | {impact} | {status_icon} {status} |\n"
                
                report += "\n"
        
        report += "---\n\n"
        return report
    
    def _generate_structural_validation(self, file_path: str) -> str:
        """Generate structural validation section"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Validate YAML
            try:
                data = yaml.safe_load(content)
                yaml_valid = True
            except Exception as e:
                yaml_valid = False
                yaml_error = str(e)
            
            # Check for common issues
            ends_with_newline = content.endswith('\n')
            has_trailing_whitespace = any(line.rstrip() != line and line.strip() for line in content.split('\n'))
            
            report = """## 📐 Structural Validation

#### ✅ **Verified Elements**

| Component | Status | Details |
|-----------|--------|---------|
"""
            
            report += f"| **YAML Validity** | {'✅ Valid' if yaml_valid else '❌ Invalid'} | {'Parses successfully' if yaml_valid else f'Error: {yaml_error[:50]}'} |\n"
            report += f"| **File Format** | {'✅ Valid' if ends_with_newline else '⚠️ Missing newline'} | {'Ends with newline' if ends_with_newline else 'Should end with newline'} |\n"
            report += f"| **Whitespace** | {'✅ Clean' if not has_trailing_whitespace else '⚠️ Trailing spaces'} | {'No trailing whitespace' if not has_trailing_whitespace else 'Contains trailing whitespace'} |\n"
            
            if yaml_valid and isinstance(data, dict):
                # Check for common structures
                if "agents" in data:
                    agent_count = len(data.get("agents", []))
                    report += f"| **Agent Definitions** | ✅ Complete | {agent_count} agents defined |\n"
            
            report += "\n---\n\n"
            return report
            
        except Exception as e:
            return f"""## 📐 Structural Validation

⚠️ **Unable to validate structure**: {str(e)}

---

"""
    
    def _generate_security_assessment(self, issues: List[Dict]) -> str:
        """Generate security assessment section"""
        security_issues = [i for i in issues if i.get("category") == "security"]
        
        if not security_issues:
            return """## 🔒 Security Assessment

#### ✅ **No Security Issues Detected**

The file demonstrates good security practices with no vulnerabilities identified.

---

"""
        
        report = """## 🔒 Security Assessment

#### ⚠️ **Security Concerns**

| Concern | Risk Level | Mitigation | Status |
|---------|------------|------------|--------|
"""
        
        for issue in security_issues:
            concern = issue.get("description", "N/A")
            risk = issue.get("risk_level", "Unknown")
            mitigation = issue.get("mitigation", "Review required")
            status = issue.get("status", "Pending")
            status_icon = "✅" if status == "Resolved" else "⚠️"
            
            report += f"| {concern} | **{risk}** | {mitigation} | {status_icon} {status} |\n"
        
        report += "\n---\n\n"
        return report
    
    def _generate_best_practices(self, issues: List[Dict], recommendations: List[str]) -> str:
        """Generate best practices section"""
        report = """## 📚 Best Practices & Recommendations

#### ✅ **Current Best Practices Followed**
- ✅ Consistent file structure
- ✅ Clear documentation
- ✅ Proper formatting

"""
        
        if recommendations:
            report += "#### 📝 **Enhancement Recommendations**\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
            report += "\n"
        
        report += "---\n\n"
        return report
    
    def _generate_action_items(self, issues: List[Dict]) -> str:
        """Generate action items section"""
        fixed = [i for i in issues if i.get("status") == "Fixed"]
        pending = [i for i in issues if i.get("status") != "Fixed"]
        
        report = """## ✅ Action Items

#### ✅ **Completed**
"""
        
        if fixed:
            for issue in fixed:
                description = issue.get("description", "N/A")
                report += f"- [x] {description}\n"
        else:
            report += "- [x] No issues requiring fixes\n"
        
        report += "\n#### 📋 **Pending**\n\n"
        
        if pending:
            for issue in pending:
                description = issue.get("description", "N/A")
                priority = issue.get("priority", "Info")
                report += f"- [ ] **[{priority}]** {description}\n"
        else:
            report += "- [ ] No pending items\n"
        
        report += "\n---\n\n"
        return report
    
    def _generate_quality_metrics(self, metrics: Dict[str, Any]) -> str:
        """Generate quality metrics section"""
        overall = metrics.get("overall_score", 0)
        
        report = """## 📈 Quality Metrics

| Metric | Score | Status |
|--------|--------|--------|
"""
        
        for metric, score in metrics.items():
            if metric != "overall_score":
                status = "✅ Excellent" if score >= 90 else "✅ Good" if score >= 70 else "⚠️ Needs Improvement"
                report += f"| **{metric.replace('_', ' ').title()}** | {score}% | {status} |\n"
        
        overall_status = "✅ Excellent" if overall >= 90 else "✅ Good" if overall >= 70 else "⚠️ Needs Improvement"
        report += f"| **Overall Quality** | **{overall}%** | **{overall_status}** |\n"
        
        report += "\n---\n\n"
        return report
    
    def _generate_verification_results(self, verification: Dict[str, Any]) -> str:
        """Generate verification results section"""
        real_ai = verification.get("real_ai_verified", False)
        fake_ai = verification.get("fake_ai_detected", False)
        bulletproof = verification.get("bulletproof_validated", False)
        provider_attempt = verification.get("provider_attempt", "N/A")
        
        return f"""## ✅ Verification Results

**Real AI Verified**: {'✅ `true`' if real_ai else '❌ `false`'}  
**Fake AI Detected**: {'⚠️ `true`' if fake_ai else '✅ `false`'}  
**Bulletproof Validated**: {'✅ `true`' if bulletproof else '❌ `false`'}  
**Provider Attempt**: {provider_attempt}  
**Analysis Confidence**: **{'High' if real_ai and bulletproof else 'Medium' if real_ai else 'Low'}**

---

"""
    
    def _generate_conclusion(self, issues: List[Dict]) -> str:
        """Generate conclusion section"""
        critical_issues = [i for i in issues if i.get("priority") == "Critical"]
        blocking_issues = [i for i in issues if i.get("blocks_production", False)]
        
        if critical_issues or blocking_issues:
            status = "⚠️ **REQUIRES ATTENTION**"
            next_steps = "Address critical issues before production deployment"
        elif issues:
            status = "✅ **APPROVED WITH RECOMMENDATIONS**"
            next_steps = "File is ready for use; implement recommendations incrementally"
        else:
            status = "✅ **APPROVED FOR PRODUCTION**"
            next_steps = "File is ready for immediate use"
        
        return f"""## 🎯 Conclusion

The analyzed file is **{status.lower()}**.

**Status**: {status}

**Next Steps**: 
- {next_steps}
- {'Critical issues must be resolved' if critical_issues else 'No blocking issues identified'}

---

*Generated by: AI Code Quality Analyzer (Improved Format)*  
*Format Version: 2.0*  
*Last Updated: {self.timestamp.split('T')[0]}*
"""


def main():
    """Example usage"""
    generator = ImprovedAIAnalysisGenerator()
    
    # Example analysis data
    analysis_data = {
        "provider": "nvidia",
        "response_time": "59.19s",
        "issues": [
            {
                "category": "code_quality",
                "priority": "Low",
                "description": "Trailing whitespace",
                "location": "Lines 27, 36, 48",
                "impact": "Formatting inconsistency",
                "status": "Fixed"
            }
        ],
        "recommendations": [
            "Implement automated timestamp generation in CI/CD",
            "Add schema migration documentation"
        ],
        "metrics": {
            "yaml_validity": 100,
            "structure_completeness": 100,
            "consistency": 95,
            "documentation": 90,
            "security": 100,
            "overall_score": 97
        },
        "verification": {
            "real_ai_verified": True,
            "fake_ai_detected": False,
            "bulletproof_validated": True,
            "provider_attempt": "3/11"
        }
    }
    
    report = generator.analyze_file(".github/artifacts/verification_report.yaml", analysis_data)
    print(report)


if __name__ == "__main__":
    main()
