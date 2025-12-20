# Agent-Workflow Integration Guide

## Overview

This document describes how the 7 autonomous agents integrate with the 8 core workflows in the AMAS system.

**Part of PR #274: AI Autonomy Initiative**

## Architecture

```
8 Core Workflows
    ↓
AI Autonomy Orchestrator
    ↓
7 Autonomous Agents
    ↓
Zero-Failure AI Orchestrator (16 providers)
```

## Core Workflows

The 8 core workflows that integrate with agents:

1. **01-ai-agentic-project-self-improver.yml** - Project self-improvement
2. **02-ai-agentic-issue-auto-responder.yml** - Issue management
3. **03-ai-agent-project-audit-documentation.yml** - Project audit
4. **04-ai-enhanced-build-deploy.yml** - Build and deployment
5. **05-ai-security-threat-intelligence.yml** - Security monitoring
6. **06-ai-code-quality-performance.yml** - Code quality
7. **07-ai-enhanced-cicd-pipeline.yml** - CI/CD pipeline
8. **bulletproof-ai-pr-analysis.yml** - PR analysis

## Agent Integration Points

### Agent-1: Workflow Orchestrator
**Integration**: All 8 core workflows

**Purpose**: Intelligent routing and scheduling

**Usage**:
```yaml
jobs:
  workflow-routing:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: workflow_orchestrator
      context: |
        {
          "task_type": "code_review",
          "task_data": {...}
        }
```

### Agent-2: Data Validator
**Integration**: 
- Core-1 (Project Self-Improver)
- Core-3 (Project Audit)
- Core-5 (Code Quality)

**Purpose**: Data quality monitoring

**Usage**:
```yaml
jobs:
  data-validation:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: data_validator
      context: |
        {
          "data": {...},
          "validation_type": "comprehensive"
        }
```

### Agent-3: Performance Optimizer
**Integration**:
- Core-2 (Issue Responder)
- Core-4 (Build Deploy)
- Core-7 (CI/CD Pipeline)

**Purpose**: Real-time performance tuning

**Usage**:
```yaml
jobs:
  performance-optimization:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: performance_optimizer
      context: |
        {
          "metrics": {...},
          "target": "execution_time"
        }
```

### Agent-4: Security Monitor
**Integration**:
- Core-6 (Security Threat Intelligence)
- All authentication points

**Purpose**: Continuous security scanning

**Usage**:
```yaml
jobs:
  security-monitoring:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: security_monitor
      context: |
        {
          "target": "codebase",
          "scan_type": "comprehensive"
        }
```

### Agent-5: Cost Optimizer
**Integration**: All 8 core workflows, cloud resources

**Purpose**: Intelligent cost minimization

**Usage**:
```yaml
jobs:
  cost-optimization:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: cost_optimizer
      context: |
        {
          "costs": {...},
          "budget_limit": 0.20
        }
```

### Agent-6: Analytics Aggregator
**Integration**:
- Core-5 (Code Quality)
- Core-8 (PR Analysis)
- Dashboard

**Purpose**: Unified metrics & reporting

**Usage**:
```yaml
jobs:
  analytics:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: analytics_aggregator
      context: |
        {
          "time_range": "24h",
          "metrics_types": ["performance", "cost", "security"]
        }
```

### Agent-7: Rollback Guardian
**Integration**: All 8 core workflows, backup system

**Purpose**: Automated rollback decision-making

**Usage**:
```yaml
jobs:
  rollback-guardian:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: rollback_guardian
      context: |
        {
          "deployment_status": {...},
          "metrics": {...}
        }
```

## Integration Patterns

### Pattern 1: Pre-Execution Agent Check

```yaml
jobs:
  pre-check:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: data_validator
      context: |
        {
          "data": {...},
          "validation_type": "pre_execution"
        }
  
  main-workflow:
    needs: [pre-check]
    if: needs.pre-check.outputs.success == 'true'
    # ... workflow steps
```

### Pattern 2: Post-Execution Agent Analysis

```yaml
jobs:
  main-workflow:
    # ... workflow steps
  
  post-analysis:
    needs: [main-workflow]
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: analytics_aggregator
      context: |
        {
          "workflow_results": {...},
          "time_range": "1h"
        }
```

### Pattern 3: Continuous Monitoring

```yaml
jobs:
  monitoring:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: all
      context: |
        {
          "monitoring_mode": "continuous",
          "interval": "5m"
        }
```

## Migration Guide

### Step 1: Identify AI Calls

Find all direct AI provider calls in your workflow:
- Python scripts calling AI APIs directly
- Environment variables with API keys
- Direct API calls in workflow steps

### Step 2: Replace with Orchestrator

Replace direct calls with orchestrator workflow_call:

**Before**:
```yaml
- name: Run AI Analysis
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    python analyze.py
```

**After**:
```yaml
jobs:
  ai-analysis:
    uses: ./.github/workflows/00-zero-failure-ai-orchestrator.yml
    with:
      task_type: pr_analysis
      system_message: "..."
      user_prompt: "..."
    secrets: inherit

  process-results:
    needs: [ai-analysis]
    if: needs.ai-analysis.outputs.success == 'true'
    run: |
      echo "${{ needs.ai-analysis.outputs.response }}" > results.txt
```

### Step 3: Add Agent Integration

Add agent calls where appropriate:

```yaml
jobs:
  agent-check:
    uses: ./.github/workflows/ai-autonomy-orchestrator.yml
    with:
      agent: security_monitor
      context: |
        {
          "target": "codebase",
          "scan_type": "pre_deployment"
        }
  
  deployment:
    needs: [agent-check]
    if: needs.agent-check.outputs.success == 'true'
    # ... deployment steps
```

## Success Metrics

### Agent-1: Workflow Orchestrator
- **Target**: 15% additional performance gain
- **Measurement**: Compare workflow execution times before/after

### Agent-2: Data Validator
- **Target**: <0.1% data anomalies
- **Measurement**: Track validation failure rate

### Agent-3: Performance Optimizer
- **Target**: 18 min → 15 min (25% faster)
- **Measurement**: Average workflow execution time

### Agent-4: Security Monitor
- **Target**: 99.99% uptime, zero breaches
- **Measurement**: Security incident tracking

### Agent-5: Cost Optimizer
- **Target**: $0.24/run → $0.18/run (25% cheaper)
- **Measurement**: Cost per workflow run

### Agent-6: Analytics Aggregator
- **Target**: 100% metrics coverage
- **Measurement**: Percentage of workflows with metrics

### Agent-7: Rollback Guardian
- **Target**: RTO <2 minutes
- **Measurement**: Rollback time from detection to completion

## Troubleshooting

### Agent Not Responding

1. Check agent logs: `.github/data/agent_results/latest.json`
2. Verify orchestrator health: Check `ai-health-monitor.yml` results
3. Review agent metrics: `.github/data/agent_metrics/*.json`

### Workflow Integration Issues

1. Verify workflow_call syntax
2. Check secrets inheritance
3. Review output format compatibility

### Performance Degradation

1. Check agent overhead: Review metrics
2. Optimize agent execution frequency
3. Consider caching agent results

## Examples

See:
- `.github/workflows/bulletproof-ai-pr-analysis.yml` - PR analysis with orchestrator
- `.github/workflows/ai-autonomy-orchestrator.yml` - Agent coordination
- `tests/integration/test_workflow_integration.py` - Integration tests

## References

- [Zero-Failure AI Orchestrator Documentation](ZERO_FAILURE_AI_ORCHESTRATOR.md)
- [AI Autonomy Agents Documentation](AI_AUTONOMY_AGENTS.md)

