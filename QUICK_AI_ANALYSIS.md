# ⚡ Quick AI Analysis Reference

## 🚀 After Committing Fixes

**One Command:**
```bash
python scripts/wait_for_ai_analysis.py --wait
```

That's it! The script will:
- ✅ Auto-detect PR number
- ✅ Monitor for AI analysis
- ✅ Display results when ready
- ✅ Never merge until you see results

## 🎯 Three Ways to Use

### 1. Command Line (Auto-detect PR)
```bash
python scripts/wait_for_ai_analysis.py --wait
```

### 2. Command Line (Specify PR)
```bash
python scripts/wait_for_ai_analysis.py 3542 --wait
```

### 3. VSCode/Cursor Task
- Press `Ctrl+Shift+P`
- Type: `Tasks: Run Task`
- Select: `⏳ Wait for AI Analysis`

## ✅ Quick Status Check

```bash
python scripts/check_ai_ready.py <PR_NUMBER>
```

Returns:
- `0` = ✅ Ready
- `1` = ⏳ Not ready

## 📋 Complete Workflow

1. **Commit fixes** → `git commit -m "fix: ..."`
2. **Push** → `git push`
3. **Wait for AI** → `python scripts/wait_for_ai_analysis.py --wait`
4. **Review results** → Fix issues if needed
5. **Repeat** → Until no critical issues
6. **Merge** → Only when AI analysis is clean

## 🎨 What You'll See

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
[... AI Analysis Results ...]
--------------------------------------------------------------------------------

🎯 AI Analysis Complete! Review the results above.
```

## ⚠️ Remember

- **NEVER merge** until AI analysis is complete
- **Always wait** after every commit
- **Fix critical issues** first
- **Review all recommendations**

## 🆘 Need More Details?

See: `AUTOMATED_AI_ANALYSIS_WORKFLOW.md`














