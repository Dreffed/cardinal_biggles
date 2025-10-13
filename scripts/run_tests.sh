#!/bin/bash
# Test runner script for Cardinal Biggles

set -e

echo "🧪 Running Cardinal Biggles Test Suite"
echo "======================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run different test categories

echo ""
echo "📦 Running unit tests..."
pytest tests/ -m unit -v

echo ""
echo "🔗 Running integration tests (requires Ollama)..."
pytest tests/ -m integration -v --tb=short || true

echo ""
echo "📊 Generating coverage report..."
pytest tests/ --cov=cardinal_biggles --cov-report=html --cov-report=term-missing

echo ""
echo "✅ Tests complete!"
echo "📈 Coverage report: htmlcov/index.html"
