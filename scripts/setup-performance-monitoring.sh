#!/bin/bash
# AMAS Performance Monitoring Setup Script

set -e

echo "🔍 Setting up AMAS Performance Monitoring System..."
echo "=================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Install Python dependencies
echo "📦 Installing performance monitoring dependencies..."
pip install psutil aioredis matplotlib seaborn aiohttp locust

# Install Redis if not available
if ! command -v redis-server &> /dev/null; then
    echo "📥 Redis not found. Installing Redis..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y redis-server
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install redis
    fi
fi

# Start Redis service
echo "🚀 Starting Redis service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start redis
fi

# Create monitoring directories
echo "📁 Creating monitoring directories..."
mkdir -p logs/performance
mkdir -p data/metrics
mkdir -p reports/load-tests

# Create monitoring configuration
echo "⚙️ Creating monitoring configuration..."
cat > config/monitoring.json << EOF
{
    "monitoring": {
        "enabled": true,
        "interval_seconds": 60,
        "redis_url": "redis://localhost:6379",
        "alert_thresholds": {
            "cpu_warning": 70,
            "cpu_critical": 90,
            "memory_warning": 80,
            "memory_critical": 95,
            "response_time_warning": 3.0,
            "response_time_critical": 8.0
        },
        "data_retention_hours": 168
    },
    "load_testing": {
        "base_url": "http://localhost:8000",
        "max_concurrent_users": 100,
        "test_duration_minutes": 10,
        "cool_down_seconds": 5
    }
}
EOF

# Create systemd service for monitoring (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Creating systemd service..."
    
    sudo tee /etc/systemd/system/amas-monitor.service > /dev/null << EOF
[Unit]
Description=AMAS Performance Monitor
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:$PATH
ExecStart=$(pwd)/venv/bin/python src/amas/monitoring/performance_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable amas-monitor.service
    
    echo -e "${GREEN}✅ Systemd service created. Start with: sudo systemctl start amas-monitor${NC}"
fi

# Create monitoring dashboard start script
cat > start-monitoring.sh << 'EOF'
#!/bin/bash
# Start AMAS monitoring dashboard

echo "🔍 Starting AMAS Performance Monitoring..."

# Check if Redis is running
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start performance monitor in background
python src/amas/monitoring/performance_monitor.py --interval 30 &
MONITOR_PID=$!

echo "✅ Performance monitor started (PID: $MONITOR_PID)"
echo "📊 Dashboard available at: http://localhost:8000/monitoring"
echo ""
echo "Press Ctrl+C to stop monitoring..."

# Wait for interrupt
trap "kill $MONITOR_PID; exit" INT
wait $MONITOR_PID
EOF

chmod +x start-monitoring.sh

# Create load testing script
cat > run-load-tests.sh << 'EOF'
#!/bin/bash
# Run AMAS load tests

echo "⚡ Starting AMAS Load Tests..."

# Quick test
if [ "$1" = "quick" ]; then
    python tests/load/amas_load_test.py --quick
    exit 0
fi

# Stress test  
if [ "$1" = "stress" ]; then
    python tests/load/amas_load_test.py --stress
    exit 0
fi

# Full test suite
python tests/load/amas_load_test.py

echo ""
echo "📊 Load test reports generated:"
echo "  - amas_load_test_results.png"
echo "  - Console performance report"
EOF

chmod +x run-load-tests.sh

echo ""
echo -e "${BLUE}=================================================="
echo "✅ AMAS Performance Monitoring Setup Complete!"
echo -e "==================================================${NC}"
echo ""
echo -e "${GREEN}Available Commands:${NC}"
echo "  ./start-monitoring.sh     - Start performance monitoring"
echo "  ./run-load-tests.sh       - Run full load test suite"  
echo "  ./run-load-tests.sh quick - Run quick load test"
echo "  ./run-load-tests.sh stress - Run stress test"
echo ""
echo -e "${YELLOW}Monitoring Features:${NC}"
echo "  ✅ Real-time system metrics collection"
echo "  ✅ Intelligent alerting system"
echo "  ✅ Performance trend analysis"
echo "  ✅ Redis-based data storage"
echo "  ✅ Comprehensive load testing"
echo "  ✅ Visual performance reports"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Start monitoring: ./start-monitoring.sh"
echo "2. In another terminal, run load tests: ./run-load-tests.sh quick"
echo "3. Check Redis data: redis-cli monitor"
echo ""
echo "🚀 Your AMAS system now has enterprise-grade monitoring! 📊"