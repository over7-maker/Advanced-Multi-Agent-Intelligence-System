# Follow-up PRs After PR 235

## ✅ Completed: PR #1 - Lockfiles & CI Improvements

**Branch**: `followup/lockfiles-and-ci-improvements`  
**Status**: Pushed, ready for PR creation

**Changes**:
- ✅ Lockfile support (`requirements-security-lock.in`)
- ✅ Automated lockfile generation workflow
- ✅ Actionlint in main CI (non-blocking)
- ✅ Modern Semgrep usage (replaced deprecated action)
- ✅ Enhanced SBOM with release attachments

**Create PR**: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/new/followup/lockfiles-and-ci-improvements

---

## 🔄 Remaining Follow-up PRs

### PR #2: Pickle Replacement (Data Serialization)

**Files to Fix**:
1. `src/amas/agents/adaptive_personality.py` - Personality data
2. `src/amas/intelligence/collective_learning.py` - Knowledge base
3. `src/amas/services/reinforcement_learning_optimizer.py` - Training data

**Note**: `ml_service.py` uses pickle for scikit-learn models (legitimate use case). Verify if this needs replacement.

**Approach**:
```python
# Replace pickle.dump/load with JSON
import json

# Before: pickle.dump(data, f)
json.dump(data, f, indent=2)

# Before: pickle.load(f)
data = json.load(f)
```

**Branch**: `followup/replace-pickle-with-json`

---

### PR #3: Auto-Format Workflow Cleanup

**File**: `.github/workflows/auto-format-and-commit.yml`

**Issues**:
- [ ] Verify same-repo scope (already has check)
- [ ] Remove any deprecated inputs
- [ ] Ensure modern semgrep usage if Semgrep runs here

**Status**: Workflow looks good, just needs verification

---

### PR #4: Environment Protection Configuration

**Files**: `.github/workflows/production-cicd-secure.yml` and deployment workflows

**Changes Needed**:
```yaml
jobs:
  deploy:
    environment:
      name: production
      # Requires GitHub environment protection rules
```

**Steps**:
1. Configure GitHub environment protection rules in repo settings
2. Add `environment: production` to deploy jobs
3. Reference required reviewers

**Branch**: `followup/environment-protection`

---

### PR #5: SBOM Provenance/SLSA (Optional)

**Status**: Can be deferred or planned as immediate follow-up

**Components**:
- SLSA attestations for builds
- Provenance metadata
- Signed artifacts

**Tools**: `slsa-github-generator` or `gh attestation`

---

## 📋 PR Checklist Generator

To generate the remaining PRs, say **"generate PR checklist"** and I'll create:
- Commit-ready code changes
- PR descriptions
- Branch names
- Implementation steps

---

## 🎯 Acceptance Checklist Status

### PR 235 Pre-Merge Items

- [x] **CI Green**: Security scan passes (assumed)
- [ ] **Workflow Hygiene**: Actionlint ✅ (PR #1), Environment protection ❌ (PR #4)
- [ ] **Supply Chain**: SBOM ✅ (PR #1), Provenance ⏸️ (PR #5 - optional)
- [ ] **Code Security**: Pickle replacement ❌ (PR #2)

### Recommendation

1. ✅ **Merge PR 235** (strong consolidation)
2. ✅ **Merge PR #1** (lockfiles & CI improvements)
3. 🔄 **Merge PR #2** (pickle replacement)
4. 🔄 **Merge PR #4** (environment protection)
5. ⏸️ **Plan PR #5** (SLSA/provenance - can wait)

---

## Quick Commands

```bash
# Check pickle usage
grep -r "pickle\." src/ --include="*.py"

# Generate lockfiles
make lock-deps

# Validate workflows
actionlint .github/workflows/*.yml

# Check SBOM
syft packages dir:. -o cyclonedx-json
```
