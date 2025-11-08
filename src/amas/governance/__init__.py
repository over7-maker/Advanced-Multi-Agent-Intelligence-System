"""
Data Governance and Compliance Module for AMAS

Provides:
- Automatic PII detection with confidence scoring
- 5-tier data classification (Public → Top Secret)
- Compliance framework mapping (GDPR, HIPAA, PCI)
- Redaction helpers for safe logging and storage
- Compliance reporting and audit trails
"""

from .data_classifier import (
    DataClassification,
    PIIType,
    PIIDetection,
    ClassificationResult,
    PIIDetector,
    DataClassifier,
    ComplianceReporter,
    get_data_classifier,
    get_compliance_reporter,
    classify_input_data,
)

from .agent_contracts import (
    AgentRoleContract,
    ToolSchema,
    AGENT_CONTRACTS,
    validate_agent_action,
    get_contract_for_role,
    list_all_roles,
)

__all__ = [
    # Data Classification
    "DataClassification",
    "PIIType",
    "PIIDetection",
    "ClassificationResult",
    "PIIDetector",
    "DataClassifier",
    "ComplianceReporter",
    "get_data_classifier",
    "get_compliance_reporter",
    "classify_input_data",
    # Agent Contracts
    "AgentRoleContract",
    "ToolSchema",
    "AGENT_CONTRACTS",
    "validate_agent_action",
    "get_contract_for_role",
    "list_all_roles",
]
