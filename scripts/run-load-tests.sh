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