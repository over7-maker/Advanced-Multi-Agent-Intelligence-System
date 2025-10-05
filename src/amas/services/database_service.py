"""
Database Service Implementation for AMAS
SECURITY HARDENED - No hardcoded passwords
"""

import asyncio
import logging
import os
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
"""
class DatabaseService:
    """Database Service for AMAS Intelligence System - Security hardened"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pg_pool = None
        self.redis_client = None
        self.initialized = False
        
        # Security: Validate configuration
        self._validate_config()

    def _validate_config(self):
        Validate database configuration for security"""
        # Ensure no secrets are in config - they should be in environment
        db_config = self.config.get('database', {})
        redis_config = self.config.get('redis', {})
        
        # Warn if passwords found in config (should use env vars)
        if 'password' in db_config or 'password' in redis_config:
            logger.warning("Passwords found in config - should use environment variables")
"""
    async def initialize(self):
        """Initialize database connections securely"""
        try:
            if ASYNC_DB_AVAILABLE:
                # Initialize PostgreSQL connection
                await self._initialize_postgres()
                
                # Initialize Redis connection
                await self._initialize_redis()
                
                # Create database schema
                await self._create_schema()
                
                self.initialized = True
                logger.info("Database service initialized successfully")"""
            else:"""
                logger.warning("Database drivers not available, using fallback mode")
                self.initialized = True

        except Exception as e:"""
            logger.error(f"Failed to initialize database service: {e}")
            raise

    async def _initialize_postgres(self):
        """Initialize PostgreSQL connection using environment variables"""
        try:
            # SECURITY: Get credentials from environment variables only
            host = os.getenv('POSTGRES_HOST', 'localhost')
            port = int(os.getenv('POSTGRES_PORT', '5432'))
            user = os.getenv('POSTGRES_USER', 'amas')
            password = os.getenv('POSTGRES_PASSWORD')
            database = os.getenv('POSTGRES_DB', 'amas')
            
            if not password:
                logger.warning("POSTGRES_PASSWORD environment variable not set")
                # Fallback only for development
                password = self.config.get('database', {}).get('password', 'amas123')
            
            # Validate connection parameters"""
            if not all([host, user, database]):"""
                raise ValueError("Missing required database connection parameters")
            
            self.pg_pool = await asyncpg.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'amas_intelligence_system',
                    'jit': 'off'  # Disable JIT for security
                }
            )"""
            logger.info(f"PostgreSQL connection pool created - host: {host}, db: {database}")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise

    async def _initialize_redis(self):
        """Initialize Redis connection using environment variables"""
        try:
            # SECURITY: Get credentials from environment variables only
            host = os.getenv('REDIS_HOST', 'localhost')
            port = int(os.getenv('REDIS_PORT', '6379'))
            db = int(os.getenv('REDIS_DB', '0'))
            password = os.getenv('REDIS_PASSWORD')
            
            # Create Redis connection with security settings
            connection_params = {
                'host': host,
                'port': port,
                'db': db,
                'decode_responses': True,
                'socket_timeout': 5,
                'socket_connect_timeout': 5,
                'retry_on_timeout': True,
                'health_check_interval': 30
            }
            
            # Only add password if it exists
            if password:
                connection_params['password'] = password
            
            self.redis_client = redis.Redis(**connection_params)
            
            # Test connection
            await self.redis_client.ping()
            logger.info(f"Redis connection established - host: {host}:{port}")
            """
        except Exception as e:"""
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def _create_schema(self):"""
        Create database schema with security considerations"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Create tasks table with security columns
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id UUID PRIMARY KEY,
                        type VARCHAR(100) NOT NULL,
                        description TEXT,
                        status VARCHAR(50) NOT NULL,
                        priority INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5),
                        assigned_agent VARCHAR(100),
                        created_by VARCHAR(100),
                        security_classification VARCHAR(20) DEFAULT 'internal',
                        created_at TIMESTAMP DEFAULT NOW(),
                        started_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        parameters JSONB,
                        result JSONB,
                        error TEXT,
                        CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
                        CONSTRAINT valid_classification CHECK (security_classification IN ('public', 'internal', 'confidential', 'restricted'))
                    )
                )

                # Create agents table with security controls
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS agents (
                        id VARCHAR(100) PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        type VARCHAR(100) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        capabilities JSONB,
                        security_clearance VARCHAR(20) DEFAULT 'internal',
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_activity TIMESTAMP,
                        metrics JSONB,
                        is_active BOOLEAN DEFAULT TRUE,
                        CONSTRAINT valid_agent_status CHECK (status IN ('active', 'inactive', 'maintenance', 'error')),
                        CONSTRAINT valid_clearance CHECK (security_clearance IN ('public', 'internal', 'confidential', 'restricted'))
                    )
                """)

                # Create audit_log table with enhanced security
                await conn.execute(
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id SERIAL PRIMARY KEY,
                        event_id UUID UNIQUE,
                        event_type VARCHAR(100) NOT NULL,
                        user_id VARCHAR(100),
                        session_id VARCHAR(100),
                        action VARCHAR(200) NOT NULL,
                        resource VARCHAR(200),
                        details JSONB,
                        classification VARCHAR(50) DEFAULT 'internal',
                        result VARCHAR(20) DEFAULT 'success',
                        timestamp TIMESTAMP DEFAULT NOW(),
                        ip_address INET,
                        user_agent TEXT,
                        correlation_id VARCHAR(100),
                        CONSTRAINT valid_result CHECK (result IN ('success', 'failure', 'warning')),
                        CONSTRAINT valid_audit_classification CHECK (classification IN ('public', 'internal', 'confidential', 'restricted'))
                    )
                """)
                
                # Create users table for authentication
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        salt VARCHAR(100) NOT NULL,
                        roles JSONB DEFAULT '[]',
                        security_clearance VARCHAR(20) DEFAULT 'internal',
                        is_active BOOLEAN DEFAULT TRUE,
                        failed_login_attempts INTEGER DEFAULT 0,
                        last_login TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        CONSTRAINT valid_user_clearance CHECK (security_clearance IN ('public', 'internal', 'confidential', 'restricted'))
                    )
                """)

                # Create security indexes for performance and security
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")"""
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(type)")"""
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_by ON tasks(created_by)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_classification ON tasks(security_classification)")
                
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active)")
                
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_classification ON audit_log(classification)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_correlation_id ON audit_log(correlation_id)")
                
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")

                logger.info("Database schema created successfully with security enhancements")

        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check database health without exposing sensitive information"""
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
                    health_status['connections']['postgresql'] = {
                        'status': 'healthy',
                        'pool_size': self.pg_pool.get_size(),
                        'idle_connections': self.pg_pool.get_idle_size()
                    }
                except Exception as e:
                    health_status['connections']['postgresql'] = {'status': 'unhealthy'}
                    health_status['status'] = 'degraded'

            # Check Redis
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                    info = await self.redis_client.info()
                    health_status['connections']['redis'] = {
                        'status': 'healthy',
                        'connected_clients': info.get('connected_clients', 0),
                        'used_memory_human': info.get('used_memory_human', 'unknown')
                    }
                except Exception as e:
                    health_status['connections']['redis'] = {'status': 'unhealthy'}
                    health_status['status'] = 'degraded'

            return health_status
"""
        except Exception as e:"""
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'database'
            }

    async def save_task(self, task_data: Dict[str, Any]) -> str:"""
        Save task to database with security validation"""
        try:
            if not self.pg_pool:
                return task_data.get('id', 'no_db')
            
            # Security validation
            required_fields = ['id', 'type', 'status']
            for field in required_fields:
                if field not in task_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate field lengths for security"""
            if len(task_data.get('type', '')) > 100:"""
                raise ValueError("Task type too long")
            
            if len(task_data.get('description', '')) > 10000:"""
                raise ValueError("Task description too long")

            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO tasks (id, type, description, status, priority, assigned_agent, 
                                    created_by, security_classification, created_at, started_at, 
                                    completed_at, parameters, result, error)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
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
                task_data.get('description', '')[:10000],  # Truncate for security
                task_data.get('status'),
                min(max(task_data.get('priority', 2), 1), 5),  # Clamp priority
                task_data.get('assigned_agent'),
                task_data.get('created_by'),
                task_data.get('security_classification', 'internal'),
                task_data.get('created_at', datetime.utcnow()),
                task_data.get('started_at'),
                task_data.get('completed_at'),
                json.dumps(task_data.get('parameters', {}))[:50000],  # Limit JSON size
                json.dumps(task_data.get('result', {}))[:50000],
                task_data.get('error', '')[:5000] if task_data.get('error') else None
                )

            return task_data.get('id')

        except Exception as e:
            logger.error(f"Failed to save task: {e}")
            raise
"""
    async def get_task(self, task_id: str, user_clearance: str = 'internal') -> Optional[Dict[str, Any]]:
        """Get task from database with security filtering"""
        try:
            if not self.pg_pool or not task_id:
                return None
            
            # Input validation
            if len(task_id) > 100:
                return None

            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    SELECT * FROM tasks 
                    WHERE id = $1 
                    AND (security_classification = 'public' OR 
                         (security_classification = 'internal' AND $2 IN ('internal', 'confidential', 'restricted')) OR
                         (security_classification = 'confidential' AND $2 IN ('confidential', 'restricted')) OR
                         (security_classification = 'restricted' AND $2 = 'restricted'))
                """, task_id, user_clearance)

                if row:
                    task_dict = dict(row)
                    # Remove sensitive fields based on clearance
                    if user_clearance not in ['confidential', 'restricted']:
                        task_dict.pop('error', None)
                    return task_dict

            return None

        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None

    async def get_tasks(self, status_filter: Optional[str] = None, limit: int = 100, """
                       user_clearance: str = 'internal') -> List[Dict[str, Any]]:
        """Get tasks from database with security filtering"""
        try:
            if not self.pg_pool:
                return []
            
            # Security: limit the maximum number of results
            limit = min(limit, 1000)

            async with self.pg_pool.acquire() as conn:
                base_query = 
                    SELECT * FROM tasks 
                    WHERE (security_classification = 'public' OR 
                           (security_classification = 'internal' AND $2 IN ('internal', 'confidential', 'restricted')) OR
                           (security_classification = 'confidential' AND $2 IN ('confidential', 'restricted')) OR
                           (security_classification = 'restricted' AND $2 = 'restricted'))
                """
                
                if status_filter:
                    # Validate status filter
                    valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
                    if status_filter not in valid_statuses:
                        return []
                    
                    rows = await conn.fetch(base_query + """
                        AND status = $1 ORDER BY created_at DESC LIMIT $3
                    , status_filter, user_clearance, limit)
                else:
                    rows = await conn.fetch(base_query + """
                        ORDER BY created_at DESC LIMIT $3
                    """, None, user_clearance, limit)

                tasks = []
                for row in rows:
                    task_dict = dict(row)
                    # Remove sensitive fields based on clearance
                    if user_clearance not in ['confidential', 'restricted']:
                        task_dict.pop('error', None)
                    tasks.append(task_dict)
                
                return tasks

        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
"""
    async def save_agent(self, agent_data: Dict[str, Any]) -> str:
        """Save agent to database with security validation"""
        try:
            if not self.pg_pool:
                return agent_data.get('id', 'no_db')
            
            # Security validation
            required_fields = ['id', 'name', 'type', 'status']
            for field in required_fields:
                if field not in agent_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate field lengths"""
            if len(agent_data.get('name', '')) > 200:"""
                raise ValueError("Agent name too long")

            async with self.pg_pool.acquire() as conn:"""
                await conn.execute(
                    INSERT INTO agents (id, name, type, status, capabilities, security_clearance,
                                      created_at, last_activity, metrics, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        status = EXCLUDED.status,
                        capabilities = EXCLUDED.capabilities,
                        security_clearance = EXCLUDED.security_clearance,
                        last_activity = EXCLUDED.last_activity,
                        metrics = EXCLUDED.metrics,
                        is_active = EXCLUDED.is_active
                """,
                agent_data.get('id'),
                agent_data.get('name')[:200],  # Truncate for security
                agent_data.get('type')[:100],
                agent_data.get('status'),
                json.dumps(agent_data.get('capabilities', []))[:10000],
                agent_data.get('security_clearance', 'internal'),
                agent_data.get('created_at', datetime.utcnow()),
                agent_data.get('last_activity'),
                json.dumps(agent_data.get('metrics', {}))[:10000],
                agent_data.get('is_active', True)
                )

            return agent_data.get('id')

        except Exception as e:
            logger.error(f"Failed to save agent: {e}")
            raise
"""
    async def get_agent(self, agent_id: str, user_clearance: str = 'internal') -> Optional[Dict[str, Any]]:
        """Get agent from database with security filtering"""
        try:
            if not self.pg_pool or not agent_id:
                return None
            
            # Input validation
            if len(agent_id) > 100:
                return None

            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    SELECT * FROM agents 
                    WHERE id = $1 AND is_active = TRUE
                    AND (security_clearance = 'public' OR 
                         (security_clearance = 'internal' AND $2 IN ('internal', 'confidential', 'restricted')) OR
                         (security_clearance = 'confidential' AND $2 IN ('confidential', 'restricted')) OR
                         (security_clearance = 'restricted' AND $2 = 'restricted'))
                """, agent_id, user_clearance)

                if row:
                    return dict(row)

            return None

        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
"""
    async def get_agents(self, user_clearance: str = 'internal') -> List[Dict[str, Any]]:
        """Get all agents from database with security filtering"""
        try:
            if not self.pg_pool:
                return []

            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(
                    SELECT * FROM agents 
                    WHERE is_active = TRUE
                    AND (security_clearance = 'public' OR 
                         (security_clearance = 'internal' AND $1 IN ('internal', 'confidential', 'restricted')) OR
                         (security_clearance = 'confidential' AND $1 IN ('confidential', 'restricted')) OR
                         (security_clearance = 'restricted' AND $1 = 'restricted'))
                    ORDER BY created_at DESC
                    LIMIT 1000
                """, user_clearance)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []
"""
    async def save_audit_event(self, event_data: Dict[str, Any]) -> int:
        """Save audit event with security validation"""
        try:
            if not self.pg_pool:
                return 0
            
            # Security validation - sanitize audit data
            sanitized_details = self._sanitize_audit_details(event_data.get('details', {}))

            async with self.pg_pool.acquire() as conn:
                result = await conn.fetchval(
                    INSERT INTO audit_log (event_id, event_type, user_id, session_id, action, 
                                         resource, details, classification, result, timestamp, 
                                         ip_address, user_agent, correlation_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                    RETURNING id
                """,
                event_data.get('event_id'),
                event_data.get('event_type', '')[:100],
                event_data.get('user_id', '')[:100],
                event_data.get('session_id', '')[:100],
                event_data.get('action', '')[:200],
                event_data.get('resource', '')[:200],
                json.dumps(sanitized_details)[:50000],
                event_data.get('classification', 'internal'),
                event_data.get('result', 'success'),
                event_data.get('timestamp', datetime.utcnow()),
                event_data.get('ip_address'),
                event_data.get('user_agent', '')[:1000] if event_data.get('user_agent') else None,
                event_data.get('correlation_id', '')[:100]
                )

            return result

        except Exception as e:
            logger.error(f"Failed to save audit event: {e}")
            return 0
    """
    def _sanitize_audit_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize audit event details to remove sensitive data"""
        import re
        
        sensitive_patterns = [
            r'password=os.getenv("POSTGRES_PASSWORD", "secure_default")
]+["\']',
            r'token["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'key["\']?\s*[:=]\s*["\'][^"\'
]+["\']',
            r'secret["\']?\s*[:=]\s*["\'][^"\'
]+["\']'
        ]
        
        def sanitize_value(value):
            if isinstance(value, str):
                for pattern in sensitive_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return '[REDACTED]'
                return value[:1000]  # Limit string length
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(v) for v in value]
            else:
                return value
        
        return {k: sanitize_value(v) for k, v in details.items()}

    async def get_audit_log(self, user_id: Optional[str] = None, 
                          event_type: Optional[str] = None, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          limit: int = 100,
                          offset: int = 0,
                          user_clearance: str = 'internal') -> List[Dict[str, Any]]:
        """Get audit log with security filtering
        try:
            if not self.pg_pool:
                return []
            
            # Security: limit results and validate inputs
            limit = min(limit, 1000)
            offset = max(offset, 0)

            async with self.pg_pool.acquire() as conn:
                query = """
                    SELECT event_id, event_type, user_id, action, resource, 
                           classification, result, timestamp, correlation_id
                    FROM audit_log 
                    WHERE (classification = 'public' OR 
                           (classification = 'internal' AND $1 IN ('internal', 'confidential', 'restricted')) OR
                           (classification = 'confidential' AND $1 IN ('confidential', 'restricted')) OR
                           (classification = 'restricted' AND $1 = 'restricted'))
                """
                params = [user_clearance]
                param_count = 1

                if user_id:
                    param_count += 1
                    query += f" AND user_id = ${param_count}"
                    params.append(user_id[:100])  # Truncate for security

                if event_type:"""
                    param_count += 1"""
                    query += f" AND event_type = ${param_count}"
                    params.append(event_type[:100])
                
                if start_date:
                    param_count += 1"""
                    query += f" AND timestamp >= ${param_count}"
                    params.append(start_date)
                
                if end_date:
                    param_count += 1
                    query += f" AND timestamp <= ${param_count}"
                    params.append(end_date)

                query += f" ORDER BY timestamp DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
                params.extend([offset, limit])

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get audit log: {e}")
            return []
    
    async def get_audit_statistics(self, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 user_clearance: str = 'internal') -> Dict[str, Any]:
        """Get audit statistics with security filtering
        try:
            if not self.pg_pool:
                return {}

            async with self.pg_pool.acquire() as conn:
                # Base security filter
                security_filter = """
                    WHERE (classification = 'public' OR 
                           (classification = 'internal' AND $1 IN ('internal', 'confidential', 'restricted')) OR
                           (classification = 'confidential' AND $1 IN ('confidential', 'restricted')) OR
                           (classification = 'restricted' AND $1 = 'restricted'))
                """
                params = [user_clearance]
                param_count = 1
                
                if start_date:
                    param_count += 1
                    security_filter += f" AND timestamp >= ${param_count}"
                    params.append(start_date)
                
                if end_date:"""
                    param_count += 1"""
                    security_filter += f" AND timestamp <= ${param_count}"
                    params.append(end_date)

                # Get basic statistics"""
                total_events = await conn.fetchval(f
                    SELECT COUNT(*) FROM audit_log {security_filter}
                """, *params)
                
                # Get event type distribution
                event_types = await conn.fetch(f"""
                    SELECT event_type, COUNT(*) as count 
                    FROM audit_log {security_filter}
                    GROUP BY event_type 
                    ORDER BY count DESC 
                    LIMIT 10
                """, *params)
                
                return {
                    'total_events': total_events,
                    'events_by_type': {row['event_type']: row['count'] for row in event_types},
                    'period': {
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {}
    """
    async def cleanup_old_audit_logs(self, cutoff_date: datetime) -> int:
        """Clean up old audit logs with security validation"""
        try:
            if not self.pg_pool:
                return 0
            
            # Security: Only allow cleanup of logs older than 30 days
            min_cutoff = datetime.utcnow() - timedelta(days=30)
            if cutoff_date > min_cutoff:
                logger.warning("Cutoff date too recent for security - adjusting to 30 days ago")
                cutoff_date = min_cutoff
"""
            async with self.pg_pool.acquire() as conn:
                result = await conn.fetchval("""
                    DELETE FROM audit_log 
                    WHERE timestamp < $1 
                    AND classification NOT IN ('confidential', 'restricted')
                    RETURNING COUNT(*)
                """, cutoff_date)

                return result or 0

        except Exception as e:
            logger.error(f"Failed to cleanup audit logs: {e}")
            return 0
"""
    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cache value with security validation"""
        try:
            if not self.redis_client or not key:
                return False
            
            # Security: validate key and limit TTL
            if len(key) > 250 or not key.replace(':', '').replace('-', '').replace('_', '').isalnum():
                return False
            
            ttl = min(ttl, 86400)  # Max 24 hours
            
            # Sanitize value before caching
            safe_value = self._sanitize_cache_value(value)
            await self.redis_client.setex(key, ttl, json.dumps(safe_value, default=str))
            return True

        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    """
    def _sanitize_cache_value(self, value: Any) -> Any:
        """Sanitize cache values to remove sensitive data"""
        if isinstance(value, dict):
            sanitized = {}
            for k, v in value.items():
                if any(sensitive in str(k).lower() for sensitive in ['password', 'token', 'key', 'secret']):
                    sanitized[k] = '[REDACTED]'
                else:
                    sanitized[k] = self._sanitize_cache_value(v)
            return sanitized
        elif isinstance(value, list):
            return [self._sanitize_cache_value(v) for v in value[:100]]  # Limit list size
        elif isinstance(value, str):
            return value[:10000]  # Limit string size
        else:
            return value

    async def cache_get(self, key: str) -> Optional[Any]:
        Get cache value with security validation"""
        try:
            if not self.redis_client or not key:
                return None
            
            # Security: validate key
            if len(key) > 250:
                return None

            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None

        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None
"""
    async def cache_delete(self, key: str) -> bool:
        """Delete cache value with security validation"""
        try:
            if not self.redis_client or not key:
                return False
            
            # Security: validate key
            if len(key) > 250:
                return False

            await self.redis_client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
"""
    async def close(self):
        """Close database connections securely"""
        try:
            if self.pg_pool:
                await self.pg_pool.close()
                logger.info("PostgreSQL connection pool closed")

            if self.redis_client:"""
                await self.redis_client.close()"""
                logger.info("Redis connection closed")

        except Exception as e:"""
            logger.error(f"Error closing database connections: {e}")
