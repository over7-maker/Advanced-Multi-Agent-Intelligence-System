#!/bin/bash
# Frontend Setup Verification Script

echo "🔍 Verifying Frontend Setup..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js >=18.17.0 <20.0.0"
    echo "   Visit: https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ] || [ "$NODE_VERSION" -ge 20 ]; then
        echo "⚠️  Node.js version $(node --version) may not be compatible"
        echo "   Recommended: >=18.17.0 <20.0.0"
    else
        echo "✅ Node.js $(node --version) is installed"
    fi
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
else
    echo "✅ npm $(npm --version) is installed"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Dependencies not installed"
    echo "   Run: npm install"
    exit 1
else
    echo "✅ Dependencies installed"
fi

# Check required files
REQUIRED_FILES=(
    "package.json"
    "vite.config.ts"
    "index.html"
    "src/main.tsx"
    "src/App.tsx"
    "tsconfig.json"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "✅ All required files present"
else
    echo "❌ $MISSING_FILES required file(s) missing"
    exit 1
fi

# Type check
echo ""
echo "🔍 Running TypeScript type check..."
if npm run type-check 2>&1 | grep -q "error"; then
    echo "❌ TypeScript errors found"
    npm run type-check
    exit 1
else
    echo "✅ No TypeScript errors"
fi

echo ""
echo "✅ Frontend setup is complete and verified!"
echo ""
echo "🚀 Ready to start development server:"
echo "   npm run dev"

