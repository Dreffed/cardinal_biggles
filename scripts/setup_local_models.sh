#!/bin/bash
# Setup script for local Ollama models

echo "=== Cardinal Biggles - Local Model Setup ==="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is not installed"
    echo "Please install from: https://ollama.com"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Error: Ollama is not running"
    echo "Please start Ollama: ollama serve"
    exit 1
fi

echo "✓ Ollama is installed and running"
echo ""

# Option 1: Minimal setup (fastest, 8GB RAM)
echo "Option 1: Minimal Setup (Recommended for testing)"
echo "  - Model: llama3.1:8b"
echo "  - RAM: ~8GB"
echo "  - Speed: Fast"
echo ""

# Option 2: Standard setup (better quality, 16GB RAM)
echo "Option 2: Standard Setup (Better quality)"
echo "  - Models: llama3.1:8b + llama3.1"
echo "  - RAM: ~16GB"
echo "  - Speed: Medium"
echo ""

read -p "Choose option (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Pulling llama3.1:8b..."
        ollama pull llama3.1:8b

        if [ $? -eq 0 ]; then
            echo "✓ Successfully pulled llama3.1:8b"
            echo ""
            echo "Setup complete! You can now run:"
            echo "  python -m cli.main research \"Test Topic\" --config config/local_ollama.yaml"
        else
            echo "❌ Failed to pull model"
            exit 1
        fi
        ;;
    2)
        echo ""
        echo "Pulling llama3.1:8b..."
        ollama pull llama3.1:8b

        echo ""
        echo "Pulling llama3.1..."
        ollama pull llama3.1

        if [ $? -eq 0 ]; then
            echo "✓ Successfully pulled both models"
            echo ""
            echo "Setup complete! You can now run:"
            echo "  python -m cli.main research \"Test Topic\" --config config/local_ollama.yaml"
            echo ""
            echo "Note: Update config/local_ollama.yaml to use llama3.1 for reporter agent"
        else
            echo "❌ Failed to pull models"
            exit 1
        fi
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
