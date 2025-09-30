#!/bin/bash
set -e

# AMAS Docker Entrypoint Script
# Handles initialization and startup of AMAS in containerized environment

echo "🚀 Starting AMAS - Advanced Multi-Agent Intelligence System"
echo "Environment: ${AMAS_ENVIRONMENT:-development}"
echo "Version: ${AMAS_VERSION:-1.0.0}"

# Function to wait for service availability
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-60}
    
    echo "⏳ Waiting for $service_name at $host:$port..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        if [ $i -eq $timeout ]; then
            echo "❌ Timeout waiting for $service_name"
            return 1
        fi
        
        sleep 1
    done
}

# Function to initialize database
init_database() {
    echo "🗄️ Initializing database..."
    
    # Wait for PostgreSQL to be ready
    if [ -n "${AMAS_DB_HOST}" ]; then
        wait_for_service "${AMAS_DB_HOST}" "${AMAS_DB_PORT:-5432}" "PostgreSQL"
    fi
    
    # Run database migrations
    python -c "
import asyncio
from amas.config import get_settings
from amas.services.database_service import DatabaseService

async def init_db():
    config = get_settings()
    db_service = DatabaseService(config)
    await db_service.initialize()
    await db_service.create_tables()
    print('Database initialized successfully')

asyncio.run(init_db())
"
}

# Function to wait for external services
wait_for_dependencies() {
    echo "🔍 Checking service dependencies..."
    
    # Wait for Redis
    if [ -n "${AMAS_REDIS_HOST}" ]; then
        wait_for_service "${AMAS_REDIS_HOST}" "${AMAS_REDIS_PORT:-6379}" "Redis"
    fi
    
    # Wait for Neo4j
    if [ -n "${AMAS_NEO4J_HOST}" ]; then
        wait_for_service "${AMAS_NEO4J_HOST}" "${AMAS_NEO4J_PORT:-7687}" "Neo4j"
    fi
    
    # Wait for Ollama
    if [ -n "${AMAS_LLM_HOST}" ]; then
        wait_for_service "${AMAS_LLM_HOST}" "${AMAS_LLM_PORT:-11434}" "Ollama"
    fi
}

# Function to validate configuration
validate_config() {
    echo "⚙️ Validating configuration..."
    
    python -c "
from amas.config import get_settings
try:
    config = get_settings()
    print(f'✅ Configuration valid for environment: {config.environment}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"
}

# Function to perform health check
health_check() {
    echo "🏥 Performing health check..."
    
    python -c "
import asyncio
from amas.main import AMASApplication

async def health_check():
    try:
        app = AMASApplication()
        status = await app.get_system_status()
        if status.get('status') == 'operational':
            print('✅ System health check passed')
        else:
            print(f'⚠️ System health check warning: {status}')
    except Exception as e:
        print(f'❌ Health check failed: {e}')
        exit(1)

asyncio.run(health_check())
"
}

# Main initialization sequence
main() {
    echo "🔧 Starting AMAS initialization sequence..."
    
    # Create necessary directories
    mkdir -p logs data models
    
    # Validate configuration
    validate_config
    
    # Wait for external dependencies
    if [ "${AMAS_WAIT_FOR_DEPENDENCIES:-true}" = "true" ]; then
        wait_for_dependencies
    fi
    
    # Initialize database if needed
    if [ "${AMAS_INIT_DATABASE:-true}" = "true" ]; then
        init_database
    fi
    
    # Perform health check if not in development
    if [ "${AMAS_ENVIRONMENT:-development}" != "development" ]; then
        health_check
    fi
    
    echo "✅ AMAS initialization completed successfully"
    echo "🚀 Starting AMAS application..."
    
    # Execute the main command
    exec "$@"
}

# Handle different initialization modes
case "${1:-start}" in
    "start")
        main uvicorn amas.api.main:app --host 0.0.0.0 --port 8000
        ;;
    "worker")
        main celery -A amas.tasks.worker worker --loglevel=info
        ;;
    "scheduler")
        main celery -A amas.tasks.worker beat --loglevel=info
        ;;
    "migrate")
        validate_config
        wait_for_service "${AMAS_DB_HOST}" "${AMAS_DB_PORT:-5432}" "PostgreSQL"
        init_database
        ;;
    "health")
        validate_config
        health_check
        ;;
    "shell")
        python -c "
import asyncio
from amas.main import AMASApplication
print('AMAS Python shell - Access via app variable')
app = AMASApplication()
"
        ;;
    *)
        # Execute custom command
        main "$@"
        ;;
esac