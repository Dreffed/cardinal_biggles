#!/bin/bash
# Quick test - just verify CLI works with local config

echo "=== Quick Local Test ==="
echo ""

TEMP_OUTPUT="/tmp/cardinal_quick_test_$$.md"

python -m cli.main research "Quick Test" \
    --config config/local_ollama.yaml \
    --output "$TEMP_OUTPUT" \
    --no-hil

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Quick test passed"
    echo ""
    echo "Report preview:"
    cat "$TEMP_OUTPUT" | head -20
    rm -f "$TEMP_OUTPUT"
else
    echo "❌ Quick test failed"
    exit 1
fi
