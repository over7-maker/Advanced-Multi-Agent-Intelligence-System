"""
Database Service for AMAS Intelligence System
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import asyncpg
    import redis.asyncio as redis
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logging.warning("Database drivers not available")

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.postgres_pool = None
        self.redis_client = None
        self.initialized = False

    async def initialize(self):
        """Initialize database connections"""
        try:
            if not DATABASE_AVAILABLE:
                logger.warning("Database drivers not available, using mock mode")
                self.initialized = True
                return

            # Initialize PostgreSQL connection pool
            self.postgres_pool = await asyncpg.create_pool(
                host=self.config.get('postgres_host', 'localhost'),
                port=self.config.get('postgres_port', 5432),
                user=self.config.get('postgres_user', 'amas'),
                password=self.config.get('postgres_password', 'amas123'),
                database=self.config.get('postgres_db', 'amas'),
                min_size=1,
                max_size=10
            )
            logger.info("PostgreSQL connection pool created")

            # Initialize Redis client
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                db=self.config.get('redis_db', 0),
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")

            # Create database schema
            await self._create_schema()

            self.initialized = True
            logger.info("Database service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise

    async def _create_schema(self):
        """Create database schema"""
        try:
            async with self.postgres_pool.acquire() as conn:
                # Create agents table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS agents (
                        id SERIAL PRIMARY KEY,
                        agent_id VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        capabilities JSONB,
                        status VARCHAR(50) DEFAULT 'idle',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create tasks table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        task_id VARCHAR(255) UNIQUE NOT NULL,
                        task_type VARCHAR(100) NOT NULL,
                        description TEXT,
                        parameters JSONB,
                        priority INTEGER DEFAULT 2,
                        status VARCHAR(50) DEFAULT 'pending',
                        assigned_agent VARCHAR(255),
                        result JSONB,
                        error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """)

                # Create workflows table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS workflows (
                        id SERIAL PRIMARY KEY,
                        workflow_id VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        steps JSONB,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create intelligence_data table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS intelligence_data (
                        id SERIAL PRIMARY KEY,
                        data_id VARCHAR(255) UNIQUE NOT NULL,
                        data_type VARCHAR(100) NOT NULL,
                        source VARCHAR(255),
                        content JSONB,
                        metadata JSONB,
                        classification VARCHAR(50) DEFAULT 'unclassified',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(assigned_agent)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_intelligence_type ON intelligence_data(data_type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_intelligence_classification ON intelligence_data(classification)")

                logger.info("Database schema created successfully")

        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            raise

    async def store_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Store agent data"""
        try:
            if not self.initialized:
                return False

            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO agents (agent_id, name, capabilities, status)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (agent_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    capabilities = EXCLUDED.capabilities,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
                """, agent_data['agent_id'], agent_data['name'],
                     json.dumps(agent_data.get('capabilities', [])),
                     agent_data.get('status', 'idle'))

                return True

        except Exception as e:
            logger.error(f"Error storing agent: {e}")
            return False

    async def store_task(self, task_data: Dict[str, Any]) -> bool:
        """Store task data"""
        try:
            if not self.initialized:
                return False

            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tasks (task_id, task_type, description, parameters, priority, status, assigned_agent)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (task_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    assigned_agent = EXCLUDED.assigned_agent,
                    result = EXCLUDED.result,
                    error = EXCLUDED.error,
                    started_at = EXCLUDED.started_at,
                    completed_at = EXCLUDED.completed_at
                """, task_data['task_id'], task_data['task_type'],
                     task_data.get('description', ''),
                     json.dumps(task_data.get('parameters', {})),
                     task_data.get('priority', 2),
                     task_data.get('status', 'pending'),
                     task_data.get('assigned_agent'))

                return True

        except Exception as e:
            logger.error(f"Error storing task: {e}")
            return False

    async def store_intelligence_data(self, data: Dict[str, Any]) -> bool:
        """Store intelligence data"""
        try:
            if not self.initialized:
                return False

            async with self.postgres_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO intelligence_data (data_id, data_type, source, content, metadata, classification)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (data_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                """, data['data_id'], data['data_type'],
                     data.get('source', ''),
                     json.dumps(data.get('content', {})),
                     json.dumps(data.get('metadata', {})),
                     data.get('classification', 'unclassified'))

                return True

        except Exception as e:
            logger.error(f"Error storing intelligence data: {e}")
            return False

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent data"""
        try:
            if not self.initialized:
                return None

            async with self.postgres_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM agents WHERE agent_id = $1", agent_id
                )

                if row:
                    return dict(row)
                return None

        except Exception as e:
            logger.error(f"Error getting agent: {e}")
            return None

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data"""
        try:
            if not self.initialized:
                return None

            async with self.postgres_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE task_id = $1", task_id
                )

                if row:
                    return dict(row)
                return None

        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return None

    async def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get tasks by status"""
        try:
            if not self.initialized:
                return []

            async with self.postgres_pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM tasks WHERE status = $1 ORDER BY created_at DESC", status
                )

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting tasks by status: {e}")
            return []

    async def update_task_status(self, task_id: str, status: str, result: Dict[str, Any] = None, error: str = None) -> bool:
        """Update task status"""
        try:
            if not self.initialized:
                return False

            async with self.postgres_pool.acquire() as conn:
                if status == 'in_progress':
                    await conn.execute("""
                        UPDATE tasks SET status = $1, started_at = CURRENT_TIMESTAMP
                        WHERE task_id = $2
                    """, status, task_id)
                elif status in ['completed', 'failed']:
                    await conn.execute("""
                        UPDATE tasks SET status = $1, completed_at = CURRENT_TIMESTAMP,
                        result = $2, error = $3 WHERE task_id = $4
                    """, status, json.dumps(result) if result else None, error, task_id)
                else:
                    await conn.execute("""
                        UPDATE tasks SET status = $1 WHERE task_id = $2
                    """, status, task_id)

                return True

        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False

    async def cache_data(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache data in Redis"""
        try:
            if not self.initialized or not self.redis_client:
                return False

            await self.redis_client.setex(key, ttl, json.dumps(data))
            return True

        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached data from Redis"""
        try:
            if not self.initialized or not self.redis_client:
                return None

            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            if not self.initialized:
                return {
                    'status': 'unhealthy',
                    'error': 'Database not initialized',
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Check PostgreSQL
            postgres_healthy = False
            if self.postgres_pool:
                try:
                    async with self.postgres_pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                        postgres_healthy = True
                except Exception as e:
                    logger.error(f"PostgreSQL health check failed: {e}")

            # Check Redis
            redis_healthy = False
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    redis_healthy = True
                except Exception as e:
                    logger.error(f"Redis health check failed: {e}")

            overall_status = 'healthy' if postgres_healthy and redis_healthy else 'degraded'

            return {
                'status': overall_status,
                'postgres': 'healthy' if postgres_healthy else 'unhealthy',
                'redis': 'healthy' if redis_healthy else 'unhealthy',
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking database health: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close database connections"""
        try:
            if self.postgres_pool:
                await self.postgres_pool.close()
                logger.info("PostgreSQL connection pool closed")

            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")

            logger.info("Database service closed successfully")

        except Exception as e:
            logger.error(f"Error closing database service: {e}")
