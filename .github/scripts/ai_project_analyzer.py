#!/usr/bin/env python3
"""
AI Project Analyzer - Advanced Multi-Agent Project Analysis System
Part of the AMAS (Advanced Multi-Agent Intelligence System)
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIProjectAnalyzer:
    """Advanced AI-powered project analyzer with multi-agent intelligence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'project_analysis',
            'mode': config.get('mode', 'intelligent'),
            'areas': config.get('areas', 'all'),
            'depth': config.get('depth', 'deep'),
            'auto_apply': config.get('auto_apply', False),
            'findings': [],
            'recommendations': [],
            'metrics': {},
            'status': 'success'
        }
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure and organization"""
        logger.info("🔍 Analyzing project structure...")
        
        structure_analysis = {
            'directories': [],
            'files': [],
            'languages': {},
            'frameworks': [],
            'architecture_patterns': [],
            'complexity_score': 0
        }
        
        try:
            # Scan project directory
            project_root = Path('.')
            
            for item in project_root.rglob('*'):
                if item.is_file():
                    structure_analysis['files'].append({
                        'path': str(item.relative_to(project_root)),
                        'size': item.stat().st_size,
                        'extension': item.suffix,
                        'modified': item.stat().st_mtime
                    })
                    
                    # Detect language by extension
                    ext = item.suffix.lower()
                    if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                        lang = ext[1:]
                        structure_analysis['languages'][lang] = structure_analysis['languages'].get(lang, 0) + 1
                        
                elif item.is_dir() and not any(part.startswith('.') for part in item.parts):
                    structure_analysis['directories'].append(str(item.relative_to(project_root)))
            
            # Detect frameworks and patterns
            structure_analysis['frameworks'] = self._detect_frameworks()
            structure_analysis['architecture_patterns'] = self._detect_architecture_patterns()
            structure_analysis['complexity_score'] = self._calculate_complexity_score(structure_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            structure_analysis['error'] = str(e)
            
        return structure_analysis
    
    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        logger.info("📊 Analyzing code quality...")
        
        quality_analysis = {
            'lines_of_code': 0,
            'cyclomatic_complexity': 0,
            'maintainability_index': 0,
            'technical_debt': 0,
            'code_smells': [],
            'duplications': [],
            'test_coverage': 0,
            'documentation_coverage': 0
        }
        
        try:
            # Count lines of code
            total_lines = 0
            code_files = 0
            
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                            code_files += 1
                    except Exception:
                        continue
            
            quality_analysis['lines_of_code'] = total_lines
            quality_analysis['files_analyzed'] = code_files
            
            # Analyze code patterns
            quality_analysis['code_smells'] = self._detect_code_smells()
            quality_analysis['duplications'] = self._detect_duplications()
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            quality_analysis['error'] = str(e)
            
        return quality_analysis
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        logger.info("📦 Analyzing dependencies...")
        
        dependency_analysis = {
            'dependencies': [],
            'dev_dependencies': [],
            'outdated_packages': [],
            'security_vulnerabilities': [],
            'license_conflicts': [],
            'dependency_health': 'good'
        }
        
        try:
            # Check for requirements files
            req_files = ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml', 'setup.py']
            
            for req_file in req_files:
                if Path(req_file).exists():
                    dependency_analysis['dependencies'].extend(self._parse_requirements(req_file))
            
            # Analyze dependency health
            dependency_analysis['dependency_health'] = self._assess_dependency_health(dependency_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {e}")
            dependency_analysis['error'] = str(e)
            
        return dependency_analysis
    
    def analyze_security(self) -> Dict[str, Any]:
        """Analyze security aspects"""
        logger.info("🔒 Analyzing security...")
        
        security_analysis = {
            'vulnerabilities': [],
            'secrets_detected': [],
            'permissions': [],
            'encryption_usage': [],
            'security_score': 0
        }
        
        try:
            # Check for common security issues
            security_analysis['secrets_detected'] = self._detect_secrets()
            security_analysis['vulnerabilities'] = self._detect_vulnerabilities()
            security_analysis['security_score'] = self._calculate_security_score(security_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            security_analysis['error'] = str(e)
            
        return security_analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        logger.info("⚡ Analyzing performance...")
        
        performance_analysis = {
            'bottlenecks': [],
            'optimization_opportunities': [],
            'resource_usage': {},
            'performance_score': 0
        }
        
        try:
            # Analyze performance patterns
            performance_analysis['bottlenecks'] = self._detect_performance_bottlenecks()
            performance_analysis['optimization_opportunities'] = self._find_optimization_opportunities()
            performance_analysis['performance_score'] = self._calculate_performance_score(performance_analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            performance_analysis['error'] = str(e)
            
        return performance_analysis
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        logger.info("💡 Generating recommendations...")
        
        recommendations = []
        
        try:
            # Analyze findings and generate recommendations
            if self.results['findings']:
                for finding in self.results['findings']:
                    if finding.get('severity') == 'high':
                        recommendations.append({
                            'type': 'critical_fix',
                            'priority': 'high',
                            'title': f"Fix {finding.get('type', 'issue')}",
                            'description': finding.get('description', ''),
                            'action': finding.get('recommended_action', ''),
                            'impact': 'high'
                        })
            
            # Add general recommendations based on analysis
            recommendations.extend(self._generate_general_recommendations())
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            
        return recommendations
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and libraries used"""
        frameworks = []
        
        # Check for common framework indicators
        framework_indicators = {
            'django': ['django/', 'manage.py', 'settings.py'],
            'flask': ['app.py', 'flask_app.py'],
            'fastapi': ['main.py', 'app.py'],
            'react': ['package.json', 'src/'],
            'vue': ['vue.config.js', 'src/'],
            'angular': ['angular.json', 'src/'],
            'spring': ['pom.xml', 'application.properties'],
            'express': ['package.json', 'app.js', 'server.js']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(Path(indicator).exists() for indicator in indicators):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_architecture_patterns(self) -> List[str]:
        """Detect architectural patterns"""
        patterns = []
        
        # Check for common patterns
        if Path('src/').exists() and Path('tests/').exists():
            patterns.append('layered_architecture')
        
        if any(Path(p).exists() for p in ['api/', 'services/', 'models/']):
            patterns.append('service_oriented')
        
        if Path('docker-compose.yml').exists():
            patterns.append('microservices')
        
        return patterns
    
    def _calculate_complexity_score(self, structure: Dict[str, Any]) -> int:
        """Calculate project complexity score"""
        score = 0
        
        # Base score on number of files and directories
        score += len(structure['files']) * 0.1
        score += len(structure['directories']) * 0.5
        
        # Add complexity for multiple languages
        score += len(structure['languages']) * 2
        
        # Add complexity for frameworks
        score += len(structure['frameworks']) * 1.5
        
        return int(score)
    
    def _detect_code_smells(self) -> List[Dict[str, Any]]:
        """Detect code smells"""
        smells = []
        
        try:
            # Check for common code smells
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Check for long functions (simplified)
                            lines = content.split('\n')
                            if len(lines) > 50:
                                smells.append({
                                    'type': 'long_function',
                                    'file': str(file_path),
                                    'description': 'Function or file is too long',
                                    'severity': 'medium'
                                })
                            
                            # Check for duplicate code patterns
                            if 'TODO' in content or 'FIXME' in content:
                                smells.append({
                                    'type': 'technical_debt',
                                    'file': str(file_path),
                                    'description': 'Contains TODO or FIXME comments',
                                    'severity': 'low'
                                })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error detecting code smells: {e}")
        
        return smells
    
    def _detect_duplications(self) -> List[Dict[str, Any]]:
        """Detect code duplications"""
        duplications = []
        
        # Simplified duplication detection
        # In a real implementation, this would use more sophisticated algorithms
        try:
            file_contents = {}
            
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            file_contents[str(file_path)] = content
                    except Exception:
                        continue
            
            # Simple duplication detection based on common patterns
            common_patterns = [
                'import os',
                'import sys',
                'def main():',
                'if __name__ == "__main__":'
            ]
            
            for pattern in common_patterns:
                files_with_pattern = [f for f, c in file_contents.items() if pattern in c]
                if len(files_with_pattern) > 3:
                    duplications.append({
                        'type': 'common_pattern',
                        'pattern': pattern,
                        'files': files_with_pattern,
                        'severity': 'low'
                    })
        except Exception as e:
            logger.error(f"Error detecting duplications: {e}")
        
        return duplications
    
    def _parse_requirements(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse requirements file"""
        requirements = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Simple parsing - in reality would use proper requirement parsing
                        if '==' in line:
                            name, version = line.split('==', 1)
                            requirements.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'constraint': '=='
                            })
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                            requirements.append({
                                'name': name.strip(),
                                'version': version.strip(),
                                'constraint': '>='
                            })
                        else:
                            requirements.append({
                                'name': line,
                                'version': 'latest',
                                'constraint': 'none'
                            })
        except Exception as e:
            logger.error(f"Error parsing requirements {file_path}: {e}")
        
        return requirements
    
    def _assess_dependency_health(self, analysis: Dict[str, Any]) -> str:
        """Assess overall dependency health"""
        if not analysis['dependencies']:
            return 'unknown'
        
        # Simple health assessment
        total_deps = len(analysis['dependencies'])
        if total_deps < 10:
            return 'excellent'
        elif total_deps < 50:
            return 'good'
        elif total_deps < 100:
            return 'fair'
        else:
            return 'poor'
    
    def _detect_secrets(self) -> List[Dict[str, Any]]:
        """Detect potential secrets in code"""
        secrets = []
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        try:
            import re
            
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            for pattern in secret_patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    secrets.append({
                                        'type': 'potential_secret',
                                        'file': str(file_path),
                                        'pattern': pattern,
                                        'match': match,
                                        'severity': 'high'
                                    })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error detecting secrets: {e}")
        
        return secrets
    
    def _detect_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Detect security vulnerabilities"""
        vulnerabilities = []
        
        # Check for common vulnerability patterns
        vuln_patterns = [
            {
                'pattern': r'eval\s*\(',
                'type': 'code_injection',
                'severity': 'high'
            },
            {
                'pattern': r'exec\s*\(',
                'type': 'code_injection',
                'severity': 'high'
            },
            {
                'pattern': r'shell=True',
                'type': 'command_injection',
                'severity': 'medium'
            }
        ]
        
        try:
            import re
            
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            for vuln in vuln_patterns:
                                matches = re.findall(vuln['pattern'], content)
                                for match in matches:
                                    vulnerabilities.append({
                                        'type': vuln['type'],
                                        'file': str(file_path),
                                        'pattern': vuln['pattern'],
                                        'match': match,
                                        'severity': vuln['severity']
                                    })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error detecting vulnerabilities: {e}")
        
        return vulnerabilities
    
    def _calculate_security_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate security score (0-100)"""
        score = 100
        
        # Deduct points for vulnerabilities
        for vuln in analysis['vulnerabilities']:
            if vuln['severity'] == 'high':
                score -= 20
            elif vuln['severity'] == 'medium':
                score -= 10
            else:
                score -= 5
        
        # Deduct points for secrets
        score -= len(analysis['secrets_detected']) * 15
        
        return max(0, score)
    
    def _detect_performance_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        try:
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Check for common performance issues
                            if 'for ' in content and 'for ' in content[content.find('for ')+1:]:
                                bottlenecks.append({
                                    'type': 'nested_loops',
                                    'file': str(file_path),
                                    'description': 'Nested loops detected',
                                    'severity': 'medium'
                                })
                            
                            if 'time.sleep(' in content:
                                bottlenecks.append({
                                    'type': 'blocking_sleep',
                                    'file': str(file_path),
                                    'description': 'Blocking sleep detected',
                                    'severity': 'low'
                                })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error detecting performance bottlenecks: {e}")
        
        return bottlenecks
    
    def _find_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Find optimization opportunities"""
        opportunities = []
        
        try:
            for file_path in Path('.').rglob('*.py'):
                if not any(part.startswith('.') for part in file_path.parts):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Check for optimization opportunities
                            if 'import *' in content:
                                opportunities.append({
                                    'type': 'wildcard_import',
                                    'file': str(file_path),
                                    'description': 'Wildcard import detected - consider specific imports',
                                    'severity': 'low'
                                })
                            
                            if 'list(' in content and 'range(' in content:
                                opportunities.append({
                                    'type': 'list_comprehension',
                                    'file': str(file_path),
                                    'description': 'Consider using list comprehension',
                                    'severity': 'low'
                                })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Error finding optimization opportunities: {e}")
        
        return opportunities
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate performance score (0-100)"""
        score = 100
        
        # Deduct points for bottlenecks
        for bottleneck in analysis['bottlenecks']:
            if bottleneck['severity'] == 'high':
                score -= 25
            elif bottleneck['severity'] == 'medium':
                score -= 15
            else:
                score -= 5
        
        return max(0, score)
    
    def _generate_general_recommendations(self) -> List[Dict[str, Any]]:
        """Generate general recommendations based on analysis"""
        recommendations = []
        
        # Add recommendations based on analysis results
        if self.results.get('metrics', {}).get('lines_of_code', 0) > 10000:
            recommendations.append({
                'type': 'code_organization',
                'priority': 'medium',
                'title': 'Consider code modularization',
                'description': 'Large codebase detected - consider breaking into smaller modules',
                'action': 'Refactor large files into smaller, focused modules',
                'impact': 'medium'
            })
        
        if len(self.results.get('findings', [])) > 20:
            recommendations.append({
                'type': 'code_quality',
                'priority': 'high',
                'title': 'Address code quality issues',
                'description': 'Multiple code quality issues detected',
                'action': 'Review and fix identified code quality problems',
                'impact': 'high'
            })
        
        return recommendations
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete project analysis"""
        logger.info("🚀 Starting AI Project Analysis...")
        
        try:
            # Run all analysis components
            self.results['structure'] = self.analyze_project_structure()
            self.results['code_quality'] = self.analyze_code_quality()
            self.results['dependencies'] = self.analyze_dependencies()
            self.results['security'] = self.analyze_security()
            self.results['performance'] = self.analyze_performance()
            
            # Generate recommendations
            self.results['recommendations'] = self.generate_recommendations()
            
            # Calculate overall metrics
            self.results['metrics'] = self._calculate_overall_metrics()
            
            logger.info("✅ Project analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return self.results
    
    def _calculate_overall_metrics(self) -> Dict[str, Any]:
        """Calculate overall project metrics"""
        metrics = {
            'total_files': len(self.results.get('structure', {}).get('files', [])),
            'total_lines': self.results.get('code_quality', {}).get('lines_of_code', 0),
            'languages_count': len(self.results.get('structure', {}).get('languages', {})),
            'frameworks_count': len(self.results.get('structure', {}).get('frameworks', [])),
            'security_score': self.results.get('security', {}).get('security_score', 0),
            'performance_score': self.results.get('performance', {}).get('performance_score', 0),
            'complexity_score': self.results.get('structure', {}).get('complexity_score', 0),
            'issues_count': len(self.results.get('findings', [])),
            'recommendations_count': len(self.results.get('recommendations', []))
        }
        
        # Calculate overall health score
        health_components = [
            metrics['security_score'],
            metrics['performance_score'],
            100 - min(metrics['complexity_score'], 100),
            100 - min(metrics['issues_count'] * 5, 100)
        ]
        
        metrics['overall_health_score'] = sum(health_components) // len(health_components)
        
        return metrics

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Project Analyzer')
    parser.add_argument('--mode', default='intelligent', help='Analysis mode')
    parser.add_argument('--areas', default='all', help='Target areas for analysis')
    parser.add_argument('--depth', default='deep', help='Analysis depth')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply fixes')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='project_analysis_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'mode': args.mode,
        'areas': args.areas,
        'depth': args.depth,
        'auto_apply': args.auto_apply,
        'use_advanced_manager': args.use_advanced_manager
    }
    
    # Initialize analyzer
    analyzer = AIProjectAnalyzer(config)
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Analysis results saved to {args.output}")
    
    return 0 if results['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())