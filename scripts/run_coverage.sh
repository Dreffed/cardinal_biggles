#!/bin/bash
# Coverage report generator

set -e

echo "📊 Generating Coverage Report"
echo "=============================="

pytest tests/ \
    --cov=cardinal_biggles \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml

echo ""
echo "✅ Coverage reports generated:"
echo "   HTML: htmlcov/index.html"
echo "   XML:  coverage.xml"
