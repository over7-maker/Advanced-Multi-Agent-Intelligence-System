"""
Dynamic Tool Discovery and Registry System

Provides intelligent tool discovery, validation, and integration
with automatic capability detection and performance optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Type, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
import inspect
import importlib
import pkgutil
from pathlib import Path
import yaml
import jsonschema
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ToolCategory(str, Enum):
    # Data & Analytics
    DATA_PROCESSING = "data_processing"
    ANALYTICS = "analytics"
    VISUALIZATION = "visualization"
    
    # Communication & Collaboration
    COMMUNICATION = "communication"
    NOTIFICATION = "notification"
    COLLABORATION = "collaboration"
    
    # Content & Media
    CONTENT_CREATION = "content_creation"
    MEDIA_PROCESSING = "media_processing"
    DOCUMENT_GENERATION = "document_generation"
    
    # Integration & Automation
    API_INTEGRATION = "api_integration"
    WORKFLOW_AUTOMATION = "workflow_automation"
    FILE_OPERATIONS = "file_operations"
    
    # Intelligence & Research
    WEB_SCRAPING = "web_scraping"
    RESEARCH_TOOLS = "research_tools"
    AI_SERVICES = "ai_services"
    
    # Security & Compliance
    SECURITY = "security"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    
    # Development & DevOps
    CODE_ANALYSIS = "code_analysis"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class ToolCapability(str, Enum):
    # Input capabilities
    TEXT_INPUT = "text_input"
    FILE_INPUT = "file_input"
    API_INPUT = "api_input"
    STREAM_INPUT = "stream_input"
    
    # Processing capabilities
    ASYNC_PROCESSING = "async_processing"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME_PROCESSING = "real_time_processing"
    PARALLEL_PROCESSING = "parallel_processing"
    
    # Output capabilities
    TEXT_OUTPUT = "text_output"
    FILE_OUTPUT = "file_output"
    API_OUTPUT = "api_output"
    STREAM_OUTPUT = "stream_output"
    VISUALIZATION_OUTPUT = "visualization_output"
    
    # Special capabilities
    AUTHENTICATION = "authentication"
    RATE_LIMITED = "rate_limited"
    CACHED = "cached"
    STATEFUL = "stateful"

@dataclass
class ToolParameter:
    """Represents a tool parameter definition"""
    name: str
    type: str  # 'string', 'integer', 'boolean', 'array', 'object'
    description: str
    required: bool = True
    default: Any = None
    validation_schema: Optional[Dict[str, Any]] = None
    
    # UI hints
    display_name: Optional[str] = None
    placeholder: Optional[str] = None
    options: Optional[List[Any]] = None  # For select/enum parameters
    sensitive: bool = False  # For passwords/tokens

@dataclass
class ToolDefinition:
    """Complete tool definition with metadata and capabilities"""
    id: str
    name: str
    description: str
    category: ToolCategory
    
    # Capabilities and requirements
    capabilities: Set[ToolCapability] = field(default_factory=set)
    parameters: List[ToolParameter] = field(default_factory=list)
    required_credentials: List[str] = field(default_factory=list)
    
    # Integration details
    module_path: str = ""
    class_name: str = ""
    function_name: str = ""
    
    # Performance characteristics
    avg_execution_time_seconds: float = 1.0
    max_execution_time_seconds: float = 300.0
    cost_per_execution: float = 0.001
    rate_limit_per_minute: Optional[int] = None
    
    # Quality and reliability
    success_rate: float = 0.95
    quality_score: float = 0.90
    uptime_percentage: float = 99.5
    
    # Metadata
    version: str = "1.0.0"
    author: str = "AMAS"
    documentation_url: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Usage statistics
    usage_count: int = 0
    last_used: Optional[datetime] = None
    user_ratings: List[float] = field(default_factory=list)
    
    def get_average_rating(self) -> float:
        """Calculate average user rating"""
        return sum(self.user_ratings) / len(self.user_ratings) if self.user_ratings else 0.0
    
    def is_compatible_with_agent(self, agent_specialty: str) -> bool:
        """Check if tool is compatible with agent specialty"""
        # Define compatibility mapping
        compatibility_map = {
            'academic_researcher': [ToolCategory.RESEARCH_TOOLS, ToolCategory.DATA_PROCESSING],
            'web_intelligence_gatherer': [ToolCategory.WEB_SCRAPING, ToolCategory.API_INTEGRATION],
            'data_analyst': [ToolCategory.DATA_PROCESSING, ToolCategory.ANALYTICS, ToolCategory.VISUALIZATION],
            'graphics_designer': [ToolCategory.VISUALIZATION, ToolCategory.MEDIA_PROCESSING],
            'content_writer': [ToolCategory.CONTENT_CREATION, ToolCategory.DOCUMENT_GENERATION],
            'fact_checker': [ToolCategory.RESEARCH_TOOLS, ToolCategory.API_INTEGRATION],
            'quality_controller': [ToolCategory.AUDIT, ToolCategory.COMPLIANCE]
        }
        
        compatible_categories = compatibility_map.get(agent_specialty, [])
        return self.category in compatible_categories

@dataclass
class ToolExecution:
    """Represents a tool execution instance"""
    id: str
    tool_id: str
    agent_id: str
    
    # Execution context
    parameters: Dict[str, Any]
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Status tracking
    status: str = "pending"  # pending, running, completed, failed, timeout
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and errors
    result: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    
    # Resource usage
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Quality metrics
    output_quality_score: Optional[float] = None
    user_satisfaction: Optional[float] = None

class BaseTool(ABC):
    """Base class for all AMAS tools"""
    
    @abstractmethod
    async def execute(self, 
                     parameters: Dict[str, Any],
                     credentials: Dict[str, str] = None,
                     context: Dict[str, Any] = None) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Get tool definition including metadata and parameters"""
        pass
    
    async def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate tool parameters before execution"""
        definition = self.get_definition()
        
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in parameters:
                raise ValueError(f"Required parameter missing: {param.name}")
            
            # Validate parameter type and schema if provided
            if param.name in parameters and param.validation_schema:
                try:
                    jsonschema.validate(parameters[param.name], param.validation_schema)
                except jsonschema.ValidationError as e:
                    raise ValueError(f"Parameter validation failed for {param.name}: {e.message}")
        
        return True
    
    async def get_cost_estimate(self, parameters: Dict[str, Any]) -> float:
        """Estimate cost for tool execution with given parameters"""
        definition = self.get_definition()
        return definition.cost_per_execution
    
    async def get_time_estimate(self, parameters: Dict[str, Any]) -> float:
        """Estimate execution time for tool with given parameters"""
        definition = self.get_definition()
        return definition.avg_execution_time_seconds

class ToolRegistry:
    """Dynamic tool discovery and registration system"""
    
    def __init__(self, tool_directories: List[str] = None):
        self.tool_directories = tool_directories or ['src/amas/tools']
        
        # Tool storage
        self.registered_tools: Dict[str, ToolDefinition] = {}
        self.tool_instances: Dict[str, BaseTool] = {}
        
        # Execution tracking
        self.active_executions: Dict[str, ToolExecution] = {}
        self.execution_history: List[ToolExecution] = []
        
        # Performance metrics
        self.total_executions: int = 0
        self.successful_executions: int = 0
        self.failed_executions: int = 0
        
        # Tool discovery state
        self.discovery_complete = False
        self.last_discovery_scan: Optional[datetime] = None
        
        logger.info(f"Tool Registry initialized with directories: {self.tool_directories}")
    
    async def discover_tools(self, force_refresh: bool = False) -> int:
        """Discover all available tools in configured directories"""
        
        if self.discovery_complete and not force_refresh:
            logger.info("Tool discovery already complete - use force_refresh=True to rescan")
            return len(self.registered_tools)
        
        logger.info("Starting tool discovery...")
        discovered_count = 0
        
        try:
            # Scan tool directories
            for directory in self.tool_directories:
                directory_path = Path(directory)
                if directory_path.exists():
                    discovered_count += await self._scan_directory(directory_path)
            
            # Load tools from configuration files
            discovered_count += await self._load_tool_configs()
            
            # Validate all discovered tools
            await self._validate_discovered_tools()
            
            self.discovery_complete = True
            self.last_discovery_scan = datetime.now(timezone.utc)
            
            logger.info(f"Tool discovery complete: {discovered_count} tools found")
            return discovered_count
            
        except Exception as e:
            logger.error(f"Error during tool discovery: {e}")
            return 0
    
    async def _scan_directory(self, directory: Path) -> int:
        """Scan directory for tool implementations"""
        discovered = 0
        
        # Look for Python tool modules
        for python_file in directory.rglob('*.py'):
            if python_file.name.startswith('_'):
                continue  # Skip private modules
                
            try:
                # Import module dynamically
                module_name = self._path_to_module_name(python_file, directory)
                module = importlib.import_module(module_name)
                
                # Find BaseTool subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseTool) and 
                        obj != BaseTool):
                        
                        # Create tool instance and register
                        tool_instance = obj()
                        tool_definition = tool_instance.get_definition()
                        
                        # Update definition with module information
                        tool_definition.module_path = module_name
                        tool_definition.class_name = name
                        
                        await self._register_tool(tool_definition, tool_instance)
                        discovered += 1
                        
                        logger.debug(f"Discovered tool: {tool_definition.name} ({tool_definition.id})")
                        
            except Exception as e:
                logger.warning(f"Error importing {python_file}: {e}")
                continue
        
        return discovered
    
    def _path_to_module_name(self, file_path: Path, base_path: Path) -> str:
        """Convert file path to Python module name"""
        relative_path = file_path.relative_to(base_path.parent)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return '.'.join(module_parts)
    
    async def _load_tool_configs(self) -> int:
        """Load tools from YAML configuration files"""
        discovered = 0
        
        # Look for tool configuration files
        config_files = []
        for directory in self.tool_directories:
            config_dir = Path(directory) / 'configs'
            if config_dir.exists():
                config_files.extend(config_dir.glob('*.yaml'))
                config_files.extend(config_dir.glob('*.yml'))
        
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                if 'tools' in config_data:
                    for tool_config in config_data['tools']:
                        definition = self._parse_tool_config(tool_config)
                        if definition:
                            await self._register_tool_definition(definition)
                            discovered += 1
                            
            except Exception as e:
                logger.warning(f"Error loading tool config {config_file}: {e}")
                continue
        
        return discovered
    
    def _parse_tool_config(self, config: Dict[str, Any]) -> Optional[ToolDefinition]:
        """Parse tool configuration into ToolDefinition"""
        try:
            # Parse parameters
            parameters = []
            for param_config in config.get('parameters', []):
                param = ToolParameter(
                    name=param_config['name'],
                    type=param_config['type'],
                    description=param_config['description'],
                    required=param_config.get('required', True),
                    default=param_config.get('default'),
                    validation_schema=param_config.get('validation'),
                    display_name=param_config.get('display_name'),
                    placeholder=param_config.get('placeholder'),
                    options=param_config.get('options'),
                    sensitive=param_config.get('sensitive', False)
                )
                parameters.append(param)
            
            # Parse capabilities
            capabilities = set()
            for cap_str in config.get('capabilities', []):
                try:
                    capabilities.add(ToolCapability(cap_str))
                except ValueError:
                    logger.warning(f"Unknown capability: {cap_str}")
            
            definition = ToolDefinition(
                id=config['id'],
                name=config['name'],
                description=config['description'],
                category=ToolCategory(config['category']),
                capabilities=capabilities,
                parameters=parameters,
                required_credentials=config.get('required_credentials', []),
                module_path=config.get('module_path', ''),
                class_name=config.get('class_name', ''),
                function_name=config.get('function_name', ''),
                avg_execution_time_seconds=config.get('avg_execution_time', 1.0),
                max_execution_time_seconds=config.get('max_execution_time', 300.0),
                cost_per_execution=config.get('cost_per_execution', 0.001),
                rate_limit_per_minute=config.get('rate_limit', None),
                version=config.get('version', '1.0.0'),
                author=config.get('author', 'Unknown'),
                documentation_url=config.get('documentation_url')
            )
            
            return definition
            
        except Exception as e:
            logger.error(f"Error parsing tool config: {e}")
            return None
    
    async def _register_tool(self, definition: ToolDefinition, tool_instance: BaseTool):
        """Register a tool with its instance"""
        self.registered_tools[definition.id] = definition
        self.tool_instances[definition.id] = tool_instance
        
        logger.info(f"Registered tool: {definition.name} ({definition.id})")
    
    async def _register_tool_definition(self, definition: ToolDefinition):
        """Register tool definition (for config-based tools)"""
        self.registered_tools[definition.id] = definition
        
        logger.info(f"Registered tool definition: {definition.name} ({definition.id})")
    
    async def _validate_discovered_tools(self):
        """Validate all discovered tools for consistency and completeness"""
        validation_errors = []
        
        for tool_id, definition in self.registered_tools.items():
            try:
                # Check required fields
                if not definition.name or not definition.description:
                    validation_errors.append(f"Tool {tool_id} missing name or description")
                
                # Validate parameters
                for param in definition.parameters:
                    if not param.name or not param.description:
                        validation_errors.append(f"Tool {tool_id} has invalid parameter: {param.name}")
                
                # Check if tool instance exists for implemented tools
                if definition.module_path and tool_id not in self.tool_instances:
                    validation_errors.append(f"Tool {tool_id} has module but no instance")
                
                # Validate performance metrics
                if definition.success_rate < 0 or definition.success_rate > 1:
                    validation_errors.append(f"Tool {tool_id} has invalid success rate")
                
            except Exception as e:
                validation_errors.append(f"Tool {tool_id} validation error: {e}")
        
        if validation_errors:
            logger.warning(f"Tool validation found {len(validation_errors)} issues:")
            for error in validation_errors[:10]:  # Log first 10 errors
                logger.warning(f"  - {error}")
        else:
            logger.info("All tools passed validation")
    
    async def execute_tool(self,
                          tool_id: str,
                          parameters: Dict[str, Any],
                          agent_id: str,
                          credentials: Dict[str, str] = None,
                          timeout_override: float = None) -> ToolExecution:
        """Execute a tool with full tracking and monitoring"""
        
        execution_id = f"tool_exec_{uuid.uuid4().hex[:8]}"
        
        # Get tool definition
        definition = self.registered_tools.get(tool_id)
        if not definition:
            raise ValueError(f"Tool not found: {tool_id}")
        
        # Create execution record
        execution = ToolExecution(
            id=execution_id,
            tool_id=tool_id,
            agent_id=agent_id,
            parameters=parameters,
            credentials=credentials or {}
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            # Validate parameters
            tool_instance = self.tool_instances.get(tool_id)
            if tool_instance:
                await tool_instance.validate_parameters(parameters)
            
            # Start execution
            execution.status = "running"
            execution.started_at = datetime.now(timezone.utc)
            
            # Execute with timeout
            timeout = timeout_override or definition.max_execution_time_seconds
            
            if tool_instance:
                # Execute tool instance
                result = await asyncio.wait_for(
                    tool_instance.execute(parameters, credentials or {}),
                    timeout=timeout
                )
            else:
                # Execute config-based tool (external API, etc.)
                result = await self._execute_external_tool(definition, parameters, credentials or {})
            
            # Record successful completion
            execution.status = "completed"
            execution.completed_at = datetime.now(timezone.utc)
            execution.result = result
            execution.execution_time_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()
            
            # Update metrics
            self.total_executions += 1
            self.successful_executions += 1
            definition.usage_count += 1
            definition.last_used = execution.completed_at
            
            logger.info(f"Tool execution successful: {tool_id} ({execution_id})")
            
        except asyncio.TimeoutError:
            execution.status = "timeout"
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_message = f"Execution timeout after {timeout}s"
            
            self.total_executions += 1
            self.failed_executions += 1
            
            logger.error(f"Tool execution timeout: {tool_id} ({execution_id})")
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_message = str(e)
            
            self.total_executions += 1
            self.failed_executions += 1
            
            logger.error(f"Tool execution failed: {tool_id} ({execution_id}): {e}")
        
        finally:
            # Move execution to history
            if execution_id in self.active_executions:
                completed_execution = self.active_executions.pop(execution_id)
                self.execution_history.append(completed_execution)
                
                # Keep only recent history (last 1000 executions)
                if len(self.execution_history) > 1000:
                    self.execution_history = self.execution_history[-1000:]
        
        return execution
    
    async def _execute_external_tool(self, 
                                   definition: ToolDefinition,
                                   parameters: Dict[str, Any],
                                   credentials: Dict[str, str]) -> Any:
        """Execute external tool via API or subprocess"""
        
        # This would implement execution of external tools
        # For now, simulate successful execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "status": "completed",
            "message": f"External tool {definition.name} executed successfully",
            "data": parameters,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def search_tools(self,
                    query: str = None,
                    category: ToolCategory = None,
                    capabilities: List[ToolCapability] = None,
                    agent_specialty: str = None,
                    max_cost: float = None,
                    max_time: float = None,
                    min_quality: float = None) -> List[ToolDefinition]:
        """Search tools with filters and ranking"""
        
        results = list(self.registered_tools.values())
        
        # Apply filters
        if category:
            results = [tool for tool in results if tool.category == category]
        
        if capabilities:
            results = [tool for tool in results 
                      if any(cap in tool.capabilities for cap in capabilities)]
        
        if agent_specialty:
            results = [tool for tool in results 
                      if tool.is_compatible_with_agent(agent_specialty)]
        
        if max_cost is not None:
            results = [tool for tool in results if tool.cost_per_execution <= max_cost]
        
        if max_time is not None:
            results = [tool for tool in results if tool.avg_execution_time_seconds <= max_time]
        
        if min_quality is not None:
            results = [tool for tool in results if tool.quality_score >= min_quality]
        
        # Text search in name and description
        if query:
            query_lower = query.lower()
            results = [tool for tool in results 
                      if query_lower in tool.name.lower() or 
                         query_lower in tool.description.lower()]
        
        # Rank results by relevance and quality
        results.sort(key=lambda t: (
            t.quality_score * 0.4 +
            t.success_rate * 0.3 +
            (1.0 - min(t.cost_per_execution / 0.1, 1.0)) * 0.2 +  # Lower cost = higher rank
            (t.usage_count / max(1, max(tool.usage_count for tool in results))) * 0.1
        ), reverse=True)
        
        return results
    
    def get_tools_for_agent(self, agent_specialty: str) -> List[ToolDefinition]:
        """Get recommended tools for specific agent specialty"""
        compatible_tools = self.search_tools(agent_specialty=agent_specialty)
        
        # Sort by compatibility score and usage
        compatible_tools.sort(key=lambda t: (
            t.quality_score * 0.5 +
            t.success_rate * 0.3 +
            (t.usage_count / max(1, max(tool.usage_count for tool in compatible_tools))) * 0.2
        ), reverse=True)
        
        return compatible_tools[:20]  # Return top 20 tools
    
    def get_tool_recommendations(self, 
                               task_description: str,
                               agent_specialty: str,
                               context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """Get AI-powered tool recommendations for a task"""
        
        # Simple keyword-based matching (could be enhanced with ML)
        task_lower = task_description.lower()
        context = context or {}
        
        # Keyword to category mapping
        keyword_categories = {
            'analyze': ToolCategory.ANALYTICS,
            'data': ToolCategory.DATA_PROCESSING,
            'chart': ToolCategory.VISUALIZATION,
            'graph': ToolCategory.VISUALIZATION,
            'email': ToolCategory.COMMUNICATION,
            'notify': ToolCategory.NOTIFICATION,
            'write': ToolCategory.CONTENT_CREATION,
            'document': ToolCategory.DOCUMENT_GENERATION,
            'api': ToolCategory.API_INTEGRATION,
            'scrape': ToolCategory.WEB_SCRAPING,
            'research': ToolCategory.RESEARCH_TOOLS,
            'file': ToolCategory.FILE_OPERATIONS
        }
        
        # Find relevant categories
        relevant_categories = set()
        for keyword, category in keyword_categories.items():
            if keyword in task_lower:
                relevant_categories.add(category)
        
        # Search tools in relevant categories
        recommendations = []
        for category in relevant_categories:
            category_tools = self.search_tools(
                category=category,
                agent_specialty=agent_specialty,
                max_time=context.get('max_execution_time', 300),
                min_quality=context.get('min_quality', 0.80)
            )
            recommendations.extend(category_tools[:5])  # Top 5 per category
        
        # Remove duplicates and sort by overall score
        unique_recommendations = list({tool.id: tool for tool in recommendations}.values())
        unique_recommendations.sort(key=lambda t: t.quality_score * t.success_rate, reverse=True)
        
        return unique_recommendations[:10]  # Return top 10 recommendations
    
    def get_registry_metrics(self) -> Dict[str, Any]:
        """Get tool registry performance metrics"""
        total_tools = len(self.registered_tools)
        active_executions = len(self.active_executions)
        
        success_rate = (self.successful_executions / max(1, self.total_executions)) * 100
        
        # Category distribution
        category_counts = {}
        for tool in self.registered_tools.values():
            category = tool.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Top used tools
        top_tools = sorted(
            self.registered_tools.values(),
            key=lambda t: t.usage_count,
            reverse=True
        )[:5]
        
        top_tools_data = [{
            'id': tool.id,
            'name': tool.name,
            'usage_count': tool.usage_count,
            'quality_score': tool.quality_score
        } for tool in top_tools]
        
        return {
            'discovery_complete': self.discovery_complete,
            'last_discovery_scan': self.last_discovery_scan.isoformat() if self.last_discovery_scan else None,
            'total_tools': total_tools,
            'active_executions': active_executions,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'success_rate_percent': round(success_rate, 2),
            'category_distribution': category_counts,
            'top_used_tools': top_tools_data
        }
    
    async def get_tool_performance_analytics(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed performance analytics for specific tool"""
        
        definition = self.registered_tools.get(tool_id)
        if not definition:
            return None
        
        # Get execution history for this tool
        tool_executions = [e for e in self.execution_history if e.tool_id == tool_id]
        
        if not tool_executions:
            return {
                'tool_id': tool_id,
                'tool_name': definition.name,
                'total_executions': 0,
                'success_rate': 0,
                'avg_execution_time': definition.avg_execution_time_seconds,
                'avg_quality_score': definition.quality_score
            }
        
        # Calculate metrics
        successful = len([e for e in tool_executions if e.status == "completed"])
        success_rate = (successful / len(tool_executions)) * 100
        
        execution_times = [e.execution_time_seconds for e in tool_executions 
                          if e.execution_time_seconds is not None]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        quality_scores = [e.output_quality_score for e in tool_executions 
                         if e.output_quality_score is not None]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else definition.quality_score
        
        # Recent performance (last 30 days)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        recent_executions = [e for e in tool_executions 
                           if e.started_at and e.started_at > recent_cutoff]
        
        return {
            'tool_id': tool_id,
            'tool_name': definition.name,
            'total_executions': len(tool_executions),
            'success_rate_percent': round(success_rate, 2),
            'avg_execution_time_seconds': round(avg_execution_time, 2),
            'avg_quality_score': round(avg_quality, 3),
            'recent_executions_30d': len(recent_executions),
            'cost_per_execution': definition.cost_per_execution,
            'last_used': definition.last_used.isoformat() if definition.last_used else None,
            'user_rating': round(definition.get_average_rating(), 2)
        }
    
    async def get_execution_history(self, 
                                  tool_id: str = None,
                                  agent_id: str = None,
                                  limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history with optional filtering"""
        
        history = list(self.execution_history)
        
        # Apply filters
        if tool_id:
            history = [e for e in history if e.tool_id == tool_id]
        
        if agent_id:
            history = [e for e in history if e.agent_id == agent_id]
        
        # Sort by execution time (most recent first)
        history.sort(key=lambda e: e.started_at or datetime.min, reverse=True)
        
        # Limit results
        history = history[:limit]
        
        # Convert to serializable format
        return [{
            'id': e.id,
            'tool_id': e.tool_id,
            'agent_id': e.agent_id,
            'status': e.status,
            'started_at': e.started_at.isoformat() if e.started_at else None,
            'completed_at': e.completed_at.isoformat() if e.completed_at else None,
            'execution_time_seconds': e.execution_time_seconds,
            'error_message': e.error_message,
            'output_quality_score': e.output_quality_score
        } for e in history]

# Global tool registry instance
_global_tool_registry: Optional[ToolRegistry] = None

def get_tool_registry() -> ToolRegistry:
    """Get global tool registry instance"""
    global _global_tool_registry
    if _global_tool_registry is None:
        _global_tool_registry = ToolRegistry()
    return _global_tool_registry

# Example tool implementation
class WebScrapingTool(BaseTool):
    """Example web scraping tool implementation"""
    
    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            id="web_scraper_basic",
            name="Basic Web Scraper",
            description="Extract content from web pages with CSS selectors",
            category=ToolCategory.WEB_SCRAPING,
            capabilities={
                ToolCapability.TEXT_INPUT,
                ToolCapability.TEXT_OUTPUT,
                ToolCapability.ASYNC_PROCESSING,
                ToolCapability.RATE_LIMITED
            },
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="URL to scrape",
                    required=True,
                    validation_schema={
                        "type": "string",
                        "format": "uri"
                    }
                ),
                ToolParameter(
                    name="selector",
                    type="string",
                    description="CSS selector for content extraction",
                    required=False,
                    default="body"
                ),
                ToolParameter(
                    name="extract_links",
                    type="boolean",
                    description="Extract all links from the page",
                    required=False,
                    default=False
                )
            ],
            avg_execution_time_seconds=2.5,
            max_execution_time_seconds=30.0,
            cost_per_execution=0.002,
            rate_limit_per_minute=30,
            success_rate=0.88,
            quality_score=0.85
        )
    
    async def execute(self, 
                     parameters: Dict[str, Any],
                     credentials: Dict[str, str] = None,
                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute web scraping"""
        url = parameters['url']
        selector = parameters.get('selector', 'body')
        extract_links = parameters.get('extract_links', False)
        
        # Simulate web scraping (in real implementation, would use aiohttp + BeautifulSoup)
        await asyncio.sleep(1)  # Simulate network request
        
        return {
            'url': url,
            'content': f"Scraped content from {url} using selector '{selector}'",
            'links': ['http://example.com/link1', 'http://example.com/link2'] if extract_links else [],
            'word_count': 1250,
            'extraction_quality': 0.87,
            'scraped_at': datetime.now(timezone.utc).isoformat()
        }
