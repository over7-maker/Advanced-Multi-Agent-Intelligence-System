# AMAS Performance Tuning Guide

## 1. Database Optimization

### 1.1 Connection Pooling
```
# Optimal pool settings
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

### 1.2 Index Strategy
```
-- Create indexes for frequently queried columns
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority DESC);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- Composite indexes for complex queries
CREATE INDEX idx_tasks_user_status ON tasks(created_by, status) 
WHERE status IN ('executing', 'pending');

-- Partial indexes for specific conditions
CREATE INDEX idx_active_tasks ON tasks(task_id) 
WHERE status = 'executing';
```

### 1.3 Query Optimization
```
# Use pagination
tasks = await db.fetch(
    "SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1 OFFSET $2",
    limit, offset
)

# Avoid N+1 queries - use joins
tasks_with_agents = await db.fetch("""
    SELECT t.*, a.name as agent_name
    FROM tasks t
    LEFT JOIN agents a ON a.agent_id = ANY(t.assigned_agents)
    WHERE t.status = 'executing'
""")

# Use EXPLAIN ANALYZE to identify slow queries
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'executing';
```

### 1.4 PostgreSQL Tuning
```
# postgresql.conf optimizations
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 20MB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

## 2. Redis Optimization

### 2.1 Cache Strategy
```
# Cache frequently accessed data
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# Cache patterns
async def get_task_with_cache(task_id: str):
    cache_key = f"task:{task_id}"
    
    # Try cache first
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    task = await db.fetchrow("SELECT * FROM tasks WHERE task_id = $1", task_id)
    
    # Cache result
    await redis.set(cache_key, json.dumps(dict(task)), ex=CACHE_TTL_MEDIUM)
    
    return task
```

### 2.2 Cache Invalidation
```
# Invalidate on update
async def update_task(task_id: str, data: dict):
    await db.execute("UPDATE tasks SET ... WHERE task_id = $1", task_id)
    await redis.delete(f"task:{task_id}")
```

## 3. API Performance

### 3.1 Async Everything
```
# Use async/await for all I/O operations
@app.get("/tasks")
async def list_tasks(db = Depends(get_db)):
    tasks = await db.fetch("SELECT * FROM tasks")
    return tasks

# Concurrent execution
results = await asyncio.gather(
    db.fetch("SELECT * FROM tasks"),
    db.fetch("SELECT * FROM agents"),
    redis.get("stats")
)
```

### 3.2 Response Compression
```
# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3.3 Pagination
```
# Always paginate large responses
@app.get("/tasks")
async def list_tasks(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    tasks = await db.fetch(
        "SELECT * FROM tasks LIMIT $1 OFFSET $2",
        limit, offset
    )
    total = await db.fetchval("SELECT COUNT(*) FROM tasks")
    
    return {
        "items": tasks,
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

## 4. AI Provider Optimization

### 4.1 Response Caching
```
# Cache AI responses for identical prompts
async def generate_with_cache(prompt: str):
    cache_key = f"ai:response:{hashlib.md5(prompt.encode()).hexdigest()}"
    
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    response = await ai_provider.generate(prompt)
    
    # Cache for 1 hour
    await redis.set(cache_key, json.dumps(response), ex=3600)
    
    return response
```

### 4.2 Batch Processing
```
# Process multiple tasks in parallel
async def process_tasks_batch(tasks: List[Task]):
    async with asyncio.TaskGroup() as tg:
        for task in tasks:
            tg.create_task(execute_task(task))
```

## 5. Frontend Optimization

### 5.1 Code Splitting
```
// Lazy load components
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const TaskList = React.lazy(() => import('./components/TaskList'));
```

### 5.2 Asset Optimization
```
// package.json build optimization
{
  "scripts": {
    "build": "react-scripts build && npm run optimize",
    "optimize": "npx imagemin build/static/**/*.{jpg,png} --out-dir=build/static"
  }
}
```

## 6. Monitoring & Profiling

### 6.1 Application Profiling
```
# Profile slow endpoints
import cProfile
import pstats

def profile_endpoint():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Execute code
    result = expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### 6.2 Query Performance Monitoring
```
# Log slow queries
async def execute_with_monitoring(query: str, *args):
    start = time.time()
    result = await db.fetch(query, *args)
    duration = time.time() - start
    
    if duration > 1.0:  # Slow query threshold
        logger.warning(f"Slow query ({duration:.2f}s): {query}")
    
    return result
```

## Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p95) | < 200ms | < 500ms |
| Database Query Time (p95) | < 50ms | < 200ms |
| Task Execution Time | < 30s | < 60s |
| Frontend Load Time | < 2s | < 4s |
| WebSocket Latency | < 100ms | < 300ms |
| Cache Hit Rate | > 80% | > 60% |
| Error Rate | < 0.1% | < 1% |

