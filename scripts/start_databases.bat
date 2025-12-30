@echo off
REM Script to start all databases (PostgreSQL, Redis, Neo4j) using Docker Compose
echo ========================================
echo 🗄️  Starting AMAS Databases
echo ========================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo 💡 Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if network exists and remove if there's a conflict
echo 🔍 Checking Docker network...
docker network inspect advanced-multi-agent-intelligence-system_amas-network >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Network does not exist, will be created
) else (
    echo ℹ️  Network already exists
)

REM Try to start databases
echo 📦 Starting PostgreSQL, Redis, and Neo4j...
docker-compose up -d postgres redis neo4j

if errorlevel 1 (
    echo.
    echo ⚠️  Failed to start databases. Trying to fix network issue...
    echo.
    echo 🔧 Attempting to remove conflicting network...
    docker network rm advanced-multi-agent-intelligence-system_amas-network >nul 2>&1
    
    echo 🔄 Retrying database startup...
    docker-compose up -d postgres redis neo4j
    
    if errorlevel 1 (
        echo.
        echo ⚠️  Still failing. Trying to use existing network...
        echo.
        echo 🔧 Checking for existing amas-network...
        docker network inspect amas-network >nul 2>&1
        if not errorlevel 1 (
            echo ℹ️  Found existing amas-network. Using it...
            docker-compose --project-name amas-db up -d postgres redis neo4j
            if errorlevel 1 (
                echo.
                echo ❌ Failed to start databases
                echo.
                echo 💡 Try manually:
                echo    1. docker network prune -f
                echo    2. docker-compose up -d postgres redis neo4j
                pause
                exit /b 1
            )
        ) else (
            echo.
            echo ❌ Failed to start databases after retry
            echo.
            echo 💡 Try manually:
            echo    1. docker network prune -f
            echo    2. docker-compose up -d postgres redis neo4j
            pause
            exit /b 1
        )
    )
)

echo.
echo ⏳ Waiting for databases to be ready...
timeout /t 15 /nobreak >nul

echo.
echo ✅ Checking database status...
docker-compose ps postgres redis neo4j

echo.
echo ========================================
echo ✅ Databases Started!
echo ========================================
echo.
echo 📊 Database Status:
echo    - PostgreSQL: localhost:5432
echo    - Redis: localhost:6379
echo    - Neo4j: localhost:7687 (Web UI: http://localhost:7474)
echo.
echo 💡 To view logs: docker-compose logs -f postgres redis neo4j
echo 💡 To stop: docker-compose stop postgres redis neo4j
echo.
pause

