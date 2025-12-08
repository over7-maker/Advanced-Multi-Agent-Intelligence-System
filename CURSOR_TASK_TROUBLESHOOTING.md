# 🔧 Cursor AI Integration - Troubleshooting Guide

## Issue: Ctrl+Shift+A Not Working

If pressing `Ctrl+Shift+A` doesn't trigger the AI analysis, try these solutions:

### Solution 1: Use Command Palette (Most Reliable)

1. **Press `Ctrl+Shift+P`** (or `Cmd+Shift+P` on Mac)
2. Type: **"Tasks: Run Task"**
3. Select: **"🤖 AI Analysis: Current File"**

This is the most reliable way to run the task.

### Solution 2: Check Keybinding

The keybinding might be conflicting with another extension. To check:

1. **Press `Ctrl+Shift+P`**
2. Type: **"Preferences: Open Keyboard Shortcuts"**
3. Search for: **"ctrl+shift+a"**
4. Check if there are conflicts

### Solution 3: Reload Cursor/VS Code

Sometimes the keybindings need a reload:

1. **Press `Ctrl+Shift+P`**
2. Type: **"Developer: Reload Window"**
3. Try `Ctrl+Shift+A` again

### Solution 4: Run Task Manually

1. **Press `Ctrl+Shift+P`**
2. Type: **"Tasks: Run Task"**
3. Select: **"🤖 AI Analysis: Current File"**

### Solution 5: Check if File is Python

The keybinding only works when:
- A Python file is open (`.py` extension)
- The editor has focus

Make sure you have a `.py` file open and the editor is focused.

### Solution 6: Test Task Directly

Run the task from terminal to verify it works:

```bash
cd /workspaces/Advanced-Multi-Agent-Intelligence-System
python3 .github/scripts/cursor_ai_diagnostics.py src/amas/agents/adaptive_personality.py
```

If this works, the issue is with the keybinding/task configuration.

### Solution 7: Alternative Keybinding

If `Ctrl+Shift+A` doesn't work, you can:

1. **Press `Ctrl+Shift+P`**
2. Type: **"Preferences: Open Keyboard Shortcuts (JSON)"**
3. Add a custom keybinding:

```json
{
  "key": "ctrl+alt+a",
  "command": "workbench.action.tasks.runTask",
  "args": "🤖 AI Analysis: Current File",
  "when": "editorTextFocus && editorLangId == 'python'"
}
```

### Solution 8: Check Task Configuration

Verify the task exists:

1. **Press `Ctrl+Shift+P`**
2. Type: **"Tasks: Run Task"**
3. Look for: **"🤖 AI Analysis: Current File"**

If it's not there, the `.vscode/tasks.json` file might not be loaded.

### Solution 9: Verify Script Works

Test the script directly:

```bash
# Test with a Python file
python3 .github/scripts/cursor_ai_diagnostics.py <path-to-python-file>
```

You should see output like:
```
🤖 Analyzing filename.py...
✅ Using provider: nvidia
📊 Found X issue(s)

filepath:line:col: severity: message
```

### Solution 10: Check Output Panel

After running the task (via Command Palette), check:

1. **View → Output** (or `Ctrl+Shift+U`)
2. Select: **"Tasks"** from the dropdown
3. Look for any error messages

### Solution 11: Check Problems Panel

After running the task, check:

1. **View → Problems** (or `Ctrl+Shift+M`)
2. Look for diagnostics from "bulletproof-ai"

---

## Quick Test Checklist

- [ ] Python file is open (`.py` extension)
- [ ] Editor has focus (click in the editor)
- [ ] Task exists in "Tasks: Run Task" menu
- [ ] Script runs from terminal
- [ ] No keybinding conflicts
- [ ] Cursor/VS Code reloaded after setup

---

## Alternative: Use Terminal Directly

If keybindings don't work, you can always run analysis from terminal:

```bash
# Analyze current file (replace with your file path)
python3 .github/scripts/cursor_ai_diagnostics.py src/amas/agents/adaptive_personality.py

# Or create an alias
alias ai-analyze='python3 .github/scripts/cursor_ai_diagnostics.py'
ai-analyze <file-path>
```

---

## Still Not Working?

If none of these solutions work:

1. **Check the terminal output** when running the task
2. **Check the Problems panel** for any errors
3. **Verify the script path** is correct
4. **Check file permissions**: `chmod +x .github/scripts/cursor_ai_diagnostics.py`

---

## Expected Behavior

When working correctly:

1. **Press `Ctrl+Shift+A`** (or use Command Palette)
2. **Terminal panel opens** showing "🤖 Analyzing..."
3. **Analysis runs** (takes 2-5 seconds)
4. **Results appear** in Problems panel
5. **Diagnostics show** with line numbers and fix recommendations

---

## Need Help?

If you're still having issues, check:
- `.vscode/tasks.json` exists and is valid JSON
- `.vscode/keybindings.json` exists and is valid JSON
- Script is executable: `chmod +x .github/scripts/cursor_ai_diagnostics.py`
- Python 3 is available: `python3 --version`

