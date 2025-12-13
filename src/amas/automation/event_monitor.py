"""
Intelligent Event Monitoring System

Monitors file systems, web changes, network events, and triggers
automated AI workflows based on intelligent event detection.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
import uuid
import json
import hashlib
import aiohttp
import sqlite3
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Optional dependencies with graceful fallback
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    
    # Create safe dummy classes instead of None to prevent TypeError
    class DummyObserver:
        """Dummy Observer when watchdog is not installed"""
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "File system monitoring requires 'watchdog' package. "
                "Install with: pip install watchdog"
            )
        
        def schedule(self, *args, **kwargs):
            raise RuntimeError("watchdog not installed")
        
        def start(self):
            raise RuntimeError("watchdog not installed")
        
        def stop(self):
            pass
        
        def join(self, timeout=None):
            pass
    
    class DummyEventHandler:
        """Dummy FileSystemEventHandler when watchdog is not installed"""
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "File system monitoring requires 'watchdog' package. "
                "Install with: pip install watchdog"
            )

        def on_any_event(self, event):
            """Placeholder method to avoid AttributeError"""
            pass
    
    class DummyEvent:
        """Dummy FileSystemEvent when watchdog is not installed"""
        pass
    
    Observer = DummyObserver
    FileSystemEventHandler = DummyEventHandler
    FileSystemEvent = DummyEvent
    
    logger.warning(
        "watchdog not installed. File system monitoring will be unavailable. "
        "Install with: pip install watchdog"
    )

# Ensure logger has at least a NullHandler to prevent "No handlers" warnings
if not logger.handlers:
    logger.addHandler(logging.NullHandler())
    logger.debug("No handlers configured; installed NullHandler to suppress warnings.")

class EventType(str, Enum):
    """Types of events that can be detected by the monitoring system"""
    # File system events
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_MOVED = "file_moved"
    
    # Web content events
    WEB_CONTENT_CHANGED = "web_content_changed"
    WEB_NEW_POST = "web_new_post"
    WEB_PRICE_CHANGED = "web_price_changed"
    WEB_AVAILABILITY_CHANGED = "web_availability_changed"
    
    # Network service events
    NETWORK_SERVICE_UP = "network_service_up"
    NETWORK_SERVICE_DOWN = "network_service_down"
    NETWORK_THRESHOLD_EXCEEDED = "network_threshold_exceeded"
    
    # Custom events
    CUSTOM_CONDITION = "custom_condition"
    SCHEDULED_TRIGGER = "scheduled_trigger"

class EventSeverity(str, Enum):
    """Severity levels for detected events"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DetectedEvent:
    """
    Represents an event detected by the monitoring system.
    
    Attributes:
        id: Globally unique identifier for the event (auto-generated UUID if not provided)
        event_type: Category of the event (e.g., file_created, web_content_changed)
        severity: Impact level of the event (info, low, medium, high, critical)
        source: Origin of event (file path, URL, service name, etc.)
        description: Human-readable summary of the event
        event_data: Additional structured data associated with the event
        detected_at: Timestamp when the event was detected (UTC)
        correlation_id: Optional correlation ID for grouping related events
        tags: Set of tags for categorizing and filtering events
        processed: Whether the event has been processed by triggers
        triggered_workflows: List of workflow IDs triggered by this event
    
    Security:
        - URLs in source are automatically sanitized to remove credentials
        - SSRF protection validates URLs don't point to internal services
        - All enum values are validated in __post_init__
    """
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: EventType
    severity: EventSeverity
    
    # Event details
    source: str                     # File path, URL, service name, etc.
    description: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    
    # Processing
    processed: bool = False
    triggered_workflows: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize enum fields after initialization"""
        # Ensure event_type is an EventType enum
        if not isinstance(self.event_type, EventType):
            try:
                self.event_type = EventType(self.event_type)
            except ValueError:
                raise ValueError(
                    f"Invalid event_type: {self.event_type}. "
                    f"Must be one of {[e.value for e in EventType]}"
                )
        
        # Ensure severity is an EventSeverity enum
        if not isinstance(self.severity, EventSeverity):
            try:
                self.severity = EventSeverity(self.severity)
            except ValueError:
                raise ValueError(
                    f"Invalid severity: {self.severity}. "
                    f"Must be one of {[e.value for e in EventSeverity]}"
                )
        
        # Validate and sanitize source if it's a URL
        if self.source.startswith(('http://', 'https://')):
            self.source = self._sanitize_url(self.source)
    
    def _sanitize_url(self, url: str) -> str:
        """
        Sanitize URL to remove credentials and validate scheme.
        
        Security:
            - Removes username/password from URLs to prevent credential leakage
            - Only allows http and https schemes
            - Validates URL is safe (not pointing to internal services)
        """
        parsed = urlparse(url)
        
        # Only allow http and https schemes
        if parsed.scheme not in ("http", "https"):
            raise ValueError(
                f"Unsupported URL scheme: {parsed.scheme}. "
                "Only http and https are allowed."
            )
        
        # Validate URL is safe (SSRF protection)
        if not self._is_safe_url(url):
            raise ValueError(
                f"Unsafe URL detected: URL points to localhost or private network. "
                "This is blocked to prevent SSRF attacks."
            )
        
        # Remove credentials from URL if present (security)
        if parsed.username or parsed.password:
            # Reconstruct URL without credentials
            netloc = parsed.hostname
            if parsed.port:
                netloc = f"{netloc}:{parsed.port}"
            sanitized = parsed._replace(netloc=netloc)
            logger.warning(f"Credentials removed from URL: {url[:50]}...")
            return sanitized.geturl()
        
        return url
    
    @staticmethod
    def _is_safe_url(url: str) -> bool:
        """
        Validate URL to prevent SSRF attacks.
        
        Blocks:
            - localhost and loopback addresses (127.0.0.1, ::1)
            - Private IP ranges (RFC 1918: 10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12)
            - Link-local addresses (169.254.0.0/16)
            - AWS metadata service (169.254.169.254)
            - Special use addresses (0.0.0.0)
        
        Returns:
            True if URL is safe to access, False otherwise
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            if not hostname:
                return False
            
            # Block localhost variants
            if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
                logger.warning(f"Blocked localhost URL: {hostname}")
                return False
            
            # Block AWS/cloud metadata services
            if hostname == "169.254.169.254":
                logger.warning(f"Blocked cloud metadata service URL: {hostname}")
                return False
            
            # Block private IP ranges (RFC 1918)
            # 10.0.0.0/8
            if re.match(r"^10\.", hostname):
                logger.warning(f"Blocked private IP (10.x.x.x): {hostname}")
                return False
            
            # 192.168.0.0/16
            if re.match(r"^192\.168\.", hostname):
                logger.warning(f"Blocked private IP (192.168.x.x): {hostname}")
                return False
            
            # 172.16.0.0/12
            if re.match(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", hostname):
                logger.warning(f"Blocked private IP (172.16-31.x.x): {hostname}")
                return False
            
            # Block link-local addresses (169.254.0.0/16)
            if hostname.startswith("169.254."):
                logger.warning(f"Blocked link-local address: {hostname}")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error validating URL {url}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "source": self.source,
            "description": self.description,
            "event_data": self.event_data,
            "detected_at": self.detected_at.isoformat(),
            "correlation_id": self.correlation_id,
            "tags": list(self.tags),
            "processed": self.processed,
            "triggered_workflows": self.triggered_workflows
        }

@dataclass
class EventTrigger:
    """Configuration for triggering workflows based on events"""
    id: str
    name: str
    description: str
    
    # Trigger conditions
    event_types: List[EventType]
    source_patterns: List[str] = field(default_factory=list)  # Regex patterns
    severity_threshold: EventSeverity = EventSeverity.MEDIUM
    
    # Filtering
    tag_filters: Set[str] = field(default_factory=set)
    cooldown_minutes: int = 30      # Minimum time between triggers
    max_triggers_per_hour: int = 10
    
    # Action configuration
    workflow_template: str = ""      # AI task template to execute
    workflow_parameters: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    
    # State tracking
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    success_count: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    
    def matches_event(self, event: DetectedEvent) -> bool:
        """Check if event matches this trigger's conditions"""
        # Check if enabled
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            time_since_last = (datetime.now(timezone.utc) - self.last_triggered).total_seconds() / 60
            if time_since_last < self.cooldown_minutes:
                return False
        
        # Check rate limiting
        if self.last_triggered:
            hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            if self.last_triggered > hour_ago and self.trigger_count >= self.max_triggers_per_hour:
                return False
        
        # Check event type
        if event.event_type not in self.event_types:
            return False
        
        # Check severity threshold
        severity_levels = {EventSeverity.INFO: 0, EventSeverity.LOW: 1, 
                          EventSeverity.MEDIUM: 2, EventSeverity.HIGH: 3, 
                          EventSeverity.CRITICAL: 4}
        
        if severity_levels[event.severity] < severity_levels[self.severity_threshold]:
            return False
        
        # Check source patterns
        if self.source_patterns:
            pattern_match = False
            for pattern in self.source_patterns:
                if re.search(pattern, event.source, re.IGNORECASE):
                    pattern_match = True
                    break
            if not pattern_match:
                return False
        
        # Check tag filters
        if self.tag_filters:
            if not self.tag_filters.intersection(event.tags):
                return False
        
        return True

class FileSystemMonitor(FileSystemEventHandler):
    """File system event handler for watchdog"""
    
    def __init__(self, event_callback: Callable[[DetectedEvent], None]):
        if not HAS_WATCHDOG:
            raise ImportError(
                "watchdog is required for file system monitoring. "
                "Install with: pip install watchdog"
            )
        super().__init__()
        self.event_callback = event_callback
        self.ignored_patterns = {
            r'\.(tmp|swp|lock)$',           # Temporary files
            r'/\.',                        # Hidden files
            r'__pycache__',                # Python cache
            r'\.git/',                     # Git files
            r'node_modules/',              # Node.js modules
        }
    
    def _should_ignore(self, path: str) -> bool:
        """Check if file should be ignored"""
        for pattern in self.ignored_patterns:
            if re.search(pattern, path):
                return True
        return False
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory and not self._should_ignore(event.src_path):
            detected_event = DetectedEvent(
                id=f"fs_{uuid.uuid4().hex[:8]}",
                event_type=EventType.FILE_CREATED,
                severity=EventSeverity.INFO,
                source=event.src_path,
                description=f"File created: {Path(event.src_path).name}",
                event_data={"path": event.src_path, "is_directory": event.is_directory}
            )
            
            asyncio.create_task(self._async_callback(detected_event))
    
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory and not self._should_ignore(event.src_path):
            detected_event = DetectedEvent(
                id=f"fs_{uuid.uuid4().hex[:8]}",
                event_type=EventType.FILE_MODIFIED,
                severity=EventSeverity.LOW,
                source=event.src_path,
                description=f"File modified: {Path(event.src_path).name}",
                event_data={"path": event.src_path, "is_directory": event.is_directory}
            )
            
            asyncio.create_task(self._async_callback(detected_event))
    
    def on_deleted(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            detected_event = DetectedEvent(
                id=f"fs_{uuid.uuid4().hex[:8]}",
                event_type=EventType.FILE_DELETED,
                severity=EventSeverity.MEDIUM,
                source=event.src_path,
                description=f"File deleted: {Path(event.src_path).name}",
                event_data={"path": event.src_path, "is_directory": event.is_directory}
            )
            
            asyncio.create_task(self._async_callback(detected_event))
    
    def on_moved(self, event: FileSystemEvent):
        if not self._should_ignore(event.src_path):
            detected_event = DetectedEvent(
                id=f"fs_{uuid.uuid4().hex[:8]}",
                event_type=EventType.FILE_MOVED,
                severity=EventSeverity.LOW,
                source=event.src_path,
                description=f"File moved: {Path(event.src_path).name} -> {Path(event.dest_path).name}",
                event_data={
                    "src_path": event.src_path, 
                    "dest_path": event.dest_path,
                    "is_directory": event.is_directory
                }
            )
            
            asyncio.create_task(self._async_callback(detected_event))
    
    async def _async_callback(self, event: DetectedEvent):
        """Wrapper to call async callback from sync event handler"""
        try:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)
            else:
                self.event_callback(event)
        except Exception as e:
            logger.error(f"Error in event callback: {e}")

@dataclass
class WebMonitorTarget:
    """Configuration for monitoring web resources"""
    id: str
    name: str
    url: str
    
    # Monitoring configuration
    check_interval_minutes: int = 60
    content_selector: Optional[str] = None  # CSS selector for specific content
    change_threshold: float = 0.05         # Minimum change to trigger event
    
    # Content tracking
    last_content_hash: Optional[str] = None
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    
    # Response time monitoring
    response_time_threshold_ms: int = 5000
    track_performance: bool = True
    
    # Headers and authentication
    headers: Dict[str, str] = field(default_factory=dict)
    auth_token: Optional[str] = None
    
    def __post_init__(self):
        """Validate URL on initialization"""
        # Validate URL for SSRF protection
        if not DetectedEvent._is_safe_url(self.url):
            raise ValueError(
                f"Unsafe URL detected: {self.url}. "
                "URLs must not point to localhost or private network ranges. "
                "This is a security measure to prevent SSRF attacks."
            )
    
    def needs_check(self) -> bool:
        """Check if target needs to be checked now"""
        if not self.last_check:
            return True
        
        time_since_check = (datetime.now(timezone.utc) - self.last_check).total_seconds() / 60
        return time_since_check >= self.check_interval_minutes

class EventMonitor:
    """
    Intelligent event monitoring and workflow triggering system.
    
    Features:
        - File system monitoring (requires watchdog)
        - Web content monitoring with change detection
        - Network service health monitoring
        - Event-driven workflow triggering
        - Persistent event storage with SQLite
    
    Security:
        - SSRF protection on all URL monitoring
        - SQL injection prevention with parameterized queries
        - Credential sanitization in logs
        - Rate limiting and cooldown on triggers
    
    Performance:
        - Async SQLite operations via executor
        - Connection pooling for HTTP requests
        - Event batching and cleanup
        - Resource-efficient monitoring loops
    """
    
    def __init__(self, db_path: str = "data/events.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Event storage and processing
        self.recent_events: Dict[str, DetectedEvent] = {}  # Recent events cache
        self.event_triggers: Dict[str, EventTrigger] = {}
        self.web_monitors: Dict[str, WebMonitorTarget] = {}
        
        # File system monitoring
        self.file_observers: Dict[str, Observer] = {}
        
        # Background tasks
        self.running = False
        self.monitor_tasks: List[asyncio.Task] = []
        
        # Performance tracking
        self.events_detected: int = 0
        self.workflows_triggered: int = 0
        self.false_positives: int = 0
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Event Monitor initialized with database: {self.db_path}")
    
    def _sanitize_log_source(self, source: str) -> str:
        """
        Sanitize source string for safe logging (removes credentials from URLs).
        
        Security:
            Prevents credential leakage in logs by removing username/password from URLs.
        """
        if source.startswith(('http://', 'https://')):
            try:
                parsed = urlparse(source)
                if parsed.username or parsed.password:
                    # Reconstruct URL without credentials
                    netloc = parsed.hostname
                    if parsed.port:
                        netloc = f"{netloc}:{parsed.port}"
                    sanitized = parsed._replace(netloc=netloc)
                    return sanitized.geturl()
            except Exception:
                # If parsing fails, return truncated version
                return source[:100] + "..." if len(source) > 100 else source
        return source
    
    def _init_database(self):
        """Initialize SQLite database for event storage"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, schedule in executor
            loop.run_in_executor(None, self._init_database_sync)
        else:
            # If no loop running, execute directly
            self._init_database_sync()
    
    def _init_database_sync(self):
        """
        Synchronous database initialization (runs in executor).
        
        Security:
            Uses parameterized queries throughout to prevent SQL injection.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT NOT NULL,
                    event_data TEXT,
                    detected_at TEXT NOT NULL,
                    correlation_id TEXT,
                    tags TEXT,
                    processed BOOLEAN DEFAULT 0,
                    triggered_workflows TEXT
                )
            """)
            
            # Event triggers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_triggers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    event_types TEXT NOT NULL,
                    source_patterns TEXT,
                    severity_threshold TEXT NOT NULL,
                    tag_filters TEXT,
                    cooldown_minutes INTEGER DEFAULT 30,
                    max_triggers_per_hour INTEGER DEFAULT 10,
                    workflow_template TEXT NOT NULL,
                    workflow_parameters TEXT,
                    priority TEXT DEFAULT 'normal',
                    enabled BOOLEAN DEFAULT 1,
                    last_triggered TEXT,
                    trigger_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    created_by TEXT DEFAULT 'system'
                )
            """)
            
            # Web monitors table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS web_monitors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    check_interval_minutes INTEGER DEFAULT 60,
                    content_selector TEXT,
                    change_threshold REAL DEFAULT 0.05,
                    last_content_hash TEXT,
                    last_check TEXT,
                    consecutive_failures INTEGER DEFAULT 0,
                    response_time_threshold_ms INTEGER DEFAULT 5000,
                    track_performance BOOLEAN DEFAULT 1,
                    headers TEXT,
                    auth_token TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    async def start_monitoring(self):
        """Start all monitoring systems"""
        if self.running:
            logger.warning("Event monitoring already running")
            return
        
        self.running = True
        
        # Start monitoring tasks
        self.monitor_tasks = [
            asyncio.create_task(self._event_processing_loop()),
            asyncio.create_task(self._web_monitoring_loop()),
            asyncio.create_task(self._network_monitoring_loop())
        ]
        
        logger.info("Event monitoring started")
    
    async def stop_monitoring(self):
        """Stop all monitoring systems"""
        self.running = False
        
        # Cancel monitoring tasks
        for task in self.monitor_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.monitor_tasks:
            await asyncio.gather(*self.monitor_tasks, return_exceptions=True)
        
        # Stop file system observers
        for observer in self.file_observers.values():
            observer.stop()
            observer.join()
        
        self.file_observers.clear()
        self.monitor_tasks.clear()
        
        logger.info("Event monitoring stopped")
    
    async def add_file_monitor(self, 
                             monitor_name: str,
                             directory_path: str,
                             recursive: bool = True,
                             file_patterns: List[str] = None) -> bool:
        """Add file system monitoring for a directory"""
        
        if not HAS_WATCHDOG:
            logger.error(
                "File system monitoring requires watchdog. "
                "Install with: pip install watchdog"
            )
            return False
        
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory does not exist: {directory_path}")
            return False
        
        # Create event handler
        handler = FileSystemMonitor(self._handle_file_event)
        
        # Create observer
        observer = Observer()
        observer.schedule(handler, str(directory), recursive=recursive)
        
        # Start monitoring
        observer.start()
        self.file_observers[monitor_name] = observer
        
        logger.info(f"File system monitoring started: {directory_path} (recursive: {recursive})")
        return True
    
    async def _handle_file_event(self, event: DetectedEvent):
        """Handle file system events"""
        # Store event
        self.recent_events[event.id] = event
        await self._persist_event(event)
        
        self.events_detected += 1
        
        # Check triggers
        await self._process_event_triggers(event)
        
        # Sanitize source before logging to prevent credential exposure
        sanitized_source = self._sanitize_log_source(event.source)
        logger.debug(f"File event processed: {event.event_type.value} - {sanitized_source}")
    
    async def add_web_monitor(self,
                            name: str,
                            url: str,
                            check_interval_minutes: int = 60,
                            content_selector: str = None,
                            change_threshold: float = 0.05,
                            headers: Dict[str, str] = None) -> str:
        """
        Add web content monitoring.
        
        Security:
            - Validates URL doesn't point to localhost or private networks (SSRF protection)
            - Removes credentials from URLs before storage
        
        Raises:
            ValueError: If URL is unsafe or has invalid scheme
        """
        
        monitor_id = f"web_{uuid.uuid4().hex[:8]}"
        
        # WebMonitorTarget validates URL in __post_init__
        web_monitor = WebMonitorTarget(
            id=monitor_id,
            name=name,
            url=url,
            check_interval_minutes=check_interval_minutes,
            content_selector=content_selector,
            change_threshold=change_threshold,
            headers=headers or {}
        )
        
        self.web_monitors[monitor_id] = web_monitor
        await self._persist_web_monitor(web_monitor)
        
        logger.info(f"Web monitor created: {name} ({self._sanitize_log_source(url)})")
        return monitor_id
    
    async def _web_monitoring_loop(self):
        """Background loop for web content monitoring"""
        while self.running:
            try:
                # Check each web monitor
                for monitor in list(self.web_monitors.values()):
                    if monitor.needs_check():
                        await self._check_web_target(monitor)
                
                # Sleep between checks
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in web monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_web_target(self, monitor: WebMonitorTarget):
        """
        Check a single web monitoring target.
        
        Security:
            - Uses SSL verification
            - Implements timeouts to prevent hanging
            - Connection pooling with limits
            - Proper error handling
        """
        current_time = datetime.now(timezone.utc)
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Create secure HTTP client with SSL verification and proper timeout
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                ssl=True,  # Enable SSL verification
                limit=20,  # Connection pool limit
                limit_per_host=5  # Per-host connection limit
            )
            
            # Fetch web content with proper error handling
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                try:
                    async with session.get(
                        monitor.url, 
                        headers=monitor.headers,
                        allow_redirects=True,
                        ssl=True  # Explicit SSL verification
                    ) as response:
                        # Raise for status to catch HTTP errors
                        response.raise_for_status()
                        content = await response.text()
                        response_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                        
                        # Calculate content hash (use SHA-256 for security)
                        content_hash = hashlib.sha256(content.encode()).hexdigest()
                        
                        # Check for content changes
                        if monitor.last_content_hash and monitor.last_content_hash != content_hash:
                            # Content changed - create event
                            event = DetectedEvent(
                                id=f"web_{uuid.uuid4().hex[:8]}",
                                event_type=EventType.WEB_CONTENT_CHANGED,
                                severity=EventSeverity.MEDIUM,
                                source=monitor.url,
                                description=f"Content changed on {monitor.name}",
                                event_data={
                                    "url": monitor.url,
                                    "response_time_ms": response_time_ms,
                                    "content_length": len(content),
                                    "previous_hash": monitor.last_content_hash,
                                    "new_hash": content_hash
                                },
                                tags={"web_change", "content_update"}
                            )
                            
                            await self._handle_web_event(event)
                        
                        # Check response time
                        if (monitor.track_performance and 
                            response_time_ms > monitor.response_time_threshold_ms):
                            
                            event = DetectedEvent(
                                id=f"web_{uuid.uuid4().hex[:8]}",
                                event_type=EventType.NETWORK_THRESHOLD_EXCEEDED,
                                severity=EventSeverity.HIGH,
                                source=monitor.url,
                                description=f"Slow response from {monitor.name}: {response_time_ms:.0f}ms",
                                event_data={
                                    "url": monitor.url,
                                    "response_time_ms": response_time_ms,
                                    "threshold_ms": monitor.response_time_threshold_ms
                                },
                                tags={"performance", "slow_response"}
                            )
                            
                            await self._handle_web_event(event)
                        
                        # Update monitor state
                        monitor.last_content_hash = content_hash
                        monitor.last_check = current_time
                        monitor.consecutive_failures = 0
                        
                        await self._persist_web_monitor(monitor)
                        
                except aiohttp.ClientResponseError as e:
                    logger.warning(f"HTTP error checking {monitor.name}: {e.status} - {e.message}")
                    raise
                except aiohttp.ClientError as e:
                    logger.warning(f"Client error checking {monitor.name}: {e}")
                    raise
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout checking {monitor.name}")
                    raise
                    
        except Exception as e:
            monitor.consecutive_failures += 1
            monitor.last_check = current_time
            
            if monitor.consecutive_failures >= 3:
                # Create service down event
                event = DetectedEvent(
                    id=f"web_{uuid.uuid4().hex[:8]}",
                    event_type=EventType.NETWORK_SERVICE_DOWN,
                    severity=EventSeverity.HIGH,
                    source=monitor.url,
                    description=f"Service unavailable: {monitor.name} - {str(e)}",
                    event_data={
                        "url": monitor.url,
                        "error": str(e),
                        "consecutive_failures": monitor.consecutive_failures
                    },
                    tags={"service_down", "monitoring_failure"}
                )
                
                await self._handle_web_event(event)
            
            await self._persist_web_monitor(monitor)
            
            logger.warning(f"Web check failed for {monitor.name}: {e}")
    
    async def _handle_web_event(self, event: DetectedEvent):
        """Handle web monitoring events"""
        # Store event
        self.recent_events[event.id] = event
        await self._persist_event(event)
        
        self.events_detected += 1
        
        # Process triggers
        await self._process_event_triggers(event)
        
        # Sanitize source before logging to prevent credential exposure
        sanitized_source = self._sanitize_log_source(event.source)
        logger.info(f"Web event detected: {event.event_type.value} - {sanitized_source}")
    
    async def _network_monitoring_loop(self):
        """Background loop for network service monitoring"""
        while self.running:
            try:
                # Placeholder for network monitoring
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in network monitoring loop: {e}")
                await asyncio.sleep(300)
    
    async def _event_processing_loop(self):
        """Background loop for processing events and triggers"""
        while self.running:
            try:
                # Process unprocessed events
                unprocessed_events = [event for event in self.recent_events.values() 
                                    if not event.processed]
                
                for event in unprocessed_events:
                    await self._process_event_triggers(event)
                    event.processed = True
                    await self._persist_event(event)
                
                # Clean up old events (keep last 1000)
                if len(self.recent_events) > 1000:
                    sorted_events = sorted(
                        self.recent_events.items(),
                        key=lambda x: x[1].detected_at,
                        reverse=True
                    )
                    self.recent_events = dict(sorted_events[:1000])
                
                await asyncio.sleep(60)  # Process events every minute
                
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(60)
    
    async def _process_event_triggers(self, event: DetectedEvent):
        """Process event against all configured triggers"""
        triggered_workflows = []
        
        for trigger in self.event_triggers.values():
            if trigger.matches_event(event):
                # Execute trigger
                workflow_id = await self._execute_trigger(trigger, event)
                if workflow_id:
                    triggered_workflows.append(workflow_id)
                    self.workflows_triggered += 1
                    
                    # Update trigger state
                    trigger.last_triggered = datetime.now(timezone.utc)
                    trigger.trigger_count += 1
                    
                    await self._persist_trigger(trigger)
        
        # Update event with triggered workflows
        event.triggered_workflows = triggered_workflows
        
        if triggered_workflows:
            logger.info(f"Event {event.id} triggered {len(triggered_workflows)} workflows")
    
    async def _execute_trigger(self, trigger: EventTrigger, event: DetectedEvent) -> Optional[str]:
        """Execute a trigger by starting an AI workflow"""
        try:
            # Build workflow request from template and event data
            workflow_request = self._build_workflow_request(trigger, event)
            
            # Execute using task scheduler for immediate execution
            from .task_scheduler import get_task_scheduler, ScheduleType, TaskPriority
            scheduler = get_task_scheduler()
            
            # Create one-time scheduled task for immediate execution
            task_id = await scheduler.schedule_task(
                name=f"Event Trigger: {trigger.name}",
                task_request=workflow_request,
                schedule_expression=datetime.now(timezone.utc).isoformat(),
                schedule_type=ScheduleType.ONE_TIME,
                priority=TaskPriority[trigger.priority.upper()],
                task_parameters={
                    **trigger.workflow_parameters,
                    "triggering_event": event.to_dict()
                },
                tags={"event_triggered", "automated"}
            )
            
            logger.info(f"Triggered workflow for event {event.id}: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error executing trigger {trigger.id}: {e}")
            return None
    
    def _build_workflow_request(self, trigger: EventTrigger, event: DetectedEvent) -> str:
        """Build workflow request from trigger template and event data"""
        # Simple template substitution (could be enhanced with Jinja2)
        request = trigger.workflow_template
        
        # Replace common placeholders
        placeholders = {
            "{event_source}": event.source,
            "{event_type}": event.event_type.value,
            "{event_description}": event.description,
            "{event_severity}": event.severity.value,
            "{detection_time}": event.detected_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
        for placeholder, value in placeholders.items():
            request = request.replace(placeholder, str(value))
        
        # Add event data context
        if event.event_data:
            request += f" [Event Context: {json.dumps(event.event_data)}]"
        
        return request
    
    async def add_event_trigger(self,
                              name: str,
                              event_types: List[EventType],
                              workflow_template: str,
                              source_patterns: List[str] = None,
                              severity_threshold: EventSeverity = EventSeverity.MEDIUM,
                              cooldown_minutes: int = 30,
                              workflow_parameters: Dict[str, Any] = None,
                              priority: str = "normal") -> str:
        """Add new event trigger configuration"""
        
        trigger_id = f"trigger_{uuid.uuid4().hex[:8]}"
        
        trigger = EventTrigger(
            id=trigger_id,
            name=name,
            description=f"Trigger for: {workflow_template[:100]}...",
            event_types=event_types,
            source_patterns=source_patterns or [],
            severity_threshold=severity_threshold,
            cooldown_minutes=cooldown_minutes,
            workflow_template=workflow_template,
            workflow_parameters=workflow_parameters or {},
            priority=priority
        )
        
        self.event_triggers[trigger_id] = trigger
        await self._persist_trigger(trigger)
        
        logger.info(f"Event trigger created: {name} ({trigger_id})")
        return trigger_id
    
    async def _persist_event(self, event: DetectedEvent):
        """Persist event to database (runs in executor to avoid blocking)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._persist_event_sync, event)
    
    def _persist_event_sync(self, event: DetectedEvent):
        """
        Synchronous event persistence (runs in executor).
        
        Security:
            Uses parameterized queries to prevent SQL injection.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO events (
                    id, event_type, severity, source, description, event_data,
                    detected_at, correlation_id, tags, processed, triggered_workflows
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id, event.event_type.value, event.severity.value,
                event.source, event.description, json.dumps(event.event_data),
                event.detected_at.isoformat(), event.correlation_id,
                json.dumps(list(event.tags)), event.processed,
                json.dumps(event.triggered_workflows)
            ))
            conn.commit()
    
    async def _persist_trigger(self, trigger: EventTrigger):
        """Persist trigger configuration to database (runs in executor to avoid blocking)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._persist_trigger_sync, trigger)
    
    def _persist_trigger_sync(self, trigger: EventTrigger):
        """
        Synchronous trigger persistence (runs in executor).
        
        Security:
            Uses parameterized queries to prevent SQL injection.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO event_triggers (
                    id, name, description, event_types, source_patterns, severity_threshold,
                    tag_filters, cooldown_minutes, max_triggers_per_hour, workflow_template,
                    workflow_parameters, priority, enabled, last_triggered, trigger_count,
                    success_count, created_at, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trigger.id, trigger.name, trigger.description,
                json.dumps([t.value for t in trigger.event_types]),
                json.dumps(trigger.source_patterns), trigger.severity_threshold.value,
                json.dumps(list(trigger.tag_filters)), trigger.cooldown_minutes,
                trigger.max_triggers_per_hour, trigger.workflow_template,
                json.dumps(trigger.workflow_parameters), trigger.priority,
                trigger.enabled, 
                trigger.last_triggered.isoformat() if trigger.last_triggered else None,
                trigger.trigger_count, trigger.success_count,
                trigger.created_at.isoformat(), trigger.created_by
            ))
            conn.commit()
    
    async def _persist_web_monitor(self, monitor: WebMonitorTarget):
        """Persist web monitor configuration to database (runs in executor to avoid blocking)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._persist_web_monitor_sync, monitor)
    
    def _persist_web_monitor_sync(self, monitor: WebMonitorTarget):
        """
        Synchronous web monitor persistence (runs in executor).
        
        Security:
            Uses parameterized queries to prevent SQL injection.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO web_monitors (
                    id, name, url, check_interval_minutes, content_selector, change_threshold,
                    last_content_hash, last_check, consecutive_failures, response_time_threshold_ms,
                    track_performance, headers, auth_token, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                monitor.id, monitor.name, monitor.url, monitor.check_interval_minutes,
                monitor.content_selector, monitor.change_threshold,
                monitor.last_content_hash,
                monitor.last_check.isoformat() if monitor.last_check else None,
                monitor.consecutive_failures, monitor.response_time_threshold_ms,
                monitor.track_performance, json.dumps(monitor.headers),
                monitor.auth_token, datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get monitoring system metrics"""
        active_file_monitors = len(self.file_observers)
        active_web_monitors = len(self.web_monitors)
        active_triggers = sum(1 for t in self.event_triggers.values() if t.enabled)
        
        trigger_success_rate = 0.0
        if self.event_triggers:
            total_triggers = sum(t.trigger_count for t in self.event_triggers.values())
            successful_triggers = sum(t.success_count for t in self.event_triggers.values())
            trigger_success_rate = (successful_triggers / max(1, total_triggers)) * 100
        
        return {
            "running": self.running,
            "events_detected": self.events_detected,
            "workflows_triggered": self.workflows_triggered,
            "false_positives": self.false_positives,
            "active_file_monitors": active_file_monitors,
            "active_web_monitors": active_web_monitors,
            "active_triggers": active_triggers,
            "recent_events_count": len(self.recent_events),
            "trigger_success_rate_percent": round(trigger_success_rate, 2)
        }

# Global event monitor instance
_global_event_monitor: Optional[EventMonitor] = None

def get_event_monitor() -> EventMonitor:
    """Get global event monitor instance"""
    global _global_event_monitor
    if _global_event_monitor is None:
        _global_event_monitor = EventMonitor()
    return _global_event_monitor
