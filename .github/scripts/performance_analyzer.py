#!/usr/bin/env python3
"""
Performance Analyzer Script
Analyzes code performance and optimization opportunities
"""

import os
import json
import re
import ast
from openai import OpenAI
from typing import Dict, List, Any, Optional
from pathlib import Path

class PerformanceAnalyzer:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openrouter_key = os.environ.get('OPENROUTER_API_KEY')
        self.deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
        self.repo_name = os.environ.get('REPO_NAME')
        
        # Initialize AI client
        self.ai_client = None
        if self.openrouter_key:
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key,
            )
        elif self.deepseek_key:
            self.ai_client = OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=self.deepseek_key,
            )
    
    def analyze_performance_patterns(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze code for performance issues"""
        issues = []
        
        # Performance anti-patterns
        performance_patterns = {
            'nested_loops': {
                'patterns': [r'for\s+\w+\s+in\s+.*:\s*\n\s*for\s+\w+\s+in\s+.*:'],
                'description': 'Nested loops can cause O(n²) complexity',
                'severity': 'medium'
            },
            'inefficient_string_concat': {
                'patterns': [r'str\s*\+\s*str', r'\.join\s*\([^)]*\+'],
                'description': 'String concatenation in loops is inefficient',
                'severity': 'low'
            },
            'unnecessary_comprehensions': {
                'patterns': [r'list\(\[.*for.*in.*\]\)', r'dict\(\[.*for.*in.*\]\)'],
                'description': 'Unnecessary list/dict comprehension wrapping',
                'severity': 'low'
            },
            'memory_intensive_operations': {
                'patterns': [r'\.copy\(\)', r'deepcopy\s*\('],
                'description': 'Memory-intensive copy operations',
                'severity': 'medium'
            },
            'inefficient_data_structures': {
                'patterns': [r'list\s*\(\s*set\s*\(', r'sorted\s*\(\s*sorted\s*\('],
                'description': 'Inefficient data structure operations',
                'severity': 'low'
            },
            'blocking_operations': {
                'patterns': [r'requests\.get\s*\(', r'requests\.post\s*\(', r'time\.sleep\s*\('],
                'description': 'Blocking operations that could be async',
                'severity': 'medium'
            },
            'large_file_operations': {
                'patterns': [r'open\s*\([^)]*\)\.read\s*\(\)', r'\.readlines\s*\('],
                'description': 'Reading entire files into memory',
                'severity': 'medium'
            }
        }
        
        for issue_type, issue_info in performance_patterns.items():
            for pattern in issue_info['patterns']:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'type': issue_type,
                        'file': file_path,
                        'line': line_num,
                        'description': issue_info['description'],
                        'severity': issue_info['severity'],
                        'code_snippet': self.get_code_snippet(content, line_num)
                    })
        
        return issues
    
    def analyze_ast_performance(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze AST for performance issues"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for nested loops
                if isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.For) and child != node:
                            issues.append({
                                'type': 'nested_loops_ast',
                                'file': file_path,
                                'line': node.lineno,
                                'description': 'Nested for loops detected in AST',
                                'severity': 'medium',
                                'code_snippet': self.get_code_snippet(content, node.lineno)
                            })
                
                # Check for inefficient comprehensions
                if isinstance(node, ast.ListComp):
                    if len(node.generators) > 1:
                        issues.append({
                            'type': 'complex_comprehension',
                            'file': file_path,
                            'line': node.lineno,
                            'description': 'Complex list comprehension with multiple generators',
                            'severity': 'low',
                            'code_snippet': self.get_code_snippet(content, node.lineno)
                        })
                
                # Check for recursive calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Check if this is a recursive call
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.FunctionDef) and parent.name == node.func.id:
                                issues.append({
                                    'type': 'recursive_call',
                                    'file': file_path,
                                    'line': node.lineno,
                                    'description': 'Recursive function call detected',
                                    'severity': 'medium',
                                    'code_snippet': self.get_code_snippet(content, node.lineno)
                                })
                                break
                
                # Check for global variables in functions
                if isinstance(node, ast.FunctionDef):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Global):
                            issues.append({
                                'type': 'global_variables',
                                'file': file_path,
                                'line': node.lineno,
                                'description': 'Function uses global variables',
                                'severity': 'low',
                                'code_snippet': self.get_code_snippet(content, node.lineno)
                            })
                            break
        
        except SyntaxError:
            # Skip files with syntax errors
            pass
        
        return issues
    
    def get_code_snippet(self, content: str, line_num: int, context: int = 2) -> str:
        """Get code snippet around a specific line"""
        lines = content.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        
        snippet_lines = []
        for i in range(start, end):
            marker = '>>> ' if i == line_num - 1 else '    '
            snippet_lines.append(f"{marker}{i+1}: {lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def analyze_with_ai(self, performance_issues: List[Dict[str, Any]]) -> Optional[str]:
        """Get AI analysis of performance issues"""
        if not self.ai_client or not performance_issues:
            return None
        
        system_prompt = """
You are a performance optimization expert for the AMAS Intelligence System.
Focus on identifying performance bottlenecks and optimization opportunities.

Provide:
1. Performance impact assessment (High/Medium/Low)
2. Optimization recommendations
3. Alternative implementations
4. Best practices for performance
5. Priority order for optimizations

Be specific and actionable with your recommendations.
"""
        
        performance_prompt = f"""
Performance Issues Found:
"""
        
        for issue in performance_issues[:10]:  # Limit to first 10 issues
            performance_prompt += f"\n**{issue.get('type', 'Unknown')}** in {issue.get('file', 'Unknown')}"
            performance_prompt += f"\n- Severity: {issue.get('severity', 'Unknown')}"
            performance_prompt += f"\n- Description: {issue.get('description', 'No description')}"
            if 'code_snippet' in issue:
                performance_prompt += f"\n- Code: {issue['code_snippet'][:200]}..."
        
        performance_prompt += "\n\nPlease analyze these performance issues and provide specific optimization recommendations."
        
        try:
            model = "deepseek/deepseek-chat-v3.1:free" if self.openrouter_key else "deepseek-chat"
            
            extra_headers = {}
            if self.openrouter_key:
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Performance Analysis",
                }
            
            response = self.ai_client.chat.completions.create(
                extra_headers=extra_headers if self.openrouter_key else None,
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": performance_prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error getting AI performance analysis: {e}")
            return None
    
    def generate_performance_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate performance analysis report"""
        report = ["# ⚡ Performance Analysis Report\n"]
        
        # Summary
        total_issues = len(analysis_results.get('performance_issues', []))
        high_severity = len([i for i in analysis_results.get('performance_issues', []) if i.get('severity') == 'high'])
        medium_severity = len([i for i in analysis_results.get('performance_issues', []) if i.get('severity') == 'medium'])
        low_severity = len([i for i in analysis_results.get('performance_issues', []) if i.get('severity') == 'low'])
        
        report.append(f"**Analysis Date**: {analysis_results.get('timestamp', 'Unknown')}")
        report.append(f"**Repository**: {self.repo_name}")
        report.append("")
        
        if total_issues > 0:
            report.append("⚡ **PERFORMANCE ISSUES DETECTED**\n")
            report.append(f"- **{total_issues}** total performance issues")
            report.append(f"- **{high_severity}** high severity")
            report.append(f"- **{medium_severity}** medium severity")
            report.append(f"- **{low_severity}** low severity\n")
        else:
            report.append("✅ **No significant performance issues detected**\n")
        
        # Performance issues by type
        if analysis_results.get('performance_issues'):
            report.append("## 🔍 Performance Issues by Type")
            
            issue_types = {}
            for issue in analysis_results['performance_issues']:
                issue_type = issue.get('type', 'unknown')
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            for issue_type, issues in issue_types.items():
                report.append(f"\n### {issue_type.replace('_', ' ').title()}")
                for issue in issues[:3]:  # Show first 3 of each type
                    report.append(f"- **{issue['description']}** in {issue['file']} (Line {issue['line']})")
                    report.append(f"  - Severity: {issue['severity']}")
                    if 'code_snippet' in issue:
                        report.append(f"  - Code: ```\n{issue['code_snippet']}\n```")
                if len(issues) > 3:
                    report.append(f"  - ... and {len(issues) - 3} more")
        
        # AI Analysis
        if analysis_results.get('ai_analysis'):
            report.append("\n## 🤖 AI Performance Analysis")
            report.append(analysis_results['ai_analysis'])
        
        # Optimization recommendations
        if total_issues > 0:
            report.append("\n## 🛠️ Optimization Recommendations")
            
            if high_severity > 0:
                report.append("- 🚨 **High Priority**: Address high-severity performance issues first")
            if medium_severity > 0:
                report.append("- ⚠️ **Medium Priority**: Review and optimize medium-severity issues")
            if low_severity > 0:
                report.append("- 💡 **Low Priority**: Consider optimizations for low-severity issues")
            
            report.append("- 📊 **Profiling**: Use Python profilers (cProfile, line_profiler) for detailed analysis")
            report.append("- 🧪 **Testing**: Add performance benchmarks and regression tests")
            report.append("- 📈 **Monitoring**: Implement performance monitoring in production")
            report.append("- 🔄 **Iterative**: Optimize incrementally and measure improvements")
        
        return "\n".join(report)
    
    def run(self):
        """Main execution function"""
        print("⚡ Starting performance analysis...")
        
        analysis_results = {
            'timestamp': str(subprocess.run(['date'], capture_output=True, text=True).stdout.strip()),
            'performance_issues': [],
            'ai_analysis': None
        }
        
        # Analyze all Python files
        python_files = list(Path('.').rglob('*.py'))
        print(f"Analyzing {len(python_files)} Python files...")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Pattern-based analysis
                pattern_issues = self.analyze_performance_patterns(content, str(file_path))
                analysis_results['performance_issues'].extend(pattern_issues)
                
                # AST-based analysis
                ast_issues = self.analyze_ast_performance(content, str(file_path))
                analysis_results['performance_issues'].extend(ast_issues)
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        # Get AI analysis
        if analysis_results['performance_issues'] and self.ai_client:
            print("Getting AI performance analysis...")
            analysis_results['ai_analysis'] = self.analyze_with_ai(analysis_results['performance_issues'])
        
        # Generate report
        report = self.generate_performance_report(analysis_results)
        
        # Save report
        with open('performance-analysis-report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("📋 Performance Analysis Report:")
        print(report)
        
        return analysis_results

if __name__ == "__main__":
    import subprocess
    analyzer = PerformanceAnalyzer()
    analyzer.run()