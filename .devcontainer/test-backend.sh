#!/bin/bash
# Diagnostic script to test if AMAS backend can start
# Tests imports, configuration, and startup

# Don't exit on error - we want to show all diagnostics
set +e

echo "🔍 AMAS Backend Diagnostic Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Check Python version
echo "1️⃣  Testing Python version..."
PYTHON_VERSION=$(python --version 2>&1)
echo "   $PYTHON_VERSION"
if python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo -e "   ${GREEN}✅ Python version is compatible${NC}"
else
    echo -e "   ${YELLOW}⚠️  Python 3.11+ recommended${NC}"
    ((WARNINGS++))
fi

# Test 2: Check if main.py exists
echo ""
echo "2️⃣  Checking application entry points..."
if [ -f "main.py" ]; then
    echo -e "   ${GREEN}✅ main.py found (root level)${NC}"
    MAIN_FILE="main.py"
elif [ -f "src/amas/api/main.py" ]; then
    echo -e "   ${GREEN}✅ src/amas/api/main.py found${NC}"
    MAIN_FILE="src.amas.api.main"
else
    echo -e "   ${RED}❌ No main.py found${NC}"
    echo "      Expected: main.py or src/amas/api/main.py"
    ((ERRORS++))
    exit 1
fi

# Test 3: Test importing main application
echo ""
echo "3️⃣  Testing application imports..."
if [ "$MAIN_FILE" = "main.py" ]; then
    if python -c "import main; print('✅ main module imported')" 2>&1; then
        echo -e "   ${GREEN}✅ main.py imports successfully${NC}"
        # Check if app exists
        if python -c "import main; assert hasattr(main, 'app'), 'No app found'; print('✅ FastAPI app found')" 2>&1; then
            echo -e "   ${GREEN}✅ FastAPI app object found${NC}"
        else
            echo -e "   ${RED}❌ FastAPI app not found in main.py${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "   ${RED}❌ Failed to import main.py${NC}"
        echo "      Error details:"
        python -c "import main" 2>&1 | head -10 | sed 's/^/      /'
        ((ERRORS++))
    fi
else
    if python -c "from src.amas.api import main; print('✅ src.amas.api.main imported')" 2>&1; then
        echo -e "   ${GREEN}✅ src/amas/api/main.py imports successfully${NC}"
        if python -c "from src.amas.api.main import app; print('✅ FastAPI app found')" 2>&1; then
            echo -e "   ${GREEN}✅ FastAPI app object found${NC}"
        else
            echo -e "   ${RED}❌ FastAPI app not found${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "   ${RED}❌ Failed to import src/amas/api/main.py${NC}"
        echo "      Error details:"
        python -c "from src.amas.api import main" 2>&1 | head -10 | sed 's/^/      /'
        ((ERRORS++))
    fi
fi

# Test 4: Check required dependencies
echo ""
echo "4️⃣  Checking critical dependencies..."
REQUIRED_PACKAGES=("fastapi" "uvicorn" "pydantic" "pydantic-settings")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import ${package//-/_}" 2>/dev/null; then
        VERSION=$(python -c "import ${package//-/_}; print(${package//-/_}.__version__)" 2>/dev/null || echo "unknown")
        echo -e "   ${GREEN}✅ ${package} (${VERSION})${NC}"
    else
        echo -e "   ${RED}❌ ${package} not installed${NC}"
        ((ERRORS++))
    fi
done

# Test 5: Check configuration
echo ""
echo "5️⃣  Checking configuration..."
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✅ .env file exists${NC}"
else
    echo -e "   ${YELLOW}⚠️  .env file not found (optional)${NC}"
    ((WARNINGS++))
fi

# Test 6: Test uvicorn can start (dry run)
echo ""
echo "6️⃣  Testing uvicorn startup (dry run)..."
if command -v uvicorn >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ uvicorn command available${NC}"
    
    # Try to get app info without starting server
    if [ "$MAIN_FILE" = "main.py" ]; then
        if timeout 5 python -c "
import uvicorn
from main import app
print('✅ App can be loaded by uvicorn')
" 2>&1; then
            echo -e "   ${GREEN}✅ Application can be loaded${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Application load test had issues (may still work)${NC}"
            ((WARNINGS++))
        fi
    else
        if timeout 5 python -c "
import uvicorn
from src.amas.api.main import app
print('✅ App can be loaded by uvicorn')
" 2>&1; then
            echo -e "   ${GREEN}✅ Application can be loaded${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Application load test had issues (may still work)${NC}"
            ((WARNINGS++))
        fi
    fi
else
    echo -e "   ${RED}❌ uvicorn command not found${NC}"
    ((ERRORS++))
fi

# Test 7: Check port availability
echo ""
echo "7️⃣  Checking port 8000..."
if command -v netstat >/dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
        echo -e "   ${YELLOW}⚠️  Port 8000 is in use${NC}"
        echo "      You may need to use a different port or stop the existing service"
        ((WARNINGS++))
    else
        echo -e "   ${GREEN}✅ Port 8000 is available${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Cannot check port (netstat not available)${NC}"
    ((WARNINGS++))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Diagnostic Summary:"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! Backend should start successfully.${NC}"
    echo ""
    echo "🚀 To start the backend:"
    if [ "$MAIN_FILE" = "main.py" ]; then
        echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    else
        echo "   uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000"
    fi
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Tests passed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "🚀 You can try starting the backend:"
    if [ "$MAIN_FILE" = "main.py" ]; then
        echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    else
        echo "   uvicorn src.amas.api.main:app --reload --host 0.0.0.0 --port 8000"
    fi
    exit 0
else
    echo -e "${RED}❌ Tests failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before starting the backend."
    exit 1
fi

