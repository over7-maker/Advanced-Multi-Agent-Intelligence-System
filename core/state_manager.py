"""
AMAS Shared State Manager

Advanced state management system for multi-agent coordination:
- Shared memory and context across agents
- State synchronization and consistency
- Conflict resolution and merging
- State versioning and history
- Real-time state updates
- State security and access control

Enables seamless information sharing and coordination between agents.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set
from enum import Enum
from dataclasses import dataclass, field
import time
import threading
from collections import defaultdict
import copy

logger = logging.getLogger(__name__)


class StateScope(Enum):
    """Scope levels for state management"""
    GLOBAL = "global"        # System-wide state
    WORKFLOW = "workflow"    # Workflow-specific state
    TASK = "task"           # Task-specific state
    AGENT = "agent"         # Agent-specific state
    SESSION = "session"     # Session-specific state


class StateOperation(Enum):
    """Types of state operations"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    LOCK = "lock"
    UNLOCK = "unlock"


class AccessLevel(Enum):
    """Access levels for state data"""
    PUBLIC = "public"        # All agents can read/write
    PROTECTED = "protected"  # Specific agents can read/write
    PRIVATE = "private"      # Only owner can read/write
    READ_ONLY = "read_only"  # All can read, owner can write


@dataclass
class StateEntry:
    """Individual state entry with metadata"""
    key: str
    value: Any
    scope: StateScope
    owner_agent: str
    access_level: AccessLevel
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    authorized_agents: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    ttl: Optional[datetime] = None


@dataclass
class StateSnapshot:
    """Snapshot of state at a specific point in time"""
    snapshot_id: str
    scope: StateScope
    scope_id: str
    state_data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    description: str = ""


@dataclass
class StateLock:
    """Lock for state synchronization"""
    lock_id: str
    state_key: str
    owner_agent: str
    acquired_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=5))
    lock_type: str = "exclusive"  # exclusive, shared


class AdvancedStateManager:
    """
    Advanced state management system for multi-agent coordination.
    
    Provides:
    - Hierarchical state scopes (global, workflow, task, agent, session)
    - Access control and security
    - State versioning and history
    - Conflict resolution
    - Real-time synchronization
    - State persistence and recovery
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # State storage
        self.state_entries: Dict[str, StateEntry] = {}
        self.state_history: Dict[str, List[StateEntry]] = defaultdict(list)
        self.state_snapshots: Dict[str, StateSnapshot] = {}
        
        # Synchronization
        self.state_locks: Dict[str, StateLock] = {}
        self.lock_waiters: Dict[str, List[asyncio.Event]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # Subscriptions and notifications
        self.state_subscribers: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.change_notifications: asyncio.Queue = asyncio.Queue()
        
        # Performance metrics
        self.state_metrics = {
            'total_operations': 0,
            'read_operations': 0,
            'write_operations': 0,
            'lock_acquisitions': 0,
            'conflict_resolutions': 0,
            'average_operation_time': 0.0,
            'state_size': 0,
            'active_locks': 0
        }
        
        # Configuration
        self.max_history_per_key = config.get('max_history_per_key', 100)
        self.default_ttl_hours = config.get('default_ttl_hours', 24)
        self.lock_timeout_minutes = config.get('lock_timeout_minutes', 5)
        self.cleanup_interval_minutes = config.get('cleanup_interval_minutes', 15)
        
        # Background tasks
        self._running = False
        self._background_tasks = []
        
        logger.info("Advanced State Manager initialized")
    
    async def start(self):
        """Start the state manager and background tasks"""
        try:
            self._running = True
            
            # Start background tasks
            self._background_tasks = [
                asyncio.create_task(self._cleanup_expired_states()),
                asyncio.create_task(self._cleanup_expired_locks()),
                asyncio.create_task(self._process_change_notifications()),
                asyncio.create_task(self._performance_monitor())
            ]
            
            logger.info("State Manager started with background tasks")
            
        except Exception as e:
            logger.error(f"Error starting state manager: {e}")
            raise
    
    async def stop(self):
        """Stop the state manager and cleanup"""
        try:
            self._running = False
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("State Manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping state manager: {e}")
    
    async def set_state(
        self,
        key: str,
        value: Any,
        scope: StateScope,
        owner_agent: str,
        access_level: AccessLevel = AccessLevel.PROTECTED,
        authorized_agents: Optional[Set[str]] = None,
        tags: Optional[Set[str]] = None,
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Set state value with comprehensive metadata and access control.
        
        Args:
            key: State key
            value: State value
            scope: State scope level
            owner_agent: Agent setting the state
            access_level: Access level for the state
            authorized_agents: Set of authorized agents (for PROTECTED access)
            tags: Optional tags for categorization
            ttl_hours: Time-to-live in hours
            
        Returns:
            True if state was set successfully
        """
        try:
            start_time = time.time()
            
            # Acquire lock if state exists
            if key in self.state_entries:
                lock_acquired = await self._acquire_state_lock(key, owner_agent)
                if not lock_acquired:
                    logger.warning(f"Could not acquire lock for state key: {key}")
                    return False
            
            try:
                # Create or update state entry
                ttl = None
                if ttl_hours:
                    ttl = datetime.utcnow() + timedelta(hours=ttl_hours)
                elif self.default_ttl_hours:
                    ttl = datetime.utcnow() + timedelta(hours=self.default_ttl_hours)
                
                if key in self.state_entries:
                    # Update existing entry
                    existing_entry = self.state_entries[key]
                    
                    # Store in history
                    self.state_history[key].append(copy.deepcopy(existing_entry))
                    
                    # Update entry
                    existing_entry.value = value
                    existing_entry.updated_at = datetime.utcnow()
                    existing_entry.version += 1
                    existing_entry.ttl = ttl
                    
                    if authorized_agents:
                        existing_entry.authorized_agents = authorized_agents
                    if tags:
                        existing_entry.tags = tags
                    
                    entry = existing_entry
                else:
                    # Create new entry
                    entry = StateEntry(
                        key=key,
                        value=value,
                        scope=scope,
                        owner_agent=owner_agent,
                        access_level=access_level,
                        authorized_agents=authorized_agents or set(),
                        tags=tags or set(),
                        ttl=ttl
                    )
                    
                    self.state_entries[key] = entry
                
                # Maintain history size
                if len(self.state_history[key]) > self.max_history_per_key:
                    self.state_history[key] = self.state_history[key][-self.max_history_per_key:]
                
                # Notify subscribers
                await self._notify_state_change(key, entry, StateOperation.UPDATE if key in self.state_entries else StateOperation.CREATE)
                
                # Update metrics
                self.state_metrics['total_operations'] += 1
                self.state_metrics['write_operations'] += 1
                self.state_metrics['state_size'] = len(self.state_entries)
                
                operation_time = time.time() - start_time
                self._update_average_operation_time(operation_time)
                
                logger.info(f"State set: {key} by {owner_agent} (scope: {scope.value})")
                
                return True
                
            finally:
                # Release lock
                if key in self.state_locks:
                    await self._release_state_lock(key, owner_agent)
            
        except Exception as e:
            logger.error(f"Error setting state {key}: {e}")
            return False
    
    async def get_state(
        self,
        key: str,
        requesting_agent: str,
        default: Any = None
    ) -> Any:
        """
        Get state value with access control validation.
        
        Args:
            key: State key
            requesting_agent: Agent requesting the state
            default: Default value if state not found
            
        Returns:
            State value or default
        """
        try:
            start_time = time.time()
            
            if key not in self.state_entries:
                return default
            
            entry = self.state_entries[key]
            
            # Check access permissions
            if not await self._check_read_access(entry, requesting_agent):
                logger.warning(f"Access denied for agent {requesting_agent} to state {key}")
                return default
            
            # Check TTL
            if entry.ttl and datetime.utcnow() > entry.ttl:
                # State expired
                await self._expire_state(key)
                return default
            
            # Update access metadata
            entry.metadata['last_accessed'] = datetime.utcnow().isoformat()
            entry.metadata['last_accessed_by'] = requesting_agent
            entry.metadata.setdefault('access_count', 0)
            entry.metadata['access_count'] += 1
            
            # Update metrics
            self.state_metrics['total_operations'] += 1
            self.state_metrics['read_operations'] += 1
            
            operation_time = time.time() - start_time
            self._update_average_operation_time(operation_time)
            
            return entry.value
            
        except Exception as e:
            logger.error(f"Error getting state {key}: {e}")
            return default
    
    async def delete_state(
        self,
        key: str,
        requesting_agent: str
    ) -> bool:
        """
        Delete state entry with access control validation.
        
        Args:
            key: State key to delete
            requesting_agent: Agent requesting deletion
            
        Returns:
            True if deletion successful
        """
        try:
            if key not in self.state_entries:
                return False
            
            entry = self.state_entries[key]
            
            # Check delete permissions (only owner or authorized agents)
            if not await self._check_write_access(entry, requesting_agent):
                logger.warning(f"Delete access denied for agent {requesting_agent} to state {key}")
                return False
            
            # Acquire lock
            lock_acquired = await self._acquire_state_lock(key, requesting_agent)
            if not lock_acquired:
                return False
            
            try:
                # Store final version in history
                self.state_history[key].append(copy.deepcopy(entry))
                
                # Delete entry
                del self.state_entries[key]
                
                # Notify subscribers
                await self._notify_state_change(key, entry, StateOperation.DELETE)
                
                # Update metrics
                self.state_metrics['total_operations'] += 1
                self.state_metrics['state_size'] = len(self.state_entries)
                
                logger.info(f"State deleted: {key} by {requesting_agent}")
                
                return True
                
            finally:
                await self._release_state_lock(key, requesting_agent)
            
        except Exception as e:
            logger.error(f"Error deleting state {key}: {e}")
            return False
    
    async def merge_state(
        self,
        key: str,
        partial_value: Dict[str, Any],
        requesting_agent: str,
        merge_strategy: str = "deep_merge"
    ) -> bool:
        """
        Merge partial state update with existing state.
        
        Args:
            key: State key
            partial_value: Partial state to merge
            requesting_agent: Agent performing the merge
            merge_strategy: Strategy for merging (deep_merge, shallow_merge, replace)
            
        Returns:
            True if merge successful
        """
        try:
            if key not in self.state_entries:
                # Create new state if doesn't exist
                return await self.set_state(
                    key=key,
                    value=partial_value,
                    scope=StateScope.WORKFLOW,
                    owner_agent=requesting_agent
                )
            
            entry = self.state_entries[key]
            
            # Check write access
            if not await self._check_write_access(entry, requesting_agent):
                logger.warning(f"Merge access denied for agent {requesting_agent} to state {key}")
                return False
            
            # Acquire lock
            lock_acquired = await self._acquire_state_lock(key, requesting_agent)
            if not lock_acquired:
                return False
            
            try:
                # Store current version in history
                self.state_history[key].append(copy.deepcopy(entry))
                
                # Perform merge based on strategy
                if merge_strategy == "deep_merge":
                    merged_value = await self._deep_merge(entry.value, partial_value)
                elif merge_strategy == "shallow_merge":
                    merged_value = {**entry.value, **partial_value} if isinstance(entry.value, dict) else partial_value
                else:  # replace
                    merged_value = partial_value
                
                # Update entry
                entry.value = merged_value
                entry.updated_at = datetime.utcnow()
                entry.version += 1
                
                # Notify subscribers
                await self._notify_state_change(key, entry, StateOperation.MERGE)
                
                # Update metrics
                self.state_metrics['total_operations'] += 1
                self.state_metrics['write_operations'] += 1
                
                logger.info(f"State merged: {key} by {requesting_agent} using {merge_strategy}")
                
                return True
                
            finally:
                await self._release_state_lock(key, requesting_agent)
            
        except Exception as e:
            logger.error(f"Error merging state {key}: {e}")
            return False
    
    async def _deep_merge(self, existing: Any, update: Any) -> Any:
        """Perform deep merge of two values"""
        try:
            if isinstance(existing, dict) and isinstance(update, dict):
                result = copy.deepcopy(existing)
                for key, value in update.items():
                    if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                        result[key] = await self._deep_merge(result[key], value)
                    else:
                        result[key] = copy.deepcopy(value)
                return result
            elif isinstance(existing, list) and isinstance(update, list):
                # For lists, append new items
                return existing + update
            else:
                # For other types, replace
                return copy.deepcopy(update)
                
        except Exception as e:
            logger.error(f"Error in deep merge: {e}")
            return update
    
    async def subscribe_to_state_changes(
        self,
        agent_id: str,
        state_key_pattern: str,
        callback: callable,
        scope: Optional[StateScope] = None
    ) -> str:
        """
        Subscribe to state changes for real-time updates.
        
        Args:
            agent_id: Subscribing agent ID
            state_key_pattern: Pattern for state keys to monitor (supports wildcards)
            callback: Callback function for notifications
            scope: Optional scope filter
            
        Returns:
            Subscription ID
        """
        try:
            subscription_id = str(uuid.uuid4())
            
            subscription = {
                'subscription_id': subscription_id,
                'agent_id': agent_id,
                'pattern': state_key_pattern,
                'callback': callback,
                'scope': scope,
                'created_at': datetime.utcnow(),
                'notification_count': 0
            }
            
            self.state_subscribers[state_key_pattern].append(subscription)
            
            logger.info(f"Agent {agent_id} subscribed to state changes: {state_key_pattern}")
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error subscribing to state changes: {e}")
            raise
    
    async def _notify_state_change(
        self,
        state_key: str,
        entry: StateEntry,
        operation: StateOperation
    ):
        """Notify subscribers of state changes"""
        try:
            notification = {
                'state_key': state_key,
                'operation': operation.value,
                'scope': entry.scope.value,
                'owner_agent': entry.owner_agent,
                'updated_at': entry.updated_at.isoformat(),
                'version': entry.version,
                'value': entry.value if entry.access_level in [AccessLevel.PUBLIC] else None
            }
            
            # Find matching subscribers
            for pattern, subscribers in self.state_subscribers.items():
                if self._matches_pattern(state_key, pattern):
                    for subscription in subscribers:
                        # Check scope filter
                        if subscription['scope'] and subscription['scope'] != entry.scope:
                            continue
                        
                        try:
                            await subscription['callback'](notification)
                            subscription['notification_count'] += 1
                        except Exception as e:
                            logger.error(f"Error in state change callback: {e}")
            
            # Add to notification queue for processing
            await self.change_notifications.put(notification)
            
        except Exception as e:
            logger.error(f"Error notifying state change: {e}")
    
    def _matches_pattern(self, state_key: str, pattern: str) -> bool:
        """Check if state key matches subscription pattern"""
        try:
            # Simple wildcard matching
            if '*' in pattern:
                import fnmatch
                return fnmatch.fnmatch(state_key, pattern)
            else:
                return state_key == pattern
                
        except Exception as e:
            logger.error(f"Error matching pattern: {e}")
            return False
    
    async def _check_read_access(self, entry: StateEntry, agent_id: str) -> bool:
        """Check if agent has read access to state entry"""
        try:
            if entry.access_level == AccessLevel.PUBLIC:
                return True
            elif entry.access_level == AccessLevel.PRIVATE:
                return agent_id == entry.owner_agent
            elif entry.access_level == AccessLevel.PROTECTED:
                return (agent_id == entry.owner_agent or 
                       agent_id in entry.authorized_agents)
            elif entry.access_level == AccessLevel.READ_ONLY:
                return True  # Everyone can read
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking read access: {e}")
            return False
    
    async def _check_write_access(self, entry: StateEntry, agent_id: str) -> bool:
        """Check if agent has write access to state entry"""
        try:
            if entry.access_level == AccessLevel.PUBLIC:
                return True
            elif entry.access_level == AccessLevel.READ_ONLY:
                return agent_id == entry.owner_agent
            elif entry.access_level in [AccessLevel.PRIVATE, AccessLevel.PROTECTED]:
                return (agent_id == entry.owner_agent or 
                       agent_id in entry.authorized_agents)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking write access: {e}")
            return False
    
    async def _acquire_state_lock(
        self,
        state_key: str,
        agent_id: str,
        timeout_seconds: int = 30
    ) -> bool:
        """Acquire exclusive lock on state key"""
        try:
            with self._lock:
                # Check if already locked
                if state_key in self.state_locks:
                    existing_lock = self.state_locks[state_key]
                    
                    # Check if lock expired
                    if datetime.utcnow() > existing_lock.expires_at:
                        del self.state_locks[state_key]
                    else:
                        # Lock still active
                        if existing_lock.owner_agent == agent_id:
                            # Extend lock
                            existing_lock.expires_at = datetime.utcnow() + timedelta(minutes=self.lock_timeout_minutes)
                            return True
                        else:
                            # Wait for lock or timeout
                            return await self._wait_for_lock(state_key, agent_id, timeout_seconds)
                
                # Acquire new lock
                lock = StateLock(
                    lock_id=str(uuid.uuid4()),
                    state_key=state_key,
                    owner_agent=agent_id
                )
                
                self.state_locks[state_key] = lock
                self.state_metrics['lock_acquisitions'] += 1
                self.state_metrics['active_locks'] = len(self.state_locks)
                
                logger.debug(f"Lock acquired on {state_key} by {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error acquiring lock on {state_key}: {e}")
            return False
    
    async def _release_state_lock(self, state_key: str, agent_id: str) -> bool:
        """Release lock on state key"""
        try:
            with self._lock:
                if state_key not in self.state_locks:
                    return False
                
                lock = self.state_locks[state_key]
                
                if lock.owner_agent != agent_id:
                    logger.warning(f"Agent {agent_id} cannot release lock owned by {lock.owner_agent}")
                    return False
                
                del self.state_locks[state_key]
                self.state_metrics['active_locks'] = len(self.state_locks)
                
                # Notify waiting agents
                if state_key in self.lock_waiters:
                    for event in self.lock_waiters[state_key]:
                        event.set()
                    del self.lock_waiters[state_key]
                
                logger.debug(f"Lock released on {state_key} by {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error releasing lock on {state_key}: {e}")
            return False
    
    async def _wait_for_lock(
        self,
        state_key: str,
        agent_id: str,
        timeout_seconds: int
    ) -> bool:
        """Wait for lock to become available"""
        try:
            event = asyncio.Event()
            self.lock_waiters[state_key].append(event)
            
            try:
                await asyncio.wait_for(event.wait(), timeout=timeout_seconds)
                # Try to acquire lock again
                return await self._acquire_state_lock(state_key, agent_id, 0)
            except asyncio.TimeoutError:
                logger.warning(f"Lock wait timeout for {state_key} by {agent_id}")
                return False
            finally:
                # Remove from waiters
                if event in self.lock_waiters[state_key]:
                    self.lock_waiters[state_key].remove(event)
                
        except Exception as e:
            logger.error(f"Error waiting for lock: {e}")
            return False
    
    async def create_state_snapshot(
        self,
        scope: StateScope,
        scope_id: str,
        creating_agent: str,
        description: str = ""
    ) -> str:
        """Create a snapshot of state for backup/restore purposes"""
        try:
            snapshot_id = str(uuid.uuid4())
            
            # Collect state data for scope
            state_data = {}
            for key, entry in self.state_entries.items():
                if entry.scope == scope:
                    # Include scope-specific filtering logic here
                    state_data[key] = {
                        'value': entry.value,
                        'version': entry.version,
                        'updated_at': entry.updated_at.isoformat(),
                        'owner_agent': entry.owner_agent,
                        'access_level': entry.access_level.value
                    }
            
            snapshot = StateSnapshot(
                snapshot_id=snapshot_id,
                scope=scope,
                scope_id=scope_id,
                state_data=state_data,
                created_by=creating_agent,
                description=description
            )
            
            self.state_snapshots[snapshot_id] = snapshot
            
            logger.info(f"State snapshot created: {snapshot_id} for scope {scope.value}")
            
            return snapshot_id
            
        except Exception as e:
            logger.error(f"Error creating state snapshot: {e}")
            raise
    
    def _update_average_operation_time(self, operation_time: float):
        """Update average operation time metric"""
        current_avg = self.state_metrics['average_operation_time']
        total_ops = self.state_metrics['total_operations']
        
        if total_ops > 0:
            self.state_metrics['average_operation_time'] = (
                (current_avg * (total_ops - 1) + operation_time) / total_ops
            )
    
    async def _cleanup_expired_states(self):
        """Background task to clean up expired state entries"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, entry in self.state_entries.items():
                    if entry.ttl and current_time > entry.ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self._expire_state(key)
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired state entries")
                
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in state cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _expire_state(self, key: str):
        """Expire a state entry"""
        try:
            if key in self.state_entries:
                entry = self.state_entries[key]
                
                # Store in history
                self.state_history[key].append(copy.deepcopy(entry))
                
                # Remove from active state
                del self.state_entries[key]
                
                # Notify subscribers
                await self._notify_state_change(key, entry, StateOperation.DELETE)
                
                logger.debug(f"State expired: {key}")
                
        except Exception as e:
            logger.error(f"Error expiring state {key}: {e}")
    
    async def _cleanup_expired_locks(self):
        """Background task to clean up expired locks"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                expired_locks = []
                
                for lock_key, lock in self.state_locks.items():
                    if current_time > lock.expires_at:
                        expired_locks.append(lock_key)
                
                for lock_key in expired_locks:
                    del self.state_locks[lock_key]
                    
                    # Notify waiters
                    if lock_key in self.lock_waiters:
                        for event in self.lock_waiters[lock_key]:
                            event.set()
                        del self.lock_waiters[lock_key]
                
                if expired_locks:
                    logger.info(f"Cleaned up {len(expired_locks)} expired locks")
                
                self.state_metrics['active_locks'] = len(self.state_locks)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in lock cleanup: {e}")
                await asyncio.sleep(300)
    
    async def _process_change_notifications(self):
        """Background task to process state change notifications"""
        while self._running:
            try:
                # Process notifications from queue
                try:
                    notification = await asyncio.wait_for(
                        self.change_notifications.get(),
                        timeout=1.0
                    )
                    
                    # Process notification (could trigger additional workflows)
                    logger.debug(f"Processed state change notification: {notification['state_key']}")
                    
                except asyncio.TimeoutError:
                    continue
                
            except Exception as e:
                logger.error(f"Error processing change notifications: {e}")
                await asyncio.sleep(5)
    
    async def _performance_monitor(self):
        """Monitor state management performance"""
        while self._running:
            try:
                # Log performance metrics
                metrics = self.state_metrics
                logger.info(f"State Manager Performance: {metrics['total_operations']} operations, "
                          f"{metrics['average_operation_time']:.4f}s avg time, "
                          f"{metrics['state_size']} active states, "
                          f"{metrics['active_locks']} active locks")
                
                await asyncio.sleep(300)  # Report every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(600)
    
    async def get_state_manager_status(self) -> Dict[str, Any]:
        """Get comprehensive state manager status"""
        try:
            return {
                'state_manager_status': 'active' if self._running else 'inactive',
                'total_state_entries': len(self.state_entries),
                'state_history_size': sum(len(history) for history in self.state_history.values()),
                'active_locks': len(self.state_locks),
                'active_subscriptions': sum(len(subs) for subs in self.state_subscribers.values()),
                'snapshots': len(self.state_snapshots),
                'metrics': self.state_metrics,
                'performance': {
                    'average_operation_time': self.state_metrics['average_operation_time'],
                    'operations_per_second': self._calculate_ops_per_second(),
                    'lock_contention_rate': self._calculate_lock_contention_rate()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting state manager status: {e}")
            return {'error': str(e)}
    
    def _calculate_ops_per_second(self) -> float:
        """Calculate operations per second"""
        # Simplified calculation - in practice, would use time windows
        return self.state_metrics['total_operations'] / max(1, time.time())
    
    def _calculate_lock_contention_rate(self) -> float:
        """Calculate lock contention rate"""
        total_waiters = sum(len(waiters) for waiters in self.lock_waiters.values())
        return total_waiters / max(1, len(self.state_locks))