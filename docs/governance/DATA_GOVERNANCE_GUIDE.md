# Data Governance & Compliance Guide

## Overview

The Data Governance & Compliance module provides enterprise-grade data governance capabilities with automatic PII detection, data classification, compliance framework mapping, and comprehensive audit trails for GDPR/HIPAA/PCI compliance.

**Status**: ✅ Production Ready (PR #242)

---

## Features

### ✅ Automatic PII Detection with Confidence Scoring

Detects and classifies Personally Identifiable Information (PII) with confidence scoring:

- **Email addresses** - Detected with high confidence
- **Social Security Numbers (SSN)** - Multiple format support
- **Credit card numbers** - Visa, MasterCard, AmEx, Discover
- **API keys and tokens** - OpenAI, Google, AWS, GitHub, Slack
- **Phone numbers** - Multiple formats (US and international)
- **IP addresses** - IPv4 and IPv6
- **Names and addresses** - Context-aware detection
- **Date of birth** - Various formats
- **Passports and driver licenses** - Multiple country formats
- **Biometric data** - Pattern-based detection

**Confidence Scoring**: Each detection includes a confidence score (0.0-1.0) based on:
- Pattern strength
- Contextual keywords
- Format validation

### ✅ 5-Tier Data Classification

Automatic classification of data into security tiers:

1. **Public** - No sensitive data, safe for public disclosure
2. **Internal** - Company-internal information
3. **Confidential** - Contains PII or sensitive business data
4. **Restricted** - High-sensitivity PII (SSN, credit cards, etc.)
5. **Top Secret** - Highest classification level

Classification is determined by:
- Content analysis (keywords, context)
- PII detection results
- Takes the most restrictive classification

### ✅ Compliance Framework Mapping

Automatic compliance requirement detection:

- **GDPR** - Triggered by emails, names, addresses, phone numbers
- **HIPAA** - Triggered by SSN, date of birth, medical keywords
- **PCI** - Triggered by credit card numbers, payment keywords

Each classification result includes compliance flags indicating which frameworks apply.

### ✅ Redaction Helpers

Safe redaction of PII for logging and storage:

- Text redaction with position-based replacement
- Dictionary redaction with nested field support
- Preserves data structure while removing PII
- Only redacts high-confidence PII (>= 0.7)

### ✅ Compliance Reporting

Comprehensive audit trails and reporting:

- Historical classification tracking
- Statistical summaries
- Compliance framework coverage metrics
- Data governance maturity scoring
- **No raw PII in reports** - only aggregated statistics

---

## Quick Start

### Installation

The module is part of the AMAS codebase. No additional installation required.

### Basic Usage

```python
from amas.governance import DataClassifier, ComplianceReporter

# Initialize classifier
classifier = DataClassifier()

# Classify data
text = "Contact john.doe@example.com for support"
result = classifier.classify_data(text)

# Check results
print(f"Classification: {result.classification.value}")
print(f"GDPR Protection: {result.requires_gdpr_protection}")
print(f"PII Count: {result.pii_count}")

# Generate compliance report
reporter = ComplianceReporter()
reporter.add_classification_result(result)
report = reporter.generate_compliance_report(days=30)
```

---

## API Reference

### DataClassifier

Main class for data classification and PII detection.

#### Methods

**`classify_data(data: Any, data_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> ClassificationResult`**

Classifies data and detects compliance requirements.

**Parameters**:
- `data`: Input data to classify (str, dict, or other)
- `data_id`: Optional identifier for the data
- `context`: Optional context dictionary

**Returns**: `ClassificationResult` with classification and compliance flags

**Raises**:
- `ValueError`: If input exceeds size limits or is invalid
- `TypeError`: If input type is not supported

**Example**:
```python
classifier = DataClassifier()
result = classifier.classify_data("User email: alice@company.com")
# Result: ClassificationResult(
#   classification=DataClassification.CONFIDENTIAL,
#   requires_gdpr_protection=True,
#   pii_count=1
# )
```

**`redact_data(data: Any, classification_result: ClassificationResult) -> Any`**

Redacts PII from data based on classification result.

**Parameters**:
- `data`: Original data
- `classification_result`: Result from `classify_data()`

**Returns**: Data with PII redacted

**Example**:
```python
original = "Contact support@example.com"
result = classifier.classify_data(original)
redacted = classifier.redact_data(original, result)
# Result: "Contact ***@example.com"
```

### ComplianceReporter

Generates compliance reports and maintains audit trails.

#### Methods

**`add_classification_result(result: ClassificationResult)`**

Adds a classification result to history for reporting.

**`generate_compliance_report(days: int = 30) -> Dict[str, Any]`**

Generates comprehensive compliance report for the specified period.

**Returns**: Dictionary with:
- Summary statistics
- Classification distribution
- PII type distribution
- Compliance requirements
- Risk assessment
- Data governance score

**Example**:
```python
reporter = ComplianceReporter()
# ... add results ...
report = reporter.generate_compliance_report(days=30)
print(f"GDPR protected items: {report['compliance_requirements']['gdpr_protected_items']}")
```

### Helper Functions

**`safe_log_pii(detection: PIIDetection, message: str = "") -> str`**

Creates a safe log message that never includes raw PII.

**Example**:
```python
from amas.governance import safe_log_pii

detection = result.pii_detected[0]
safe_msg = safe_log_pii(detection, "PII detected")
logger.info(safe_msg)  # No raw PII in logs
```

**`classify_input_data(data_param: str = "data")`**

Decorator to automatically classify input data in functions.

**Example**:
```python
from amas.governance import classify_input_data

@classify_input_data(data_param="user_data")
def process_user_data(user_data: str):
    # user_data is automatically classified
    # Classification result available in kwargs['_data_classification']
    pass
```

---

## Success Criteria

All success criteria are met and verified:

### ✅ Email → Confidential + GDPR

```python
result = classifier.classify_data("Contact john@example.com")
assert result.classification == DataClassification.CONFIDENTIAL
assert result.requires_gdpr_protection is True
```

### ✅ Credit Card → Restricted + PCI

```python
result = classifier.classify_data("Card: 4532-1234-5678-9010")
assert result.classification == DataClassification.RESTRICTED
assert result.requires_pci_protection is True
```

### ✅ Compliance Reports Without Raw PII

```python
report = reporter.generate_compliance_report()
# Report contains only statistics, no raw PII values
assert "john@example.com" not in str(report)
assert "4532-1234-5678-9010" not in str(report)
```

---

## Security Features

### Input Sanitization

- **Size Limits**: MAX_INPUT_LENGTH = 1MB
- **Depth Limits**: MAX_DICT_DEPTH = 100 nesting levels
- **Null Byte Detection**: Rejects null bytes
- **Type Validation**: Validates input types

### Safe Logging

- **No Raw PII**: Never logs original PII values
- **Redaction**: Uses redacted values or hashes
- **Helper Function**: `safe_log_pii()` for safe logging

### Compliance Flag Validation

- **Auto-Correction**: Automatically corrects false negatives
- **Validation**: Ensures flags match detected PII
- **Audit Trail**: Logs all corrections

---

## Production Usage

### Example: Classify and Protect User Data

```python
from amas.governance import DataClassifier, get_compliance_reporter

classifier = DataClassifier()
reporter = get_compliance_reporter()

# Classify user data
user_data = {
    "email": "user@example.com",
    "phone": "555-123-4567",
    "name": "John Doe"
}

result = classifier.classify_data(user_data)

# Encrypt if PCI-sensitive
if result.requires_pci_protection:
    encrypted_data = encrypt_data(user_data, key=KMS_CLIENT.get_key("pci"))
    store_encrypted(encrypted_data)

# Mask for logging
safe_data = classifier.redact_data(user_data, result)
logger.info(f"Processed user data: {safe_data}")

# Enforce access control
if result.requires_gdpr_protection:
    enforce_role_based_access("gdpr_data_reader", user)

# Add to compliance tracking
reporter.add_classification_result(result)
```

### Example: Generate Compliance Report

```python
from amas.governance import get_compliance_reporter

reporter = get_compliance_reporter()

# Generate monthly compliance report
report = reporter.generate_compliance_report(days=30)

print(f"Total items classified: {report['summary']['total_data_items_classified']}")
print(f"GDPR protected: {report['compliance_requirements']['gdpr_protected_items']}")
print(f"PCI protected: {report['compliance_requirements']['pci_protected_items']}")
print(f"Governance score: {report['risk_assessment']['data_governance_score']}")
```

---

## Testing

### Running Tests

```bash
# Run all governance tests
pytest tests/test_data_classifier.py -v

# Run performance tests
pytest tests/test_data_classifier_performance.py -v

# Run standalone verification
python3 verify_data_classifier.py
```

### Test Coverage

- **PII Detection**: 6 tests
- **Data Classification**: 5 tests
- **Redaction**: 3 tests
- **Compliance Reporting**: 2 tests
- **Performance**: 6 tests
- **Integration**: 1 test

**Total**: 23 tests, all passing

---

## CI/CD Integration

The module has dedicated CI/CD pipeline (`.github/workflows/governance-ci.yml`):

- **Type Checking**: mypy + pyright
- **Linting**: flake8 + pylint
- **Testing**: pytest with coverage
- **Performance**: Benchmarks
- **Security**: bandit + safety

All checks run automatically on:
- Push to `main` or `feature/data-governance-compliance`
- Pull requests to `main`
- Changes to governance module files

---

## Configuration

### Environment Variables

No environment variables required. The module works out of the box.

### Customization

You can customize behavior by:

1. **Extending PII patterns**:
```python
detector = PIIDetector()
detector.patterns[PIIType.EMAIL].append(re.compile(r'custom@pattern\.com'))
```

2. **Adding compliance rules**:
```python
classifier = DataClassifier()
classifier.compliance_frameworks['custom'] = {
    'triggers': [PIIType.CUSTOM],
    'min_classification': DataClassification.CONFIDENTIAL
}
```

---

## Best Practices

### 1. Always Use Redaction for Logging

```python
# ❌ WRONG
logger.info(f"User email: {user_email}")

# ✅ CORRECT
result = classifier.classify_data(user_email)
redacted = classifier.redact_data(user_email, result)
logger.info(f"User email: {redacted}")
```

### 2. Check Compliance Flags Before Processing

```python
result = classifier.classify_data(data)

if result.requires_pci_protection:
    # Apply PCI-specific protections
    encrypt_data(data)
    enforce_access_controls()

if result.requires_gdpr_protection:
    # Apply GDPR-specific protections
    request_consent()
    enable_right_to_deletion()
```

### 3. Use Compliance Reporter for Audit Trails

```python
reporter = get_compliance_reporter()
reporter.add_classification_result(result)

# Generate reports regularly
monthly_report = reporter.generate_compliance_report(days=30)
```

### 4. Validate Input Before Classification

The classifier automatically validates input, but you can add additional checks:

```python
if len(data) > 1_000_000:
    raise ValueError("Data too large")

result = classifier.classify_data(data)
```

---

## Architecture

### Module Structure

```
src/amas/governance/
├── __init__.py              # Module exports
├── data_classifier.py       # Main implementation (941 lines)
└── agent_contracts.py       # Agent role contracts
```

### Key Classes

- **`PIIDetector`**: Pattern-based PII detection
- **`DataClassifier`**: Data classification engine
- **`ComplianceReporter`**: Reporting and audit trails
- **`PIIDetection`**: PII detection result
- **`ClassificationResult`**: Classification result

### Data Flow

1. **Input** → DataClassifier.classify_data()
2. **PII Detection** → PIIDetector detects PII
3. **Classification** → Determines security tier
4. **Compliance Mapping** → Sets GDPR/HIPAA/PCI flags
5. **Validation** → Ensures flags match detected PII
6. **Reporting** → ComplianceReporter tracks results

---

## Performance

### Benchmarks

- **Large Payload (1MB)**: < 1.0s
- **Credit Card Detection**: < 100ms
- **Multiple PII Types**: < 200ms
- **ReDoS Prevention**: < 500ms with malicious input

### Optimization

- Regex patterns pre-compiled at initialization
- Efficient string processing
- Caching enabled in CI/CD
- Input size limits prevent DoS

---

## Security Considerations

### Hashing

Current implementation uses SHA-256 truncated to 16 characters for tracking only.

**For Production**:
```python
import secrets
salt = secrets.token_bytes(32)  # Store securely
value_hash = hashlib.sha256(salt + value.encode()).hexdigest()
```

### Logging

- Never log `original_value` from PIIDetection
- Always use `redacted_value` or `value_hash`
- Use `safe_log_pii()` helper function

### Compliance Flags

- Default `False` is safe (flags set by detection)
- Validation ensures no false negatives
- Auto-correction with logging for audit trail

---

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "mypy: command not found"
**Solution**: Install dependencies: `pip install -r requirements-ci.txt`

**Issue**: PII not detected
**Solution**: Check confidence threshold (default 0.7), verify pattern matches

**Issue**: Compliance flags not set
**Solution**: Validation auto-corrects, check logs for warnings

---

## Related Documentation

- [Agent Contracts](src/amas/governance/agent_contracts.py)
- [CI/CD Workflow](.github/workflows/governance-ci.yml)
- [Test Suite](tests/test_data_classifier.py)
- [Performance Tests](tests/test_data_classifier_performance.py)

---

## Changelog

### Version 1.0.0 (PR #242)

- ✅ Initial implementation
- ✅ PII detection with confidence scoring
- ✅ 5-tier data classification
- ✅ Compliance framework mapping
- ✅ Redaction helpers
- ✅ Compliance reporting
- ✅ Input sanitization
- ✅ Compliance flag validation
- ✅ Comprehensive test suite
- ✅ CI/CD automation

---

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Documentation: See [docs/](docs/) directory
- Tests: Run `python3 verify_data_classifier.py`

---

## License

Part of the AMAS project. Licensed under MIT License.
