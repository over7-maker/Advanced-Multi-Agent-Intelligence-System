#!/usr/bin/env python3
"""
AI Issue Analyzer - Advanced Multi-Agent Issue Analysis System
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
import re

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIIssueAnalyzer:
    """Advanced AI-powered issue analyzer with multi-agent intelligence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'issue_analysis',
            'mode': config.get('mode', 'intelligent'),
            'depth': config.get('depth', 'comprehensive'),
            'language': config.get('language', 'auto'),
            'auto_fix': config.get('auto_fix', False),
            'target_issues': config.get('target_issues', 'all'),
            'issues_analyzed': [],
            'categorizations': [],
            'priority_assessments': [],
            'complexity_analysis': [],
            'similar_issues': [],
            'recommendations': [],
            'status': 'success'
        }
        
    def analyze_issues(self) -> List[Dict[str, Any]]:
        """Analyze GitHub issues"""
        logger.info("🔍 Starting issue analysis...")
        
        issues = []
        
        try:
            # Get issues from GitHub API or local data
            issues = self._get_issues()
            
            for issue in issues:
                analysis = self._analyze_single_issue(issue)
                if analysis:
                    self.results['issues_analyzed'].append(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing issues: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return issues
    
    def _get_issues(self) -> List[Dict[str, Any]]:
        """Get issues to analyze"""
        # In a real implementation, this would fetch from GitHub API
        # For now, we'll create sample issues for demonstration
        
        sample_issues = [
            {
                'number': 1,
                'title': 'Bug: Application crashes on startup',
                'body': 'The application crashes immediately when I try to start it. This happens on both Windows and Mac.',
                'labels': ['bug'],
                'state': 'open',
                'created_at': '2024-01-01T10:00:00Z',
                'updated_at': '2024-01-01T10:00:00Z',
                'user': {'login': 'testuser1'},
                'comments': 0
            },
            {
                'number': 2,
                'title': 'Feature: Add dark mode support',
                'body': 'It would be great to have a dark mode option in the application. This would help users who prefer dark interfaces.',
                'labels': ['enhancement'],
                'state': 'open',
                'created_at': '2024-01-02T10:00:00Z',
                'updated_at': '2024-01-02T10:00:00Z',
                'user': {'login': 'testuser2'},
                'comments': 2
            },
            {
                'number': 3,
                'title': 'Question: How to configure the API?',
                'body': 'I need help configuring the API settings. Can someone provide documentation or examples?',
                'labels': ['question'],
                'state': 'open',
                'created_at': '2024-01-03T10:00:00Z',
                'updated_at': '2024-01-03T10:00:00Z',
                'user': {'login': 'testuser3'},
                'comments': 1
            }
        ]
        
        return sample_issues
    
    def _analyze_single_issue(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single issue"""
        try:
            analysis = {
                'issue_number': issue.get('number'),
                'title': issue.get('title'),
                'categorization': self._categorize_issue(issue),
                'priority': self._assess_priority(issue),
                'complexity': self._analyze_complexity(issue),
                'similar_issues': self._find_similar_issues(issue),
                'recommendations': self._generate_recommendations(issue),
                'language_detection': self._detect_language(issue),
                'sentiment_analysis': self._analyze_sentiment(issue),
                'urgency_score': self._calculate_urgency_score(issue)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing issue {issue.get('number')}: {e}")
            return None
    
    def _categorize_issue(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize the issue"""
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        
        # Define categorization patterns
        bug_patterns = ['bug', 'error', 'crash', 'broken', 'fix', 'issue', 'problem']
        feature_patterns = ['feature', 'enhancement', 'add', 'new', 'improve', 'request']
        question_patterns = ['question', 'help', 'how', 'what', 'why', 'documentation']
        security_patterns = ['security', 'vulnerability', 'exploit', 'attack', 'breach']
        performance_patterns = ['performance', 'slow', 'fast', 'optimize', 'speed']
        
        # Analyze content
        content = f"{title} {body}"
        
        category_scores = {
            'bug': sum(1 for pattern in bug_patterns if pattern in content),
            'feature': sum(1 for pattern in feature_patterns if pattern in content),
            'question': sum(1 for pattern in question_patterns if pattern in content),
            'security': sum(1 for pattern in security_patterns if pattern in content),
            'performance': sum(1 for pattern in performance_patterns if pattern in content)
        }
        
        # Check labels
        for label in labels:
            if label in bug_patterns:
                category_scores['bug'] += 2
            elif label in feature_patterns:
                category_scores['feature'] += 2
            elif label in question_patterns:
                category_scores['question'] += 2
            elif label in security_patterns:
                category_scores['security'] += 2
            elif label in performance_patterns:
                category_scores['performance'] += 2
        
        # Determine primary category
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        confidence = category_scores[primary_category] / max(sum(category_scores.values()), 1)
        
        return {
            'primary_category': primary_category,
            'confidence': confidence,
            'category_scores': category_scores,
            'labels': labels
        }
    
    def _assess_priority(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Assess issue priority"""
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        
        priority_score = 0
        
        # High priority indicators
        high_priority_keywords = ['critical', 'urgent', 'blocking', 'crash', 'security', 'data loss']
        for keyword in high_priority_keywords:
            if keyword in title or keyword in body:
                priority_score += 3
        
        # Medium priority indicators
        medium_priority_keywords = ['important', 'bug', 'issue', 'problem']
        for keyword in medium_priority_keywords:
            if keyword in title or keyword in body:
                priority_score += 2
        
        # Low priority indicators
        low_priority_keywords = ['enhancement', 'feature', 'nice to have', 'improvement']
        for keyword in low_priority_keywords:
            if keyword in title or keyword in body:
                priority_score += 1
        
        # Check labels
        if 'critical' in labels or 'urgent' in labels:
            priority_score += 5
        elif 'high' in labels:
            priority_score += 4
        elif 'medium' in labels:
            priority_score += 3
        elif 'low' in labels:
            priority_score += 2
        
        # Determine priority level
        if priority_score >= 8:
            priority_level = 'critical'
        elif priority_score >= 5:
            priority_level = 'high'
        elif priority_score >= 3:
            priority_level = 'medium'
        else:
            priority_level = 'low'
        
        return {
            'level': priority_level,
            'score': priority_score,
            'reasoning': f"Priority determined based on keywords and labels (score: {priority_score})"
        }
    
    def _analyze_complexity(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze issue complexity"""
        title = issue.get('title', '')
        body = issue.get('body', '')
        
        # Calculate complexity metrics
        word_count = len(body.split())
        char_count = len(body)
        line_count = len(body.split('\n'))
        
        # Check for technical terms
        technical_terms = ['api', 'database', 'algorithm', 'architecture', 'integration', 'performance', 'security']
        technical_count = sum(1 for term in technical_terms if term in body.lower())
        
        # Check for code snippets
        code_blocks = len(re.findall(r'```[\s\S]*?```', body))
        
        # Check for multiple requirements
        requirement_indicators = ['also', 'additionally', 'furthermore', 'moreover', 'and', 'plus']
        requirement_count = sum(1 for indicator in requirement_indicators if indicator in body.lower())
        
        # Calculate complexity score
        complexity_score = 0
        complexity_score += min(word_count / 100, 3)  # Word count factor
        complexity_score += min(technical_count, 3)   # Technical terms factor
        complexity_score += min(code_blocks, 2)       # Code blocks factor
        complexity_score += min(requirement_count, 2) # Multiple requirements factor
        
        # Determine complexity level
        if complexity_score >= 6:
            complexity_level = 'high'
        elif complexity_score >= 3:
            complexity_level = 'medium'
        else:
            complexity_level = 'low'
        
        return {
            'level': complexity_level,
            'score': complexity_score,
            'metrics': {
                'word_count': word_count,
                'char_count': char_count,
                'line_count': line_count,
                'technical_terms': technical_count,
                'code_blocks': code_blocks,
                'requirement_count': requirement_count
            }
        }
    
    def _find_similar_issues(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar issues"""
        # This is a simplified implementation
        # In reality, this would use more sophisticated similarity algorithms
        
        similar_issues = []
        
        # Simple keyword-based similarity
        title_words = set(issue.get('title', '').lower().split())
        body_words = set(issue.get('body', '').lower().split())
        
        # This would typically search through a database of issues
        # For now, we'll return empty results
        
        return similar_issues
    
    def _generate_recommendations(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for the issue"""
        recommendations = []
        
        categorization = self._categorize_issue(issue)
        priority = self._assess_priority(issue)
        complexity = self._analyze_complexity(issue)
        
        # Generate recommendations based on analysis
        if categorization['primary_category'] == 'bug':
            recommendations.append({
                'type': 'immediate_action',
                'title': 'Investigate and reproduce the bug',
                'description': 'Set up debugging environment to reproduce the issue',
                'priority': 'high'
            })
            
            if priority['level'] in ['critical', 'high']:
                recommendations.append({
                    'type': 'urgent_response',
                    'title': 'Assign to senior developer',
                    'description': 'High priority bug should be handled by experienced developer',
                    'priority': 'critical'
                })
        
        elif categorization['primary_category'] == 'feature':
            recommendations.append({
                'type': 'planning',
                'title': 'Create feature specification',
                'description': 'Document detailed requirements and acceptance criteria',
                'priority': 'medium'
            })
            
            if complexity['level'] == 'high':
                recommendations.append({
                    'type': 'architecture_review',
                    'title': 'Conduct architecture review',
                    'description': 'Complex feature requires architectural planning',
                    'priority': 'high'
                })
        
        elif categorization['primary_category'] == 'question':
            recommendations.append({
                'type': 'documentation',
                'title': 'Provide comprehensive answer',
                'description': 'Create detailed response with examples and documentation links',
                'priority': 'medium'
            })
        
        elif categorization['primary_category'] == 'security':
            recommendations.append({
                'type': 'immediate_action',
                'title': 'Security assessment required',
                'description': 'Conduct immediate security assessment and mitigation',
                'priority': 'critical'
            })
        
        # Add general recommendations
        recommendations.append({
            'type': 'communication',
            'title': 'Acknowledge the issue',
            'description': 'Respond to the issue author within 24 hours',
            'priority': 'medium'
        })
        
        return recommendations
    
    def _detect_language(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Detect the language of the issue"""
        content = f"{issue.get('title', '')} {issue.get('body', '')}"
        
        # Simple language detection based on common words
        # In reality, this would use proper language detection libraries
        
        english_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le']
        french_indicators = ['le', 'la', 'de', 'et', 'à', 'un', 'il', 'que', 'ne', 'se', 'ce', 'pas', 'tout']
        
        english_count = sum(1 for word in english_indicators if word in content.lower())
        spanish_count = sum(1 for word in spanish_indicators if word in content.lower())
        french_count = sum(1 for word in french_indicators if word in content.lower())
        
        if english_count > spanish_count and english_count > french_count:
            detected_language = 'english'
            confidence = english_count / max(len(content.split()), 1)
        elif spanish_count > french_count:
            detected_language = 'spanish'
            confidence = spanish_count / max(len(content.split()), 1)
        elif french_count > 0:
            detected_language = 'french'
            confidence = french_count / max(len(content.split()), 1)
        else:
            detected_language = 'unknown'
            confidence = 0
        
        return {
            'language': detected_language,
            'confidence': confidence,
            'indicators': {
                'english': english_count,
                'spanish': spanish_count,
                'french': french_count
            }
        }
    
    def _analyze_sentiment(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of the issue"""
        content = f"{issue.get('title', '')} {issue.get('body', '')}"
        
        # Simple sentiment analysis based on keywords
        positive_words = ['great', 'excellent', 'good', 'nice', 'awesome', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating', 'annoying', 'broken']
        neutral_words = ['okay', 'fine', 'normal', 'standard', 'regular', 'typical']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        neutral_count = sum(1 for word in neutral_words if word in content.lower())
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0
        elif positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_count / total_sentiment_words
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = negative_count / total_sentiment_words
        else:
            sentiment = 'neutral'
            confidence = neutral_count / total_sentiment_words
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            }
        }
    
    def _calculate_urgency_score(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate urgency score for the issue"""
        urgency_score = 0
        
        # Time-based urgency
        created_at = issue.get('created_at', '')
        if created_at:
            try:
                from datetime import datetime
                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_time).days
                
                if days_old > 30:
                    urgency_score += 3
                elif days_old > 7:
                    urgency_score += 2
                elif days_old > 1:
                    urgency_score += 1
            except Exception:
                pass
        
        # Comment activity
        comments = issue.get('comments', 0)
        if comments > 10:
            urgency_score += 3
        elif comments > 5:
            urgency_score += 2
        elif comments > 0:
            urgency_score += 1
        
        # Label-based urgency
        labels = [label.get('name', '').lower() for label in issue.get('labels', [])]
        if 'urgent' in labels or 'critical' in labels:
            urgency_score += 5
        elif 'high' in labels:
            urgency_score += 3
        elif 'blocking' in labels:
            urgency_score += 4
        
        # Content-based urgency
        content = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
        urgent_keywords = ['urgent', 'critical', 'asap', 'immediately', 'blocking', 'broken', 'crash']
        for keyword in urgent_keywords:
            if keyword in content:
                urgency_score += 2
        
        # Determine urgency level
        if urgency_score >= 8:
            urgency_level = 'critical'
        elif urgency_score >= 5:
            urgency_level = 'high'
        elif urgency_score >= 3:
            urgency_level = 'medium'
        else:
            urgency_level = 'low'
        
        return {
            'level': urgency_level,
            'score': urgency_score,
            'factors': {
                'age': days_old if 'days_old' in locals() else 0,
                'comments': comments,
                'labels': labels,
                'keywords': sum(1 for keyword in urgent_keywords if keyword in content)
            }
        }
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete issue analysis"""
        logger.info("🚀 Starting AI Issue Analysis...")
        
        try:
            # Analyze issues
            issues = self.analyze_issues()
            
            # Generate summary statistics
            self.results['summary'] = self._generate_summary()
            
            # Generate insights
            self.results['insights'] = self._generate_insights()
            
            logger.info("✅ Issue analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return self.results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate analysis summary"""
        total_issues = len(self.results['issues_analyzed'])
        
        if total_issues == 0:
            return {
                'total_issues': 0,
                'categories': {},
                'priorities': {},
                'complexities': {},
                'languages': {},
                'sentiments': {}
            }
        
        # Count by category
        categories = {}
        priorities = {}
        complexities = {}
        languages = {}
        sentiments = {}
        
        for analysis in self.results['issues_analyzed']:
            # Category
            cat = analysis['categorization']['primary_category']
            categories[cat] = categories.get(cat, 0) + 1
            
            # Priority
            pri = analysis['priority']['level']
            priorities[pri] = priorities.get(pri, 0) + 1
            
            # Complexity
            comp = analysis['complexity']['level']
            complexities[comp] = complexities.get(comp, 0) + 1
            
            # Language
            lang = analysis['language_detection']['language']
            languages[lang] = languages.get(lang, 0) + 1
            
            # Sentiment
            sent = analysis['sentiment_analysis']['sentiment']
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        return {
            'total_issues': total_issues,
            'categories': categories,
            'priorities': priorities,
            'complexities': complexities,
            'languages': languages,
            'sentiments': sentiments
        }
    
    def _generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from the analysis"""
        insights = []
        
        summary = self.results.get('summary', {})
        
        # Category insights
        categories = summary.get('categories', {})
        if categories:
            most_common_category = max(categories.items(), key=lambda x: x[1])
            insights.append({
                'type': 'category_insight',
                'title': f'Most Common Issue Type: {most_common_category[0]}',
                'description': f'{most_common_category[1]} issues are {most_common_category[0]}s',
                'recommendation': f'Focus on improving {most_common_category[0]} handling processes'
            })
        
        # Priority insights
        priorities = summary.get('priorities', {})
        if priorities:
            critical_high = priorities.get('critical', 0) + priorities.get('high', 0)
            total = sum(priorities.values())
            if critical_high > total * 0.3:
                insights.append({
                    'type': 'priority_insight',
                    'title': 'High Priority Issue Volume',
                    'description': f'{critical_high} out of {total} issues are high/critical priority',
                    'recommendation': 'Consider increasing development resources for high-priority issues'
                })
        
        # Language insights
        languages = summary.get('languages', {})
        if languages and len(languages) > 1:
            insights.append({
                'type': 'language_insight',
                'title': 'Multi-language Support Needed',
                'description': f'Issues submitted in {len(languages)} different languages',
                'recommendation': 'Consider providing multi-language support for issue responses'
            })
        
        return insights

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Issue Analyzer')
    parser.add_argument('--mode', default='intelligent', help='Analysis mode')
    parser.add_argument('--depth', default='comprehensive', help='Analysis depth')
    parser.add_argument('--language', default='auto', help='Response language preference')
    parser.add_argument('--auto-fix', action='store_true', help='Auto-fix issues when possible')
    parser.add_argument('--target-issues', default='all', help='Target issues to analyze')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='issue_analysis_results.json', help='Output file')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'mode': args.mode,
        'depth': args.depth,
        'language': args.language,
        'auto_fix': args.auto_fix,
        'target_issues': args.target_issues,
        'use_advanced_manager': args.use_advanced_manager
    }
    
    # Initialize analyzer
    analyzer = AIIssueAnalyzer(config)
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Issue analysis results saved to {args.output}")
    
    return 0 if results['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())