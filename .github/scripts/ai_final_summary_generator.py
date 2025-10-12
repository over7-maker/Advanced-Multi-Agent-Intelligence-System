#!/usr/bin/env python3
"""
AI Final Summary Generator - Advanced Multi-Agent Summary Generation System
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

class AIFinalSummaryGenerator:
    """Advanced AI-powered final summary generator with multi-agent intelligence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'summary_type': 'final_summary',
            'mode': config.get('mode', 'intelligent'),
            'areas': config.get('areas', 'all'),
            'depth': config.get('depth', 'deep'),
            'auto_apply': config.get('auto_apply', False),
            'executive_summary': {},
            'phase_summaries': {},
            'key_achievements': [],
            'critical_issues': [],
            'recommendations': [],
            'metrics': {},
            'insights': [],
            'next_steps': [],
            'status': 'success'
        }
        
    def load_all_results(self, results_path: str) -> Dict[str, Any]:
        """Load all results from all phases"""
        logger.info(f"📥 Loading all results from {results_path}")
        
        all_results = {}
        
        try:
            if os.path.isdir(results_path):
                # Load all result files
                for file_path in Path(results_path).glob('*results*.json'):
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            # Extract phase name from filename
                            phase_name = file_path.stem.replace('_results', '').replace('-', '_')
                            all_results[phase_name] = data
                    except Exception as e:
                        logger.warning(f"Error loading {file_path}: {e}")
            else:
                with open(results_path, 'r') as f:
                    all_results = json.load(f)
        except Exception as e:
            logger.error(f"Error loading results: {e}")
        
        return all_results
    
    def generate_executive_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        logger.info("📊 Generating executive summary...")
        
        executive_summary = {
            'overview': '',
            'key_metrics': {},
            'success_rate': 0,
            'total_phases': len(all_results),
            'completed_phases': 0,
            'overall_status': 'success',
            'critical_findings': [],
            'major_achievements': []
        }
        
        try:
            # Calculate overall metrics
            total_files_analyzed = 0
            total_improvements_generated = 0
            total_implementations = 0
            successful_implementations = 0
            total_insights = 0
            
            completed_phases = 0
            
            for phase_name, phase_results in all_results.items():
                if phase_results.get('status') == 'success':
                    completed_phases += 1
                
                # Aggregate metrics
                if 'metrics' in phase_results:
                    metrics = phase_results['metrics']
                    total_files_analyzed += metrics.get('total_files', 0)
                    total_insights += metrics.get('total_insights', 0)
                
                if 'improvements' in phase_results:
                    total_improvements_generated += len(phase_results['improvements'])
                
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    total_implementations += len(implementations)
                    successful_implementations += sum(1 for impl in implementations if impl.get('status') == 'success')
            
            # Calculate success rate
            if total_implementations > 0:
                success_rate = (successful_implementations / total_implementations) * 100
            else:
                success_rate = 0
            
            # Generate overview
            executive_summary['overview'] = f"""
            The AMAS (Advanced Multi-Agent Intelligence System) has completed a comprehensive analysis and improvement cycle.
            The system successfully processed {total_files_analyzed} files across {completed_phases} phases,
            generating {total_improvements_generated} improvements and implementing {successful_implementations} changes
            with a {success_rate:.1f}% success rate.
            """
            
            # Set key metrics
            executive_summary['key_metrics'] = {
                'files_analyzed': total_files_analyzed,
                'improvements_generated': total_improvements_generated,
                'implementations_attempted': total_implementations,
                'implementations_successful': successful_implementations,
                'success_rate': success_rate,
                'insights_generated': total_insights
            }
            
            executive_summary['success_rate'] = success_rate
            executive_summary['completed_phases'] = completed_phases
            
            # Determine overall status
            if success_rate >= 80:
                executive_summary['overall_status'] = 'excellent'
            elif success_rate >= 60:
                executive_summary['overall_status'] = 'good'
            elif success_rate >= 40:
                executive_summary['overall_status'] = 'fair'
            else:
                executive_summary['overall_status'] = 'needs_improvement'
            
            # Extract critical findings
            executive_summary['critical_findings'] = self._extract_critical_findings(all_results)
            
            # Extract major achievements
            executive_summary['major_achievements'] = self._extract_major_achievements(all_results)
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            executive_summary['error'] = str(e)
        
        return executive_summary
    
    def generate_phase_summaries(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summaries for each phase"""
        logger.info("📋 Generating phase summaries...")
        
        phase_summaries = {}
        
        try:
            for phase_name, phase_results in all_results.items():
                phase_summary = {
                    'status': phase_results.get('status', 'unknown'),
                    'timestamp': phase_results.get('timestamp', ''),
                    'key_activities': [],
                    'metrics': phase_results.get('metrics', {}),
                    'achievements': [],
                    'issues': [],
                    'recommendations': []
                }
                
                # Extract key activities based on phase type
                if 'analysis' in phase_name:
                    phase_summary['key_activities'] = [
                        'Project structure analysis',
                        'Code quality assessment',
                        'Dependency analysis',
                        'Security scanning',
                        'Performance analysis'
                    ]
                elif 'improvement' in phase_name:
                    phase_summary['key_activities'] = [
                        'Code improvement generation',
                        'Architectural improvement suggestions',
                        'Performance optimization recommendations',
                        'Security enhancement proposals',
                        'Documentation improvement plans'
                    ]
                elif 'implementation' in phase_name:
                    phase_summary['key_activities'] = [
                        'Code refactoring implementation',
                        'Architectural changes',
                        'Performance optimizations',
                        'Security enhancements',
                        'Documentation updates'
                    ]
                elif 'learning' in phase_name:
                    phase_summary['key_activities'] = [
                        'Pattern analysis',
                        'Adaptation strategy generation',
                        'Knowledge base updates',
                        'Model adaptations',
                        'Future recommendations'
                    ]
                
                # Extract achievements
                if 'files_created' in phase_results:
                    phase_summary['achievements'].append(f"Created {len(phase_results['files_created'])} files")
                
                if 'files_modified' in phase_results:
                    phase_summary['achievements'].append(f"Modified {len(phase_results['files_modified'])} files")
                
                if 'improvements' in phase_results:
                    phase_summary['achievements'].append(f"Generated {len(phase_results['improvements'])} improvements")
                
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                    phase_summary['achievements'].append(f"Successfully implemented {successful} changes")
                
                # Extract issues
                if phase_results.get('status') == 'error':
                    phase_summary['issues'].append(f"Phase failed: {phase_results.get('error', 'Unknown error')}")
                
                # Generate recommendations for this phase
                phase_summary['recommendations'] = self._generate_phase_recommendations(phase_name, phase_results)
                
                phase_summaries[phase_name] = phase_summary
            
        except Exception as e:
            logger.error(f"Error generating phase summaries: {e}")
        
        return phase_summaries
    
    def generate_key_achievements(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate key achievements list"""
        logger.info("🏆 Generating key achievements...")
        
        achievements = []
        
        try:
            # Aggregate achievements from all phases
            total_files_created = 0
            total_files_modified = 0
            total_improvements = 0
            total_implementations = 0
            successful_implementations = 0
            
            for phase_name, phase_results in all_results.items():
                if 'files_created' in phase_results:
                    total_files_created += len(phase_results['files_created'])
                
                if 'files_modified' in phase_results:
                    total_files_modified += len(phase_results['files_modified'])
                
                if 'improvements' in phase_results:
                    total_improvements += len(phase_results['improvements'])
                
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    total_implementations += len(implementations)
                    successful_implementations += sum(1 for impl in implementations if impl.get('status') == 'success')
            
            # Create achievement entries
            if total_files_created > 0:
                achievements.append({
                    'category': 'file_management',
                    'title': 'File Creation',
                    'description': f'Created {total_files_created} new files',
                    'impact': 'medium',
                    'value': total_files_created
                })
            
            if total_files_modified > 0:
                achievements.append({
                    'category': 'file_management',
                    'title': 'File Modification',
                    'description': f'Modified {total_files_modified} existing files',
                    'impact': 'high',
                    'value': total_files_modified
                })
            
            if total_improvements > 0:
                achievements.append({
                    'category': 'improvement_generation',
                    'title': 'Improvement Generation',
                    'description': f'Generated {total_improvements} improvement suggestions',
                    'impact': 'high',
                    'value': total_improvements
                })
            
            if successful_implementations > 0:
                achievements.append({
                    'category': 'implementation',
                    'title': 'Successful Implementation',
                    'description': f'Successfully implemented {successful_implementations} changes',
                    'impact': 'critical',
                    'value': successful_implementations
                })
            
            # Add specific achievements based on results
            achievements.extend(self._extract_specific_achievements(all_results))
            
        except Exception as e:
            logger.error(f"Error generating key achievements: {e}")
        
        return achievements
    
    def generate_critical_issues(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate critical issues list"""
        logger.info("⚠️ Generating critical issues...")
        
        issues = []
        
        try:
            # Check for failed phases
            for phase_name, phase_results in all_results.items():
                if phase_results.get('status') == 'error':
                    issues.append({
                        'type': 'phase_failure',
                        'phase': phase_name,
                        'severity': 'critical',
                        'description': f'Phase {phase_name} failed: {phase_results.get("error", "Unknown error")}',
                        'recommendation': 'Investigate and fix the phase failure'
                    })
            
            # Check for low success rates
            for phase_name, phase_results in all_results.items():
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    if implementations:
                        successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                        success_rate = (successful / len(implementations)) * 100
                        
                        if success_rate < 50:
                            issues.append({
                                'type': 'low_success_rate',
                                'phase': phase_name,
                                'severity': 'high',
                                'description': f'Phase {phase_name} has low success rate: {success_rate:.1f}%',
                                'recommendation': 'Review and improve implementation process'
                            })
            
            # Check for security issues
            for phase_name, phase_results in all_results.items():
                if 'security' in phase_results:
                    security = phase_results['security']
                    vulnerabilities = security.get('vulnerabilities', [])
                    secrets = security.get('secrets_detected', [])
                    
                    if vulnerabilities:
                        issues.append({
                            'type': 'security_vulnerability',
                            'phase': phase_name,
                            'severity': 'critical',
                            'description': f'Found {len(vulnerabilities)} security vulnerabilities',
                            'recommendation': 'Address security vulnerabilities immediately'
                        })
                    
                    if secrets:
                        issues.append({
                            'type': 'exposed_secrets',
                            'phase': phase_name,
                            'severity': 'critical',
                            'description': f'Found {len(secrets)} exposed secrets',
                            'recommendation': 'Secure exposed secrets immediately'
                        })
            
        except Exception as e:
            logger.error(f"Error generating critical issues: {e}")
        
        return issues
    
    def generate_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for future improvements"""
        logger.info("💡 Generating recommendations...")
        
        recommendations = []
        
        try:
            # Generate recommendations based on analysis
            recommendations.extend(self._generate_performance_recommendations(all_results))
            recommendations.extend(self._generate_security_recommendations(all_results))
            recommendations.extend(self._generate_process_recommendations(all_results))
            recommendations.extend(self._generate_technical_recommendations(all_results))
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def generate_insights(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate key insights from the analysis"""
        logger.info("🔍 Generating insights...")
        
        insights = []
        
        try:
            # Analyze patterns across phases
            insights.extend(self._analyze_success_patterns(all_results))
            insights.extend(self._analyze_failure_patterns(all_results))
            insights.extend(self._analyze_performance_patterns(all_results))
            insights.extend(self._analyze_improvement_patterns(all_results))
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
        
        return insights
    
    def generate_next_steps(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate next steps for continued improvement"""
        logger.info("🚀 Generating next steps...")
        
        next_steps = []
        
        try:
            # Generate immediate next steps
            next_steps.extend(self._generate_immediate_steps(all_results))
            
            # Generate medium-term steps
            next_steps.extend(self._generate_medium_term_steps(all_results))
            
            # Generate long-term steps
            next_steps.extend(self._generate_long_term_steps(all_results))
            
        except Exception as e:
            logger.error(f"Error generating next steps: {e}")
        
        return next_steps
    
    def _extract_critical_findings(self, all_results: Dict[str, Any]) -> List[str]:
        """Extract critical findings from all results"""
        findings = []
        
        # Check for critical security issues
        for phase_name, phase_results in all_results.items():
            if 'security' in phase_results:
                security = phase_results['security']
                if security.get('vulnerabilities'):
                    findings.append(f"Security vulnerabilities detected in {phase_name}")
                if security.get('secrets_detected'):
                    findings.append(f"Exposed secrets found in {phase_name}")
        
        # Check for critical performance issues
        for phase_name, phase_results in all_results.items():
            if 'performance' in phase_results:
                performance = phase_results['performance']
                if performance.get('bottlenecks'):
                    findings.append(f"Performance bottlenecks identified in {phase_name}")
        
        return findings
    
    def _extract_major_achievements(self, all_results: Dict[str, Any]) -> List[str]:
        """Extract major achievements from all results"""
        achievements = []
        
        # Count total improvements and implementations
        total_improvements = 0
        total_implementations = 0
        
        for phase_results in all_results.values():
            if 'improvements' in phase_results:
                total_improvements += len(phase_results['improvements'])
            if 'implementations' in phase_results:
                total_implementations += len(phase_results['implementations'])
        
        if total_improvements > 0:
            achievements.append(f"Generated {total_improvements} improvement suggestions")
        
        if total_implementations > 0:
            achievements.append(f"Implemented {total_implementations} changes")
        
        return achievements
    
    def _generate_phase_recommendations(self, phase_name: str, phase_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a specific phase"""
        recommendations = []
        
        if phase_results.get('status') == 'error':
            recommendations.append("Fix the phase failure before proceeding")
        
        if 'implementations' in phase_results:
            implementations = phase_results['implementations']
            if implementations:
                successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                success_rate = (successful / len(implementations)) * 100
                
                if success_rate < 80:
                    recommendations.append("Improve implementation success rate")
        
        return recommendations
    
    def _extract_specific_achievements(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific achievements from results"""
        achievements = []
        
        # Look for specific achievements in each phase
        for phase_name, phase_results in all_results.items():
            if 'achievements' in phase_results:
                achievements.extend(phase_results['achievements'])
        
        return achievements
    
    def _generate_performance_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance-related recommendations"""
        recommendations = []
        
        # Check for performance issues across phases
        for phase_name, phase_results in all_results.items():
            if 'performance' in phase_results:
                performance = phase_results['performance']
                if performance.get('bottlenecks'):
                    recommendations.append({
                        'category': 'performance',
                        'priority': 'high',
                        'title': 'Address Performance Bottlenecks',
                        'description': f'Performance bottlenecks detected in {phase_name}',
                        'action': 'Optimize identified bottlenecks'
                    })
        
        return recommendations
    
    def _generate_security_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security-related recommendations"""
        recommendations = []
        
        # Check for security issues across phases
        for phase_name, phase_results in all_results.items():
            if 'security' in phase_results:
                security = phase_results['security']
                if security.get('vulnerabilities'):
                    recommendations.append({
                        'category': 'security',
                        'priority': 'critical',
                        'title': 'Fix Security Vulnerabilities',
                        'description': f'Security vulnerabilities found in {phase_name}',
                        'action': 'Address all security vulnerabilities immediately'
                    })
                
                if security.get('secrets_detected'):
                    recommendations.append({
                        'category': 'security',
                        'priority': 'critical',
                        'title': 'Secure Exposed Secrets',
                        'description': f'Exposed secrets found in {phase_name}',
                        'action': 'Move secrets to secure storage and rotate them'
                    })
        
        return recommendations
    
    def _generate_process_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate process-related recommendations"""
        recommendations = []
        
        # Analyze process effectiveness
        total_phases = len(all_results)
        successful_phases = sum(1 for phase_results in all_results.values() if phase_results.get('status') == 'success')
        
        if successful_phases < total_phases:
            recommendations.append({
                'category': 'process',
                'priority': 'high',
                'title': 'Improve Process Reliability',
                'description': f'Only {successful_phases}/{total_phases} phases completed successfully',
                'action': 'Review and improve process reliability'
            })
        
        return recommendations
    
    def _generate_technical_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical recommendations"""
        recommendations = []
        
        # Add general technical recommendations
        recommendations.append({
            'category': 'technical',
            'priority': 'medium',
            'title': 'Implement Continuous Monitoring',
            'description': 'Set up continuous monitoring for the AMAS system',
            'action': 'Implement monitoring and alerting systems'
        })
        
        recommendations.append({
            'category': 'technical',
            'priority': 'medium',
            'title': 'Enhance Error Handling',
            'description': 'Improve error handling and recovery mechanisms',
            'action': 'Add comprehensive error handling and recovery'
        })
        
        return recommendations
    
    def _analyze_success_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze success patterns"""
        insights = []
        
        # Look for phases with high success rates
        for phase_name, phase_results in all_results.items():
            if 'implementations' in phase_results:
                implementations = phase_results['implementations']
                if implementations:
                    successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                    success_rate = (successful / len(implementations)) * 100
                    
                    if success_rate > 90:
                        insights.append({
                            'type': 'success_pattern',
                            'title': f'High Success Rate in {phase_name}',
                            'description': f'Phase {phase_name} achieved {success_rate:.1f}% success rate',
                            'recommendation': 'Replicate this approach in other phases'
                        })
        
        return insights
    
    def _analyze_failure_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze failure patterns"""
        insights = []
        
        # Look for common failure reasons
        failure_reasons = []
        for phase_results in all_results.values():
            if 'implementations' in phase_results:
                for implementation in phase_results['implementations']:
                    if implementation.get('status') == 'error' and 'error' in implementation:
                        failure_reasons.append(implementation['error'])
        
        if failure_reasons:
            # Count most common failure reasons
            from collections import Counter
            common_failures = Counter(failure_reasons).most_common(3)
            
            for failure, count in common_failures:
                insights.append({
                    'type': 'failure_pattern',
                    'title': f'Common Failure: {failure}',
                    'description': f'This failure occurred {count} times',
                    'recommendation': 'Address this common failure pattern'
                })
        
        return insights
    
    def _analyze_performance_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance patterns"""
        insights = []
        
        # Look for performance trends
        performance_scores = []
        for phase_name, phase_results in all_results.items():
            if 'performance' in phase_results:
                score = phase_results['performance'].get('performance_score', 0)
                performance_scores.append((phase_name, score))
        
        if len(performance_scores) >= 2:
            first_score = performance_scores[0][1]
            last_score = performance_scores[-1][1]
            
            if last_score > first_score:
                insights.append({
                    'type': 'performance_pattern',
                    'title': 'Performance Improvement Trend',
                    'description': f'Performance improved from {first_score} to {last_score}',
                    'recommendation': 'Continue current performance optimization approach'
                })
            elif last_score < first_score:
                insights.append({
                    'type': 'performance_pattern',
                    'title': 'Performance Decline Trend',
                    'description': f'Performance declined from {first_score} to {last_score}',
                    'recommendation': 'Investigate and address performance decline'
                })
        
        return insights
    
    def _analyze_improvement_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze improvement patterns"""
        insights = []
        
        # Count improvement types
        improvement_types = {}
        for phase_results in all_results.values():
            if 'improvements' in phase_results:
                for improvement in phase_results['improvements']:
                    imp_type = improvement.get('type', 'unknown')
                    improvement_types[imp_type] = improvement_types.get(imp_type, 0) + 1
        
        if improvement_types:
            most_common = max(improvement_types.items(), key=lambda x: x[1])
            insights.append({
                'type': 'improvement_pattern',
                'title': f'Most Common Improvement Type: {most_common[0]}',
                'description': f'Generated {most_common[1]} improvements of this type',
                'recommendation': 'Focus on this improvement type for better results'
            })
        
        return insights
    
    def _generate_immediate_steps(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate immediate next steps"""
        steps = []
        
        # Check for critical issues that need immediate attention
        for phase_results in all_results.values():
            if 'security' in phase_results:
                security = phase_results['security']
                if security.get('vulnerabilities') or security.get('secrets_detected'):
                    steps.append({
                        'timeline': 'immediate',
                        'priority': 'critical',
                        'title': 'Address Security Issues',
                        'description': 'Fix security vulnerabilities and secure exposed secrets',
                        'effort': 'high'
                    })
                    break
        
        # Add general immediate steps
        steps.append({
            'timeline': 'immediate',
            'priority': 'high',
            'title': 'Review Implementation Results',
            'description': 'Review all implementation results and verify changes',
            'effort': 'medium'
        })
        
        return steps
    
    def _generate_medium_term_steps(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate medium-term next steps"""
        steps = []
        
        steps.append({
            'timeline': 'medium_term',
            'priority': 'high',
            'title': 'Implement Process Improvements',
            'description': 'Implement recommendations for process improvements',
            'effort': 'high'
        })
        
        steps.append({
            'timeline': 'medium_term',
            'priority': 'medium',
            'title': 'Enhance Monitoring',
            'description': 'Set up comprehensive monitoring and alerting',
            'effort': 'medium'
        })
        
        return steps
    
    def _generate_long_term_steps(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate long-term next steps"""
        steps = []
        
        steps.append({
            'timeline': 'long_term',
            'priority': 'medium',
            'title': 'Advanced AI Integration',
            'description': 'Integrate more advanced AI models and techniques',
            'effort': 'very_high'
        })
        
        steps.append({
            'timeline': 'long_term',
            'priority': 'low',
            'title': 'System Optimization',
            'description': 'Optimize the entire AMAS system for better performance',
            'effort': 'high'
        })
        
        return steps
    
    def run_final_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete final summary generation"""
        logger.info("📊 Starting final summary generation...")
        
        try:
            # Generate all summary components
            self.results['executive_summary'] = self.generate_executive_summary(all_results)
            self.results['phase_summaries'] = self.generate_phase_summaries(all_results)
            self.results['key_achievements'] = self.generate_key_achievements(all_results)
            self.results['critical_issues'] = self.generate_critical_issues(all_results)
            self.results['recommendations'] = self.generate_recommendations(all_results)
            self.results['insights'] = self.generate_insights(all_results)
            self.results['next_steps'] = self.generate_next_steps(all_results)
            
            # Calculate final metrics
            self.results['metrics'] = self._calculate_final_metrics(all_results)
            
            logger.info("✅ Final summary generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during final summary generation: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return self.results
    
    def _calculate_final_metrics(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final metrics"""
        metrics = {
            'total_phases': len(all_results),
            'successful_phases': sum(1 for phase_results in all_results.values() if phase_results.get('status') == 'success'),
            'total_files_analyzed': 0,
            'total_improvements': 0,
            'total_implementations': 0,
            'successful_implementations': 0,
            'total_insights': 0,
            'critical_issues': len(self.results.get('critical_issues', [])),
            'recommendations': len(self.results.get('recommendations', [])),
            'achievements': len(self.results.get('key_achievements', []))
        }
        
        # Aggregate metrics from all phases
        for phase_results in all_results.values():
            if 'metrics' in phase_results:
                phase_metrics = phase_results['metrics']
                metrics['total_files_analyzed'] += phase_metrics.get('total_files', 0)
                metrics['total_insights'] += phase_metrics.get('total_insights', 0)
            
            if 'improvements' in phase_results:
                metrics['total_improvements'] += len(phase_results['improvements'])
            
            if 'implementations' in phase_results:
                implementations = phase_results['implementations']
                metrics['total_implementations'] += len(implementations)
                metrics['successful_implementations'] += sum(1 for impl in implementations if impl.get('status') == 'success')
        
        # Calculate success rate
        if metrics['total_implementations'] > 0:
            metrics['success_rate'] = (metrics['successful_implementations'] / metrics['total_implementations']) * 100
        else:
            metrics['success_rate'] = 0
        
        return metrics

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Final Summary Generator')
    parser.add_argument('--mode', default='intelligent', help='Summary mode')
    parser.add_argument('--areas', default='all', help='Target areas for summary')
    parser.add_argument('--depth', default='deep', help='Summary depth')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply recommendations')
    parser.add_argument('--all-results', default='final_results/', help='Path to all results')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='final_summary_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'mode': args.mode,
        'areas': args.areas,
        'depth': args.depth,
        'auto_apply': args.auto_apply,
        'use_advanced_manager': args.use_advanced_manager
    }
    
    # Initialize summary generator
    summary_generator = AIFinalSummaryGenerator(config)
    
    # Load all results
    all_results = summary_generator.load_all_results(args.all_results)
    
    # Run final summary generation
    results = summary_generator.run_final_summary(all_results)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Final summary results saved to {args.output}")
    
    return 0 if results['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())