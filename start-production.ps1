# start-production.ps1
# AMAS Production Startup Script for Windows

param(
    [switch]$UseDocker = $true,
    [string]$DatabasePassword = "amas_password",
    [string]$RedisPassword = "amas_redis_password",
    [string]$Neo4jPassword = "amas_password"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 AMAS Production Startup Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Get project root
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file. Please edit it with your production settings!" -ForegroundColor Yellow
        Write-Host "   Press any key to continue after editing .env..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "❌ .env.example not found. Please create .env manually." -ForegroundColor Red
        exit 1
    }
}

# Load .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and $value) {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
}

# Set production environment
$env:ENVIRONMENT = "production"
$env:LOG_LEVEL = "INFO"

# Check Docker
if ($UseDocker -and (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "✅ Docker found" -ForegroundColor Green
    Write-Host "🐳 Starting Docker services...`n" -ForegroundColor Cyan
    
    # Start PostgreSQL
    Write-Host "📦 Starting PostgreSQL..." -ForegroundColor Yellow
    $postgresRunning = docker ps -a --filter "name=amas-postgres" --format "{{.Names}}" | Select-String "amas-postgres"
    if ($postgresRunning) {
        docker start amas-postgres 2>$null
        Write-Host "   ✅ PostgreSQL started" -ForegroundColor Green
    } else {
        docker run -d --name amas-postgres `
            -e POSTGRES_DB=amas `
            -e POSTGRES_USER=postgres `
            -e POSTGRES_PASSWORD=$DatabasePassword `
            -p 5432:5432 `
            -v postgres_data:/var/lib/postgresql/data `
            postgres:15-alpine 2>$null
        Write-Host "   ✅ PostgreSQL container created and started" -ForegroundColor Green
    }
    
    # Start Redis
    Write-Host "📦 Starting Redis..." -ForegroundColor Yellow
    $redisRunning = docker ps -a --filter "name=amas-redis" --format "{{.Names}}" | Select-String "amas-redis"
    if ($redisRunning) {
        docker start amas-redis 2>$null
        Write-Host "   ✅ Redis started" -ForegroundColor Green
    } else {
        docker run -d --name amas-redis `
            -p 6379:6379 `
            -v redis_data:/data `
            redis:7-alpine redis-server --appendonly yes --requirepass $RedisPassword 2>$null
        Write-Host "   ✅ Redis container created and started" -ForegroundColor Green
    }
    
    # Start Neo4j
    Write-Host "📦 Starting Neo4j..." -ForegroundColor Yellow
    $neo4jRunning = docker ps -a --filter "name=amas-neo4j" --format "{{.Names}}" | Select-String "amas-neo4j"
    if ($neo4jRunning) {
        docker start amas-neo4j 2>$null
        Write-Host "   ✅ Neo4j started" -ForegroundColor Green
    } else {
        docker run -d --name amas-neo4j `
            -p 7474:7474 `
            -p 7687:7687 `
            -e NEO4J_AUTH="neo4j/$Neo4jPassword" `
            -e NEO4J_PLUGINS='["apoc","graph-data-science"]' `
            -v neo4j_data:/data `
            -v neo4j_logs:/logs `
            neo4j:5 2>$null
        Write-Host "   ✅ Neo4j container created and started" -ForegroundColor Green
    }
    
    Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
} elseif ($UseDocker) {
    Write-Host "⚠️  Docker not found. Skipping Docker services." -ForegroundColor Yellow
    Write-Host "   Make sure PostgreSQL, Redis, and Neo4j are running manually.`n" -ForegroundColor Yellow
}

# Set environment variables
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql://postgres:$DatabasePassword@localhost:5432/amas"
}
if (-not $env:REDIS_URL) {
    $env:REDIS_URL = "redis://:$RedisPassword@localhost:6379/0"
}
if (-not $env:NEO4J_URI) {
    $env:NEO4J_URI = "bolt://localhost:7687"
}
if (-not $env:NEO4J_USER) {
    $env:NEO4J_USER = "neo4j"
}
if (-not $env:NEO4J_PASSWORD) {
    $env:NEO4J_PASSWORD = $Neo4jPassword
}

# Run migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Yellow
try {
    alembic upgrade head
    Write-Host "   ✅ Migrations completed" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Migration warning: $_" -ForegroundColor Yellow
}

# Start Backend
Write-Host "`n🚀 Starting Backend (Production Mode)..." -ForegroundColor Cyan
$backendScript = @"
cd '$ProjectRoot'
`$env:ENVIRONMENT='production'
`$env:DATABASE_URL='$env:DATABASE_URL'
`$env:REDIS_URL='$env:REDIS_URL'
`$env:NEO4J_URI='$env:NEO4J_URI'
`$env:NEO4J_USER='$env:NEO4J_USER'
`$env:NEO4J_PASSWORD='$env:NEO4J_PASSWORD'
Write-Host '🚀 AMAS Backend (Production)' -ForegroundColor Cyan
Write-Host 'Running on http://localhost:8000' -ForegroundColor Green
python -m uvicorn src.amas.api.main:app --host 0.0.0.0 --port 8000 --workers 4
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Start Frontend
Write-Host "🚀 Starting Frontend (Production Mode)..." -ForegroundColor Cyan
$frontendScript = @"
cd '$ProjectRoot\frontend'
Write-Host '🚀 AMAS Frontend (Production)' -ForegroundColor Cyan
Write-Host 'Building frontend...' -ForegroundColor Yellow
npm run build
Write-Host 'Starting preview server on http://localhost:3000' -ForegroundColor Green
npm run preview
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Wait a bit
Start-Sleep -Seconds 5

# Display summary
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ AMAS Production Mode Started!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "   Backend API:      http://localhost:8000" -ForegroundColor White
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend:         http://localhost:3000" -ForegroundColor White
Write-Host "   Neo4j Browser:    http://localhost:7474" -ForegroundColor White
Write-Host "   Health Check:     http://localhost:8000/health`n" -ForegroundColor White

Write-Host "📊 Services Status:" -ForegroundColor Cyan
Write-Host "   PostgreSQL: Running on port 5432" -ForegroundColor White
Write-Host "   Redis:      Running on port 6379" -ForegroundColor White
Write-Host "   Neo4j:      Running on ports 7474, 7687" -ForegroundColor White
Write-Host "   Backend:    Running on port 8000 (4 workers)" -ForegroundColor White
Write-Host "   Frontend:   Running on port 3000`n" -ForegroundColor White

Write-Host "🛑 To stop services:" -ForegroundColor Yellow
Write-Host "   - Close the PowerShell windows" -ForegroundColor White
if ($UseDocker) {
    Write-Host "   - Or run: docker stop amas-postgres amas-redis amas-neo4j`n" -ForegroundColor White
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

