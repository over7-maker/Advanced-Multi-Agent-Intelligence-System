"""
AMAS Security Module
Enterprise-grade security with OIDC/JWT authentication,
policy-as-code authorization, and comprehensive audit logging.
"""

from .auth.jwt_middleware import (
    JWTMiddleware,
    SecurityHeadersMiddleware,
    AMASHTTPBearer,
    SecureAuthenticationManager,
    auth_context,
    token_blacklist,
    require_role,
    require_scope,
)
from .policies.opa_integration import (
    OPAClient,
    CachedOPAClient,
    AMASPolicyEngine,
    PolicyDecision,
    PolicyEvaluationResult,
    get_policy_engine,
    configure_policy_engine,
)
from .audit.audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditStatus,
    PIIRedactor,
    initialize_audit_logger,
    get_audit_logger,
    audit_operation,
)

__all__ = [
    # Authentication
    "JWTMiddleware",
    "SecurityHeadersMiddleware",
    "AMASHTTPBearer",
    "SecureAuthenticationManager",
    "auth_context",
    "token_blacklist",
    "require_role",
    "require_scope",
    # Authorization
    "OPAClient",
    "CachedOPAClient",
    "AMASPolicyEngine",
    "PolicyDecision",
    "PolicyEvaluationResult",
    "get_policy_engine",
    "configure_policy_engine",
    # Audit
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditStatus",
    "PIIRedactor",
    "initialize_audit_logger",
    "get_audit_logger",
    "audit_operation",
]
