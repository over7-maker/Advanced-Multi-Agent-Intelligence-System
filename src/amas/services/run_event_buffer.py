from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


async def list_run_events_merged(task_id: str, db: Optional[AsyncSession] = None) -> List[Dict[str, Any]]:
    """
    Return merged RunEvents for a task.

    This repository currently treats RunEvent buffering as optional/gradual adoption.
    The default implementation is a safe no-op so operator endpoints and tests can
    import/patch it without dragging in optional persistence layers.
    """
    _ = (task_id, db)
    return []

