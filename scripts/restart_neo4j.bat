@echo off
REM Script to restart Neo4j container to reset authentication rate limit
echo ========================================
echo 🔄 Restarting Neo4j Container
echo ========================================
echo.

echo 📍 Checking Neo4j container status...
docker ps --filter "name=neo4j" --format "{{.Names}}\t{{.Status}}"

echo.
echo 🔄 Restarting Neo4j container...
docker restart advanced-multi-agent-intelligence-system-neo4j-1

if errorlevel 1 (
    echo.
    echo ⚠️  Failed to restart Neo4j. Trying alternative method...
    docker-compose restart neo4j
    if errorlevel 1 (
        echo.
        echo ❌ Failed to restart Neo4j
        echo 💡 Try manually: docker restart advanced-multi-agent-intelligence-system-neo4j-1
        pause
        exit /b 1
    )
)

echo.
echo ⏳ Waiting for Neo4j to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo 📍 Checking Neo4j status after restart...
docker ps --filter "name=neo4j" --format "{{.Names}}\t{{.Status}}"

echo.
echo ========================================
echo ✅ Neo4j restart complete!
echo ========================================
echo.
echo 💡 Note: Wait 10-15 seconds before restarting the backend
echo    to allow Neo4j to fully initialize.
echo.
pause

