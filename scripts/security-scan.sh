#!/bin/bash
# AMAS Security Scan Script

echo "🔒 Running AMAS Security Scan..."
echo "================================"

# Install bandit if not present
pip install bandit

# Run security scan
python3 -m bandit -r src/ -f json -o bandit-report.json

# Check if scan passed
if [ $? -eq 0 ]; then
    echo "✅ Security scan passed"
    exit 0
else
    echo "❌ Security issues found - check bandit-report.json"
    exit 1
fi