"""
Database Setup Script for AMAS Phase 1
Creates PostgreSQL schemas and initial data
"""

import asyncio
import asyncpg
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database_schemas():
    """Create all necessary database tables and indexes"""

    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'amas',
        'password': 'amas123',
        'database': 'amas'
    }

    try:
        # Connect to database
        conn = await asyncpg.connect(**db_config)
        logger.info("Connected to PostgreSQL database")

        # Create tasks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                priority INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                assigned_agent VARCHAR(36),
                metadata JSONB DEFAULT '{}',
                result JSONB,
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                timeout_seconds INTEGER DEFAULT 300,
                dependencies JSONB DEFAULT '[]',
                tags JSONB DEFAULT '[]'
            )
        """)
        logger.info("Tasks table created")

        # Create agents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                capabilities JSONB DEFAULT '[]',
                status VARCHAR(20) NOT NULL,
                current_task VARCHAR(36),
                created_at TIMESTAMP NOT NULL,
                last_heartbeat TIMESTAMP NOT NULL,
                metadata JSONB DEFAULT '{}',
                performance_metrics JSONB DEFAULT '{}',
                error_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0
            )
        """)
        logger.info("Agents table created")

        # Create task execution history
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(36) NOT NULL,
                agent_id VARCHAR(36) NOT NULL,
                phase VARCHAR(20) NOT NULL,
                content TEXT,
                timestamp TIMESTAMP NOT NULL,
                execution_time FLOAT,
                success BOOLEAN
            )
        """)
        logger.info("Task history table created")

        # Create system metrics table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                metadata JSONB DEFAULT '{}',
                timestamp TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)
        logger.info("System metrics table created")

        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)",
            "CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(type)",
            "CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_history_agent_id ON task_history(agent_id)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)"
        ]

        for index_sql in indexes:
            await conn.execute(index_sql)

        logger.info("Database indexes created")

        # Close connection
        await conn.close()
        logger.info("Database setup completed successfully")

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_database_schemas())
