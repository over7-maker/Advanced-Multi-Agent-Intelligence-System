"""
Open Policy Agent (OPA) Integration for AMAS

Provides policy-as-code authorization with centralized policy management
and evaluation for agent access control.
"""

import httpx
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ERROR = "error"

@dataclass
class PolicyEvaluationResult:
    decision: PolicyDecision
    allowed: bool
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    evaluation_time_ms: float = 0.0

class OPAClient:
    """Client for Open Policy Agent policy evaluation"""
    
    def __init__(self, 
                 opa_url: str = "http://localhost:8181",
                 timeout_seconds: float = 5.0,
                 retry_attempts: int = 3):
        self.opa_url = opa_url.rstrip('/')
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(timeout=timeout_seconds)
        
        logger.info(f"OPA Client initialized for {self.opa_url}")
    
    async def evaluate_policy(self, 
                            policy_path: str, 
                            input_data: Dict[str, Any],
                            trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Evaluate policy against input data with retry logic"""
        start_time = datetime.now(timezone.utc)
        
        # Prepare the evaluation request
        url = f"{self.opa_url}/v1/data/{policy_path.replace('.', '/')}"
        payload = {
            "input": input_data
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if trace_id:
            headers["X-Trace-ID"] = trace_id
        
        last_exception = None
        
        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Evaluating policy {policy_path} (attempt {attempt + 1})")
                
                response = await self.client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                
                # Calculate evaluation time
                end_time = datetime.now(timezone.utc)
                evaluation_time_ms = (end_time - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    # Parse OPA response
                    policy_result = result_data.get("result", {})
                    
                    # Handle different response formats
                    if isinstance(policy_result, bool):
                        # Simple boolean result
                        decision = PolicyDecision.ALLOW if policy_result else PolicyDecision.DENY
                        allowed = policy_result
                        reason = None
                        conditions = None
                        metadata = None
                    elif isinstance(policy_result, dict):
                        # Structured result
                        allowed = policy_result.get("allow", False)
                        decision = PolicyDecision.ALLOW if allowed else PolicyDecision.DENY
                        reason = policy_result.get("reason")
                        conditions = policy_result.get("conditions")
                        metadata = policy_result.get("metadata")
                        
                        # Check for conditional access
                        if conditions and allowed:
                            decision = PolicyDecision.CONDITIONAL
                    else:
                        # Unexpected result format
                        logger.warning(f"Unexpected policy result format: {type(policy_result)}")
                        decision = PolicyDecision.ERROR
                        allowed = False
                        reason = "Invalid policy response format"
                        conditions = None
                        metadata = None
                    
                    result = PolicyEvaluationResult(
                        decision=decision,
                        allowed=allowed,
                        reason=reason,
                        conditions=conditions,
                        metadata=metadata,
                        evaluation_time_ms=evaluation_time_ms
                    )
                    
                    logger.debug(f"Policy evaluation completed: {policy_path} -> {decision.value}")
                    return result
                    
                elif response.status_code == 404:
                    logger.error(f"Policy not found: {policy_path}")
                    return PolicyEvaluationResult(
                        decision=PolicyDecision.ERROR,
                        allowed=False,
                        reason=f"Policy not found: {policy_path}",
                        evaluation_time_ms=evaluation_time_ms
                    )
                else:
                    # Server error, might be worth retrying
                    logger.warning(f"OPA server error (attempt {attempt + 1}): {response.status_code}")
                    last_exception = Exception(f"HTTP {response.status_code}: {response.text}")
                    
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                        continue
                
            except httpx.TimeoutException as e:
                logger.warning(f"OPA timeout (attempt {attempt + 1}): {e}")
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
            except Exception as e:
                logger.error(f"OPA client error (attempt {attempt + 1}): {e}")
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
        
        # All retry attempts failed
        end_time = datetime.now(timezone.utc)
        evaluation_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.error(f"Policy evaluation failed after {self.retry_attempts} attempts: {last_exception}")
        return PolicyEvaluationResult(
            decision=PolicyDecision.ERROR,
            allowed=False,
            reason=f"Policy evaluation failed: {last_exception}",
            evaluation_time_ms=evaluation_time_ms
        )
    
    async def check_agent_access(self, 
                               user_id: str, 
                               agent_id: str, 
                               action: str,
                               resource: Optional[str] = None,
                               trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Check if user can perform action on agent"""
        input_data = {
            "user_id": user_id,
            "agent_id": agent_id,
            "action": action,
            "resource": resource,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": trace_id
        }
        
        logger.debug(f"Checking agent access: {user_id} -> {agent_id}.{action}")
        return await self.evaluate_policy("agent.access", input_data, trace_id)
    
    async def check_tool_permission(self,
                                  user_id: str,
                                  agent_id: str, 
                                  tool_name: str,
                                  tool_params: Dict[str, Any],
                                  trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Check if agent can use tool with given parameters"""
        input_data = {
            "user_id": user_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "tool_params": tool_params,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": trace_id
        }
        
        logger.debug(f"Checking tool permission: {agent_id} -> {tool_name}")
        return await self.evaluate_policy("tool.permission", input_data, trace_id)
    
    async def check_data_access(self,
                              user_id: str,
                              data_source: str,
                              operation: str,
                              data_classification: str,
                              trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Check data access permissions"""
        input_data = {
            "user_id": user_id,
            "data_source": data_source,
            "operation": operation,
            "data_classification": data_classification,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": trace_id
        }
        
        logger.debug(f"Checking data access: {user_id} -> {data_source}.{operation}")
        return await self.evaluate_policy("data.access", input_data, trace_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OPA server health"""
        try:
            response = await self.client.get(f"{self.opa_url}/health")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "opa_url": self.opa_url,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    "status": "unhealthy",
                    "opa_url": self.opa_url,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "unreachable",
                "opa_url": self.opa_url,
                "error": str(e)
            }
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()

class PolicyCache:
    """Simple in-memory cache for policy decisions"""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_cleanup = datetime.now(timezone.utc)
    
    def _generate_cache_key(self, policy_path: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key from policy path and input"""
        # Create deterministic hash of input data
        input_json = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_json.encode()).hexdigest()[:16]
        return f"{policy_path}:{input_hash}"
    
    def get(self, policy_path: str, input_data: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
        """Get cached policy decision"""
        key = self._generate_cache_key(policy_path, input_data)
        
        self._cleanup_expired()
        
        cached_item = self._cache.get(key)
        if not cached_item:
            return None
        
        # Check if still valid
        cached_at = datetime.fromisoformat(cached_item['cached_at'])
        if (datetime.now(timezone.utc) - cached_at).seconds > self.ttl_seconds:
            del self._cache[key]
            return None
        
        logger.debug(f"Policy cache hit: {key}")
        return PolicyEvaluationResult(**cached_item['result'])
    
    def set(self, policy_path: str, input_data: Dict[str, Any], result: PolicyEvaluationResult):
        """Cache policy decision"""
        key = self._generate_cache_key(policy_path, input_data)
        
        # Don't cache error results
        if result.decision == PolicyDecision.ERROR:
            return
        
        self._cache[key] = {
            'result': {
                'decision': result.decision,
                'allowed': result.allowed,
                'reason': result.reason,
                'conditions': result.conditions,
                'metadata': result.metadata,
                'evaluation_time_ms': result.evaluation_time_ms
            },
            'cached_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Enforce max size
        if len(self._cache) > self.max_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._cache.keys())[:len(self._cache) - self.max_size]
            for key_to_remove in keys_to_remove:
                del self._cache[key_to_remove]
        
        logger.debug(f"Policy cached: {key}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now(timezone.utc)
        
        # Only cleanup every 5 minutes
        if (now - self._last_cleanup).seconds < 300:
            return
        
        expired_keys = []
        for key, cached_item in self._cache.items():
            cached_at = datetime.fromisoformat(cached_item['cached_at'])
            if (now - cached_at).seconds > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired policy cache entries")
        
        self._last_cleanup = now

class CachedOPAClient(OPAClient):
    """OPA client with built-in caching for performance"""
    
    def __init__(self, *args, cache_ttl: int = 300, cache_size: int = 1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = PolicyCache(ttl_seconds=cache_ttl, max_size=cache_size)
    
    async def evaluate_policy(self, 
                            policy_path: str, 
                            input_data: Dict[str, Any],
                            trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Evaluate policy with caching"""
        
        # Check cache first
        cached_result = self.cache.get(policy_path, input_data)
        if cached_result:
            logger.debug(f"Using cached policy result for {policy_path}")
            return cached_result
        
        # Evaluate policy
        result = await super().evaluate_policy(policy_path, input_data, trace_id)
        
        # Cache successful results
        if result.decision != PolicyDecision.ERROR:
            self.cache.set(policy_path, input_data, result)
        
        return result

class AMASPolicyEngine:
    """High-level policy engine for AMAS authorization"""
    
    def __init__(self, opa_client: OPAClient):
        self.opa_client = opa_client
        
    async def authorize_agent_execution(self,
                                      user_id: str,
                                      agent_id: str,
                                      operation: str,
                                      input_data: Dict[str, Any],
                                      trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Authorize agent execution with comprehensive checks"""
        
        # Check basic agent access
        access_result = await self.opa_client.check_agent_access(
            user_id, agent_id, operation, trace_id=trace_id
        )
        
        if not access_result.allowed:
            return access_result
        
        # Check input data policy compliance
        data_policy_input = {
            "user_id": user_id,
            "agent_id": agent_id,
            "operation": operation,
            "input_data": input_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        data_result = await self.opa_client.evaluate_policy(
            "agent.data_policy", data_policy_input, trace_id
        )
        
        if not data_result.allowed:
            return data_result
        
        return PolicyEvaluationResult(
            decision=PolicyDecision.ALLOW,
            allowed=True,
            reason="All authorization checks passed",
            metadata={
                "checks_performed": ["agent_access", "data_policy"],
                "total_evaluation_time_ms": access_result.evaluation_time_ms + data_result.evaluation_time_ms
            }
        )
    
    async def authorize_tool_usage(self,
                                 user_id: str,
                                 agent_id: str,
                                 tool_name: str,
                                 tool_parameters: Dict[str, Any],
                                 trace_id: Optional[str] = None) -> PolicyEvaluationResult:
        """Authorize tool usage with parameter validation"""
        
        result = await self.opa_client.check_tool_permission(
            user_id, agent_id, tool_name, tool_parameters, trace_id
        )
        
        # Add tool-specific metadata
        if result.metadata is None:
            result.metadata = {}
        
        result.metadata.update({
            "tool_name": tool_name,
            "parameter_count": len(tool_parameters),
            "authorized_at": datetime.now(timezone.utc).isoformat()
        })
        
        return result
    
    async def check_bulk_permissions(self,
                                   user_id: str,
                                   requests: List[Dict[str, Any]],
                                   trace_id: Optional[str] = None) -> List[PolicyEvaluationResult]:
        """Check multiple permissions in parallel"""
        
        tasks = []
        for request in requests:
            if request.get("type") == "agent_access":
                task = self.opa_client.check_agent_access(
                    user_id=user_id,
                    agent_id=request["agent_id"],
                    action=request["action"],
                    resource=request.get("resource"),
                    trace_id=trace_id
                )
            elif request.get("type") == "tool_permission":
                task = self.opa_client.check_tool_permission(
                    user_id=user_id,
                    agent_id=request["agent_id"],
                    tool_name=request["tool_name"],
                    tool_params=request.get("tool_params", {}),
                    trace_id=trace_id
                )
            else:
                # Unknown request type
                task = asyncio.create_task(
                    self._create_error_result(f"Unknown request type: {request.get('type')}")
                )
            
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        policy_results = []
        for result in results:
            if isinstance(result, Exception):
                policy_results.append(PolicyEvaluationResult(
                    decision=PolicyDecision.ERROR,
                    allowed=False,
                    reason=str(result)
                ))
            else:
                policy_results.append(result)
        
        return policy_results
    
    async def _create_error_result(self, error_message: str) -> PolicyEvaluationResult:
        """Create an error policy result"""
        return PolicyEvaluationResult(
            decision=PolicyDecision.ERROR,
            allowed=False,
            reason=error_message
        )
    
    async def get_user_permissions_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's permissions across agents and tools"""
        # This would typically query OPA for user's effective permissions
        # For now, return a basic structure
        
        input_data = {
            "user_id": user_id,
            "query_type": "permissions_summary",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        result = await self.opa_client.evaluate_policy("user.permissions", input_data)
        
        if result.allowed and result.metadata:
            return result.metadata
        else:
            return {
                "user_id": user_id,
                "agents": [],
                "tools": [],
                "error": result.reason if not result.allowed else None
            }

# Global policy engine instance
_policy_engine = None

def get_policy_engine() -> AMASPolicyEngine:
    """Get global policy engine instance"""
    global _policy_engine
    if _policy_engine is None:
        # Default OPA client configuration
        opa_client = CachedOPAClient(
            opa_url="http://localhost:8181",
            timeout_seconds=5.0,
            retry_attempts=3
        )
        _policy_engine = AMASPolicyEngine(opa_client)
    return _policy_engine

def configure_policy_engine(opa_url: str, **kwargs) -> AMASPolicyEngine:
    """Configure global policy engine"""
    global _policy_engine
    opa_client = CachedOPAClient(opa_url=opa_url, **kwargs)
    _policy_engine = AMASPolicyEngine(opa_client)
    return _policy_engine
