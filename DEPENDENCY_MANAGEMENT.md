# 📦 AMAS Dependency Management Guide

## Overview

This guide covers the comprehensive dependency management strategy for AMAS, including vulnerability scanning, automated updates, and security best practices.

## 📋 Dependency Files

### Production Dependencies
- **`requirements.txt`**: Production dependencies with exact versions
- **`requirements-dev.txt`**: Development dependencies with exact versions
- **`requirements-test.txt`**: Testing dependencies with exact versions
- **`requirements-monitoring.txt`**: Monitoring dependencies with exact versions

### Version Pinning Strategy
All dependencies are pinned to exact versions to ensure reproducible builds:

```txt
# Example from requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.4
pydantic-settings==2.7.0
```

## 🔍 Vulnerability Scanning

### Automated Security Scanning

#### 1. Safety Scan
```bash
# Run Safety vulnerability scan
python3 -m safety check

# Run with JSON output
python3 -m safety check --json > safety-report.json

# Run with specific requirements file
python3 -m safety check --file requirements.txt
```

#### 2. pip-audit Scan
```bash
# Run pip-audit vulnerability scan
python3 -m pip_audit

# Run with JSON output
python3 -m pip_audit --format=json > pip-audit-report.json

# Run with specific requirements file
python3 -m pip_audit --file requirements.txt
```

#### 3. Bandit Security Linting
```bash
# Run Bandit security linting
python3 -m bandit -r src/

# Run with JSON output
python3 -m bandit -r src/ -f json -o bandit-report.json

# Run with specific configuration
python3 -m bandit -r src/ -c .bandit
```

### Comprehensive Security Scan
```bash
# Run comprehensive security scan
python3 scripts/security_scan.py

# This will run all security scans and generate a report
```

## 🔄 Automated Dependency Updates

### CI/CD Pipeline Integration

The CI/CD pipeline automatically checks for dependency updates:

```yaml
# .github/workflows/ci.yml
dependency-update:
  name: Dependency Update Check
  runs-on: ubuntu-latest
  if: github.event_name == 'schedule'
  steps:
    - name: Check for dependency updates
      run: |
        pip-compile --upgrade requirements.in > requirements-updated.txt
        diff requirements.txt requirements-updated.txt || echo "Dependencies need updating"
```

### Manual Dependency Updates

#### 1. Check for Updates
```bash
# Check for outdated packages
pip list --outdated

# Check specific package
pip show <package-name>
```

#### 2. Update Dependencies
```bash
# Update a specific package
pip install --upgrade <package-name>

# Update all packages (use with caution)
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```

#### 3. Regenerate Requirements
```bash
# Generate new requirements.txt with updated versions
pip freeze > requirements-new.txt

# Compare with existing requirements
diff requirements.txt requirements-new.txt
```

## 🛡️ Security Best Practices

### 1. Regular Security Audits
- **Weekly**: Automated vulnerability scans in CI/CD
- **Monthly**: Manual security review
- **Quarterly**: Comprehensive security audit

### 2. Dependency Selection Criteria
- **Active Maintenance**: Choose packages with regular updates
- **Security Track Record**: Avoid packages with known vulnerabilities
- **Community Support**: Prefer packages with active community
- **License Compatibility**: Ensure licenses are compatible

### 3. Vulnerability Response
- **Critical**: Fix immediately (within 24 hours)
- **High**: Fix within 1 week
- **Medium**: Fix within 1 month
- **Low**: Fix within 3 months

## 📊 Monitoring and Reporting

### Security Reports
- **Safety Report**: `safety-report.json`
- **pip-audit Report**: `pip-audit-report.json`
- **Bandit Report**: `bandit-report.json`
- **Combined Report**: `security_report.json`

### Metrics Tracking
- **Vulnerability Count**: Track number of vulnerabilities over time
- **Update Frequency**: Monitor how often dependencies are updated
- **Security Score**: Calculate overall security score

## 🔧 Configuration Files

### .bandit Configuration
```ini
[bandit]
exclude_dirs = src/amas
skips = B311,B615,B104
```

### Safety Configuration
```yaml
# .safety.yml
ignore:
  - 12345  # Ignore specific vulnerability IDs
  - 67890
```

### pip-audit Configuration
```yaml
# .pip-audit.yml
ignore:
  - CVE-2023-1234
  - CVE-2023-5678
```

## 🚀 Deployment Considerations

### Production Deployment
1. **Pin All Versions**: Never use version ranges in production
2. **Security Scan**: Run security scans before deployment
3. **Dependency Audit**: Audit all dependencies for security issues
4. **Update Strategy**: Have a clear strategy for dependency updates

### Staging Environment
1. **Test Updates**: Test dependency updates in staging first
2. **Security Validation**: Validate security fixes in staging
3. **Performance Testing**: Ensure updates don't impact performance

## 📝 Documentation Requirements

### Dependency Documentation
- **Purpose**: Document why each dependency is needed
- **Version**: Document version selection rationale
- **Security**: Document security considerations
- **Updates**: Document update procedures

### Change Log
- **Version Changes**: Document all version changes
- **Security Fixes**: Document security-related updates
- **Breaking Changes**: Document any breaking changes

## 🔍 Troubleshooting

### Common Issues

#### 1. Version Conflicts
```bash
# Check for version conflicts
pip check

# Resolve conflicts
pip install --upgrade <conflicting-package>
```

#### 2. Security Vulnerabilities
```bash
# Check specific vulnerability
python3 -m safety check --json | grep <vulnerability-id>

# Update vulnerable package
pip install --upgrade <vulnerable-package>
```

#### 3. Dependency Resolution
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 📚 Additional Resources

### Security Tools
- **Safety**: https://github.com/pyupio/safety
- **pip-audit**: https://github.com/pypa/pip-audit
- **Bandit**: https://github.com/PyCQA/bandit

### Best Practices
- **OWASP Dependency Check**: https://owasp.org/www-project-dependency-check/
- **Python Security**: https://python-security.readthedocs.io/
- **Dependency Management**: https://packaging.python.org/guides/dependency-management/

## 🎯 Success Metrics

### Security Metrics
- **Zero Critical Vulnerabilities**: No critical vulnerabilities in production
- **Low Vulnerability Count**: Minimal high/medium vulnerabilities
- **Fast Response Time**: Quick response to security issues

### Quality Metrics
- **Dependency Health**: All dependencies actively maintained
- **Update Frequency**: Regular dependency updates
- **Security Score**: High security score in scans

---

**Note**: This dependency management strategy ensures AMAS maintains high security standards while providing reliable, reproducible builds across all environments.