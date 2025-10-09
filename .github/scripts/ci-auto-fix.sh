#!/bin/bash
set -e

echo "🤖 CI Auto-Fix Script"
echo "====================="

# Function to run command and show result
run_fix() {
    local cmd="$1"
    local description="$2"
    
    echo "🔧 $description"
    if eval "$cmd"; then
        echo "✅ $description - SUCCESS"
        return 0
    else
        echo "⚠️ $description - FAILED (continuing...)"
        return 1
    fi
}

# Step 1: Fix CI workflow dependencies
echo "🔧 Fixing CI workflow dependency issues..."

# Fix ci-cd.yml workflow
if [ -f ".github/workflows/ci-cd.yml" ]; then
    echo "📝 Updating ci-cd.yml workflow dependencies..."
    # Ensure all dependency installation steps include requirements-dev.txt
    sed -i 's/pip install -r requirements\.txt$/&\n        pip install -r requirements-dev.txt/g' .github/workflows/ci-cd.yml
    echo "✅ ci-cd.yml updated"
fi

# Fix ci.yml workflow
if [ -f ".github/workflows/ci.yml" ]; then
    echo "📝 Updating ci.yml workflow dependencies..."
    # Ensure all dependency installation steps include requirements-dev.txt
    sed -i 's/pip install -r requirements\.txt$/&\n        pip install -r requirements-dev.txt/g' .github/workflows/ci.yml
    echo "✅ ci.yml updated"
fi

# Step 2: Fix pytest configuration
if [ -f "pytest.ini" ]; then
    echo "📝 Fixing pytest configuration..."
    # Ensure pytest.ini has correct section header
    sed -i 's/\[tool:pytest\]/[pytest]/g' pytest.ini
    echo "✅ pytest configuration fixed"
fi

# Step 3: Fix code formatting
run_fix "python3 -m black src/ tests/" "Fixing code formatting with Black"

# Step 4: Fix import sorting
run_fix "python3 -m isort src/ tests/" "Fixing import sorting with isort"

# Step 5: Fix Black formatting again (isort might change formatting)
run_fix "python3 -m black src/ tests/" "Re-applying Black formatting after isort"

# Step 6: Verify fixes
echo "🔍 Verifying fixes..."
if python3 -m black --check src/ tests/; then
    echo "✅ Black formatting - PASS"
else
    echo "❌ Black formatting - FAIL"
fi

if python3 -m isort --check-only src/ tests/; then
    echo "✅ Import sorting - PASS"
else
    echo "❌ Import sorting - FAIL"
fi

echo "🎉 CI Auto-fix completed!"
