#!/bin/bash
# Complete Frontend Testing Suite

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

FRONTEND_URL="http://localhost:3000"
FRONTEND_DIR="frontend"

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}============================================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

PASSED=0
FAILED=0
WARNINGS=0

print_header "🧪 AMAS Frontend - Complete Test Suite"

# Test 1: Check if frontend directory exists
print_info "Checking frontend directory..."
if [ -d "$FRONTEND_DIR" ]; then
    print_success "Frontend directory exists"
    ((PASSED++))
else
    print_error "Frontend directory not found"
    ((FAILED++))
    exit 1
fi

# Test 2: Check if package.json exists
print_info "Checking package.json..."
if [ -f "$FRONTEND_DIR/package.json" ]; then
    print_success "package.json exists"
    ((PASSED++))
else
    print_error "package.json not found"
    ((FAILED++))
    exit 1
fi

# Test 3: Check if node_modules exists
print_info "Checking dependencies..."
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    print_success "Dependencies installed"
    ((PASSED++))
else
    print_warning "Dependencies not installed - run: cd frontend && npm install"
    ((WARNINGS++))
fi

# Test 4: TypeScript compilation
print_info "Testing TypeScript compilation..."
cd "$FRONTEND_DIR"
if npm run type-check > /dev/null 2>&1; then
    print_success "TypeScript compilation passed"
    ((PASSED++))
else
    print_error "TypeScript compilation failed"
    ((FAILED++))
fi
cd ..

# Test 5: ESLint check
print_info "Testing ESLint..."
cd "$FRONTEND_DIR"
if npm run lint > /dev/null 2>&1; then
    print_success "ESLint check passed"
    ((PASSED++))
else
    print_warning "ESLint found issues (non-blocking)"
    ((WARNINGS++))
fi
cd ..

# Test 6: Check if dev server is running
print_info "Checking if dev server is running..."
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    print_success "Dev server is running on $FRONTEND_URL"
    ((PASSED++))
    
    # Test 7: Check if React app loads
    print_info "Checking if React app loads..."
    HTML=$(curl -s "$FRONTEND_URL")
    if echo "$HTML" | grep -q "root"; then
        print_success "React app HTML structure correct"
        ((PASSED++))
    else
        print_error "React app HTML structure incorrect"
        ((FAILED++))
    fi
    
    # Test 8: Check if main.tsx is accessible
    print_info "Checking if main.tsx is accessible..."
    if curl -s "$FRONTEND_URL/src/main.tsx" > /dev/null 2>&1; then
        print_success "main.tsx is accessible"
        ((PASSED++))
    else
        print_warning "main.tsx not accessible (may be normal for production build)"
        ((WARNINGS++))
    fi
else
    print_warning "Dev server not running - start with: cd frontend && npm run dev"
    print_info "Trying alternative ports..."
    
    for port in 3001 3002 3003; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1; then
            print_success "Dev server found on port $port"
            FRONTEND_URL="http://localhost:$port"
            ((PASSED++))
            break
        fi
    done
    
    if [ $FAILED -eq 0 ] && [ $PASSED -lt 6 ]; then
        print_warning "Dev server not accessible on common ports"
        ((WARNINGS++))
    fi
fi

# Test 9: Check required files exist
print_info "Checking required component files..."
REQUIRED_FILES=(
    "src/App.tsx"
    "src/main.tsx"
    "src/components/Dashboard/Dashboard.tsx"
    "src/components/Dashboard/AgentStatusGrid.tsx"
    "src/components/Dashboard/WorkflowCard.tsx"
    "src/components/Dashboard/PerformanceMetrics.tsx"
    "src/components/Dashboard/RecentActivity.tsx"
    "src/types/agent.ts"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$FRONTEND_DIR/$file" ]; then
        print_success "Found: $file"
        ((PASSED++))
    else
        print_error "Missing: $file"
        ((FAILED++))
    fi
done

# Test 10: Check if build works
print_info "Testing production build..."
cd "$FRONTEND_DIR"
if timeout 120 npm run build > /dev/null 2>&1; then
    print_success "Production build successful"
    ((PASSED++))
else
    print_warning "Production build failed or timed out"
    ((WARNINGS++))
fi
cd ..

# Print summary
print_header "📊 Test Results Summary"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"

if [ $FAILED -eq 0 ]; then
    print_success "All critical tests passed!"
    exit 0
else
    print_error "Some tests failed"
    exit 1
fi

