# AMAS Security Guide

## Security Model
- OIDC/JWT authentication for all endpoints
- OPA (Open Policy Agent) based policy-enforcement for APIs and agent graphs
- Strict PII detection, redaction, and compliance (GDPR/HIPAA/PCI)

## Dependency and Supply Chain Security
- Dependabot and scheduled `pip` audit for vulnerabilities
- Only signed, reviewed dependencies allowed in production
- Code and configuration review required for all PRs

## Vulnerability Reporting
- If you discover a vulnerability, please report it by creating a private security advisory via GitHub or emailing the project maintainer.

## Penetration Testing
- Regular internal and third-party pen-tests before production
- All critical CVEs prioritized for patch within 2 business days

## More Information
Advanced security recommendations, release audit logs, and previous reports are available in the `/docs/security/` directory.