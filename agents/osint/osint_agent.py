"""
OSINT Collection Agent

This module implements the OSINT (Open Source Intelligence) Collection Agent
for gathering and analyzing open-source intelligence data from various sources.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import json

from ..base.react_agent import ReactAgent
from .web_scraper import WebScraper
from .api_connectors import APIConnectors
from .data_filter import DataFilter


class OSINTAgent(ReactAgent):
    """
    OSINT Collection Agent for gathering open-source intelligence.
    
    This agent specializes in collecting, filtering, and analyzing
    open-source intelligence data from various sources including
    social media, news outlets, forums, and public databases.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str = "OSINT Collection Agent",
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None
    ):
        """
        Initialize the OSINT Collection Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            llm_service: LLM service for AI operations
            vector_service: Vector service for semantic search
            knowledge_graph: Knowledge graph service
            security_service: Security service for access control
        """
        capabilities = [
            'osint_collection',
            'web_scraping',
            'api_integration',
            'data_filtering',
            'content_analysis',
            'source_monitoring',
            'trend_analysis',
            'entity_extraction'
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
        
        # OSINT-specific components
        self.web_scraper = WebScraper()
        self.api_connectors = APIConnectors()
        self.data_filter = DataFilter()
        
        # Configuration
        self.config = {
            'max_sources_per_task': 50,
            'scraping_delay': 1.0,  # Delay between requests
            'max_content_length': 10000,  # Max content length to process
            'supported_formats': ['html', 'json', 'xml', 'rss', 'atom'],
            'filter_keywords': [],
            'exclude_domains': [],
            'rate_limits': {
                'requests_per_minute': 60,
                'requests_per_hour': 1000
            }
        }
        
        # Monitoring sources
        self.monitored_sources = {}
        self.collection_history = []
        
        # Performance metrics
        self.osint_metrics = {
            'sources_scraped': 0,
            'data_points_collected': 0,
            'filtered_content': 0,
            'entities_extracted': 0,
            'trends_identified': 0
        }
    
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate if this agent can handle the given task.
        
        Args:
            task: Task definition to validate
            
        Returns:
            True if agent can handle the task, False otherwise
        """
        task_type = task.get('type', '').lower()
        return task_type in ['osint', 'collection', 'monitoring', 'scraping']
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an OSINT collection task.
        
        Args:
            task: Task definition with parameters and context
            
        Returns:
            Task execution results
        """
        self.logger.info(f"Executing OSINT task: {task.get('id', 'unknown')}")
        
        # Extract task parameters
        sources = task.get('sources', [])
        keywords = task.get('keywords', [])
        filters = task.get('filters', {})
        monitoring = task.get('monitoring', False)
        
        try:
            if monitoring:
                # Set up continuous monitoring
                result = await self._setup_monitoring(sources, keywords, filters)
            else:
                # Perform one-time collection
                result = await self._collect_osint_data(sources, keywords, filters)
            
            # Update metrics
            self._update_osint_metrics(result)
            
            return {
                'task_id': task.get('id'),
                'status': 'completed',
                'result': result,
                'metrics': self.osint_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"OSINT task failed: {e}")
            return {
                'task_id': task.get('id'),
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _collect_osint_data(
        self,
        sources: List[str],
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect OSINT data from specified sources.
        
        Args:
            sources: List of sources to collect from
            keywords: Keywords to search for
            filters: Filters to apply to collected data
            
        Returns:
            Collected OSINT data
        """
        self.logger.info(f"Collecting OSINT data from {len(sources)} sources")
        
        collected_data = {
            'sources': {},
            'entities': [],
            'trends': [],
            'summary': {},
            'metadata': {
                'collection_time': datetime.utcnow().isoformat(),
                'sources_processed': 0,
                'data_points': 0
            }
        }
        
        # Process each source
        for source in sources[:self.config['max_sources_per_task']]:
            try:
                source_data = await self._process_source(source, keywords, filters)
                if source_data:
                    collected_data['sources'][source] = source_data
                    collected_data['metadata']['sources_processed'] += 1
                    collected_data['metadata']['data_points'] += len(source_data.get('content', []))
                
                # Rate limiting
                await asyncio.sleep(self.config['scraping_delay'])
                
            except Exception as e:
                self.logger.warning(f"Failed to process source {source}: {e}")
                continue
        
        # Analyze collected data
        if collected_data['sources']:
            analysis_result = await self._analyze_collected_data(collected_data)
            collected_data.update(analysis_result)
        
        # Store in knowledge base
        await self._store_osint_data(collected_data)
        
        return collected_data
    
    async def _process_source(
        self,
        source: str,
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single OSINT source.
        
        Args:
            source: Source URL or identifier
            keywords: Keywords to search for
            filters: Filters to apply
            
        Returns:
            Processed source data or None if failed
        """
        try:
            parsed_url = urlparse(source)
            
            if parsed_url.scheme in ['http', 'https']:
                # Web scraping
                content = await self.web_scraper.scrape_url(
                    url=source,
                    keywords=keywords,
                    max_content_length=self.config['max_content_length']
                )
            else:
                # API or other source
                content = await self.api_connectors.fetch_data(
                    source=source,
                    keywords=keywords,
                    filters=filters
                )
            
            if not content:
                return None
            
            # Filter content
            filtered_content = await self.data_filter.filter_content(
                content=content,
                keywords=keywords,
                filters=filters
            )
            
            if not filtered_content:
                return None
            
            # Extract entities
            entities = await self._extract_entities(filtered_content)
            
            # Analyze sentiment and relevance
            analysis = await self._analyze_content(filtered_content, keywords)
            
            return {
                'source': source,
                'content': filtered_content,
                'entities': entities,
                'analysis': analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing source {source}: {e}")
            return None
    
    async def _extract_entities(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract entities from content using LLM.
        
        Args:
            content: Content to extract entities from
            
        Returns:
            List of extracted entities
        """
        if not self.llm_service:
            return []
        
        try:
            # Create entity extraction prompt
            prompt = f"""
Extract entities from the following content. Focus on:
- People (names, titles, organizations)
- Locations (cities, countries, addresses)
- Events (dates, incidents, activities)
- Technologies (software, hardware, systems)
- Organizations (companies, groups, institutions)

Content:
{content.get('text', '')[:2000]}

Provide the entities in JSON format:
{{
    "people": ["name1", "name2"],
    "locations": ["location1", "location2"],
    "events": ["event1", "event2"],
    "technologies": ["tech1", "tech2"],
    "organizations": ["org1", "org2"]
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse result
            try:
                entities = json.loads(result)
                return entities
            except:
                return []
                
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def _analyze_content(
        self,
        content: Dict[str, Any],
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze content for sentiment, relevance, and trends.
        
        Args:
            content: Content to analyze
            keywords: Keywords to check relevance against
            
        Returns:
            Analysis results
        """
        if not self.llm_service:
            return {'sentiment': 'neutral', 'relevance': 0.5, 'trends': []}
        
        try:
            # Create analysis prompt
            prompt = f"""
Analyze the following content for intelligence value:

Content: {content.get('text', '')[:1000]}

Keywords: {', '.join(keywords)}

Provide analysis in JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "relevance_score": 0.0-1.0,
    "key_themes": ["theme1", "theme2"],
    "threat_indicators": ["indicator1", "indicator2"],
    "intelligence_value": "high|medium|low"
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse result
            try:
                analysis = json.loads(result)
                return analysis
            except:
                return {'sentiment': 'neutral', 'relevance': 0.5, 'trends': []}
                
        except Exception as e:
            self.logger.error(f"Content analysis failed: {e}")
            return {'sentiment': 'neutral', 'relevance': 0.5, 'trends': []}
    
    async def _analyze_collected_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze all collected data for trends and patterns.
        
        Args:
            collected_data: All collected OSINT data
            
        Returns:
            Analysis results
        """
        if not self.llm_service:
            return {'trends': [], 'patterns': [], 'summary': 'No analysis available'}
        
        try:
            # Create analysis prompt
            prompt = f"""
Analyze the following OSINT data for trends and patterns:

Sources: {len(collected_data.get('sources', {}))}
Data Points: {collected_data.get('metadata', {}).get('data_points', 0)}

Provide analysis in JSON format:
{{
    "trends": ["trend1", "trend2"],
    "patterns": ["pattern1", "pattern2"],
    "summary": "Overall analysis summary",
    "recommendations": ["rec1", "rec2"]
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse result
            try:
                analysis = json.loads(result)
                return analysis
            except:
                return {'trends': [], 'patterns': [], 'summary': 'Analysis failed'}
                
        except Exception as e:
            self.logger.error(f"Data analysis failed: {e}")
            return {'trends': [], 'patterns': [], 'summary': 'Analysis failed'}
    
    async def _store_osint_data(self, collected_data: Dict[str, Any]):
        """
        Store collected OSINT data in knowledge base.
        
        Args:
            collected_data: Collected OSINT data to store
        """
        try:
            # Store in vector service
            if self.vector_service:
                for source, data in collected_data.get('sources', {}).items():
                    await self.vector_service.store_document(
                        content=data.get('content', {}).get('text', ''),
                        metadata={
                            'source': source,
                            'type': 'osint',
                            'timestamp': data.get('timestamp'),
                            'entities': data.get('entities', []),
                            'analysis': data.get('analysis', {})
                        }
                    )
            
            # Store in knowledge graph
            if self.knowledge_graph:
                for source, data in collected_data.get('sources', {}).items():
                    entities = data.get('entities', {})
                    for entity_type, entity_list in entities.items():
                        for entity in entity_list:
                            await self.knowledge_graph.add_entity(
                                entity=entity,
                                entity_type=entity_type,
                                source=source,
                                metadata=data.get('analysis', {})
                            )
            
            self.logger.info("OSINT data stored successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to store OSINT data: {e}")
    
    async def _setup_monitoring(
        self,
        sources: List[str],
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up continuous monitoring of OSINT sources.
        
        Args:
            sources: Sources to monitor
            keywords: Keywords to monitor for
            filters: Filters to apply
            
        Returns:
            Monitoring setup results
        """
        self.logger.info(f"Setting up monitoring for {len(sources)} sources")
        
        monitoring_id = f"osint_monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Store monitoring configuration
        self.monitored_sources[monitoring_id] = {
            'sources': sources,
            'keywords': keywords,
            'filters': filters,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        # Start monitoring task
        asyncio.create_task(self._monitor_sources(monitoring_id, sources, keywords, filters))
        
        return {
            'monitoring_id': monitoring_id,
            'sources': sources,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
    
    async def _monitor_sources(
        self,
        monitoring_id: str,
        sources: List[str],
        keywords: List[str],
        filters: Dict[str, Any]
    ):
        """
        Continuously monitor sources for new content.
        
        Args:
            monitoring_id: ID of the monitoring task
            sources: Sources to monitor
            keywords: Keywords to monitor for
            filters: Filters to apply
        """
        self.logger.info(f"Starting monitoring task {monitoring_id}")
        
        while monitoring_id in self.monitored_sources:
            try:
                # Check each source
                for source in sources:
                    # Check for new content
                    new_content = await self._check_for_new_content(source, keywords, filters)
                    
                    if new_content:
                        # Process new content
                        await self._process_new_content(monitoring_id, source, new_content)
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in monitoring task {monitoring_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _check_for_new_content(
        self,
        source: str,
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check a source for new content.
        
        Args:
            source: Source to check
            keywords: Keywords to search for
            filters: Filters to apply
            
        Returns:
            New content if found, None otherwise
        """
        try:
            # Get last check time for this source
            last_check = self.collection_history[-1].get('timestamp') if self.collection_history else None
            
            # Check for new content
            new_content = await self._process_source(source, keywords, filters)
            
            if new_content and last_check:
                # Filter content newer than last check
                content_time = datetime.fromisoformat(new_content.get('timestamp', ''))
                if content_time > datetime.fromisoformat(last_check):
                    return new_content
            
            return new_content
            
        except Exception as e:
            self.logger.error(f"Error checking source {source}: {e}")
            return None
    
    async def _process_new_content(
        self,
        monitoring_id: str,
        source: str,
        content: Dict[str, Any]
    ):
        """
        Process new content found during monitoring.
        
        Args:
            monitoring_id: ID of the monitoring task
            source: Source of the content
            content: New content to process
        """
        try:
            # Store new content
            await self._store_osint_data({'sources': {source: content}})
            
            # Notify other agents
            await self.communication.broadcast_message(
                message_type='event',
                content={
                    'event_type': 'new_osint_content',
                    'monitoring_id': monitoring_id,
                    'source': source,
                    'content': content
                }
            )
            
            self.logger.info(f"New content processed from {source}")
            
        except Exception as e:
            self.logger.error(f"Error processing new content from {source}: {e}")
    
    def _update_osint_metrics(self, result: Dict[str, Any]):
        """Update OSINT-specific metrics."""
        sources = result.get('sources', {})
        self.osint_metrics['sources_scraped'] += len(sources)
        
        for source_data in sources.values():
            content = source_data.get('content', {})
            entities = source_data.get('entities', {})
            
            self.osint_metrics['data_points_collected'] += len(content.get('items', []))
            self.osint_metrics['entities_extracted'] += sum(len(entities.get(key, [])) for key in entities)
        
        # Update trends if identified
        if result.get('trends'):
            self.osint_metrics['trends_identified'] += len(result['trends'])
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get status of all monitoring tasks.
        
        Returns:
            Monitoring status information
        """
        return {
            'active_monitoring': len(self.monitored_sources),
            'monitored_sources': list(self.monitored_sources.keys()),
            'metrics': self.osint_metrics,
            'last_activity': self.last_activity.isoformat()
        }
    
    async def stop_monitoring(self, monitoring_id: str) -> bool:
        """
        Stop a monitoring task.
        
        Args:
            monitoring_id: ID of the monitoring task to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if monitoring_id in self.monitored_sources:
                del self.monitored_sources[monitoring_id]
                self.logger.info(f"Stopped monitoring task {monitoring_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring task {monitoring_id}: {e}")
            return False