"""
Performance tests for Data Classifier

Tests performance characteristics including:
- Large payload handling
- Regex pattern efficiency
- Classification speed
- Memory usage
"""

import pytest
import time
import sys
sys.path.insert(0, 'src')

from amas.governance.data_classifier import DataClassifier, PIIType


class TestPerformance:
    """Performance tests for data classification"""
    
    def test_large_payload_classification(self):
        """Test classification performance on large payloads"""
        classifier = DataClassifier()
        
        # Create large payload with PII at the end
        large_data = "x" * 1_000_000 + " Contact: user@example.com"
        
        start_time = time.time()
        result = classifier.classify_data(large_data)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 1 second for 1MB)
        assert elapsed < 1.0, f"Classification took {elapsed:.2f}s, expected < 1.0s"
        assert result.pii_count > 0
        assert result.requires_gdpr_protection is True
    
    def test_credit_card_detection_performance(self):
        """Test credit card detection performance"""
        classifier = DataClassifier()
        
        # Test with credit card number
        test_data = "Payment card: 4532-1234-5678-9010"
        
        start_time = time.time()
        result = classifier.classify_data(test_data)
        elapsed = time.time() - start_time
        
        # Should be very fast (< 100ms)
        assert elapsed < 0.1, f"Credit card detection took {elapsed:.3f}s, expected < 0.1s"
        assert result.requires_pci_protection is True
    
    def test_multiple_pii_types_performance(self):
        """Test performance with multiple PII types"""
        classifier = DataClassifier()
        
        test_data = """
        User Information:
        Email: john.doe@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        Credit Card: 4532-1234-5678-9010
        """
        
        start_time = time.time()
        result = classifier.classify_data(test_data)
        elapsed = time.time() - start_time
        
        # Should handle multiple PII types efficiently
        assert elapsed < 0.2, f"Multiple PII detection took {elapsed:.3f}s, expected < 0.2s"
        assert result.pii_count >= 4
        assert result.requires_gdpr_protection is True
        assert result.requires_pci_protection is True
        assert result.requires_hipaa_protection is True
    
    def test_regex_no_redos(self):
        """Test that regex patterns don't cause ReDoS"""
        classifier = DataClassifier()
        
        # Malicious input that could cause ReDoS with bad patterns
        malicious_input = "a" * 10000 + "4111-1111-1111-1111"
        
        start_time = time.time()
        result = classifier.classify_data(malicious_input)
        elapsed = time.time() - start_time
        
        # Should complete quickly even with malicious input
        assert elapsed < 0.5, f"ReDoS test took {elapsed:.3f}s, expected < 0.5s"
    
    def test_dict_depth_limits(self):
        """Test that dictionary depth limits prevent stack overflow"""
        classifier = DataClassifier()
        
        # Create deeply nested dictionary
        deep_dict = {}
        current = deep_dict
        for i in range(150):  # Exceeds MAX_DICT_DEPTH
            current['level'] = i
            current['next'] = {}
            current = current['next']
        
        # Should raise ValueError, not crash
        with pytest.raises(ValueError, match="exceeds maximum nesting depth"):
            classifier.classify_data(deep_dict)
    
    def test_input_size_limits(self):
        """Test that input size limits prevent DoS"""
        classifier = DataClassifier()
        
        # Create input exceeding MAX_INPUT_LENGTH
        large_input = "x" * (DataClassifier.MAX_INPUT_LENGTH + 1)
        
        # Should raise ValueError, not crash
        with pytest.raises(ValueError, match="exceeds maximum length"):
            classifier.classify_data(large_input)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
