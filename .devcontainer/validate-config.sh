#!/bin/bash
# Validation script for AMAS devcontainer configuration
# Checks if all configuration files are valid and ready for container startup

set -e

echo "🔍 Validating AMAS Devcontainer Configuration..."
echo ""

ERRORS=0
WARNINGS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in the right directory
if [ ! -d ".devcontainer" ]; then
    echo -e "${RED}❌ Error: .devcontainer directory not found${NC}"
    echo "   Please run this script from the project root directory"
    exit 1
fi

cd .devcontainer || exit 1

# 1. Validate devcontainer.json
echo "📋 Checking devcontainer.json..."
if [ -f "devcontainer.json" ]; then
    if command_exists python3; then
        if python3 -c "import json; json.load(open('devcontainer.json'))" 2>/dev/null; then
            echo -e "${GREEN}   ✅ devcontainer.json is valid JSON${NC}"
            # Check for required fields
            if python3 -c "import json; d=json.load(open('devcontainer.json')); assert 'dockerComposeFile' in d or 'build' in d, 'Missing dockerComposeFile or build'; print('   ✅ Contains dockerComposeFile or build')" 2>/dev/null; then
                echo -e "${GREEN}   ✅ Contains required configuration${NC}"
            else
                echo -e "${RED}   ❌ Missing dockerComposeFile or build configuration${NC}"
                ((ERRORS++))
            fi
        else
            echo -e "${RED}   ❌ devcontainer.json has invalid JSON syntax${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "${YELLOW}   ⚠️  Python3 not available, skipping JSON validation${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}   ❌ devcontainer.json not found${NC}"
    ((ERRORS++))
fi

# 2. Validate docker-compose.yml
echo ""
echo "🐳 Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    if command_exists python3; then
        if python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" 2>/dev/null; then
            echo -e "${GREEN}   ✅ docker-compose.yml is valid YAML${NC}"
            # Check for version
            if grep -q "^version:" docker-compose.yml; then
                echo -e "${GREEN}   ✅ Contains version field${NC}"
            else
                echo -e "${YELLOW}   ⚠️  Missing version field (recommended but not required)${NC}"
                ((WARNINGS++))
            fi
        else
            echo -e "${RED}   ❌ docker-compose.yml has invalid YAML syntax${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "${YELLOW}   ⚠️  Python3 not available, skipping YAML validation${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}   ❌ docker-compose.yml not found${NC}"
    ((ERRORS++))
fi

# 3. Check Dockerfile
echo ""
echo "🐋 Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}   ✅ Dockerfile exists${NC}"
    if [ -r "Dockerfile" ]; then
        echo -e "${GREEN}   ✅ Dockerfile is readable${NC}"
    else
        echo -e "${RED}   ❌ Dockerfile is not readable${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${RED}   ❌ Dockerfile not found${NC}"
    ((ERRORS++))
fi

# 4. Check post-create script
echo ""
echo "📜 Checking post-create.sh..."
if [ -f "post-create.sh" ]; then
    echo -e "${GREEN}   ✅ post-create.sh exists${NC}"
    if [ -x "post-create.sh" ]; then
        echo -e "${GREEN}   ✅ post-create.sh is executable${NC}"
    else
        echo -e "${YELLOW}   ⚠️  post-create.sh is not executable, fixing...${NC}"
        chmod +x post-create.sh
        echo -e "${GREEN}   ✅ Fixed permissions${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}   ⚠️  post-create.sh not found (optional)${NC}"
    ((WARNINGS++))
fi

# 5. Check Docker availability (skip if inside container)
echo ""
echo "🐳 Checking Docker..."
# Check if we're inside a container
if [ -f /.dockerenv ] || [ -n "${DEVCONTAINER}" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo -e "${GREEN}   ✅ Running inside container (Docker check skipped)${NC}"
    echo "      Docker is not needed inside the container"
    INSIDE_CONTAINER=true
elif command_exists docker; then
    echo -e "${GREEN}   ✅ Docker command available${NC}"
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Docker daemon is running${NC}"
    else
        echo -e "${RED}   ❌ Docker daemon is not running${NC}"
        echo "      Please start Docker Desktop or Docker daemon"
        ((ERRORS++))
    fi
else
    echo -e "${RED}   ❌ Docker command not found${NC}"
    echo "      Please install Docker"
    ((ERRORS++))
fi

# 6. Check docker-compose availability (skip if inside container)
echo ""
echo "🐙 Checking docker-compose..."
if [ "${INSIDE_CONTAINER:-false}" = "true" ]; then
    echo -e "${GREEN}   ✅ Running inside container (docker-compose check skipped)${NC}"
    echo "      docker-compose is not needed inside the container"
elif command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    echo -e "${GREEN}   ✅ docker-compose available${NC}"
else
    echo -e "${YELLOW}   ⚠️  docker-compose not found (VS Code/Cursor will handle this)${NC}"
    ((WARNINGS++))
fi

# 7. Check port availability (skip if inside container - ports are already forwarded)
echo ""
echo "🔌 Checking ports..."
if [ "${INSIDE_CONTAINER:-false}" = "true" ]; then
    echo -e "${GREEN}   ✅ Running inside container${NC}"
    echo "      Ports are managed by docker-compose and VS Code/Cursor"
    echo "      Checking if services can bind to ports inside container..."
    # Check if ports are available inside container (for services running in container)
    for port in 8000 8080 3000; do
        if command_exists netstat && netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo -e "${YELLOW}   ⚠️  Port $port is in use inside container${NC}"
        else
            echo -e "${GREEN}   ✅ Port $port is available inside container${NC}"
        fi
    done
else
    check_port() {
        local port=$1
        local name=$2
        if command_exists lsof; then
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo -e "${YELLOW}   ⚠️  Port $port ($name) is in use${NC}"
                echo "      Consider setting ${name}_PORT environment variable"
                ((WARNINGS++))
            else
                echo -e "${GREEN}   ✅ Port $port ($name) is available${NC}"
            fi
        elif command_exists netstat; then
            if netstat -ano 2>/dev/null | grep -q ":$port "; then
                echo -e "${YELLOW}   ⚠️  Port $port ($name) is in use${NC}"
                ((WARNINGS++))
            else
                echo -e "${GREEN}   ✅ Port $port ($name) is available${NC}"
            fi
        else
            echo -e "${YELLOW}   ⚠️  Cannot check port $port (no port checking tool)${NC}"
            ((WARNINGS++))
        fi
    }
    
    check_port 8000 "BACKEND"
    check_port 8080 "DASHBOARD"
    check_port 3000 "FRONTEND"
fi

# 8. Check environment variables
echo ""
echo "🌍 Checking environment variables..."
if [ -n "$BACKEND_PORT" ] || [ -n "$DASHBOARD_PORT" ] || [ -n "$FRONTEND_PORT" ]; then
    echo -e "${GREEN}   ✅ Custom port configuration detected:${NC}"
    [ -n "$BACKEND_PORT" ] && echo "      BACKEND_PORT=$BACKEND_PORT"
    [ -n "$DASHBOARD_PORT" ] && echo "      DASHBOARD_PORT=$DASHBOARD_PORT"
    [ -n "$FRONTEND_PORT" ] && echo "      FRONTEND_PORT=$FRONTEND_PORT"
else
    echo -e "${GREEN}   ✅ Using default ports (8000, 8080, 3000)${NC}"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Validation Summary:"
echo ""

if [ "${INSIDE_CONTAINER:-false}" = "true" ]; then
    echo ""
    echo -e "${GREEN}✅ Container configuration is valid!${NC}"
    echo ""
    echo "📦 You're already inside the AMAS development container!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Verify Python is working: python --version"
    echo "   2. Install dependencies: pip install -r requirements.txt"
    echo "   3. Start the backend: python -m uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "💡 Tip: Run this script from the host machine to check Docker and port availability"
    exit 0
elif [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Configuration is ready.${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Open this folder in VS Code or Cursor"
    echo "   2. When prompted, click 'Reopen in Container'"
    echo "   3. Or use Command Palette: 'Dev Containers: Reopen in Container'"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Configuration has $WARNINGS warning(s) but should work${NC}"
    echo ""
    echo "🚀 You can proceed, but review the warnings above."
    exit 0
else
    echo -e "${RED}❌ Configuration has $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors before starting the container."
    exit 1
fi

