# Data Governance & Compliance Module

## Overview

The Data Governance & Compliance module provides enterprise-grade data governance capabilities for the AMAS system, including automatic PII detection, data classification, compliance framework mapping, and comprehensive audit trails.

**Status**: ✅ Production Ready  
**PR**: #242  
**Version**: 1.0.0

---

## Quick Links

- [Complete Guide](DATA_GOVERNANCE_GUIDE.md) - Comprehensive usage guide
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Examples](../../examples/governance_example.py) - Usage examples

---

## Features

✅ **Automatic PII Detection** - 13 PII types with confidence scoring  
✅ **5-Tier Classification** - Public → Top Secret  
✅ **Compliance Mapping** - GDPR, HIPAA, PCI  
✅ **Redaction Helpers** - Safe logging and storage  
✅ **Compliance Reporting** - Audit trails and summaries

---

## Quick Start

```python
from amas.governance import DataClassifier

classifier = DataClassifier()
result = classifier.classify_data("Contact: user@example.com")

print(f"Classification: {result.classification.value}")
print(f"GDPR: {result.requires_gdpr_protection}")
```

---

## Documentation

- [Data Governance Guide](DATA_GOVERNANCE_GUIDE.md) - Complete guide
- [API Reference](API_REFERENCE.md) - API documentation
- [Examples](../../examples/governance_example.py) - Code examples

---

## Testing

```bash
# Run tests
pytest tests/test_data_classifier.py -v

# Run performance tests
pytest tests/test_data_classifier_performance.py -v

# Standalone verification
python3 verify_data_classifier.py
```

---

## CI/CD

Automated CI/CD pipeline runs on every change:
- Type checking (mypy, pyright)
- Linting (flake8, pylint)
- Testing (pytest)
- Performance benchmarks
- Security scanning (bandit, safety)

See [.github/workflows/governance-ci.yml](../../.github/workflows/governance-ci.yml)

---

## Support

- Issues: [GitHub Issues](https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues)
- Documentation: [docs/governance/](docs/governance/)
