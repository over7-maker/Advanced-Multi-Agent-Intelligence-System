"""
Enhanced OSINT Collection Agent
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp
from urllib.parse import urljoin, urlparse

from agents.base.intelligence_agent import IntelligenceAgent, AgentStatus

logger = logging.getLogger(__name__)

class OSINTAgent(IntelligenceAgent):
    """Enhanced OSINT Collection Agent for AMAS Intelligence System"""
    
    def __init__(
        self,
        agent_id: str,
        name: str = "OSINT Agent",
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None
    ):
        capabilities = [
            "web_scraping",
            "social_media_monitoring", 
            "news_aggregation",
            "domain_analysis",
            "email_analysis",
            "social_network_analysis",
            "threat_intelligence",
            "dark_web_monitoring"
        ]
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            capabilities=capabilities,
            llm_service=llm_service,
            vector_service=vector_service,
            knowledge_graph=knowledge_graph,
            security_service=security_service
        )
        
        self.data_sources = {
            'news': [
                'https://www.bbc.com/news',
                'https://www.reuters.com',
                'https://www.cnn.com',
                'https://www.theguardian.com'
            ],
            'social_media': [
                'https://twitter.com',
                'https://www.reddit.com',
                'https://www.linkedin.com'
            ],
            'forums': [
                'https://www.hackernews.com',
                'https://www.securityfocus.com'
            ]
        }
        
        self.collected_data = {}
        self.analysis_results = {}
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OSINT task"""
        try:
            task_type = task.get('type', 'general')
            task_id = task.get('id', 'unknown')
            
            logger.info(f"Executing OSINT task {task_id} of type {task_type}")
            
            if task_type == 'web_scraping':
                return await self._perform_web_scraping(task)
            elif task_type == 'social_media_monitoring':
                return await self._monitor_social_media(task)
            elif task_type == 'news_aggregation':
                return await self._aggregate_news(task)
            elif task_type == 'domain_analysis':
                return await self._analyze_domain(task)
            elif task_type == 'email_analysis':
                return await self._analyze_email(task)
            elif task_type == 'threat_intelligence':
                return await self._collect_threat_intelligence(task)
            else:
                return await self._perform_general_osint(task)
                
        except Exception as e:
            logger.error(f"Error executing OSINT task: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if this agent can handle the task"""
        osint_keywords = [
            'osint', 'intelligence', 'gathering', 'collection', 'monitoring',
            'web', 'social', 'news', 'domain', 'email', 'threat'
        ]
        
        task_text = f"{task.get('type', '')} {task.get('description', '')}".lower()
        return any(keyword in task_text for keyword in osint_keywords)
    
    async def _perform_web_scraping(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web scraping"""
        try:
            urls = task.get('parameters', {}).get('urls', [])
            keywords = task.get('parameters', {}).get('keywords', [])
            max_pages = task.get('parameters', {}).get('max_pages', 10)
            
            scraped_data = []
            for url in urls[:max_pages]:
                try:
                    # Mock web scraping - in production, this would use actual scraping
                    page_data = await self._scrape_webpage(url, keywords)
                    if page_data:
                        scraped_data.append(page_data)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
            
            # Analyze scraped data
            analysis = await self._analyze_scraped_data(scraped_data, keywords)
            
            return {
                'success': True,
                'task_type': 'web_scraping',
                'urls_scraped': len(scraped_data),
                'data': scraped_data,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _scrape_webpage(self, url: str, keywords: List[str]) -> Dict[str, Any]:
        """Scrape a single webpage"""
        try:
            # Mock webpage scraping
            page_data = {
                'url': url,
                'title': f'Mock Title for {url}',
                'content': f'Mock content for {url} containing keywords: {", ".join(keywords)}',
                'links': [f'{url}/link1', f'{url}/link2'],
                'images': [f'{url}/image1.jpg', f'{url}/image2.jpg'],
                'metadata': {
                    'scraped_at': datetime.utcnow().isoformat(),
                    'keywords_found': keywords,
                    'content_length': len(f'Mock content for {url}')
                }
            }
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error scraping webpage {url}: {e}")
            return None
    
    async def _analyze_scraped_data(self, scraped_data: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
        """Analyze scraped data"""
        try:
            # Mock analysis
            analysis = {
                'total_pages': len(scraped_data),
                'keywords_found': keywords,
                'entities': ['Entity1', 'Entity2', 'Entity3'],
                'sentiment': 'neutral',
                'threat_indicators': [],
                'summary': f'Analyzed {len(scraped_data)} pages for keywords: {", ".join(keywords)}'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing scraped data: {e}")
            return {'error': str(e)}
    
    async def _monitor_social_media(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor social media platforms"""
        try:
            platforms = task.get('parameters', {}).get('platforms', ['twitter', 'reddit'])
            keywords = task.get('parameters', {}).get('keywords', [])
            time_range = task.get('parameters', {}).get('time_range', '24h')
            
            # Mock social media monitoring
            social_data = []
            for platform in platforms:
                platform_data = {
                    'platform': platform,
                    'posts': [
                        {
                            'id': f'{platform}_post_1',
                            'content': f'Mock post about {", ".join(keywords)}',
                            'author': f'user_{platform}',
                            'timestamp': datetime.utcnow().isoformat(),
                            'engagement': {'likes': 10, 'shares': 5, 'comments': 3}
                        }
                    ],
                    'mentions': keywords,
                    'sentiment': 'positive'
                }
                social_data.append(platform_data)
            
            # Analyze social media data
            analysis = await self._analyze_social_data(social_data, keywords)
            
            return {
                'success': True,
                'task_type': 'social_media_monitoring',
                'platforms_monitored': len(platforms),
                'data': social_data,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in social media monitoring: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _analyze_social_data(self, social_data: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
        """Analyze social media data"""
        try:
            # Mock social media analysis
            analysis = {
                'total_posts': sum(len(platform['posts']) for platform in social_data),
                'platforms_analyzed': len(social_data),
                'keywords_mentioned': keywords,
                'sentiment_analysis': {
                    'positive': 0.6,
                    'neutral': 0.3,
                    'negative': 0.1
                },
                'trending_topics': ['topic1', 'topic2'],
                'influencers': ['user1', 'user2'],
                'summary': f'Analyzed social media data across {len(social_data)} platforms'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing social data: {e}")
            return {'error': str(e)}
    
    async def _aggregate_news(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate news from multiple sources"""
        try:
            sources = task.get('parameters', {}).get('sources', self.data_sources['news'])
            keywords = task.get('parameters', {}).get('keywords', [])
            time_range = task.get('parameters', {}).get('time_range', '24h')
            
            # Mock news aggregation
            news_data = []
            for source in sources:
                source_data = {
                    'source': source,
                    'articles': [
                        {
                            'title': f'News article about {", ".join(keywords)}',
                            'url': f'{source}/article1',
                            'published': datetime.utcnow().isoformat(),
                            'summary': f'Summary of news about {", ".join(keywords)}',
                            'keywords': keywords,
                            'relevance_score': 0.8
                        }
                    ]
                }
                news_data.append(source_data)
            
            # Analyze news data
            analysis = await self._analyze_news_data(news_data, keywords)
            
            return {
                'success': True,
                'task_type': 'news_aggregation',
                'sources_checked': len(sources),
                'data': news_data,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in news aggregation: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _analyze_news_data(self, news_data: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
        """Analyze news data"""
        try:
            # Mock news analysis
            analysis = {
                'total_articles': sum(len(source['articles']) for source in news_data),
                'sources_analyzed': len(news_data),
                'keywords_covered': keywords,
                'trending_stories': ['story1', 'story2'],
                'sentiment_analysis': {
                    'positive': 0.4,
                    'neutral': 0.4,
                    'negative': 0.2
                },
                'summary': f'Analyzed news from {len(news_data)} sources'
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news data: {e}")
            return {'error': str(e)}
    
    async def _analyze_domain(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze domain information"""
        try:
            domain = task.get('parameters', {}).get('domain', '')
            analysis_type = task.get('parameters', {}).get('analysis_type', 'comprehensive')
            
            # Mock domain analysis
            domain_data = {
                'domain': domain,
                'whois_info': {
                    'registrar': 'Mock Registrar',
                    'creation_date': '2020-01-01',
                    'expiration_date': '2025-01-01',
                    'nameservers': ['ns1.example.com', 'ns2.example.com']
                },
                'dns_records': {
                    'A': ['192.168.1.1'],
                    'MX': ['mail.example.com'],
                    'TXT': ['v=spf1 include:_spf.google.com ~all']
                },
                'ssl_certificate': {
                    'issuer': 'Mock CA',
                    'valid_from': '2023-01-01',
                    'valid_to': '2024-01-01',
                    'subject': f'CN={domain}'
                },
                'subdomains': [f'www.{domain}', f'mail.{domain}', f'admin.{domain}'],
                'threat_indicators': [],
                'reputation_score': 0.8
            }
            
            return {
                'success': True,
                'task_type': 'domain_analysis',
                'domain': domain,
                'analysis_type': analysis_type,
                'data': domain_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in domain analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _analyze_email(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email information"""
        try:
            email = task.get('parameters', {}).get('email', '')
            analysis_type = task.get('parameters', {}).get('analysis_type', 'basic')
            
            # Mock email analysis
            email_data = {
                'email': email,
                'domain': email.split('@')[1] if '@' in email else '',
                'disposable': False,
                'role_based': email.startswith('admin') or email.startswith('info'),
                'social_media_presence': ['twitter', 'linkedin'],
                'data_breaches': [],
                'reputation_score': 0.7
            }
            
            return {
                'success': True,
                'task_type': 'email_analysis',
                'email': email,
                'analysis_type': analysis_type,
                'data': email_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in email analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _collect_threat_intelligence(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Collect threat intelligence"""
        try:
            threat_types = task.get('parameters', {}).get('threat_types', ['malware', 'phishing'])
            sources = task.get('parameters', {}).get('sources', ['virustotal', 'threatconnect'])
            
            # Mock threat intelligence collection
            threat_data = []
            for threat_type in threat_types:
                threat_info = {
                    'threat_type': threat_type,
                    'indicators': [
                        {
                            'type': 'ip',
                            'value': '192.168.1.100',
                            'confidence': 0.8,
                            'source': 'virustotal'
                        },
                        {
                            'type': 'domain',
                            'value': 'malicious.example.com',
                            'confidence': 0.9,
                            'source': 'threatconnect'
                        }
                    ],
                    'description': f'Mock {threat_type} threat intelligence',
                    'severity': 'high',
                    'last_seen': datetime.utcnow().isoformat()
                }
                threat_data.append(threat_info)
            
            return {
                'success': True,
                'task_type': 'threat_intelligence',
                'threat_types': threat_types,
                'sources': sources,
                'data': threat_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in threat intelligence collection: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_general_osint(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general OSINT collection"""
        try:
            description = task.get('description', '')
            parameters = task.get('parameters', {})
            
            # Mock general OSINT
            osint_result = {
                'collection_id': f"osint_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'description': description,
                'status': 'completed',
                'findings': [
                    'OSINT collection completed successfully',
                    'Multiple sources analyzed',
                    'No significant threats detected'
                ],
                'recommendations': [
                    'Continue monitoring key sources',
                    'Update collection parameters'
                ],
                'confidence': 0.85
            }
            
            return {
                'success': True,
                'task_type': 'general_osint',
                'result': osint_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in general OSINT: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }