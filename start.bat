@echo off
REM AMAS Intelligence System Startup Script for Windows

echo 🚀 Starting AMAS Intelligence System...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist data mkdir data
if not exist data\vector_index mkdir data\vector_index
if not exist data\knowledge_graph mkdir data\knowledge_graph
if not exist data\models mkdir data\models
if not exist data\workflows mkdir data\workflows

REM Start services with Docker Compose
echo 🐳 Starting Docker services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...
python scripts\health_check.py

REM Display access information
echo.
echo ✅ AMAS Intelligence System is running!
echo.
echo 🌐 Access Points:
echo    Web Interface: http://localhost:3000
echo    API Documentation: http://localhost:8000/docs
echo    n8n Workflows: http://localhost:5678
echo    Grafana Monitoring: http://localhost:3001
echo    Neo4j Browser: http://localhost:7474
echo.
echo 📊 System Status:
echo    Agents: 8 specialized intelligence agents
echo    Services: Ollama, Vector, Graph, Redis, PostgreSQL
echo    Workflows: n8n automation engine
echo    Monitoring: Prometheus + Grafana
echo.
echo 🛠️  CLI Commands:
echo    python scripts\cli.py --help
echo    python scripts\health_check.py
echo    python main.py
echo.
echo 📚 Documentation:
echo    README.md - Complete setup guide
echo    docs\ - Technical documentation
echo    examples\ - Usage examples
echo.
echo 🎯 Ready for intelligence operations!