# 🔧 Step-by-Step Conflict Resolution for PR #157

## 🎯 Quick Overview
PR #157 contains critical test suite fixes. When resolving conflicts:
- **KEEP** PR #157's test improvements
- **MERGE** new features from main
- **USE** TaskPriority enum (not strings)
- **PRESERVE** metadata field structure

## 📋 Command Sequence

### 1. First, verify you're in merge state
```bash
git status
```

### 2. Create backups (safety first!)
```bash
mkdir -p conflict-backups
for f in README.md src/amas/__init__.py src/amas/agents/__init__.py \
         src/amas/agents/base/agent_communication.py src/amas/config/settings.py \
         src/amas/core/integration_manager.py src/amas/core/orchestrator.py \
         src/amas/main.py src/amas/services/service_manager.py \
         tests/test_agents.py tests/test_integration.py; do
    cp "$f" "conflict-backups/$(echo $f | tr '/' '_').backup" 2>/dev/null
done
```

## 🔍 File-by-File Resolution

### File 1: README.md
```bash
# Open the file
code README.md  # or vim/nano

# Resolution strategy:
# - Keep both versions' content
# - Merge feature lists
# - Update version numbers
# - Remove conflict markers: <<<<<<< HEAD, =======, >>>>>>>

# After editing:
git add README.md
```

### File 2: src/amas/__init__.py
```bash
code src/amas/__init__.py

# Resolution: MERGE ALL IMPORTS
# Example:
# If HEAD has: from .orchestrator import Orchestrator
# If PR has: from .unified_orchestrator_v2 import UnifiedOrchestratorV2
# Keep BOTH!

git add src/amas/__init__.py
```

### File 3: src/amas/agents/__init__.py
```bash
code src/amas/agents/__init__.py

# Same as above - merge all agent imports
# Remove duplicates, keep all unique imports

git add src/amas/agents/__init__.py
```

### File 4: src/amas/agents/base/agent_communication.py
```bash
code src/amas/agents/base/agent_communication.py

# PRIORITY: Keep PR's async fixes!
# Look for properly awaited coroutines
# Merge any new methods from main

git add src/amas/agents/base/agent_communication.py
```

### File 5: src/amas/config/settings.py
```bash
code src/amas/config/settings.py

# Merge all configuration entries
# Watch for duplicate keys
# Keep the most complete/recent values

git add src/amas/config/settings.py
```

### File 6: src/amas/core/integration_manager.py
```bash
code src/amas/core/integration_manager.py

# CRITICAL: Keep PR's metadata structure!
# OLD: task = OrchestratorTask(title=..., parameters=...)
# NEW: task = OrchestratorTask(metadata={"title": ..., "parameters": ...})

git add src/amas/core/integration_manager.py
```

### File 7: src/amas/core/orchestrator.py
```bash
code src/amas/core/orchestrator.py

# CRITICAL: Keep PR's submit_task signature!
# OLD: submit_task(title, description, parameters)
# NEW: submit_task(description, task_type, priority, metadata)

git add src/amas/core/orchestrator.py
```

### File 8: src/amas/main.py
```bash
code src/amas/main.py

# Merge initialization code
# Keep both PR's fixes and new features

git add src/amas/main.py
```

### File 9: src/amas/services/service_manager.py
```bash
code src/amas/services/service_manager.py

# Keep PR's async improvements
# Add any new services from main

git add src/amas/services/service_manager.py
```

### File 10: tests/test_agents.py ⚠️ CRITICAL
```bash
code tests/test_agents.py

# MUST KEEP PR's changes!
# All tests now use:
# task = OrchestratorTask(
#     task_id="test_001",
#     metadata={"title": ..., "parameters": ..., "required_agent_roles": [...]}
# )

git add tests/test_agents.py
```

### File 11: tests/test_integration.py ⚠️ MOST CRITICAL
```bash
code tests/test_integration.py

# MUST KEEP ALL PR CHANGES!
# Key changes to preserve:
# 1. TaskPriority.MEDIUM (not "medium")
# 2. metadata field usage
# 3. New submit_task signature
# 4. Fixed async fixtures

git add tests/test_integration.py
```

## ✅ Verification Steps

### 3. Check all conflicts resolved
```bash
# No output = good!
grep -r "<<<<<<< HEAD" src/ tests/ README.md
grep -r "=======" src/ tests/ README.md
grep -r ">>>>>>>" src/ tests/ README.md
```

### 4. Verify Python syntax
```bash
python -m py_compile src/amas/*.py src/amas/**/*.py
```

### 5. Quick test
```bash
# Run a simple test to ensure basics work
python -m pytest tests/test_core.py::TestCore::test_initialization -v
```

### 6. Complete the merge
```bash
# Check all files are staged
git status

# Commit with descriptive message
git commit -m "Merge main into feature/test-suite-fixes

Resolved conflicts by:
- Preserving all test suite improvements from PR #157
- Keeping new task structure with metadata field
- Maintaining TaskPriority enum usage
- Merging new features from main branch
- Fixing async fixture handling"
```

### 7. Push the resolution
```bash
git push origin feature/test-suite-fixes
```

## 🚨 If Something Goes Wrong

```bash
# Restore from backups
for f in conflict-backups/*.backup; do
    original=$(echo "$(basename "$f" .backup)" | tr '_' '/')
    cp "$f" "$original"
done

# Or abort and start over
git merge --abort
```

## 💡 Remember These Key Points:

1. **tests/test_integration.py** - Keep ALL PR changes
2. **tests/test_agents.py** - Keep new test structure
3. **Task structure** - Always use metadata field
4. **TaskPriority** - Use enum, not strings
5. **Async fixes** - Keep all await corrections

---
Need help with a specific file? Check the conflict markers and apply the rules above!