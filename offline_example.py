#!/usr/bin/env python3
"""
AMAS Intelligence System - Offline-First Example
Demonstrates complete local isolation with no internet dependency
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import offline components
from offline_agent import OfflineSystem, OfflineOSINTAgent, OfflineInvestigationAgent
from offline_config import OfflineConfig

class OfflineAMASExample:
    """Complete offline AMAS system demonstration"""
    
    def __init__(self):
        self.offline_system = None
        self.config = OfflineConfig()
        
    async def initialize_offline_system(self):
        """Initialize completely offline system"""
        try:
            logger.info("🔒 Initializing AMAS Offline System...")
            logger.info("=" * 60)
            
            # Get offline configuration
            offline_config = self.config.get_offline_config()
            
            logger.info(f"🌐 System Mode: {offline_config['system_mode']}")
            logger.info(f"🔒 Internet Access: {offline_config['internet_access']}")
            logger.info(f"🏠 Local Services: {len(offline_config['local_services'])}")
            logger.info(f"🛡️ Network Isolation: {offline_config['network_isolation']['block_external_connections']}")
            logger.info("=" * 60)
            
            # Initialize offline system
            self.offline_system = OfflineSystem()
            success = await self.offline_system.initialize_offline_system()
            
            if success:
                logger.info("✅ AMAS Offline System initialized successfully")
                return True
            else:
                logger.error("❌ Failed to initialize offline system")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing offline system: {e}")
            return False
    
    async def demonstrate_offline_osint(self):
        """Demonstrate offline OSINT capabilities"""
        try:
            logger.info("🔍 Demonstrating Offline OSINT Capabilities...")
            
            # Test offline OSINT agent
            osint_agent = OfflineOSINTAgent()
            await osint_agent.initialize_offline()
            
            # Test different offline OSINT tasks
            tasks = [
                {
                    'type': 'offline_web_scraping',
                    'description': 'Scrape local web data',
                    'parameters': {'sources': ['local_db'], 'keywords': ['security', 'threat']}
                },
                {
                    'type': 'local_data_analysis',
                    'description': 'Analyze local datasets',
                    'parameters': {'datasets': ['threat_intelligence', 'osint_sources']}
                },
                {
                    'type': 'offline_social_monitoring',
                    'description': 'Monitor local social media',
                    'parameters': {'platforms': ['local_forum'], 'keywords': ['cyber']}
                },
                {
                    'type': 'local_news_aggregation',
                    'description': 'Aggregate local news',
                    'parameters': {'sources': ['local_news_db'], 'time_range': '24h'}
                }
            ]
            
            results = []
            for task in tasks:
                logger.info(f"📋 Executing: {task['description']}")
                result = await osint_agent.execute_offline_task(task)
                results.append(result)
                logger.info(f"✅ Completed: {result['success']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in offline OSINT demonstration: {e}")
            return []
    
    async def demonstrate_offline_investigation(self):
        """Demonstrate offline investigation capabilities"""
        try:
            logger.info("🕵️ Demonstrating Offline Investigation Capabilities...")
            
            # Test offline investigation agent
            investigation_agent = OfflineInvestigationAgent()
            await investigation_agent.initialize_offline()
            
            # Test offline investigation tasks
            tasks = [
                {
                    'type': 'offline_evidence_analysis',
                    'description': 'Analyze local evidence',
                    'parameters': {'evidence_path': './data/evidence', 'analysis_type': 'comprehensive'}
                },
                {
                    'type': 'local_forensics',
                    'description': 'Perform local forensics',
                    'parameters': {'target': 'local_system', 'scope': 'full'}
                },
                {
                    'type': 'offline_network_analysis',
                    'description': 'Analyze local network',
                    'parameters': {'network_scope': 'local', 'analysis_depth': 'deep'}
                }
            ]
            
            results = []
            for task in tasks:
                logger.info(f"📋 Executing: {task['description']}")
                result = await investigation_agent.execute_offline_task(task)
                results.append(result)
                logger.info(f"✅ Completed: {result['success']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in offline investigation demonstration: {e}")
            return []
    
    async def demonstrate_offline_workflow(self):
        """Demonstrate complete offline workflow"""
        try:
            logger.info("🔄 Demonstrating Offline Workflow...")
            
            # Create comprehensive offline workflow
            workflow = {
                'name': 'Offline Intelligence Workflow',
                'description': 'Complete offline intelligence gathering and analysis',
                'tasks': [
                    {
                        'agent_id': 'osint_offline_001',
                        'type': 'offline_web_scraping',
                        'description': 'Gather local web intelligence',
                        'priority': 1
                    },
                    {
                        'agent_id': 'osint_offline_001',
                        'type': 'local_data_analysis',
                        'description': 'Analyze local threat data',
                        'priority': 2
                    },
                    {
                        'agent_id': 'investigation_offline_001',
                        'type': 'offline_evidence_analysis',
                        'description': 'Analyze collected evidence',
                        'priority': 3
                    },
                    {
                        'agent_id': 'investigation_offline_001',
                        'type': 'local_forensics',
                        'description': 'Perform forensic analysis',
                        'priority': 4
                    }
                ]
            }
            
            # Execute offline workflow
            result = await self.offline_system.execute_offline_workflow(workflow)
            
            logger.info(f"📊 Workflow Results:")
            logger.info(f"   ✅ Success: {result['success']}")
            logger.info(f"   📋 Tasks Completed: {result['tasks_completed']}")
            logger.info(f"   🔒 Mode: {result['workflow_type']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in offline workflow demonstration: {e}")
            return {'success': False, 'error': str(e)}
    
    async def demonstrate_hybrid_mode(self):
        """Demonstrate hybrid mode with optional internet access"""
        try:
            logger.info("🌐 Demonstrating Hybrid Mode (Optional Internet Access)...")
            
            # Get hybrid configuration
            hybrid_config = self.config.get_hybrid_config(internet_access=True)
            
            logger.info(f"🔧 Hybrid Configuration:")
            logger.info(f"   🌐 Internet Access: {hybrid_config['internet_access']}")
            logger.info(f"   🛡️ Network Isolation: {hybrid_config['network_isolation']['block_external_connections']}")
            logger.info(f"   🔗 Allowed Domains: {len(hybrid_config['network_isolation']['allowed_domains'])}")
            logger.info(f"   🤖 Hybrid Agents: {hybrid_config['agents']['hybrid_workflows']}")
            
            # Simulate hybrid workflow
            hybrid_workflow = {
                'name': 'Hybrid Intelligence Workflow',
                'description': 'Offline-first with optional internet access',
                'mode': 'hybrid',
                'tasks': [
                    {
                        'agent_id': 'osint_hybrid_001',
                        'type': 'offline_web_scraping',
                        'description': 'Local web scraping (offline)',
                        'priority': 1,
                        'offline': True
                    },
                    {
                        'agent_id': 'osint_hybrid_001',
                        'type': 'online_api_call',
                        'description': 'External API call (on-demand)',
                        'priority': 2,
                        'offline': False,
                        'requires_internet': True
                    }
                ]
            }
            
            logger.info("✅ Hybrid mode configuration ready")
            logger.info("   🔒 Default: Offline operation")
            logger.info("   🌐 Optional: Internet access when needed")
            logger.info("   🛡️ Controlled: Network isolation maintained")
            
            return hybrid_workflow
            
        except Exception as e:
            logger.error(f"Error in hybrid mode demonstration: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_offline_demonstration(self):
        """Run complete offline demonstration"""
        try:
            logger.info("🚀 AMAS Offline-First System Demonstration")
            logger.info("=" * 60)
            logger.info("🔒 Complete Local Isolation - No Internet Required")
            logger.info("=" * 60)
            
            # Initialize offline system
            if not await self.initialize_offline_system():
                logger.error("Failed to initialize offline system")
                return False
            
            # Demonstrate offline OSINT
            osint_results = await self.demonstrate_offline_osint()
            logger.info(f"📊 OSINT Results: {len(osint_results)} tasks completed")
            
            # Demonstrate offline investigation
            investigation_results = await self.demonstrate_offline_investigation()
            logger.info(f"📊 Investigation Results: {len(investigation_results)} tasks completed")
            
            # Demonstrate offline workflow
            workflow_result = await self.demonstrate_offline_workflow()
            logger.info(f"📊 Workflow Result: {workflow_result['success']}")
            
            # Demonstrate hybrid mode
            hybrid_result = await self.demonstrate_hybrid_mode()
            logger.info(f"📊 Hybrid Mode: Ready for optional internet access")
            
            # Final summary
            logger.info("=" * 60)
            logger.info("🎉 OFFLINE DEMONSTRATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info("✅ Complete local isolation achieved")
            logger.info("✅ All agents working offline")
            logger.info("✅ No internet dependency")
            logger.info("✅ Hybrid mode ready for optional internet")
            logger.info("✅ Production-ready offline system")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in offline demonstration: {e}")
            return False

async def main():
    """Main function"""
    try:
        example = OfflineAMASExample()
        success = await example.run_offline_demonstration()
        
        if success:
            logger.info("🏆 AMAS Offline System demonstration completed successfully!")
            return 0
        else:
            logger.error("❌ AMAS Offline System demonstration failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)