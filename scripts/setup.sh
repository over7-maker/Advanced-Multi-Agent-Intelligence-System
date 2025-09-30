#!/bin/bash

# AMAS Setup Script
# This script sets up the development environment for AMAS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
        log_warning "Python version $PYTHON_VERSION detected. Python 3.11+ is recommended."
    fi
    
    log_success "Python $PYTHON_VERSION found"
}

check_node() {
    log_info "Checking Node.js installation..."
    
    if ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed. Web interface will not be available."
        return
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    log_success "Node.js $NODE_VERSION found"
}

install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    log_info "Installing Python requirements..."
    pip install -r requirements.txt
    
    # Install development requirements
    if [ -f "requirements-dev.txt" ]; then
        log_info "Installing development requirements..."
        pip install -r requirements-dev.txt
    fi
    
    log_success "Python dependencies installed"
}

install_web_deps() {
    if [ -d "web" ] && command -v npm &> /dev/null; then
        log_info "Installing web interface dependencies..."
        cd web
        npm install
        cd ..
        log_success "Web interface dependencies installed"
    else
        log_warning "Web interface dependencies not installed (Node.js not available)"
    fi
}

setup_directories() {
    log_info "Setting up directories..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p data/vectors
    mkdir -p data/models
    mkdir -p docker/nginx/ssl
    mkdir -p docker/prometheus/rules
    mkdir -p docker/grafana/dashboards
    mkdir -p docker/grafana/datasources
    
    log_success "Directories created"
}

setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# AMAS Environment Configuration
AMAS_ENVIRONMENT=development

# Database Configuration
POSTGRES_DB=amas
POSTGRES_USER=amas
POSTGRES_PASSWORD=amas_secure_password_123

# Redis Configuration
REDIS_PASSWORD=amas_redis_password_123

# Neo4j Configuration
NEO4J_AUTH=neo4j/amas_neo4j_password_123

# Security Configuration
JWT_SECRET=development_jwt_secret_change_in_production
ENCRYPTION_KEY=development_32_byte_key_change_in_production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Monitoring Configuration
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=amas_admin_password
EOF
        log_success "Environment file created"
    else
        log_info "Environment file already exists"
    fi
}

setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for AMAS

echo "Running pre-commit checks..."

# Run linting
if [ -f "requirements-dev.txt" ]; then
    source venv/bin/activate
    python -m flake8 src/ --max-line-length=100
    python -m black --check src/
fi

echo "Pre-commit checks passed"
EOF
    
    chmod +x .git/hooks/pre-commit
    log_success "Git hooks configured"
}

run_tests() {
    log_info "Running tests..."
    
    if [ -f "requirements-test.txt" ]; then
        source venv/bin/activate
        python -m pytest tests/ -v --tb=short
        log_success "Tests passed"
    else
        log_warning "Test requirements not found, skipping tests"
    fi
}

show_next_steps() {
    log_info "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Start the development services: ./scripts/deploy.sh development start"
    echo "3. Run the API server: python -m uvicorn src.amas.api.main:app --reload"
    echo "4. Access the web interface: http://localhost:3000 (if Node.js is installed)"
    echo "5. Access the API documentation: http://localhost:8000/docs"
    echo ""
    echo "For production deployment:"
    echo "1. Update the .env file with production values"
    echo "2. Run: ./scripts/deploy.sh production deploy"
    echo ""
    echo "For more information, see the README.md file"
}

# Main script
main() {
    log_info "Setting up AMAS development environment..."
    
    check_python
    check_node
    setup_directories
    setup_environment
    install_python_deps
    install_web_deps
    setup_git_hooks
    
    # Run tests if requested
    if [ "$1" = "--test" ]; then
        run_tests
    fi
    
    show_next_steps
}

# Run main function
main "$@"