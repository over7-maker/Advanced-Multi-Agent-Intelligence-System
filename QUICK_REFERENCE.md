# 🎯 Quick Reference: PR #157 Key Changes

## Task Structure Change (CRITICAL!)

### ❌ OLD (Don't use this):
```python
task = await orchestrator.submit_task(
    title="My Task",
    description="Do something",
    parameters={"key": "value"},
    priority="high"
)
```

### ✅ NEW (Always use this):
```python
from amas.core.unified_orchestrator_v2 import TaskPriority

task = await orchestrator.submit_task(
    description="Do something",
    task_type="analysis",
    priority=TaskPriority.HIGH,  # Enum!
    metadata={
        "title": "My Task",
        "parameters": {"key": "value"},
        "required_agent_roles": ["analyzer"]
    }
)
```

## Test Pattern Change

### ❌ OLD Test Pattern:
```python
result = await agent.execute_task(
    title="Test",
    parameters={...}
)
```

### ✅ NEW Test Pattern:
```python
task = OrchestratorTask(
    task_id="test_001",
    description="Test",
    task_type="test",
    metadata={
        "title": "Test",
        "parameters": {...},
        "required_agent_roles": ["test_agent"]
    }
)
result = await agent.execute_task(task)
```

## Async Fixture Fix

### ❌ OLD (Causes warnings):
```python
@pytest.fixture
async def my_fixture(dependency):
    return MyClass(dependency)  # Missing await!
```

### ✅ NEW (Fixed):
```python
@pytest.fixture
async def my_fixture(dependency):
    instance = MyClass(dependency)
    await instance.initialize()  # Proper await
    return instance
```

## Import Merging Rule

When you see conflicts in imports:
1. Take ALL imports from BOTH sides
2. Remove duplicates
3. Sort them
4. Group by: standard lib, third-party, local

## Quick Conflict Resolution

```bash
# 1. See the structure changes
python scripts/auto-resolve-helper.py show-structure

# 2. For each conflicted file
code <filename>  # or vim, nano, etc.

# 3. After fixing
git add <filename>

# 4. When done
git commit
```

## Priority Order

1. 🔴 **tests/test_integration.py** - Most critical, keep PR changes
2. 🔴 **tests/test_agents.py** - Keep new test patterns
3. 🟡 **src/amas/core/orchestrator.py** - Keep new signatures
4. 🟡 **src/amas/core/integration_manager.py** - Keep metadata handling
5. 🟢 **__init__.py files** - Just merge all imports
6. 🟢 **Other files** - Merge features from both

---
**Golden Rule**: When in doubt about test code, keep PR #157's version!