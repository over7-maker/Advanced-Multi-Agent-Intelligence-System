# 🚀 Automated AI Analysis Workflow Guide

## Overview

This guide shows you how to **automatically wait for and view AI analysis results** after committing fixes to PRs. This ensures you never merge PRs without reviewing AI analysis first.

---

## 🎯 Quick Start (3 Methods)

### Method 1: Command Line (Recommended)

After pushing commits to a PR:

```bash
# Auto-detect PR number from branch
python scripts/wait_for_ai_analysis.py --wait

# Or specify PR number
python scripts/wait_for_ai_analysis.py 3542 --wait
```

The script will:
- ✅ Monitor PR for AI analysis comments
- ✅ Check workflow status
- ✅ Display formatted results when ready
- ✅ Show progress updates every 30 seconds

### Method 2: VSCode/Cursor Tasks

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `Tasks: Run Task`
3. Select: **"⏳ Wait for AI Analysis"**
4. Enter PR number when prompted
5. Results appear in terminal panel

### Method 3: Quick Status Check

Just want to check if AI analysis is ready?

```bash
python scripts/check_ai_ready.py <PR_NUMBER>
```

Returns:
- Exit code `0` = ✅ AI Analysis ready
- Exit code `1` = ⏳ Not ready yet

---

## 📋 Complete Workflow

### Step 1: Make Your Changes

```bash
# Make code changes
# Test locally
# Commit
git add .
git commit -m "fix: address issue #123"
```

### Step 2: Push to PR

```bash
git push origin your-branch
```

### Step 3: Wait for AI Analysis (AUTOMATIC)

```bash
# Run the wait script (auto-detects PR number)
python scripts/wait_for_ai_analysis.py --wait
```

**What happens:**
- 🔍 Script monitors PR comments
- ⏳ Checks every 30 seconds
- 📊 Shows workflow progress
- ✅ Displays AI analysis when ready
- ⏰ Times out after 30 minutes (configurable)

**Example Output:**
```
🔍 Monitoring PR #3542 for AI Analysis...
⏱️  Will check every 30 seconds (max 30 minutes)

⏳ AI workflows running: 2 active workflows...
✅ New AI Analysis Found! (1 total)

================================================================================
🤖 BULLETPROOF REAL AI Analysis Results
================================================================================

📊 Analysis #1
👤 Author: github-actions[bot]
🕐 Created: 2024-01-15T10:30:00Z
--------------------------------------------------------------------------------
🤖 BULLETPROOF REAL AI Analysis
Status: ✅ REAL AI Verified
Provider: cerebras
Provider Attempt: 1/15

## 🔍 Analysis Results

### Critical Issues
- Line 42: Unpinned Docker image tag

### Code Quality Issues
- Line 89: Missing error handling

[... rest of analysis ...]
--------------------------------------------------------------------------------

🎯 AI Analysis Complete! Review the results above.
```

### Step 4: Review AI Analysis

The script displays:
- ✅ **Critical Issues** - Fix immediately (security, syntax errors)
- ⚠️ **Code Quality Issues** - Address before merging
- 📈 **Performance Recommendations** - Optimize if needed
- 📝 **Best Practice Violations** - Follow suggestions

### Step 5: Address Issues

```bash
# Fix issues from AI analysis
# Commit fixes
git add .
git commit -m "fix: address AI analysis recommendations"
git push

# Wait for new AI analysis
python scripts/wait_for_ai_analysis.py --wait
```

### Step 6: Merge When Ready

Only merge when:
- ✅ AI Analysis shows no critical issues
- ✅ All workflow checks pass
- ✅ You've reviewed all recommendations

---

## 🛠️ Advanced Usage

### Custom Wait Time

```bash
# Wait up to 60 minutes instead of default 30
python scripts/wait_for_ai_analysis.py 3542 --wait --max-wait 60
```

### Custom Check Interval

```bash
# Check every 60 seconds instead of default 30
python scripts/wait_for_ai_analysis.py 3542 --wait --interval 60
```

### View Current Status (No Waiting)

```bash
# Just show current AI analysis if it exists
python scripts/wait_for_ai_analysis.py 3542
```

### Integration with Git Hooks

Add to `.git/hooks/post-commit`:

**Windows (`post-commit.bat`):**
```batch
@echo off
python scripts/wait_for_ai_analysis.py --wait
```

**Linux/Mac (`post-commit`):**
```bash
#!/bin/bash
python scripts/wait_for_ai_analysis.py --wait
```

Then make it executable:
```bash
chmod +x .git/hooks/post-commit
```

---

## 🎨 VSCode/Cursor Integration

### Available Tasks

Press `Ctrl+Shift+P` → `Tasks: Run Task`:

1. **🔍 Check AI Analysis Status** - Quick check if ready
2. **⏳ Wait for AI Analysis** - Monitor and show results
3. **📊 View AI Analysis Results** - Show existing analysis
4. **🚀 Post-Commit: Wait for AI Analysis** - Auto-run after commits

### Keyboard Shortcuts

Add to `keybindings.json`:

```json
{
  "key": "ctrl+shift+a",
  "command": "workbench.action.tasks.runTask",
  "args": "⏳ Wait for AI Analysis"
}
```

---

## 🔍 How It Works

### Auto-Detection

The script tries to detect PR number from:
1. **Branch name**: `pr-3542`, `feature/pr-3542`, etc.
2. **Commit message**: `fix: issue #3542`
3. **Git remote**: If branch is linked to PR

### Monitoring Logic

1. **Fetches PR comments** every 30 seconds
2. **Checks for** "BULLETPROOF REAL AI Analysis" comments
3. **Monitors workflows** to see if analysis is running
4. **Displays results** when AI analysis appears
5. **Stops monitoring** when analysis is complete or timeout reached

### Exit Codes

- `0` = Success (AI analysis found and displayed)
- `1` = Error (PR not found, GitHub CLI not installed, etc.)
- `130` = Interrupted (Ctrl+C pressed)

---

## ⚠️ Troubleshooting

### "Could not auto-detect PR number"

**Solution:**
```bash
# Specify PR number manually
python scripts/wait_for_ai_analysis.py 3542 --wait
```

### "GitHub CLI (gh) not found"

**Solution:**
```bash
# Windows
winget install --id GitHub.cli

# Linux/Mac
# Follow: https://cli.github.com/manual/installation
```

### "No AI Analysis comments found yet"

**This is normal!** The script will keep monitoring. Wait for:
- Workflows to complete (usually 2-5 minutes)
- AI analysis to be posted as PR comment

### Script Times Out

**Solution:**
- Increase timeout: `--max-wait 60` (60 minutes)
- Check workflow status manually: `gh run list`
- View PR in browser: `gh pr view 3542 --web`

---

## 📊 Example Workflow Timeline

```
10:00:00 - Commit and push fixes
10:00:05 - Run: python scripts/wait_for_ai_analysis.py --wait
10:00:10 - Script detects PR #3542
10:00:15 - No AI analysis yet, monitoring...
10:00:45 - AI workflows running: 2 active...
10:01:15 - AI workflows running: 1 active...
10:02:30 - ✅ AI Analysis found! Displaying results...
10:02:35 - Review analysis, see critical issue on line 42
10:05:00 - Fix issue, commit, push
10:05:05 - Run: python scripts/wait_for_ai_analysis.py --wait
10:07:20 - ✅ New AI Analysis found! No critical issues!
10:07:25 - Merge PR ✅
```

---

## 🎯 Best Practices

1. **Always wait** for AI analysis after every commit
2. **Fix critical issues** before merging
3. **Review all recommendations** even if not critical
4. **Use VSCode tasks** for easy access
5. **Set up git hooks** for automatic monitoring
6. **Don't merge** until AI analysis shows no critical issues

---

## 📚 Related Scripts

- `scripts/view_pr_comments.py` - View all PR comments
- `scripts/check_pr_workflows.py` - Check workflow status
- `scripts/check_ai_ready.py` - Quick status check
- `scripts/wait_for_ai_analysis.py` - **Main monitoring script**

---

## 🆘 Need Help?

- Check: `CURSOR_GITHUB_COMPLETE_GUIDE.md`
- View example: `VIEW_PR_235_EXAMPLE.md`
- Quick start: `QUICK_START_CURSOR_GITHUB.md`














