"""
OPA (Open Policy Agent) Policy Enforcer for Agent Tool Access
Implements policy-as-code for tool access control
"""

import json
import logging
from typing import Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class OPAPolicyEnforcer:
    """Enforces OPA policies for agent tool access"""

    def __init__(self, opa_url: str = "http://localhost:8181", policy_path: str = "amas/tool_access"):
        self.opa_url = opa_url
        self.policy_path = policy_path
        self.base_url = f"{opa_url}/v1/data/{policy_path}"

    async def check_tool_access(
        self,
        agent_role: str,
        tool_name: str,
        user_role: Optional[str] = None,
        environment: Optional[str] = None,
        has_human_approval: bool = False,
        approved_by: Optional[str] = None,
        recent_calls: Optional[list] = None,
        rate_limit: int = 10,
    ) -> bool:
        """Check if agent can access a tool based on policy"""

        input_data = {
            "agent_role": agent_role,
            "tool_name": tool_name,
            "user_role": user_role or "user",
            "environment": environment or "development",
            "has_human_approval": has_human_approval,
            "approved_by": approved_by or "",
            "recent_calls": recent_calls or [],
            "rate_limit": rate_limit,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/allow",
                    json={"input": input_data},
                )
                response.raise_for_status()
                result = response.json()
                return result.get("result", False)
        except httpx.HTTPError as e:
            logger.error(f"OPA policy check failed: {e}")
            # Fail closed: deny access if OPA is unavailable
            return False
        except Exception as e:
            logger.error(f"Unexpected error in OPA check: {e}")
            return False

    async def check_and_escalate(
        self,
        agent_role: str,
        tool_name: str,
        escalation_handler=None,
    ) -> bool:
        """Check access and escalate if needed"""

        # First check if allowed
        allowed = await self.check_tool_access(agent_role, tool_name)

        if allowed:
            return True

        # If not allowed and escalation handler provided, request approval
        if escalation_handler:
            logger.info(
                f"Access denied for {agent_role} to {tool_name}, requesting escalation"
            )
            approval = await escalation_handler(agent_role, tool_name)
            if approval:
                # Re-check with approval
                return await self.check_tool_access(
                    agent_role,
                    tool_name,
                    has_human_approval=True,
                    approved_by=approval.get("approved_by"),
                )

        return False


# Singleton instance
_opa_enforcer: Optional[OPAPolicyEnforcer] = None


def get_opa_enforcer() -> OPAPolicyEnforcer:
    """Get singleton OPA enforcer instance"""
    global _opa_enforcer
    if _opa_enforcer is None:
        opa_url = "http://localhost:8181"  # Configurable via env
        _opa_enforcer = OPAPolicyEnforcer(opa_url=opa_url)
    return _opa_enforcer
