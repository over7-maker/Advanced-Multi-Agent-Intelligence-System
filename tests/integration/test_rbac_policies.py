"""
Integration tests for RBAC policies and OPA integration
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.amas.security.policies.opa_integration import (
    OPAClient,
    CachedOPAClient,
    AMASPolicyEngine,
    PolicyDecision,
    PolicyEvaluationResult,
    configure_policy_engine,
    get_policy_engine,
)


@pytest.fixture
def mock_opa_response():
    """Mock OPA server response"""
    return {
        "result": {
            "allow": True,
            "reason": "User has required role",
            "metadata": {
                "user_id": "test-user",
                "agent_id": "agent-123",
                "action": "execute"
            }
        }
    }


@pytest.fixture
def opa_client():
    """Create OPA client instance"""
    return OPAClient(
        opa_url="http://localhost:8181",
        timeout_seconds=5.0,
        retry_attempts=3
    )


@pytest.fixture
def policy_engine(opa_client):
    """Create policy engine instance"""
    return AMASPolicyEngine(opa_client)


class TestOPAClient:
    """Test OPA client integration"""
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_success(self, opa_client, mock_opa_response):
        """Test successful policy evaluation"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_opa_response
            mock_response.elapsed.total_seconds.return_value = 0.1
            
            mock_client_instance.post.return_value = mock_response
            
            result = await opa_client.evaluate_policy(
                policy_path="agent.access",
                input_data={
                    "user_id": "test-user",
                    "agent_id": "agent-123",
                    "action": "execute"
                }
            )
            
            assert result.allowed is True
            assert result.decision == PolicyDecision.ALLOW
            assert result.reason == "User has required role"
            assert result.metadata is not None
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_denied(self, opa_client):
        """Test policy evaluation that denies access"""
        mock_deny_response = {
            "result": {
                "allow": False,
                "reason": "Insufficient permissions"
            }
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_deny_response
            mock_response.elapsed.total_seconds.return_value = 0.1
            
            mock_client_instance.post.return_value = mock_response
            
            result = await opa_client.evaluate_policy(
                policy_path="agent.access",
                input_data={
                    "user_id": "test-user",
                    "agent_id": "agent-123",
                    "action": "delete"
                }
            )
            
            assert result.allowed is False
            assert result.decision == PolicyDecision.DENY
            assert "Insufficient" in result.reason
    
    @pytest.mark.asyncio
    async def test_check_agent_access(self, opa_client, mock_opa_response):
        """Test agent access check"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_opa_response
            mock_response.elapsed.total_seconds.return_value = 0.05
            
            mock_client_instance.post.return_value = mock_response
            
            result = await opa_client.check_agent_access(
                user_id="test-user",
                agent_id="agent-123",
                action="execute"
            )
            
            assert result.allowed is True
            assert result.evaluation_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_check_tool_permission(self, opa_client):
        """Test tool permission check"""
        mock_response = {
            "result": {
                "allow": True,
                "metadata": {
                    "tool_name": "web_search",
                    "parameter_count": 2
                }
            }
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = mock_response
            response.elapsed.total_seconds.return_value = 0.05
            
            mock_client_instance.post.return_value = response
            
            result = await opa_client.check_tool_permission(
                user_id="test-user",
                agent_id="agent-123",
                tool_name="web_search",
                tool_params={"query": "test", "limit": 10}
            )
            
            assert result.allowed is True
    
    @pytest.mark.asyncio
    async def test_opa_retry_logic(self, opa_client):
        """Test that OPA client retries on failure"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # First call fails, second succeeds
            mock_response_fail = MagicMock()
            mock_response_fail.status_code = 500
            
            mock_response_success = MagicMock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = {"result": {"allow": True}}
            mock_response_success.elapsed.total_seconds.return_value = 0.1
            
            mock_client_instance.post.side_effect = [
                mock_response_fail,
                mock_response_success
            ]
            
            result = await opa_client.evaluate_policy(
                policy_path="agent.access",
                input_data={"user_id": "test-user", "agent_id": "agent-123", "action": "read"}
            )
            
            assert result.allowed is True
            assert mock_client_instance.post.call_count == 2  # Retried once
    
    @pytest.mark.asyncio
    async def test_opa_timeout_handling(self, opa_client):
        """Test OPA timeout handling"""
        import asyncio
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            mock_client_instance.post.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await opa_client.evaluate_policy(
                policy_path="agent.access",
                input_data={"user_id": "test-user", "agent_id": "agent-123", "action": "read"}
            )
            
            assert result.decision == PolicyDecision.ERROR
            assert result.allowed is False
            assert "timeout" in result.reason.lower() or "failed" in result.reason.lower()


class TestCachedOPAClient:
    """Test cached OPA client"""
    
    @pytest.mark.asyncio
    async def test_policy_caching(self):
        """Test that policy results are cached"""
        cached_client = CachedOPAClient(
            opa_url="http://localhost:8181",
            cache_ttl=300,
            cache_size=1000
        )
        
        mock_response = {
            "result": {
                "allow": True,
                "reason": "Cached result"
            }
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = mock_response
            response.elapsed.total_seconds.return_value = 0.1
            
            mock_client_instance.post.return_value = response
            
            input_data = {"user_id": "test-user", "agent_id": "agent-123", "action": "read"}
            
            # First call - should hit OPA
            result1 = await cached_client.evaluate_policy("agent.access", input_data)
            assert result1.allowed is True
            assert mock_client_instance.post.call_count == 1
            
            # Second call - should use cache
            result2 = await cached_client.evaluate_policy("agent.access", input_data)
            assert result2.allowed is True
            # Should still be 1 call due to caching
            assert mock_client_instance.post.call_count == 1


class TestAMASPolicyEngine:
    """Test AMAS policy engine"""
    
    @pytest.mark.asyncio
    async def test_authorize_agent_execution(self, policy_engine):
        """Test agent execution authorization"""
        with patch.object(policy_engine.opa_client, 'check_agent_access') as mock_check:
            mock_check.return_value = PolicyEvaluationResult(
                decision=PolicyDecision.ALLOW,
                allowed=True,
                reason="Access granted"
            )
            
            with patch.object(policy_engine.opa_client, 'evaluate_policy') as mock_eval:
                mock_eval.return_value = PolicyEvaluationResult(
                    decision=PolicyDecision.ALLOW,
                    allowed=True,
                    reason="Data policy compliant"
                )
                
                result = await policy_engine.authorize_agent_execution(
                    user_id="test-user",
                    agent_id="agent-123",
                    operation="execute",
                    input_data={"query": "test"}
                )
                
                assert result.allowed is True
                assert result.decision == PolicyDecision.ALLOW
                assert mock_check.call_count == 1
                assert mock_eval.call_count == 1
    
    @pytest.mark.asyncio
    async def test_authorize_agent_execution_denied(self, policy_engine):
        """Test agent execution authorization denied"""
        with patch.object(policy_engine.opa_client, 'check_agent_access') as mock_check:
            mock_check.return_value = PolicyEvaluationResult(
                decision=PolicyDecision.DENY,
                allowed=False,
                reason="Insufficient permissions"
            )
            
            result = await policy_engine.authorize_agent_execution(
                user_id="test-user",
                agent_id="agent-123",
                operation="execute",
                input_data={}
            )
            
            assert result.allowed is False
            assert result.decision == PolicyDecision.DENY
    
    @pytest.mark.asyncio
    async def test_check_bulk_permissions(self, policy_engine):
        """Test bulk permission checking"""
        with patch.object(policy_engine.opa_client, 'check_agent_access') as mock_check:
            mock_check.return_value = PolicyEvaluationResult(
                decision=PolicyDecision.ALLOW,
                allowed=True
            )
            
            requests = [
                {
                    "type": "agent_access",
                    "agent_id": "agent-1",
                    "action": "read"
                },
                {
                    "type": "agent_access",
                    "agent_id": "agent-2",
                    "action": "execute"
                }
            ]
            
            results = await policy_engine.check_bulk_permissions(
                user_id="test-user",
                requests=requests
            )
            
            assert len(results) == 2
            assert all(r.allowed for r in results)
            assert mock_check.call_count == 2


class TestPolicyIntegration:
    """Integration tests for policy system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_authorization_flow(self):
        """Test complete authorization flow from request to policy evaluation"""
        # This would test the full integration with actual OPA server
        # For now, we'll mock it
        
        policy_engine = get_policy_engine()
        
        with patch.object(policy_engine.opa_client, 'check_agent_access') as mock_check:
            mock_check.return_value = PolicyEvaluationResult(
                decision=PolicyDecision.ALLOW,
                allowed=True,
                reason="User has agent_user role",
                metadata={
                    "roles": ["agent_user"],
                    "evaluated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            result = await policy_engine.authorize_agent_execution(
                user_id="test-user-123",
                agent_id="research-agent",
                operation="execute",
                input_data={"query": "test query"}
            )
            
            # In test environment, OPA may not be available, so we check for allowed or error
            if result.decision == "error":
                # OPA connection failed - skip test or use fallback
                pytest.skip("OPA server not available in test environment")
            
            assert result.allowed is True
            assert "agent_user" in str(result.metadata or {})
