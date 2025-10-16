#!/usr/bin/env python3
"""
AI Response Generator - Advanced Multi-Agent Response Generation System
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

class AIResponseGenerator:
    """Advanced AI-powered response generator with multi-agent intelligence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'generation_type': 'response_generation',
            'mode': config.get('mode', 'intelligent'),
            'depth': config.get('depth', 'comprehensive'),
            'language': config.get('language', 'auto'),
            'auto_fix': config.get('auto_fix', False),
            'target_issues': config.get('target_issues', 'all'),
            'responses_generated': [],
            'response_templates': [],
            'personalization_data': [],
            'context_analysis': [],
            'status': 'success'
        }
        
    def load_analysis_results(self, analysis_path: str) -> Dict[str, Any]:
        """Load analysis results from previous phase"""
        logger.info(f"📥 Loading analysis results from {analysis_path}")
        
        try:
            if os.path.isdir(analysis_path):
                # Look for analysis results in directory
                for file_path in Path(analysis_path).glob('*analysis*results*.json'):
                    with open(file_path, 'r') as f:
                        return json.load(f)
            else:
                with open(analysis_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analysis results: {e}")
            return {}
    
    def generate_responses(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate responses for analyzed issues"""
        logger.info("💬 Generating intelligent responses...")
        
        responses = []
        
        try:
            issues_analyzed = analysis.get('issues_analyzed', [])
            
            for issue_analysis in issues_analyzed:
                response = self._generate_single_response(issue_analysis)
                if response:
                    responses.append(response)
            
            self.results['responses_generated'] = responses
            
        except Exception as e:
            logger.error(f"Error generating responses: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return responses
    
    def _generate_single_response(self, issue_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate response for a single issue"""
        try:
            issue_number = issue_analysis.get('issue_number')
            title = issue_analysis.get('title', '')
            categorization = issue_analysis.get('categorization', {})
            priority = issue_analysis.get('priority', {})
            complexity = issue_analysis.get('complexity', {})
            recommendations = issue_analysis.get('recommendations', [])
            language_detection = issue_analysis.get('language_detection', {})
            sentiment_analysis = issue_analysis.get('sentiment_analysis', {})
            
            # Generate response based on issue type
            response = {
                'issue_number': issue_number,
                'title': title,
                'response_type': self._determine_response_type(categorization, priority),
                'content': self._generate_response_content(issue_analysis),
                'tone': self._determine_tone(sentiment_analysis, priority),
                'language': language_detection.get('language', 'english'),
                'personalization': self._generate_personalization(issue_analysis),
                'next_steps': self._generate_next_steps(recommendations),
                'estimated_resolution_time': self._estimate_resolution_time(complexity, priority),
                'assigned_team': self._suggest_team_assignment(categorization, complexity),
                'tags': self._generate_tags(categorization, priority),
                'follow_up_required': self._determine_follow_up_required(complexity, priority)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response for issue {issue_analysis.get('issue_number')}: {e}")
            return None
    
    def _determine_response_type(self, categorization: Dict[str, Any], priority: Dict[str, Any]) -> str:
        """Determine the type of response needed"""
        category = categorization.get('primary_category', 'unknown')
        priority_level = priority.get('level', 'low')
        
        if category == 'bug':
            if priority_level in ['critical', 'high']:
                return 'urgent_bug_response'
            else:
                return 'standard_bug_response'
        elif category == 'feature':
            return 'feature_request_response'
        elif category == 'question':
            return 'question_response'
        elif category == 'security':
            return 'security_response'
        elif category == 'performance':
            return 'performance_response'
        else:
            return 'general_response'
    
    def _generate_response_content(self, issue_analysis: Dict[str, Any]) -> str:
        """Generate the main response content"""
        categorization = issue_analysis.get('categorization', {})
        priority = issue_analysis.get('priority', {})
        complexity = issue_analysis.get('complexity', {})
        recommendations = issue_analysis.get('recommendations', [])
        language_detection = issue_analysis.get('language_detection', {})
        
        category = categorization.get('primary_category', 'unknown')
        priority_level = priority.get('level', 'low')
        complexity_level = complexity.get('level', 'low')
        language = language_detection.get('language', 'english')
        
        # Generate greeting based on language
        greeting = self._get_greeting(language)
        
        # Generate acknowledgment
        acknowledgment = self._generate_acknowledgment(category, priority_level, language)
        
        # Generate explanation
        explanation = self._generate_explanation(category, complexity_level, language)
        
        # Generate action plan
        action_plan = self._generate_action_plan(recommendations, language)
        
        # Generate closing
        closing = self._get_closing(language)
        
        # Combine all parts
        content = f"""
{greeting}

{acknowledgment}

{explanation}

{action_plan}

{closing}
        """.strip()
        
        return content
    
    def _get_greeting(self, language: str) -> str:
        """Get greeting based on language"""
        greetings = {
            'english': "Thank you for opening this issue! 🙏",
            'spanish': "¡Gracias por abrir este issue! 🙏",
            'french': "Merci d'avoir ouvert ce problème ! 🙏",
            'german': "Vielen Dank für das Öffnen dieses Issues! 🙏",
            'chinese': "感谢您提出这个问题！🙏",
            'japanese': "この問題を報告していただき、ありがとうございます！🙏"
        }
        return greetings.get(language, greetings['english'])
    
    def _generate_acknowledgment(self, category: str, priority_level: str, language: str) -> str:
        """Generate acknowledgment based on issue type and priority"""
        if language == 'english':
            if category == 'bug':
                if priority_level in ['critical', 'high']:
                    return "I understand this is a critical bug that needs immediate attention. Our team will prioritize this issue and work on a fix as soon as possible."
                else:
                    return "I've identified this as a bug report. We'll investigate and work on resolving this issue."
            elif category == 'feature':
                return "Thank you for this feature request! This is a great suggestion that could improve our project."
            elif category == 'question':
                return "I see you have a question about our project. I'll do my best to provide you with a helpful answer."
            elif category == 'security':
                return "Thank you for reporting this security concern. Security is our top priority, and we'll investigate this immediately."
            else:
                return "Thank you for bringing this to our attention. We'll review and address this issue."
        else:
            # For other languages, use English for now (in reality would translate)
            return self._generate_acknowledgment(category, priority_level, 'english')
    
    def _generate_explanation(self, category: str, complexity_level: str, language: str) -> str:
        """Generate explanation based on issue type and complexity"""
        if language == 'english':
            if category == 'bug':
                return f"""
**Issue Analysis:**
- **Type**: Bug Report
- **Complexity**: {complexity_level.title()}
- **Status**: Under Investigation

We're currently analyzing this bug to understand the root cause and determine the best approach for fixing it.
                """.strip()
            elif category == 'feature':
                return f"""
**Feature Request Analysis:**
- **Type**: Feature Request
- **Complexity**: {complexity_level.title()}
- **Status**: Under Review

This feature request has been added to our backlog. We'll evaluate its feasibility and priority for future releases.
                """.strip()
            elif category == 'question':
                return """
**Question Analysis:**
- **Type**: Support Question
- **Status**: Ready to Answer

I'll provide you with a comprehensive answer based on our documentation and best practices.
                """.strip()
            elif category == 'security':
                return """
**Security Analysis:**
- **Type**: Security Issue
- **Priority**: Critical
- **Status**: Immediate Investigation

This security concern is being treated with the highest priority. Our security team will investigate and respond accordingly.
                """.strip()
            else:
                return f"""
**Issue Analysis:**
- **Type**: General Issue
- **Complexity**: {complexity_level.title()}
- **Status**: Under Review

We're reviewing this issue to determine the appropriate response and action plan.
                """.strip()
        else:
            # For other languages, use English for now
            return self._generate_explanation(category, complexity_level, 'english')
    
    def _generate_action_plan(self, recommendations: List[Dict[str, Any]], language: str) -> str:
        """Generate action plan based on recommendations"""
        if not recommendations:
            return "**Next Steps:** We'll review this issue and provide updates as we progress."
        
        if language == 'english':
            action_plan = "**Action Plan:**\n\n"
            for i, rec in enumerate(recommendations[:3], 1):  # Limit to top 3 recommendations
                action_plan += f"{i}. {rec.get('title', 'Action item')}\n"
                action_plan += f"   - {rec.get('description', '')}\n\n"
            
            return action_plan.strip()
        else:
            # For other languages, use English for now
            return self._generate_action_plan(recommendations, 'english')
    
    def _get_closing(self, language: str) -> str:
        """Get closing based on language"""
        closings = {
            'english': "Please let me know if you have any questions or need further assistance!\n\n---\n🤖 *This response was generated by AMAS AI Assistant*\n💡 *Powered by your integrated AI models*",
            'spanish': "¡Por favor, hágame saber si tiene alguna pregunta o necesita más ayuda!\n\n---\n🤖 *Esta respuesta fue generada por AMAS AI Assistant*\n💡 *Impulsado por sus modelos de IA integrados*",
            'french': "N'hésitez pas à me faire savoir si vous avez des questions ou besoin d'aide supplémentaire !\n\n---\n🤖 *Cette réponse a été générée par AMAS AI Assistant*\n💡 *Alimenté par vos modèles d'IA intégrés*"
        }
        return closings.get(language, closings['english'])
    
    def _determine_tone(self, sentiment_analysis: Dict[str, Any], priority: Dict[str, Any]) -> str:
        """Determine the appropriate tone for the response"""
        sentiment = sentiment_analysis.get('sentiment', 'neutral')
        priority_level = priority.get('level', 'low')
        
        if priority_level in ['critical', 'high']:
            return 'professional_urgent'
        elif sentiment == 'negative':
            return 'empathetic_professional'
        elif sentiment == 'positive':
            return 'friendly_enthusiastic'
        else:
            return 'professional_friendly'
    
    def _generate_personalization(self, issue_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalization data for the response"""
        language_detection = issue_analysis.get('language_detection', {})
        sentiment_analysis = issue_analysis.get('sentiment_analysis', {})
        complexity = issue_analysis.get('complexity', {})
        
        return {
            'preferred_language': language_detection.get('language', 'english'),
            'sentiment_awareness': sentiment_analysis.get('sentiment', 'neutral'),
            'complexity_level': complexity.get('level', 'low'),
            'response_style': 'detailed' if complexity.get('level') == 'high' else 'standard',
            'technical_depth': 'high' if complexity.get('score', 0) > 5 else 'medium'
        }
    
    def _generate_next_steps(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate next steps based on recommendations"""
        next_steps = []
        
        for rec in recommendations[:3]:  # Limit to top 3
            if rec.get('type') == 'immediate_action':
                next_steps.append(f"🔴 {rec.get('title', 'Immediate action required')}")
            elif rec.get('type') == 'urgent_response':
                next_steps.append(f"🟠 {rec.get('title', 'Urgent response needed')}")
            elif rec.get('type') == 'planning':
                next_steps.append(f"🟡 {rec.get('title', 'Planning required')}")
            else:
                next_steps.append(f"🔵 {rec.get('title', 'Action item')}")
        
        return next_steps
    
    def _estimate_resolution_time(self, complexity: Dict[str, Any], priority: Dict[str, Any]) -> str:
        """Estimate resolution time based on complexity and priority"""
        complexity_level = complexity.get('level', 'low')
        priority_level = priority.get('level', 'low')
        
        if priority_level == 'critical':
            if complexity_level == 'low':
                return '1-2 hours'
            elif complexity_level == 'medium':
                return '4-8 hours'
            else:
                return '1-2 days'
        elif priority_level == 'high':
            if complexity_level == 'low':
                return '1-2 days'
            elif complexity_level == 'medium':
                return '3-5 days'
            else:
                return '1-2 weeks'
        elif priority_level == 'medium':
            if complexity_level == 'low':
                return '3-5 days'
            elif complexity_level == 'medium':
                return '1-2 weeks'
            else:
                return '2-4 weeks'
        else:
            if complexity_level == 'low':
                return '1-2 weeks'
            elif complexity_level == 'medium':
                return '2-4 weeks'
            else:
                return '1-2 months'
    
    def _suggest_team_assignment(self, categorization: Dict[str, Any], complexity: Dict[str, Any]) -> str:
        """Suggest team assignment based on issue type and complexity"""
        category = categorization.get('primary_category', 'unknown')
        complexity_level = complexity.get('level', 'low')
        
        if category == 'security':
            return 'Security Team'
        elif category == 'performance':
            return 'Performance Team'
        elif category == 'bug':
            if complexity_level == 'high':
                return 'Senior Development Team'
            else:
                return 'Development Team'
        elif category == 'feature':
            if complexity_level == 'high':
                return 'Architecture Team'
            else:
                return 'Feature Development Team'
        else:
            return 'General Support Team'
    
    def _generate_tags(self, categorization: Dict[str, Any], priority: Dict[str, Any]) -> List[str]:
        """Generate tags for the response"""
        tags = []
        
        category = categorization.get('primary_category', 'unknown')
        priority_level = priority.get('level', 'low')
        
        # Add category tags
        if category == 'bug':
            tags.extend(['bug', 'investigation'])
        elif category == 'feature':
            tags.extend(['feature', 'enhancement'])
        elif category == 'question':
            tags.extend(['question', 'support'])
        elif category == 'security':
            tags.extend(['security', 'urgent'])
        elif category == 'performance':
            tags.extend(['performance', 'optimization'])
        
        # Add priority tags
        if priority_level == 'critical':
            tags.extend(['critical', 'urgent'])
        elif priority_level == 'high':
            tags.append('high-priority')
        
        return tags
    
    def _determine_follow_up_required(self, complexity: Dict[str, Any], priority: Dict[str, Any]) -> bool:
        """Determine if follow-up is required"""
        complexity_level = complexity.get('level', 'low')
        priority_level = priority.get('level', 'low')
        
        return (priority_level in ['critical', 'high'] or 
                complexity_level == 'high' or
                complexity.get('score', 0) > 5)
    
    def generate_response_templates(self) -> List[Dict[str, Any]]:
        """Generate response templates for different issue types"""
        logger.info("📝 Generating response templates...")
        
        templates = []
        
        # Bug response template
        templates.append({
            'type': 'bug_response',
            'title': 'Bug Report Response Template',
            'template': """
Thank you for reporting this bug! 🐛

**Issue Analysis:**
- **Type**: Bug Report
- **Priority**: {priority}
- **Complexity**: {complexity}
- **Status**: Under Investigation

**What we're doing:**
1. Reproducing the issue
2. Identifying the root cause
3. Developing a fix
4. Testing the solution

**Expected Resolution:** {estimated_time}

We'll keep you updated on our progress. Please let us know if you have any additional information that might help us resolve this issue.

---
🤖 *This response was generated by AMAS AI Assistant*
            """.strip()
        })
        
        # Feature request template
        templates.append({
            'type': 'feature_response',
            'title': 'Feature Request Response Template',
            'template': """
Thank you for this feature request! ✨

**Feature Analysis:**
- **Type**: Feature Request
- **Complexity**: {complexity}
- **Status**: Under Review

**What we're doing:**
1. Evaluating feasibility
2. Assessing impact
3. Planning implementation
4. Adding to roadmap

**Next Steps:** This feature has been added to our backlog. We'll evaluate its priority for future releases.

---
🤖 *This response was generated by AMAS AI Assistant*
            """.strip()
        })
        
        # Question response template
        templates.append({
            'type': 'question_response',
            'title': 'Question Response Template',
            'template': """
Thank you for your question! ❓

**Question Analysis:**
- **Type**: Support Question
- **Status**: Ready to Answer

**Answer:**
{detailed_answer}

**Additional Resources:**
- Documentation: [Link to relevant docs]
- Examples: [Link to examples]
- Related Issues: [Link to similar issues]

If you need further clarification, please don't hesitate to ask!

---
🤖 *This response was generated by AMAS AI Assistant*
            """.strip()
        })
        
        # Security response template
        templates.append({
            'type': 'security_response',
            'title': 'Security Issue Response Template',
            'template': """
Thank you for reporting this security concern! 🔒

**Security Analysis:**
- **Type**: Security Issue
- **Priority**: Critical
- **Status**: Immediate Investigation

**What we're doing:**
1. Immediate security assessment
2. Vulnerability analysis
3. Impact evaluation
4. Mitigation planning

**Security Team Response:** Our security team has been notified and will investigate this issue immediately.

**Confidentiality:** Please do not share details of this security issue publicly until we've had a chance to address it.

---
🤖 *This response was generated by AMAS AI Assistant*
            """.strip()
        })
        
        self.results['response_templates'] = templates
        return templates
    
    def run_response_generation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete response generation"""
        logger.info("🚀 Starting AI Response Generation...")
        
        try:
            # Generate responses
            responses = self.generate_responses(analysis)
            
            # Generate templates
            templates = self.generate_response_templates()
            
            # Generate personalization data
            personalization = self._generate_personalization_data(analysis)
            self.results['personalization_data'] = personalization
            
            # Generate context analysis
            context_analysis = self._generate_context_analysis(analysis)
            self.results['context_analysis'] = context_analysis
            
            # Calculate metrics
            self.results['metrics'] = self._calculate_response_metrics()
            
            logger.info("✅ Response generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during response generation: {e}")
            self.results['status'] = 'error'
            self.results['error'] = str(e)
        
        return self.results
    
    def _generate_personalization_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalization data for responses"""
        issues_analyzed = analysis.get('issues_analyzed', [])
        
        personalization = {
            'total_issues': len(issues_analyzed),
            'language_distribution': {},
            'sentiment_distribution': {},
            'category_distribution': {},
            'priority_distribution': {},
            'complexity_distribution': {}
        }
        
        for issue_analysis in issues_analyzed:
            # Language distribution
            lang = issue_analysis.get('language_detection', {}).get('language', 'unknown')
            personalization['language_distribution'][lang] = personalization['language_distribution'].get(lang, 0) + 1
            
            # Sentiment distribution
            sent = issue_analysis.get('sentiment_analysis', {}).get('sentiment', 'neutral')
            personalization['sentiment_distribution'][sent] = personalization['sentiment_distribution'].get(sent, 0) + 1
            
            # Category distribution
            cat = issue_analysis.get('categorization', {}).get('primary_category', 'unknown')
            personalization['category_distribution'][cat] = personalization['category_distribution'].get(cat, 0) + 1
            
            # Priority distribution
            pri = issue_analysis.get('priority', {}).get('level', 'low')
            personalization['priority_distribution'][pri] = personalization['priority_distribution'].get(pri, 0) + 1
            
            # Complexity distribution
            comp = issue_analysis.get('complexity', {}).get('level', 'low')
            personalization['complexity_distribution'][comp] = personalization['complexity_distribution'].get(comp, 0) + 1
        
        return personalization
    
    def _generate_context_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate context analysis for responses"""
        issues_analyzed = analysis.get('issues_analyzed', [])
        
        context = {
            'common_themes': [],
            'frequent_keywords': [],
            'response_patterns': [],
            'escalation_triggers': [],
            'success_indicators': []
        }
        
        # Analyze common themes
        all_titles = [issue.get('title', '') for issue in issues_analyzed]
        all_bodies = [issue.get('body', '') for issue in issues_analyzed]
        
        # Simple keyword extraction (in reality would use more sophisticated NLP)
        common_words = {}
        for title in all_titles:
            words = title.lower().split()
            for word in words:
                if len(word) > 3:  # Filter short words
                    common_words[word] = common_words.get(word, 0) + 1
        
        # Get most common words
        context['frequent_keywords'] = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return context
    
    def _calculate_response_metrics(self) -> Dict[str, Any]:
        """Calculate response generation metrics"""
        metrics = {
            'total_responses': len(self.results.get('responses_generated', [])),
            'response_templates': len(self.results.get('response_templates', [])),
            'personalization_data_points': len(self.results.get('personalization_data', {})),
            'context_analysis_items': len(self.results.get('context_analysis', {}))
        }
        
        # Calculate response quality metrics
        responses = self.results.get('responses_generated', [])
        if responses:
            metrics['average_response_length'] = sum(len(resp.get('content', '')) for resp in responses) / len(responses)
            metrics['responses_with_next_steps'] = sum(1 for resp in responses if resp.get('next_steps'))
            metrics['responses_with_estimated_time'] = sum(1 for resp in responses if resp.get('estimated_resolution_time'))
        
        return metrics

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Response Generator')
    parser.add_argument('--mode', default='intelligent', help='Generation mode')
    parser.add_argument('--depth', default='comprehensive', help='Generation depth')
    parser.add_argument('--language', default='auto', help='Response language preference')
    parser.add_argument('--auto-fix', action='store_true', help='Auto-fix issues when possible')
    parser.add_argument('--target-issues', default='all', help='Target issues to respond to')
    parser.add_argument('--analysis-results', default='analysis_results/', help='Path to analysis results')
    parser.add_argument('--use-advanced-manager', action='store_true', help='Use advanced manager')
    parser.add_argument('--output', default='response_generation_results.json', help='Output file')
    
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
    
    # Initialize generator
    generator = AIResponseGenerator(config)
    
    # Load analysis results
    analysis = generator.load_analysis_results(args.analysis_results)
    
    # Run response generation
    results = generator.run_response_generation(analysis)
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Response generation results saved to {args.output}")
    
    return 0 if results['status'] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())