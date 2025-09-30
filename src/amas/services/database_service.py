"""
Database Service Implementation for AMAS
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    import asyncpg
    import redis
    ASYNC_DB_AVAILABLE = True
except ImportError:
    ASYNC_DB_AVAILABLE = False
    logging.warning("Database drivers not available")

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database Service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pg_pool = None
        self.redis_client = None
        self.initialized = False

    async def initialize(self):
        """Initialize database connections"""
        try:
            if ASYNC_DB_AVAILABLE:
                # Initialize PostgreSQL connection
                await self._initialize_postgres()
                
                # Initialize Redis connection
                await self._initialize_redis()
                
                # Create database schema
                await self._create_schema()
                
                self.initialized = True
                logger.info("Database service initialized successfully")
            else:
                logger.warning("Database drivers not available, using fallback mode")
                self.initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise

    async def _initialize_postgres(self):
        """Initialize PostgreSQL connection"""
        try:
            db_config = self.config.get('database', {})
            self.pg_pool = await asyncpg.create_pool(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                user=db_config.get('user', 'amas'),
                password=db_config.get('password', 'amas123'),
                database=db_config.get('database', 'amas'),
                min_size=1,
                max_size=10
            )
            logger.info("PostgreSQL connection pool created")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise

    async def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def _create_schema(self):
        """Create database schema"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Create tasks table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id UUID PRIMARY KEY,
                        type VARCHAR(100) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) NOT NULL,
                        priority INTEGER DEFAULT 2,
                        assigned_agent VARCHAR(100),
                        created_at TIMESTAMP DEFAULT NOW(),
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        parameters JSONB,
                        result JSONB,
                        error TEXT
                    )
                """)

                # Create agents table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS agents (
                        id VARCHAR(100) PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        type VARCHAR(100) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        capabilities JSONB,
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_activity TIMESTAMP,
                        metrics JSONB
                    )
                """)

                # Create audit_log table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR(100) NOT NULL,
                        user_id VARCHAR(100),
                        action VARCHAR(200) NOT NULL,
                        details TEXT,
                        classification VARCHAR(50),
                        timestamp TIMESTAMP DEFAULT NOW(),
                        ip_address INET,
                        user_agent TEXT
                    )
                """)

                # Create indexes
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type)")

                logger.info("Database schema created successfully")

        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'database',
                'connections': {}
            }

            # Check PostgreSQL
            if self.pg_pool:
                try:
                    async with self.pg_pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                    health_status['connections']['postgresql'] = 'healthy'
                except Exception as e:
                    health_status['connections']['postgresql'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'

            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    health_status['connections']['redis'] = 'healthy'
                except Exception as e:
                    health_status['connections']['redis'] = f'unhealthy: {e}'
                    health_status['status'] = 'degraded'

            return health_status

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'database'
            }

    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save task to database"""
        try:
            if not self.pg_pool:
                return task_data.get('id', 'no_db')

            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tasks (id, type, description, status, priority, assigned_agent, 
                                    created_at, started_at, completed_at, parameters, result, error)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (id) DO UPDATE SET
                        status = EXCLUDED.status,
                        assigned_agent = EXCLUDED.assigned_agent,
                        started_at = EXCLUDED.started_at,
                        completed_at = EXCLUDED.completed_at,
                        parameters = EXCLUDED.parameters,
                        result = EXCLUDED.result,
                        error = EXCLUDED.error
                """, 
                task_data.get('id'),
                task_data.get('type'),
                task_data.get('description'),
                task_data.get('status'),
                task_data.get('priority'),
                task_data.get('assigned_agent'),
                task_data.get('created_at'),
                task_data.get('started_at'),
                task_data.get('completed_at'),
                json.dumps(task_data.get('parameters', {})),
                json.dumps(task_data.get('result', {})),
                task_data.get('error')
                )

            return task_data.get('id')

        except Exception as e:
            logger.error(f"Failed to save task: {e}")
            raise

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task from database"""
        try:
            if not self.pg_pool:
                return None

            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM tasks WHERE id = $1
                """, task_id)

                if row:
                    return dict(row)

            return None

        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    async def get_tasks(self, status_filter: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tasks from database"""
        try:
            if not self.pg_pool:
                return []

            async with self.pg_pool.acquire() as conn:
                if status_filter:
                    rows = await conn.fetch("""
                        SELECT * FROM tasks WHERE status = $1 ORDER BY created_at DESC LIMIT $2
                    """, status_filter, limit)
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1
                    """, limit)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []

    async def save_agent(self, agent_data: Dict[str, Any]) -> str:
        """Save agent to database"""
        try:
            if not self.pg_pool:
                return agent_data.get('id', 'no_db')

            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO agents (id, name, type, status, capabilities, created_at, 
                                      last_activity, metrics)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        status = EXCLUDED.status,
                        capabilities = EXCLUDED.capabilities,
                        last_activity = EXCLUDED.last_activity,
                        metrics = EXCLUDED.metrics
                """,
                agent_data.get('id'),
                agent_data.get('name'),
                agent_data.get('type'),
                agent_data.get('status'),
                json.dumps(agent_data.get('capabilities', [])),
                agent_data.get('created_at'),
                agent_data.get('last_activity'),
                json.dumps(agent_data.get('metrics', {}))
                )

            return agent_data.get('id')

        except Exception as e:
            logger.error(f"Failed to save agent: {e}")
            raise

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent from database"""
        try:
            if not self.pg_pool:
                return None

            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM agents WHERE id = $1
                """, agent_id)

                if row:
                    return dict(row)

            return None

        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None

    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents from database"""
        try:
            if not self.pg_pool:
                return []

            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM agents ORDER BY created_at DESC
                """)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []

    async def log_audit_event(self, event_data: Dict[str, Any]) -> int:
        """Log audit event"""
        try:
            if not self.pg_pool:
                return 0

            async with self.pg_pool.acquire() as conn:
                result = await conn.fetchval("""
                    INSERT INTO audit_log (event_type, user_id, action, details, 
                                         classification, timestamp, ip_address, user_agent)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id
                """,
                event_data.get('event_type'),
                event_data.get('user_id'),
                event_data.get('action'),
                event_data.get('details'),
                event_data.get('classification'),
                event_data.get('timestamp', datetime.utcnow()),
                event_data.get('ip_address'),
                event_data.get('user_agent')
                )

            return result

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return 0

    async def get_audit_log(self, user_id: Optional[str] = None, 
                          event_type: Optional[str] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log"""
        try:
            if not self.pg_pool:
                return []

            async with self.pg_pool.acquire() as conn:
                query = "SELECT * FROM audit_log WHERE 1=1"
                params = []
                param_count = 0

                if user_id:
                    param_count += 1
                    query += f" AND user_id = ${param_count}"
                    params.append(user_id)

                if event_type:
                    param_count += 1
                    query += f" AND event_type = ${param_count}"
                    params.append(event_type)

                query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1}"
                params.append(limit)

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []

    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value"""
        try:
            if not self.redis_client:
                return False

            await self.redis_client.setex(key, ttl, json.dumps(value))
            return True

        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            if not self.redis_client:
                return None

            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None

    async def cache_delete(self, key: str) -> bool:
        """Delete cache value"""
        try:
            if not self.redis_client:
                return False

            await self.redis_client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False

    async def close(self):
        """Close database connections"""
        try:
            if self.pg_pool:
                await self.pg_pool.close()
                logger.info("PostgreSQL connection pool closed")

            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis connection closed")

        except Exception as e:
            logger.error(f"Error closing database connections: {e}")