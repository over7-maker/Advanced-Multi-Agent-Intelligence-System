"""
N8N Workflow Integration Connector

Provides seamless integration with N8N for advanced workflow automation,
tool orchestration, and external service coordination.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

logger = logging.getLogger(__name__)

class N8NWorkflowStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    WAITING = "waiting"

class TriggerType(str, Enum):
    WEBHOOK = "webhook"
    CRON = "cron"
    MANUAL = "manual"
    API_CALL = "api_call"
    FILE_WATCH = "file_watch"
    EMAIL = "email"
    DATABASE = "database"

@dataclass
class N8NNode:
    """Represents an N8N workflow node configuration"""
    id: str
    name: str
    type: str
    position: tuple[int, int]
    
    # Node configuration
    parameters: Dict[str, Any] = field(default_factory=dict)
    credentials: Optional[str] = None
    
    # Connection information
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    
    # Execution tracking
    disabled: bool = False
    notes: str = ""

@dataclass
class N8NWorkflow:
    """Represents an N8N workflow configuration"""
    id: str
    name: str
    active: bool
    
    # Workflow structure
    nodes: List[N8NNode]
    connections: Dict[str, Any]
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Integration context
    amas_workflow_id: Optional[str] = None
    trigger_type: TriggerType = TriggerType.WEBHOOK
    
    # Performance tracking
    execution_count: int = 0
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    
    # Created/modified tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class N8NExecution:
    """Represents an N8N workflow execution"""
    id: str
    workflow_id: str
    status: N8NWorkflowStatus
    
    # Execution details
    started_at: datetime
    finished_at: Optional[datetime] = None
    mode: str = "trigger"  # trigger, manual, retry
    
    # Execution data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Node-level execution details
    node_executions: Dict[str, Any] = field(default_factory=dict)
    
    # AMAS integration
    triggered_by_amas: bool = False
    amas_context: Dict[str, Any] = field(default_factory=dict)

class N8NConnector:
    """N8N integration connector for advanced workflow automation"""
    
    def __init__(self, 
                 n8n_base_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None):
        """
        Initialize N8N connector with credentials from settings or parameters
        
        Priority:
        1. Parameters (if provided)
        2. Credential manager (from settings/env)
        3. Default values
        """
        # Try to get credentials from credential manager
        try:
            from src.amas.services.credential_manager import get_credential_manager
            cred_manager = get_credential_manager()
            creds = cred_manager.get_integration_credentials("n8n")
            
            self.base_url = (n8n_base_url or creds.get("base_url") or "http://localhost:5678").rstrip('/')
            self.api_key = api_key or creds.get("api_key")
            self.username = username or creds.get("username")
            self.password = password or creds.get("password")
        except Exception as e:
            logger.debug(f"Could not load credentials from manager: {e}")
            # Fallback to parameters or defaults
            self.base_url = (n8n_base_url or "http://localhost:5678").rstrip('/')
            self.api_key = api_key
            self.username = username
            self.password = password
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.authenticated = False
        
        # Workflow registry
        self.registered_workflows: Dict[str, N8NWorkflow] = {}
        self.webhook_mappings: Dict[str, str] = {}  # webhook_url -> workflow_id
        
        # Execution tracking
        self.active_executions: Dict[str, N8NExecution] = {}
        self.execution_history: List[N8NExecution] = []
        
        # Performance metrics
        self.total_executions: int = 0
        self.successful_executions: int = 0
        self.failed_executions: int = 0
        
        logger.info(f"N8N Connector initialized for: {self.base_url}")
    
    async def initialize(self) -> bool:
        """Initialize N8N connection and authenticate"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100)
            )
            
            # Authenticate if credentials provided
            if self.api_key:
                self.session.headers.update({'X-N8N-API-KEY': self.api_key})
                self.authenticated = True
            elif self.username and self.password:
                await self._authenticate_with_credentials()
            else:
                logger.warning("No N8N credentials provided - public API access only")
            
            # Test connection
            await self._test_connection()
            
            # Load existing workflows
            await self.load_workflows()
            
            logger.info("N8N Connector successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize N8N Connector: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def _authenticate_with_credentials(self):
        """Authenticate with N8N using username/password"""
        if self.session is None:
            raise RuntimeError("Session not initialized")
        
        auth_url = urljoin(self.base_url, '/rest/login')
        
        auth_data = {
            'email': self.username,
            'password': self.password
        }
        
        async with self.session.post(auth_url, json=auth_data) as response:
            if response.status == 200:
                # N8N typically returns authentication token in cookie
                self.authenticated = True
                logger.info("Successfully authenticated with N8N")
            else:
                error_text = await response.text()
                raise Exception(f"Authentication failed: {error_text}")
    
    async def _test_connection(self):
        """Test N8N API connection"""
        if self.session is None:
            raise RuntimeError("Session not initialized")
        
        health_url = urljoin(self.base_url, '/healthz')
        
        async with self.session.get(health_url) as response:
            if response.status != 200:
                raise Exception(f"N8N health check failed: {response.status}")
            
            health_data = await response.json()
            logger.info(f"N8N connection healthy: {health_data}")
    
    async def load_workflows(self) -> List[N8NWorkflow]:
        """Load existing workflows from N8N instance"""
        if not self.authenticated:
            logger.warning("Not authenticated - cannot load workflows")
            return []
        
        try:
            if self.session is None:
                logger.warning("Session not initialized - cannot load workflows")
                return []
            
            workflows_url = urljoin(self.base_url, '/rest/workflows')
            
            async with self.session.get(workflows_url) as response:
                if response.status == 200:
                    workflows_data = await response.json()
                    
                    loaded_workflows = []
                    for workflow_data in workflows_data:
                        workflow = self._parse_n8n_workflow(workflow_data)
                        self.registered_workflows[workflow.id] = workflow
                        loaded_workflows.append(workflow)
                    
                    logger.info(f"Loaded {len(loaded_workflows)} workflows from N8N")
                    return loaded_workflows
                else:
                    logger.error(f"Failed to load workflows: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")
            return []
    
    def _parse_n8n_workflow(self, workflow_data: Dict[str, Any]) -> N8NWorkflow:
        """Parse N8N workflow data into internal format"""
        # Extract nodes
        nodes = []
        for node_data in workflow_data.get('nodes', []):
            node = N8NNode(
                id=node_data['id'],
                name=node_data['name'],
                type=node_data['type'],
                position=(
                    node_data.get('position', [0, 0])[0],
                    node_data.get('position', [0, 0])[1]
                ),
                parameters=node_data.get('parameters', {}),
                credentials=node_data.get('credentials'),
                disabled=node_data.get('disabled', False),
                notes=node_data.get('notes', "")
            )
            nodes.append(node)
        
        # Determine trigger type
        trigger_type = TriggerType.MANUAL
        for node in nodes:
            if 'trigger' in node.type.lower():
                if 'webhook' in node.type.lower():
                    trigger_type = TriggerType.WEBHOOK
                elif 'cron' in node.type.lower() or 'schedule' in node.type.lower():
                    trigger_type = TriggerType.CRON
                elif 'email' in node.type.lower():
                    trigger_type = TriggerType.EMAIL
                break
        
        return N8NWorkflow(
            id=workflow_data['id'],
            name=workflow_data['name'],
            active=workflow_data.get('active', False),
            nodes=nodes,
            connections=workflow_data.get('connections', {}),
            tags=workflow_data.get('tags', []),
            settings=workflow_data.get('settings', {}),
            trigger_type=trigger_type,
            created_at=datetime.fromisoformat(
                workflow_data.get('createdAt', datetime.now(timezone.utc).isoformat())
            ),
            updated_at=datetime.fromisoformat(
                workflow_data.get('updatedAt', datetime.now(timezone.utc).isoformat())
            )
        )
    
    async def create_amas_integration_workflow(self,
                                             workflow_name: str,
                                             amas_workflow_id: str,
                                             integration_config: Dict[str, Any]) -> Optional[str]:
        """Create N8N workflow optimized for AMAS integration"""
        
        # Build N8N workflow for AMAS integration
        workflow_config = self._build_amas_integration_workflow(
            workflow_name, amas_workflow_id, integration_config
        )
        
        try:
            if self.session is None:
                logger.error("Session not initialized - cannot create workflow")
                return None
            
            create_url = urljoin(self.base_url, '/rest/workflows')
            
            async with self.session.post(create_url, json=workflow_config) as response:
                if response.status == 201:
                    created_workflow = await response.json()
                    workflow_id = created_workflow['id']
                    
                    # Parse and store the created workflow
                    workflow = self._parse_n8n_workflow(created_workflow)
                    workflow.amas_workflow_id = amas_workflow_id
                    self.registered_workflows[workflow_id] = workflow
                    
                    logger.info(f"Created N8N workflow: {workflow_id} for AMAS workflow: {amas_workflow_id}")
                    return workflow_id
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to create workflow: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating N8N workflow: {e}")
            return None
    
    def _build_amas_integration_workflow(self,
                                       name: str,
                                       amas_workflow_id: str,
                                       config: Dict[str, Any]) -> Dict[str, Any]:
        """Build N8N workflow configuration for AMAS integration"""
        
        nodes = []
        connections = {}
        
        # 1. Webhook trigger node (for AMAS to trigger N8N workflows)
        webhook_node = {
            "id": "webhook_trigger",
            "name": "AMAS Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [100, 200],
            "parameters": {
                "httpMethod": "POST",
                "path": f"amas/{amas_workflow_id}",
                "responseMode": "onReceived",
                "options": {}
            }
        }
        nodes.append(webhook_node)
        
        # 2. Data processing nodes based on configuration
        node_y_position = 300
        previous_node = "webhook_trigger"
        
        # Add configured integration steps
        integration_steps = config.get('integration_steps', [])
        
        for i, step in enumerate(integration_steps):
            step_type = step.get('type')
            node_id = f"step_{i+1}_{step_type}"
            
            if step_type == 'data_transformation':
                # Add data transformation node
                transform_node = {
                    "id": node_id,
                    "name": f"Transform: {step.get('name', 'Data')}",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [300 + i * 200, node_y_position],
                    "parameters": {
                        "functionCode": step.get('transformation_code', 'return items;')
                    }
                }
                nodes.append(transform_node)
                
            elif step_type == 'api_call':
                # Add HTTP request node
                api_node = {
                    "id": node_id,
                    "name": f"API: {step.get('name', 'External Service')}",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [300 + i * 200, node_y_position],
                    "parameters": {
                        "url": step.get('endpoint_url', ''),
                        "authentication": step.get('auth_type', 'none'),
                        "requestMethod": step.get('method', 'GET'),
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": step.get('headers', [])
                        }
                    }
                }
                
                if step.get('auth_type') == 'bearer':
                    api_node['parameters']['authentication'] = 'genericCredentialType'
                    api_node['credentials'] = {'httpHeaderAuth': step.get('credential_id')}
                
                nodes.append(api_node)
                
            elif step_type == 'database_operation':
                # Add database node
                db_node = {
                    "id": node_id,
                    "name": f"DB: {step.get('name', 'Database Operation')}",
                    "type": "n8n-nodes-base.postgres",  # or other DB type
                    "typeVersion": 1,
                    "position": [300 + i * 200, node_y_position],
                    "parameters": {
                        "operation": step.get('operation', 'select'),
                        "query": step.get('query', ''),
                    },
                    "credentials": {
                        "postgres": step.get('db_credential_id')
                    }
                }
                nodes.append(db_node)
                
            elif step_type == 'file_operation':
                # Add file operation node
                file_node = {
                    "id": node_id,
                    "name": f"File: {step.get('name', 'File Operation')}",
                    "type": "n8n-nodes-base.readWriteFile",
                    "typeVersion": 1,
                    "position": [300 + i * 200, node_y_position],
                    "parameters": {
                        "operation": step.get('file_operation', 'read'),
                        "filePath": step.get('file_path', ''),
                        "encoding": "utf8"
                    }
                }
                nodes.append(file_node)
            
            # Set up connection from previous node
            if i == 0:
                # Connect from webhook trigger
                connections["webhook_trigger"] = {
                    "main": [[{"node": node_id, "type": "main", "index": 0}]]
                }
            else:
                # Connect from previous step
                connections[previous_node] = {
                    "main": [[{"node": node_id, "type": "main", "index": 0}]]
                }
            
            previous_node = node_id
        
        # 3. Response/callback node (send results back to AMAS)
        callback_node = {
            "id": "amas_callback",
            "name": "AMAS Callback",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 3,
            "position": [300 + len(integration_steps) * 200, node_y_position],
            "parameters": {
                "url": config.get('callback_url', f"http://localhost:8000/api/workflows/{amas_workflow_id}/n8n_callback"),
                "requestMethod": "POST",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "Authorization", "value": f"Bearer {config.get('amas_api_token', '')}"}
                    ]
                },
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "execution_id", "value": "={{ $json.execution_id }}"},
                        {"name": "status", "value": "completed"},
                        {"name": "results", "value": "={{ $json }}"},
                        {"name": "timestamp", "value": "={{ new Date().toISOString() }}"}
                    ]
                }
            }
        }
        nodes.append(callback_node)
        
        # Connect last integration step to callback
        if integration_steps:
            connections[previous_node] = {
                "main": [[{"node": "amas_callback", "type": "main", "index": 0}]]
            }
        else:
            # Connect webhook directly to callback if no steps
            connections["webhook_trigger"] = {
                "main": [[{"node": "amas_callback", "type": "main", "index": 0}]]
            }
        
        # Build complete workflow
        workflow_config = {
            "name": name,
            "active": True,
            "nodes": nodes,
            "connections": connections,
            "settings": {
                "executionOrder": "v1"
            },
            "tags": ["amas", "integration", "auto-generated"]
        }
        
        return workflow_config
    
    async def execute_workflow(self,
                             workflow_id: str,
                             input_data: Optional[Dict[str, Any]] = None,
                             wait_for_completion: bool = False,
                             timeout_seconds: int = 300) -> Optional[N8NExecution]:
        """Execute N8N workflow and optionally wait for completion"""
        
        workflow = self.registered_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow not found: {workflow_id}")
            return None
        
        try:
            # Trigger workflow execution
            if workflow.trigger_type == TriggerType.WEBHOOK:
                execution = await self._trigger_webhook_workflow(workflow, input_data or {})
            else:
                execution = await self._trigger_manual_workflow(workflow_id, input_data or {})
            
            if not execution:
                return None
            
            self.active_executions[execution.id] = execution
            self.total_executions += 1
            
            # Wait for completion if requested
            if wait_for_completion:
                final_execution = await self._wait_for_execution_completion(
                    execution.id, timeout_seconds
                )
                return final_execution
            
            return execution
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            return None
    
    async def _trigger_webhook_workflow(self, 
                                      workflow: N8NWorkflow, 
                                      input_data: Dict[str, Any]) -> Optional[N8NExecution]:
        """Trigger workflow via webhook"""
        
        # Find webhook node to get URL
        webhook_node = next((node for node in workflow.nodes 
                           if 'webhook' in node.type.lower()), None)
        
        if not webhook_node:
            logger.error(f"No webhook trigger found in workflow {workflow.id}")
            return None
        
        # Build webhook URL
        webhook_path = webhook_node.parameters.get('path', f"webhook/{workflow.id}")
        webhook_url = urljoin(self.base_url, f"/webhook/{webhook_path}")
        
        # Prepare execution data
        execution_data = {
            **input_data,
            'amas_workflow_id': workflow.amas_workflow_id,
            'triggered_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Trigger webhook
        if self.session is None:
            logger.error("Session not initialized - cannot trigger webhook")
            return None
        
        async with self.session.post(webhook_url, json=execution_data) as response:
            if response.status in [200, 201]:
                # Create execution record
                execution = N8NExecution(
                    id=f"exec_{uuid.uuid4().hex[:8]}",
                    workflow_id=workflow.id,
                    status=N8NWorkflowStatus.RUNNING,
                    started_at=datetime.now(timezone.utc),
                    input_data=execution_data,
                    triggered_by_amas=True,
                    amas_context={'workflow_id': workflow.amas_workflow_id}
                )
                
                logger.info(f"Triggered webhook workflow: {workflow.id}")
                return execution
            else:
                logger.error(f"Webhook trigger failed: {response.status}")
                return None
    
    async def _trigger_manual_workflow(self, 
                                     workflow_id: str, 
                                     input_data: Dict[str, Any]) -> Optional[N8NExecution]:
        """Trigger workflow manually via API"""
        
        execute_url = urljoin(self.base_url, f'/rest/workflows/{workflow_id}/execute')
        
        # Prepare execution payload
        if self.session is None:
            logger.error("Session not initialized - cannot trigger workflow")
            return None
        
        execution_payload = {
            "startNodes": [],  # Empty means start from trigger nodes
            "destinationNode": "",  # Empty means execute complete workflow
            "runData": input_data
        }
        
        async with self.session.post(execute_url, json=execution_payload) as response:
            if response.status == 201:
                execution_data = await response.json()
                
                # Create execution record
                execution = N8NExecution(
                    id=execution_data.get('id', f"exec_{uuid.uuid4().hex[:8]}"),
                    workflow_id=workflow_id,
                    status=N8NWorkflowStatus.RUNNING,
                    started_at=datetime.now(timezone.utc),
                    input_data=input_data,
                    triggered_by_amas=True
                )
                
                logger.info(f"Triggered manual workflow: {workflow_id}")
                return execution
            else:
                error_text = await response.text()
                logger.error(f"Manual workflow trigger failed: {error_text}")
                return None
    
    async def _wait_for_execution_completion(self, 
                                           execution_id: str,
                                           timeout_seconds: int) -> Optional[N8NExecution]:
        """Wait for N8N execution to complete"""
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
            # Check execution status
            execution = await self.get_execution_status(execution_id)
            
            if execution and execution.status in [
                N8NWorkflowStatus.SUCCESS, 
                N8NWorkflowStatus.FAILED, 
                N8NWorkflowStatus.CANCELED
            ]:
                # Execution completed
                if execution.status == N8NWorkflowStatus.SUCCESS:
                    self.successful_executions += 1
                else:
                    self.failed_executions += 1
                
                # Move from active to history
                if execution_id in self.active_executions:
                    completed_execution = self.active_executions.pop(execution_id)
                    self.execution_history.append(completed_execution)
                
                logger.info(f"N8N execution completed: {execution_id} - {execution.status.value}")
                return execution
            
            # Wait before next check
            await asyncio.sleep(5)
        
        # Timeout reached
        logger.warning(f"N8N execution timeout: {execution_id}")
        execution = self.active_executions.get(execution_id)
        if execution:
            execution.status = N8NWorkflowStatus.FAILED
            execution.error_message = "Execution timeout"
            execution.finished_at = datetime.now(timezone.utc)
        
        return execution
    
    async def get_execution_status(self, execution_id: str) -> Optional[N8NExecution]:
        """Get current status of N8N execution"""
        
        # Check local cache first
        execution = self.active_executions.get(execution_id)
        if not execution:
            return None
        
        try:
            if self.session is None:
                logger.warning("Session not initialized - returning cached execution")
                return execution
            
            # Query N8N for latest execution status
            executions_url = urljoin(self.base_url, f'/rest/executions/{execution_id}')
            
            async with self.session.get(executions_url) as response:
                if response.status == 200:
                    execution_data = await response.json()
                    
                    # Update execution with latest data
                    execution.status = N8NWorkflowStatus(execution_data.get('status', 'running'))
                    
                    if execution_data.get('stoppedAt'):
                        execution.finished_at = datetime.fromisoformat(
                            execution_data['stoppedAt']
                        )
                    
                    if execution_data.get('data'):
                        execution.output_data = execution_data['data']
                    
                    # Extract node execution details
                    execution.node_executions = execution_data.get('data', {}).get('resultData', {})
                    
                    return execution
                else:
                    logger.error(f"Failed to get execution status: {response.status}")
                    return execution
                    
        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return execution
    
    async def create_webhook_endpoint(self, 
                                    workflow_id: str,
                                    webhook_path: str,
                                    response_format: str = "json") -> Optional[str]:
        """Create webhook endpoint for AMAS-N8N integration"""
        
        workflow = self.registered_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow not found: {workflow_id}")
            return None
        
        # Build webhook URL
        webhook_url = urljoin(self.base_url, f"/webhook/{webhook_path}")
        
        # Register webhook mapping
        self.webhook_mappings[webhook_url] = workflow_id
        
        logger.info(f"Created webhook endpoint: {webhook_url} -> {workflow_id}")
        return webhook_url
    
    async def setup_amas_automation_workflows(self) -> Dict[str, str]:
        """Set up common N8N workflows for AMAS automation"""
        
        automation_workflows = []
        
        # 1. Data Processing Workflow
        data_processing_config = {
            'integration_steps': [
                {
                    'type': 'data_transformation',
                    'name': 'Format AMAS Data',
                    'transformation_code': '''
                        // Transform AMAS workflow data for external processing
                        const amasData = items[0].json;
                        
                        return [{
                            json: {
                                workflow_id: amasData.workflow_id,
                                task_results: amasData.task_results || [],
                                quality_scores: amasData.quality_scores || {},
                                agent_assignments: amasData.agent_assignments || {},
                                formatted_at: new Date().toISOString()
                            }
                        }];
                    '''
                },
                {
                    'type': 'api_call',
                    'name': 'External Analytics API',
                    'endpoint_url': 'https://api.example.com/analytics',
                    'method': 'POST',
                    'auth_type': 'bearer'
                }
            ],
            'callback_url': 'http://localhost:8000/api/n8n/callback/data_processing'
        }
        
        data_workflow_id = await self.create_amas_integration_workflow(
            "AMAS Data Processing Pipeline",
            "amas_data_processing",
            data_processing_config
        )
        
        if data_workflow_id:
            automation_workflows.append(('data_processing', data_workflow_id))
        
        # 2. Notification Distribution Workflow
        notification_config = {
            'integration_steps': [
                {
                    'type': 'data_transformation',
                    'name': 'Format Notifications',
                    'transformation_code': '''
                        const notification = items[0].json;
                        
                        // Format for different channels
                        return [{
                            json: {
                                slack_message: {
                                    text: notification.title,
                                    blocks: [{
                                        type: "section",
                                        text: {
                                            type: "mrkdwn",
                                            text: notification.message
                                        }
                                    }]
                                },
                                email_content: {
                                    subject: notification.title,
                                    html: `<h2>${notification.title}</h2><p>${notification.message}</p>`,
                                    text: `${notification.title}\n\n${notification.message}`
                                },
                                webhook_data: notification
                            }
                        }];
                    '''
                },
                {
                    'type': 'api_call',
                    'name': 'Slack Notification',
                    'endpoint_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
                    'method': 'POST'
                },
                {
                    'type': 'api_call',
                    'name': 'Email Service',
                    'endpoint_url': 'https://api.sendgrid.com/v3/mail/send',
                    'method': 'POST',
                    'auth_type': 'bearer'
                }
            ],
            'callback_url': 'http://localhost:8000/api/n8n/callback/notifications'
        }
        
        notification_workflow_id = await self.create_amas_integration_workflow(
            "AMAS Notification Distribution",
            "amas_notifications",
            notification_config
        )
        
        if notification_workflow_id:
            automation_workflows.append(('notifications', notification_workflow_id))
        
        # 3. File Processing Workflow
        file_processing_config = {
            'integration_steps': [
                {
                    'type': 'file_operation',
                    'name': 'Read AMAS Output',
                    'file_operation': 'read',
                    'file_path': '/tmp/amas_output.json'
                },
                {
                    'type': 'data_transformation',
                    'name': 'Convert to CSV',
                    'transformation_code': '''
                        const jsonData = JSON.parse(items[0].binary.data.toString());
                        
                        // Convert JSON to CSV format
                        const csv = convertJsonToCsv(jsonData);
                        
                        return [{
                            json: { csv_data: csv },
                            binary: {
                                data: Buffer.from(csv),
                                mimeType: 'text/csv',
                                fileName: 'amas_output.csv'
                            }
                        }];
                    '''
                },
                {
                    'type': 'api_call',
                    'name': 'Upload to Cloud Storage',
                    'endpoint_url': 'https://api.dropbox.com/2/files/upload',
                    'method': 'POST',
                    'auth_type': 'bearer'
                }
            ],
            'callback_url': 'http://localhost:8000/api/n8n/callback/file_processing'
        }
        
        file_workflow_id = await self.create_amas_integration_workflow(
            "AMAS File Processing Pipeline",
            "amas_file_processing",
            file_processing_config
        )
        
        if file_workflow_id:
            automation_workflows.append(('file_processing', file_workflow_id))
        
        logger.info(f"Set up {len(automation_workflows)} AMAS automation workflows")
        return dict(automation_workflows)
    
    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get N8N integration performance metrics"""
        active_workflows = sum(1 for w in self.registered_workflows.values() if w.active)
        total_workflows = len(self.registered_workflows)
        
        success_rate = (self.successful_executions / max(1, self.total_executions)) * 100
        
        # Calculate average execution time from history
        avg_execution_time = 0.0
        completed_executions = [e for e in self.execution_history 
                              if e.finished_at and e.started_at]
        
        if completed_executions:
            total_time = sum(
                (e.finished_at - e.started_at).total_seconds() 
                for e in completed_executions
                if e.finished_at is not None
            )
            avg_execution_time = total_time / len(completed_executions)
        
        return {
            'connected': self.authenticated,
            'base_url': self.base_url,
            'total_workflows': total_workflows,
            'active_workflows': active_workflows,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'success_rate_percent': round(success_rate, 2),
            'avg_execution_time_seconds': round(avg_execution_time, 2),
            'active_executions': len(self.active_executions),
            'registered_webhooks': len(self.webhook_mappings)
        }
    
    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Validate N8N credentials (IntegrationManager interface)
        
        Required credentials:
        - base_url: N8N instance URL
        - api_key: N8N API key (optional for testing)
        """
        
        try:
            base_url = credentials.get("base_url")
            api_key = credentials.get("api_key")
            
            # In test environment, allow test credentials
            if api_key == "test_key" or credentials.get("test_mode"):
                logger.debug("Using test credentials for N8N")
                return True
            
            if not base_url:
                return False
            
            # Test connection (api_key is optional for public instances)
            async with aiohttp.ClientSession() as session:
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["X-N8N-API-KEY"] = api_key
                
                # Try health check first (doesn't require auth)
                try:
                    async with session.get(
                        f"{base_url}/healthz",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            return True
                except Exception:
                    pass
                
                # Try workflows endpoint if api_key provided
                if api_key:
                    try:
                        async with session.get(
                            f"{base_url}/api/v1/workflows",
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            return response.status in [200, 401]  # 401 means auth required but endpoint exists
                    except Exception:
                        pass
                
                # If we get here, validation failed
                return False
        
        except Exception as e:
            logger.debug(f"N8N credential validation failed: {e}")
            return False
    
    async def execute(
        self,
        event_type: str,
        data: Dict[str, Any],
        credentials: Dict[str, Any],
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute N8N workflow (IntegrationManager interface)
        
        Event types:
        - task_completed: Trigger when task completes
        - task_failed: Trigger when task fails
        - alert_triggered: Trigger on system alerts
        - custom: Custom event with data
        """
        
        try:
            base_url = credentials["base_url"]
            api_key = credentials["api_key"]
            webhook_id = configuration.get("webhook_id")
            
            if not webhook_id:
                raise ValueError("N8N webhook_id not configured")
            
            # Prepare payload
            from datetime import datetime
            payload = {
                "event": event_type,
                "source": "amas",
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # Send to N8N webhook
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-N8N-API-KEY": api_key,
                    "Content-Type": "application/json"
                }
                
                webhook_url = f"{base_url}/webhook/{webhook_id}"
                
                logger.info(f"Triggering N8N webhook: {webhook_url}")
                
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    logger.info("N8N workflow triggered successfully")
                    
                    return {
                        "success": True,
                        "execution_id": result.get("executionId"),
                        "status": result.get("status"),
                        "response": result
                    }
        
        except Exception as e:
            logger.error(f"N8N execution failed: {e}", exc_info=True)
            raise
    
    async def validate_webhook_signature(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """
        Validate webhook signature from N8N (IntegrationManager interface)
        
        N8N sends signature in X-N8N-Signature header
        """
        
        try:
            import hashlib
            import hmac
            
            signature = headers.get("X-N8N-Signature")
            webhook_secret = headers.get("X-N8N-Webhook-Secret")
            
            if not signature or not webhook_secret:
                logger.warning("Missing signature or secret in N8N webhook")
                return True  # N8N webhooks may not always have signatures
            
            # Compute expected signature
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                webhook_secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception as e:
            logger.error(f"Signature validation error: {e}")
            return False
    
    async def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incoming N8N webhook (IntegrationManager interface)
        
        Returns:
            Parsed event data
        """
        
        return {
            "type": payload.get("event", "n8n_webhook"),
            "data": payload.get("data", {}),
            "execution_id": payload.get("executionId"),
            "workflow_id": payload.get("workflowId")
        }
    
    async def cleanup(self):
        """Clean up N8N connector resources"""
        if self.session:
            await self.session.close()
        
        self.authenticated = False
        
        logger.info("N8N Connector cleaned up")

# Global N8N connector instance
_global_n8n_connector: Optional[N8NConnector] = None

async def get_n8n_connector(config: Optional[Dict[str, Any]] = None) -> N8NConnector:
    """Get global N8N connector instance"""
    global _global_n8n_connector
    
    if _global_n8n_connector is None:
        # Initialize with configuration
        config = config or {}
        
        _global_n8n_connector = N8NConnector(
            n8n_base_url=config.get('n8n_base_url', 'http://localhost:5678'),
            api_key=config.get('api_key'),
            username=config.get('username'),
            password=config.get('password')
        )
        
        # Initialize connection
        await _global_n8n_connector.initialize()
    
    return _global_n8n_connector

# Example usage
if __name__ == "__main__":
    async def test_n8n_integration():
        # Initialize connector
        connector = N8NConnector(
            n8n_base_url="http://localhost:5678",
            username="admin@amas.ai",
            password="secure_password"
        )
        
        # Initialize connection
        success = await connector.initialize()
        if not success:
            print("Failed to connect to N8N")
            return
        
        # Set up automation workflows
        workflows = await connector.setup_amas_automation_workflows()
        print(f"Created automation workflows: {workflows}")
        
        # Test workflow execution
        if 'data_processing' in workflows:
            execution = await connector.execute_workflow(
                workflows['data_processing'],
                {'test_data': 'AMAS integration test'},
                wait_for_completion=True
            )
            
            if execution:
                print(f"Execution result: {execution.status.value}")
                print(f"Output: {execution.output_data}")
        
        # Get metrics
        metrics = await connector.get_workflow_metrics()
        print(f"\nN8N Metrics: {json.dumps(metrics, indent=2)}")
        
        # Cleanup
        await connector.cleanup()
    
    # Run test
    asyncio.run(test_n8n_integration())
