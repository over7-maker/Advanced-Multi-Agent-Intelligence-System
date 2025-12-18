# Phase 2 Workflows - Usage Guide

**Version**: 2.0  
**Date**: December 18, 2025  
**Status**: Ready for Use  

---

## Overview

This guide explains how to use the 8 consolidated Phase 2 workflows in your repository.

---

## Workflow Descriptions

### 1. Master Orchestrator (`00-master-orchestrator.yml`)

**Purpose**: Central orchestration of all AI processes  
**Triggers**: Push to main, Hourly schedule  
**Key Jobs**: orchestrate, initialize, route_tasks, monitor

**Usage**:
```bash
# Triggered automatically on push
git push origin main

# Or runs hourly via schedule
# No manual trigger needed
```

---

### 2. AI Agents (`01-ai-agents.yml`)

**Purpose**: Intelligent agent-based automation  
**Triggers**: Push, Pull Requests, Every 2 hours  
**Key Jobs**: analyze, plan, code, test, review, learn

**Usage**:
```bash
# Triggered on push or PR
git push origin main
git pull-request create
```

---

### 3. Audit & Documentation (`02-audit-documentation.yml`)

**Purpose**: Project auditing and documentation  
**Triggers**: Push to main, Weekly schedule  
**Key Jobs**: audit, document, publish

**Usage**:
```bash
# Runs automatically on push
# Also runs weekly on Sundays at 1 AM
```

---

### 4. Build & Deploy (`03-build-deploy.yml`)

**Purpose**: Production CI/CD pipeline  
**Triggers**: Push to main  
**Key Jobs**: build, test, deploy, verify

**Usage**:
```bash
# Triggered automatically on merge to main
git push origin main
```

---

### 5. Security (`04-security.yml`)

**Purpose**: Security scanning and threat intelligence  
**Triggers**: Push, Daily schedule  
**Key Jobs**: scan, analyze, report

**Usage**:
```bash
# Runs daily automatically
# Also runs on code push
```

---

### 6. Quality (`05-quality.yml`)

**Purpose**: Code quality and performance  
**Triggers**: Push  
**Key Jobs**: quality_check, performance_test, benchmark

**Usage**:
```bash
# Triggered on every push
# Validates code quality
```

---

### 7. CI/CD Pipeline (`06-cicd-pipeline.yml`)

**Purpose**: Core CI/CD operations  
**Triggers**: Push, Pull Requests  
**Key Jobs**: lint, build, push, publish

**Usage**:
```bash
# Runs on push and PRs
# Core build pipeline
```

---

### 8. Governance (`07-governance.yml`)

**Purpose**: Organizational governance and compliance  
**Triggers**: Push, Weekly  
**Key Jobs**: compliance, audit

**Usage**:
```bash
# Compliance checks run weekly
# Also on code push
```

---

## Monitoring

### GitHub Actions Tab
1. Navigate to **Actions** tab in repository
2. Select workflow from left sidebar
3. View run status and logs

### Checking Specific Run
```bash
# View workflow runs
gh workflow view

# View run details
gh workflow-run view <run-id>
```

---

## Troubleshooting

### Workflow Failed
1. Click on the failed run
2. Review error logs
3. Check job output
4. Fix and push again

### Viewing Logs
```bash
# Download logs
gh workflow-run download <run-id>
```

---

## Best Practices

1. **Always review PRs before merge**
2. **Check CI status before deployment**
3. **Monitor security scan results**
4. **Keep workflows in sync with code**
5. **Document custom environment variables**

---

## Environment Variables

Key variables used across workflows:

```yaml
CONSOLIDATION_VERSION: "2.0"
ENABLED_PROVIDERS: "26"
LOG_LEVEL: "INFO"
AGENTS_ENABLED: "12"
ML_MODEL: "latest"
```

---

**Status**: Ready for Production Use  
**Last Updated**: December 18, 2025
