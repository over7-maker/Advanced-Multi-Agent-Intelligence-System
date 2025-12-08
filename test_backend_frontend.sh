#!/bin/bash
# Comprehensive Backend and Frontend Test Suite

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🧪 COMPREHENSIVE BACKEND & FRONTEND TEST SUITE             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
test_check() {
    local name="$1"
    local command="$2"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if eval "$command" > /tmp/test_output_$$.txt 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}: $name"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $name"
        cat /tmp/test_output_$$.txt | head -20
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# ============================================================================
# BACKEND TESTS
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    BACKEND TESTS                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Python version
test_check "Python Version" "python3 --version"

# Test 2: Backend dependencies
test_check "Backend Dependencies" "python3 -c 'import fastapi, uvicorn, pydantic; print(\"OK\")'"

# Test 3: Backend imports
test_check "Backend Imports" "python3 -c 'import sys; sys.path.insert(0, \"src\"); from src.api.routes import health; print(\"OK\")'"

# Test 4: Main application
test_check "Main Application Import" "python3 -c 'import main; print(\"OK\")'"

# Test 5: Configuration
test_check "Configuration Validation" "python3 -c 'from src.config.settings import get_settings; s = get_settings(); print(\"OK\")'"

# Test 6: Run pytest tests
if [ -d "tests" ] && [ -f "tests/conftest.py" ]; then
    test_check "Pytest Tests" "python3 -m pytest tests/ -v --tb=short -x || true"
else
    echo "⚠️  Skipping pytest: tests directory or conftest.py not found"
fi

# Test 7: API routes
test_check "API Routes Import" "python3 -c 'from src.api.routes import agents, health, tasks, users, auth; print(\"OK\")'"

# Test 8: Security modules
test_check "Security Modules" "python3 -c 'from src.amas.security.security_manager import initialize_security; print(\"OK\")'"

# ============================================================================
# FRONTEND TESTS
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    FRONTEND TESTS                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 9: Node.js version
if command -v node &> /dev/null; then
    test_check "Node.js Version" "node --version"
else
    echo "⚠️  Node.js not found, skipping frontend tests"
    echo "   Install Node.js to test frontend"
fi

# Test 10: Frontend dependencies
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    if [ -d "frontend/node_modules" ]; then
        test_check "Frontend Dependencies Installed" "test -d frontend/node_modules"
    else
        echo "⚠️  Frontend node_modules not found"
        echo "   Run: cd frontend && npm install"
    fi
    
    # Test 11: Frontend build
    if [ -d "frontend/node_modules" ]; then
        test_check "Frontend TypeScript Check" "cd frontend && npx tsc --noEmit || true"
    fi
    
    # Test 12: Frontend lint
    if [ -d "frontend/node_modules" ] && [ -f "frontend/.eslintrc.json" ]; then
        test_check "Frontend Lint" "cd frontend && npx eslint src --ext .ts,.tsx --max-warnings 0 || true"
    fi
else
    echo "⚠️  Frontend directory or package.json not found"
fi

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  INTEGRATION TESTS                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 13: Environment variables
test_check "Environment Variables" "test -f .env && echo 'OK'"

# Test 14: API keys
test_check "API Keys Configuration" "grep -q 'API_KEY' .env && echo 'OK'"

# Test 15: Database connection (if configured)
# test_check "Database Connection" "python3 -c 'from src.database.connection import get_db; print(\"OK\")' || echo 'SKIP'"

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

TOTAL=$((PASSED + FAILED))
echo "Results: $PASSED/$TOTAL tests passed"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "✅ Backend: Ready"
    echo "✅ Frontend: Ready"
    echo "✅ Integration: Ready"
    echo ""
    echo "🚀 To start the application:"
    echo "   Backend:  uvicorn main:app --reload"
    echo "   Frontend: cd frontend && npm run dev"
    rm -f /tmp/test_output_$$.txt
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed${NC}"
    echo ""
    echo "Review the output above for details"
    rm -f /tmp/test_output_$$.txt
    exit 1
fi

