"""
AMAS CrewAI Integration Tests

Comprehensive test suite for CrewAI framework integration:
- Crew member initialization and role assignment
- Mission planning and execution
- Team collaboration and coordination
- Tool integration and usage
- Performance monitoring and optimization
- Fallback implementation testing

Validates enterprise-grade team-based agent collaboration.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

# Import CrewAI components
from agents.crew.amas_crew import (
    AMASIntelligenceCrew, CrewMember, CrewMission, IntelligenceMissionTemplates
)
from tools.amas_tools import AMASToolRegistry, ToolDefinition


class TestAMASIntelligenceCrew:
    """Test suite for AMAS Intelligence Crew"""
    
    @pytest.fixture
    async def intelligence_crew(self):
        """Create intelligence crew for testing"""
        config = {
            'crew_size_limit': 10,
            'mission_timeout_minutes': 120
        }
        
        # Mock AMAS system
        mock_amas = Mock()
        mock_amas.agents = {
            'osint_agent': Mock(),
            'analysis_agent': Mock(),
            'investigation_agent': Mock(),
            'reporting_agent': Mock()
        }
        
        # Configure mock agents
        for agent_id, agent in mock_amas.agents.items():
            agent.capabilities = [agent_id.split('_')[0]]
            agent.process_task = AsyncMock(return_value={
                'success': True,
                'confidence': 0.8,
                'result': f'Mock result from {agent_id}'
            })
        
        crew = AMASIntelligenceCrew(config, mock_amas)
        return crew
    
    @pytest.mark.asyncio
    async def test_crew_initialization(self, intelligence_crew):
        """Test intelligence crew initialization"""
        assert intelligence_crew is not None
        assert hasattr(intelligence_crew, 'crew_members')
        assert hasattr(intelligence_crew, 'role_definitions')
        assert hasattr(intelligence_crew, 'tool_registry')
        
        # Check role definitions
        assert 'orchestrator' in intelligence_crew.role_definitions
        assert 'researcher' in intelligence_crew.role_definitions
        assert 'analyst' in intelligence_crew.role_definitions
        assert 'critic' in intelligence_crew.role_definitions
        assert 'writer' in intelligence_crew.role_definitions
        
        # Check role definition structure
        orchestrator_role = intelligence_crew.role_definitions['orchestrator']
        assert 'role' in orchestrator_role
        assert 'goal' in orchestrator_role
        assert 'backstory' in orchestrator_role
        assert 'capabilities' in orchestrator_role
        assert 'cognitive_bias' in orchestrator_role
    
    @pytest.mark.asyncio
    async def test_crew_composition_determination(self, intelligence_crew):
        """Test optimal crew composition determination"""
        # OSINT-focused mission
        osint_mission = CrewMission(
            mission_id="test_osint",
            name="OSINT Collection Test",
            description="Collect comprehensive open-source intelligence on target domain",
            objectives=["Research target domain", "Gather social media intelligence"]
        )
        
        composition = await intelligence_crew._determine_optimal_crew_composition(osint_mission)
        
        assert 'orchestrator' in composition
        assert 'researcher' in composition
        assert len(composition) >= 3  # Minimum viable crew
        
        # Analysis-focused mission
        analysis_mission = CrewMission(
            mission_id="test_analysis",
            name="Data Analysis Test",
            description="Analyze collected data for patterns and correlations",
            objectives=["Analyze threat patterns", "Correlate multiple data sources"]
        )
        
        composition = await intelligence_crew._determine_optimal_crew_composition(analysis_mission)
        
        assert 'orchestrator' in composition
        assert 'analyst' in composition
        
        # Comprehensive mission
        comprehensive_mission = CrewMission(
            mission_id="test_comprehensive",
            name="Comprehensive Mission",
            description="Plan, research, analyze, validate, and report on intelligence target",
            objectives=[
                "Plan investigation approach",
                "Collect intelligence from multiple sources", 
                "Analyze and correlate findings",
                "Validate results for accuracy",
                "Generate comprehensive report"
            ]
        )
        
        composition = await intelligence_crew._determine_optimal_crew_composition(comprehensive_mission)
        
        # Should include all major roles for comprehensive mission
        assert 'orchestrator' in composition
        assert 'planner' in composition
        assert 'researcher' in composition
        assert 'analyst' in composition
        assert 'critic' in composition
        assert 'writer' in composition
    
    @pytest.mark.asyncio
    async def test_crew_creation(self, intelligence_crew):
        """Test crew creation for missions"""
        mission = CrewMission(
            mission_id="test_mission_001",
            name="Test Intelligence Mission",
            description="Test mission for crew creation",
            objectives=["Collect intelligence", "Analyze data", "Generate report"]
        )
        
        crew_id = await intelligence_crew.create_intelligence_crew(
            mission=mission,
            crew_composition=['orchestrator', 'researcher', 'analyst', 'writer']
        )
        
        assert crew_id is not None
        assert crew_id in intelligence_crew.active_crews
        
        # Check crew details
        crew_info = intelligence_crew.active_crews[crew_id]
        assert crew_info['mission'] == mission
        assert crew_info['composition'] == ['orchestrator', 'researcher', 'analyst', 'writer']
        assert crew_info['status'] == 'created'
    
    @pytest.mark.asyncio
    async def test_mission_execution(self, intelligence_crew):
        """Test intelligence mission execution"""
        mission = CrewMission(
            mission_id="test_execution_001",
            name="Test Mission Execution",
            description="Test mission for execution validation",
            objectives=[
                "Collect target intelligence",
                "Perform threat assessment",
                "Generate intelligence report"
            ],
            context={'target': 'test.example.com', 'priority': 'high'}
        )
        
        # Execute mission
        result = await intelligence_crew.execute_intelligence_mission(mission)
        
        assert result is not None
        assert 'mission_id' in result
        assert 'status' in result
        assert result['mission_id'] == mission.mission_id
        
        # Check execution results
        if result['status'] == 'completed':
            assert 'execution_time' in result
            assert 'team_composition' in result
            assert result['execution_time'] > 0
        elif result['status'] == 'error':
            assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_agent_role_mapping(self, intelligence_crew):
        """Test mapping between crew roles and AMAS agents"""
        # Test researcher role mapping
        researcher_agent = intelligence_crew._find_amas_agent_for_role('researcher')
        if researcher_agent:
            assert 'osint' in researcher_agent.capabilities
        
        # Test analyst role mapping
        analyst_agent = intelligence_crew._find_amas_agent_for_role('analyst')
        if analyst_agent:
            assert any('analysis' in cap for cap in analyst_agent.capabilities)
        
        # Test invalid role
        invalid_agent = intelligence_crew._find_amas_agent_for_role('invalid_role')
        assert invalid_agent is None
    
    @pytest.mark.asyncio
    async def test_crew_performance_metrics(self, intelligence_crew):
        """Test crew performance metrics tracking"""
        initial_metrics = intelligence_crew.crew_metrics.copy()
        
        # Simulate successful mission
        successful_result = {
            'mission_id': 'test_mission',
            'status': 'completed',
            'execution_time': 180.5,
            'performance_metrics': {
                'efficiency_score': 0.8,
                'collaboration_score': 0.9,
                'quality_score': 0.85
            }
        }
        
        await intelligence_crew._update_crew_metrics(successful_result, True)
        
        # Check metrics updated
        updated_metrics = intelligence_crew.crew_metrics
        assert updated_metrics['total_missions'] > initial_metrics['total_missions']
        assert updated_metrics['successful_missions'] > initial_metrics['successful_missions']
        assert updated_metrics['average_mission_time'] > 0
        
        # Test team effectiveness calculation
        if updated_metrics['total_missions'] > 0:
            expected_effectiveness = updated_metrics['successful_missions'] / updated_metrics['total_missions']
            assert updated_metrics['team_effectiveness'] == expected_effectiveness
    
    @pytest.mark.asyncio
    async def test_crew_status_reporting(self, intelligence_crew):
        """Test crew status reporting"""
        # Create test crew
        mission = CrewMission(
            mission_id="status_test",
            name="Status Test Mission",
            description="Test mission for status reporting",
            objectives=["Test objective"]
        )
        
        crew_id = await intelligence_crew.create_intelligence_crew(mission)
        
        # Get crew status
        status = await intelligence_crew.get_crew_status(crew_id)
        
        assert status is not None
        assert status['crew_id'] == crew_id
        assert status['mission_name'] == mission.name
        assert status['mission_id'] == mission.mission_id
        assert 'composition' in status
        assert 'created_at' in status
        assert 'team_size' in status
        
        # Test status for non-existent crew
        invalid_status = await intelligence_crew.get_crew_status('invalid_crew_id')
        assert invalid_status is None
    
    @pytest.mark.asyncio
    async def test_crew_system_status(self, intelligence_crew):
        """Test overall crew system status"""
        status = intelligence_crew.get_crew_system_status()
        
        assert 'crew_system_status' in status
        assert 'crewai_available' in status
        assert 'total_crew_members' in status
        assert 'metrics' in status
        assert 'available_roles' in status
        assert 'role_definitions' in status
        
        # Check role definitions in status
        role_defs = status['role_definitions']
        assert 'orchestrator' in role_defs
        assert 'researcher' in role_defs
        
        # Check orchestrator role definition
        orchestrator_def = role_defs['orchestrator']
        assert 'role' in orchestrator_def
        assert 'capabilities' in orchestrator_def
        assert 'cognitive_bias' in orchestrator_def


class TestAMASToolRegistry:
    """Test suite for AMAS Tool Registry"""
    
    @pytest.fixture
    def tool_registry(self):
        """Create tool registry for testing"""
        return AMASToolRegistry()
    
    @pytest.mark.asyncio
    async def test_tool_registry_initialization(self, tool_registry):
        """Test tool registry initialization"""
        assert tool_registry is not None
        assert hasattr(tool_registry, 'tools')
        assert hasattr(tool_registry, 'tool_usage_stats')
        
        # Check that built-in tools are registered
        assert len(tool_registry.tools) > 0
        
        # Check for essential tools
        essential_tools = ['web_search', 'domain_intel', 'data_analyzer', 'report_generator']
        for tool_id in essential_tools:
            assert tool_id in tool_registry.tools
    
    @pytest.mark.asyncio
    async def test_tool_execution(self, tool_registry):
        """Test tool execution and usage tracking"""
        # Execute web search tool
        result = await tool_registry.execute_tool(
            tool_id='web_search',
            parameters={
                'query': 'test search query',
                'max_results': 5
            },
            executing_agent='test_agent'
        )
        
        assert result is not None
        assert result.get('success', False) is True
        assert 'tool_metadata' in result
        assert result['tool_metadata']['tool_id'] == 'web_search'
        assert result['tool_metadata']['executing_agent'] == 'test_agent'
        
        # Check usage stats updated
        stats = tool_registry.tool_usage_stats['web_search']
        assert stats['usage_count'] > 0
        assert stats['success_count'] > 0
        assert stats['last_used'] is not None
    
    @pytest.mark.asyncio
    async def test_domain_intelligence_tool(self, tool_registry):
        """Test domain intelligence tool"""
        result = await tool_registry.execute_tool(
            tool_id='domain_intel',
            parameters={
                'domain': 'test.example.com',
                'analysis_depth': 'comprehensive'
            }
        )
        
        assert result['success'] is True
        assert 'domain_intelligence' in result
        
        domain_intel = result['domain_intelligence']
        assert domain_intel['domain'] == 'test.example.com'
        assert 'whois_data' in domain_intel
        assert 'dns_records' in domain_intel
        assert 'ssl_info' in domain_intel
        assert domain_intel['analysis_depth'] == 'comprehensive'
        
        # Comprehensive analysis should include additional data
        assert 'subdomains' in domain_intel
        assert 'technologies' in domain_intel
    
    @pytest.mark.asyncio
    async def test_threat_intelligence_tool(self, tool_registry):
        """Test threat intelligence tool"""
        result = await tool_registry.execute_tool(
            tool_id='threat_intel',
            parameters={
                'indicators': ['192.168.1.100', 'malicious.example.com'],
                'feed_types': ['virustotal', 'otx'],
                'confidence_threshold': 0.8
            }
        )
        
        assert result['success'] is True
        assert 'threat_intelligence' in result
        assert 'high_confidence_threats' in result
        
        threat_data = result['threat_intelligence']
        assert len(threat_data) == 2  # Two indicators
        
        for threat in threat_data:
            assert 'indicator' in threat
            assert 'threat_feeds' in threat
            assert 'overall_threat_score' in threat
            assert 'confidence' in threat
    
    @pytest.mark.asyncio
    async def test_data_analysis_tool(self, tool_registry):
        """Test data analysis tool"""
        test_data = {
            'records': [
                {'timestamp': '2024-01-01', 'value': 100},
                {'timestamp': '2024-01-02', 'value': 150},
                {'timestamp': '2024-01-03', 'value': 120}
            ]
        }
        
        result = await tool_registry.execute_tool(
            tool_id='data_analyzer',
            parameters={
                'data': test_data,
                'analysis_type': 'correlation',
                'confidence_threshold': 0.7
            }
        )
        
        assert result['success'] is True
        assert 'analysis_result' in result
        
        analysis = result['analysis_result']
        assert analysis['analysis_type'] == 'correlation'
        assert 'data_summary' in analysis
        assert 'findings' in analysis
        assert 'confidence' in analysis
    
    @pytest.mark.asyncio
    async def test_report_generation_tool(self, tool_registry):
        """Test report generation tool"""
        test_data = {
            'intelligence_findings': 'Comprehensive intelligence collected',
            'threat_assessment': 'Low risk identified',
            'recommendations': ['Continue monitoring', 'Implement security measures']
        }
        
        result = await tool_registry.execute_tool(
            tool_id='report_generator',
            parameters={
                'data': test_data,
                'report_type': 'intelligence',
                'format': 'markdown',
                'audience': 'executive'
            }
        )
        
        assert result['success'] is True
        assert 'report' in result
        
        report = result['report']
        assert report['format'] == 'markdown'
        assert report['type'] == 'intelligence'
        assert report['audience'] == 'executive'
        assert 'content' in report
        assert len(report['content']) > 0
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, tool_registry):
        """Test tool error handling"""
        # Test non-existent tool
        result = await tool_registry.execute_tool(
            tool_id='non_existent_tool',
            parameters={}
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'not found' in result['error'].lower()
        
        # Test tool with invalid parameters (would depend on tool validation)
        result = await tool_registry.execute_tool(
            tool_id='web_search',
            parameters={}  # Missing required 'query' parameter
        )
        
        # Should handle missing parameters gracefully
        assert 'success' in result
    
    @pytest.mark.asyncio
    async def test_tool_usage_statistics(self, tool_registry):
        """Test tool usage statistics tracking"""
        tool_id = 'web_search'
        initial_stats = tool_registry.tool_usage_stats[tool_id].copy()
        
        # Execute tool multiple times
        for i in range(3):
            await tool_registry.execute_tool(
                tool_id=tool_id,
                parameters={'query': f'test query {i}'},
                executing_agent=f'test_agent_{i}'
            )
        
        # Check stats updated
        updated_stats = tool_registry.tool_usage_stats[tool_id]
        assert updated_stats['usage_count'] > initial_stats['usage_count']
        assert updated_stats['success_count'] > initial_stats['success_count']
        assert updated_stats['average_execution_time'] >= 0
        assert updated_stats['last_used'] is not None
    
    @pytest.mark.asyncio
    async def test_tool_registry_status(self, tool_registry):
        """Test tool registry status reporting"""
        status = tool_registry.get_tool_registry_status()
        
        assert 'registry_status' in status
        assert 'total_tools' in status
        assert 'tool_categories' in status
        assert 'crewai_integration' in status
        assert 'tools_by_category' in status
        assert 'usage_statistics' in status
        
        # Check tools are categorized
        tools_by_category = status['tools_by_category']
        assert 'intelligence' in tools_by_category
        assert 'analysis' in tools_by_category
        assert 'reporting' in tools_by_category
        
        # Check tool information structure
        intelligence_tools = tools_by_category['intelligence']
        assert len(intelligence_tools) > 0
        
        for tool_info in intelligence_tools:
            assert 'tool_id' in tool_info
            assert 'name' in tool_info
            assert 'description' in tool_info
            assert 'usage_stats' in tool_info


class TestIntelligenceMissionTemplates:
    """Test suite for Intelligence Mission Templates"""
    
    @pytest.mark.asyncio
    async def test_osint_mission_template(self):
        """Test OSINT mission template creation"""
        target = "test.example.com"
        mission = IntelligenceMissionTemplates.create_comprehensive_osint_mission(target)
        
        assert mission is not None
        assert mission.name == f"Comprehensive OSINT Collection - {target}"
        assert target in mission.description
        assert len(mission.objectives) > 0
        assert 'orchestrator' in mission.crew_composition
        assert 'researcher' in mission.crew_composition
        assert 'analyst' in mission.crew_composition
        
        # Check success criteria
        assert 'min_confidence' in mission.success_criteria
        assert 'min_sources' in mission.success_criteria
        assert mission.success_criteria['min_confidence'] > 0.5
        
        # Check context
        assert mission.context['target'] == target
        assert mission.context['collection_type'] == 'comprehensive'
    
    @pytest.mark.asyncio
    async def test_threat_assessment_mission_template(self):
        """Test threat assessment mission template creation"""
        threat_indicator = "suspicious.malware.com"
        mission = IntelligenceMissionTemplates.create_threat_assessment_mission(threat_indicator)
        
        assert mission is not None
        assert threat_indicator in mission.name
        assert threat_indicator in mission.description
        assert len(mission.objectives) > 0
        
        # Check threat-specific objectives
        objectives_text = ' '.join(mission.objectives).lower()
        assert 'threat' in objectives_text
        assert 'risk' in objectives_text
        assert 'assessment' in objectives_text
        
        # Check context
        assert mission.context['threat_indicator'] == threat_indicator
        assert mission.context['assessment_type'] == 'comprehensive'
    
    @pytest.mark.asyncio
    async def test_investigation_mission_template(self):
        """Test investigation mission template creation"""
        case_description = "Suspicious network activity detected from internal systems"
        mission = IntelligenceMissionTemplates.create_investigation_mission(case_description)
        
        assert mission is not None
        assert case_description in mission.description
        assert len(mission.objectives) > 0
        
        # Check investigation-specific elements
        objectives_text = ' '.join(mission.objectives).lower()
        assert 'evidence' in objectives_text
        assert 'timeline' in objectives_text
        assert 'investigation' in objectives_text
        
        # Should include planner for investigation methodology
        assert 'planner' in mission.crew_composition
        assert 'critic' in mission.crew_composition  # For evidence validation
        
        # Check success criteria
        assert 'evidence_quality' in mission.success_criteria
        assert 'timeline_accuracy' in mission.success_criteria


class TestCrewAIIntegration:
    """Integration tests for CrewAI framework"""
    
    @pytest.mark.asyncio
    async def test_crewai_availability_handling(self):
        """Test handling of CrewAI availability"""
        # Test with CrewAI available
        crew = AMASIntelligenceCrew({}, None)
        
        # Should handle both available and unavailable scenarios
        assert hasattr(crew, 'crew_members')
        
        # Test crew system status includes CrewAI availability
        status = crew.get_crew_system_status()
        assert 'crewai_available' in status
    
    @pytest.mark.asyncio
    async def test_fallback_crew_implementation(self):
        """Test fallback crew implementation when CrewAI unavailable"""
        config = {}
        crew = AMASIntelligenceCrew(config, None)
        
        # Create mission
        mission = CrewMission(
            mission_id="fallback_test",
            name="Fallback Test Mission",
            description="Test fallback crew implementation",
            objectives=["Test objective 1", "Test objective 2"]
        )
        
        # Create fallback crew
        crew_id = await crew._create_fallback_crew(mission, ['researcher', 'analyst'])
        
        assert crew_id is not None
        assert crew_id in crew.active_crews
        
        crew_info = crew.active_crews[crew_id]
        assert crew_info['type'] == 'fallback'
        assert crew_info['composition'] == ['researcher', 'analyst']


class TestCrewPerformance:
    """Performance tests for crew operations"""
    
    @pytest.mark.asyncio
    async def test_crew_creation_performance(self):
        """Test crew creation performance"""
        config = {}
        crew = AMASIntelligenceCrew(config, None)
        
        # Create multiple crews rapidly
        start_time = time.time()
        crew_count = 10
        
        tasks = []
        for i in range(crew_count):
            mission = CrewMission(
                mission_id=f"perf_test_{i}",
                name=f"Performance Test Mission {i}",
                description=f"Performance test mission {i}",
                objectives=[f"Objective {i}"]
            )
            
            task = crew.create_intelligence_crew(mission)
            tasks.append(task)
        
        # Wait for all crew creations
        crew_ids = await asyncio.gather(*tasks)
        creation_time = time.time() - start_time
        
        # Should create crews efficiently
        assert creation_time < 5.0  # Should create 10 crews in under 5 seconds
        assert len(crew_ids) == crew_count
        assert len(set(crew_ids)) == crew_count  # All unique
        
        print(f"Crew creation performance: {crew_count / creation_time:.2f} crews/second")
    
    @pytest.mark.asyncio
    async def test_tool_execution_performance(self):
        """Test tool execution performance"""
        tool_registry = AMASToolRegistry()
        
        # Execute tools rapidly
        start_time = time.time()
        execution_count = 20
        
        tasks = []
        for i in range(execution_count):
            task = tool_registry.execute_tool(
                tool_id='data_analyzer',
                parameters={
                    'data': {'test_data': f'data_{i}'},
                    'analysis_type': 'correlation'
                },
                executing_agent=f'perf_agent_{i % 4}'  # Simulate 4 agents
            )
            tasks.append(task)
        
        # Wait for all executions
        results = await asyncio.gather(*tasks)
        execution_time = time.time() - start_time
        
        # Check performance
        successful_executions = sum(1 for result in results if result.get('success', False))
        throughput = execution_count / execution_time
        
        assert successful_executions >= execution_count * 0.9  # 90% success rate
        assert throughput > 5  # Should handle at least 5 tool executions/second
        
        print(f"Tool execution performance: {throughput:.2f} executions/second")


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=agents.crew",
        "--cov=tools.amas_tools",
        "--cov-report=html:htmlcov/crewai_tests",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ])