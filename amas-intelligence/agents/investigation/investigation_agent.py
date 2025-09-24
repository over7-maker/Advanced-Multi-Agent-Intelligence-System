"""
Investigation Agent

This module implements the Investigation Agent for deep investigation
and link analysis in intelligence operations.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json

from ..base.react_agent import ReactAgent
from .link_analysis import LinkAnalysis
from .cross_platform import CrossPlatformAnalysis
from .entity_resolution import EntityResolution


class InvestigationAgent(ReactAgent):
    """
    Investigation Agent for deep investigation and link analysis.
    
    This agent specializes in investigating entities, analyzing connections,
    and building comprehensive intelligence pictures through multi-source
    analysis and correlation.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str = "Investigation Agent",
        llm_service: Any = None,
        vector_service: Any = None,
        knowledge_graph: Any = None,
        security_service: Any = None
    ):
        """
        Initialize the Investigation Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            llm_service: LLM service for AI operations
            vector_service: Vector service for semantic search
            knowledge_graph: Knowledge graph service
            security_service: Security service for access control
        """
        capabilities = [
            'investigation',
            'link_analysis',
            'entity_resolution',
            'cross_platform_analysis',
            'relationship_mapping',
            'timeline_reconstruction',
            'threat_assessment',
            'intelligence_correlation'
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
        
        # Investigation-specific components
        self.link_analysis = LinkAnalysis()
        self.cross_platform = CrossPlatformAnalysis()
        self.entity_resolution = EntityResolution()
        
        # Configuration
        self.config = {
            'max_investigation_depth': 5,
            'max_entities_per_investigation': 100,
            'correlation_threshold': 0.7,
            'timeline_window_days': 365,
            'supported_platforms': ['social_media', 'news', 'forums', 'databases'],
            'analysis_methods': ['link_analysis', 'entity_resolution', 'cross_platform']
        }
        
        # Investigation state
        self.active_investigations = {}
        self.investigation_history = []
        
        # Performance metrics
        self.investigation_metrics = {
            'investigations_completed': 0,
            'entities_analyzed': 0,
            'relationships_discovered': 0,
            'threats_identified': 0,
            'average_investigation_time': 0.0
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
        return task_type in ['investigation', 'analysis', 'correlation', 'link_analysis']
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an investigation task.
        
        Args:
            task: Task definition with parameters and context
            
        Returns:
            Task execution results
        """
        self.logger.info(f"Executing investigation task: {task.get('id', 'unknown')}")
        
        # Extract task parameters
        entities = task.get('entities', [])
        investigation_type = task.get('investigation_type', 'comprehensive')
        depth = task.get('depth', 'medium')
        platforms = task.get('platforms', self.config['supported_platforms'])
        
        try:
            # Start investigation
            investigation_id = await self._start_investigation(
                entities, investigation_type, depth, platforms
            )
            
            # Perform investigation steps
            investigation_result = await self._perform_investigation(
                investigation_id, entities, investigation_type, depth, platforms
            )
            
            # Complete investigation
            final_result = await self._complete_investigation(
                investigation_id, investigation_result
            )
            
            # Update metrics
            self._update_investigation_metrics(final_result)
            
            return {
                'task_id': task.get('id'),
                'status': 'completed',
                'investigation_id': investigation_id,
                'result': final_result,
                'metrics': self.investigation_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Investigation task failed: {e}")
            return {
                'task_id': task.get('id'),
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _start_investigation(
        self,
        entities: List[str],
        investigation_type: str,
        depth: str,
        platforms: List[str]
    ) -> str:
        """
        Start a new investigation.
        
        Args:
            entities: Entities to investigate
            investigation_type: Type of investigation
            depth: Investigation depth
            platforms: Platforms to investigate on
            
        Returns:
            Investigation ID
        """
        investigation_id = f"investigation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create investigation record
        investigation = {
            'id': investigation_id,
            'entities': entities,
            'type': investigation_type,
            'depth': depth,
            'platforms': platforms,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'steps_completed': [],
            'findings': [],
            'relationships': [],
            'threats': []
        }
        
        # Store investigation
        self.active_investigations[investigation_id] = investigation
        
        self.logger.info(f"Started investigation {investigation_id} for {len(entities)} entities")
        return investigation_id
    
    async def _perform_investigation(
        self,
        investigation_id: str,
        entities: List[str],
        investigation_type: str,
        depth: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """
        Perform the investigation steps.
        
        Args:
            investigation_id: ID of the investigation
            entities: Entities to investigate
            investigation_type: Type of investigation
            depth: Investigation depth
            platforms: Platforms to investigate on
            
        Returns:
            Investigation results
        """
        investigation = self.active_investigations[investigation_id]
        results = {
            'entities_analyzed': [],
            'relationships_discovered': [],
            'threats_identified': [],
            'timeline_events': [],
            'cross_platform_findings': []
        }
        
        try:
            # Step 1: Entity Resolution
            self.logger.info(f"Step 1: Entity resolution for investigation {investigation_id}")
            entity_results = await self._resolve_entities(entities)
            results['entities_analyzed'] = entity_results
            investigation['steps_completed'].append('entity_resolution')
            
            # Step 2: Link Analysis
            self.logger.info(f"Step 2: Link analysis for investigation {investigation_id}")
            link_results = await self._analyze_links(entity_results, depth)
            results['relationships_discovered'] = link_results
            investigation['steps_completed'].append('link_analysis')
            
            # Step 3: Cross-Platform Analysis
            self.logger.info(f"Step 3: Cross-platform analysis for investigation {investigation_id}")
            cross_platform_results = await self._cross_platform_analysis(
                entity_results, platforms
            )
            results['cross_platform_findings'] = cross_platform_results
            investigation['steps_completed'].append('cross_platform_analysis')
            
            # Step 4: Threat Assessment
            self.logger.info(f"Step 4: Threat assessment for investigation {investigation_id}")
            threat_results = await self._assess_threats(
                entity_results, link_results, cross_platform_results
            )
            results['threats_identified'] = threat_results
            investigation['steps_completed'].append('threat_assessment')
            
            # Step 5: Timeline Reconstruction
            self.logger.info(f"Step 5: Timeline reconstruction for investigation {investigation_id}")
            timeline_results = await self._reconstruct_timeline(
                entity_results, link_results, cross_platform_results
            )
            results['timeline_events'] = timeline_results
            investigation['steps_completed'].append('timeline_reconstruction')
            
            # Update investigation with results
            investigation['findings'] = results
            investigation['status'] = 'completed'
            investigation['completed_at'] = datetime.utcnow().isoformat()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Investigation {investigation_id} failed: {e}")
            investigation['status'] = 'failed'
            investigation['error'] = str(e)
            raise
    
    async def _resolve_entities(self, entities: List[str]) -> List[Dict[str, Any]]:
        """
        Resolve entities across multiple sources.
        
        Args:
            entities: List of entities to resolve
            
        Returns:
            Resolved entity information
        """
        try:
            resolved_entities = []
            
            for entity in entities:
                # Use entity resolution component
                resolution_result = await self.entity_resolution.resolve_entity(
                    entity, self.vector_service, self.knowledge_graph
                )
                
                if resolution_result:
                    resolved_entities.append({
                        'entity': entity,
                        'resolved_info': resolution_result,
                        'confidence': resolution_result.get('confidence', 0.0),
                        'sources': resolution_result.get('sources', []),
                        'aliases': resolution_result.get('aliases', []),
                        'attributes': resolution_result.get('attributes', {})
                    })
            
            return resolved_entities
            
        except Exception as e:
            self.logger.error(f"Entity resolution failed: {e}")
            return []
    
    async def _analyze_links(
        self,
        entities: List[Dict[str, Any]],
        depth: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze links and relationships between entities.
        
        Args:
            entities: Resolved entities
            depth: Analysis depth
            
        Returns:
            Link analysis results
        """
        try:
            # Use link analysis component
            link_results = await self.link_analysis.analyze_relationships(
                entities, depth, self.knowledge_graph, self.llm_service
            )
            
            return link_results
            
        except Exception as e:
            self.logger.error(f"Link analysis failed: {e}")
            return []
    
    async def _cross_platform_analysis(
        self,
        entities: List[Dict[str, Any]],
        platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Perform cross-platform analysis.
        
        Args:
            entities: Resolved entities
            platforms: Platforms to analyze
            
        Returns:
            Cross-platform analysis results
        """
        try:
            # Use cross-platform analysis component
            cross_platform_results = await self.cross_platform.analyze_entities(
                entities, platforms, self.vector_service, self.llm_service
            )
            
            return cross_platform_results
            
        except Exception as e:
            self.logger.error(f"Cross-platform analysis failed: {e}")
            return []
    
    async def _assess_threats(
        self,
        entities: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
        cross_platform: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Assess threats based on investigation findings.
        
        Args:
            entities: Resolved entities
            links: Link analysis results
            cross_platform: Cross-platform analysis results
            
        Returns:
            Threat assessment results
        """
        try:
            if not self.llm_service:
                return []
            
            # Prepare data for threat assessment
            assessment_data = {
                'entities': entities,
                'relationships': links,
                'cross_platform_findings': cross_platform
            }
            
            # Create threat assessment prompt
            prompt = f"""
Perform threat assessment on the following investigation data:

Entities: {len(entities)} entities analyzed
Relationships: {len(links)} relationships discovered
Cross-platform findings: {len(cross_platform)} findings

Assessment data: {json.dumps(assessment_data, default=str)[:2000]}

Analyze for:
1. Potential threats and risks
2. Suspicious patterns or behaviors
3. Security implications
4. Recommended actions

Provide assessment in JSON format:
{{
    "threats": [
        {{
            "type": "threat_type",
            "severity": "low|medium|high|critical",
            "description": "threat description",
            "entities_involved": ["entity1", "entity2"],
            "evidence": ["evidence1", "evidence2"],
            "recommendations": ["rec1", "rec2"]
        }}
    ],
    "overall_risk_level": "low|medium|high|critical",
    "summary": "overall assessment summary"
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse result
            try:
                threat_assessment = json.loads(result)
                return threat_assessment.get('threats', [])
            except:
                return []
                
        except Exception as e:
            self.logger.error(f"Threat assessment failed: {e}")
            return []
    
    async def _reconstruct_timeline(
        self,
        entities: List[Dict[str, Any]],
        links: List[Dict[str, Any]],
        cross_platform: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reconstruct timeline of events.
        
        Args:
            entities: Resolved entities
            links: Link analysis results
            cross_platform: Cross-platform analysis results
            
        Returns:
            Timeline events
        """
        try:
            if not self.llm_service:
                return []
            
            # Prepare data for timeline reconstruction
            timeline_data = {
                'entities': entities,
                'relationships': links,
                'cross_platform_findings': cross_platform
            }
            
            # Create timeline reconstruction prompt
            prompt = f"""
Reconstruct a timeline of events from the following investigation data:

Entities: {len(entities)} entities
Relationships: {len(links)} relationships
Cross-platform findings: {len(cross_platform)} findings

Data: {json.dumps(timeline_data, default=str)[:2000]}

Create a chronological timeline that:
1. Orders events by time
2. Identifies key milestones
3. Shows relationships between events
4. Highlights significant findings

Provide timeline in JSON format:
{{
    "events": [
        {{
            "timestamp": "YYYY-MM-DD HH:MM:SS",
            "event_type": "event_type",
            "description": "event description",
            "entities_involved": ["entity1", "entity2"],
            "source": "source_of_information",
            "significance": "low|medium|high"
        }}
    ],
    "key_milestones": ["milestone1", "milestone2"],
    "timeline_summary": "overall timeline summary"
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=1200,
                temperature=0.3
            )
            
            # Parse result
            try:
                timeline = json.loads(result)
                return timeline.get('events', [])
            except:
                return []
                
        except Exception as e:
            self.logger.error(f"Timeline reconstruction failed: {e}")
            return []
    
    async def _complete_investigation(
        self,
        investigation_id: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete the investigation and generate final report.
        
        Args:
            investigation_id: ID of the investigation
            results: Investigation results
            
        Returns:
            Final investigation report
        """
        try:
            investigation = self.active_investigations[investigation_id]
            
            # Generate final report
            final_report = {
                'investigation_id': investigation_id,
                'summary': {
                    'entities_analyzed': len(results.get('entities_analyzed', [])),
                    'relationships_discovered': len(results.get('relationships_discovered', [])),
                    'threats_identified': len(results.get('threats_identified', [])),
                    'timeline_events': len(results.get('timeline_events', [])),
                    'cross_platform_findings': len(results.get('cross_platform_findings', []))
                },
                'findings': results,
                'recommendations': await self._generate_recommendations(results),
                'confidence_score': await self._calculate_confidence_score(results),
                'completed_at': datetime.utcnow().isoformat()
            }
            
            # Store in investigation history
            self.investigation_history.append(final_report)
            
            # Remove from active investigations
            del self.active_investigations[investigation_id]
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Investigation completion failed: {e}")
            raise
    
    async def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on investigation results."""
        try:
            if not self.llm_service:
                return ["Continue monitoring", "Review findings with team"]
            
            # Create recommendations prompt
            prompt = f"""
Generate recommendations based on investigation findings:

Entities analyzed: {len(results.get('entities_analyzed', []))}
Relationships discovered: {len(results.get('relationships_discovered', []))}
Threats identified: {len(results.get('threats_identified', []))}
Timeline events: {len(results.get('timeline_events', []))}

Provide actionable recommendations in JSON format:
{{
    "recommendations": [
        "recommendation1",
        "recommendation2",
        "recommendation3"
    ],
    "priority_actions": [
        "action1",
        "action2"
    ]
}}
"""
            
            result = await self.llm_service.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse result
            try:
                recommendations = json.loads(result)
                return recommendations.get('recommendations', [])
            except:
                return ["Continue monitoring", "Review findings with team"]
                
        except Exception as e:
            self.logger.error(f"Recommendations generation failed: {e}")
            return ["Continue monitoring", "Review findings with team"]
    
    async def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score for investigation results."""
        try:
            # Simple confidence calculation based on data quality
            total_findings = sum(len(results.get(key, [])) for key in [
                'entities_analyzed', 'relationships_discovered', 
                'threats_identified', 'timeline_events', 'cross_platform_findings'
            ])
            
            if total_findings == 0:
                return 0.0
            
            # Base confidence on number of findings and their quality
            base_confidence = min(total_findings / 50.0, 1.0)  # Normalize to 0-1
            
            # Adjust based on data sources
            if results.get('cross_platform_findings'):
                base_confidence += 0.1
            
            if results.get('threats_identified'):
                base_confidence += 0.1
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Confidence score calculation failed: {e}")
            return 0.5
    
    def _update_investigation_metrics(self, results: Dict[str, Any]):
        """Update investigation-specific metrics."""
        try:
            self.investigation_metrics['investigations_completed'] += 1
            
            summary = results.get('summary', {})
            self.investigation_metrics['entities_analyzed'] += summary.get('entities_analyzed', 0)
            self.investigation_metrics['relationships_discovered'] += summary.get('relationships_discovered', 0)
            self.investigation_metrics['threats_identified'] += summary.get('threats_identified', 0)
            
            # Update average investigation time
            if 'completed_at' in results:
                # This would need to be calculated based on start/end times
                pass
                
        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")
    
    async def get_investigation_status(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an investigation.
        
        Args:
            investigation_id: ID of the investigation
            
        Returns:
            Investigation status or None if not found
        """
        if investigation_id in self.active_investigations:
            return self.active_investigations[investigation_id]
        
        # Check in history
        for investigation in self.investigation_history:
            if investigation['investigation_id'] == investigation_id:
                return investigation
        
        return None
    
    async def get_investigation_history(self) -> List[Dict[str, Any]]:
        """
        Get investigation history.
        
        Returns:
            List of completed investigations
        """
        return self.investigation_history
    
    async def get_active_investigations(self) -> List[Dict[str, Any]]:
        """
        Get active investigations.
        
        Returns:
            List of active investigations
        """
        return list(self.active_investigations.values())