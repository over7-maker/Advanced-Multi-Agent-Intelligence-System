#!/usr/bin/env python3
"""
AI Learning & Adaptation - Advanced Multi-Agent Learning System
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

class AILearningAdaptation:
    """Advanced AI-powered learning and adaptation system with multi-agent intelligence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'learning_type': 'learning_adaptation',
            'mode': config.get('mode', 'intelligent'),
            'areas': config.get('areas', 'all'),
            'depth': config.get('depth', 'deep'),
            'auto_apply': config.get('auto_apply', False),
            'learning_insights': [],
            'adaptation_strategies': [],
            'performance_metrics': {},
            'improvement_recommendations': [],
            'knowledge_base_updates': [],
            'model_adaptations': [],
            'status': 'success'
        }
        
    def load_all_results(self, results_path: str) -> Dict[str, Any]:
        """Load all results from previous phases"""
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
    
    def analyze_learning_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze learning patterns from all phases"""
        logger.info("🧠 Analyzing learning patterns...")
        
        insights = []
        
        try:
            # Analyze project evolution
            project_evolution = self._analyze_project_evolution(all_results)
            if project_evolution:
                insights.append(project_evolution)
            
            # Analyze improvement effectiveness
            improvement_effectiveness = self._analyze_improvement_effectiveness(all_results)
            if improvement_effectiveness:
                insights.append(improvement_effectiveness)
            
            # Analyze implementation success
            implementation_success = self._analyze_implementation_success(all_results)
            if implementation_success:
                insights.append(implementation_success)
            
            # Analyze performance trends
            performance_trends = self._analyze_performance_trends(all_results)
            if performance_trends:
                insights.append(performance_trends)
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
        
        return insights
    
    def generate_adaptation_strategies(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate adaptation strategies based on insights"""
        logger.info("🎯 Generating adaptation strategies...")
        
        strategies = []
        
        try:
            # Generate strategies based on insights
            for insight in insights:
                strategy = self._generate_strategy_from_insight(insight)
                if strategy:
                    strategies.append(strategy)
            
            # Generate general adaptation strategies
            strategies.extend(self._generate_general_adaptation_strategies(insights))
            
        except Exception as e:
            logger.error(f"Error generating adaptation strategies: {e}")
        
        return strategies
    
    def update_knowledge_base(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update knowledge base with new learnings"""
        logger.info("📚 Updating knowledge base...")
        
        updates = []
        
        try:
            # Extract key learnings from each phase
            for phase_name, phase_results in all_results.items():
                learning = self._extract_phase_learning(phase_name, phase_results)
                if learning:
                    updates.append(learning)
            
            # Update knowledge base files
            self._update_knowledge_files(updates)
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
        
        return updates
    
    def adapt_models(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adapt AI models based on learnings"""
        logger.info("🤖 Adapting AI models...")
        
        adaptations = []
        
        try:
            # Adapt based on performance patterns
            performance_adaptations = self._adapt_performance_models(insights)
            adaptations.extend(performance_adaptations)
            
            # Adapt based on error patterns
            error_adaptations = self._adapt_error_models(insights)
            adaptations.extend(error_adaptations)
            
            # Adapt based on success patterns
            success_adaptations = self._adapt_success_models(insights)
            adaptations.extend(success_adaptations)
            
        except Exception as e:
            logger.error(f"Error adapting models: {e}")
        
        return adaptations
    
    def generate_improvement_recommendations(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations for future cycles"""
        logger.info("💡 Generating improvement recommendations...")
        
        recommendations = []
        
        try:
            # Analyze what worked well
            successful_patterns = self._identify_successful_patterns(all_results)
            for pattern in successful_patterns:
                recommendations.append({
                    'type': 'continue_successful',
                    'title': f'Continue {pattern["type"]} approach',
                    'description': pattern['description'],
                    'priority': 'high',
                    'impact': 'high',
                    'effort': 'low'
                })
            
            # Analyze what needs improvement
            improvement_areas = self._identify_improvement_areas(all_results)
            for area in improvement_areas:
                recommendations.append({
                    'type': 'improve_area',
                    'title': f'Improve {area["type"]} process',
                    'description': area['description'],
                    'priority': 'medium',
                    'impact': 'medium',
                    'effort': 'medium'
                })
            
            # Generate new approaches
            new_approaches = self._generate_new_approaches(all_results)
            for approach in new_approaches:
                recommendations.append({
                    'type': 'new_approach',
                    'title': f'Try {approach["type"]} approach',
                    'description': approach['description'],
                    'priority': 'low',
                    'impact': 'unknown',
                    'effort': 'high'
                })
            
        except Exception as e:
            logger.error(f"Error generating improvement recommendations: {e}")
        
        return recommendations
    
    def _analyze_project_evolution(self, all_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze how the project has evolved"""
        evolution_metrics = {
            'files_created': 0,
            'files_modified': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'complexity_changes': [],
            'quality_improvements': []
        }
        
        try:
            # Aggregate metrics from all phases
            for phase_name, phase_results in all_results.items():
                if 'files_created' in phase_results:
                    evolution_metrics['files_created'] += len(phase_results['files_created'])
                if 'files_modified' in phase_results:
                    evolution_metrics['files_modified'] += len(phase_results['files_modified'])
                
                # Analyze complexity changes
                if 'structure' in phase_results:
                    complexity = phase_results['structure'].get('complexity_score', 0)
                    evolution_metrics['complexity_changes'].append({
                        'phase': phase_name,
                        'complexity': complexity
                    })
            
            return {
                'type': 'project_evolution',
                'title': 'Project Evolution Analysis',
                'description': 'Analysis of how the project has evolved through different phases',
                'metrics': evolution_metrics,
                'insights': [
                    f"Created {evolution_metrics['files_created']} new files",
                    f"Modified {evolution_metrics['files_modified']} existing files",
                    f"Complexity changes: {len(evolution_metrics['complexity_changes'])} phases"
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing project evolution: {e}")
            return None
    
    def _analyze_improvement_effectiveness(self, all_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze effectiveness of improvements"""
        effectiveness_metrics = {
            'total_improvements': 0,
            'implemented_improvements': 0,
            'successful_implementations': 0,
            'improvement_categories': {}
        }
        
        try:
            # Analyze improvement generation and implementation
            for phase_name, phase_results in all_results.items():
                if 'improvements' in phase_results:
                    improvements = phase_results['improvements']
                    effectiveness_metrics['total_improvements'] += len(improvements)
                    
                    # Categorize improvements
                    for improvement in improvements:
                        category = improvement.get('type', 'unknown')
                        effectiveness_metrics['improvement_categories'][category] = \
                            effectiveness_metrics['improvement_categories'].get(category, 0) + 1
                
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    effectiveness_metrics['implemented_improvements'] += len(implementations)
                    
                    # Count successful implementations
                    successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                    effectiveness_metrics['successful_implementations'] += successful
            
            # Calculate effectiveness rate
            if effectiveness_metrics['total_improvements'] > 0:
                effectiveness_rate = (effectiveness_metrics['implemented_improvements'] / 
                                    effectiveness_metrics['total_improvements'] * 100)
            else:
                effectiveness_rate = 0
            
            return {
                'type': 'improvement_effectiveness',
                'title': 'Improvement Effectiveness Analysis',
                'description': 'Analysis of how effective the improvement generation and implementation process was',
                'metrics': effectiveness_metrics,
                'effectiveness_rate': effectiveness_rate,
                'insights': [
                    f"Generated {effectiveness_metrics['total_improvements']} improvements",
                    f"Implemented {effectiveness_metrics['implemented_improvements']} improvements",
                    f"Effectiveness rate: {effectiveness_rate:.1f}%"
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing improvement effectiveness: {e}")
            return None
    
    def _analyze_implementation_success(self, all_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze implementation success patterns"""
        success_metrics = {
            'total_implementations': 0,
            'successful_implementations': 0,
            'failed_implementations': 0,
            'implementation_types': {},
            'common_failure_reasons': []
        }
        
        try:
            # Analyze implementation results
            for phase_name, phase_results in all_results.items():
                if 'implementations' in phase_results:
                    implementations = phase_results['implementations']
                    success_metrics['total_implementations'] += len(implementations)
                    
                    for implementation in implementations:
                        impl_type = implementation.get('type', 'unknown')
                        success_metrics['implementation_types'][impl_type] = \
                            success_metrics['implementation_types'].get(impl_type, 0) + 1
                        
                        if implementation.get('status') == 'success':
                            success_metrics['successful_implementations'] += 1
                        else:
                            success_metrics['failed_implementations'] += 1
                            if 'error' in implementation:
                                success_metrics['common_failure_reasons'].append(implementation['error'])
            
            # Calculate success rate
            if success_metrics['total_implementations'] > 0:
                success_rate = (success_metrics['successful_implementations'] / 
                              success_metrics['total_implementations'] * 100)
            else:
                success_rate = 0
            
            return {
                'type': 'implementation_success',
                'title': 'Implementation Success Analysis',
                'description': 'Analysis of implementation success patterns and failure reasons',
                'metrics': success_metrics,
                'success_rate': success_rate,
                'insights': [
                    f"Success rate: {success_rate:.1f}%",
                    f"Most common implementation type: {max(success_metrics['implementation_types'].items(), key=lambda x: x[1])[0] if success_metrics['implementation_types'] else 'none'}",
                    f"Failed implementations: {success_metrics['failed_implementations']}"
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing implementation success: {e}")
            return None
    
    def _analyze_performance_trends(self, all_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze performance trends across phases"""
        performance_metrics = {
            'security_scores': [],
            'performance_scores': [],
            'quality_scores': [],
            'complexity_scores': []
        }
        
        try:
            # Collect performance metrics from all phases
            for phase_name, phase_results in all_results.items():
                if 'security' in phase_results:
                    security_score = phase_results['security'].get('security_score', 0)
                    performance_metrics['security_scores'].append({
                        'phase': phase_name,
                        'score': security_score
                    })
                
                if 'performance' in phase_results:
                    perf_score = phase_results['performance'].get('performance_score', 0)
                    performance_metrics['performance_scores'].append({
                        'phase': phase_name,
                        'score': perf_score
                    })
                
                if 'code_quality' in phase_results:
                    quality_score = phase_results['code_quality'].get('maintainability_index', 0)
                    performance_metrics['quality_scores'].append({
                        'phase': phase_name,
                        'score': quality_score
                    })
                
                if 'structure' in phase_results:
                    complexity_score = phase_results['structure'].get('complexity_score', 0)
                    performance_metrics['complexity_scores'].append({
                        'phase': phase_name,
                        'score': complexity_score
                    })
            
            # Calculate trends
            trends = self._calculate_performance_trends(performance_metrics)
            
            return {
                'type': 'performance_trends',
                'title': 'Performance Trends Analysis',
                'description': 'Analysis of performance trends across different phases',
                'metrics': performance_metrics,
                'trends': trends,
                'insights': [
                    f"Security trend: {trends.get('security', 'stable')}",
                    f"Performance trend: {trends.get('performance', 'stable')}",
                    f"Quality trend: {trends.get('quality', 'stable')}",
                    f"Complexity trend: {trends.get('complexity', 'stable')}"
                ]
            }
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return None
    
    def _calculate_performance_trends(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Calculate performance trends"""
        trends = {}
        
        for metric_name, scores in metrics.items():
            if len(scores) >= 2:
                first_score = scores[0]['score']
                last_score = scores[-1]['score']
                
                if last_score > first_score * 1.1:
                    trends[metric_name.replace('_scores', '')] = 'improving'
                elif last_score < first_score * 0.9:
                    trends[metric_name.replace('_scores', '')] = 'declining'
                else:
                    trends[metric_name.replace('_scores', '')] = 'stable'
            else:
                trends[metric_name.replace('_scores', '')] = 'insufficient_data'
        
        return trends
    
    def _generate_strategy_from_insight(self, insight: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate adaptation strategy from insight"""
        insight_type = insight.get('type', '')
        
        if insight_type == 'project_evolution':
            return {
                'type': 'evolution_strategy',
                'title': 'Adapt to Project Evolution',
                'description': 'Adjust processes based on project evolution patterns',
                'priority': 'medium',
                'actions': [
                    'Monitor file creation patterns',
                    'Adjust complexity thresholds',
                    'Optimize for project size'
                ]
            }
        elif insight_type == 'improvement_effectiveness':
            return {
                'type': 'effectiveness_strategy',
                'title': 'Improve Effectiveness',
                'description': 'Focus on improving improvement generation and implementation effectiveness',
                'priority': 'high',
                'actions': [
                    'Refine improvement generation algorithms',
                    'Improve implementation success rates',
                    'Better categorize improvements'
                ]
            }
        elif insight_type == 'implementation_success':
            return {
                'type': 'success_strategy',
                'title': 'Improve Implementation Success',
                'description': 'Focus on improving implementation success rates',
                'priority': 'high',
                'actions': [
                    'Address common failure reasons',
                    'Improve error handling',
                    'Add more validation'
                ]
            }
        elif insight_type == 'performance_trends':
            return {
                'type': 'performance_strategy',
                'title': 'Optimize Performance Trends',
                'description': 'Focus on improving performance trends',
                'priority': 'medium',
                'actions': [
                    'Focus on declining metrics',
                    'Maintain improving metrics',
                    'Set performance targets'
                ]
            }
        
        return None
    
    def _generate_general_adaptation_strategies(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate general adaptation strategies"""
        strategies = []
        
        # Add general strategies based on insights
        if len(insights) > 0:
            strategies.append({
                'type': 'general_adaptation',
                'title': 'Continuous Learning',
                'description': 'Implement continuous learning mechanisms',
                'priority': 'high',
                'actions': [
                    'Update knowledge base regularly',
                    'Adapt models based on results',
                    'Refine processes continuously'
                ]
            })
        
        return strategies
    
    def _extract_phase_learning(self, phase_name: str, phase_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract key learning from a phase"""
        learning = {
            'phase': phase_name,
            'timestamp': phase_results.get('timestamp', ''),
            'key_insights': [],
            'success_factors': [],
            'failure_factors': []
        }
        
        try:
            # Extract insights based on phase type
            if 'analysis' in phase_name:
                learning['key_insights'].append('Analysis phase completed')
                if 'metrics' in phase_results:
                    learning['key_insights'].append(f"Analyzed {phase_results['metrics'].get('total_files', 0)} files")
            
            elif 'improvement' in phase_name:
                learning['key_insights'].append('Improvement generation completed')
                if 'improvements' in phase_results:
                    learning['key_insights'].append(f"Generated {len(phase_results['improvements'])} improvements")
            
            elif 'implementation' in phase_name:
                learning['key_insights'].append('Implementation phase completed')
                if 'implementations' in phase_results:
                    successful = sum(1 for impl in phase_results['implementations'] if impl.get('status') == 'success')
                    learning['key_insights'].append(f"Successfully implemented {successful} changes")
            
        except Exception as e:
            logger.error(f"Error extracting phase learning: {e}")
            return None
        
        return learning
    
    def _update_knowledge_files(self, updates: List[Dict[str, Any]]):
        """Update knowledge base files"""
        try:
            # Create knowledge base directory
            kb_dir = Path('knowledge_base')
            kb_dir.mkdir(exist_ok=True)
            
            # Update learning history
            learning_file = kb_dir / 'learning_history.json'
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.extend(updates)
            
            with open(learning_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Update patterns file
            patterns_file = kb_dir / 'patterns.json'
            patterns = self._extract_patterns(updates)
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error updating knowledge files: {e}")
    
    def _extract_patterns(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from updates"""
        patterns = {
            'successful_phases': [],
            'common_insights': [],
            'frequent_issues': []
        }
        
        # Analyze patterns (simplified)
        for update in updates:
            if update.get('phase'):
                patterns['successful_phases'].append(update['phase'])
            
            if 'key_insights' in update:
                patterns['common_insights'].extend(update['key_insights'])
        
        return patterns
    
    def _adapt_performance_models(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adapt models based on performance insights"""
        adaptations = []
        
        for insight in insights:
            if insight.get('type') == 'performance_trends':
                trends = insight.get('trends', {})
                
                for metric, trend in trends.items():
                    if trend == 'declining':
                        adaptations.append({
                            'type': 'performance_model_adaptation',
                            'metric': metric,
                            'action': 'increase_focus',
                            'description': f'Increase focus on {metric} due to declining trend'
                        })
                    elif trend == 'improving':
                        adaptations.append({
                            'type': 'performance_model_adaptation',
                            'metric': metric,
                            'action': 'maintain_focus',
                            'description': f'Maintain focus on {metric} due to improving trend'
                        })
        
        return adaptations
    
    def _adapt_error_models(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adapt models based on error patterns"""
        adaptations = []
        
        for insight in insights:
            if insight.get('type') == 'implementation_success':
                metrics = insight.get('metrics', {})
                failure_reasons = metrics.get('common_failure_reasons', [])
                
                if failure_reasons:
                    adaptations.append({
                        'type': 'error_model_adaptation',
                        'action': 'improve_error_handling',
                        'description': 'Improve error handling based on common failure reasons',
                        'failure_reasons': failure_reasons
                    })
        
        return adaptations
    
    def _adapt_success_models(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adapt models based on success patterns"""
        adaptations = []
        
        for insight in insights:
            if insight.get('type') == 'improvement_effectiveness':
                effectiveness_rate = insight.get('effectiveness_rate', 0)
                
                if effectiveness_rate > 80:
                    adaptations.append({
                        'type': 'success_model_adaptation',
                        'action': 'maintain_approach',
                        'description': 'Maintain current approach due to high effectiveness'
                    })
                elif effectiveness_rate < 50:
                    adaptations.append({
                        'type': 'success_model_adaptation',
                        'action': 'revise_approach',
                        'description': 'Revise approach due to low effectiveness'
                    })
        
        return adaptations
    
    def _identify_successful_patterns(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify successful patterns"""
        patterns = []
        
        # Look for high success rates
        for phase_name, phase_results in all_results.items():
            if 'implementations' in phase_results:
                implementations = phase_results['implementations']
                if implementations:
                    successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                    success_rate = successful / len(implementations) * 100
                    
                    if success_rate > 80:
                        patterns.append({
                            'type': 'high_success_rate',
                            'phase': phase_name,
                            'success_rate': success_rate,
                            'description': f'Phase {phase_name} had {success_rate:.1f}% success rate'
                        })
        
        return patterns
    
    def _identify_improvement_areas(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify areas that need improvement"""
        areas = []
        
        # Look for low success rates
        for phase_name, phase_results in all_results.items():
            if 'implementations' in phase_results:
                implementations = phase_results['implementations']
                if implementations:
                    successful = sum(1 for impl in implementations if impl.get('status') == 'success')
                    success_rate = successful / len(implementations) * 100
                    
                    if success_rate < 50:
                        areas.append({
                            'type': 'low_success_rate',
                            'phase': phase_name,
                            'success_rate': success_rate,
                            'description': f'Phase {phase_name} had {success_rate:.1f}% success rate - needs improvement'
                        })
        
        return areas
    
    def _generate_new_approaches(self, all_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate new approaches to try"""
        approaches = []
        
        # Suggest new approaches based on analysis
        approaches.append({
            'type': 'machine_learning',
            'description': 'Implement machine learning for better pattern recognition'
        })
        
        approaches.append({
            'type': 'parallel_processing',
            'description': 'Use parallel processing for faster analysis'
        })
        
        approaches.append({
            'type': 'advanced_ai',
            'description': 'Integrate more advanced AI models for better insights'
        })
        
        return approaches
    
    def run_learning_adaptation(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete learning and adaptation process"""
        logger.info("🧠 Starting learning and adaptation...")
        
        try:
            # Analyze learning patterns
            insights = self.analyze_learning_patterns(all_results)
            self.results['learning_insights'] = insights
            
            # Generate adaptation strategies
            strategies = self.generate_adaptation_strategies(insights)
            self.results['adaptation_strategies'] = strategies
            
            # Update knowledge base
            knowledge_updates = self.update_knowledge_base(all_results)
            self.results['knowledge_base_updates'] = knowledge_updates
            
            # Adapt models
            model_adaptations = self.adapt_models(insights)
            self.results['model_adaptations'] = model_adaptations
            
            # Generate improvement recommendations
            recommendations = self.generate_improvement_recommendations(all_results)
            self.results['improvement_recommendations'] = recommendations
            
            # Calculate performance metrics
            self.results['performance_metrics'] = self._calculate_learning_metrics()
            
            logger.info("✅ Learning and adaptation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during learning and adaptation: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return self.results
    
    def _calculate_learning_metrics(self) -> Dict[str, Any]:
        """Calculate learning and adaptation metrics"""
        metrics = {
            'total_insights': len(self.results.get('learning_insights', [])),
            'total_strategies': len(self.results.get('adaptation_strategies', [])),
            'knowledge_updates': len(self.results.get('knowledge_base_updates', [])),
            'model_adaptations': len(self.results.get('model_adaptations', [])),
            'recommendations': len(self.results.get('improvement_recommendations', []))
        }
        
        return metrics

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Learning & Adaptation')
    parser.add_argument('--mode', default='intelligent', help='Learning mode')
    parser.add_argument('--areas', default='all', help='Target areas for learning')
    parser.add_argument('--depth', default='deep', help='Learning depth')
    parser.add_argument('--auto-apply', action='store_true', help='Auto-apply adaptations')
    parser.add_argument('--all-results', default='all_results/', help='Path to all results')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='learning_adaptation_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'mode': args.mode,
        'areas': args.areas,
        'depth': args.depth,
        'auto_apply': args.auto_apply,
        'use_advanced_manager': args.use_advanced_manager
    }
    
    # Initialize learning system
    learning_system = AILearningAdaptation(config)
    
    # Load all results
    all_results = learning_system.load_all_results(args.all_results)
    
    # Run learning and adaptation
    results = learning_system.run_learning_adaptation(all_results)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Learning and adaptation results saved to {args.output}")
    
    return 0 if results['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())