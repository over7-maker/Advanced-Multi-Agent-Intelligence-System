"""
AMAS Intelligence System - Main Application
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
        logging.FileHandler('logs/amas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import core components
from core.orchestrator import IntelligenceOrchestrator
from agents.osint.osint_agent import OSINTAgent
from agents.investigation.investigation_agent import InvestigationAgent
from agents.forensics.forensics_agent import ForensicsAgent
from agents.data_analysis.data_analysis_agent import DataAnalysisAgent
from agents.reverse_engineering.reverse_engineering_agent import ReverseEngineeringAgent
from agents.metadata.metadata_agent import MetadataAgent
from agents.reporting.reporting_agent import ReportingAgent
from agents.technology_monitor.technology_monitor_agent import TechnologyMonitorAgent
from agents.agentic_rag import AgenticRAG
from agents.prompt_maker import PromptMaker
from agents.n8n_integration import N8NIntegration

class AMASIntelligenceSystem:
    """Main AMAS Intelligence System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.orchestrator = None
        self.agents = {}
        self.agentic_rag = None
        self.prompt_maker = None
        self.n8n_integration = None
        
    async def initialize(self):
        """Initialize the AMAS system"""
        try:
            logger.info("Initializing AMAS Intelligence System...")
            
            # Initialize orchestrator
            self.orchestrator = IntelligenceOrchestrator(
                llm_service=None,  # Will be initialized later
                vector_service=None,
                knowledge_graph=None,
                security_service=None
            )
            
            # Initialize specialized agents
            await self._initialize_agents()
            
            # Initialize Agentic RAG
            self.agentic_rag = AgenticRAG(self.config)
            await self.agentic_rag.initialize()
            
            # Initialize Prompt Maker
            self.prompt_maker = PromptMaker(self.config)
            
            # Initialize n8n integration
            self.n8n_integration = N8NIntegration(self.config)
            await self.n8n_integration.initialize()
            
            logger.info("AMAS Intelligence System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AMAS system: {e}")
            raise
    
    async def _initialize_agents(self):
        """Initialize all specialized agents"""
        try:
            # Create agent instances
            agents_config = [
                (OSINTAgent, "osint_001", "OSINT Agent"),
                (InvestigationAgent, "investigation_001", "Investigation Agent"),
                (ForensicsAgent, "forensics_001", "Forensics Agent"),
                (DataAnalysisAgent, "data_analysis_001", "Data Analysis Agent"),
                (ReverseEngineeringAgent, "reverse_engineering_001", "Reverse Engineering Agent"),
                (MetadataAgent, "metadata_001", "Metadata Agent"),
                (ReportingAgent, "reporting_001", "Reporting Agent"),
                (TechnologyMonitorAgent, "technology_monitor_001", "Technology Monitor Agent")
            ]
            
            for agent_class, agent_id, agent_name in agents_config:
                agent = agent_class(
                    agent_id=agent_id,
                    name=agent_name,
                    llm_service=None,
                    vector_service=None,
                    knowledge_graph=None,
                    security_service=None
                )
                await self.orchestrator.register_agent(agent)
                self.agents[agent_id] = agent
                logger.info(f"Registered {agent_name} with ID {agent_id}")
                
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    async def submit_intelligence_task(self, task_data: Dict[str, Any]) -> str:
        """Submit an intelligence task"""
        try:
            task_id = await self.orchestrator.submit_task(
                task_type=task_data.get('type', 'general'),
                description=task_data.get('description', ''),
                parameters=task_data.get('parameters', {}),
                priority=task_data.get('priority', 2)
            )
            
            logger.info(f"Task {task_id} submitted successfully")
            return task_id
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            raise
    
    async def _find_suitable_agent(self, task_data: Dict[str, Any]) -> Any:
        """Find a suitable agent for the task"""
        task_type = task_data.get('type', 'general')
        
        # Map task types to agent types
        task_type_mapping = {
            'osint': 'osint_001',
            'investigation': 'investigation_001',
            'forensics': 'forensics_001',
            'data_analysis': 'data_analysis_001',
            'reverse_engineering': 'reverse_engineering_001',
            'metadata': 'metadata_001',
            'reporting': 'reporting_001',
            'technology_monitor': 'technology_monitor_001'
        }
        
        agent_id = task_type_mapping.get(task_type)
        if agent_id and agent_id in self.agents:
            return self.agents[agent_id]
        
        return None
    
    async def execute_intelligence_workflow(self, workflow_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an intelligence workflow"""
        try:
            # Create n8n workflow
            workflow = await self.n8n_integration.create_intelligence_workflow(workflow_type, config)
            
            # Execute workflow
            execution_result = await self.n8n_integration.execute_workflow(workflow['id'], config)
            
            return {
                'workflow_id': workflow['id'],
                'execution_result': execution_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {'error': str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            status = await self.orchestrator.get_system_status()
            
            return {
                'status': 'operational',
                'agents': status.get('active_agents', 0),
                'active_tasks': status.get('active_tasks', 0),
                'total_tasks': status.get('total_tasks', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the system"""
        try:
            logger.info("Shutting down AMAS Intelligence System...")
            # Cleanup operations
            logger.info("AMAS Intelligence System shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

async def main():
    """Main application entry point"""
    try:
        # Configuration
        config = {
            'llm_service_url': 'http://localhost:11434',
            'vector_service_url': 'http://localhost:8001',
            'graph_service_url': 'http://localhost:7474',
            'n8n_url': 'http://localhost:5678',
            'n8n_api_key': 'your_api_key_here'
        }
        
        # Initialize system
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()
        
        # Example usage
        logger.info("AMAS Intelligence System is ready!")
        
        # Submit example task
        task_data = {
            'type': 'osint',
            'description': 'Collect intelligence on emerging cyber threats',
            'priority': 2,
            'metadata': {
                'sources': ['news', 'social_media', 'forums'],
                'keywords': ['cyber', 'threat', 'security']
            }
        }
        
        task_id = await amas.submit_intelligence_task(task_data)
        logger.info(f"Submitted task {task_id}")
        
        # Get system status
        status = await amas.get_system_status()
        logger.info(f"System status: {status}")
        
        # Keep system running
        await asyncio.sleep(60)  # Run for 1 minute
        
        # Shutdown
        await amas.shutdown()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())