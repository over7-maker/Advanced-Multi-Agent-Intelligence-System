"""
Enhanced Test Script for AMAS Intelligence System - Phase 2
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_enhanced_amas_system():
    """Test the enhanced AMAS Intelligence System"""
    try:
        # Import the main system
        from main import AMASIntelligenceSystem
        
        # Enhanced configuration
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
            'jwt_secret': 'your_jwt_secret_here',
            'encryption_key': 'your_encryption_key_here',
            'n8n_url': 'http://localhost:5678',
            'n8n_api_key': 'your_api_key_here'
        }
        
        # Initialize system
        logger.info("Initializing Enhanced AMAS Intelligence System...")
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()
        
        # Test service health
        logger.info("Checking service health...")
        health_status = await amas.service_manager.health_check_all_services()
        logger.info(f"Service health: {health_status}")
        
        # Test database service
        logger.info("Testing database service...")
        db_health = await amas.database_service.health_check()
        logger.info(f"Database health: {db_health}")
        
        # Test security service
        logger.info("Testing security service...")
        security_health = await amas.security_service.health_check()
        logger.info(f"Security health: {security_health}")
        
        # Test system status
        logger.info("Getting system status...")
        status = await amas.get_system_status()
        logger.info(f"System status: {status}")
        
        # Test enhanced OSINT task
        logger.info("Submitting enhanced OSINT task...")
        osint_task = {
            'type': 'web_scraping',
            'description': 'Collect intelligence on emerging cyber threats from multiple sources',
            'priority': 2,
            'parameters': {
                'urls': ['https://example.com', 'https://test.com'],
                'keywords': ['cyber', 'threat', 'security', 'malware'],
                'max_pages': 5
            }
        }
        
        task_id = await amas.submit_intelligence_task(osint_task)
        logger.info(f"Submitted OSINT task {task_id}")
        
        # Test social media monitoring task
        logger.info("Submitting social media monitoring task...")
        social_task = {
            'type': 'social_media_monitoring',
            'description': 'Monitor social media for threat indicators',
            'priority': 2,
            'parameters': {
                'platforms': ['twitter', 'reddit'],
                'keywords': ['cyber', 'threat', 'security'],
                'time_range': '24h'
            }
        }
        
        social_task_id = await amas.submit_intelligence_task(social_task)
        logger.info(f"Submitted social media task {social_task_id}")
        
        # Test domain analysis task
        logger.info("Submitting domain analysis task...")
        domain_task = {
            'type': 'domain_analysis',
            'description': 'Analyze suspicious domain for threat indicators',
            'priority': 1,
            'parameters': {
                'domain': 'suspicious.example.com',
                'analysis_type': 'comprehensive'
            }
        }
        
        domain_task_id = await amas.submit_intelligence_task(domain_task)
        logger.info(f"Submitted domain analysis task {domain_task_id}")
        
        # Wait for task processing
        logger.info("Waiting for task processing...")
        await asyncio.sleep(3)
        
        # Get updated status
        status = await amas.get_system_status()
        logger.info(f"Updated system status: {status}")
        
        # Test service statistics
        logger.info("Getting service statistics...")
        service_stats = await amas.service_manager.get_service_stats()
        logger.info(f"Service statistics: {service_stats}")
        
        # Test database operations
        logger.info("Testing database operations...")
        tasks = await amas.database_service.get_tasks_by_status('pending')
        logger.info(f"Pending tasks: {len(tasks)}")
        
        # Test security operations
        logger.info("Testing security operations...")
        auth_result = await amas.security_service.authenticate_user('admin', 'admin123')
        logger.info(f"Authentication result: {auth_result.get('success', False)}")
        
        # Test audit logging
        logger.info("Testing audit logging...")
        audit_log = await amas.security_service.get_audit_log()
        logger.info(f"Audit log entries: {len(audit_log)}")
        
        # Shutdown
        await amas.shutdown()
        logger.info("Enhanced AMAS Intelligence System test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_enhanced_amas_system())