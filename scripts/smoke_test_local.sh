#!/bin/bash
# End-to-end smoke test with local Ollama

set -e  # Exit on error

echo "=== Cardinal Biggles - Local Smoke Test ==="
echo ""

# Configuration
CONFIG="config/local_ollama.yaml"
TOPIC="Artificial Intelligence"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="./reports/local/smoke_test_${TIMESTAMP}.md"

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed"
    exit 1
fi

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama not running"
    echo "Please start Ollama: ollama serve"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# Step 2: Check models
echo "Step 2: Checking Ollama models..."

if ! ollama list | grep -q "llama3.1:8b"; then
    echo "❌ Model llama3.1:8b not found"
    echo "Run: ollama pull llama3.1:8b"
    exit 1
fi

echo "✓ Required models available"
echo ""

# Step 3: Verify config
echo "Step 3: Verifying configuration..."

if [ ! -f "$CONFIG" ]; then
    echo "❌ Config file not found: $CONFIG"
    exit 1
fi

python -m cli.main show-config --config "$CONFIG" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Configuration valid"
else
    echo "❌ Configuration invalid"
    exit 1
fi

echo ""

# Create output directory
mkdir -p ./reports/local

# Step 4: Run research workflow
echo "Step 4: Running research workflow..."
echo "Topic: $TOPIC"
echo "Config: $CONFIG"
echo "Output: $OUTPUT"
echo ""

start_time=$(date +%s)

python -m cli.main research "$TOPIC" \
    --config "$CONFIG" \
    --output "$OUTPUT" \
    --no-hil

exit_code=$?
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""

# Step 5: Verify results
if [ $exit_code -eq 0 ]; then
    echo "✓ Research workflow completed successfully"
    echo "Duration: ${duration}s ($(($duration / 60))m $(($duration % 60))s)"
    echo ""

    # Check output file
    if [ -f "$OUTPUT" ]; then
        file_size=$(wc -c < "$OUTPUT")
        line_count=$(wc -l < "$OUTPUT")

        echo "Step 5: Verifying output..."
        echo "  Output file: $OUTPUT"
        echo "  File size: ${file_size} bytes"
        echo "  Line count: ${line_count}"

        if [ $file_size -gt 1000 ]; then
            echo "  ✓ Output file has reasonable size"
        else
            echo "  ⚠ Output file seems small (< 1KB)"
        fi

        # Check for key sections
        if grep -q "# Executive Summary" "$OUTPUT" || grep -q "Executive Summary" "$OUTPUT"; then
            echo "  ✓ Contains Executive Summary"
        else
            echo "  ⚠ Missing Executive Summary"
        fi

        if grep -q "# Trend" "$OUTPUT" || grep -q "Trend" "$OUTPUT"; then
            echo "  ✓ Contains Trend Analysis"
        else
            echo "  ⚠ Missing Trend Analysis"
        fi

        echo ""
        echo "=== SMOKE TEST PASSED ==="
        echo "Report available at: $OUTPUT"
        echo ""
        echo "Preview (first 20 lines):"
        head -20 "$OUTPUT"

    else
        echo "❌ Output file not created"
        exit 1
    fi
else
    echo "❌ Research workflow failed with exit code: $exit_code"
    exit 1
fi
