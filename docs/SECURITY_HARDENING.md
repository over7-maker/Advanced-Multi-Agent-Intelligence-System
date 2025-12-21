# Security Hardening Guide

**Date**: December 21, 2025  
**Purpose**: Security best practices for core workflows

## Security Principles

1. **Least Privilege**
   - Grant minimum required permissions
   - Use job-level permissions
   - Restrict write access

2. **Secret Management**
   - Never hardcode secrets
   - Use GitHub Secrets
   - Rotate keys regularly

3. **Input Validation**
   - Validate all inputs
   - Sanitize user data
   - Use allowlists

4. **Error Handling**
   - Don't expose sensitive data in errors
   - Log securely
   - Handle failures gracefully

## Security Practices

### 1. Permission Management

**Best Practice**:
```yaml
permissions:
  contents: read  # Minimum required
  pull-requests: write  # Only if needed
  issues: write  # Only if needed
```

**Avoid**:
```yaml
permissions:
  contents: write  # Too broad
```

### 2. Secret Handling

**Best Practice**:
```yaml
jobs:
  my_job:
    uses: ./.github/workflows/orchestrator.yml
    secrets: inherit  # Inherit securely
```

**Avoid**:
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}  # Exposed in logs
```

### 3. Input Validation

**Best Practice**:
```yaml
workflow_dispatch:
  inputs:
    mode:
      type: choice  # Restricted choices
      options: [option1, option2]
```

**Avoid**:
```yaml
workflow_dispatch:
  inputs:
    mode:
      type: string  # Unrestricted input
```

### 4. Error Handling

**Best Practice**:
```yaml
- name: Sensitive Operation
  run: |
    # Operation that might fail
  continue-on-error: true
  if: failure()
    run: echo "Operation failed"  # Generic message
```

## Security Checklist

- [ ] All workflows use least privilege permissions
- [ ] All secrets are in GitHub Secrets
- [ ] No hardcoded credentials
- [ ] All inputs are validated
- [ ] Error messages don't expose sensitive data
- [ ] Artifacts don't contain secrets
- [ ] Dependencies are from trusted sources
- [ ] Security scanning is enabled
- [ ] Compliance checks are in place

## Vulnerability Scanning

Core-6 (Security Gateway) includes:
- Safety checks for Python dependencies
- Bandit scans for security issues
- Detect-secrets for credential leaks
- Link validation for markdown files

## Compliance

Core-6 (Security Gateway) includes:
- Governance checks
- Compliance validation
- Audit trails
- Security reporting

## Incident Response

1. **Immediate Actions**
   - Disable affected workflows
   - Rotate compromised secrets
   - Review access logs

2. **Investigation**
   - Check workflow logs
   - Review recent changes
   - Identify attack vector

3. **Remediation**
   - Fix vulnerabilities
   - Update security policies
   - Improve monitoring

## Security Monitoring

Core-8 (Monitoring & Alert) provides:
- Security event monitoring
- Alert generation
- Threat detection
- Compliance tracking

