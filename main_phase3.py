"""
AMAS Intelligence System - Phase 3 Enhanced Main Application
Complete integration with advanced workflow capabilities, real-time monitoring, and performance optimization
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/amas_phase3.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import core components
from core.orchestrator import IntelligenceOrchestrator
from core.integration_manager import IntegrationManager
from services.service_manager import ServiceManager
from services.database_service import DatabaseService
from services.security_service import SecurityService
from services.monitoring_service import MonitoringService
from services.performance_service import PerformanceService

# Import agents
from agents.osint.osint_agent import OSINTAgent
from agents.investigation.investigation_agent import InvestigationAgent
from agents.forensics.forensics_agent import ForensicsAgent
from agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from agents.reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from agents.metadata.metadata_agent import MetadataAgent
from agents.reporting.reporting_agent import ReportingAgent
from agents.technology_monitor.technology_monitor_agent import TechnologyMonitorAgent

class AMASIntelligenceSystemPhase3:
    """Enhanced AMAS Intelligence System with Phase 3 capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator = None
        self.integration_manager = None
        self.agents = {}
        self.service_manager = None
        self.database_service = None
        self.security_service = None
        self.monitoring_service = None
        self.performance_service = None
        
        # Phase 3 specific components
        self.workflow_engine = None
        self.real_time_monitoring = None
        self.performance_optimization = None
        
    async def initialize(self):
        """Initialize the enhanced AMAS system with Phase 3 capabilities"""
        try:
            logger.info("Initializing AMAS Intelligence System Phase 3...")
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize Phase 3 services
            await self._initialize_phase3_services()
            
            # Initialize orchestrator with enhanced capabilities
            await self._initialize_enhanced_orchestrator()
            
            # Initialize integration manager
            await self._initialize_integration_manager()
            
            # Initialize specialized agents
            await self._initialize_enhanced_agents()
            
            # Initialize workflow engine
            await self._initialize_workflow_engine()
            
            # Initialize real-time monitoring
            await self._initialize_real_time_monitoring()
            
            # Initialize performance optimization
            await self._initialize_performance_optimization()
            
            # Start system monitoring
            await self._start_system_monitoring()
            
            logger.info("AMAS Intelligence System Phase 3 initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AMAS system Phase 3: {e}")
            raise
    
    async def _initialize_core_services(self):
        """Initialize core services"""
        try:
            logger.info("Initializing core services...")
            
            # Initialize service manager
            self.service_manager = ServiceManager(self.config)
            await self.service_manager.initialize_all_services()
            
            # Initialize database service
            self.database_service = DatabaseService(self.config)
            await self.database_service.initialize()
            
            # Initialize security service
            self.security_service = SecurityService(self.config)
            await self.security_service.initialize()
            
            logger.info("Core services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core services: {e}")
            raise
    
    async def _initialize_phase3_services(self):
        """Initialize Phase 3 services"""
        try:
            logger.info("Initializing Phase 3 services...")
            
            # Initialize monitoring service
            self.monitoring_service = MonitoringService(self.config)
            await self.monitoring_service.initialize()
            
            # Initialize performance service
            self.performance_service = PerformanceService(self.config)
            await self.performance_service.initialize()
            
            logger.info("Phase 3 services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 3 services: {e}")
            raise
    
    async def _initialize_enhanced_orchestrator(self):
        """Initialize enhanced orchestrator"""
        try:
            logger.info("Initializing enhanced orchestrator...")
            
            # Initialize orchestrator with all services
            self.orchestrator = IntelligenceOrchestrator(
                llm_service=self.service_manager.get_llm_service(),
                vector_service=self.service_manager.get_vector_service(),
                knowledge_graph=self.service_manager.get_knowledge_graph_service(),
                security_service=self.security_service
            )
            
            logger.info("Enhanced orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced orchestrator: {e}")
            raise
    
    async def _initialize_integration_manager(self):
        """Initialize integration manager"""
        try:
            logger.info("Initializing integration manager...")
            
            # Initialize integration manager
            self.integration_manager = IntegrationManager(
                orchestrator=self.orchestrator,
                service_manager=self.service_manager,
                database_service=self.database_service,
                security_service=self.security_service
            )
            
            # Initialize complete system integration
            await self.integration_manager.initialize_integration()
            
            logger.info("Integration manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize integration manager: {e}")
            raise
    
    async def _initialize_enhanced_agents(self):
        """Initialize enhanced agents with Phase 3 capabilities"""
        try:
            logger.info("Initializing enhanced agents...")
            
            # Create agent instances with enhanced capabilities
            agents_config = [
                (OSINTAgent, "osint_001", "Enhanced OSINT Agent"),
                (InvestigationAgent, "investigation_001", "Enhanced Investigation Agent"),
                (ForensicsAgent, "forensics_001", "Enhanced Forensics Agent"),
                (DataAnalysisAgent, "data_analysis_001", "Enhanced Data Analysis Agent"),
                (ReverseEngineeringAgent, "reverse_engineering_001", "Enhanced Reverse Engineering Agent"),
                (MetadataAgent, "metadata_001", "Enhanced Metadata Agent"),
                (ReportingAgent, "reporting_001", "Enhanced Reporting Agent"),
                (TechnologyMonitorAgent, "technology_monitor_001", "Enhanced Technology Monitor Agent")
            ]
            
            for agent_class, agent_id, agent_name in agents_config:
                agent = agent_class(
                    agent_id=agent_id,
                    name=agent_name,
                    llm_service=self.service_manager.get_llm_service(),
                    vector_service=self.service_manager.get_vector_service(),
                    knowledge_graph=self.service_manager.get_knowledge_graph_service(),
                    security_service=self.security_service
                )
                
                # Register agent with orchestrator
                await self.orchestrator.register_agent(agent)
                self.agents[agent_id] = agent
                
                # Store agent in database
                await self.database_service.store_agent({
                    'agent_id': agent_id,
                    'name': agent_name,
                    'capabilities': agent.capabilities,
                    'status': 'active'
                })
                
                logger.info(f"Registered enhanced {agent_name} with ID {agent_id}")
            
            logger.info("Enhanced agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced agents: {e}")
            raise
    
    async def _initialize_workflow_engine(self):
        """Initialize enhanced workflow engine"""
        try:
            logger.info("Initializing enhanced workflow engine...")
            
            # The workflow engine is integrated into the integration manager
            self.workflow_engine = self.integration_manager
            
            logger.info("Enhanced workflow engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow engine: {e}")
            raise
    
    async def _initialize_real_time_monitoring(self):
        """Initialize real-time monitoring"""
        try:
            logger.info("Initializing real-time monitoring...")
            
            # Real-time monitoring is handled by the monitoring service
            self.real_time_monitoring = self.monitoring_service
            
            logger.info("Real-time monitoring initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize real-time monitoring: {e}")
            raise
    
    async def _initialize_performance_optimization(self):
        """Initialize performance optimization"""
        try:
            logger.info("Initializing performance optimization...")
            
            # Performance optimization is handled by the performance service
            self.performance_optimization = self.performance_service
            
            logger.info("Performance optimization initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance optimization: {e}")
            raise
    
    async def _start_system_monitoring(self):
        """Start system monitoring"""
        try:
            logger.info("Starting system monitoring...")
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_system_health())
            asyncio.create_task(self._monitor_performance())
            asyncio.create_task(self._monitor_workflows())
            
            logger.info("System monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {e}")
            raise
    
    async def _monitor_system_health(self):
        """Monitor system health"""
        while True:
            try:
                # Get system health status
                health_status = await self.integration_manager.get_integration_status()
                
                # Log health status
                if health_status['integration_status'] != 'connected':
                    logger.warning(f"System health issue: {health_status}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"System health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_performance(self):
        """Monitor system performance"""
        while True:
            try:
                # Get performance status
                performance_status = await self.performance_service.get_performance_status()
                
                # Log performance metrics
                logger.info(f"Performance status: {performance_status}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_workflows(self):
        """Monitor workflow executions"""
        while True:
            try:
                # Get active workflows
                active_workflows = len(self.integration_manager.active_workflows)
                
                if active_workflows > 0:
                    logger.info(f"Active workflows: {active_workflows}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Workflow monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def submit_advanced_task(self, task_data: Dict[str, Any]) -> str:
        """Submit an advanced intelligence task"""
        try:
            # Use performance service to select optimal agent
            agent_id = await self.performance_service.select_agent(task_data.get('type', 'general'))
            
            # Submit task through orchestrator
            task_id = await self.orchestrator.submit_task(
                task_type=task_data.get('type', 'general'),
                description=task_data.get('description', ''),
                parameters=task_data.get('parameters', {}),
                priority=task_data.get('priority', 2)
            )
            
            logger.info(f"Advanced task {task_id} submitted to agent {agent_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error submitting advanced task: {e}")
            raise
    
    async def execute_advanced_workflow(self, workflow_type: str, parameters: Dict[str, Any], user_id: str = None) -> str:
        """Execute an advanced workflow"""
        try:
            # Execute workflow through integration manager
            execution_id = await self.integration_manager.execute_advanced_workflow(
                workflow_id=workflow_type,
                parameters=parameters,
                user_id=user_id
            )
            
            logger.info(f"Advanced workflow {workflow_type} execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing advanced workflow: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get integration status
            integration_status = await self.integration_manager.get_integration_status()
            
            # Get monitoring status
            monitoring_status = await self.monitoring_service.get_monitoring_status()
            
            # Get performance status
            performance_status = await self.performance_service.get_performance_status()
            
            # Get orchestrator status
            orchestrator_status = await self.orchestrator.get_system_status()
            
            return {
                'system_status': 'operational',
                'phase': 'phase3',
                'integration': integration_status,
                'monitoring': monitoring_status,
                'performance': performance_status,
                'orchestrator': orchestrator_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        try:
            status = await self.integration_manager.get_workflow_status(execution_id)
            return status
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {'error': str(e)}
    
    async def get_monitoring_metrics(self, metric_name: str = None) -> Dict[str, Any]:
        """Get monitoring metrics"""
        try:
            metrics = await self.monitoring_service.get_metrics(metric_name)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting monitoring metrics: {e}")
            return {'error': str(e)}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            cache_stats = await self.performance_service.get_cache_stats()
            performance_status = await self.performance_service.get_performance_status()
            
            return {
                'cache': cache_stats,
                'performance': performance_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the enhanced AMAS system"""
        try:
            logger.info("Shutting down AMAS Intelligence System Phase 3...")
            
            # Shutdown integration manager
            if self.integration_manager:
                await self.integration_manager.shutdown()
            
            # Shutdown monitoring service
            if self.monitoring_service:
                await self.monitoring_service.shutdown()
            
            # Shutdown performance service
            if self.performance_service:
                await self.performance_service.shutdown()
            
            # Shutdown orchestrator
            if self.orchestrator:
                # Shutdown orchestrator components
                pass
            
            logger.info("AMAS Intelligence System Phase 3 shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main application entry point for Phase 3"""
    try:
        # Enhanced configuration for Phase 3
        config = {
            'llm_service_url': 'http://localhost:11434',
            'vector_service_url': 'http://localhost:8001',
            'graph_service_url': 'bolt://localhost:7687',
            'postgres_host': 'localhost',
            'postgres_port': 5432,
            'postgres_user': 'amas',
            'postgres_password': 'amas123',
            'postgres_db': 'amas',
            'redis_host': 'localhost',
            'redis_port': 6379,
            'redis_db': 0,
            'neo4j_username': 'neo4j',
            'neo4j_password': 'amas123',
            'neo4j_database': 'neo4j',
            'jwt_secret': 'amas_jwt_secret_key_2024_secure',
            'encryption_key': 'amas_encryption_key_2024_secure_32_chars',
            'deepseek_api_key': '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',
            'glm_api_key': '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',
            'grok_api_key': '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',
            'n8n_url': 'http://localhost:5678',
            'n8n_api_key': 'your_n8n_api_key_here',
            # Phase 3 specific configuration
            'cache_max_size': 1000,
            'cache_default_ttl': 3600,
            'cache_strategy': 'lru',
            'load_balance_strategy': 'round_robin',
            'monitoring_enabled': True,
            'performance_optimization': True
        }
        
        # Initialize enhanced system
        amas = AMASIntelligenceSystemPhase3(config)
        await amas.initialize()
        
        # Example usage
        logger.info("AMAS Intelligence System Phase 3 is ready!")
        
        # Submit advanced OSINT task
        advanced_task = {
            'type': 'osint',
            'description': 'Advanced OSINT investigation with multi-source intelligence collection',
            'priority': 1,
            'parameters': {
                'sources': ['web', 'social_media', 'forums', 'news', 'academic'],
                'keywords': ['cyber', 'threat', 'security', 'malware'],
                'timeframe': '30d',
                'depth': 'deep',
                'correlation_analysis': True,
                'threat_assessment': True
            }
        }
        
        task_id = await amas.submit_advanced_task(advanced_task)
        logger.info(f"Submitted advanced task {task_id}")
        
        # Execute advanced workflow
        workflow_result = await amas.execute_advanced_workflow(
            'advanced_osint_investigation',
            {
                'target': 'suspicious_domain.com',
                'depth': 'deep',
                'sources': ['web', 'social_media', 'forums'],
                'threat_assessment': True,
                'correlation_analysis': True
            },
            user_id='admin'
        )
        logger.info(f"Advanced workflow execution started: {workflow_result}")
        
        # Get comprehensive system status
        status = await amas.get_system_status()
        logger.info(f"System status: {status}")
        
        # Get monitoring metrics
        metrics = await amas.get_monitoring_metrics()
        logger.info(f"Monitoring metrics: {metrics}")
        
        # Get performance metrics
        performance = await amas.get_performance_metrics()
        logger.info(f"Performance metrics: {performance}")
        
        # Keep system running
        logger.info("AMAS Intelligence System Phase 3 is running...")
        await asyncio.sleep(3600)  # Run for 1 hour
        
        # Shutdown
        await amas.shutdown()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())