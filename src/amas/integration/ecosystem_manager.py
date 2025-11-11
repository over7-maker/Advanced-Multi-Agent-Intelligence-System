"""
Comprehensive Ecosystem Integration Manager

Manages integration with external platforms, APIs, and services
to create a unified AI automation ecosystem.
"""

# Standard library imports
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Type, Union
from urllib.parse import urljoin, urlparse

# Third-party imports
import aiohttp

logger = logging.getLogger(__name__)


def _validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF and open redirect vulnerabilities.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is safe (http/https with valid netloc), False otherwise
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

class IntegrationType(str, Enum):
    # Workflow & Automation Platforms
    N8N = "n8n"
    ZAPIER = "zapier"
    MAKE = "make"
    POWER_AUTOMATE = "power_automate"
    
    # Communication Platforms
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    
    # Cloud Services
    AWS = "aws"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    
    # Business Applications
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    NOTION = "notion"
    AIRTABLE = "airtable"
    
    # Development Tools
    GITHUB = "github"
    GITLAB = "gitlab"
    JIRA = "jira"
    JENKINS = "jenkins"
    
    # Data Platforms
    SNOWFLAKE = "snowflake"
    DATABRICKS = "databricks"
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    
    # AI Services
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"

class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    CONFIGURING = "configuring"
    TESTING = "testing"
    DEPRECATED = "deprecated"

@dataclass
class IntegrationConfig:
    """Configuration for external service integration
    
    Security Note: Sensitive fields (api_key, password, oauth_token) are
    excluded from __repr__ to prevent credential leakage in logs.
    """
    integration_id: str
    integration_type: IntegrationType
    name: str
    
    # Connection configuration
    # Security: Sensitive fields use repr=False to prevent logging leaks
    base_url: Optional[str] = None
    api_key: Optional[str] = field(default=None, repr=False)
    username: Optional[str] = None
    password: Optional[str] = field(default=None, repr=False)
    oauth_token: Optional[str] = field(default=None, repr=False)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Integration settings
    enabled: bool = True
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30
    retry_count: int = 3
    
    # Capability mapping
    supported_operations: List[str] = field(default_factory=list)
    webhook_endpoints: List[str] = field(default_factory=list)
    
    # Performance tracking
    status: IntegrationStatus = IntegrationStatus.INACTIVE
    last_health_check: Optional[datetime] = None
    uptime_percentage: float = 0.0
    avg_response_time_ms: float = 0.0
    
    # Usage statistics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    tags: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate required fields
        if not self.integration_id:
            raise ValueError("integration_id is required")
        if not isinstance(self.integration_type, IntegrationType):
            raise TypeError(f"integration_type must be IntegrationType, got {type(self.integration_type)}")
        if not self.name:
            raise ValueError("name is required")
        
        # Validate URL if provided
        if self.base_url and not _validate_url(self.base_url):
            raise ValueError(f"Invalid base_url format: {self.base_url}. Must be http:// or https:// with valid domain")
        
        # Validate numeric fields
        if self.rate_limit_per_minute < 1:
            raise ValueError("rate_limit_per_minute must be >= 1")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be >= 1")
        if self.retry_count < 0:
            raise ValueError("retry_count must be >= 0")
        
        # Validate uptime percentage
        if not 0.0 <= self.uptime_percentage <= 100.0:
            raise ValueError("uptime_percentage must be between 0.0 and 100.0")

@dataclass
class IntegrationExecution:
    """Represents an execution through an external integration"""
    id: str
    integration_id: str
    operation: str
    
    # Request/response data
    request_data: Dict[str, Any]
    response_data: Optional[Dict[str, Any]] = None
    
    # Execution tracking
    status: str = "pending"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Performance metrics
    response_time_ms: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    
    # AMAS context
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None

class BaseIntegration(ABC):
    """Base class for all external integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize integration connection"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if integration is healthy"""
        pass
    
    @abstractmethod
    async def execute_operation(self, 
                              operation: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific operation through this integration"""
        pass
    
    async def cleanup(self):
        """Clean up integration resources"""
        if self.session:
            await self.session.close()

class SlackIntegration(BaseIntegration):
    """Slack platform integration"""
    
    async def initialize(self) -> bool:
        """Initialize Slack connection"""
        try:
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.config.oauth_token}'},
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            # Test authentication
            async with self.session.get('https://slack.com/api/auth.test') as response:
                if response.status == 200:
                    auth_data = await response.json()
                    if auth_data.get('ok'):
                        self.authenticated = True
                        self.config.status = IntegrationStatus.ACTIVE
                        logger.info(f"Slack integration initialized for team: {auth_data.get('team')}")
                        return True
            
            self.config.status = IntegrationStatus.FAILED
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Slack integration: {e}")
            self.config.status = IntegrationStatus.FAILED
            return False
    
    async def health_check(self) -> bool:
        """Check Slack API health"""
        try:
            if not self.session:
                return False
            
            async with self.session.get('https://slack.com/api/api.test') as response:
                if response.status == 200:
                    test_data = await response.json()
                    return test_data.get('ok', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Slack health check failed: {e}")
            return False
    
    async def execute_operation(self, 
                              operation: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack operation"""
        
        if operation == "send_message":
            return await self._send_message(parameters)
        elif operation == "create_channel":
            return await self._create_channel(parameters)
        elif operation == "upload_file":
            return await self._upload_file(parameters)
        else:
            raise ValueError(f"Unsupported Slack operation: {operation}")
    
    async def _send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Slack channel"""
        payload = {
            'channel': params['channel'],
            'text': params.get('text', ''),
            'blocks': params.get('blocks', []),
            'username': params.get('username', 'AMAS Bot'),
            'icon_emoji': params.get('icon', ':robot_face:')
        }
        
        async with self.session.post(
            'https://slack.com/api/chat.postMessage',
            json=payload
        ) as response:
            result = await response.json()
            
            if result.get('ok'):
                return {
                    'success': True,
                    'message_ts': result.get('ts'),
                    'channel': result.get('channel')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }

class NotionIntegration(BaseIntegration):
    """Notion workspace integration"""
    
    async def initialize(self) -> bool:
        """Initialize Notion connection"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.config.oauth_token}',
                    'Notion-Version': '2022-06-28',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            # Test connection by getting user info
            async with self.session.get('https://api.notion.com/v1/users/me') as response:
                if response.status == 200:
                    self.authenticated = True
                    self.config.status = IntegrationStatus.ACTIVE
                    logger.info("Notion integration initialized")
                    return True
            
            self.config.status = IntegrationStatus.FAILED
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Notion integration: {e}")
            self.config.status = IntegrationStatus.FAILED
            return False
    
    async def health_check(self) -> bool:
        """Check Notion API health"""
        try:
            async with self.session.get('https://api.notion.com/v1/users/me') as response:
                return response.status == 200
        except:
            return False
    
    async def execute_operation(self, 
                              operation: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Notion operation"""
        
        if operation == "create_page":
            return await self._create_page(parameters)
        elif operation == "update_page":
            return await self._update_page(parameters)
        elif operation == "query_database":
            return await self._query_database(parameters)
        else:
            raise ValueError(f"Unsupported Notion operation: {operation}")
    
    async def _create_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new Notion page"""
        payload = {
            'parent': {'database_id': params['database_id']},
            'properties': params.get('properties', {}),
            'children': params.get('content_blocks', [])
        }
        
        async with self.session.post(
            'https://api.notion.com/v1/pages',
            json=payload
        ) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'success': True,
                    'page_id': result.get('id'),
                    'url': result.get('url')
                }
            else:
                error_data = await response.json()
                return {
                    'success': False,
                    'error': error_data.get('message', 'Unknown error')
                }

class EcosystemManager:
    """Comprehensive ecosystem integration management"""
    
    def __init__(self):
        # Integration registry
        self.integrations: Dict[str, IntegrationConfig] = {}
        self.integration_instances: Dict[str, BaseIntegration] = {}
        
        # Execution tracking
        self.active_executions: Dict[str, IntegrationExecution] = {}
        self.execution_history: List[IntegrationExecution] = []
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Performance metrics
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        
        # Tool registry integration
        from .tool_registry import get_tool_registry
        self.tool_registry = get_tool_registry()
        
        # N8N connector integration
        self.n8n_connector: Optional[Any] = None
        
        logger.info("Ecosystem Manager initialized")
    
    async def initialize(self, integration_configs: List[Dict[str, Any]]) -> bool:
        """Initialize all configured integrations"""
        initialization_success = True
        
        for config_data in integration_configs:
            try:
                # Create integration config
                config = IntegrationConfig(
                    integration_id=config_data.get('id', f"int_{uuid.uuid4().hex[:8]}"),
                    integration_type=IntegrationType(config_data['type']),
                    name=config_data['name'],
                    base_url=config_data.get('base_url'),
                    api_key=config_data.get('api_key'),
                    username=config_data.get('username'),
                    password=config_data.get('password'),
                    oauth_token=config_data.get('oauth_token'),
                    custom_headers=config_data.get('headers', {}),
                    supported_operations=config_data.get('operations', []),
                    rate_limit_per_minute=config_data.get('rate_limit', 60),
                    timeout_seconds=config_data.get('timeout', 30)
                )
                
                # Create integration instance
                integration_instance = self._create_integration_instance(config)
                
                if integration_instance:
                    # Initialize integration
                    success = await integration_instance.initialize()
                    
                    if success:
                        self.integrations[config.integration_id] = config
                        self.integration_instances[config.integration_id] = integration_instance
                        
                        logger.info(f"Initialized integration: {config.name} ({config.integration_type.value})")
                    else:
                        initialization_success = False
                        logger.error(f"Failed to initialize integration: {config.name}")
                else:
                    initialization_success = False
                    logger.error(f"Failed to create integration instance: {config.integration_type.value}")
                    
            except Exception as e:
                initialization_success = False
                logger.error(f"Error initializing integration {config_data.get('name', 'unknown')}: {e}")
        
        # Initialize N8N connector if configured
        n8n_config = next((c for c in integration_configs if c.get('type') == 'n8n'), None)
        if n8n_config:
            await self._initialize_n8n_connector(n8n_config)
        
        # Start health monitoring
        if initialization_success:
            await self.start_health_monitoring()
        
        logger.info(f"Ecosystem initialization {'successful' if initialization_success else 'completed with errors'}")
        return initialization_success
    
    def _create_integration_instance(self, config: IntegrationConfig) -> Optional[BaseIntegration]:
        """Factory method to create integration instances"""
        
        if config.integration_type == IntegrationType.SLACK:
            return SlackIntegration(config)
        elif config.integration_type == IntegrationType.NOTION:
            return NotionIntegration(config)
        elif config.integration_type == IntegrationType.N8N:
            # N8N is handled separately via N8NConnector
            return None
        else:
            # For other integrations, create a generic HTTP integration
            return GenericAPIIntegration(config)
    
    async def _initialize_n8n_connector(self, n8n_config: Dict[str, Any]):
        """Initialize N8N connector separately"""
        try:
            from .n8n_connector import get_n8n_connector
            
            self.n8n_connector = await get_n8n_connector({
                'n8n_base_url': n8n_config.get('base_url', 'http://localhost:5678'),
                'api_key': n8n_config.get('api_key'),
                'username': n8n_config.get('username'),
                'password': n8n_config.get('password')
            })
            
            # Set up automation workflows
            automation_workflows = await self.n8n_connector.setup_amas_automation_workflows()
            
            logger.info(f"N8N connector initialized with {len(automation_workflows)} automation workflows")
            
        except Exception as e:
            logger.error(f"Failed to initialize N8N connector: {e}")
    
    async def start_health_monitoring(self):
        """Start background health monitoring for all integrations"""
        if self.running:
            return
        
        self.running = True
        self.health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
        
        logger.info("Health monitoring started for ecosystem integrations")
    
    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        self.running = False
        
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Health monitoring stopped")
    
    async def _health_monitoring_loop(self):
        """Background loop for health checking all integrations"""
        while self.running:
            try:
                # Check health of all active integrations
                for integration_id, integration in self.integration_instances.items():
                    config = self.integrations[integration_id]
                    
                    if config.status == IntegrationStatus.ACTIVE:
                        try:
                            is_healthy = await integration.health_check()
                            
                            if is_healthy:
                                config.last_health_check = datetime.now(timezone.utc)
                                # Update uptime percentage (simplified calculation)
                                config.uptime_percentage = min(99.9, config.uptime_percentage + 0.1)
                            else:
                                config.status = IntegrationStatus.FAILED
                                logger.warning(f"Integration health check failed: {config.name}")
                                
                        except Exception as e:
                            config.status = IntegrationStatus.FAILED
                            logger.error(f"Health check error for {config.name}: {e}")
                
                # Check N8N connector health
                if self.n8n_connector:
                    try:
                        n8n_metrics = await self.n8n_connector.get_workflow_metrics()
                        if not n8n_metrics.get('connected'):
                            logger.warning("N8N connector appears disconnected")
                    except Exception as e:
                        logger.error(f"N8N health check error: {e}")
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def execute_integration_operation(self,
                                         integration_id: str,
                                         operation: str,
                                         parameters: Dict[str, Any],
                                         agent_context: Dict[str, Any] = None) -> IntegrationExecution:
        """Execute operation through specific integration"""
        
        execution_id = f"int_exec_{uuid.uuid4().hex[:8]}"
        agent_context = agent_context or {}
        
        # Create execution record
        execution = IntegrationExecution(
            id=execution_id,
            integration_id=integration_id,
            operation=operation,
            request_data=parameters,
            agent_id=agent_context.get('agent_id'),
            workflow_id=agent_context.get('workflow_id'),
            task_id=agent_context.get('task_id')
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            # Get integration instance
            integration = self.integration_instances.get(integration_id)
            if not integration:
                raise ValueError(f"Integration not found: {integration_id}")
            
            config = self.integrations[integration_id]
            if config.status != IntegrationStatus.ACTIVE:
                raise ValueError(f"Integration not active: {integration_id}")
            
            # Record start time
            start_time = asyncio.get_event_loop().time()
            execution.status = "running"
            
            # Execute operation with retry logic
            result = await self._execute_with_retries(
                integration, operation, parameters, config.retry_count
            )
            
            # Record completion
            execution.completed_at = datetime.now(timezone.utc)
            execution.status = "completed"
            execution.response_data = result
            execution.response_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Update metrics
            self.total_requests += 1
            self.successful_requests += 1
            config.total_requests += 1
            config.successful_requests += 1
            
            # Update average response time
            config.avg_response_time_ms = (
                (config.avg_response_time_ms * 0.9) + 
                (execution.response_time_ms * 0.1)
            )
            
            logger.info(f"Integration execution successful: {integration_id}.{operation} ({execution_id})")
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_message = str(e)
            
            # Update metrics
            self.total_requests += 1
            self.failed_requests += 1
            config = self.integrations.get(integration_id)
            if config:
                config.total_requests += 1
                config.failed_requests += 1
            
            logger.error(f"Integration execution failed: {integration_id}.{operation} ({execution_id}): {e}")
        
        finally:
            # Move to history
            if execution_id in self.active_executions:
                completed_execution = self.active_executions.pop(execution_id)
                self.execution_history.append(completed_execution)
                
                # Keep only recent history
                if len(self.execution_history) > 1000:
                    self.execution_history = self.execution_history[-1000:]
        
        return execution
    
    async def _execute_with_retries(self,
                                  integration: BaseIntegration,
                                  operation: str,
                                  parameters: Dict[str, Any],
                                  max_retries: int) -> Dict[str, Any]:
        """Execute operation with retry logic"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await integration.execute_operation(operation, parameters)
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = min(60, 2 ** attempt)
                    logger.warning(f"Integration operation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Integration operation failed after {max_retries + 1} attempts: {e}")
        
        raise last_exception
    
    async def trigger_n8n_workflow(self,
                                 workflow_name: str,
                                 input_data: Dict[str, Any],
                                 wait_for_completion: bool = False) -> Optional[Dict[str, Any]]:
        """Trigger N8N workflow from AMAS"""
        
        if not self.n8n_connector:
            logger.error("N8N connector not initialized")
            return None
        
        try:
            # Find workflow by name
            workflows = self.n8n_connector.registered_workflows
            workflow = next((w for w in workflows.values() if w.name == workflow_name), None)
            
            if not workflow:
                logger.error(f"N8N workflow not found: {workflow_name}")
                return None
            
            # Execute workflow
            execution = await self.n8n_connector.execute_workflow(
                workflow.id,
                input_data,
                wait_for_completion
            )
            
            if execution:
                return {
                    'execution_id': execution.id,
                    'workflow_id': workflow.id,
                    'status': execution.status.value,
                    'started_at': execution.started_at.isoformat(),
                    'input_data': execution.input_data
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error triggering N8N workflow {workflow_name}: {e}")
            return None
    
    def get_available_integrations(self, 
                                 integration_type: IntegrationType = None,
                                 status_filter: IntegrationStatus = None) -> List[Dict[str, Any]]:
        """Get list of available integrations with status"""
        
        integrations_list = []
        
        for config in self.integrations.values():
            # Apply filters
            if integration_type and config.integration_type != integration_type:
                continue
            
            if status_filter and config.status != status_filter:
                continue
            
            integration_info = {
                'id': config.integration_id,
                'name': config.name,
                'type': config.integration_type.value,
                'status': config.status.value,
                'enabled': config.enabled,
                'supported_operations': config.supported_operations,
                'uptime_percentage': round(config.uptime_percentage, 2),
                'avg_response_time_ms': round(config.avg_response_time_ms, 1),
                'success_rate_percent': round(
                    (config.successful_requests / max(1, config.total_requests)) * 100, 2
                ),
                'last_health_check': config.last_health_check.isoformat() if config.last_health_check else None,
                'total_requests': config.total_requests
            }
            
            integrations_list.append(integration_info)
        
        return integrations_list
    
    def get_integration_capabilities(self) -> Dict[str, List[str]]:
        """Get comprehensive mapping of available integration capabilities"""
        
        capabilities = {
            'communication': [],
            'data_processing': [],
            'workflow_automation': [],
            'file_operations': [],
            'business_applications': [],
            'ai_services': [],
            'development_tools': []
        }
        
        for config in self.integrations.values():
            if config.status == IntegrationStatus.ACTIVE:
                
                # Categorize integrations
                if config.integration_type in [IntegrationType.SLACK, IntegrationType.DISCORD, IntegrationType.TEAMS]:
                    capabilities['communication'].append({
                        'name': config.name,
                        'type': config.integration_type.value,
                        'operations': config.supported_operations
                    })
                    
                elif config.integration_type in [IntegrationType.AWS, IntegrationType.GOOGLE_CLOUD, IntegrationType.AZURE]:
                    capabilities['data_processing'].append({
                        'name': config.name,
                        'type': config.integration_type.value,
                        'operations': config.supported_operations
                    })
                    
                elif config.integration_type in [IntegrationType.N8N, IntegrationType.ZAPIER, IntegrationType.MAKE]:
                    capabilities['workflow_automation'].append({
                        'name': config.name,
                        'type': config.integration_type.value,
                        'operations': config.supported_operations
                    })
                
                # Add to other categories as appropriate...
        
        return capabilities
    
    async def optimize_tool_selection(self,
                                    task_description: str,
                                    agent_specialty: str,
                                    available_integrations: List[str] = None,
                                    performance_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """AI-powered optimization of tool and integration selection"""
        
        performance_requirements = performance_requirements or {}
        available_integrations = available_integrations or list(self.integrations.keys())
        
        # Get tool recommendations from registry
        recommended_tools = self.tool_registry.get_tool_recommendations(
            task_description, agent_specialty
        )
        
        # Filter tools based on available integrations
        compatible_tools = []
        for tool in recommended_tools:
            # Check if tool requires integrations that are available
            if self._check_tool_integration_compatibility(tool, available_integrations):
                compatible_tools.append(tool)
        
        # Get relevant integrations for the task
        relevant_integrations = self._get_relevant_integrations(
            task_description, available_integrations
        )
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            compatible_tools, relevant_integrations, performance_requirements
        )
        
        return {
            'recommended_tools': [{
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'quality_score': tool.quality_score,
                'estimated_time': tool.avg_execution_time_seconds,
                'estimated_cost': tool.cost_per_execution
            } for tool in compatible_tools[:5]],  # Top 5 tools
            
            'recommended_integrations': [{
                'id': integration_id,
                'name': self.integrations[integration_id].name,
                'type': self.integrations[integration_id].integration_type.value,
                'operations': self.integrations[integration_id].supported_operations
            } for integration_id in relevant_integrations[:3]],  # Top 3 integrations
            
            'optimization_score': optimization_score,
            'estimated_total_time': sum(tool.avg_execution_time_seconds for tool in compatible_tools[:5]),
            'estimated_total_cost': sum(tool.cost_per_execution for tool in compatible_tools[:5])
        }
    
    def _check_tool_integration_compatibility(self, 
                                            tool, 
                                            available_integrations: List[str]) -> bool:
        """Check if tool is compatible with available integrations"""
        # Simple compatibility check - could be enhanced
        return True  # For now, assume all tools are compatible
    
    def _get_relevant_integrations(self, 
                                 task_description: str, 
                                 available_integrations: List[str]) -> List[str]:
        """Get integrations most relevant to the task"""
        
        task_lower = task_description.lower()
        relevant = []
        
        for integration_id in available_integrations:
            config = self.integrations.get(integration_id)
            if not config or config.status != IntegrationStatus.ACTIVE:
                continue
            
            # Simple keyword matching
            integration_keywords = {
                IntegrationType.SLACK: ['slack', 'message', 'notify', 'team', 'communication'],
                IntegrationType.NOTION: ['notion', 'document', 'database', 'page', 'knowledge'],
                IntegrationType.N8N: ['workflow', 'automation', 'process', 'pipeline'],
                IntegrationType.GITHUB: ['github', 'code', 'repository', 'git', 'development'],
                IntegrationType.SALESFORCE: ['salesforce', 'crm', 'sales', 'customer', 'lead']
            }
            
            keywords = integration_keywords.get(config.integration_type, [])
            if any(keyword in task_lower for keyword in keywords):
                relevant.append(integration_id)
        
        return relevant
    
    def _calculate_optimization_score(self,
                                    tools: List[Any],
                                    integrations: List[str],
                                    requirements: Dict[str, Any]) -> float:
        """Calculate overall optimization score for tool/integration selection"""
        
        if not tools and not integrations:
            return 0.0
        
        # Base score from tool quality
        tool_score = sum(tool.quality_score * tool.success_rate for tool in tools) / max(1, len(tools))
        
        # Integration health score
        integration_score = 0.0
        if integrations:
            total_uptime = sum(
                self.integrations[int_id].uptime_percentage 
                for int_id in integrations 
                if int_id in self.integrations
            )
            integration_score = total_uptime / (len(integrations) * 100.0)
        
        # Performance requirements score
        performance_score = 1.0
        if requirements:
            max_time = requirements.get('max_execution_time')
            max_cost = requirements.get('max_cost')
            
            if max_time and tools:
                avg_time = sum(tool.avg_execution_time_seconds for tool in tools) / len(tools)
                performance_score *= min(1.0, max_time / max(avg_time, 1.0))
            
            if max_cost and tools:
                avg_cost = sum(tool.cost_per_execution for tool in tools) / len(tools)
                performance_score *= min(1.0, max_cost / max(avg_cost, 0.001))
        
        # Combine scores
        final_score = (tool_score * 0.5 + integration_score * 0.3 + performance_score * 0.2)
        return min(1.0, final_score)
    
    async def get_ecosystem_metrics(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem metrics"""
        
        active_integrations = sum(1 for config in self.integrations.values() 
                                if config.status == IntegrationStatus.ACTIVE)
        
        total_integrations = len(self.integrations)
        
        success_rate = (self.successful_requests / max(1, self.total_requests)) * 100
        
        # Get tool registry metrics
        tool_metrics = self.tool_registry.get_registry_metrics()
        
        # Get N8N metrics if available
        n8n_metrics = {}
        if self.n8n_connector:
            try:
                n8n_metrics = await self.n8n_connector.get_workflow_metrics()
            except:
                n8n_metrics = {'connected': False}
        
        return {
            'ecosystem_health': 'healthy' if active_integrations > 0 else 'degraded',
            'total_integrations': total_integrations,
            'active_integrations': active_integrations,
            'integration_uptime_avg': round(
                sum(c.uptime_percentage for c in self.integrations.values()) / max(1, total_integrations), 2
            ),
            'total_requests': self.total_requests,
            'success_rate_percent': round(success_rate, 2),
            'avg_response_time_ms': round(
                sum(c.avg_response_time_ms for c in self.integrations.values()) / max(1, total_integrations), 1
            ),
            'active_executions': len(self.active_executions),
            'tool_registry': tool_metrics,
            'n8n_connector': n8n_metrics
        }
    
    async def cleanup(self):
        """Clean up all integration resources"""
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Clean up integration instances
        for integration in self.integration_instances.values():
            try:
                await integration.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up integration: {e}")
        
        # Clean up N8N connector
        if self.n8n_connector:
            try:
                await self.n8n_connector.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up N8N connector: {e}")
        
        logger.info("Ecosystem Manager cleaned up")

class GenericAPIIntegration(BaseIntegration):
    """Generic HTTP API integration for unsupported services"""
    
    async def initialize(self) -> bool:
        """Initialize generic API connection"""
        try:
            headers = self.config.custom_headers.copy()
            
            if self.config.api_key:
                headers['Authorization'] = f'Bearer {self.config.api_key}'
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )
            
            # Test connection if base_url provided
            if self.config.base_url:
                await self.health_check()
            
            self.authenticated = True
            self.config.status = IntegrationStatus.ACTIVE
            
            logger.info(f"Generic API integration initialized: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize generic API integration: {e}")
            self.config.status = IntegrationStatus.FAILED
            return False
    
    async def health_check(self) -> bool:
        """Check API health"""
        if not self.config.base_url or not self.session:
            return False
        
        try:
            # Try to access base URL or health endpoint
            # Security: Validate URL before use to prevent SSRF
            health_url = urljoin(self.config.base_url, '/health')
            if not _validate_url(health_url):
                logger.warning(f"Invalid health URL constructed: {health_url}")
                return False
            
            async with self.session.get(health_url) as response:
                return response.status < 500  # Accept any non-server-error status
                
        except Exception:
            # If health endpoint fails, try base URL
            # base_url is already validated in __post_init__, but double-check for safety
            if not _validate_url(self.config.base_url):
                return False
            try:
                async with self.session.get(self.config.base_url) as response:
                    return response.status < 500
            except:
                return False
    
    async def execute_operation(self, 
                              operation: str, 
                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic API operation"""
        
        if operation == "get":
            return await self._make_request("GET", parameters.get('endpoint', ''), parameters.get('params', {}))
        elif operation == "post":
            return await self._make_request("POST", parameters.get('endpoint', ''), data=parameters.get('data', {}))
        elif operation == "put":
            return await self._make_request("PUT", parameters.get('endpoint', ''), data=parameters.get('data', {}))
        elif operation == "delete":
            return await self._make_request("DELETE", parameters.get('endpoint', ''), parameters.get('params', {}))
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def _make_request(self, 
                          method: str, 
                          endpoint: str, 
                          params: Dict[str, Any] = None,
                          data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to external API
        
        Security: Validates URL before making request to prevent SSRF attacks.
        """
        if self.config.base_url:
            url = urljoin(self.config.base_url, endpoint)
            # Security: Validate constructed URL to prevent SSRF
            if not _validate_url(url):
                raise ValueError(f"Invalid URL constructed from base_url and endpoint: {url}")
        else:
            # If no base_url, endpoint must be a full URL
            url = endpoint
            if not _validate_url(url):
                raise ValueError(f"Invalid endpoint URL: {url}")
        
        async with self.session.request(
            method=method,
            url=url,
            params=params,
            json=data
        ) as response:
            response_data = {
                'status_code': response.status,
                'headers': dict(response.headers),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            try:
                response_data['data'] = await response.json()
            except:
                response_data['text'] = await response.text()
            
            return response_data

# Global ecosystem manager
_global_ecosystem_manager: Optional[EcosystemManager] = None

def get_ecosystem_manager() -> EcosystemManager:
    """Get global ecosystem manager instance"""
    global _global_ecosystem_manager
    if _global_ecosystem_manager is None:
        _global_ecosystem_manager = EcosystemManager()
    return _global_ecosystem_manager
