# Migration Runbook

**Date**: December 21, 2025  
**Purpose**: Step-by-step guide for migrating from 46 workflows to 8 cores

## Pre-Migration Checklist

- [ ] Backup all existing workflows
- [ ] Document current workflow dependencies
- [ ] Identify all workflow triggers
- [ ] List all secrets and environment variables
- [ ] Document all artifact outputs
- [ ] Test all core workflows individually

## Migration Steps

### Phase 1: Preparation (Day 1)

1. **Create Backup Branch**
   ```bash
   git checkout -b workflow-backup-$(date +%Y%m%d)
   git push origin workflow-backup-$(date +%Y%m%d)
   ```

2. **Document Current State**
   - List all 46 workflows
   - Document their triggers
   - Document their dependencies
   - Document their outputs

3. **Create Mapping Document**
   - Map each workflow to its core
   - Document functionality preservation
   - Note any breaking changes

### Phase 2: Implementation (Day 2)

1. **Create Core Workflows**
   - Create all 8 core workflow files
   - Implement all functionality
   - Add comprehensive error handling

2. **Create Test Suite**
   - Write unit tests (42 tests)
   - Write integration tests (50 tests)
   - Write validation tests (35 tests)
   - Write performance tests (24 tests)

3. **Create Documentation**
   - Consolidation guide
   - Technical specifications
   - Migration runbook
   - Troubleshooting guide

### Phase 3: Testing (Day 3)

1. **Run Test Suite**
   ```bash
   pytest tests/unit/ -v
   pytest tests/integration/ -v
   pytest tests/validation/ -v
   pytest tests/performance/ -v
   ```

2. **Verify Functionality**
   - Test each core workflow manually
   - Verify all functionality preserved
   - Check data integrity (0% loss)

3. **Performance Validation**
   - Measure execution times
   - Verify 60% improvement
   - Check resource usage

### Phase 4: Deployment (Day 4)

1. **Disable Legacy Workflows**
   ```bash
   # Rename legacy workflows
   for file in .github/workflows/*.yml; do
     if [[ ! "$file" =~ core- ]]; then
       mv "$file" "${file}.disabled"
     fi
   done
   ```

2. **Enable Core Workflows**
   - All core workflows are already active
   - Verify they trigger correctly
   - Monitor initial runs

3. **Monitor for 1 Week**
   - Check all workflow runs
   - Verify no functionality loss
   - Address any issues

### Phase 5: Cleanup (Day 5+)

1. **Archive Legacy Workflows**
   ```bash
   mkdir -p .github/workflows/legacy
   mv .github/workflows/*.disabled .github/workflows/legacy/
   ```

2. **Update Documentation**
   - Update README files
   - Update workflow index
   - Archive old documentation

3. **Final Verification**
   - Verify all 8 cores working
   - Verify 0% data loss
   - Verify performance improvements

## Rollback Procedure

If issues are detected:

1. **Immediate Rollback**
   ```bash
   git checkout workflow-backup-$(date +%Y%m%d)
   git push origin main --force
   ```

2. **Restore Legacy Workflows**
   ```bash
   mv .github/workflows/legacy/*.disabled .github/workflows/
   # Remove .disabled extension
   for file in .github/workflows/*.disabled; do
     mv "$file" "${file%.disabled}"
   done
   ```

3. **Disable Core Workflows**
   ```bash
   for file in .github/workflows/core-*.yml; do
     mv "$file" "${file}.disabled"
   done
   ```

## Verification Checklist

- [ ] All 8 core workflows exist
- [ ] All core workflows are functional
- [ ] All tests passing (>95%)
- [ ] Data integrity verified (0% loss)
- [ ] Performance improved (60%)
- [ ] Size reduced (21%)
- [ ] Documentation complete
- [ ] Legacy workflows archived
- [ ] No breaking changes
- [ ] All secrets preserved

## Common Issues

### Issue: Workflow Not Triggering
**Solution**: Check trigger definitions and paths

### Issue: Job Failing
**Solution**: Check error logs, verify dependencies

### Issue: Artifacts Not Uploading
**Solution**: Check artifact paths and retention settings

### Issue: Performance Not Improved
**Solution**: Check job parallelization and dependencies

## Support

For issues or questions:
1. Check troubleshooting guide
2. Review workflow logs
3. Check GitHub Actions documentation
4. Contact team lead

