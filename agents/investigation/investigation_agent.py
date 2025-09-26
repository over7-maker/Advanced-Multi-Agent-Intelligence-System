"""
Investigation Agent Implementation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base.intelligence_agent import IntelligenceAgent, AgentStatus

logger = logging.getLogger(__name__)

class InvestigationAgent(IntelligenceAgent):
    """Investigation Agent for AMAS Intelligence System"""
    
    def __init__(
        self,
        agent_id: str,
        name: str = "Investigation Agent",
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None
    ):
        capabilities = [
            "link_analysis",
            "entity_resolution", 
            "timeline_reconstruction",
            "correlation_analysis",
            "investigation_management"
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
        
        self.investigation_cases = {}
        self.entity_relationships = {}
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute investigation task"""
        try:
            task_type = task.get('type', 'general')
            task_id = task.get('id', 'unknown')
            
            logger.info(f"Executing investigation task {task_id} of type {task_type}")
            
            if task_type == 'link_analysis':
                return await self._perform_link_analysis(task)
            elif task_type == 'entity_resolution':
                return await self._perform_entity_resolution(task)
            elif task_type == 'timeline_reconstruction':
                return await self._perform_timeline_reconstruction(task)
            elif task_type == 'correlation_analysis':
                return await self._perform_correlation_analysis(task)
            else:
                return await self._perform_general_investigation(task)
                
        except Exception as e:
            logger.error(f"Error executing investigation task: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if this agent can handle the task"""
        investigation_keywords = [
            'investigation', 'analysis', 'correlation', 'timeline',
            'entity', 'link', 'relationship', 'evidence'
        ]
        
        task_text = f"{task.get('type', '')} {task.get('description', '')}".lower()
        return any(keyword in task_text for keyword in investigation_keywords)
    
    async def _perform_link_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform link analysis on entities"""
        try:
            entities = task.get('parameters', {}).get('entities', [])
            analysis_depth = task.get('parameters', {}).get('depth', 'medium')
            
            # Mock link analysis
            relationships = []
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i+1:], i+1):
                    if self._entities_related(entity1, entity2):
                        relationships.append({
                            'source': entity1,
                            'target': entity2,
                            'relationship_type': 'related',
                            'strength': 0.8,
                            'evidence': ['shared_attributes', 'temporal_proximity']
                        })
            
            return {
                'success': True,
                'task_type': 'link_analysis',
                'entities_analyzed': len(entities),
                'relationships_found': len(relationships),
                'relationships': relationships,
                'analysis_depth': analysis_depth,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in link analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_entity_resolution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform entity resolution"""
        try:
            entities = task.get('parameters', {}).get('entities', [])
            resolution_threshold = task.get('parameters', {}).get('threshold', 0.8)
            
            # Mock entity resolution
            resolved_entities = {}
            for entity in entities:
                # Check if entity already exists in knowledge graph
                if self.knowledge_graph:
                    existing = await self._check_existing_entity(entity)
                    if existing:
                        resolved_entities[entity] = {
                            'resolved_to': existing,
                            'confidence': 0.9,
                            'method': 'knowledge_graph_lookup'
                    }
                else:
                    # Mock resolution
                    resolved_entities[entity] = {
                        'resolved_to': f"resolved_{entity}",
                        'confidence': 0.7,
                        'method': 'fuzzy_matching'
                    }
            
            return {
                'success': True,
                'task_type': 'entity_resolution',
                'entities_processed': len(entities),
                'resolved_entities': resolved_entities,
                'resolution_threshold': resolution_threshold,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in entity resolution: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_timeline_reconstruction(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Reconstruct timeline of events"""
        try:
            events = task.get('parameters', {}).get('events', [])
            time_range = task.get('parameters', {}).get('time_range', {})
            
            # Mock timeline reconstruction
            timeline = []
            for event in events:
                timeline.append({
                    'event_id': event.get('id', f"event_{len(timeline)}"),
                    'timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                    'description': event.get('description', ''),
                    'entities_involved': event.get('entities', []),
                    'evidence': event.get('evidence', []),
                    'confidence': 0.8
                })
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x['timestamp'])
            
            return {
                'success': True,
                'task_type': 'timeline_reconstruction',
                'events_processed': len(events),
                'timeline': timeline,
                'time_range': time_range,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in timeline reconstruction: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_correlation_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform correlation analysis"""
        try:
            data_sources = task.get('parameters', {}).get('data_sources', [])
            correlation_type = task.get('parameters', {}).get('correlation_type', 'statistical')
            
            # Mock correlation analysis
            correlations = []
            for i, source1 in enumerate(data_sources):
                for source2 in data_sources[i+1:]:
                    correlation_score = self._calculate_correlation(source1, source2)
                    if correlation_score > 0.5:
                        correlations.append({
                            'source1': source1,
                            'source2': source2,
                            'correlation_score': correlation_score,
                            'correlation_type': correlation_type,
                            'significance': 'high' if correlation_score > 0.8 else 'medium'
                        })
            
            return {
                'success': True,
                'task_type': 'correlation_analysis',
                'data_sources': len(data_sources),
                'correlations_found': len(correlations),
                'correlations': correlations,
                'correlation_type': correlation_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _perform_general_investigation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform general investigation"""
        try:
            description = task.get('description', '')
            parameters = task.get('parameters', {})
            
            # Mock general investigation
            investigation_result = {
                'investigation_id': f"inv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'description': description,
                'status': 'completed',
                'findings': [
                    'Investigation completed successfully',
                    'No suspicious activity detected',
                    'All entities verified'
                ],
                'recommendations': [
                    'Continue monitoring',
                    'Update investigation protocols'
                ],
                'confidence': 0.85
            }
            
            return {
                'success': True,
                'task_type': 'general_investigation',
                'result': investigation_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in general investigation: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _entities_related(self, entity1: str, entity2: str) -> bool:
        """Check if two entities are related"""
        # Mock relationship detection
        return hash(entity1) % 3 == hash(entity2) % 3
    
    async def _check_existing_entity(self, entity: str) -> Optional[Dict[str, Any]]:
        """Check if entity exists in knowledge graph"""
        if not self.knowledge_graph:
            return None
        
        try:
            result = await self.knowledge_graph.query_entities(
                properties={'name': entity}
            )
            if result.get('success') and result.get('entities'):
                return result['entities'][0]
            return None
        except Exception as e:
            logger.error(f"Error checking existing entity: {e}")
            return None
    
    def _calculate_correlation(self, source1: str, source2: str) -> float:
        """Calculate correlation between two data sources"""
        # Mock correlation calculation
        return abs(hash(source1) - hash(source2)) / 1000.0