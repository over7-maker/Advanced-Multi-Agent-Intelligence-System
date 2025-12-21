"""
Data Classification and PII Detection for AMAS

Provides automatic data classification, PII detection,
and compliance-ready data governance capabilities.

SECURITY WARNING:
================
This module handles sensitive PII data. When logging or serializing:
- NEVER log original_value fields from PIIDetection objects
- NEVER include raw PII in log messages
- ALWAYS use redacted_value or value_hash for tracking
- ALWAYS use safe_log_pii() helper for any PII-related logging

Example:
    # ❌ WRONG - Never do this:
    logger.info(f"Found email: {detection.original_value}")

    # ✅ CORRECT - Use redacted value:
    logger.info(f"Found email: {detection.redacted_value}")
    logger.info(f"PII hash: {detection.value_hash}")
"""

import re
import json
import logging
import hashlib
import time
import statistics
import asyncio
import copy
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import uuid

logger = logging.getLogger(__name__)


def safe_log_pii(detection: 'PIIDetection', message: str = "") -> str:
    """
    Create a safe log message that never includes raw PII.

    Args:
        detection: PIIDetection object
        message: Optional message prefix

    Returns:
        Safe log string with only redacted_value and hash
    """
    safe_info = (
        f"PII type: {detection.pii_type.value}, "
        f"redacted: {detection.redacted_value}, "
        f"hash: {detection.value_hash}, "
        f"confidence: {detection.confidence:.2f}"
    )

    if message:
        return f"{message} - {safe_info}"
    return safe_info


class DataClassification(str, Enum):
    """Enumeration of data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class PIIType(str, Enum):
    """Enumeration of Personally Identifiable Information types"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    API_KEY = "api_key"
    TOKEN = "token"
    BIOMETRIC = "biometric"


@dataclass
class PIIDetection:
    """Result of PII detection in data

    Security Note: Never log original_value or include it in reports.
    Always use redacted_value or value_hash for tracking purposes.
    """
    pii_type: PIIType
    confidence: float  # 0.0 to 1.0
    location: str      # Where in the data
    value_hash: str    # Hashed value for tracking (SHA-256, truncated)
    redacted_value: str
    original_value: str  # Original detected value for redaction
    context: Optional[str] = None

    def __post_init__(self):
        """Validate dataclass fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, "
                f"got {self.confidence}"
            )
        if not self.value_hash or len(self.value_hash) < 8:
            raise ValueError("value_hash must be at least 8 characters")
        if not self.redacted_value:
            raise ValueError("redacted_value cannot be empty")


@dataclass
class ClassificationResult:
    """Result of data classification analysis

    Security Note: pii_detected contains PIIDetection objects with
    original_value. Never serialize or log original_value fields.
    Use redacted_value or value_hash.
    """
    data_id: str
    classification: DataClassification
    confidence: float

    # PII analysis
    pii_detected: List[PIIDetection] = field(default_factory=list)
    pii_count: int = 0
    highest_pii_confidence: float = 0.0

    # Compliance flags
    requires_gdpr_protection: bool = False
    requires_hipaa_protection: bool = False
    requires_pci_protection: bool = False

    # Metadata
    classified_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    classifier_version: str = "1.0.0"
    processing_time_ms: float = 0.0

    def __post_init__(self):
        """Validate dataclass fields"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, "
                f"got {self.confidence}"
            )
        if self.pii_count < 0:
            raise ValueError(
                f"pii_count cannot be negative, got {self.pii_count}"
            )
        if not 0.0 <= self.highest_pii_confidence <= 1.0:
            raise ValueError(
                f"highest_pii_confidence must be between 0.0 and 1.0, "
                f"got {self.highest_pii_confidence}"
            )
        if self.processing_time_ms < 0:
            raise ValueError(
                f"processing_time_ms cannot be negative, "
                f"got {self.processing_time_ms}"
            )


class PIIDetector:
    """Advanced PII detection with configurable patterns and ML-ready"""

    def __init__(self):
        self.patterns = {
            PIIType.EMAIL: [
                re.compile(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    re.IGNORECASE
                ),
                re.compile(
                    r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b',
                    re.IGNORECASE
                )
            ],

            PIIType.PHONE: [
                re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),
                re.compile(r'\(\d{3}\)\s?\d{3}-\d{4}'),
                re.compile(r'\b\d{10}\b'),
                re.compile(r'\+1\s?\d{3}\s?\d{3}\s?\d{4}'),
                re.compile(r'\b1-\d{3}-\d{3}-\d{4}\b')
            ],

            PIIType.SSN: [
                re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
                re.compile(r'\b\d{9}\b'),
                re.compile(r'\b\d{3}\s\d{2}\s\d{4}\b')
            ],

            PIIType.CREDIT_CARD: [
                re.compile(
                    r'\b4\d{3}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}(?:\d{3})?\b'
                ),
                re.compile(r'\b4\d{12}(?:\d{3})?\b'),
                re.compile(
                    r'\b5[1-5]\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
                ),
                re.compile(r'\b5[1-5]\d{14}\b'),
                re.compile(r'\b3[47]\d{2}[- ]?\d{6}[- ]?\d{5}\b'),
                re.compile(r'\b3[47]\d{13}\b'),
                re.compile(
                    r'\b6(?:011|5\d{2})[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
                ),
                re.compile(r'\b6(?:011|5\d{2})\d{12}\b')
            ],

            PIIType.IP_ADDRESS: [
                re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
                re.compile(
                    r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
                )
            ],

            PIIType.API_KEY: [
                re.compile(r'\bsk-[A-Za-z0-9]{48}\b'),
                re.compile(r'\b[A-Za-z0-9]{32,64}\b'),
                re.compile(r'\bAIza[A-Za-z0-9_-]{35}\b'),
                re.compile(r'\bxoxb-[A-Za-z0-9-]{50,}\b')
            ],

            PIIType.TOKEN: [
                re.compile(r'\bBearer\s+[A-Za-z0-9\._-]+\b'),
                re.compile(r'\bToken\s+[A-Za-z0-9\._-]+\b'),
                re.compile(r'\bghp_[A-Za-z0-9]{36}\b'),
                re.compile(r'\baws_[A-Za-z0-9+/]{40}\b')
            ],

            PIIType.PASSPORT: [
                re.compile(r'\b[A-Z][0-9]{8}\b'),
                re.compile(r'\b[A-Z]{2}[0-9]{7}\b'),
            ],

            PIIType.DRIVER_LICENSE: [
                re.compile(r'\b[A-Z]\d{7}\b'),
                re.compile(r'\b[A-Z]{1,2}\d{6,8}\b')
            ]
        }

        # Contextual keywords that increase PII confidence
        self.context_keywords = {
            PIIType.EMAIL: ['email', 'e-mail', 'mail', 'contact'],
            PIIType.PHONE: ['phone', 'mobile', 'tel', 'call', 'number'],
            PIIType.NAME: ['name', 'full name', 'first name', 'last name'],
            PIIType.ADDRESS: ['address', 'street', 'city', 'zip', 'postal'],
            PIIType.SSN: ['ssn', 'social security', 'social'],
            PIIType.DATE_OF_BIRTH: ['birth', 'dob', 'birthday', 'born']
        }

        logger.info(
            "PII Detector initialized with %d pattern types",
            len(self.patterns)
        )

    def detect_pii_in_text(
        self,
        text: str,
        context: Optional[str] = None
    ) -> List[PIIDetection]:
        """Detect PII in text content with confidence scoring"""
        if not text or not isinstance(text, str):
            return []

        detections = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)

                for match in matches:
                    matched_value = match.group()

                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        pii_type, matched_value, text
                    )

                    # Create redacted value
                    redacted_value = self._create_redacted_value(
                        pii_type, matched_value
                    )

                    # Generate secure hash for tracking
                    value_hash = hashlib.sha256(
                        matched_value.encode()
                    ).hexdigest()[:16]

                    detection = PIIDetection(
                        pii_type=pii_type,
                        confidence=confidence,
                        location=f"position_{match.start()}_{match.end()}",
                        value_hash=value_hash,
                        redacted_value=redacted_value,
                        original_value=matched_value,
                        context=context
                    )

                    detections.append(detection)

        return detections

    def detect_pii_in_dict(
        self,
        data: Dict[str, Any],
        parent_key: str = ""
    ) -> List[PIIDetection]:
        """Recursively detect PII in dictionary structures"""
        detections = []

        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            if isinstance(value, str):
                # Check if field name suggests PII
                context = key if any(
                    keyword in key.lower()
                    for keywords in self.context_keywords.values()
                    for keyword in keywords
                ) else None

                text_detections = self.detect_pii_in_text(value, context)
                for detection in text_detections:
                    detection.location = f"field_{full_key}"
                detections.extend(text_detections)

            elif isinstance(value, dict):
                nested_detections = self.detect_pii_in_dict(value, full_key)
                detections.extend(nested_detections)

            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        item_detections = self.detect_pii_in_text(item)
                        for detection in item_detections:
                            detection.location = f"field_{full_key}[{i}]"
                        detections.extend(item_detections)
                    elif isinstance(item, dict):
                        item_detections = self.detect_pii_in_dict(
                            item, f"{full_key}[{i}]"
                        )
                        detections.extend(item_detections)

        return detections

    def _calculate_confidence(
        self,
        pii_type: PIIType,
        matched_value: str,
        full_text: str
    ) -> float:
        """Calculate confidence score for PII detection"""
        base_confidence = 0.7  # Base confidence for pattern match

        # Boost confidence based on context keywords
        if pii_type in self.context_keywords:
            context_lower = full_text.lower()
            if any(
                keyword in context_lower
                for keyword in self.context_keywords[pii_type]
            ):
                base_confidence = min(0.95, base_confidence + 0.2)

        # Boost confidence for strong patterns
        if (
            pii_type == PIIType.EMAIL
            and '@' in matched_value
            and '.' in matched_value
        ):
            base_confidence = min(0.95, base_confidence + 0.15)
        elif pii_type == PIIType.SSN and '-' in matched_value:
            base_confidence = min(0.95, base_confidence + 0.2)
        elif pii_type == PIIType.CREDIT_CARD and len(matched_value) >= 15:
            base_confidence = min(0.95, base_confidence + 0.2)

        # Reduce confidence for potential false positives
        if pii_type == PIIType.IP_ADDRESS:
            # Check if it's a common internal IP
            if matched_value.startswith(('192.168.', '10.', '172.')):
                base_confidence = max(0.3, base_confidence - 0.3)

        return round(base_confidence, 2)

    def _create_redacted_value(
        self,
        pii_type: PIIType,
        original_value: str
    ) -> str:
        """Create appropriate redacted representation"""
        if pii_type == PIIType.EMAIL:
            parts = original_value.split('@')
            if len(parts) == 2:
                return f"***@{parts[1]}"
        elif pii_type == PIIType.PHONE:
            if len(original_value) >= 10:
                return f"***-***-{original_value[-4:]}"
        elif pii_type == PIIType.SSN:
            return "***-**-****"
        elif pii_type == PIIType.CREDIT_CARD:
            if len(original_value) >= 12:
                return f"****-****-****-{original_value[-4:]}"

        # Default redaction
        return f"[{pii_type.value.upper()}_REDACTED]"


class DataClassifier:
    """Intelligent data classifier with compliance mapping"""

    # Input size limits to prevent DoS attacks
    MAX_INPUT_LENGTH = 1_000_000  # 1MB limit
    MAX_DICT_DEPTH = 100  # Maximum nesting depth for dictionaries

    def __init__(self):
        self.pii_detector = PIIDetector()

        # Classification rules based on content analysis
        self.classification_rules = {
            # High-sensitivity indicators
            DataClassification.TOP_SECRET: [
                'top secret', 'classified', 'confidential business',
                'trade secret', 'proprietary algorithm', 'security key',
                'master password'
            ],

            DataClassification.RESTRICTED: [
                'restricted', 'internal only', 'employee only',
                'not for distribution', 'customer data',
                'personal information', 'financial data',
                'medical record', 'health information', 'payment info'
            ],

            DataClassification.CONFIDENTIAL: [
                'confidential', 'sensitive', 'private', 'internal use',
                'business sensitive', 'competitive', 'strategic'
            ],

            DataClassification.INTERNAL: [
                'internal', 'company', 'organization', 'team only',
                'draft', 'preliminary', 'planning'
            ]
        }

        # Compliance framework mappings
        self.compliance_frameworks = {
            'gdpr': {
                'triggers': [
                    PIIType.EMAIL, PIIType.NAME,
                    PIIType.ADDRESS, PIIType.PHONE
                ],
                'min_classification': DataClassification.CONFIDENTIAL
            },
            'hipaa': {
                'triggers': [PIIType.SSN, PIIType.DATE_OF_BIRTH],
                'keywords': [
                    'medical', 'health', 'patient', 'diagnosis', 'treatment'
                ],
                'min_classification': DataClassification.RESTRICTED
            },
            'pci': {
                'triggers': [PIIType.CREDIT_CARD],
                'keywords': ['payment', 'card', 'transaction', 'billing'],
                'min_classification': DataClassification.RESTRICTED
            }
        }

    def classify_data(
        self,
        data: Any,
        data_id: Optional[str] = None
    ) -> ClassificationResult:
        """Classify data and detect compliance requirements

        Args:
            data: Input data to classify (str, dict, or other)
            data_id: Optional identifier for the data

        Returns:
            ClassificationResult with classification and compliance flags

        Raises:
            ValueError: If input exceeds size limits or is invalid
            TypeError: If input type is not supported
        """
        start_time = time.time()
        data_id = data_id or str(uuid.uuid4())

        # Input sanitization and validation
        if isinstance(data, str):
            # Validate string input
            if len(data) > self.MAX_INPUT_LENGTH:
                raise ValueError(
                    f"Input string exceeds maximum length of "
                    f"{self.MAX_INPUT_LENGTH} characters. "
                    f"Received {len(data)} characters."
                )
            # Check for null bytes
            if '\x00' in data:
                raise ValueError(
                    "Input contains null bytes which are not allowed"
                )
            text_content = data
            pii_detections = self.pii_detector.detect_pii_in_text(data)
        elif isinstance(data, dict):
            # Validate dictionary input
            text_content = json.dumps(data, default=str)
            if len(text_content) > self.MAX_INPUT_LENGTH:
                raise ValueError(
                    f"Input dictionary serialized size exceeds maximum "
                    f"length of {self.MAX_INPUT_LENGTH} characters. "
                    f"Serialized size: {len(text_content)} characters."
                )
            # Check nesting depth to prevent stack overflow
            if self._get_dict_depth(data) > self.MAX_DICT_DEPTH:
                raise ValueError(
                    f"Input dictionary exceeds maximum nesting depth of "
                    f"{self.MAX_DICT_DEPTH}. "
                    f"Found depth: {self._get_dict_depth(data)}"
                )
            pii_detections = self.pii_detector.detect_pii_in_dict(data)
        elif data is None:
            raise TypeError("Input data cannot be None")
        else:
            # Convert other types to string with validation
            text_content = str(data)
            if len(text_content) > self.MAX_INPUT_LENGTH:
                raise ValueError(
                    f"Input serialized size exceeds maximum length of "
                    f"{self.MAX_INPUT_LENGTH} characters. "
                    f"Serialized size: {len(text_content)} characters."
                )
            pii_detections = self.pii_detector.detect_pii_in_text(
                text_content
            )

        # Determine base classification
        base_classification = self._classify_by_content(
            text_content.lower()
        )

        # Adjust classification based on PII content
        pii_classification = self._classify_by_pii(pii_detections)

        # Take the more restrictive classification
        final_classification = self._max_classification(
            base_classification, pii_classification
        )

        # Calculate overall confidence
        content_confidence = self._calculate_content_confidence(
            text_content, final_classification
        )
        pii_confidence = max(
            (d.confidence for d in pii_detections), default=0.0
        )
        overall_confidence = max(content_confidence, pii_confidence)

        # Determine compliance requirements
        compliance_flags = self._determine_compliance_requirements(
            pii_detections, text_content
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        result = ClassificationResult(
            data_id=data_id,
            classification=final_classification,
            confidence=overall_confidence,
            pii_detected=pii_detections,
            pii_count=len(pii_detections),
            highest_pii_confidence=pii_confidence,
            processing_time_ms=processing_time_ms,
            **compliance_flags
        )

        # Post-classification validation
        self._validate_compliance_flags(result, pii_detections)

        # Safe logging - never log raw PII
        logger.debug(
            "Data classified as %s (confidence: %.2f, PII items: %d)",
            final_classification.value,
            overall_confidence,
            len(pii_detections)
        )

        return result

    def _get_dict_depth(
        self,
        data: Dict[str, Any],
        current_depth: int = 0
    ) -> int:
        """Calculate the maximum nesting depth of a dictionary"""
        if not isinstance(data, dict) or current_depth >= self.MAX_DICT_DEPTH:
            return current_depth

        max_depth = current_depth
        for value in data.values():
            if isinstance(value, dict):
                depth = self._get_dict_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        depth = self._get_dict_depth(
                            item, current_depth + 1
                        )
                        max_depth = max(max_depth, depth)

        return max_depth

    def _validate_compliance_flags(
        self,
        result: ClassificationResult,
        pii_detections: List[PIIDetection]
    ):
        """Validate that compliance flags are correctly set"""
        # Check for credit card detection - must have PCI flag
        credit_card_detections = [
            d for d in pii_detections
            if d.pii_type == PIIType.CREDIT_CARD and d.confidence >= 0.7
        ]
        if credit_card_detections and not result.requires_pci_protection:
            logger.warning(
                "Credit card detected but PCI flag not set. "
                "Detections: %d. Auto-correcting compliance flag.",
                len(credit_card_detections)
            )
            result.requires_pci_protection = True

        # Check for GDPR-triggering PII
        gdpr_types = {
            PIIType.EMAIL, PIIType.NAME, PIIType.ADDRESS, PIIType.PHONE
        }
        gdpr_detections = [
            d for d in pii_detections
            if d.pii_type in gdpr_types and d.confidence >= 0.7
        ]
        if gdpr_detections and not result.requires_gdpr_protection:
            logger.warning(
                "GDPR-triggering PII detected but GDPR flag not set. "
                "Detections: %d. Auto-correcting compliance flag.",
                len(gdpr_detections)
            )
            result.requires_gdpr_protection = True

        # Check for HIPAA-triggering PII
        hipaa_types = {PIIType.SSN, PIIType.DATE_OF_BIRTH}
        hipaa_detections = [
            d for d in pii_detections
            if d.pii_type in hipaa_types and d.confidence >= 0.7
        ]
        if hipaa_detections and not result.requires_hipaa_protection:
            logger.warning(
                "HIPAA-triggering PII detected but HIPAA flag not set. "
                "Detections: %d. Auto-correcting compliance flag.",
                len(hipaa_detections)
            )
            result.requires_hipaa_protection = True

    def _classify_by_content(
        self,
        text_lower: str
    ) -> DataClassification:
        """Classify data based on content keywords"""
        for classification, keywords in self.classification_rules.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return classification

        # Default to internal if no specific classification found
        return DataClassification.INTERNAL

    def _classify_by_pii(
        self,
        pii_detections: List[PIIDetection]
    ) -> DataClassification:
        """Classify data based on PII content"""
        if not pii_detections:
            return DataClassification.PUBLIC

        # High-confidence PII requires restricted classification
        high_confidence_pii = [
            d for d in pii_detections if d.confidence >= 0.8
        ]
        if high_confidence_pii:
            sensitive_types = {
                PIIType.SSN, PIIType.CREDIT_CARD,
                PIIType.PASSPORT, PIIType.BIOMETRIC
            }
            if any(
                d.pii_type in sensitive_types for d in high_confidence_pii
            ):
                return DataClassification.RESTRICTED
            return DataClassification.CONFIDENTIAL

        # Medium-confidence PII requires confidential classification
        medium_confidence_pii = [
            d for d in pii_detections if d.confidence >= 0.6
        ]
        if medium_confidence_pii:
            return DataClassification.CONFIDENTIAL

        # Any PII requires at least internal classification
        return DataClassification.INTERNAL

    def _max_classification(
        self,
        class1: DataClassification,
        class2: DataClassification
    ) -> DataClassification:
        """Return the more restrictive classification"""
        order = [
            DataClassification.PUBLIC,
            DataClassification.INTERNAL,
            DataClassification.CONFIDENTIAL,
            DataClassification.RESTRICTED,
            DataClassification.TOP_SECRET
        ]

        index1 = order.index(class1)
        index2 = order.index(class2)

        return order[max(index1, index2)]

    def _calculate_content_confidence(
        self,
        text: str,
        classification: DataClassification
    ) -> float:
        """Calculate confidence in content-based classification"""
        text_lower = text.lower()
        matching_keywords = []

        if classification in self.classification_rules:
            for keyword in self.classification_rules[classification]:
                if keyword in text_lower:
                    matching_keywords.append(keyword)

        # Base confidence increases with number of matching keywords
        keyword_confidence = min(0.9, 0.4 + (len(matching_keywords) * 0.1))

        # Adjust based on text length
        length_bonus = min(0.1, len(text) / 10000)

        return keyword_confidence + length_bonus

    def _determine_compliance_requirements(
        self,
        pii_detections: List[PIIDetection],
        text: str
    ) -> Dict[str, bool]:
        """Determine which compliance frameworks apply"""
        text_lower = text.lower()

        compliance_flags = {
            'requires_gdpr_protection': False,
            'requires_hipaa_protection': False,
            'requires_pci_protection': False
        }

        # Check each compliance framework
        for framework, rules in self.compliance_frameworks.items():
            framework_triggered = False

            # Check PII triggers
            if 'triggers' in rules:
                detected_types = {
                    d.pii_type for d in pii_detections
                    if d.confidence >= 0.7
                }
                if any(
                    trigger_type in detected_types
                    for trigger_type in rules['triggers']
                ):
                    framework_triggered = True

            # Check keyword triggers
            if 'keywords' in rules and not framework_triggered:
                if any(
                    keyword in text_lower for keyword in rules['keywords']
                ):
                    framework_triggered = True

            if framework_triggered:
                compliance_flags[f'requires_{framework}_protection'] = True

        return compliance_flags

    def redact_data(
        self,
        data: Any,
        classification_result: ClassificationResult
    ) -> Any:
        """Redact PII from data based on classification result"""
        if not classification_result.pii_detected:
            return data

        if isinstance(data, str):
            return self._redact_string(data, classification_result)
        if isinstance(data, dict):
            return self._redact_dict(
                data, classification_result.pii_detected
            )
        return data

    def _redact_string(
        self,
        data: str,
        classification_result: ClassificationResult
    ) -> str:
        """Redact PII from string data"""
        redacted_text = data
        position_detections = []

        for detection in classification_result.pii_detected:
            if (
                detection.location.startswith("position_")
                and detection.confidence >= 0.7
            ):
                try:
                    parts = detection.location.split('_')
                    start_pos = int(parts[1])
                    end_pos = int(parts[2])
                    position_detections.append(
                        (start_pos, end_pos, detection)
                    )
                except (IndexError, ValueError):
                    # Fallback: use string replacement
                    if detection.original_value in redacted_text:
                        redacted_text = redacted_text.replace(
                            detection.original_value,
                            detection.redacted_value,
                            1
                        )

        # Apply redactions in reverse order
        for start_pos, end_pos, detection in sorted(
            position_detections, reverse=True
        ):
            if start_pos < len(redacted_text) and end_pos <= len(
                redacted_text
            ):
                redacted_text = (
                    redacted_text[:start_pos] +
                    detection.redacted_value +
                    redacted_text[end_pos:]
                )

        return redacted_text

    def _redact_dict(
        self,
        data: Dict[str, Any],
        pii_detections: List[PIIDetection]
    ) -> Dict[str, Any]:
        """Redact PII from dictionary based on field locations"""
        redacted_data = copy.deepcopy(data)

        for detection in pii_detections:
            if detection.confidence < 0.7:
                continue
            if not detection.location.startswith("field_"):
                continue

            field_path = detection.location[6:]

            # Navigate to the field and redact
            try:
                # Handle simple field paths
                if '.' not in field_path and '[' not in field_path:
                    if field_path in redacted_data:
                        if isinstance(redacted_data[field_path], str):
                            redacted_data[field_path] = (
                                redacted_data[field_path].replace(
                                    detection.original_value,
                                    detection.redacted_value
                                )
                            )
                        else:
                            redacted_data[field_path] = (
                                detection.redacted_value
                            )
                else:
                    # Handle nested paths
                    self._redact_nested_field(
                        redacted_data, field_path, detection
                    )
            except (KeyError, TypeError, IndexError):
                # Field path doesn't exist or is invalid, skip
                logger.debug(
                    "Could not redact field %s: field not found",
                    field_path
                )

        return redacted_data

    def _redact_nested_field(
        self,
        data: Dict[str, Any],
        field_path: str,
        detection: PIIDetection
    ):
        """Redact PII in nested dictionary structures"""
        parts = field_path.replace('[', '.').replace(']', '').split('.')
        current = data

        # Navigate to the parent of the target field
        for part in parts[:-1]:
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]

        # Redact the final field
        final_key = parts[-1]
        if final_key.isdigit():
            idx = int(final_key)
            if isinstance(current[idx], str):
                current[idx] = current[idx].replace(
                    detection.original_value,
                    detection.redacted_value
                )
            else:
                current[idx] = detection.redacted_value
        else:
            if isinstance(current.get(final_key), str):
                current[final_key] = current[final_key].replace(
                    detection.original_value,
                    detection.redacted_value
                )
            else:
                current[final_key] = detection.redacted_value


class ComplianceReporter:
    """Generate compliance reports and data governance summaries"""

    def __init__(self):
        self.classification_history: List[ClassificationResult] = []

    def add_classification_result(self, result: ClassificationResult):
        """Add classification result to history"""
        self.classification_history.append(result)

        # Keep only recent results (last 10000)
        if len(self.classification_history) > 10000:
            self.classification_history = self.classification_history[-10000:]

    def generate_compliance_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)

        recent_results = [
            result for result in self.classification_history
            if result.classified_at >= cutoff_time
        ]

        if not recent_results:
            return {
                "error": "No classification data available for report period"
            }

        # Overall statistics
        total_classified = len(recent_results)
        pii_containing_items = len(
            [r for r in recent_results if r.pii_count > 0]
        )

        # Classification distribution
        classification_counts = {}
        for result in recent_results:
            classification = result.classification.value
            classification_counts[classification] = (
                classification_counts.get(classification, 0) + 1
            )

        # PII type distribution
        pii_type_counts = {}
        for result in recent_results:
            for detection in result.pii_detected:
                pii_type = detection.pii_type.value
                pii_type_counts[pii_type] = (
                    pii_type_counts.get(pii_type, 0) + 1
                )

        # Compliance framework requirements
        gdpr_items = len(
            [r for r in recent_results if r.requires_gdpr_protection]
        )
        hipaa_items = len(
            [r for r in recent_results if r.requires_hipaa_protection]
        )
        pci_items = len(
            [r for r in recent_results if r.requires_pci_protection]
        )

        return {
            "report_period_days": days,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_data_items_classified": total_classified,
                "items_containing_pii": pii_containing_items,
                "pii_detection_rate_percent": (
                    (pii_containing_items / total_classified) * 100
                ),
            },
            "classification_distribution": classification_counts,
            "pii_type_distribution": pii_type_counts,
            "compliance_requirements": {
                "gdpr_protected_items": gdpr_items,
                "hipaa_protected_items": hipaa_items,
                "pci_protected_items": pci_items
            },
            "risk_assessment": {
                "high_risk_items": len([
                    r for r in recent_results
                    if r.classification in [
                        DataClassification.RESTRICTED,
                        DataClassification.TOP_SECRET
                    ]
                ]),
                "avg_pii_confidence": statistics.mean([
                    r.highest_pii_confidence for r in recent_results
                    if r.highest_pii_confidence > 0
                ]) if any(
                    r.highest_pii_confidence > 0 for r in recent_results
                ) else 0.0,
                "data_governance_score": self._calculate_governance_score(
                    recent_results
                )
            }
        }

    def _calculate_governance_score(
        self,
        results: List[ClassificationResult]
    ) -> float:
        """Calculate data governance maturity score (0-100)"""
        if not results:
            return 0.0

        # Factors for governance score
        classification_coverage = 100.0  # All data is classified

        pii_detection_accuracy = statistics.mean([
            r.highest_pii_confidence for r in results if r.pii_count > 0
        ]) * 100 if any(r.pii_count > 0 for r in results) else 100.0

        compliance_coverage = len([
            r for r in results
            if (
                r.requires_gdpr_protection
                or r.requires_hipaa_protection
                or r.requires_pci_protection
            )
        ]) / len(results) * 100

        processing_efficiency = 100 - min(
            50, statistics.mean([
                r.processing_time_ms for r in results
            ]) / 10
        )

        # Weighted score
        score = (
            classification_coverage * 0.3 +
            pii_detection_accuracy * 0.3 +
            compliance_coverage * 0.2 +
            processing_efficiency * 0.2
        )

        return round(score, 1)


# Global singleton instances
_classifier_instance: DataClassifier | None = None
_reporter_instance: ComplianceReporter | None = None


def get_data_classifier() -> DataClassifier:
    """Get global data classifier instance (singleton)"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DataClassifier()
    return _classifier_instance


def get_compliance_reporter() -> ComplianceReporter:
    """Get global compliance reporter instance (singleton)"""
    global _reporter_instance
    if _reporter_instance is None:
        _reporter_instance = ComplianceReporter()
    return _reporter_instance


# Decorators for automatic classification
def classify_input_data(data_param: str = "data"):
    """Decorator to automatically classify input data"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                classifier = get_data_classifier()
                reporter = get_compliance_reporter()

                # Extract data parameter
                data = kwargs.get(data_param) or (
                    args[0] if args else None
                )
                if data is not None:
                    # Classify the data
                    result = classifier.classify_data(data)

                    # Add to compliance reporting
                    reporter.add_classification_result(result)

                    # Add classification context to kwargs
                    kwargs['_data_classification'] = result

                    # Log if sensitive data detected
                    if result.pii_count > 0:
                        logger.info(
                            "Processing %s data with %d PII items",
                            result.classification.value,
                            result.pii_count
                        )

                return await func(*args, **kwargs)
            return async_wrapper

        def sync_wrapper(*args, **kwargs):
            classifier = get_data_classifier()
            reporter = get_compliance_reporter()

            # Extract data parameter
            data = kwargs.get(data_param) or (
                args[0] if args else None
            )
            if data is not None:
                # Classify the data
                result = classifier.classify_data(data)

                # Add to compliance reporting
                reporter.add_classification_result(result)

                # Add classification context to kwargs
                kwargs['_data_classification'] = result

                # Log if sensitive data detected
                if result.pii_count > 0:
                    logger.info(
                        "Processing %s data with %d PII items",
                        result.classification.value,
                        result.pii_count
                    )

            return func(*args, **kwargs)
        return sync_wrapper
    return decorator
