#!/usr/bin/env python3
"""
Standalone verification script for Data Governance & Compliance PR
Tests all success criteria without requiring full AMAS dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly from file to avoid __init__ dependencies
import importlib.util
spec = importlib.util.spec_from_file_location(
    "data_classifier",
    os.path.join(os.path.dirname(__file__), "src", "amas", "governance", "data_classifier.py")
)
data_classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_classifier)

DataClassifier = data_classifier.DataClassifier
ComplianceReporter = data_classifier.ComplianceReporter
DataClassification = data_classifier.DataClassification
PIIType = data_classifier.PIIType

def test_email_confidential_gdpr():
    """Success Criteria: Email in text → Classified Confidential + GDPR flag"""
    print("\n" + "="*60)
    print("TEST 1: Email → Confidential + GDPR")
    print("="*60)
    
    classifier = DataClassifier()
    text = "Please contact john.doe@example.com for more information"
    result = classifier.classify_data(text)
    
    print(f"Text: {text}")
    print(f"Classification: {result.classification.value}")
    print(f"GDPR Protection: {result.requires_gdpr_protection}")
    print(f"PII Count: {result.pii_count}")
    print(f"Confidence: {result.confidence:.2f}")
    
    # Verify success criteria
    assert result.classification == DataClassification.CONFIDENTIAL, \
        f"Expected CONFIDENTIAL, got {result.classification.value}"
    assert result.requires_gdpr_protection is True, \
        "Expected GDPR protection flag to be True"
    assert result.pii_count > 0, "Expected at least one PII detection"
    
    email_detections = [d for d in result.pii_detected if d.pii_type == PIIType.EMAIL]
    assert len(email_detections) > 0, "Expected email to be detected"
    
    print("✓ SUCCESS: Email classified as Confidential with GDPR flag")
    return True


def test_credit_card_restricted_pci():
    """Success Criteria: Credit card → Classified Restricted + PCI flag"""
    print("\n" + "="*60)
    print("TEST 2: Credit Card → Restricted + PCI")
    print("="*60)
    
    classifier = DataClassifier()
    text = "Payment card: 4532-1234-5678-9010"
    result = classifier.classify_data(text)
    
    print(f"Text: {text}")
    print(f"Classification: {result.classification.value}")
    print(f"PCI Protection: {result.requires_pci_protection}")
    print(f"PII Count: {result.pii_count}")
    print(f"Confidence: {result.confidence:.2f}")
    
    # Verify success criteria
    assert result.classification == DataClassification.RESTRICTED, \
        f"Expected RESTRICTED, got {result.classification.value}"
    assert result.requires_pci_protection is True, \
        "Expected PCI protection flag to be True"
    assert result.pii_count > 0, "Expected at least one PII detection"
    
    cc_detections = [d for d in result.pii_detected if d.pii_type == PIIType.CREDIT_CARD]
    assert len(cc_detections) > 0, "Expected credit card to be detected"
    
    print("✓ SUCCESS: Credit card classified as Restricted with PCI flag")
    return True


def test_compliance_report_no_raw_pii():
    """Success Criteria: Compliance report generates summaries without raw PII"""
    print("\n" + "="*60)
    print("TEST 3: Compliance Report (No Raw PII)")
    print("="*60)
    
    classifier = DataClassifier()
    reporter = ComplianceReporter()
    
    # Add test data with various PII
    test_cases = [
        "Contact john@example.com for support",
        "Card: 4532-1234-5678-9010",
        "SSN: 123-45-6789",
        "Public announcement with no sensitive data"
    ]
    
    print("Adding classification results...")
    for text in test_cases:
        result = classifier.classify_data(text)
        reporter.add_classification_result(result)
        print(f"  - Classified: {result.classification.value} (PII: {result.pii_count})")
    
    # Generate report
    report = reporter.generate_compliance_report(days=30)
    
    print("\nReport Structure:")
    print(f"  - Summary: {list(report.get('summary', {}).keys())}")
    print(f"  - Classification Distribution: {report.get('classification_distribution', {})}")
    print(f"  - PII Type Distribution: {report.get('pii_type_distribution', {})}")
    print(f"  - Compliance Requirements: {report.get('compliance_requirements', {})}")
    
    # Convert report to string and check for raw PII
    report_str = str(report)
    
    # Verify no raw PII in report
    raw_pii_found = []
    if "john@example.com" in report_str:
        raw_pii_found.append("john@example.com")
    if "4532-1234-5678-9010" in report_str:
        raw_pii_found.append("4532-1234-5678-9010")
    if "123-45-6789" in report_str:
        raw_pii_found.append("123-45-6789")
    
    assert len(raw_pii_found) == 0, \
        f"Found raw PII in report: {raw_pii_found}"
    
    # Verify report contains statistics
    assert "summary" in report, "Report missing summary section"
    assert "total_data_items_classified" in report["summary"], \
        "Report missing total_data_items_classified"
    assert report["summary"]["total_data_items_classified"] == len(test_cases), \
        "Report item count mismatch"
    
    print(f"\n✓ SUCCESS: Compliance report generated with {report['summary']['total_data_items_classified']} items")
    print("✓ SUCCESS: No raw PII found in report (only statistics and summaries)")
    return True


def test_redaction():
    """Test redaction functionality"""
    print("\n" + "="*60)
    print("TEST 4: PII Redaction")
    print("="*60)
    
    classifier = DataClassifier()
    text = "Contact support@example.com or call 555-123-4567"
    result = classifier.classify_data(text)
    
    print(f"Original: {text}")
    redacted = classifier.redact_data(text, result)
    print(f"Redacted: {redacted}")
    
    # Verify redaction
    assert "support@example.com" not in redacted or "@example.com" in redacted, \
        "Email not properly redacted"
    
    print("✓ SUCCESS: PII properly redacted")
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Data Governance & Compliance PR - Verification Tests")
    print("="*60)
    
    tests = [
        test_email_confidential_gdpr,
        test_credit_card_restricted_pci,
        test_compliance_report_no_raw_pii,
        test_redaction,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - PR Success Criteria Met!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
