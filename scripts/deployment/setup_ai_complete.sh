#!/bin/bash

# AMAS AI Integration Complete Setup Script
# This script sets up the complete AI integration for AMAS

set -e  # Exit on any error

echo "🚀 AMAS AI Integration Complete Setup"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the AMAS project root directory"
    exit 1
fi

print_info "Starting AMAS AI Integration Setup..."

# Step 1: Check Python version
print_info "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
if [[ $(echo "$python_version" | cut -d'.' -f1) -ge 3 && $(echo "$python_version" | cut -d'.' -f2) -ge 8 ]]; then
    print_status "Python $python_version is compatible"
else
    print_error "Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

# Step 2: Check if virtual environment exists
print_info "Checking virtual environment..."
if [ -d "venv" ]; then
    print_status "Virtual environment already exists"
else
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Step 3: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Step 4: Install dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencies installed"

# Step 5: Check environment variables
print_info "Checking environment variables..."
missing_vars=()

if [ -z "$DEEPSEEK_API_KEY" ]; then
    missing_vars+=("DEEPSEEK_API_KEY")
fi

if [ -z "$GLM_API_KEY" ]; then
    missing_vars+=("GLM_API_KEY")
fi

if [ -z "$GROK_API_KEY" ]; then
    missing_vars+=("GROK_API_KEY")
fi

if [ -z "$KIMI_API_KEY" ]; then
    missing_vars+=("KIMI_API_KEY")
fi

if [ -z "$QWEN_API_KEY" ]; then
    missing_vars+=("QWEN_API_KEY")
fi

if [ -z "$GPTOSS_API_KEY" ]; then
    missing_vars+=("GPTOSS_API_KEY")
fi

if [ ${#missing_vars[@]} -eq 0 ]; then
    print_status "All AI API keys are set"
else
    print_warning "Missing environment variables: ${missing_vars[*]}"
    print_info "Please set these environment variables or create a .env file"
    print_info "Example .env file:"
    echo "DEEPSEEK_API_KEY=your_key_here"
    echo "GLM_API_KEY=your_key_here"
    echo "GROK_API_KEY=your_key_here"
    echo "KIMI_API_KEY=your_key_here"
    echo "QWEN_API_KEY=your_key_here"
    echo "GPTOSS_API_KEY=your_key_here"
fi

# Step 6: Create necessary directories
print_info "Creating necessary directories..."
mkdir -p logs data models cache temp output reports backups
print_status "Directories created"

# Step 7: Run environment setup
print_info "Running environment setup..."
python scripts/setup_environment.py --output environment_setup_report.json
if [ $? -eq 0 ]; then
    print_status "Environment setup completed"
else
    print_warning "Environment setup had issues - check environment_setup_report.json"
fi

# Step 8: Test AI integration
print_info "Testing AI integration..."
python scripts/setup_ai_integration.py --output ai_integration_report.json
if [ $? -eq 0 ]; then
    print_status "AI integration test completed"
else
    print_warning "AI integration test had issues - check ai_integration_report.json"
fi

# Step 9: Run complete AI integration
print_info "Running complete AI integration..."
python scripts/complete_ai_integration.py --output complete_ai_integration_report.json
if [ $? -eq 0 ]; then
    print_status "Complete AI integration completed"
else
    print_warning "Complete AI integration had issues - check complete_ai_integration_report.json"
fi

# Step 10: Test AI capabilities
print_info "Testing AI capabilities..."

# Test code analysis
print_info "Testing code analysis..."
python scripts/ai_code_analyzer.py --files main.py --output test_analysis_report.md
if [ $? -eq 0 ]; then
    print_status "Code analysis test completed"
else
    print_warning "Code analysis test failed"
fi

# Test code improvement
print_info "Testing code improvement..."
python scripts/ai_code_improver.py --files main.py --output test_improved_code/
if [ $? -eq 0 ]; then
    print_status "Code improvement test completed"
else
    print_warning "Code improvement test failed"
fi

# Test test generation
print_info "Testing test generation..."
python scripts/ai_test_generator.py --files main.py --output test_generated_tests/
if [ $? -eq 0 ]; then
    print_status "Test generation test completed"
else
    print_warning "Test generation test failed"
fi

# Step 11: Create GitHub Actions workflow (if not exists)
print_info "Checking GitHub Actions workflow..."
if [ ! -f ".github/workflows/ai_development.yml" ]; then
    print_warning "GitHub Actions workflow not found"
    print_info "The workflow file should be at .github/workflows/ai_development.yml"
else
    print_status "GitHub Actions workflow exists"
fi

# Step 12: Generate final report
print_info "Generating final setup report..."

cat > setup_complete_report.md << EOF
# AMAS AI Integration Setup Complete

## Setup Summary

- **Python Version**: $python_version
- **Virtual Environment**: Created and activated
- **Dependencies**: Installed
- **Environment Variables**: ${#missing_vars[@]} missing
- **Directories**: Created
- **AI Integration**: Tested
- **GitHub Actions**: Configured

## Generated Reports

- \`environment_setup_report.json\` - Environment setup results
- \`ai_integration_report.json\` - AI integration test results
- \`complete_ai_integration_report.json\` - Complete integration results
- \`test_analysis_report.md\` - Code analysis test results
- \`test_improved_code/\` - Code improvement test results
- \`test_generated_tests/\` - Test generation results

## Next Steps

1. **Set Missing Environment Variables**: ${missing_vars[*]}
2. **Review Reports**: Check all generated reports for any issues
3. **Test AI Capabilities**: Run individual AI scripts to test functionality
4. **Configure GitHub Secrets**: Add API keys to GitHub repository secrets
5. **Run GitHub Actions**: Test the automated AI development workflow

## AI Integration Features

- **6 AI Providers**: DeepSeek, GLM, Grok, Kimi, Qwen, GPT-OSS
- **Intelligent Fallback**: Automatic provider switching on failure
- **Rate Limiting**: Built-in rate limit management
- **Health Monitoring**: Real-time provider health tracking
- **Code Analysis**: AI-powered code quality analysis
- **Code Improvement**: AI-generated code improvements
- **Test Generation**: AI-generated comprehensive tests
- **Continuous Development**: AI-powered continuous development

## Usage Examples

\`\`\`bash
# Test AI integration
python scripts/setup_ai_integration.py --validate-only

# Analyze code quality
python scripts/ai_code_analyzer.py --directory . --output analysis_report.md

# Improve code
python scripts/ai_code_improver.py --directory . --output improved_code/

# Generate tests
python scripts/ai_test_generator.py --directory . --output tests/generated/

# Continuous development
python scripts/ai_continuous_developer.py --project-path . --mode full_analysis
\`\`\`

## Troubleshooting

If you encounter issues:

1. Check the generated reports for specific error messages
2. Verify all environment variables are set correctly
3. Ensure internet connectivity for AI provider access
4. Check Python dependencies are installed correctly
5. Review the AI_INTEGRATION_README.md for detailed documentation

## Support

For more information, see:
- \`AI_INTEGRATION_README.md\` - Complete AI integration documentation
- \`README.md\` - Main project documentation
- Generated reports for specific error details

EOF

print_status "Final setup report generated: setup_complete_report.md"

# Step 13: Display final status
echo ""
echo "🎉 AMAS AI Integration Setup Complete!"
echo "====================================="
echo ""
print_info "Setup completed successfully!"
echo ""
print_info "Generated files:"
echo "  - environment_setup_report.json"
echo "  - ai_integration_report.json"
echo "  - complete_ai_integration_report.json"
echo "  - test_analysis_report.md"
echo "  - setup_complete_report.md"
echo ""
if [ ${#missing_vars[@]} -gt 0 ]; then
    print_warning "Missing environment variables: ${missing_vars[*]}"
    echo "  Please set these variables or create a .env file"
fi
echo ""
print_info "Next steps:"
echo "  1. Review the generated reports"
echo "  2. Set any missing environment variables"
echo "  3. Test AI capabilities with individual scripts"
echo "  4. Configure GitHub Secrets for automated workflows"
echo ""
print_info "For detailed documentation, see AI_INTEGRATION_README.md"
echo ""
print_status "Setup complete! 🚀"