#!/usr/bin/env python3
"""
Data Governance & Compliance Usage Examples

This file demonstrates how to use the Data Governance & Compliance module
for PII detection, data classification, and compliance reporting.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from amas.governance import (
    DataClassifier,
    ComplianceReporter,
    DataClassification,
    PIIType,
    get_data_classifier,
    get_compliance_reporter,
    safe_log_pii,
    classify_input_data,
)


def example_basic_classification():
    """Example: Basic data classification"""
    print("=" * 60)
    print("Example 1: Basic Data Classification")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    # Classify text with email
    text = "Please contact support@example.com for assistance"
    result = classifier.classify_data(text)
    
    print(f"Text: {text}")
    print(f"Classification: {result.classification.value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"PII Count: {result.pii_count}")
    print(f"GDPR Protection: {result.requires_gdpr_protection}")
    print(f"PCI Protection: {result.requires_pci_protection}")
    print(f"HIPAA Protection: {result.requires_hipaa_protection}")
    print()


def example_credit_card_detection():
    """Example: Credit card detection and PCI compliance"""
    print("=" * 60)
    print("Example 2: Credit Card Detection (PCI Compliance)")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    # Classify text with credit card
    text = "Payment card: 4532-1234-5678-9010"
    result = classifier.classify_data(text)
    
    print(f"Text: {text}")
    print(f"Classification: {result.classification.value}")
    print(f"PCI Protection Required: {result.requires_pci_protection}")
    print(f"PII Detected: {len(result.pii_detected)} items")
    
    for detection in result.pii_detected:
        print(f"  - {detection.pii_type.value}: {detection.redacted_value} (confidence: {detection.confidence:.2f})")
    print()


def example_redaction():
    """Example: PII redaction for safe logging"""
    print("=" * 60)
    print("Example 3: PII Redaction")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    # Original data with PII
    original = "User: john.doe@example.com, Phone: 555-123-4567"
    result = classifier.classify_data(original)
    
    # Redact PII
    redacted = classifier.redact_data(original, result)
    
    print(f"Original: {original}")
    print(f"Redacted: {redacted}")
    print(f"Safe for logging: {original != redacted}")
    print()


def example_compliance_reporting():
    """Example: Compliance reporting"""
    print("=" * 60)
    print("Example 4: Compliance Reporting")
    print("=" * 60)
    
    classifier = DataClassifier()
    reporter = ComplianceReporter()
    
    # Classify multiple data items
    test_cases = [
        "Contact: user@example.com",
        "Card: 4532-1234-5678-9010",
        "SSN: 123-45-6789",
        "Public announcement"
    ]
    
    for text in test_cases:
        result = classifier.classify_data(text)
        reporter.add_classification_result(result)
        print(f"Classified: {text[:30]}... → {result.classification.value}")
    
    # Generate report
    report = reporter.generate_compliance_report(days=1)
    
    print("\nCompliance Report:")
    print(f"  Total items: {report['summary']['total_data_items_classified']}")
    print(f"  Items with PII: {report['summary']['items_containing_pii']}")
    print(f"  GDPR protected: {report['compliance_requirements']['gdpr_protected_items']}")
    print(f"  PCI protected: {report['compliance_requirements']['pci_protected_items']}")
    print(f"  HIPAA protected: {report['compliance_requirements']['hipaa_protected_items']}")
    print(f"  Governance score: {report['risk_assessment']['data_governance_score']}")
    print()


def example_safe_logging():
    """Example: Safe logging with PII"""
    print("=" * 60)
    print("Example 5: Safe Logging")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    text = "User email: admin@company.com"
    result = classifier.classify_data(text)
    
    # Safe logging
    for detection in result.pii_detected:
        safe_msg = safe_log_pii(detection, "PII detected in user data")
        print(f"Safe log message: {safe_msg}")
        # This is safe to log - no raw PII
    print()


def example_decorator_usage():
    """Example: Using the classify_input_data decorator"""
    print("=" * 60)
    print("Example 6: Automatic Classification Decorator")
    print("=" * 60)
    
    @classify_input_data(data_param="data")
    def process_user_data(data: str, _data_classification=None):
        """Process user data with automatic classification"""
        if _data_classification:
            print(f"Data automatically classified as: {_data_classification.classification.value}")
            if _data_classification.requires_gdpr_protection:
                print("  → Applying GDPR protections")
            if _data_classification.requires_pci_protection:
                print("  → Applying PCI protections")
        return f"Processed: {data[:20]}..."
    
    # Function automatically classifies input
    result = process_user_data("Contact: user@example.com")
    print(f"Result: {result}")
    print()


def example_dict_classification():
    """Example: Classifying dictionary data"""
    print("=" * 60)
    print("Example 7: Dictionary Data Classification")
    print("=" * 60)
    
    classifier = DataClassifier()
    
    # Classify dictionary
    user_data = {
        "email": "user@example.com",
        "phone": "555-123-4567",
        "name": "John Doe"
    }
    
    result = classifier.classify_data(user_data)
    
    print(f"User data classified as: {result.classification.value}")
    print(f"PII items detected: {result.pii_count}")
    print(f"GDPR protection: {result.requires_gdpr_protection}")
    
    # Redact dictionary
    redacted = classifier.redact_data(user_data, result)
    print(f"\nRedacted data: {redacted}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Data Governance & Compliance - Usage Examples")
    print("=" * 60 + "\n")
    
    try:
        example_basic_classification()
        example_credit_card_detection()
        example_redaction()
        example_compliance_reporting()
        example_safe_logging()
        example_decorator_usage()
        example_dict_classification()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
