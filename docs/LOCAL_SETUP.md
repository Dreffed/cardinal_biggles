# Local Setup Guide - Running Cardinal Biggles with Ollama

This guide explains how to run Cardinal Biggles entirely locally using Ollama, without requiring any external API keys or cloud services.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Running Research](#running-research)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Performance Notes](#performance-notes)

---

## Overview

Cardinal Biggles supports fully local execution using [Ollama](https://ollama.com), an open-source tool for running large language models locally. This mode:

- **No API Keys Required**: Runs entirely on your local machine
- **Privacy**: All data stays on your computer
- **No Usage Costs**: Free to run (only hardware costs)
- **Offline Capable**: Works without internet (after model download)

**Trade-offs:**
- Slower than cloud APIs
- Requires significant RAM (8GB+ recommended)
- No built-in web search (Perplexity features unavailable)

---

## Prerequisites

### 1. System Requirements

**Minimum:**
- RAM: 8GB
- Storage: 10GB free (for models)
- OS: Windows, macOS, or Linux

**Recommended:**
- RAM: 16GB+
- GPU: NVIDIA GPU with 8GB+ VRAM (for faster inference)
- Storage: 20GB+ free

### 2. Install Ollama

#### Windows
1. Download from [ollama.com](https://ollama.com)
2. Run the installer
3. Verify installation:
   ```cmd
   ollama --version
   ```

#### macOS
```bash
brew install ollama
```

Or download from [ollama.com](https://ollama.com)

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 3. Start Ollama Service

The Ollama service must be running before using Cardinal Biggles.

#### Windows
Ollama should start automatically after installation. Verify it's running:
```cmd
curl http://localhost:11434/api/tags
```

#### macOS/Linux
```bash
ollama serve
```

In a separate terminal, verify:
```bash
curl http://localhost:11434/api/tags
```

---

## Quick Start

### 1. Pull Required Models

We provide setup scripts that will pull the required models.

#### Windows
```cmd
scripts\setup_local_models.bat
```

#### Linux/macOS
```bash
chmod +x scripts/setup_local_models.sh
./scripts/setup_local_models.sh
```

This will pull `llama3.1:8b` (~4.7GB), which is the model used in the local configuration.

### 2. Run a Test Research

```bash
python -m cli.main research "Test Topic" --config config/local_ollama.yaml --no-hil
```

### 3. Run Smoke Tests

To verify everything works:

#### Windows
```cmd
scripts\smoke_test_local.bat
```

#### Linux/macOS
```bash
chmod +x scripts/smoke_test_local.sh
./scripts/smoke_test_local.sh
```

---

## Detailed Setup

### Manual Model Setup

If you prefer to set up models manually:

#### Option 1: Minimal (Recommended for Testing)
```bash
ollama pull llama3.1:8b
```
- Size: ~4.7GB
- RAM: ~8GB
- Speed: Fast
- Quality: Good for testing

#### Option 2: Standard (Better Quality)
```bash
ollama pull llama3.1
```
- Size: ~7.3GB
- RAM: ~12GB
- Speed: Medium
- Quality: Better for production

#### Option 3: High Quality (Resource Intensive)
```bash
ollama pull llama3.1:70b
```
- Size: ~40GB
- RAM: ~48GB
- Speed: Slow
- Quality: Best (comparable to GPT-4)

### Verify Models

List installed models:
```bash
ollama list
```

Test a model:
```bash
ollama run llama3.1:8b "Say hello"
```

---

## Running Research

### Basic Usage

```bash
python -m cli.main research "Your Topic" --config config/local_ollama.yaml --no-hil
```

### Command Options

```bash
python -m cli.main research "Your Topic" \
    --config config/local_ollama.yaml \
    --output reports/my_report.md \
    --no-hil
```

**Options:**
- `--config`: Path to config file (use `config/local_ollama.yaml` for local mode)
- `--output`: Custom output path for the report
- `--no-hil`: Disable Human-in-the-Loop mode (recommended for faster execution)

### Configuration

The local configuration (`config/local_ollama.yaml`) is optimized for:

1. **All agents use Ollama**: No external API calls
2. **Single model**: `llama3.1:8b` for all agents (simplicity)
3. **Reduced research parameters**: Faster completion
   - Fewer trends (3 vs 5)
   - Fewer papers (3 vs 5-15)
   - Fewer articles (5 vs 10-25)
   - Fewer books (3 vs 5-10)

To customize, edit `config/local_ollama.yaml`:

```yaml
llm:
  default_provider: "ollama"
  default_model: "llama3.1"

  providers:
    ollama:
      base_url: "http://localhost:11434"
      models:
        fast: "llama3.1:8b"
        standard: "llama3.1"
        powerful: "llama3.1:70b"
      default_temperature: 0.1
      timeout: 120

agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1:8b"

  # ... all agents use ollama ...

research:
  trend_scout:
    max_trends: 3  # Reduced for speed
  scholar:
    min_papers: 3  # Reduced for speed
  journalist:
    min_articles: 5  # Reduced for speed
  bibliophile:
    min_books: 3  # Reduced for speed
```

---

## Testing

### Quick Test

Fast validation that everything works:

```bash
./scripts/quick_test_local.sh  # Linux/macOS
scripts\quick_test_local.bat   # Windows
```

### Full Smoke Test

Comprehensive end-to-end test with validation:

```bash
./scripts/smoke_test_local.sh  # Linux/macOS
scripts\smoke_test_local.bat   # Windows
```

The smoke test will:
1. Check prerequisites (Ollama installed and running)
2. Verify models are available
3. Validate configuration
4. Run a full research workflow
5. Verify output file quality

### Manual Testing

Test specific components:

```bash
# Show configuration
python -m cli.main show-config --config config/local_ollama.yaml

# Test Ollama provider
python -m cli.main test-providers --config config/local_ollama.yaml
```

---

## Troubleshooting

### Common Issues

#### 1. "Could not connect to Ollama"

**Error:**
```
Error initializing orchestrator: Could not connect to Ollama at http://localhost:11434
```

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve  # macOS/Linux

# On Windows, restart the Ollama application
```

#### 2. "Model not found"

**Error:**
```
Error: model 'llama3.1:8b' not found
```

**Solution:**
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify it's available
ollama list
```

#### 3. "Out of Memory" / System Freezing

**Cause:** Model too large for available RAM

**Solutions:**

1. **Use smaller model:**
   ```bash
   # Edit config/local_ollama.yaml
   # Change model to: llama3.1:8b (4.7GB) instead of llama3.1 (7.3GB)
   ```

2. **Close other applications:** Free up RAM

3. **Enable GPU acceleration** (if you have NVIDIA GPU):
   ```bash
   # Ollama automatically uses GPU if available
   # Verify GPU usage:
   nvidia-smi
   ```

4. **Use quantized models:**
   ```bash
   # Pull smaller quantized version
   ollama pull llama3.1:8b-q4_0
   ```

#### 4. Slow Performance

**Expected:** Local models are slower than cloud APIs

**Optimization tips:**

1. **Reduce research parameters** in `config/local_ollama.yaml`:
   ```yaml
   research:
     trend_scout:
       max_trends: 2
     scholar:
       min_papers: 2
       max_papers: 5
   ```

2. **Use faster model:**
   ```bash
   ollama pull phi3  # Smaller, faster model
   ```

3. **Enable GPU acceleration** (NVIDIA GPUs):
   - Ollama automatically detects and uses NVIDIA GPUs
   - Verify with `nvidia-smi`

4. **Reduce timeout in config:**
   ```yaml
   providers:
     ollama:
       timeout: 60  # Reduced from 120
   ```

#### 5. Unicode Errors on Windows

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution:**
This should be fixed in the latest version. If you encounter it, ensure you're using the latest code.

---

## Performance Notes

### Typical Execution Times (llama3.1:8b on 16GB RAM)

- **Trend Scouting**: 2-3 minutes
- **Historical Research**: 3-4 minutes
- **Academic Research**: 4-5 minutes
- **News Analysis**: 3-4 minutes
- **Book Research**: 3-4 minutes
- **Report Generation**: 5-7 minutes
- **Total**: 20-30 minutes

Compare to cloud APIs: 5-10 minutes total

### Hardware Impact

| Component | Impact |
|-----------|--------|
| **RAM** | More RAM = can run larger models |
| **GPU (NVIDIA)** | 3-5x faster inference |
| **CPU** | Minimal impact (GPU handles inference) |
| **Storage (SSD)** | Faster model loading |

### Cost Analysis

**Local (Ollama):**
- Setup: Free (just download)
- Per research: $0 (only electricity)
- Hardware: One-time cost (if upgrading)

**Cloud APIs (OpenAI/Claude/Perplexity):**
- Setup: Free
- Per research: $18-29
- Monthly (10 researches): $180-290

**Break-even:** If running 2+ researches per month, local is cost-effective (after hardware costs)

---

## Advanced Usage

### Custom Model Selection

You can use different models for different agents:

```yaml
agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1:8b"  # Fast model for coordination

  scholar:
    provider: "ollama"
    model: "llama3.1:70b"  # Powerful model for analysis

  reporter:
    provider: "ollama"
    model: "llama3.1:70b"  # Best model for final report
```

### Hybrid Configuration

Mix local and cloud providers:

```yaml
agents:
  coordinator:
    provider: "ollama"  # Free coordination

  trend_scout:
    provider: "perplexity"  # Web search capabilities

  scholar:
    provider: "ollama"  # Local analysis

  reporter:
    provider: "claude"  # Best quality final report
```

This gives you:
- Cost savings (local for bulk work)
- Quality (cloud for critical tasks)
- Web search (Perplexity for current info)

### Using Different Ollama Models

Cardinal Biggles works with any Ollama model:

```bash
# Install alternative models
ollama pull phi3           # Microsoft's smaller model
ollama pull mistral        # Alternative to Llama
ollama pull codellama      # Specialized for code
ollama pull gemma          # Google's model
```

Update config to use them:
```yaml
agents:
  coordinator:
    model: "phi3"  # Faster, smaller
```

---

## Next Steps

1. **Run your first research**: Follow the [Quick Start](#quick-start)
2. **Customize configuration**: Edit `config/local_ollama.yaml`
3. **Experiment with models**: Try different Ollama models
4. **Optimize for your hardware**: Adjust based on RAM/GPU
5. **Explore hybrid mode**: Mix local and cloud providers

For more information:
- **Main Documentation**: [README.md](../README.md)
- **Architecture Details**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Development Guide**: [CLAUDE.md](../CLAUDE.md)

---

## Support

**Issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review [Ollama documentation](https://github.com/ollama/ollama)
- Open an issue on GitHub

**Questions?**
- See main [README.md](../README.md) for general Cardinal Biggles help
- Check [Ollama Discord](https://discord.gg/ollama) for Ollama-specific questions
