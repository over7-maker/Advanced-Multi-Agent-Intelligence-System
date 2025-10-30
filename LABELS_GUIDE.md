# GitHub Labels Guide for AMAS Project

## 🎯 **Automation Labels** (Trigger Actions)

### `auto-format`
- **Purpose**: Triggers automatic Black/isort code formatting
- **When to use**: When CI fails on code formatting issues
- **Action**: Runs `auto-format-and-commit.yml` workflow
- **How**: Add label → Workflow formats code → Commits changes automatically

### `auto-deploy` (if you add it)
- **Purpose**: Triggers automatic deployment after tests pass
- **When to use**: For hotfixes that need immediate deployment

---

## 🏷️ **Priority Labels**

### `priority:critical`
- Production issues, security vulnerabilities
- Requires immediate attention

### `priority:high`
- Important features, major bugs
- Should be addressed soon

### `priority:medium`
- Normal priority items
- Default priority level

### `priority:low`
- Nice-to-have features, minor improvements
- Can wait for next sprint

---

## 📋 **Type Labels**

### `type:bug`
- Something is broken
- Needs investigation and fix

### `type:feature`
- New functionality
- Adds new capabilities

### `type:refactor`
- Code improvements without changing behavior
- Maintainability improvements

### `type:documentation`
- README, docs, comments updates
- No code changes needed

### `type:chore`
- Dependencies, CI/CD, tooling updates
- Maintenance work

### `type:security`
- Security fixes, vulnerability patches
- High priority review

---

## 🔍 **Status Labels**

### `status:needs-review`
- Code is ready for review
- Waiting for approval

### `status:in-progress`
- Actively being worked on
- Don't duplicate effort

### `status:blocked`
- Waiting on external dependency
- Cannot proceed currently

### `status:needs-qa`
- Ready for testing
- Needs QA verification

### `status:ready-to-merge`
- All checks pass
- Approved and ready

### `status:wip`
- Work in progress
- Not ready for review

---

## 🏗️ **Component Labels**

### `area:backend`
- Server-side code, APIs
- Python services, databases

### `area:frontend`
- UI, web interfaces
- User-facing components

### `area:ci-cd`
- GitHub Actions, pipelines
- Deployment automation

### `area:security`
- Security features, scans
- Authentication, authorization

### `area:ai-agents`
- AI agent functionality
- Agent orchestration, routing

### `area:infrastructure`
- Docker, Kubernetes, Helm
- Deployment infrastructure

---

## 📊 **Size Labels** (Optional)

### `size:xs` (1–10 lines)
- Tiny changes
- Quick fixes

### `size:s` (10–50 lines)
- Small changes
- Minor features

### `size:m` (50–200 lines)
- Medium changes
- Typical PR size

### `size:l` (200–500 lines)
- Large changes
- May need extra review

### `size:xl` (500+ lines)
- Very large changes
- Consider breaking into smaller PRs

---

## 🔧 **Special Labels**

### `breaking-change`
- Changes that break compatibility
- Requires migration guide

### `good-first-issue`
- Good for new contributors
- Well-documented, smaller scope

### `help-wanted`
- Community can help
- Welcomes external contributions

---

## 💡 **How to Use Labels**

### **Adding Labels**
1. Go to PR or Issue
2. Click "Labels" on the right sidebar
3. Select or create labels
4. Multiple labels can be added

### **Label Combinations Examples**
- `type:bug` + `priority:high` + `area:security` = Critical security bug
- `type:feature` + `area:backend` + `status:needs-review` = Backend feature ready for review
- `auto-format` + `type:chore` = Formatting fix

### **Searching with Labels**
```
label:bug label:priority:high
label:area:backend is:open
label:auto-format
```

### **Automating with Labels**
- Workflows can check for specific labels
- Auto-assign reviewers based on labels
- Auto-close issues when merged
- Move cards in project boards

---

## 🎨 **Label Colors** (Suggested)

- 🔴 Red: Priority critical/high, bugs
- 🟠 Orange: Features, in-progress
- 🟡 Yellow: Needs attention, blocked
- 🟢 Green: Ready, approved
- 🔵 Blue: Documentation, info
- 🟣 Purple: Security, special
- ⚫ Gray: Low priority, chore

---

## ✅ **Quick Reference: `auto-format` Label**

1. **When CI fails** with "37 files would be reformatted"
2. **Add `auto-format` label** to the PR
3. **Workflow runs automatically** → Formats code → Commits changes
4. **Remove label** if you want to prevent auto-formatting again
5. **Re-run CI** → Should pass now!

---

*Last updated: 2025-10-30*
