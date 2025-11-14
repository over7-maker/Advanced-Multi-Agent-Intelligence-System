"""
Comprehensive tests for Data Governance & Compliance PR

Tests verify all success criteria:
✅ Email in text → Classified Confidential + GDPR flag
✅ Credit card → Classified Restricted + PCI flag
✅ Compliance report generates summaries without raw PII
"""

import pytest
from src.amas.governance.data_classifier import (
    DataClassifier,
    PIIDetector,
    ComplianceReporter,
    DataClassification,
    PIIType,
    get_data_classifier,
    get_compliance_reporter,
)


class TestPIIDetection:
    """Test PII detection capabilities"""
    
    def test_email_detection(self):
        """Test email detection with confidence scoring"""
        detector = PIIDetector()
        text = "Contact us at support@example.com for assistance"
        detections = detector.detect_pii_in_text(text)
        
        assert len(detections) > 0
        email_detections = [d for d in detections if d.pii_type == PIIType.EMAIL]
        assert len(email_detections) > 0
        assert email_detections[0].confidence > 0.7
        assert "support@example.com" in email_detections[0].original_value
        assert "@example.com" in email_detections[0].redacted_value
    
    def test_credit_card_detection(self):
        """Test credit card detection"""
        detector = PIIDetector()
        text = "Card number: 4532-1234-5678-9010"
        detections = detector.detect_pii_in_text(text)
        
        assert len(detections) > 0
        cc_detections = [d for d in detections if d.pii_type == PIIType.CREDIT_CARD]
        assert len(cc_detections) > 0
        assert cc_detections[0].confidence > 0.7
    
    def test_ssn_detection(self):
        """Test SSN detection"""
        detector = PIIDetector()
        text = "SSN: 123-45-6789"
        detections = detector.detect_pii_in_text(text)
        
        assert len(detections) > 0
        ssn_detections = [d for d in detections if d.pii_type == PIIType.SSN]
        assert len(ssn_detections) > 0
    
    def test_api_key_detection(self):
        """Test API key detection"""
        detector = PIIDetector()
        text = "API key: sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        detections = detector.detect_pii_in_text(text)
        
        assert len(detections) > 0
        api_detections = [d for d in detections if d.pii_type == PIIType.API_KEY]
        assert len(api_detections) > 0
    
    def test_dict_detection(self):
        """Test PII detection in dictionary structures"""
        detector = PIIDetector()
        data = {
            "user": {
                "email": "user@example.com",
                "phone": "555-123-4567"
            }
        }
        detections = detector.detect_pii_in_dict(data)
        
        assert len(detections) >= 2
        email_detections = [d for d in detections if d.pii_type == PIIType.EMAIL]
        phone_detections = [d for d in detections if d.pii_type == PIIType.PHONE]
        assert len(email_detections) > 0
        assert len(phone_detections) > 0


class TestDataClassification:
    """Test data classification capabilities"""
    
    def test_email_classification_confidential_gdpr(self):
        """
        Success Criteria Test: Email in text → Classified Confidential + GDPR flag
        """
        classifier = DataClassifier()
        text = "Please contact john.doe@example.com for more information"
        result = classifier.classify_data(text)
        
        # Verify classification
        assert result.classification == DataClassification.CONFIDENTIAL
        assert result.pii_count > 0
        
        # Verify GDPR flag
        assert result.requires_gdpr_protection is True
        
        # Verify email was detected
        email_detections = [d for d in result.pii_detected if d.pii_type == PIIType.EMAIL]
        assert len(email_detections) > 0
        
        print(f"✓ Email classified as {result.classification.value} with GDPR protection")
    
    def test_credit_card_classification_restricted_pci(self):
        """
        Success Criteria Test: Credit card → Classified Restricted + PCI flag
        """
        classifier = DataClassifier()
        text = "Payment card: 4532-1234-5678-9010"
        result = classifier.classify_data(text)
        
        # Verify classification
        assert result.classification == DataClassification.RESTRICTED
        
        # Verify PCI flag
        assert result.requires_pci_protection is True
        
        # Verify credit card was detected
        cc_detections = [d for d in result.pii_detected if d.pii_type == PIIType.CREDIT_CARD]
        assert len(cc_detections) > 0
        
        print(f"✓ Credit card classified as {result.classification.value} with PCI protection")
    
    def test_ssn_classification_hipaa(self):
        """Test SSN triggers HIPAA protection"""
        classifier = DataClassifier()
        text = "Patient SSN: 123-45-6789"
        result = classifier.classify_data(text)
        
        assert result.requires_hipaa_protection is True
        assert result.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]
    
    def test_multiple_pii_types(self):
        """Test classification with multiple PII types"""
        classifier = DataClassifier()
        text = "User: john@example.com, Phone: 555-123-4567, Card: 4532-1234-5678-9010"
        result = classifier.classify_data(text)
        
        assert result.pii_count >= 3
        assert result.requires_gdpr_protection is True
        assert result.requires_pci_protection is True
        assert result.classification == DataClassification.RESTRICTED
    
    def test_no_pii_public_classification(self):
        """Test that data without PII can be classified as public"""
        classifier = DataClassifier()
        text = "This is a public announcement with no sensitive information"
        result = classifier.classify_data(text)
        
        # Should default to internal or public depending on content
        assert result.pii_count == 0
        assert result.requires_gdpr_protection is False
        assert result.requires_hipaa_protection is False
        assert result.requires_pci_protection is False


class TestRedaction:
    """Test PII redaction capabilities"""
    
    def test_email_redaction(self):
        """Test email redaction in text"""
        classifier = DataClassifier()
        text = "Contact support@example.com for help"
        result = classifier.classify_data(text)
        
        redacted = classifier.redact_data(text, result)
        
        assert "support@example.com" not in redacted
        assert "@example.com" in redacted or "***" in redacted
        assert "for help" in redacted  # Non-PII content preserved
    
    def test_credit_card_redaction(self):
        """Test credit card redaction"""
        classifier = DataClassifier()
        text = "Card: 4532-1234-5678-9010"
        result = classifier.classify_data(text)
        
        redacted = classifier.redact_data(text, result)
        
        assert "4532-1234-5678-9010" not in redacted
        assert "****" in redacted or "REDACTED" in redacted
    
    def test_dict_redaction(self):
        """Test redaction in dictionary structures"""
        classifier = DataClassifier()
        data = {
            "email": "user@example.com",
            "name": "John Doe",
            "phone": "555-123-4567"
        }
        result = classifier.classify_data(data)
        
        redacted = classifier.redact_data(data, result)
        
        assert isinstance(redacted, dict)
        # Email should be redacted
        if "email" in redacted:
            assert "user@example.com" not in str(redacted["email"])


class TestComplianceReporting:
    """Test compliance reporting capabilities"""
    
    def test_compliance_report_no_raw_pii(self):
        """
        Success Criteria Test: Compliance report generates summaries without raw PII
        """
        reporter = ComplianceReporter()
        classifier = DataClassifier()
        
        # Add some classification results
        test_cases = [
            "Contact john@example.com",
            "Card: 4532-1234-5678-9010",
            "SSN: 123-45-6789",
            "Public information only"
        ]
        
        for text in test_cases:
            result = classifier.classify_data(text)
            reporter.add_classification_result(result)
        
        # Generate report
        report = reporter.generate_compliance_report(days=30)
        
        # Verify report structure
        assert "summary" in report
        assert "classification_distribution" in report
        assert "pii_type_distribution" in report
        assert "compliance_requirements" in report
        
        # Verify no raw PII in report (should only have counts and statistics)
        report_str = str(report)
        assert "john@example.com" not in report_str
        assert "4532-1234-5678-9010" not in report_str
        assert "123-45-6789" not in report_str
        
        # Verify statistics are present
        assert report["summary"]["total_data_items_classified"] == len(test_cases)
        assert "gdpr_protected_items" in report["compliance_requirements"]
        assert "pci_protected_items" in report["compliance_requirements"]
        
        print(f"✓ Compliance report generated with {report['summary']['total_data_items_classified']} items, no raw PII")
    
    def test_compliance_report_statistics(self):
        """Test compliance report contains proper statistics"""
        reporter = ComplianceReporter()
        classifier = DataClassifier()
        
        # Add mixed classification results
        results = [
            classifier.classify_data("Email: user@example.com"),
            classifier.classify_data("Card: 4532-1234-5678-9010"),
            classifier.classify_data("Public data"),
        ]
        
        for result in results:
            reporter.add_classification_result(result)
        
        report = reporter.generate_compliance_report(days=30)
        
        assert report["summary"]["items_containing_pii"] >= 2
        assert "pii_detection_rate_percent" in report["summary"]
        assert report["compliance_requirements"]["gdpr_protected_items"] >= 1
        assert report["compliance_requirements"]["pci_protected_items"] >= 1


class TestGlobalInstances:
    """Test global instance access"""
    
    def test_get_data_classifier(self):
        """Test global classifier access"""
        classifier1 = get_data_classifier()
        classifier2 = get_data_classifier()
        
        assert classifier1 is classifier2  # Should be same instance
    
    def test_get_compliance_reporter(self):
        """Test global reporter access"""
        reporter1 = get_compliance_reporter()
        reporter2 = get_compliance_reporter()
        
        assert reporter1 is reporter2  # Should be same instance


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_classification_workflow(self):
        """Test complete classification workflow"""
        classifier = get_data_classifier()
        reporter = get_compliance_reporter()
        
        # Classify data with email
        text = "User email: alice@company.com"
        result = classifier.classify_data(text)
        
        # Verify classification
        assert result.classification == DataClassification.CONFIDENTIAL
        assert result.requires_gdpr_protection is True
        
        # Add to reporter
        reporter.add_classification_result(result)
        
        # Generate report
        report = reporter.generate_compliance_report(days=1)
        
        assert report["summary"]["total_data_items_classified"] >= 1
        assert report["compliance_requirements"]["gdpr_protected_items"] >= 1
        
        # Test redaction
        redacted = classifier.redact_data(text, result)
        assert "alice@company.com" not in redacted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
