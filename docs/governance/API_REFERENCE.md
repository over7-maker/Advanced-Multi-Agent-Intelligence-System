# Data Governance & Compliance API Reference

## Module: `amas.governance`

Complete API reference for the Data Governance & Compliance module.

---

## Enums

### `DataClassification`

5-tier data classification levels.

```python
class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"
```

### `PIIType`

Types of Personally Identifiable Information detected.

```python
class PIIType(str, Enum):
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
```

---

## Classes

### `PIIDetection`

Result of PII detection in data.

**Attributes**:
- `pii_type: PIIType` - Type of PII detected
- `confidence: float` - Confidence score (0.0-1.0)
- `location: str` - Where in the data (position or field path)
- `value_hash: str` - Hashed value for tracking
- `redacted_value: str` - Redacted representation
- `original_value: str` - Original detected value (for redaction)
- `context: Optional[str]` - Context information

**Example**:
```python
detection = PIIDetection(
    pii_type=PIIType.EMAIL,
    confidence=0.95,
    location="position_10_30",
    value_hash="abc123...",
    redacted_value="***@example.com",
    original_value="user@example.com"
)
```

### `ClassificationResult`

Result of data classification analysis.

**Attributes**:
- `data_id: str` - Unique identifier for the data
- `classification: DataClassification` - Security classification
- `confidence: float` - Overall confidence (0.0-1.0)
- `pii_detected: List[PIIDetection]` - List of PII detections
- `pii_count: int` - Number of PII items detected
- `highest_pii_confidence: float` - Highest PII confidence score
- `requires_gdpr_protection: bool` - GDPR compliance flag
- `requires_hipaa_protection: bool` - HIPAA compliance flag
- `requires_pci_protection: bool` - PCI compliance flag
- `classified_at: datetime` - Timestamp of classification
- `classifier_version: str` - Version of classifier
- `processing_time_ms: float` - Processing time in milliseconds

**Example**:
```python
result = ClassificationResult(
    data_id="data_123",
    classification=DataClassification.CONFIDENTIAL,
    confidence=0.85,
    pii_detected=[detection1, detection2],
    pii_count=2,
    requires_gdpr_protection=True
)
```

### `PIIDetector`

Advanced PII detection with configurable patterns.

**Methods**:

**`detect_pii_in_text(text: str, context: Optional[str] = None) -> List[PIIDetection]`**

Detects PII in text content with confidence scoring.

**Parameters**:
- `text`: Text to analyze
- `context`: Optional context (e.g., field name)

**Returns**: List of PIIDetection objects

**Example**:
```python
detector = PIIDetector()
detections = detector.detect_pii_in_text("Email: user@example.com")
```

**`detect_pii_in_dict(data: Dict[str, Any], parent_key: str = "") -> List[PIIDetection]`**

Recursively detects PII in dictionary structures.

**Parameters**:
- `data`: Dictionary to analyze
- `parent_key`: Parent key path (for nested structures)

**Returns**: List of PIIDetection objects

**Example**:
```python
data = {"user": {"email": "user@example.com"}}
detections = detector.detect_pii_in_dict(data)
```

### `DataClassifier`

Intelligent data classifier with compliance mapping.

**Constants**:
- `MAX_INPUT_LENGTH = 1_000_000` - Maximum input size (1MB)
- `MAX_DICT_DEPTH = 100` - Maximum dictionary nesting depth

**Methods**:

**`classify_data(data: Any, data_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> ClassificationResult`**

Classify data and detect compliance requirements.

**Parameters**:
- `data`: Input data (str, dict, or other)
- `data_id`: Optional identifier
- `context`: Optional context dictionary

**Returns**: ClassificationResult

**Raises**:
- `ValueError`: If input exceeds limits or is invalid
- `TypeError`: If input type is not supported

**Example**:
```python
classifier = DataClassifier()
result = classifier.classify_data("Contact: john@example.com")
```

**`redact_data(data: Any, classification_result: ClassificationResult) -> Any`**

Redact PII from data based on classification result.

**Parameters**:
- `data`: Original data
- `classification_result`: Result from classify_data()

**Returns**: Data with PII redacted

**Example**:
```python
original = "Email: user@example.com"
result = classifier.classify_data(original)
redacted = classifier.redact_data(original, result)
# Result: "Email: ***@example.com"
```

### `ComplianceReporter`

Generate compliance reports and maintain audit trails.

**Methods**:

**`add_classification_result(result: ClassificationResult)`**

Add classification result to history.

**Parameters**:
- `result`: ClassificationResult to add

**Example**:
```python
reporter = ComplianceReporter()
reporter.add_classification_result(result)
```

**`generate_compliance_report(days: int = 30) -> Dict[str, Any]`**

Generate comprehensive compliance report.

**Parameters**:
- `days`: Number of days to include in report (default: 30)

**Returns**: Dictionary with report data

**Report Structure**:
```python
{
    "report_period_days": 30,
    "generated_at": "2025-11-09T00:00:00Z",
    "summary": {
        "total_data_items_classified": 100,
        "items_containing_pii": 45,
        "pii_detection_rate_percent": 45.0
    },
    "classification_distribution": {
        "confidential": 30,
        "restricted": 15
    },
    "pii_type_distribution": {
        "email": 25,
        "credit_card": 10
    },
    "compliance_requirements": {
        "gdpr_protected_items": 30,
        "hipaa_protected_items": 5,
        "pci_protected_items": 10
    },
    "risk_assessment": {
        "high_risk_items": 15,
        "avg_pii_confidence": 0.85,
        "data_governance_score": 87.5
    }
}
```

---

## Functions

### `get_data_classifier() -> DataClassifier`

Get global data classifier instance (singleton).

**Returns**: DataClassifier instance

**Example**:
```python
from amas.governance import get_data_classifier

classifier = get_data_classifier()
```

### `get_compliance_reporter() -> ComplianceReporter`

Get global compliance reporter instance (singleton).

**Returns**: ComplianceReporter instance

**Example**:
```python
from amas.governance import get_compliance_reporter

reporter = get_compliance_reporter()
```

### `safe_log_pii(detection: PIIDetection, message: str = "") -> str`

Create a safe log message that never includes raw PII.

**Parameters**:
- `detection`: PIIDetection object
- `message`: Optional message prefix

**Returns**: Safe log string

**Example**:
```python
from amas.governance import safe_log_pii

safe_msg = safe_log_pii(detection, "PII detected")
logger.info(safe_msg)
```

### `classify_input_data(data_param: str = "data")`

Decorator to automatically classify input data.

**Parameters**:
- `data_param`: Name of the parameter containing data (default: "data")

**Returns**: Decorator function

**Example**:
```python
from amas.governance import classify_input_data

@classify_input_data(data_param="user_data")
def process_user_data(user_data: str, _data_classification=None):
    if _data_classification and _data_classification.requires_gdpr_protection:
        # Apply GDPR protections
        pass
    return processed_data
```

---

## Error Handling

### Exceptions

**`ValueError`**: Raised when:
- Input exceeds size limits
- Input contains null bytes
- Dictionary exceeds depth limits
- Invalid confidence values
- Invalid hash values

**`TypeError`**: Raised when:
- Input is None
- Input type is not supported

### Example Error Handling

```python
try:
    result = classifier.classify_data(large_data)
except ValueError as e:
    logger.error(f"Classification failed: {e}")
    # Handle error appropriately
except TypeError as e:
    logger.error(f"Invalid input type: {e}")
    # Handle error appropriately
```

---

## Performance Considerations

### Input Size Limits

- **MAX_INPUT_LENGTH**: 1MB (prevents DoS)
- **MAX_DICT_DEPTH**: 100 levels (prevents stack overflow)

### Optimization Tips

1. **Pre-classify**: Classify data once, reuse results
2. **Batch Processing**: Process multiple items together
3. **Caching**: Cache classification results when possible
4. **Selective Redaction**: Only redact high-confidence PII

---

## Security Best Practices

1. **Never log original PII**:
   ```python
   # ❌ WRONG
   logger.info(f"Email: {detection.original_value}")
   
   # ✅ CORRECT
   logger.info(f"Email: {detection.redacted_value}")
   ```

2. **Use safe logging helper**:
   ```python
   safe_msg = safe_log_pii(detection)
   logger.info(safe_msg)
   ```

3. **Encrypt sensitive data**:
   ```python
   if result.requires_pci_protection:
       encrypted = encrypt_data(data)
   ```

4. **Validate compliance flags**:
   ```python
   # Validation happens automatically
   # Check logs for auto-corrections
   ```

---

## Examples

See [examples/](examples/) directory for complete usage examples.
