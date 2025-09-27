"""
AMAS Phase 1 Setup Script
Automated setup for Phase 1 foundation components
"""

import asyncio
import os
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_phase1():
    """Complete Phase 1 setup process"""
    
    logger.info("Starting AMAS Phase 1 Foundation Setup...")
    
    try:
        # 1. Create necessary directories
        directories = ['logs', 'data', 'config', 'temp']
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            logger.info(f"Created directory: {dir_name}")
        
        # 2. Install Python dependencies
        logger.info("Installing Python dependencies...")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        logger.info("Dependencies installed successfully")
        
        # 3. Start Docker services
        logger.info("Starting Docker services...")
        subprocess.run(['docker-compose', 'up', '-d', 'postgres', 'redis', 'neo4j'], check=True)
        logger.info("Core services started")
        
        # 4. Wait for services to be ready
        logger.info("Waiting for services to initialize...")
        await asyncio.sleep(30)
        
        # 5. Setup database schemas
        logger.info("Setting up database schemas...")
        from setup_database import create_database_schemas
        await create_database_schemas()
        
        # 6. Validate setup
        logger.info("Validating setup...")
        await validate_setup()
        
        logger.info("Phase 1 setup completed successfully!")
        logger.info("You can now run the enhanced orchestrator")
        
    except Exception as e:
        logger.error(f"Phase 1 setup failed: {e}")
        raise

async def validate_setup():
    """Validate that all Phase 1 components are working"""
    
    # Check database connection
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host='localhost', port=5432, 
            user='amas', password='amas123', database='amas'
        )
        await conn.fetchval('SELECT 1')
        await conn.close()
        logger.info("✓ Database connection validated")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise
    
    # Check Redis connection
    try:
        import redis.asyncio as redis
        r = redis.from_url('redis://localhost:6379')
        await r.ping()
        await r.close()
        logger.info("✓ Redis connection validated")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        raise
    
    logger.info("All Phase 1 components validated successfully")

if __name__ == "__main__":
    asyncio.run(setup_phase1())
