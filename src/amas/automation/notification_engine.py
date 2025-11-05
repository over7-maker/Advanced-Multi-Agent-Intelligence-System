"""
Smart Notification Engine

Provides context-aware notifications across multiple channels with
intelligent batching, personalization, and delivery optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sqlite3
import jinja2

logger = logging.getLogger(__name__)

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"

class NotificationPriority(str, Enum):
    LOW = "low"                      # Batched notifications
    NORMAL = "normal"                # Standard delivery
    HIGH = "high"                    # Immediate delivery
    URGENT = "urgent"                # Multi-channel delivery
    CRITICAL = "critical"            # All channels + escalation

class NotificationStatus(str, Enum):
    PENDING = "pending"
    BATCHED = "batched"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class NotificationTemplate:
    """Template for notification content generation"""
    id: str
    name: str
    notification_type: str
    
    # Template content
    subject_template: str
    body_template: str
    
    # Channel-specific templates
    channel_templates: Dict[NotificationChannel, Dict[str, str]] = field(default_factory=dict)
    
    # Template metadata
    variables: List[str] = field(default_factory=list)
    supports_html: bool = True
    supports_markdown: bool = True
    
    def render_content(self, 
                      channel: NotificationChannel,
                      data: Dict[str, Any],
                      format_type: str = "html") -> Dict[str, str]:
        """Render template with provided data"""
        env = jinja2.Environment()
        
        # Get channel-specific template or fall back to default
        if channel in self.channel_templates:
            subject_template = self.channel_templates[channel].get("subject", self.subject_template)
            body_template = self.channel_templates[channel].get("body", self.body_template)
        else:
            subject_template = self.subject_template
            body_template = self.body_template
        
        try:
            # Render templates
            subject = env.from_string(subject_template).render(data)
            body = env.from_string(body_template).render(data)
            
            return {"subject": subject, "body": body}
            
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return {
                "subject": f"Notification: {self.name}",
                "body": f"Error rendering template: {str(e)}"
            }

@dataclass
class NotificationChannel:
    """Configuration for a notification delivery channel"""
    id: str
    channel_type: NotificationChannel
    name: str
    
    # Channel configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Delivery settings
    enabled: bool = True
    rate_limit_per_hour: int = 100
    batch_size: int = 10
    batch_delay_minutes: int = 15
    
    # Performance tracking
    messages_sent: int = 0
    delivery_success_rate: float = 0.95
    avg_delivery_time_ms: float = 1000.0
    
    # Error handling
    retry_count: int = 3
    retry_delay_seconds: int = 60
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    
    def is_healthy(self) -> bool:
        """Check if channel is healthy for delivery"""
        if not self.enabled:
            return False
        
        # Check recent failure rate
        if self.last_failure:
            time_since_failure = (datetime.now(timezone.utc) - self.last_failure).total_seconds()
            if time_since_failure < 300 and self.failure_count >= 3:  # 5 minutes, 3+ failures
                return False
        
        return self.delivery_success_rate >= 0.70  # 70% minimum success rate

@dataclass
class NotificationMessage:
    """Individual notification message"""
    id: str
    notification_type: str
    priority: NotificationPriority
    
    # Recipient and channel
    channels: List[NotificationChannel]
    recipient_data: Dict[str, Any] = field(default_factory=dict)
    
    # Content
    subject: str = ""
    body: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Delivery tracking
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_for: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    # Delivery results
    delivery_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    # Context
    correlation_id: Optional[str] = None
    source_workflow_id: Optional[str] = None
    source_task_id: Optional[str] = None
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if notification has expired"""
        age_hours = (datetime.now(timezone.utc) - self.created_at).total_seconds() / 3600
        return age_hours > max_age_hours
    
    def should_deliver_now(self) -> bool:
        """Check if notification should be delivered immediately"""
        if self.status != NotificationStatus.PENDING:
            return False
        
        # High priority notifications deliver immediately
        if self.priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
            return True
        
        # Check if scheduled time has arrived
        if self.scheduled_for:
            return datetime.now(timezone.utc) >= self.scheduled_for
        
        # Normal and low priority can be batched
        return False

class NotificationEngine:
    """Smart notification delivery system"""
    
    def __init__(self, db_path: str = "data/notifications.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Notification storage
        self.pending_notifications: Dict[str, NotificationMessage] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        
        # Batching system
        self.batch_queues: Dict[str, List[str]] = {}  # channel_id -> notification_ids
        self.batch_timers: Dict[str, asyncio.Task] = {}
        
        # Background processing
        self.running = False
        self.processor_tasks: List[asyncio.Task] = []
        
        # Performance metrics
        self.total_notifications: int = 0
        self.successful_deliveries: int = 0
        self.failed_deliveries: int = 0
        
        # Initialize database and templates
        self._init_database()
        asyncio.create_task(self._load_default_templates())
        
        logger.info(f"Notification Engine initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize notification database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    notification_type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    channels TEXT NOT NULL,  -- JSON list
                    recipient_data TEXT,  -- JSON
                    subject TEXT,
                    body TEXT,
                    data TEXT,  -- JSON
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    scheduled_for TEXT,
                    delivered_at TEXT,
                    delivery_results TEXT,  -- JSON
                    delivery_attempts INTEGER DEFAULT 0,
                    correlation_id TEXT,
                    source_workflow_id TEXT,
                    source_task_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_channels (
                    id TEXT PRIMARY KEY,
                    channel_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,  -- JSON
                    enabled BOOLEAN DEFAULT 1,
                    rate_limit_per_hour INTEGER DEFAULT 100,
                    batch_size INTEGER DEFAULT 10,
                    batch_delay_minutes INTEGER DEFAULT 15,
                    messages_sent INTEGER DEFAULT 0,
                    delivery_success_rate REAL DEFAULT 0.95,
                    avg_delivery_time_ms REAL DEFAULT 1000.0,
                    retry_count INTEGER DEFAULT 3,
                    failure_count INTEGER DEFAULT 0,
                    last_failure TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    async def _load_default_templates(self):
        """Load default notification templates"""
        default_templates = [
            NotificationTemplate(
                id="scheduled_task_result",
                name="Scheduled Task Result",
                notification_type="scheduled_task_result",
                subject_template="Scheduled Task {{ 'Completed' if success else 'Failed' }}: {{ task_name }}",
                body_template="""
Your scheduled task has {{ 'completed successfully' if success else 'failed' }}.

Task: {{ task_name }}
Execution Time: {{ execution_time_formatted }}
{% if success %}
Workflow ID: {{ workflow_id }}
{% else %}
Error: {{ error_details }}
{% endif %}

View details in your dashboard.
                """,
                channel_templates={
                    NotificationChannel.SLACK: {
                        "subject": "Task {{ 'Success' if success else 'Failure' }}: {{ task_name }}",
                        "body": """
:{{ 'white_check_mark' if success else 'x' }}: *{{ task_name }}*

{{ 'Completed successfully' if success else 'Failed' }} in {{ execution_time_formatted }}

{% if success %}
:information_source: Workflow: `{{ workflow_id }}`
{% else %}
:warning: Error: {{ error_details }}
{% endif %}
                        """
                    }
                },
                variables=["task_name", "success", "execution_time_formatted", "workflow_id", "error_details"]
            ),
            
            NotificationTemplate(
                id="web_content_changed",
                name="Web Content Changed",
                notification_type="web_content_changed",
                subject_template="Content Update Detected: {{ source_name }}",
                body_template="""
A change has been detected on {{ source_name }}.

URL: {{ url }}
Detected: {{ detection_time }}
Change Type: {{ change_type }}

{% if analysis_summary %}
Analysis: {{ analysis_summary }}
{% endif %}

Automatic analysis workflow has been triggered.
                """,
                variables=["source_name", "url", "detection_time", "change_type", "analysis_summary"]
            ),
            
            NotificationTemplate(
                id="agent_coordination_alert",
                name="Agent Coordination Alert",
                notification_type="agent_coordination_alert",
                subject_template="Agent System Alert: {{ alert_type }}",
                body_template="""
Agent coordination system alert:

Alert Type: {{ alert_type }}
Severity: {{ severity }}
Affected Agents: {{ affected_agents_count }}

Details:
{{ alert_details }}

{% if recommended_actions %}
Recommended Actions:
{% for action in recommended_actions %}
- {{ action }}
{% endfor %}
{% endif %}

Timestamp: {{ alert_time }}
                """,
                variables=["alert_type", "severity", "affected_agents_count", "alert_details", "recommended_actions", "alert_time"]
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
        
        logger.info(f"Loaded {len(default_templates)} default notification templates")
    
    async def add_notification_channel(self,
                                     channel_type: NotificationChannel,
                                     name: str,
                                     config: Dict[str, Any],
                                     rate_limit_per_hour: int = 100,
                                     batch_size: int = 10) -> str:
        """Add a new notification delivery channel"""
        
        channel_id = f"{channel_type.value}_{uuid.uuid4().hex[:8]}"
        
        channel = NotificationChannel(
            id=channel_id,
            channel_type=channel_type,
            name=name,
            config=config,
            rate_limit_per_hour=rate_limit_per_hour,
            batch_size=batch_size
        )
        
        self.notification_channels[channel_id] = channel
        await self._persist_channel(channel)
        
        logger.info(f"Notification channel added: {name} ({channel_type.value})")
        return channel_id
    
    async def send_notification(self,
                              notification_type: str,
                              data: Dict[str, Any],
                              channels: List[str],
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              recipient_data: Dict[str, Any] = None,
                              correlation_id: str = None) -> str:
        """Send notification through specified channels"""
        
        # Create notification message
        notification_id = f"notif_{uuid.uuid4().hex[:8]}"
        
        # Get template
        template = self.templates.get(notification_type)
        if not template:
            logger.warning(f"No template found for notification type: {notification_type}")
            template = self._create_default_template(notification_type)
        
        # Render content for first channel (for storage)
        if channels:
            first_channel_type = NotificationChannel.EMAIL  # Default
            for channel_id in channels:
                channel = self.notification_channels.get(channel_id)
                if channel:
                    first_channel_type = channel.channel_type
                    break
            
            rendered_content = template.render_content(first_channel_type, data)
        else:
            rendered_content = {"subject": "Notification", "body": "No content"}
        
        notification = NotificationMessage(
            id=notification_id,
            notification_type=notification_type,
            priority=priority,
            channels=channels,
            recipient_data=recipient_data or {},
            subject=rendered_content["subject"],
            body=rendered_content["body"],
            data=data,
            correlation_id=correlation_id
        )
        
        # Determine delivery strategy based on priority
        if priority in [NotificationPriority.HIGH, NotificationPriority.URGENT, NotificationPriority.CRITICAL]:
            # Immediate delivery
            notification.scheduled_for = datetime.now(timezone.utc)
        else:
            # Batch for later delivery
            notification.status = NotificationStatus.BATCHED
            notification.scheduled_for = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        self.pending_notifications[notification_id] = notification
        await self._persist_notification(notification)
        
        self.total_notifications += 1
        
        # Queue for delivery
        if notification.should_deliver_now():
            asyncio.create_task(self._deliver_notification(notification_id))
        else:
            await self._add_to_batch_queue(notification_id, channels)
        
        logger.info(f"Notification queued: {notification_id} ({notification_type}, priority: {priority.value})")
        return notification_id
    
    def _create_default_template(self, notification_type: str) -> NotificationTemplate:
        """Create default template for unknown notification type"""
        return NotificationTemplate(
            id=f"default_{notification_type}",
            name=f"Default {notification_type.replace('_', ' ').title()}",
            notification_type=notification_type,
            subject_template=f"Notification: {notification_type.replace('_', ' ').title()}",
            body_template="{{ description | default('Notification details not available.') }}"
        )
    
    async def _add_to_batch_queue(self, notification_id: str, channels: List[str]):
        """Add notification to batch queues for each channel"""
        for channel_id in channels:
            if channel_id not in self.batch_queues:
                self.batch_queues[channel_id] = []
            
            self.batch_queues[channel_id].append(notification_id)
            
            # Check if batch is ready for delivery
            channel = self.notification_channels.get(channel_id)
            if channel and len(self.batch_queues[channel_id]) >= channel.batch_size:
                await self._deliver_batch(channel_id)
    
    async def _deliver_batch(self, channel_id: str):
        """Deliver batched notifications for a channel"""
        batch = self.batch_queues.get(channel_id, [])
        if not batch:
            return
        
        logger.info(f"Delivering batch of {len(batch)} notifications for channel {channel_id}")
        
        # Process batch
        for notification_id in batch:
            await self._deliver_notification(notification_id, single_channel=channel_id)
        
        # Clear batch
        self.batch_queues[channel_id] = []
    
    async def _deliver_notification(self, 
                                  notification_id: str, 
                                  single_channel: str = None):
        """Deliver notification through all configured channels"""
        notification = self.pending_notifications.get(notification_id)
        if not notification:
            logger.error(f"Notification not found: {notification_id}")
            return
        
        notification.delivery_attempts += 1
        delivery_results = {}
        
        # Determine channels to use
        channels_to_use = [single_channel] if single_channel else notification.channels
        
        # Deliver through each channel
        for channel_id in channels_to_use:
            channel = self.notification_channels.get(channel_id)
            if not channel or not channel.is_healthy():
                delivery_results[channel_id] = {"status": "failed", "error": "channel_unavailable"}
                continue
            
            # Get template and render for this channel
            template = self.templates.get(notification.notification_type)
            if template:
                rendered_content = template.render_content(channel.channel_type, notification.data)
            else:
                rendered_content = {"subject": notification.subject, "body": notification.body}
            
            # Deliver through specific channel
            try:
                result = await self._deliver_through_channel(
                    channel, rendered_content, notification.recipient_data
                )
                delivery_results[channel_id] = result
                
                if result["status"] == "success":
                    channel.messages_sent += 1
                else:
                    channel.failure_count += 1
                    channel.last_failure = datetime.now(timezone.utc)
                
            except Exception as e:
                logger.error(f"Delivery failed for channel {channel_id}: {e}")
                delivery_results[channel_id] = {"status": "failed", "error": str(e)}
                
                channel.failure_count += 1
                channel.last_failure = datetime.now(timezone.utc)
        
        # Update notification status
        notification.delivery_results = delivery_results
        
        success_count = sum(1 for result in delivery_results.values() 
                           if result["status"] == "success")
        
        if success_count > 0:
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.now(timezone.utc)
            self.successful_deliveries += 1
        else:
            if notification.delivery_attempts >= notification.max_delivery_attempts:
                notification.status = NotificationStatus.FAILED
                self.failed_deliveries += 1
            else:
                # Retry later
                retry_delay = min(300, notification.delivery_attempts * 60)  # Exponential backoff
                notification.scheduled_for = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
        
        await self._persist_notification(notification)
        
        logger.info(f"Notification delivery completed: {notification_id} "
                   f"({success_count}/{len(delivery_results)} channels successful)")
    
    async def _deliver_through_channel(self,
                                     channel: NotificationChannel,
                                     content: Dict[str, str],
                                     recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver notification through specific channel"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if channel.channel_type == NotificationChannel.EMAIL:
                result = await self._deliver_email(channel, content, recipient_data)
            elif channel.channel_type == NotificationChannel.SLACK:
                result = await self._deliver_slack(channel, content, recipient_data)
            elif channel.channel_type == NotificationChannel.DISCORD:
                result = await self._deliver_discord(channel, content, recipient_data)
            elif channel.channel_type == NotificationChannel.WEBHOOK:
                result = await self._deliver_webhook(channel, content, recipient_data)
            else:
                result = {"status": "failed", "error": "unsupported_channel_type"}
            
            # Track delivery time
            delivery_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            result["delivery_time_ms"] = delivery_time_ms
            
            # Update channel performance metrics
            if result["status"] == "success":
                # Update running average
                channel.avg_delivery_time_ms = (
                    (channel.avg_delivery_time_ms * 0.9) + (delivery_time_ms * 0.1)
                )
            
            return result
            
        except Exception as e:
            delivery_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return {
                "status": "failed",
                "error": str(e),
                "delivery_time_ms": delivery_time_ms
            }
    
    async def _deliver_email(self, 
                           channel: NotificationChannel,
                           content: Dict[str, str],
                           recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver notification via email"""
        config = channel.config
        recipient_email = recipient_data.get("email")
        
        if not recipient_email:
            return {"status": "failed", "error": "no_recipient_email"}
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = config.get('from_email', 'noreply@amas.ai')
            msg['To'] = recipient_email
            msg['Subject'] = content['subject']
            
            # Add body
            msg.attach(MIMEText(content['body'], 'html' if '<' in content['body'] else 'plain'))
            
            # Send via SMTP (using config)
            smtp_server = config.get('smtp_server', 'localhost')
            smtp_port = config.get('smtp_port', 587)
            username = config.get('username')
            password = config.get('password')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if username and password:
                    server.starttls()
                    server.login(username, password)
                
                server.send_message(msg)
            
            return {"status": "success", "recipient": recipient_email}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_slack(self,
                           channel: NotificationChannel,
                           content: Dict[str, str],
                           recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver notification via Slack"""
        config = channel.config
        webhook_url = config.get('webhook_url')
        
        if not webhook_url:
            return {"status": "failed", "error": "no_webhook_url"}
        
        try:
            # Build Slack message payload
            payload = {
                "text": content['subject'],
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": content['body']
                        }
                    }
                ]
            }
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        return {"status": "success", "response": await response.text()}
                    else:
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_discord(self,
                             channel: NotificationChannel,
                             content: Dict[str, str],
                             recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver notification via Discord webhook"""
        config = channel.config
        webhook_url = config.get('webhook_url')
        
        if not webhook_url:
            return {"status": "failed", "error": "no_webhook_url"}
        
        try:
            # Build Discord message payload
            payload = {
                "embeds": [
                    {
                        "title": content['subject'],
                        "description": content['body'],
                        "color": config.get('color', 0x0099ff),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }
            
            # Send to Discord
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:  # Discord webhooks return 204
                        return {"status": "success"}
                    else:
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _deliver_webhook(self,
                             channel: NotificationChannel,
                             content: Dict[str, str],
                             recipient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver notification via generic webhook"""
        config = channel.config
        webhook_url = config.get('webhook_url')
        
        if not webhook_url:
            return {"status": "failed", "error": "no_webhook_url"}
        
        try:
            # Build generic webhook payload
            payload = {
                "notification_id": notification.id,
                "type": notification.notification_type,
                "priority": notification.priority.value,
                "subject": content['subject'],
                "body": content['body'],
                "data": notification.data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add custom headers if configured
            headers = config.get('headers', {})
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    if response.status < 400:
                        return {"status": "success", "http_status": response.status}
                    else:
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def start_notification_processing(self):
        """Start background notification processing"""
        if self.running:
            return
        
        self.running = True
        
        # Start processing tasks
        self.processor_tasks = [
            asyncio.create_task(self._notification_delivery_loop()),
            asyncio.create_task(self._batch_processing_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        logger.info("Notification processing started")
    
    async def stop_notification_processing(self):
        """Stop background notification processing"""
        self.running = False
        
        # Cancel processing tasks
        for task in self.processor_tasks:
            task.cancel()
        
        if self.processor_tasks:
            await asyncio.gather(*self.processor_tasks, return_exceptions=True)
        
        self.processor_tasks.clear()
        
        logger.info("Notification processing stopped")
    
    async def _notification_delivery_loop(self):
        """Background loop for immediate notification delivery"""
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Find notifications ready for immediate delivery
                ready_notifications = []
                for notification in self.pending_notifications.values():
                    if (notification.should_deliver_now() and 
                        notification.status == NotificationStatus.PENDING):
                        ready_notifications.append(notification.id)
                
                # Deliver ready notifications
                for notification_id in ready_notifications:
                    asyncio.create_task(self._deliver_notification(notification_id))
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in notification delivery loop: {e}")
                await asyncio.sleep(60)
    
    async def _batch_processing_loop(self):
        """Background loop for batch processing"""
        while self.running:
            try:
                # Process batch queues that are ready
                for channel_id, batch in list(self.batch_queues.items()):
                    channel = self.notification_channels.get(channel_id)
                    if channel and batch:
                        # Check if batch delay has passed
                        oldest_notification_id = batch[0]
                        oldest_notification = self.pending_notifications.get(oldest_notification_id)
                        
                        if oldest_notification and oldest_notification.created_at:
                            age_minutes = (datetime.now(timezone.utc) - oldest_notification.created_at).total_seconds() / 60
                            
                            if age_minutes >= channel.batch_delay_minutes:
                                await self._deliver_batch(channel_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in batch processing loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Background cleanup of old notifications and metrics"""
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Clean up old notifications (keep for 7 days)
                cutoff_time = current_time - timedelta(days=7)
                
                expired_notifications = []
                for notification_id, notification in self.pending_notifications.items():
                    if notification.created_at < cutoff_time:
                        expired_notifications.append(notification_id)
                
                # Remove expired notifications
                for notification_id in expired_notifications:
                    del self.pending_notifications[notification_id]
                
                if expired_notifications:
                    logger.info(f"Cleaned up {len(expired_notifications)} old notifications")
                
                # Update channel success rates
                await self._update_channel_success_rates()
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def _update_channel_success_rates(self):
        """Update delivery success rates for channels"""
        for channel in self.notification_channels.values():
            total_attempts = channel.messages_sent + channel.failure_count
            if total_attempts > 0:
                success_rate = channel.messages_sent / total_attempts
                # Exponential moving average
                channel.delivery_success_rate = (channel.delivery_success_rate * 0.9) + (success_rate * 0.1)
    
    async def _persist_notification(self, notification: NotificationMessage):
        """Persist notification to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notifications (
                    id, notification_type, priority, channels, recipient_data, subject, body,
                    data, status, created_at, scheduled_for, delivered_at, delivery_results,
                    delivery_attempts, correlation_id, source_workflow_id, source_task_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.id, notification.notification_type, notification.priority.value,
                json.dumps(notification.channels), json.dumps(notification.recipient_data),
                notification.subject, notification.body, json.dumps(notification.data),
                notification.status.value, notification.created_at.isoformat(),
                notification.scheduled_for.isoformat() if notification.scheduled_for else None,
                notification.delivered_at.isoformat() if notification.delivered_at else None,
                json.dumps(notification.delivery_results), notification.delivery_attempts,
                notification.correlation_id, notification.source_workflow_id, notification.source_task_id
            ))
            conn.commit()
    
    async def _persist_channel(self, channel: NotificationChannel):
        """Persist channel configuration to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notification_channels (
                    id, channel_type, name, config, enabled, rate_limit_per_hour, batch_size,
                    batch_delay_minutes, messages_sent, delivery_success_rate, avg_delivery_time_ms,
                    retry_count, failure_count, last_failure, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                channel.id, channel.channel_type.value, channel.name, json.dumps(channel.config),
                channel.enabled, channel.rate_limit_per_hour, channel.batch_size,
                channel.batch_delay_minutes, channel.messages_sent, channel.delivery_success_rate,
                channel.avg_delivery_time_ms, channel.retry_count, channel.failure_count,
                channel.last_failure.isoformat() if channel.last_failure else None,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
    
    def get_notification_metrics(self) -> Dict[str, Any]:
        """Get notification system metrics"""
        active_channels = sum(1 for c in self.notification_channels.values() if c.enabled)
        healthy_channels = sum(1 for c in self.notification_channels.values() if c.is_healthy())
        
        pending_count = sum(1 for n in self.pending_notifications.values() 
                           if n.status == NotificationStatus.PENDING)
        
        success_rate = (self.successful_deliveries / max(1, self.total_notifications)) * 100
        
        return {
            "running": self.running,
            "total_notifications": self.total_notifications,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries,
            "success_rate_percent": round(success_rate, 2),
            "pending_notifications": pending_count,
            "active_channels": active_channels,
            "healthy_channels": healthy_channels,
            "total_templates": len(self.templates),
            "batched_notifications": sum(len(batch) for batch in self.batch_queues.values())
        }

# Global notification engine instance
_global_notification_engine: Optional[NotificationEngine] = None

def get_notification_engine() -> NotificationEngine:
    """Get global notification engine instance"""
    global _global_notification_engine
    if _global_notification_engine is None:
        _global_notification_engine = NotificationEngine()
    return _global_notification_engine
