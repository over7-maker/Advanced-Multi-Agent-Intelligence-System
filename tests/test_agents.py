"""
Test suite for AMAS Intelligence Agents
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from agents.osint.osint_agent import OSINTAgent
from agents.investigation.investigation_agent import InvestigationAgent
from agents.forensics.forensics_agent import ForensicsAgent
from agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from agents.reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from agents.metadata.metadata_agent import MetadataAgent
from agents.reporting.reporting_agent import ReportingAgent
from agents.technology_monitor.technology_monitor_agent import TechnologyMonitorAgent

class TestOSINTAgent:
    """Test OSINT Agent"""
    
    @pytest.fixture
    async def osint_agent(self):
        """Create OSINT agent for testing"""
        agent = OSINTAgent(
            agent_id="test_osint_001",
            name="Test OSINT Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_web_scraping_task(self, osint_agent):
        """Test web scraping task"""
        task = {
            'id': 'test_1',
            'type': 'web_scraping',
            'description': 'Scrape websites for intelligence',
            'parameters': {
                'urls': ['https://example.com'],
                'keywords': ['cyber', 'threat'],
                'max_pages': 5
            }
        }
        
        result = await osint_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'web_scraping'
        assert 'data' in result
        assert 'analysis' in result
    
    @pytest.mark.asyncio
    async def test_social_media_monitoring(self, osint_agent):
        """Test social media monitoring task"""
        task = {
            'id': 'test_2',
            'type': 'social_media_monitoring',
            'description': 'Monitor social media platforms',
            'parameters': {
                'platforms': ['twitter', 'reddit'],
                'keywords': ['cyber', 'threat'],
                'time_range': '24h'
            }
        }
        
        result = await osint_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'social_media_monitoring'
        assert 'data' in result
        assert 'analysis' in result
    
    @pytest.mark.asyncio
    async def test_domain_analysis(self, osint_agent):
        """Test domain analysis task"""
        task = {
            'id': 'test_3',
            'type': 'domain_analysis',
            'description': 'Analyze domain for threats',
            'parameters': {
                'domain': 'suspicious.example.com',
                'analysis_type': 'comprehensive'
            }
        }
        
        result = await osint_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'domain_analysis'
        assert 'data' in result
        assert result['domain'] == 'suspicious.example.com'

class TestInvestigationAgent:
    """Test Investigation Agent"""
    
    @pytest.fixture
    async def investigation_agent(self):
        """Create Investigation agent for testing"""
        agent = InvestigationAgent(
            agent_id="test_investigation_001",
            name="Test Investigation Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_link_analysis(self, investigation_agent):
        """Test link analysis task"""
        task = {
            'id': 'test_1',
            'type': 'link_analysis',
            'description': 'Analyze entity relationships',
            'parameters': {
                'entities': ['Entity1', 'Entity2', 'Entity3'],
                'depth': 'medium'
            }
        }
        
        result = await investigation_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'link_analysis'
        assert 'entities_analyzed' in result
        assert 'relationships' in result
    
    @pytest.mark.asyncio
    async def test_entity_resolution(self, investigation_agent):
        """Test entity resolution task"""
        task = {
            'id': 'test_2',
            'type': 'entity_resolution',
            'description': 'Resolve entity identities',
            'parameters': {
                'entities': ['Entity1', 'Entity2'],
                'threshold': 0.8
            }
        }
        
        result = await investigation_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'entity_resolution'
        assert 'entities_processed' in result
        assert 'resolved_entities' in result

class TestForensicsAgent:
    """Test Forensics Agent"""
    
    @pytest.fixture
    async def forensics_agent(self):
        """Create Forensics agent for testing"""
        agent = ForensicsAgent(
            agent_id="test_forensics_001",
            name="Test Forensics Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_evidence_acquisition(self, forensics_agent):
        """Test evidence acquisition task"""
        task = {
            'id': 'test_1',
            'type': 'evidence_acquisition',
            'description': 'Acquire evidence from source',
            'parameters': {
                'source_path': '/path/to/evidence',
                'acquisition_type': 'forensic'
            }
        }
        
        result = await forensics_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'evidence_acquisition'
        assert 'result' in result
        assert 'evidence_id' in result['result']
    
    @pytest.mark.asyncio
    async def test_file_analysis(self, forensics_agent):
        """Test file analysis task"""
        task = {
            'id': 'test_2',
            'type': 'file_analysis',
            'description': 'Analyze files for forensics',
            'parameters': {
                'file_paths': ['/path/to/file1', '/path/to/file2'],
                'analysis_depth': 'standard'
            }
        }
        
        result = await forensics_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'file_analysis'
        assert 'files_analyzed' in result
        assert 'analysis_results' in result

class TestDataAnalysisAgent:
    """Test Data Analysis Agent"""
    
    @pytest.fixture
    async def data_analysis_agent(self):
        """Create Data Analysis agent for testing"""
        agent = DataAnalysisAgent(
            agent_id="test_data_analysis_001",
            name="Test Data Analysis Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_statistical_analysis(self, data_analysis_agent):
        """Test statistical analysis task"""
        task = {
            'id': 'test_1',
            'type': 'statistical_analysis',
            'description': 'Perform statistical analysis',
            'parameters': {
                'data': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'analysis_type': 'descriptive'
            }
        }
        
        result = await data_analysis_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'statistical_analysis'
        assert 'statistics' in result
        assert 'data_points' in result
    
    @pytest.mark.asyncio
    async def test_anomaly_detection(self, data_analysis_agent):
        """Test anomaly detection task"""
        task = {
            'id': 'test_2',
            'type': 'anomaly_detection',
            'description': 'Detect anomalies in data',
            'parameters': {
                'data': [1, 2, 3, 4, 5, 100, 6, 7, 8, 9, 10],
                'threshold': 0.8
            }
        }
        
        result = await data_analysis_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'anomaly_detection'
        assert 'anomalies_found' in result
        assert 'anomalies' in result

class TestReportingAgent:
    """Test Reporting Agent"""
    
    @pytest.fixture
    async def reporting_agent(self):
        """Create Reporting agent for testing"""
        agent = ReportingAgent(
            agent_id="test_reporting_001",
            name="Test Reporting Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_report_generation(self, reporting_agent):
        """Test report generation task"""
        task = {
            'id': 'test_1',
            'type': 'report_generation',
            'description': 'Generate intelligence report',
            'parameters': {
                'data': {'findings': ['Finding1', 'Finding2']},
                'report_type': 'intelligence',
                'output_format': 'pdf'
            }
        }
        
        result = await reporting_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'report_generation'
        assert 'report_content' in result
        assert 'output_format' in result
    
    @pytest.mark.asyncio
    async def test_executive_summary(self, reporting_agent):
        """Test executive summary generation"""
        task = {
            'id': 'test_2',
            'type': 'executive_summary',
            'description': 'Generate executive summary',
            'parameters': {
                'data': {'findings': ['Finding1', 'Finding2']},
                'audience': 'executives'
            }
        }
        
        result = await reporting_agent.execute_task(task)
        
        assert result['success'] is True
        assert result['task_type'] == 'executive_summary'
        assert 'summary' in result
        assert 'audience' in result['summary']

class TestAgentIntegration:
    """Test agent integration"""
    
    @pytest.mark.asyncio
    async def test_agent_communication(self):
        """Test agent communication"""
        # Create multiple agents
        osint_agent = OSINTAgent(
            agent_id="test_osint_001",
            name="Test OSINT Agent"
        )
        
        investigation_agent = InvestigationAgent(
            agent_id="test_investigation_001",
            name="Test Investigation Agent"
        )
        
        await osint_agent.start()
        await investigation_agent.start()
        
        try:
            # Test agent status
            osint_status = await osint_agent.get_status()
            investigation_status = await investigation_agent.get_status()
            
            assert osint_status['agent_id'] == 'test_osint_001'
            assert investigation_status['agent_id'] == 'test_investigation_001'
            
            # Test agent capabilities
            osint_capabilities = await osint_agent.get_capabilities()
            investigation_capabilities = await investigation_agent.get_capabilities()
            
            assert len(osint_capabilities) > 0
            assert len(investigation_capabilities) > 0
            
        finally:
            await osint_agent.stop()
            await investigation_agent.stop()
    
    @pytest.mark.asyncio
    async def test_agent_health_check(self):
        """Test agent health check"""
        agent = OSINTAgent(
            agent_id="test_health_001",
            name="Test Health Agent"
        )
        
        await agent.start()
        
        try:
            health = await agent.health_check()
            
            assert 'status' in health
            assert 'timestamp' in health
            
        finally:
            await agent.stop()

if __name__ == "__main__":
    pytest.main([__file__])