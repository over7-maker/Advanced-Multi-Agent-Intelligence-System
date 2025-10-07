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