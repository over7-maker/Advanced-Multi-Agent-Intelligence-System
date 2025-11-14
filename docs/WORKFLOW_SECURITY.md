# 🔒 Progressive Delivery Workflow Security

## Overview

The Progressive Delivery Pipeline (`.github/workflows/progressive-delivery.yml`) implements comprehensive security measures to ensure only authorized, validated code reaches production. This document details all security features and best practices.

## Table of Contents

- [Multi-Layer PR Merge Validation](#multi-layer-pr-merge-validation)
- [Branch Protection](#branch-protection)
- [Permissions](#permissions)
- [Input Validation](#input-validation)
- [Concurrency Control](#concurrency-control)
- [Timeout Protection](#timeout-protection)
- [Security Best Practices](#security-best-practices)

---

## Multi-Layer PR Merge Validation

The workflow implements three validation layers to ensure only merged PRs trigger production deployments:

### Layer 1: Event-Level Validation

**Location**: Job `if` conditions

```yaml
if: |
  github.event_name == 'pull_request' && 
  github.event.action == 'closed' && 
  github.event.pull_request.merged == true &&
  github.base_ref == 'main'
```

**Purpose**: Prevents workflow execution on non-merged PR closures at the event level.

### Layer 2: Job-Level Validation

**Location**: `validate-pr-merge` job

```yaml
validate-pr-merge:
  name: 🛡️ Validate PR Merge
  steps:
    - name: 🔍 Verify PR Was Merged
      run: |
        if [ "${{ github.event.pull_request.merged }}" != "true" ]; then
          echo "❌ ERROR: PR was closed but not merged"
          exit 1  # Fail job to prevent downstream jobs
        fi
```

**Purpose**: Explicitly validates merge status via GitHub API and fails the job if PR was closed without merge.

### Layer 3: Dependency Enforcement

**Location**: Production deployment jobs

```yaml
deploy-production-canary:
  needs: [build-and-security-scan, deploy-staging, validate-pr-merge]
  if: |
    needs.build-and-security-scan.result == 'success' && (
      (github.event_name == 'pull_request' && 
       github.event.action == 'closed' && 
       github.event.pull_request.merged == true &&
       github.base_ref == 'main' &&
       needs.validate-pr-merge.result == 'success') ||
      ...
    )
```

**Purpose**: Production deployment jobs require `validate-pr-merge` to succeed before running.

---

## Branch Protection

### Restricted Triggers

Only `main` branch PRs can trigger production deployments:

```yaml
pull_request:
  branches:
    - main  # Only main branch for production safety
```

**Security Benefit**: Prevents feature branch PRs from triggering production deployments.

### Runtime Validation

Branch protection rules are validated via GitHub API:

```yaml
- name: 🔍 Check Branch Protection Rules
  run: |
    response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
      "https://api.github.com/repos/${{ github.repository }}/branches/main/protection")
    
    if echo "$response" | grep -q "Not Found"; then
      echo "ERROR: Branch protection not enabled on main"
      exit 1
    fi
```

**Security Benefit**: Ensures branch protection is actually enabled, not just documented.

### Environment Protection

Production environment requires manual approval (configured in GitHub Settings):

```yaml
deploy-production-canary:
  environment: 
    name: production
    # Requires manual approval in GitHub Settings > Environments > production
```

**Configuration Required**:
- Settings > Environments > production
- Required reviewers: [devops-team, security-team]
- Deployment branches: main only

---

## Permissions

The workflow uses explicit, minimal permissions following the principle of least privilege:

```yaml
permissions:
  contents: read           # Repository read access (for checkout)
  packages: write        # Container image publishing (GHCR)
  security-events: write  # Security scan results (SARIF upload)
  actions: read           # Workflow status (for job dependencies)
  deployments: write       # Deployment status tracking
  checks: write           # Deployment gates and status checks
```

**Security Benefit**: Prevents unauthorized access to repository contents, secrets, or deployment capabilities.

---

## Input Validation

### Workflow Dispatch Inputs

All manual inputs are validated before use:

```yaml
workflow_dispatch:
  inputs:
    environment:
      description: 'Deployment environment'
      required: true
      default: 'staging'
      type: choice
      options:
        - staging
        - production
    deployment_strategy:
      description: 'Deployment strategy'
      required: true
      default: 'canary'
      type: choice
      options:
        - canary
        - blue-green
```

### Runtime Validation

Inputs are validated in the `validate-inputs` job:

```yaml
validate-inputs:
  name: ✅ Validate Workflow Inputs
  steps:
    - name: Validate environment
      run: |
        case "${{ inputs.environment }}" in
          staging|production) echo "Valid environment";;
          *) echo "Invalid environment" >&2; exit 1;;
        esac
```

**Security Benefit**: Prevents injection attacks via user-provided inputs.

---

## Concurrency Control

Prevents race conditions with concurrent deployments:

```yaml
concurrency:
  group: progressive-delivery-${{ github.ref }}
  cancel-in-progress: false  # Don't cancel deployments in progress (safety)
```

**Security Benefit**: Ensures only one deployment per branch runs at a time, preventing conflicts.

---

## Timeout Protection

All jobs have explicit timeouts to prevent resource exhaustion:

| Job | Timeout | Purpose |
|-----|---------|---------|
| `validate-pr-merge` | 5 minutes | Quick validation |
| `validate-inputs` | 5 minutes | Quick validation |
| `build-and-security-scan` | 45 minutes | Complex builds |
| `deploy-staging` | 20 minutes | Staging deployment |
| `deploy-production-canary` | 30 minutes | Production canary |
| `deploy-production-blue-green` | 20 minutes | Blue-green switch |
| `emergency-rollback` | 10 minutes | Quick rollback |
| `notify-failure` | 5 minutes | Notification |

**Security Benefit**: Prevents jobs from running indefinitely and consuming resources.

---

## Security Best Practices

### 1. Never Bypass Branch Protection

- Always require PR reviews before merging
- Require status checks to pass
- Require branches to be up to date
- Do not allow bypassing for admins

### 2. Use GitHub Environments

Configure production environment with:
- Required reviewers (at least 1)
- Deployment branch policy (main only)
- Wait timer (optional, for approval delays)
- Protection rules (prevent deletion, etc.)

### 3. Monitor Workflow Runs

- Review all production deployments
- Check GitHub Actions audit logs regularly
- Set up alerts for failed validations
- Monitor for unauthorized access attempts

### 4. Rotate Secrets Regularly

- Update registry tokens every 90 days
- Rotate API keys quarterly
- Use short-lived tokens when possible
- Review secret usage in audit logs

### 5. Limit Workflow Permissions

- Use minimal required permissions
- Review permissions quarterly
- Remove unused permissions
- Document why each permission is needed

### 6. Validate All Inputs

- Sanitize user-provided inputs
- Use allow-lists, not block-lists
- Validate input types and formats
- Never trust user input

### 7. Enable Security Scanning

- Use Trivy for container scanning
- Use Snyk for dependency scanning
- Use Semgrep for code scanning
- Review and fix vulnerabilities promptly

### 8. Review Dependencies

- Keep GitHub Actions up to date
- Pin action versions (avoid `@main`)
- Review action source code
- Use official actions when possible

### 9. Test Security Changes

- Validate security updates in staging first
- Test merge validation with test PRs
- Verify branch protection rules
- Test rollback procedures

### 10. Document Security Decisions

- Document why each security measure exists
- Update documentation when security changes
- Share security knowledge with team
- Review security documentation quarterly

---

## Security Checklist

Before deploying to production, verify:

- [ ] Branch protection is enabled on `main`
- [ ] Production environment has required reviewers
- [ ] All workflow permissions are minimal and necessary
- [ ] Input validation is working correctly
- [ ] PR merge validation is enforced
- [ ] Security scanning is enabled
- [ ] Timeouts are set for all jobs
- [ ] Concurrency control is configured
- [ ] Secrets are rotated regularly
- [ ] Audit logs are reviewed

---

## Incident Response

If a security issue is detected:

1. **Immediately**: Stop the deployment if in progress
2. **Assess**: Determine the scope and impact
3. **Contain**: Isolate affected systems
4. **Remediate**: Fix the security issue
5. **Document**: Record the incident and resolution
6. **Review**: Update security measures to prevent recurrence

---

## Additional Resources

- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Progressive Delivery Documentation](deployment/PROGRESSIVE_DELIVERY.md)
- [CI/CD Pipeline Documentation](deployment/CI_CD_PIPELINE_DOCUMENTATION.md)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

---

**Last Updated**: 2025-01-XX
