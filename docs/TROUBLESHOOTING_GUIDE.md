# Troubleshooting Guide

**Date**: December 21, 2025  
**Purpose**: Common issues and solutions for core workflows

## Common Issues

### Issue 1: Workflow Not Triggering

**Symptoms**:
- Workflow doesn't run on expected events
- Manual dispatch doesn't work

**Solutions**:
1. Check trigger definitions in workflow file
2. Verify path filters are correct
3. Check branch names match
4. Verify workflow_dispatch inputs

**Example Fix**:
```yaml
on:
  push:
    branches: [main, develop]  # Verify branches match
  workflow_dispatch:  # Ensure this is present
```

### Issue 2: Job Failing Immediately

**Symptoms**:
- Job fails within seconds
- No meaningful error message

**Solutions**:
1. Check job conditions (`if` statements)
2. Verify dependencies are met
3. Check for syntax errors
4. Verify secrets are available

**Example Fix**:
```yaml
jobs:
  my_job:
    if: env.MODE == 'comprehensive'  # Check condition
    needs: [other_job]  # Verify dependency exists
```

### Issue 3: Python Dependencies Not Installing

**Symptoms**:
- `pip install` fails
- Package version not found

**Solutions**:
1. Use compatible package versions
2. Add fallback installation
3. Use `--prefer-binary` flag
4. Check Python version compatibility

**Example Fix**:
```bash
pip install --prefer-binary package==version || pip install package
```

### Issue 4: Artifacts Not Uploading

**Symptoms**:
- Artifacts step succeeds but no files
- Artifacts not found in GitHub UI

**Solutions**:
1. Check file paths are correct
2. Use `if-no-files-found: ignore`
3. Verify files exist before upload
4. Check artifact retention settings

**Example Fix**:
```yaml
- uses: actions/upload-artifact@v4
  with:
    path: results.json
    if-no-files-found: ignore
```

### Issue 5: Timeout Errors

**Symptoms**:
- Jobs timing out
- Workflow taking too long

**Solutions**:
1. Increase timeout-minutes
2. Optimize job execution
3. Split large jobs
4. Use parallel execution

**Example Fix**:
```yaml
jobs:
  my_job:
    timeout-minutes: 60  # Increase timeout
```

### Issue 6: Secret Not Available

**Symptoms**:
- API key errors
- Authentication failures

**Solutions**:
1. Verify secret exists in repository
2. Check secret name matches
3. Use `secrets: inherit` for reusable workflows
4. Verify permissions

**Example Fix**:
```yaml
jobs:
  my_job:
    uses: ./.github/workflows/orchestrator.yml
    secrets: inherit  # Inherit all secrets
```

### Issue 7: Conditional Logic Not Working

**Symptoms**:
- Jobs running when they shouldn't
- Jobs not running when they should

**Solutions**:
1. Check condition syntax
2. Verify environment variables
3. Use proper comparison operators
4. Check job dependencies

**Example Fix**:
```yaml
jobs:
  my_job:
    if: env.MODE == 'comprehensive' || env.MODE == 'all'
```

### Issue 8: Integration Failures

**Symptoms**:
- Orchestrator not working
- Agent coordination failing

**Solutions**:
1. Verify orchestrator workflow exists
2. Check agent scripts are present
3. Verify API keys are available
4. Check error logs

**Example Fix**:
```yaml
jobs:
  ai_task:
    uses: ./.github/workflows/00-zero-failure-ai-orchestrator.yml
    continue-on-error: true  # Don't fail workflow
```

## Performance Issues

### Slow Execution
1. Enable job parallelization
2. Use caching where possible
3. Optimize job dependencies
4. Reduce unnecessary steps

### High Resource Usage
1. Optimize dependency installation
2. Use binary wheels
3. Reduce artifact sizes
4. Clean up temporary files

## Debugging Tips

1. **Enable Debug Logging**
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
     ACTIONS_RUNNER_DEBUG: true
   ```

2. **Check Workflow Logs**
   - View detailed logs in GitHub Actions
   - Check each step's output
   - Review error messages

3. **Test Locally**
   - Use `act` to test workflows locally
   - Verify scripts work independently
   - Check Python/Node versions

4. **Use Artifacts**
   - Upload debug information
   - Save intermediate results
   - Export logs

## Getting Help

1. Check this troubleshooting guide
2. Review workflow logs
3. Check GitHub Actions documentation
4. Contact team lead
5. Create issue with details

