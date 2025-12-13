# 🤖 Bulletproof AI Integration for Cursor IDE

Complete integration of the **Bulletproof Real AI Analysis** system into Cursor IDE, providing the same high-quality AI analysis you see in GitHub PRs, directly in your local development environment.

## 🎯 Features

- ✅ **Real-time Diagnostics**: AI analysis appears in VS Code Problems panel
- ✅ **Auto-analysis on Save**: Watch mode automatically analyzes files as you edit
- ✅ **Same AI System**: Uses your existing 15-provider bulletproof AI router
- ✅ **Pre-commit Hooks**: Automatic analysis before commits
- ✅ **Keyboard Shortcuts**: Quick access to AI analysis
- ✅ **JSON Reports**: Detailed analysis reports for programmatic use

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install watchdog aiohttp
```

### 2. Verify Setup

```bash
# Test the AI diagnostics script
python3 .github/scripts/cursor_ai_diagnostics.py src/amas/core/orchestrator.py
```

### 3. Start Using

**Option A: Manual Analysis (Recommended for first-time use)**
- Open any Python file
- Press `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac)
- View results in Problems panel (`Ctrl+Shift+M`)

**Option B: Auto-analysis (Watch Mode)**
- Press `Ctrl+Shift+Alt+A` to start watch mode
- Edit Python files - they'll be analyzed automatically on save
- Results appear in Problems panel in real-time

## 📋 Usage Guide

### Manual Analysis

1. **Analyze Current File**:
   - Open a Python file
   - Press `Ctrl+Shift+A`
   - Results appear in Problems panel

2. **View JSON Report**:
   - After analysis, press `Ctrl+Shift+R`
   - See detailed JSON report with all diagnostics

3. **Command Palette**:
   - `Ctrl+Shift+P` → "Tasks: Run Task"
   - Select "🤖 AI Analysis: Current File"

### Watch Mode (Background Analysis)

1. **Start Watch Mode**:
   - Press `Ctrl+Shift+Alt+A`
   - Or: `Ctrl+Shift+P` → "Tasks: Run Task" → "🔄 AI Analysis: Watch Mode"

2. **Automatic Analysis**:
   - Edit any Python file in `src/`
   - Save the file
   - Analysis runs automatically
   - Results appear in Problems panel

3. **Stop Watch Mode**:
   - Close the terminal panel running watch mode
   - Or press `Ctrl+C` in the terminal

### Pre-commit Hook

The pre-commit hook automatically analyzes staged Python files before commit:

```bash
# Normal commit (runs AI analysis)
git commit -m "Your message"

# Skip analysis (not recommended)
git commit --no-verify -m "Your message"
```

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+A` | Analyze current Python file |
| `Ctrl+Shift+Alt+A` | Start/stop watch mode |
| `Ctrl+Shift+J` | Analyze current file (JSON output) |
| `Ctrl+Shift+R` | View JSON report for current file |
| `Ctrl+Shift+M` | Open Problems panel |

## 📊 Understanding Results

### Severity Levels

- 🔴 **Error (Critical/High)**: Must fix before committing
  - Syntax errors
  - Security vulnerabilities
  - Critical bugs

- 🟡 **Warning (Medium)**: Should fix
  - Code quality issues
  - Performance concerns
  - Best practice violations

- 🔵 **Info (Low)**: Nice to fix
  - Style suggestions
  - Documentation improvements

### Diagnostic Format

Each diagnostic includes:
- **Line & Column**: Exact location
- **Message**: Clear description
- **Recommendation**: Specific fix (when available)
- **Category**: Type of issue (syntax, security, performance, etc.)

### Example Output

```
src/amas/integration/ecosystem_manager.py:73:1: error: ANTHROPIC enum member incomplete - missing value assignment
💡 Fix: Add: ANTHROPIC = 'anthropic'
```

## 🔧 Configuration

### VS Code Settings

Settings are configured in `.vscode/settings.json`:

- **Auto-save**: Enabled with 1 second delay
- **Problem Matcher**: Configured for Bulletproof AI diagnostics
- **Python**: Ruff formatter, type checking enabled

### Customization

**Change Cache Timeout**:
Edit `.github/scripts/cursor_ai_diagnostics.py`:
```python
self.cache_timeout = 300  # Change to desired seconds
```

**Change Watch Cooldown**:
Edit `.github/scripts/ai_watch_daemon.py`:
```python
self.cooldown_seconds = 3  # Change to desired seconds
```

**Modify Analysis Types**:
Edit the `analyze_code` call in `cursor_ai_diagnostics.py`:
```python
analysis_types = ["code_quality", "security", "performance", "best_practices"]
```

## 🐛 Troubleshooting

### "Could not import enhanced_router_v2"

**Solution**: Make sure you're in the project root and `src/amas/ai/enhanced_router_v2.py` exists.

```bash
cd /workspaces/Advanced-Multi-Agent-Intelligence-System
python3 -c "from amas.ai.enhanced_router_v2 import generate_with_fallback; print('OK')"
```

### "watchdog not installed"

**Solution**: Install watchdog:
```bash
pip install watchdog
```

### "No API keys configured"

**Solution**: Make sure your `.env` file has at least one API key:
```bash
# Check if .env exists and has keys
cat .env | grep API_KEY
```

Or use the setup script:
```bash
python scripts/implement_all_api_keys.py
```

### Analysis Not Appearing in Problems Panel

**Solution**:
1. Check that the task ran successfully (look at terminal output)
2. Verify problem matcher is working: `Ctrl+Shift+P` → "Problems: Focus on Problems View"
3. Check file path is absolute (should be automatic)

### Watch Mode Not Working

**Solution**:
1. Check terminal output for errors
2. Verify `src/` directory exists
3. Make sure files are being saved (not just edited)
4. Check cooldown period (default 3 seconds)

## 📁 File Structure

```
.github/scripts/
├── cursor_ai_diagnostics.py    # Main diagnostics script
├── ai_watch_daemon.py          # Watch mode daemon
└── CURSOR_AI_INTEGRATION_README.md  # This file

.vscode/
├── tasks.json                  # VS Code tasks configuration
├── settings.json               # VS Code settings
├── keybindings.json            # Keyboard shortcuts
└── extensions.json             # Recommended extensions

.git/hooks/
└── pre-commit                  # Pre-commit hook
```

## 🔗 Integration with GitHub Actions

This local integration uses the **exact same AI system** as your GitHub Actions PR analysis:

- Same AI router (`enhanced_router_v2.py`)
- Same 15-provider fallback system
- Same analysis format
- Same bulletproof validation

**Difference**: Local analysis is faster (no GitHub API calls) and provides real-time feedback.

## 📈 Performance

- **First Analysis**: ~2-5 seconds (depends on AI provider)
- **Cached Analysis**: Instant (5-minute cache)
- **Watch Mode**: ~3 second cooldown per file
- **Pre-commit**: Analyzes all staged files in parallel

## 🎓 Best Practices

1. **Use Watch Mode During Active Development**
   - Start watch mode at beginning of session
   - Get real-time feedback as you code
   - Fix issues immediately

2. **Manual Analysis for Deep Dives**
   - Use `Ctrl+Shift+A` for focused analysis
   - Review JSON reports for detailed insights
   - Compare before/after when refactoring

3. **Pre-commit Hook for Quality Gate**
   - Never skip pre-commit analysis
   - Fix critical issues before committing
   - Address warnings when possible

4. **Review Problems Panel Regularly**
   - Keep Problems panel open (`Ctrl+Shift+M`)
   - Sort by severity (errors first)
   - Use "Go to Problem" to navigate quickly

## 🚀 Advanced Usage

### Analyze Multiple Files

```bash
# Analyze all Python files in a directory
find src/amas -name "*.py" -exec python3 .github/scripts/cursor_ai_diagnostics.py {} \;
```

### Generate JSON Reports for All Files

```bash
# Generate JSON reports for all Python files
find src/amas -name "*.py" -exec python3 .github/scripts/cursor_ai_diagnostics.py {} json \;
```

### Custom Analysis Script

```python
import asyncio
from .github.scripts.cursor_ai_diagnostics import BulletproofAIDiagnostics

async def analyze_project():
    analyzer = BulletproofAIDiagnostics()
    
    for file_path in Path("src").rglob("*.py"):
        with open(file_path) as f:
            code = f.read()
        
        diagnostics = await analyzer.analyze_code(str(file_path), code)
        print(f"{file_path}: {len(diagnostics)} issues")

asyncio.run(analyze_project())
```

## 📝 Example Workflow

1. **Start Development Session**:
   ```bash
   # Start watch mode
   Ctrl+Shift+Alt+A
   ```

2. **Edit Code**:
   - Open `src/amas/core/orchestrator.py`
   - Make changes
   - Save file (Ctrl+S)

3. **Review Analysis**:
   - Check Problems panel (Ctrl+Shift+M)
   - See real-time diagnostics
   - Fix issues inline

4. **Deep Analysis**:
   - Press Ctrl+Shift+A for detailed analysis
   - Review JSON report (Ctrl+Shift+R)
   - Address all critical issues

5. **Commit**:
   ```bash
   git add .
   git commit -m "Fix: Address AI analysis recommendations"
   # Pre-commit hook runs automatically
   ```

## ✅ Verification

Test that everything works:

```bash
# 1. Test diagnostics script
python3 .github/scripts/cursor_ai_diagnostics.py src/amas/core/orchestrator.py

# 2. Test watch daemon (run in background)
python3 .github/scripts/ai_watch_daemon.py &
# Edit a file, save it, check output

# 3. Test pre-commit hook
git add .github/scripts/cursor_ai_diagnostics.py
git commit -m "Test: Verify pre-commit hook"
```

## 🎉 Success Indicators

You'll know it's working when:

- ✅ Pressing `Ctrl+Shift+A` shows analysis in terminal
- ✅ Problems panel shows Bulletproof AI diagnostics
- ✅ Watch mode outputs analysis on file save
- ✅ Pre-commit hook runs before commits
- ✅ JSON reports are generated (`.diagnostics.json` files)

## 📞 Support

If you encounter issues:

1. Check this README's troubleshooting section
2. Review terminal output for error messages
3. Verify API keys are configured
4. Check that all dependencies are installed
5. Review `.github/scripts/cursor_ai_diagnostics.py` logs

## 🔄 Updates

This integration automatically uses the latest version of:
- `src/amas/ai/enhanced_router_v2.py` (AI router)
- `.github/scripts/bulletproof_ai_pr_analyzer.py` (analysis logic)

No separate updates needed - just pull the latest code!

---

**Enjoy your enhanced development experience with Bulletproof AI Analysis! 🚀**

