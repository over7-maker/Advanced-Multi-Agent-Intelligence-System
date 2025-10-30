#!/bin/bash
# Auto-formatting script to fix CI Black formatting failures
# Resolves: "37 files would be reformatted, 1 file would fail to reformat"

set -e  # Exit on any error

echo "🔧 AMAS Auto-Formatting Script - Fixing CI Black Failures"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
    print_error "Not in project root directory. Please run from AMAS root."
    exit 1
fi

print_status "Starting code formatting process..."

# Install formatting tools if not available
print_status "Ensuring formatting tools are available..."
if ! command -v black &> /dev/null; then
    print_status "Installing Black..."
    pip install --user black==23.11.0
fi

if ! command -v isort &> /dev/null; then
    print_status "Installing isort..."
    pip install --user isort==5.12.0
fi

if ! command -v autopep8 &> /dev/null; then
    print_status "Installing autopep8..."
    pip install --user autopep8==2.0.4
fi

# Create backup directory
BACKUP_DIR=".formatting-backup-$(date +%Y%m%d-%H%M%S)"
print_status "Creating backup in $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"

# Find all Python files and create backups
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" -not -path "./dist/*" -not -path "./.tox/*" -not -path "./.pytest_cache/*" -not -path "./htmlcov/*" | while read -r file; do
    if [ -f "$file" ]; then
        # Create directory structure in backup
        backup_file="$BACKUP_DIR/$file"
        mkdir -p "$(dirname "$backup_file")"
        cp "$file" "$backup_file"
    fi
done

print_success "Backup created successfully"

# Step 1: Fix import sorting with isort
print_status "Step 1: Fixing import sorting with isort..."
if isort . --check-only --diff --quiet; then
    print_success "Import sorting is already correct"
else
    print_warning "Fixing import sorting issues..."
    isort . --profile black --line-length 88 --multi-line 3 --trailing-comma --force-grid-wrap 0 --use-parentheses --ensure-newline-before-comments
    print_success "Import sorting fixed"
fi

# Step 2: Fix basic PEP 8 issues with autopep8
print_status "Step 2: Fixing basic PEP 8 issues with autopep8..."
autopep8 --in-place --recursive --aggressive --aggressive \
    --exclude="venv,.venv,build,dist,.tox,.pytest_cache,htmlcov" \
    --max-line-length=88 .

print_success "Basic PEP 8 issues fixed"

# Step 3: Apply Black formatting
print_status "Step 3: Applying Black formatting..."
if black --check --quiet . 2>/dev/null; then
    print_success "Black formatting is already correct"
else
    print_warning "Applying Black formatting..."
    black . --line-length 88 --target-version py311 \
        --exclude="/(venv|\.venv|build|dist|\.tox|\.pytest_cache|htmlcov)/"
    
    if [ $? -eq 0 ]; then
        print_success "Black formatting applied successfully"
    else
        print_error "Black formatting encountered issues"
        print_status "Trying to fix individual files..."
        
        # Find files that Black cannot format and try to fix them
        find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./build/*" -not -path "./dist/*" | while read -r file; do
            if [ -f "$file" ]; then
                if ! black --check "$file" 2>/dev/null; then
                    print_warning "Fixing problematic file: $file"
                    # Try to fix syntax errors that prevent Black from running
                    
                    # Common fixes for files that fail Black formatting
                    # Fix unclosed strings, brackets, etc.
                    python3 -c "
import ast
import sys
try:
    with open('$file', 'r', encoding='utf-8') as f:
        content = f.read()
    ast.parse(content)
    print('File is syntactically correct')
except SyntaxError as e:
    print(f'Syntax error in $file: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Error checking $file: {e}')
    sys.exit(1)
" || {
                        print_error "File $file has syntax errors - skipping"
                        continue
                    }
                    
                    # Try to format the file
                    black "$file" 2>/dev/null || print_warning "Could not format $file"
                fi
            fi
        done
    fi
fi

# Step 4: Verify formatting
print_status "Step 4: Verifying formatting..."

# Check Black
print_status "Checking Black formatting..."
if black --check --diff . 2>/dev/null; then
    print_success "✅ Black formatting verification passed"
else
    print_warning "Some files still have Black formatting issues"
    black --check --diff . || true
fi

# Check isort
print_status "Checking import sorting..."
if isort . --check-only --diff --quiet; then
    print_success "✅ Import sorting verification passed"
else
    print_warning "Some files still have import sorting issues"
    isort . --check-only --diff || true
fi

# Step 5: Run additional fixes for common issues
print_status "Step 5: Running additional fixes..."

# Fix trailing whitespace
print_status "Removing trailing whitespace..."
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec sed -i 's/[[:space:]]*$//' {} \;

# Fix file endings
print_status "Ensuring proper file endings..."
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec sed -i -e '$a\' {} \;

# Step 6: Final verification
print_status "Step 6: Final verification..."

# Count files that would be reformatted
FILES_TO_FORMAT=$(black --check . 2>&1 | grep -c "would reformat" || echo "0")
FILES_FAILED=$(black --check . 2>&1 | grep -c "would fail to reformat" || echo "0")

if [ "$FILES_TO_FORMAT" -eq 0 ] && [ "$FILES_FAILED" -eq 0 ]; then
    print_success "🎉 All files are properly formatted!"
    print_success "CI Black formatting check should now pass"
    
    # Clean up backup if everything is successful
    read -p "Delete backup directory $BACKUP_DIR? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$BACKUP_DIR"
        print_success "Backup directory cleaned up"
    else
        print_status "Backup directory kept at $BACKUP_DIR"
    fi
else
    print_warning "Still have formatting issues:"
    if [ "$FILES_TO_FORMAT" -gt 0 ]; then
        print_warning "- $FILES_TO_FORMAT files would be reformatted"
    fi
    if [ "$FILES_FAILED" -gt 0 ]; then
        print_error "- $FILES_FAILED files would fail to reformat (syntax errors)"
        print_status "Files with syntax errors need manual review:"
        black --check . 2>&1 | grep "error:" || true
    fi
    print_status "Backup directory kept at $BACKUP_DIR"
fi

# Step 7: Show summary
echo
echo "==========================================================="
print_status "AMAS Code Formatting Summary"
echo "==========================================================="
print_status "Backup location: $BACKUP_DIR"
print_status "Tools used: Black, isort, autopep8"
print_status "Target line length: 88 characters"
print_status "Python target version: 3.11"

if [ "$FILES_TO_FORMAT" -eq 0 ] && [ "$FILES_FAILED" -eq 0 ]; then
    print_success "✅ Code formatting completed successfully!"
    print_success "Your CI pipeline should now pass the Black formatting checks"
else
    print_warning "⚠️  Some issues remain - check the output above"
    print_status "You may need to manually review files with syntax errors"
fi

echo "==========================================================="
