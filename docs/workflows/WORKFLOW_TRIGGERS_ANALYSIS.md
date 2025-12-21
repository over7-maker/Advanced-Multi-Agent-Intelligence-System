# GitHub Actions Workflow Triggers Analysis

## Overview

This document provides a comprehensive analysis of all workflow triggers across the 40+ GitHub Actions workflows in the AMAS project. Understanding triggers is critical for optimizing CI/CD performance and preventing unnecessary workflow executions.

## Trigger Categories

### 1. Pull Request Triggers

#### PR Event Types Used

| Event Type | Workflows Using It | Purpose |
|------------|-------------------|---------|
| `opened` | 25+ workflows | Initial PR analysis |
| `synchronize` | 25+ workflows | Re-analysis on new commits |
| `reopened` | 20+ workflows | Re-analysis when PR reopened |
| `closed` | 8 workflows | Cleanup, final analysis |
| `merged` | 5 workflows | Post-merge actions |
| `ready_for_review` | 1 workflow | Quality checks when PR ready |

#### PR Branch Filters

**Target Branches:**
- `main` - Most common (production protection)
- `develop` - Development branch
- `feature/*` - Feature branches (some workflows)
- No filter - All PRs (some workflows)

**Key Workflows with PR Triggers:**

1. **bulletproof-ai-pr-analysis.yml**
   ```yaml
   pull_request:
     types: [opened, synchronize, reopened]
     branches: [main, develop]
   ```
   - **Purpose**: AI-powered PR analysis
   - **Frequency**: Every PR update to main/develop
   - **Impact**: High (runs AI analysis)

2. **pr-ci-checks.yml**
   ```yaml
   pull_request:
     types: [opened, synchronize, reopened, ready_for_review]
   ```
   - **Purpose**: Code quality and security checks
   - **Frequency**: All PRs, all events
   - **Impact**: Medium (code quality validation)

3. **governance-ci.yml**
   ```yaml
   pull_request:
     branches: [main]
     paths:
       - 'src/amas/governance/**/*.py'
       - 'tests/test_data_classifier*.py'
       # ... more paths
   ```
   - **Purpose**: Governance module CI
   - **Frequency**: Only when governance files change
   - **Impact**: Low (path-filtered)

4. **web-ci.yml**
   ```yaml
   pull_request:
     paths:
       - 'web/**'
   ```
   - **Purpose**: Frontend CI
   - **Frequency**: Only when web files change
   - **Impact**: Low (path-filtered)

### 2. Push Event Triggers

#### Push Branch Patterns

| Pattern | Workflows | Purpose |
|---------|-----------|---------|
| `main` | 15+ workflows | Production deployments |
| `develop` | 10+ workflows | Development pipeline |
| `feature/*` | 8 workflows | Feature branch testing |
| `hotfix/*` | 5 workflows | Hotfix handling |
| All branches | 3 workflows | Universal triggers |

#### Path-Based Filtering

Several workflows use path filters to optimize execution:

**governance-ci.yml:**
- Only triggers on governance-related files
- Reduces unnecessary runs by ~90%

**web-ci.yml:**
- Only triggers on `web/**` changes
- Prevents backend workflows from running on frontend-only changes

**progressive-delivery.yml:**
- Excludes docs and templates
- Only runs on code changes

**test-production.yml:**
- Only on infrastructure files (Dockerfile, k8s, nginx)
- Prevents runs on code-only changes

### 3. Schedule Triggers (Cron)

#### Scheduled Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| **00-master-ai-orchestrator.yml** | `0 */6 * * *` (every 6 hours) | Continuous AI orchestration |
| **04-ai-enhanced-build-deploy.yml** | `0 */12 * * *` (every 12 hours) | Continuous deployment |
| **07-ai-enhanced-cicd-pipeline.yml** | `0 */8 * * *` (every 8 hours) | Continuous integration |
| **05-ai-security-threat-intelligence.yml** | `0 */2 * * *` (every 2 hours) | Security monitoring |
| **comprehensive-audit.yml** | `0 2 * * 1` (Monday 2AM) | Weekly audit |
| **workflow-audit-monitor.yml** | `0 0 1 * *` (1st of month) | Monthly audit |
| **ai-agent-project-audit-documentation.yml** | `0 2 * * 0` (Sunday 2AM) | Weekly documentation audit |
| **ai-adaptive-prompt-improvement.yml** | `0 18 * * *` (6 PM daily) | Daily prompt optimization |
| **ai-enhanced-version-package-build.yml** | `0 4 * * 1` (Monday 4AM) | Weekly package build |

**Total Scheduled Executions per Day**: **~22 runs/day** from the daily/interval crons (4 + 12 + 3 + 2 + 1), plus ~0.45/day on average from weekly/monthly jobs (≈ **~22–23/day** averaged).

### 4. Manual Dispatch Triggers

#### Workflow Dispatch Usage

**Most workflows support manual dispatch** with various input options:

**Common Input Patterns:**

1. **Mode Selection**
   ```yaml
   inputs:
     mode:
       description: 'Execution Mode'
       type: choice
       options: [intelligent, fast, comprehensive]
   ```

2. **Environment Selection**
   ```yaml
   inputs:
     environment:
       description: 'Target Environment'
       type: choice
       options: [development, staging, production]
   ```

3. **Component Selection**
   ```yaml
   inputs:
     target_components:
       description: 'Components (comma-separated)'
       type: string
   ```

**Key Manual-Only Workflows:**
- `auto-format-and-commit.yml` - Code formatting
- `simple-audit-test.yml` - Testing workflows
- `workflow-audit-monitor.yml` - Workflow auditing

### 5. Issue Event Triggers

#### Issue Event Types

| Event Type | Workflows | Purpose |
|------------|-----------|---------|
| `opened` | 5 workflows | Initial issue analysis |
| `edited` | 3 workflows | Re-analysis on edits |
| `reopened` | 2 workflows | Re-analysis on reopen |
| `labeled` | 3 workflows | Label-based actions |
| `closed` | 2 workflows | Cleanup actions |

**Key Issue-Triggered Workflows:**

1. **02-ai-agentic-issue-auto-responder.yml**
   ```yaml
   issues:
     types: [opened, reopened, labeled, edited]
   ```
   - Auto-responds to issues
   - Classifies and labels issues

2. **ai-agentic-issue-auto-responder.yml**
   ```yaml
   issues:
     types: [opened, reopened, labeled, edited]
   issue_comment:
     types: [created, edited]
   ```
   - Responds to issues and comments

3. **ai-adaptive-prompt-improvement.yml**
   ```yaml
   issues:
     types: [opened, labeled]
   ```
   - Uses issues to trigger prompt improvements

### 6. Release Event Triggers

#### Release Event Types

| Event Type | Workflows | Purpose |
|------------|-----------|---------|
| `published` | 5 workflows | Production release |
| `created` | 3 workflows | Release preparation |
| `prereleased` | 2 workflows | Pre-release validation |
| `edited` | 2 workflows | Release updates |
| `deleted` | 1 workflow | Release cleanup |

**Key Release Workflows:**
- `production-cicd.yml` - Production deployment
- `04-ai-enhanced-build-deploy.yml` - Build and deploy
- `07-ai-enhanced-cicd-pipeline.yml` - Full CI/CD pipeline

## Trigger Optimization Patterns

### 1. Path-Based Filtering

**Benefits:**
- Reduces unnecessary workflow runs by 70-90%
- Faster feedback for relevant changes
- Lower GitHub Actions minutes usage

**Examples:**
```yaml
# Only run on specific paths
paths:
  - 'src/amas/governance/**/*.py'
  - 'tests/test_data_classifier*.py'
```

### 2. Concurrency Control

**Pattern:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Benefits:**
- Prevents duplicate runs
- Saves compute resources
- Faster feedback (cancels outdated runs)

**Used in:** 15+ workflows

### 3. Branch Filtering

**Patterns:**
- `branches: [main]` - Production only
- `branches: [main, develop]` - Main branches
- `branches-ignore: ['**']` - Exclude all (PRs only)

### 4. Event Type Filtering

**Optimization:**
- Only listen to relevant events
- Avoid `closed` events if not needed
- Use `synchronize` for re-analysis

## Trigger Frequency Analysis

### High Frequency Workflows

| Workflow | Frequency | Impact |
|----------|-----------|--------|
| pr-ci-checks.yml | Every PR event | High |
| bulletproof-ai-pr-analysis.yml | Every PR to main/develop | High |
| web-ci.yml | Every web/** change | Medium |
| governance-ci.yml | Every governance change | Low |

### Low Frequency Workflows

| Workflow | Frequency | Impact |
|----------|-----------|--------|
| comprehensive-audit.yml | Weekly | Low |
| workflow-audit-monitor.yml | Monthly | Low |
| ai-enhanced-version-package-build.yml | Weekly | Low |

### Scheduled Workflows Impact

**Daily Executions:**
- AI Orchestrator: 4 runs/day
- Security Monitoring: 12 runs/day
- CI/CD Pipeline: 3 runs/day
- Build/Deploy: 2 runs/day
- Daily prompt improvement: 1 run/day

**Total Scheduled Runs/Day**: **~22 runs/day** (not counting weekly/monthly averages)

## Recommendations

### 1. Consolidate PR Analyzers

**Current State:**
- `bulletproof-ai-pr-analysis.yml` (Primary)
- `ai_pr_analyzer.yml` (Legacy)
- `real-ai-analysis.yml` (Validator)

**Recommendation:**
- Keep only `bulletproof-ai-pr-analysis.yml`
- Remove or disable others
- **Savings**: ~2 workflow runs per PR

### 2. Optimize Schedule Frequency

**Current State:**
- Some workflows run every 2-6 hours
- May be excessive for some use cases

**Recommendation:**
- Review actual usage patterns
- Adjust schedules based on need
- **Potential Savings**: 30-50% of scheduled runs

### 3. Enhance Path Filtering

**Current State:**
- Only 5 workflows use path filtering
- Most workflows run on all changes

**Recommendation:**
- Add path filters to more workflows
- **Potential Savings**: 40-60% reduction in runs

### 4. Implement Workflow Dependencies

**Current State:**
- Workflows run independently
- No coordination between related workflows

**Recommendation:**
- Use `workflow_call` for reusable workflows
- Chain related workflows
- **Benefit**: Better organization, easier maintenance

## Trigger Statistics

### Total Workflow Count: 40+

### Trigger Distribution:

- **PR Triggers**: 30+ workflows (75%)
- **Push Triggers**: 25+ workflows (62%)
- **Schedule Triggers**: 9 workflows (22%)
- **Manual Dispatch**: 35+ workflows (87%)
- **Issue Triggers**: 5 workflows (12%)
- **Release Triggers**: 5 workflows (12%)

### Average Triggers per Workflow: 2.3

## Conclusion

The workflow trigger system is comprehensive but has optimization opportunities:

✅ **Strengths:**
- Comprehensive coverage
- Multiple trigger types
- Path-based filtering where implemented

⚠️ **Improvements Needed:**
- Consolidate redundant PR analyzers
- Optimize schedule frequency
- Expand path filtering
- Better workflow coordination

**Estimated Optimization Potential**: 30-50% reduction in workflow executions while maintaining full functionality.
