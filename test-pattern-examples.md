# 🎯 Test Pattern Examples for PR #157

## Critical: These patterns MUST be preserved when resolving conflicts!

### 1. Task Submission Pattern

#### ❌ OLD Pattern (from main branch - DON'T USE)
```python
# This is what main branch has - DON'T KEEP THIS
task_id = await orchestrator.submit_task(
    title="Test Task",
    description="A test task",
    parameters={"param": "value"},
    priority="high"  # String priority - WRONG!
)
```

#### ✅ NEW Pattern (from PR #157 - KEEP THIS)
```python
# This is what PR #157 introduces - ALWAYS USE THIS
from amas.core.unified_orchestrator_v2 import TaskPriority

task_id = await orchestrator.submit_task(
    description="A test task",
    task_type="test",
    priority=TaskPriority.HIGH,  # Enum - CORRECT!
    metadata={
        "title": "Test Task",
        "parameters": {"param": "value"},
        "required_agent_roles": ["test_agent"]
    }
)
```

### 2. Agent Execute Task Pattern

#### ❌ OLD Pattern
```python
# Don't use this
result = await agent.execute_task(
    title="Test",
    parameters={"key": "value"}
)
```

#### ✅ NEW Pattern
```python
# Use this instead
from amas.core.unified_orchestrator_v2 import OrchestratorTask

task = OrchestratorTask(
    task_id="test_001",
    description="Test task",
    task_type="test",
    metadata={
        "title": "Test",
        "parameters": {"key": "value"},
        "required_agent_roles": ["test_agent"]
    }
)
result = await agent.execute_task(task)
```

### 3. Test Fixture Pattern

#### ❌ OLD Async Fixture (causes warnings)
```python
@pytest.fixture
async def my_agent(mock_orchestrator):
    # This causes "coroutine was never awaited" warning
    return MyAgent(orchestrator=mock_orchestrator)
```

#### ✅ NEW Async Fixture (fixed)
```python
@pytest.fixture
async def my_agent(mock_orchestrator):
    agent = MyAgent(orchestrator=mock_orchestrator)
    await agent.initialize()  # Properly await initialization
    return agent
```

### 4. Import Pattern in __init__.py

When you see conflicts in __init__.py files, **MERGE ALL IMPORTS**:

```python
# If HEAD has:
from .orchestrator import Orchestrator
from .task_manager import TaskManager

# And PR branch has:
from .unified_orchestrator_v2 import UnifiedOrchestratorV2
from .task_manager import TaskManager
from .types import TaskPriority

# KEEP ALL (remove duplicates):
from .orchestrator import Orchestrator
from .unified_orchestrator_v2 import UnifiedOrchestratorV2
from .task_manager import TaskManager
from .types import TaskPriority

__all__ = [
    "Orchestrator",
    "UnifiedOrchestratorV2", 
    "TaskManager",
    "TaskPriority",
]
```

## 🔍 What to Look for in Conflicts

### In test files (tests/*.py):
1. **Find:** `priority="high"` → **Replace with:** `priority=TaskPriority.HIGH`
2. **Find:** `title=` as direct parameter → **Move to:** `metadata={"title": ...}`
3. **Find:** `parameters=` as direct parameter → **Move to:** `metadata={"parameters": ...}`

### In core files (src/amas/core/*.py):
1. **Keep:** New `submit_task` signature with `metadata` parameter
2. **Keep:** `_handle_agent_message` that extracts from metadata
3. **Keep:** AgentConfig usage in `_initialize_orchestrator_agents`

## 📝 Conflict Resolution Checklist

When you open a conflicted file:

- [ ] Look for `<<<<<<< HEAD` markers
- [ ] Identify if it's test code or core code
- [ ] If test code: KEEP PR #157's version
- [ ] If core code: Keep PR's structure, merge new features
- [ ] Remove all conflict markers
- [ ] Verify imports are complete
- [ ] Check indentation is correct
- [ ] Save and `git add` the file

## 💡 Pro Tip

When in doubt, ask yourself:
1. Does this code use the metadata field? (Should be YES)
2. Does this code use TaskPriority enum? (Should be YES)
3. Are async fixtures properly awaited? (Should be YES)

If any answer is NO, you're probably keeping the wrong version!