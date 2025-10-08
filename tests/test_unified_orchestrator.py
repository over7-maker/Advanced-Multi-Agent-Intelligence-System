"""
Comprehensive test suite for Unified Intelligence Orchestrator
"""

import asyncio
import pytest
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.amas.core.unified_orchestrator import (
    UnifiedIntelligenceOrchestrator,
    AgentType,
    TaskPriority,
    TaskStatus,
    ProviderManager
)
from src.amas.config.minimal_config import MinimalMode, get_minimal_config_manager

class TestUnifiedIntelligenceOrchestrator:
    """Test the unified orchestrator"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator for testing"""
        # Mock the services
        mock_llm_service = Mock()
        mock_vector_service = Mock()
        mock_knowledge_graph = Mock()
        mock_security_service = Mock()

        orchestrator = UnifiedIntelligenceOrchestrator(
            llm_service=mock_llm_service,
            vector_service=mock_vector_service,
            knowledge_graph=mock_knowledge_graph,
            security_service=mock_security_service
        )

        # Mock agent initialization
        with patch.object(orchestrator, '_initialize_agents') as mock_init_agents:
            mock_init_agents.return_value = None
            await orchestrator.initialize()

        return orchestrator

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.max_concurrent_tasks == 10
        assert orchestrator.task_timeout == 300

    async def test_submit_task(self, orchestrator):
        """Test task submission"""
        task_id = await orchestrator.submit_task(
            title="Test Task",
            description="Test description",
            agent_type=AgentType.OSINT,
            priority=TaskPriority.MEDIUM
        )

        assert task_id is not None
        assert len(orchestrator.task_queue) == 1
        assert orchestrator.task_queue[0].title == "Test Task"

    async def test_task_priority_ordering(self, orchestrator):
        """Test tasks are ordered by priority"""
        # Submit tasks with different priorities
        await orchestrator.submit_task("Low Task", "Description", AgentType.OSINT, TaskPriority.LOW)
        await orchestrator.submit_task("High Task", "Description", AgentType.OSINT, TaskPriority.HIGH)
        await orchestrator.submit_task("Medium Task", "Description", AgentType.OSINT, TaskPriority.MEDIUM)

        # Check ordering
        priorities = [task.priority.value for task in orchestrator.task_queue]
        assert priorities == [3, 2, 1]  # HIGH, MEDIUM, LOW

    async def test_get_task_status(self, orchestrator):
        """Test getting task status"""
        task_id = await orchestrator.submit_task(
            "Test Task", "Description", AgentType.OSINT, TaskPriority.MEDIUM
        )

        status = await orchestrator.get_task_status(task_id)
        assert status is not None
        assert status["id"] == task_id
        assert status["title"] == "Test Task"

    async def test_system_status(self, orchestrator):
        """Test system status reporting"""
        status = await orchestrator.get_system_status()

        assert "orchestrator_status" in status
        assert "total_agents" in status
        assert "active_tasks" in status
        assert "queued_tasks" in status
        assert "performance_metrics" in status

    async def test_orchestrator_shutdown(self, orchestrator):
        """Test orchestrator shutdown"""
        await orchestrator.shutdown()

        # Check that agents are stopped and queues are cleared
        assert len(orchestrator.task_queue) == 0
        assert len(orchestrator.active_tasks) == 0

class TestProviderManager:
    """Test the provider manager"""

    @pytest.fixture
    def mock_ai_config(self):
        """Create mock AI config"""
        mock_config = Mock()
        mock_config.get_enabled_providers.return_value = {}
        mock_config.get_provider_config.return_value = Mock(enabled=True)
        return mock_config

    @pytest.fixture
    def provider_manager(self, mock_ai_config):
        """Create provider manager for testing"""
        return ProviderManager(mock_ai_config)

    def test_provider_manager_initialization(self, provider_manager):
        """Test provider manager initializes correctly"""
        assert provider_manager is not None
        assert len(provider_manager.circuit_breakers) > 0
        assert len(provider_manager.provider_stats) > 0

    def test_record_success(self, provider_manager):
        """Test recording successful request"""
        from src.amas.config.ai_config import AIProvider

        provider = AIProvider.DEEPSEEK
        response_time = 1.5

        provider_manager.record_success(provider, response_time)

        stats = provider_manager.provider_stats[provider]
        assert stats["successful_requests"] == 1
        assert stats["average_response_time"] == 1.5

    def test_record_failure(self, provider_manager):
        """Test recording failed request"""
        from src.amas.config.ai_config import AIProvider

        provider = AIProvider.DEEPSEEK
        error = "Connection timeout"

        provider_manager.record_failure(provider, error)

        circuit = provider_manager.circuit_breakers[provider]
        assert circuit["failures"] == 1
        assert circuit["last_failure"] is not None

    def test_circuit_breaker_opens(self, provider_manager):
        """Test circuit breaker opens after failures"""
        from src.amas.config.ai_config import AIProvider

        provider = AIProvider.DEEPSEEK

        # Record multiple failures
        for _ in range(6):  # More than threshold
            provider_manager.record_failure(provider, "Error")

        circuit = provider_manager.circuit_breakers[provider]
        assert circuit["state"] == "open"

    def test_get_provider_health(self, provider_manager):
        """Test getting provider health status"""
        health = provider_manager.get_provider_health()

        assert isinstance(health, dict)
        assert len(health) > 0

class TestMinimalConfiguration:
    """Test minimal configuration functionality"""

    def test_minimal_config_manager(self):
        """Test minimal config manager"""
        manager = get_minimal_config_manager()

        # Test basic mode
        basic_config = manager.get_minimal_config(MinimalMode.BASIC)
        assert basic_config.mode == MinimalMode.BASIC
        assert len(basic_config.required_providers) == 3

        # Test standard mode
        standard_config = manager.get_minimal_config(MinimalMode.STANDARD)
        assert standard_config.mode == MinimalMode.STANDARD
        assert len(standard_config.required_providers) == 4

    def test_environment_validation(self):
        """Test environment validation"""
        manager = get_minimal_config_manager()

        # Mock environment with no API keys
        with patch.dict(os.environ, {}, clear=True):
            result = manager.validate_minimal_setup(MinimalMode.BASIC)

            assert result["mode"] == "basic"
            assert not result["valid"]
            assert len(result["missing_required"]) > 0

    def test_environment_setup_guide(self):
        """Test environment setup guide generation"""
        manager = get_minimal_config_manager()

        guide = manager.get_environment_setup_guide(MinimalMode.BASIC)

        assert "AMAS Minimal Configuration Setup Guide" in guide
        assert "DEEPSEEK_API_KEY" in guide
        assert "GLM_API_KEY" in guide
        assert "GROK_API_KEY" in guide

    def test_docker_compose_generation(self):
        """Test docker-compose generation"""
        manager = get_minimal_config_manager()

        compose = manager.get_minimal_docker_compose(MinimalMode.BASIC)

        assert "version: '3.8'" in compose
        assert "services:" in compose
        assert "amas:" in compose
        assert "postgres:" in compose
        assert "redis:" in compose
        assert "neo4j:" in compose

class TestOSINTAgentRealImplementation:
    """Test OSINT agent with real implementation"""

    @pytest.fixture
    async def osint_agent(self):
        """Create OSINT agent for testing"""
        from src.amas.agents.osint.osint_agent import OSINTAgent

        agent = OSINTAgent(
            agent_id="test_osint_001",
            name="Test OSINT Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()

    async def test_web_scraping_real(self, osint_agent):
        """Test real web scraping functionality"""
        # Test with a simple, reliable website
        task = {
            "type": "web_scraping",
            "parameters": {
                "urls": ["https://httpbin.org/html"],
                "keywords": ["test", "example"],
                "max_pages": 1
            }
        }

        result = await osint_agent.execute_task(task)

        assert result["success"] is True
        assert result["task_type"] == "web_scraping"
        assert result["urls_scraped"] > 0
        assert "data" in result
        assert "analysis" in result

    async def test_web_scraping_error_handling(self, osint_agent):
        """Test web scraping error handling"""
        task = {
            "type": "web_scraping",
            "parameters": {
                "urls": ["https://invalid-url-that-does-not-exist.com"],
                "keywords": ["test"],
                "max_pages": 1
            }
        }

        result = await osint_agent.execute_task(task)

        # Should handle errors gracefully
        assert "success" in result
        # May succeed with empty results or fail gracefully

    async def test_news_aggregation(self, osint_agent):
        """Test news aggregation functionality"""
        task = {
            "type": "news_aggregation",
            "parameters": {
                "keywords": ["technology", "security"],
                "max_articles": 5
            }
        }

        result = await osint_agent.execute_task(task)

        assert result["success"] is True
        assert result["task_type"] == "news_aggregation"
        assert "articles" in result
        assert "analysis" in result

class TestForensicsAgentRealImplementation:
    """Test Forensics agent with real implementation"""

    @pytest.fixture
    async def forensics_agent(self):
        """Create Forensics agent for testing"""
        from src.amas.agents.forensics.forensics_agent import ForensicsAgent

        agent = ForensicsAgent(
            agent_id="test_forensics_001",
            name="Test Forensics Agent"
        )
        await agent.start()
        yield agent
        await agent.stop()

    async def test_file_analysis_real(self, forensics_agent):
        """Test real file analysis functionality"""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("This is a test file for forensics analysis.\n")
            f.write("It contains some test content.\n")
            f.write("Email: test@example.com\n")
            f.write("URL: https://example.com\n")
            temp_file = f.name

        try:
            task_description = f"Analyze file {temp_file}"
            metadata = {"file_path": temp_file}

            result = await forensics_agent.execute_task(task_description, metadata)

            assert result["success"] is True
            assert result["task_type"] == "file_analysis"
            assert "file_info" in result
            assert "hashes" in result
            assert "content_analysis" in result
            assert "security_analysis" in result

            # Check file info
            file_info = result["file_info"]
            assert file_info["name"].endswith(".txt")
            assert file_info["size"] > 0

            # Check hashes
            hashes = result["hashes"]
            assert "md5" in hashes
            assert "sha1" in hashes
            assert "sha256" in hashes
            assert "sha512" in hashes
            assert "_security_note" in hashes

            # Check content analysis
            content_analysis = result["content_analysis"]
            assert content_analysis["is_text"] is True
            assert content_analysis["lines"] >= 4
            assert content_analysis["words"] > 0

        finally:
            # Clean up
            os.unlink(temp_file)

    async def test_hash_analysis(self, forensics_agent):
        """Test hash analysis functionality"""
        task_description = "Analyze hash d41d8cd98f00b204e9800998ecf8427e"
        metadata = {"hash": "d41d8cd98f00b204e9800998ecf8427e"}

        result = await forensics_agent.execute_task(task_description, metadata)

        assert result["success"] is True
        assert result["task_type"] == "hash_analysis"
        assert result["hash"] == "d41d8cd98f00b204e9800998ecf8427e"
        assert result["hash_type"] == "MD5"

    async def test_metadata_extraction(self, forensics_agent):
        """Test metadata extraction functionality"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name

        try:
            task_description = f"Extract metadata from {temp_file}"
            metadata = {"file_path": temp_file}

            result = await forensics_agent.execute_task(task_description, metadata)

            assert result["success"] is True
            assert result["task_type"] == "metadata_extraction"
            assert "metadata" in result

            metadata_info = result["metadata"]
            assert "file_name" in metadata_info
            assert "file_size" in metadata_info
            assert "created_time" in metadata_info
            assert "modified_time" in metadata_info

        finally:
            os.unlink(temp_file)

    async def test_file_not_found_error(self, forensics_agent):
        """Test error handling for non-existent file"""
        task_description = "Analyze file /nonexistent/file.txt"
        metadata = {"file_path": "/nonexistent/file.txt"}

        result = await forensics_agent.execute_task(task_description, metadata)

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

class TestPerformanceAndIntegration:
    """Test performance and integration aspects"""

    async def test_concurrent_task_processing(self):
        """Test handling multiple concurrent tasks"""
        # This would test the orchestrator's ability to handle multiple tasks
        # concurrently without issues
        pass

    async def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        # This would test for memory leaks during long-running operations
        pass

    async def test_error_recovery(self):
        """Test system recovers from errors gracefully"""
        # This would test that the system continues to function after errors
        pass

# Performance benchmarks
class TestBenchmarks:
    """Performance benchmark tests"""

    @pytest.mark.benchmark
    async def test_task_processing_speed(self):
        """Benchmark task processing speed"""
        # This would measure how quickly tasks are processed
        pass

    @pytest.mark.benchmark
    async def test_memory_efficiency(self):
        """Benchmark memory efficiency"""
        # This would measure memory usage patterns
        pass

    @pytest.mark.benchmark
    async def test_concurrent_load(self):
        """Benchmark concurrent load handling"""
        # This would test system performance under load
        pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
