"""
Database connection pooling and optimization for AMAS
Implements RD-083: Optimize database queries and connections
Implements RD-084: Implement connection pooling
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import asyncpg
import psycopg2
from psycopg2 import pool
import time
from dataclasses import dataclass
from enum import Enum
import threading
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
DB_CONNECTIONS_ACTIVE = Gauge('amas_db_connections_active', 'Active database connections')
DB_CONNECTIONS_IDLE = Gauge('amas_db_connections_idle', 'Idle database connections')
DB_CONNECTIONS_TOTAL = Gauge('amas_db_connections_total', 'Total database connections')
DB_QUERY_DURATION = Histogram('amas_db_query_duration_seconds', 'Database query duration', ['query_type'])
DB_QUERY_COUNT = Counter('amas_db_queries_total', 'Total database queries', ['query_type', 'status'])
DB_CONNECTION_ERRORS = Counter('amas_db_connection_errors_total', 'Database connection errors')

class ConnectionState(Enum):
    """Connection states"""
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    CLOSED = "closed"

@dataclass
class ConnectionInfo:
    """Connection information"""
    connection_id: str
    state: ConnectionState
    created_at: float
    last_used: float
    query_count: int
    error_count: int

class AsyncConnectionPool:
    """AsyncPG connection pool with monitoring"""
    
    def __init__(self, 
                 database_url: str,
                 min_connections: int = 5,
                 max_connections: int = 20,
                 max_queries: int = 50000,
                 max_inactive_connection_lifetime: float = 300.0):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_queries = max_queries
        self.max_inactive_connection_lifetime = max_inactive_connection_lifetime
        
        self.pool: Optional[asyncpg.Pool] = None
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'connection_errors': 0
        }
        
    async def initialize(self):
        """Initialize the connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_connections,
                max_size=self.max_connections,
                max_queries=self.max_queries,
                max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
                init=self._init_connection
            )
            logger.info(f"Database connection pool initialized: {self.min_connections}-{self.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            DB_CONNECTION_ERRORS.inc()
            raise
            
    async def _init_connection(self, connection):
        """Initialize a new connection"""
        connection_id = id(connection)
        self.connection_info[connection_id] = ConnectionInfo(
            connection_id=str(connection_id),
            state=ConnectionState.IDLE,
            created_at=time.time(),
            last_used=time.time(),
            query_count=0,
            error_count=0
        )
        logger.debug(f"Initialized connection {connection_id}")
        
    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.connection_info.clear()
            logger.info("Database connection pool closed")
            
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")
            
        connection = None
        try:
            connection = await self.pool.acquire()
            connection_id = id(connection)
            
            # Update connection info
            if connection_id in self.connection_info:
                info = self.connection_info[connection_id]
                info.state = ConnectionState.ACTIVE
                info.last_used = time.time()
            else:
                self.connection_info[connection_id] = ConnectionInfo(
                    connection_id=str(connection_id),
                    state=ConnectionState.ACTIVE,
                    created_at=time.time(),
                    last_used=time.time(),
                    query_count=0,
                    error_count=0
                )
            
            yield connection
            
        except Exception as e:
            if connection:
                connection_id = id(connection)
                if connection_id in self.connection_info:
                    self.connection_info[connection_id].error_count += 1
                    self.connection_info[connection_id].state = ConnectionState.ERROR
            self.stats['connection_errors'] += 1
            DB_CONNECTION_ERRORS.inc()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection_id = id(connection)
                if connection_id in self.connection_info:
                    self.connection_info[connection_id].state = ConnectionState.IDLE
                await self.pool.release(connection)
                
    async def execute_query(self, query: str, *args, query_type: str = "unknown") -> Any:
        """Execute a query with monitoring"""
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                result = await conn.fetch(query, *args)
                
                # Update stats
                self.stats['total_queries'] += 1
                self.stats['successful_queries'] += 1
                DB_QUERY_COUNT.labels(query_type=query_type, status='success').inc()
                
                # Update connection info
                connection_id = id(conn)
                if connection_id in self.connection_info:
                    self.connection_info[connection_id].query_count += 1
                
                return result
                
        except Exception as e:
            self.stats['total_queries'] += 1
            self.stats['failed_queries'] += 1
            DB_QUERY_COUNT.labels(query_type=query_type, status='error').inc()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)
            
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not self.pool:
            return {}
            
        active_connections = sum(1 for info in self.connection_info.values() 
                               if info.state == ConnectionState.ACTIVE)
        idle_connections = sum(1 for info in self.connection_info.values() 
                             if info.state == ConnectionState.IDLE)
        total_connections = len(self.connection_info)
        
        # Update Prometheus metrics
        DB_CONNECTIONS_ACTIVE.set(active_connections)
        DB_CONNECTIONS_IDLE.set(idle_connections)
        DB_CONNECTIONS_TOTAL.set(total_connections)
        
        return {
            'pool_size': self.pool.get_size(),
            'pool_min_size': self.pool.get_min_size(),
            'pool_max_size': self.pool.get_max_size(),
            'active_connections': active_connections,
            'idle_connections': idle_connections,
            'total_connections': total_connections,
            'total_queries': self.stats['total_queries'],
            'successful_queries': self.stats['successful_queries'],
            'failed_queries': self.stats['failed_queries'],
            'success_rate': (self.stats['successful_queries'] / self.stats['total_queries'] * 100) 
                          if self.stats['total_queries'] > 0 else 0
        }

class SyncConnectionPool:
    """Synchronous psycopg2 connection pool"""
    
    def __init__(self, 
                 database_url: str,
                 min_connections: int = 5,
                 max_connections: int = 20):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        # Parse database URL
        self.connection_params = self._parse_database_url(database_url)
        
        self.pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'connection_errors': 0
        }
        
    def _parse_database_url(self, url: str) -> Dict[str, str]:
        """Parse database URL into connection parameters"""
        # Simple URL parsing - in production, use urllib.parse
        if url.startswith('postgresql://'):
            url = url[13:]  # Remove postgresql://
            
        if '@' in url:
            auth, host_part = url.split('@', 1)
            if ':' in auth:
                user, password = auth.split(':', 1)
            else:
                user, password = auth, ''
        else:
            user, password = 'postgres', ''
            
        if '/' in host_part:
            host_port, database = host_part.split('/', 1)
        else:
            host_port, database = host_part, 'postgres'
            
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, '5432'
            
        return {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
    def initialize(self):
        """Initialize the connection pool"""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                **self.connection_params
            )
            logger.info(f"Sync database connection pool initialized: {self.min_connections}-{self.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize sync connection pool: {e}")
            DB_CONNECTION_ERRORS.inc()
            raise
            
    def close(self):
        """Close the connection pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Sync database connection pool closed")
            
    def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            raise RuntimeError("Connection pool not initialized")
            
        try:
            return self.pool.getconn()
        except Exception as e:
            self.stats['connection_errors'] += 1
            DB_CONNECTION_ERRORS.inc()
            logger.error(f"Failed to get connection from pool: {e}")
            raise
            
    def put_connection(self, connection):
        """Return a connection to the pool"""
        if self.pool and connection:
            self.pool.putconn(connection)
            
    def execute_query(self, query: str, params: tuple = (), query_type: str = "unknown") -> List[tuple]:
        """Execute a query with monitoring"""
        start_time = time.time()
        connection = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            
            # Update stats
            self.stats['total_queries'] += 1
            self.stats['successful_queries'] += 1
            DB_QUERY_COUNT.labels(query_type=query_type, status='success').inc()
            
            return result
            
        except Exception as e:
            self.stats['total_queries'] += 1
            self.stats['failed_queries'] += 1
            DB_QUERY_COUNT.labels(query_type=query_type, status='error').inc()
            logger.error(f"Sync query execution failed: {e}")
            raise
        finally:
            if connection:
                self.put_connection(connection)
            duration = time.time() - start_time
            DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)
            
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not self.pool:
            return {}
            
        return {
            'pool_size': self.pool.closed,
            'pool_min_size': self.min_connections,
            'pool_max_size': self.max_connections,
            'total_queries': self.stats['total_queries'],
            'successful_queries': self.stats['successful_queries'],
            'failed_queries': self.stats['failed_queries'],
            'success_rate': (self.stats['successful_queries'] / self.stats['total_queries'] * 100) 
                          if self.stats['total_queries'] > 0 else 0
        }

class QueryOptimizer:
    """Database query optimizer"""
    
    def __init__(self, connection_pool: Union[AsyncConnectionPool, SyncConnectionPool]):
        self.pool = connection_pool
        self.query_cache = {}  # Simple query plan cache
        
    def optimize_query(self, query: str) -> str:
        """Optimize SQL query"""
        # Basic query optimization
        optimized = query.strip()
        
        # Remove unnecessary whitespace
        optimized = ' '.join(optimized.split())
        
        # Add query hints if needed
        if 'SELECT' in optimized.upper() and 'LIMIT' not in optimized.upper():
            # Add LIMIT for large result sets
            if 'ORDER BY' in optimized.upper():
                optimized += ' LIMIT 1000'
                
        return optimized
        
    def get_query_plan(self, query: str) -> Dict[str, Any]:
        """Get query execution plan"""
        # This would typically use EXPLAIN ANALYZE
        # For now, return basic info
        return {
            'query': query,
            'estimated_cost': 0,
            'estimated_rows': 0,
            'indexes_used': [],
            'optimization_suggestions': []
        }

# Global connection pools
async_pool: Optional[AsyncConnectionPool] = None
sync_pool: Optional[SyncConnectionPool] = None

async def initialize_connection_pools(database_url: str):
    """Initialize both async and sync connection pools"""
    global async_pool, sync_pool
    
    # Initialize async pool
    async_pool = AsyncConnectionPool(database_url)
    await async_pool.initialize()
    
    # Initialize sync pool
    sync_pool = SyncConnectionPool(database_url)
    sync_pool.initialize()
    
    logger.info("Database connection pools initialized")

async def get_async_pool() -> AsyncConnectionPool:
    """Get async connection pool"""
    if not async_pool:
        raise RuntimeError("Async connection pool not initialized")
    return async_pool

def get_sync_pool() -> SyncConnectionPool:
    """Get sync connection pool"""
    if not sync_pool:
        raise RuntimeError("Sync connection pool not initialized")
    return sync_pool

async def close_connection_pools():
    """Close all connection pools"""
    global async_pool, sync_pool
    
    if async_pool:
        await async_pool.close()
        async_pool = None
        
    if sync_pool:
        sync_pool.close()
        sync_pool = None
        
    logger.info("All connection pools closed")