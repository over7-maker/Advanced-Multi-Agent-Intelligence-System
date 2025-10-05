"""
Test agent implementations
"""

import pytest
import asyncio
from typing import Dict, Any

from amas.agents.osint.osint_agent import OSINTAgent
from amas.agents.investigation.investigation_agent import InvestigationAgent
from amas.agents.forensics.forensics_agent import ForensicsAgent
from amas.agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from amas.agents.reverse_engineering.reverse_engineering_agent import (
    ReverseEngineeringAgent,
)
from amas.agents.metadata.metadata_agent import MetadataAgent
from amas.agents.reporting.reporting_agent import ReportingAgent
from amas.agents.technology_monitor.technology_monitor_agent import (
    TechnologyMonitorAgent,
)


class TestOSINTAgent:
    """Test OSINT agent functionality"""

    @pytest.fixture
    def osint_agent(self):
        """Create OSINT agent instance"""
        return OSINTAgent(agent_id="test_osint", name="Test OSINT Agent")

    @pytest.mark.asyncio
    async def test_agent_initialization(self, osint_agent):
        """Test agent initialization"""
        assert osint_agent.agent_id == "test_osint"
        assert osint_agent.name == "Test OSINT Agent"
        assert "intelligence_collection" in osint_agent.capabilities
        assert "social_media_monitoring" in osint_agent.capabilities

    @pytest.mark.asyncio
    async def test_task_validation(self, osint_agent):
        """Test task validation"""
        valid_task = {"type": "osint", "description": "Collect intelligence on target"}
        invalid_task = {"type": "forensics", "description": "Analyze disk image"}

        assert await osint_agent.validate_task(valid_task) == True
        assert await osint_agent.validate_task(invalid_task) == False

    @pytest.mark.asyncio
    async def test_task_execution(self, osint_agent):
        """Test task execution"""
        task = {
            "id": "test_task_1",
            "type": "intelligence_collection",
            "description": "Collect intelligence on target",
            "parameters": {"target": "test_target", "sources": ["web", "social_media"]},
        }

        result = await osint_agent.execute_task(task)
        assert result["success"] == True
        assert "timestamp" in result


class TestInvestigationAgent:
    """Test Investigation agent functionality"""

    @pytest.fixture
    def investigation_agent(self):
        """Create Investigation agent instance"""
        return InvestigationAgent(
            agent_id="test_investigation", name="Test Investigation Agent"
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, investigation_agent):
        """Test agent initialization"""
        assert investigation_agent.agent_id == "test_investigation"
        assert investigation_agent.name == "Test Investigation Agent"
        assert "case_management" in investigation_agent.capabilities
        assert "evidence_analysis" in investigation_agent.capabilities

    @pytest.mark.asyncio
    async def test_task_execution(self, investigation_agent):
        """Test task execution"""
        task = {
            "id": "test_task_2",
            "type": "case_management",
            "description": "Manage investigation case",
            "parameters": {"case_id": "case_001", "priority": "high"},
        }

        result = await investigation_agent.execute_task(task)
        assert result["success"] == True
        assert "timestamp" in result


class TestForensicsAgent:
    """Test Forensics agent functionality"""

    @pytest.fixture
    def forensics_agent(self):
        """Create Forensics agent instance"""
        return ForensicsAgent(agent_id="test_forensics", name="Test Forensics Agent")

    @pytest.mark.asyncio
    async def test_agent_initialization(self, forensics_agent):
        """Test agent initialization"""
        assert forensics_agent.agent_id == "test_forensics"
        assert forensics_agent.name == "Test Forensics Agent"
        assert "evidence_acquisition" in forensics_agent.capabilities
        assert "malware_analysis" in forensics_agent.capabilities

    @pytest.mark.asyncio
    async def test_evidence_acquisition(self, forensics_agent):
        """Test evidence acquisition task"""
        task = {
            "id": "test_task_3",
            "type": "evidence_acquisition",
            "description": "Acquire evidence from disk",
            "parameters": {"source": "/dev/sda1", "acquisition_type": "disk_image"},
        }

        result = await forensics_agent.execute_task(task)
        assert result["success"] == True
        assert "evidence_id" in result
        assert "status" in result


class TestDataAnalysisAgent:
    """Test Data Analysis agent functionality"""

    @pytest.fixture
    def data_analysis_agent(self):
        """Create Data Analysis agent instance"""
        return DataAnalysisAgent(
            agent_id="test_data_analysis", name="Test Data Analysis Agent"
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, data_analysis_agent):
        """Test agent initialization"""
        assert data_analysis_agent.agent_id == "test_data_analysis"
        assert data_analysis_agent.name == "Test Data Analysis Agent"
        assert "statistical_analysis" in data_analysis_agent.capabilities
        assert "anomaly_detection" in data_analysis_agent.capabilities

    @pytest.mark.asyncio
    async def test_statistical_analysis(self, data_analysis_agent):
        """Test statistical analysis task"""
        task = {
            "id": "test_task_4",
            "type": "statistical_analysis",
            "description": "Perform statistical analysis",
            "parameters": {
                "dataset_id": "test_data",
                "data": [
                    {"value": i, "category": "A" if i % 2 == 0 else "B"}
                    for i in range(10)
                ],
                "column": "value",
            },
        }

        result = await data_analysis_agent.execute_task(task)
        assert result["success"] == True
        assert "statistics" in result


class TestReverseEngineeringAgent:
    """Test Reverse Engineering agent functionality"""

    @pytest.fixture
    def reverse_engineering_agent(self):
        """Create Reverse Engineering agent instance"""
        return ReverseEngineeringAgent(
            agent_id="test_reverse_engineering", name="Test Reverse Engineering Agent"
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, reverse_engineering_agent):
        """Test agent initialization"""
        assert reverse_engineering_agent.agent_id == "test_reverse_engineering"
        assert reverse_engineering_agent.name == "Test Reverse Engineering Agent"
        assert "static_analysis" in reverse_engineering_agent.capabilities
        assert "malware_disassembly" in reverse_engineering_agent.capabilities

    @pytest.mark.asyncio
    async def test_static_analysis(self, reverse_engineering_agent):
        """Test static analysis task"""
        task = {
            "id": "test_task_5",
            "type": "static_analysis",
            "description": "Perform static analysis",
            "parameters": {"target": "malware.exe"},
        }

        result = await reverse_engineering_agent.execute_task(task)
        assert result["success"] == True
        assert "report_id" in result


class TestMetadataAgent:
    """Test Metadata agent functionality"""

    @pytest.fixture
    def metadata_agent(self):
        """Create Metadata agent instance"""
        return MetadataAgent(agent_id="test_metadata", name="Test Metadata Agent")

    @pytest.mark.asyncio
    async def test_agent_initialization(self, metadata_agent):
        """Test agent initialization"""
        assert metadata_agent.agent_id == "test_metadata"
        assert metadata_agent.name == "Test Metadata Agent"
        assert "metadata_extraction" in metadata_agent.capabilities
        assert "steganography_detection" in metadata_agent.capabilities

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, metadata_agent):
        """Test metadata extraction task"""
        task = {
            "id": "test_task_6",
            "type": "metadata_extraction",
            "description": "Extract metadata from files",
            "parameters": {"file_paths": ["/path/to/file1.txt", "/path/to/file2.pdf"]},
        }

        result = await metadata_agent.execute_task(task)
        assert result["success"] == True
        assert "metadata_results" in result


class TestReportingAgent:
    """Test Reporting agent functionality"""

    @pytest.fixture
    def reporting_agent(self):
        """Create Reporting agent instance"""
        return ReportingAgent(agent_id="test_reporting", name="Test Reporting Agent")

    @pytest.mark.asyncio
    async def test_agent_initialization(self, reporting_agent):
        """Test agent initialization"""
        assert reporting_agent.agent_id == "test_reporting"
        assert reporting_agent.name == "Test Reporting Agent"
        assert "report_generation" in reporting_agent.capabilities
        assert "data_visualization" in reporting_agent.capabilities

    @pytest.mark.asyncio
    async def test_report_generation(self, reporting_agent):
        """Test report generation task"""
        task = {
            "id": "test_task_7",
            "type": "report_generation",
            "description": "Generate intelligence report",
            "parameters": {
                "report_type": "intelligence_report",
                "data": {"findings": ["Finding 1", "Finding 2"]},
                "format": "pdf",
            },
        }

        result = await reporting_agent.execute_task(task)
        assert result["success"] == True
        assert "report_id" in result


class TestTechnologyMonitorAgent:
    """Test Technology Monitor agent functionality"""

    @pytest.fixture
    def technology_monitor_agent(self):
        """Create Technology Monitor agent instance"""
        return TechnologyMonitorAgent(
            agent_id="test_technology_monitor", name="Test Technology Monitor Agent"
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, technology_monitor_agent):
        """Test agent initialization"""
        assert technology_monitor_agent.agent_id == "test_technology_monitor"
        assert technology_monitor_agent.name == "Test Technology Monitor Agent"
        assert "technology_trend_monitoring" in technology_monitor_agent.capabilities
        assert "ai_advancement_tracking" in technology_monitor_agent.capabilities

    @pytest.mark.asyncio
    async def test_technology_trend_monitoring(self, technology_monitor_agent):
        """Test technology trend monitoring task"""
        task = {
            "id": "test_task_8",
            "type": "technology_trend_monitoring",
            "description": "Monitor technology trends",
            "parameters": {
                "technologies": ["AI", "Quantum Computing"],
                "timeframe": "monthly",
            },
        }

        result = await technology_monitor_agent.execute_task(task)
        assert result["success"] == True
        assert "trends" in result
