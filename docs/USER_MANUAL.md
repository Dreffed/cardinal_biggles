# Cardinal Biggles User Manual

**Version**: 0.2.0
**Last Updated**: 2025-10-14
**Status**: Complete

---

## Table of Contents

### [Part 1: Getting Started](#part-1-getting-started)
1. [Introduction](#1-introduction)
2. [What is Cardinal Biggles?](#2-what-is-cardinal-biggles)
3. [Key Features](#3-key-features)
4. [Quick Start](#4-quick-start)
5. [Installation](#5-installation)
6. [First Research Project](#6-first-research-project)

### [Part 2: Core Concepts](#part-2-core-concepts)
7. [Multi-Agent Architecture](#7-multi-agent-architecture)
8. [LLM Providers](#8-llm-providers)
9. [Research Workflow](#9-research-workflow)
10. [Knowledge Store](#10-knowledge-store)
11. [Report Generation](#11-report-generation)

### [Part 3: Configuration](#part-3-configuration)
12. [Configuration Overview](#12-configuration-overview)
13. [LLM Provider Configuration](#13-llm-provider-configuration)
14. [Agent Configuration](#14-agent-configuration)
15. [Research Parameters](#15-research-parameters)
16. [Output Configuration](#16-output-configuration)
17. [Logging Configuration](#17-logging-configuration)

### [Part 4: Using Cardinal Biggles](#part-4-using-cardinal-biggles)
18. [CLI Commands](#18-cli-commands)
19. [Running Research](#19-running-research)
20. [Local Mode (No API Keys)](#20-local-mode-no-api-keys)
21. [Cloud Mode (API Keys)](#21-cloud-mode-api-keys)
22. [Hybrid Mode (Mixed Providers)](#22-hybrid-mode-mixed-providers)
23. [Human-in-the-Loop Mode](#23-human-in-the-loop-mode)

### [Part 5: Advanced Topics](#part-5-advanced-topics)
24. [Custom Agents](#24-custom-agents)
25. [Provider Fallbacks](#25-provider-fallbacks)
26. [Performance Optimization](#26-performance-optimization)
27. [Cost Management](#27-cost-management)
28. [Batch Processing](#28-batch-processing)
29. [Integration with Other Tools](#29-integration-with-other-tools)

### [Part 6: Troubleshooting](#part-6-troubleshooting)
30. [Common Issues](#30-common-issues)
31. [Error Messages](#31-error-messages)
32. [Performance Problems](#32-performance-problems)
33. [Provider-Specific Issues](#33-provider-specific-issues)
34. [FAQ](#34-faq)

### [Part 7: Reference](#part-7-reference)
35. [CLI Reference](#35-cli-reference)
36. [Configuration Schema](#36-configuration-schema)
37. [Environment Variables](#37-environment-variables)
38. [Output Formats](#38-output-formats)
39. [Glossary](#39-glossary)

### [Part 8: Appendices](#part-8-appendices)
40. [Example Configurations](#40-example-configurations)
41. [Use Case Examples](#41-use-case-examples)
42. [Best Practices](#42-best-practices)
43. [Changelog](#43-changelog)

---

## Part 1: Getting Started

### 1. Introduction

Welcome to Cardinal Biggles, your AI-powered research assistant! This comprehensive user manual will guide you through every aspect of using Cardinal Biggles to conduct thorough, well-cited research on any topic.

**Who Should Use This Manual**:
- **Researchers** conducting market analysis
- **Business Analysts** exploring industry trends
- **Product Managers** researching competitors
- **Developers** integrating Cardinal Biggles into workflows
- **Anyone** needing comprehensive research reports with citations

**What You'll Learn**:
- How to install and configure Cardinal Biggles
- How to run research workflows locally or in the cloud
- How to customize agent behavior and research parameters
- How to optimize performance and manage costs
- How to troubleshoot common issues

**Manual Conventions**:
- `Code examples` are shown in monospace font
- **Important** terms are in bold
- *Emphasis* is in italics
- Links to other sections are [clickable](#)

### 2. What is Cardinal Biggles?

Cardinal Biggles is a sophisticated multi-agent research orchestration system that leverages multiple Large Language Models (LLMs) to conduct comprehensive research on any topic. Named after a legendary character known for thoroughness and wit, Cardinal Biggles brings AI-powered research capabilities to your fingertips.

**Core Capabilities**:

1. **Multi-Agent Research**: Seven specialized agents work together to research different aspects of your topic
2. **Multi-Provider Support**: Use Ollama (local), OpenAI, Claude, or Perplexity - or mix them
3. **Intelligent Citation**: Automatic URL extraction and reference tracking
4. **Human Oversight**: Human-in-the-Loop checkpoints for quality control
5. **Comprehensive Reports**: Markdown reports with executive summaries and reference tables
6. **Flexible Deployment**: Run entirely locally or use cloud APIs

**What Makes It Special**:
- **No Single Point of Failure**: Multiple providers mean resilience
- **Cost Optimization**: Use free local models where appropriate, paid APIs where needed
- **Privacy Options**: Run entirely locally with no data leaving your machine
- **Extensible**: Easy to add custom agents or integrate with other tools

### 3. Key Features

#### Multi-Agent Architecture

Cardinal Biggles uses seven specialized agents, each with a specific role:

| Agent | Symbol | Role | Default Provider |
|-------|--------|------|------------------|
| **Coordinator** | 🎯 | Orchestrates the workflow | Ollama (local) |
| **Trend Scout** | 📊 | Identifies market trends | Perplexity |
| **Historian** | 📜 | Researches historical context | Perplexity |
| **Scholar** | 🎓 | Analyzes academic papers | Claude |
| **Journalist** | 📰 | Reviews news articles | Perplexity |
| **Bibliophile** | 📚 | Researches books | Claude |
| **Reporter** | 📝 | Generates final reports | Claude Opus |

#### Flexible LLM Support

**Local Models (Ollama)**:
- Free to use
- Complete privacy
- Works offline
- Requires 8GB+ RAM

**OpenAI (GPT-4, GPT-3.5)**:
- Fast and reliable
- Good general performance
- Competitive pricing
- Requires API key

**Anthropic Claude**:
- Excellent analysis
- Long context windows
- Great for complex research
- Requires API key

**Perplexity**:
- Built-in web search
- Real-time information
- Citation tracking
- Requires API key

#### Human-in-the-Loop (HIL)

Review and approve outputs at key checkpoints:
- **Trend Review**: After initial trend identification
- **Research Review**: After all research phases
- **Report Review**: Before final report is saved

Actions at each checkpoint:
- **Approve**: Continue with results
- **Edit**: Modify the output
- **Regenerate**: Re-run with different parameters
- **Skip**: Proceed without changes
- **Quit**: Exit and save partial results

### 4. Quick Start

Get running in 5 minutes with either local or cloud mode:

#### Option 1: Local Mode (No API Keys)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama (in separate terminal)
ollama serve

# 3. Pull model
ollama pull llama3.1:8b

# 4. Clone and setup
git clone https://github.com/Dreffed/cardinal_biggles.git
cd cardinal_biggles
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 5. Run research
python -m cli.main research "AI Trends 2025" \
  --config config/local_ollama.yaml \
  --no-hil
```

**Pros**: Free, private, offline-capable
**Cons**: Slower (20-30 min), requires RAM

#### Option 2: Cloud Mode (With API Keys)

```bash
# 1. Clone and setup
git clone https://github.com/Dreffed/cardinal_biggles.git
cd cardinal_biggles
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."

# 3. Run research
python -m cli.main research "AI Trends 2025" --no-hil
```

**Pros**: Faster (5-10 min), better quality
**Cons**: Costs $18-29 per research, requires internet

### 5. Installation

Detailed installation instructions for all platforms.

#### Prerequisites

**Required**:
- **Python 3.9+**: Check with `python --version`
- **pip**: Python package installer
- **Git**: For cloning the repository
- **8GB+ RAM**: For local models (16GB recommended)

**Optional**:
- **Ollama**: For local model execution
- **API Keys**: For cloud providers (OpenAI, Claude, Perplexity)

#### Step-by-Step Installation

**1. Clone the Repository**

```bash
git clone https://github.com/Dreffed/cardinal_biggles.git
cd cardinal_biggles
```

**2. Create Virtual Environment**

```bash
# Create venv
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

**3. Install Dependencies**

```bash
# Install required packages
pip install -r requirements.txt

# Optional: Install development dependencies
pip install -r requirements-dev.txt
```

**4. Verify Installation**

```bash
# Check CLI works
python -m cli.main --help

# Expected output: CLI help message
```

**5. Choose Your Mode**

**For Local Mode** (Ollama):
```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Install Ollama (Windows)
# Download from https://ollama.com

# Start Ollama
ollama serve

# Pull model (in new terminal)
ollama pull llama3.1:8b

# Verify model
ollama list

# Use local config
cp config/local_ollama.yaml config/my_config.yaml
```

**For Cloud Mode**:
```bash
# Create config
python -m cli.main init-config config/my_config.yaml

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export PERPLEXITY_API_KEY="your-perplexity-key"

# Or create .env file
echo "OPENAI_API_KEY=your-key" > .env
echo "ANTHROPIC_API_KEY=your-key" >> .env
echo "PERPLEXITY_API_KEY=your-key" >> .env
```

#### Platform-Specific Notes

**Linux**:
- Use package manager for Python: `apt install python3 python3-pip python3-venv`
- Ollama installs via curl script

**macOS**:
- Use Homebrew: `brew install python`
- Ollama available via Homebrew: `brew install ollama`

**Windows**:
- Download Python from python.org
- Download Ollama from ollama.com
- Use PowerShell or Command Prompt
- May need to set execution policy: `Set-ExecutionPolicy RemoteSigned`

### 6. First Research Project

Let's run your first research project step-by-step!

#### Step 1: Choose Your Topic

Pick something specific and interesting:

**Good Topics**:
- "Quantum Computing Trends 2025"
- "Electric Vehicle Market Analysis"
- "Remote Work Technology Impact"
- "AI in Healthcare Applications"

**Avoid**:
- Too broad: "Technology" (too vague)
- Too narrow: "Python 3.11.2 release notes" (too specific)

#### Step 2: Run the Research

**Using Local Mode**:
```bash
python -m cli.main research "Quantum Computing Trends 2025" \
  --config config/local_ollama.yaml \
  --output reports/my_first_report.md \
  --no-hil
```

**Using Cloud Mode**:
```bash
python -m cli.main research "Quantum Computing Trends 2025" \
  --output reports/my_first_report.md \
  --no-hil
```

#### Step 3: Watch the Progress

You'll see output like this:

```
Multi-Agent Research Orchestrator
Topic: Quantum Computing Trends 2025

Initializing Research Agents...
Created ollama LLM for trend_scout (model: llama3.1:8b)
...
All agents initialized successfully

Starting research workflow for: Quantum Computing Trends 2025

Phase 1: Scouting market trends...
Found trends. Analysis complete.

Phase 2: Researching history of 'Quantum Error Correction'...
Phase 3: Finding white papers on 'Quantum Error Correction'...
Phase 4: Analyzing recent news on 'Quantum Error Correction'...
Phase 5: Finding books on 'Quantum Error Correction'...
All research phases complete.

Phase 6: Generating comprehensive report...
Report generated.

Research Complete!
Report saved to: /path/to/reports/my_first_report.md
```

#### Step 4: Review Your Report

```bash
# View in terminal
cat reports/my_first_report.md

# Or open in editor
code reports/my_first_report.md
nano reports/my_first_report.md
vim reports/my_first_report.md
```

#### What to Expect

**Execution Time**:
- Local Mode: 20-30 minutes
- Cloud Mode: 5-10 minutes

**Report Contents**:
- **Executive Summary**: High-level overview
- **Trend Analysis**: Top 5 trends with impact scores
- **Historical Context**: Evolution of the topic
- **Academic Research**: White papers and studies
- **News Analysis**: Recent articles and developments
- **Books & Resources**: Comprehensive literature
- **Key Insights**: Synthesized findings
- **Recommendations**: Actionable next steps
- **Reference Tables**: Organized citations

**File Size**: Typically 50-200 lines (3-10 KB)

#### Next Steps

Now that you've completed your first research:

1. **Try HIL Mode**: Remove `--no-hil` to review results interactively
2. **Customize Config**: Edit config file to adjust research depth
3. **Explore Output**: Check intermediate JSON files in reports/
4. **Read the Manual**: Learn about advanced features below

---

## Part 2: Core Concepts

### 7. Multi-Agent Architecture

Cardinal Biggles uses a multi-agent system where specialized agents collaborate on research tasks.

#### Agent Roles

**1. Coordinator Agent**
- **Role**: Orchestrates the entire workflow
- **Provider**: Ollama (cost-effective for routing logic)
- **Tasks**:
  - Breaks down research requests
  - Determines task execution order
  - Monitors progress
  - Synthesizes agent outputs
  - Manages HIL checkpoints

**2. Trend Scout Agent**
- **Role**: Identifies market trends
- **Provider**: Perplexity (built-in web search)
- **Tasks**:
  - Scouts for emerging trends
  - Rates trends by impact score
  - Identifies adoption phases
  - Provides evidence and citations
  - Recommends focus areas

**Output Format**:
```markdown
# Trend: Quantum Error Correction
- Impact Score: 9/10
- Adoption Phase: Early Majority
- Evidence: Multiple research papers, industry adoption
- Recommendation: Deep dive recommended
```

**3. Historian Agent**
- **Role**: Researches historical context
- **Provider**: Perplexity (web search across time periods)
- **Tasks**:
  - Traces topic evolution
  - Identifies key milestones
  - Provides background context
  - Links past to present

**4. Scholar Agent**
- **Role**: Analyzes academic research
- **Provider**: Claude (excellent at long-form analysis)
- **Tasks**:
  - Finds white papers and academic papers
  - Analyzes research quality
  - Summarizes key findings
  - Tracks citations
  - Evaluates methodology

**Search Sources**:
- Google Scholar
- arXiv
- IEEE Xplore
- ResearchGate
- ACM Digital Library

**5. Journalist Agent**
- **Role**: Reviews news and industry reports
- **Provider**: Perplexity (best for current news)
- **Tasks**:
  - Finds recent news articles
  - Analyzes industry reports
  - Tracks company announcements
  - Identifies market sentiment
  - Evaluates source credibility

**6. Bibliophile Agent**
- **Role**: Researches books and comprehensive resources
- **Provider**: Claude (good at synthesis)
- **Tasks**:
  - Finds relevant books
  - Summarizes key concepts
  - Identifies authoritative sources
  - Recommends reading materials

**7. Reporter Agent**
- **Role**: Generates final comprehensive reports
- **Provider**: Claude Opus (best synthesis)
- **Tasks**:
  - Synthesizes all research
  - Creates executive summary
  - Organizes findings
  - Generates reference tables
  - Ensures coherent narrative

#### Agent Communication

Agents communicate through the **Knowledge Store**:

```
Agent 1 → Knowledge Store → Agent 2
   ↓                           ↓
Stores findings          Retrieves context
```

**Knowledge Flow**:
1. Each agent stores its findings
2. Later agents retrieve context from earlier work
3. Reporter synthesizes all stored knowledge
4. Final report includes all agent contributions

#### Workflow Pattern

```
Coordinator
    ↓
Phase 1: Trend Scout (sequential)
    ↓
Phase 2-5: Parallel Execution
    ├── Historian
    ├── Scholar
    ├── Journalist
    └── Bibliophile
    ↓
Phase 6: Reporter (sequential)
    ↓
Final Report
```

**Parallel Execution**: Phases 2-5 run simultaneously for speed.

### 8. LLM Providers

Cardinal Biggles supports four LLM provider types.

#### Ollama (Local)

**What is it**: Open-source tool for running LLMs locally

**Models Available**:
- llama3.1:8b (fast, 8GB RAM)
- llama3.1 (standard, 16GB RAM)
- llama3.1:70b (powerful, 48GB RAM)
- Many others (phi3, mistral, gemma, etc.)

**Pros**:
- Free to use
- Complete privacy
- Works offline
- No rate limits
- Full control

**Cons**:
- Slower than cloud
- Requires RAM
- Lower quality than GPT-4/Claude
- No built-in web search

**Best For**:
- Development and testing
- Privacy-sensitive research
- Budget-conscious users
- Offline environments

**Setup**:
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve

# Pull model
ollama pull llama3.1:8b
```

#### OpenAI

**What is it**: Leading AI company with GPT models

**Models Available**:
- gpt-3.5-turbo (fast, cheap)
- gpt-4 (balanced)
- gpt-4-turbo (latest)

**Pros**:
- Fast and reliable
- Good general performance
- Wide model selection
- Extensive documentation

**Cons**:
- Requires API key
- Usage costs
- Rate limits
- Less privacy

**Pricing** (approximate):
- GPT-3.5: $0.002/1K tokens
- GPT-4: $0.03/1K tokens
- GPT-4-turbo: $0.01/1K tokens

**Best For**:
- General purpose research
- Fast turnaround needed
- Cost-conscious cloud users

**Setup**:
```bash
export OPENAI_API_KEY="sk-..."
```

#### Anthropic Claude

**What is it**: AI safety company with Claude models

**Models Available**:
- claude-3-haiku (fast)
- claude-3-sonnet (balanced)
- claude-3-opus (best)

**Pros**:
- Excellent analysis
- Long context windows (200K tokens)
- Great for complex research
- Strong reasoning

**Cons**:
- Requires API key
- Higher cost than GPT-3.5
- Slower than GPT-4

**Pricing** (approximate):
- Haiku: $0.0025/1K tokens
- Sonnet: $0.015/1K tokens
- Opus: $0.075/1K tokens

**Best For**:
- Academic research
- Complex analysis
- Long-form synthesis
- High-quality reports

**Setup**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

#### Perplexity

**What is it**: AI search company with LLMs + search

**Models Available**:
- llama-3.1-sonar-small (fast)
- llama-3.1-sonar-large (standard)
- llama-3.1-sonar-huge (powerful)

**Pros**:
- Built-in web search
- Real-time information
- Citation tracking
- Good for current events

**Cons**:
- Requires API key
- Usage costs
- Search-focused (not general purpose)

**Pricing** (approximate):
- Small: $0.002/1K tokens
- Large: $0.005/1K tokens
- Huge: $0.008/1K tokens

**Best For**:
- Trend scouting
- News analysis
- Historical research
- Any task needing current data

**Setup**:
```bash
export PERPLEXITY_API_KEY="pplx-..."
```

#### Provider Comparison

| Feature | Ollama | OpenAI | Claude | Perplexity |
|---------|--------|--------|--------|------------|
| **Cost** | Free | $$ | $$$ | $$ |
| **Speed** | Slow | Fast | Medium | Fast |
| **Quality** | Good | Very Good | Excellent | Good |
| **Privacy** | Excellent | Low | Low | Low |
| **Web Search** | No | No | No | Yes |
| **Offline** | Yes | No | No | No |

### 9. Research Workflow

Understanding the workflow helps you optimize research.

#### Phase 1: Trend Scouting

**Agent**: Trend Scout
**Duration**: 1-3 minutes
**Output**: List of 3-5 trends with impact scores

**What Happens**:
1. Analyzes the research topic
2. Identifies emerging trends
3. Rates each trend by impact (1-10)
4. Determines adoption phase
5. Recommends top trend for deeper research

**Example Output**:
```markdown
# Top Trends in Quantum Computing

1. **Quantum Error Correction** (9/10)
   - Phase: Early Majority
   - Evidence: Multiple breakthroughs in 2024
   - Action: Recommended for deep dive

2. **Topological Qubits** (8/10)
   - Phase: Early Adopters
   - Evidence: Microsoft and IBM investments

3. **Quantum Machine Learning** (7.5/10)
   - Phase: Innovators
   - Evidence: Academic interest growing
```

**HIL Checkpoint**: Optionally review trends before proceeding.

#### Phase 2-5: Parallel Research

These phases run simultaneously for efficiency.

**Phase 2: Historical Research**
- **Agent**: Historian
- **Duration**: 3-6 minutes
- **Focus**: Topic evolution and milestones
- **Output**: Historical timeline and context

**Phase 3: Academic Research**
- **Agent**: Scholar
- **Duration**: 4-8 minutes
- **Focus**: White papers and academic studies
- **Output**: Summaries of 3-15 papers

**Phase 4: News Analysis**
- **Agent**: Journalist
- **Duration**: 3-6 minutes
- **Focus**: Recent articles and industry reports
- **Output**: 5-25 news summaries

**Phase 5: Book Research**
- **Agent**: Bibliophile
- **Duration**: 3-6 minutes
- **Focus**: Books and comprehensive resources
- **Output**: 3-10 book recommendations

**HIL Checkpoint**: Optionally review research before report generation.

#### Phase 6: Report Generation

**Agent**: Reporter
**Duration**: 5-15 minutes
**Output**: Final comprehensive report

**What Happens**:
1. Retrieves all agent outputs from knowledge store
2. Synthesizes findings into coherent narrative
3. Creates executive summary
4. Organizes by section
5. Generates reference tables
6. Formats as markdown

**Report Structure**:
1. Executive Summary
2. Trend Overview
3. Historical Context
4. Academic Research Findings
5. News & Industry Analysis
6. Books & Resources
7. Key Insights & Recommendations
8. Reference Tables

**HIL Checkpoint**: Optionally review report before saving.

#### Workflow Optimization

**For Speed**:
- Use cloud providers (OpenAI/Claude)
- Reduce research parameters
- Skip HIL checkpoints
- Use smaller models

**For Quality**:
- Use Claude for analysis
- Increase research parameters
- Enable HIL checkpoints
- Use larger models

**For Cost**:
- Use Ollama for all agents
- Reduce research parameters
- Skip HIL (auto-approve)
- Cache results

### 10. Knowledge Store

The knowledge store is Cardinal Biggles' "memory" during research.

#### What It Does

**Stores**:
- Agent outputs
- Research findings
- Web content
- Citations

**Provides**:
- Semantic search
- Context retrieval
- Cross-agent communication
- Persistence (optional)

#### How It Works

```python
# Agent stores finding
knowledge_store.add_document(
    content="Research finding...",
    source="scholar",
    document_type="ACADEMIC_PAPER",
    tags=["quantum", "error-correction"]
)

# Later agent retrieves
results = knowledge_store.search(
    query="error correction methods",
    source="scholar"
)
```

#### Document Types

- `RESEARCH_FINDING`: General research results
- `AGENT_OUTPUT`: Agent-generated content
- `WEB_CONTENT`: Scraped web pages
- `ACADEMIC_PAPER`: Academic papers
- `NEWS_ARTICLE`: News articles
- `BOOK_SUMMARY`: Book summaries
- `REPORT`: Final reports

#### Storage Location

**In-Memory** (default):
- Fast access
- No persistence
- Lost after execution

**Persistent** (optional):
- Saved to disk
- Can resume sessions
- Enables caching

**Configuration**:
```yaml
knowledge_store:
  type: "simple"  # or "persistent"
  persist_directory: "./data/knowledge_store"
```

### 11. Report Generation

Understanding report structure helps you interpret results.

#### Report Sections

**1. Executive Summary**
- High-level overview (2-3 paragraphs)
- Key findings
- Main recommendations
- Expected audience: Decision makers

**2. Trend Overview**
- Top 3-5 trends
- Impact scores
- Evidence summary
- Recommendations

**3. Historical Context**
- Topic evolution
- Key milestones
- Important developments
- How we got here

**4. Academic Research Findings**
- White paper summaries
- Key academic insights
- Research methodologies
- Citations

**5. News & Industry Analysis**
- Recent developments
- Company announcements
- Market sentiment
- Industry trends

**6. Books & Resources**
- Recommended books
- Key concepts from each
- Author expertise
- Where to learn more

**7. Key Insights & Recommendations**
- Synthesized findings
- Actionable recommendations
- Risk considerations
- Next steps

**8. Reference Tables**
- Organized by source type
- URLs and titles
- Publication dates
- Quality/relevance scores

#### Report Customization

**Via Configuration**:
```yaml
output:
  default_format: "markdown"
  include_reference_tables: true
  include_metadata: true
  save_intermediate_results: true
```

**Via CLI**:
```bash
python -m cli.main research "Topic" \
  --output custom_report.md
```

#### Report Quality

**Factors Affecting Quality**:
1. **Provider Selection**: Better models = better reports
2. **Research Depth**: More sources = more comprehensive
3. **Topic Specificity**: Focused topics = better results
4. **Agent Configuration**: Proper temperature/parameters

**Quality Indicators**:
- Report length (50-200 lines typical)
- Number of citations (10-50 typical)
- Coherent narrative structure
- Actionable recommendations
- Proper markdown formatting

---

## Part 3: Configuration

### 12. Configuration Overview

Cardinal Biggles uses YAML configuration files for all settings.

#### Configuration File Location

**Default**: `config/config.yaml`

**Custom**: Specify with `--config` flag
```bash
python -m cli.main research "Topic" --config config/my_config.yaml
```

**Provided Configs**:
- `config/config.yaml`: Default multi-provider setup
- `config/local_ollama.yaml`: Local-only with Ollama

#### Configuration Structure

```yaml
llm:                    # LLM provider settings
  default_provider: "..."
  providers:
    ollama: {...}
    openai: {...}
    claude: {...}
    perplexity: {...}

agents:                 # Per-agent configuration
  coordinator: {...}
  trend_scout: {...}
  ...

research:               # Research parameters
  trend_scout: {...}
  historian: {...}
  ...

output:                 # Output settings
  default_format: "..."
  ...

logging:                # Logging configuration
  level: "..."
  ...

hil:                    # Human-in-the-Loop settings
  enabled: false
  ...
```

#### Configuration Priority

1. **CLI flags**: `--provider`, `--model`, `--hil`
2. **Config file**: YAML settings
3. **Defaults**: Built-in fallbacks

Example:
```bash
# Uses OpenAI for all agents (overrides config)
python -m cli.main research "Topic" --provider openai
```

### 13. LLM Provider Configuration

Configure each LLM provider with specific settings.

#### Ollama Configuration

```yaml
llm:
  providers:
    ollama:
      base_url: "http://localhost:11434"
      models:
        fast: "llama3.1:8b"
        standard: "llama3.1"
        powerful: "llama3.1:70b"
      default_temperature: 0.1
      timeout: 120            # seconds
      max_retries: 3
```

**Settings Explained**:
- `base_url`: Ollama server address
- `models`: Available model tiers
- `default_temperature`: Creativity (0=deterministic, 1=creative)
- `timeout`: Max wait time for response
- `max_retries`: Retry failed requests

**Custom Ollama URL**:
```yaml
# If Ollama runs on different port/host
ollama:
  base_url: "http://192.168.1.100:11434"
```

#### OpenAI Configuration

```yaml
llm:
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        fast: "gpt-3.5-turbo"
        standard: "gpt-4"
        powerful: "gpt-4-turbo"
      default_temperature: 0.1
      max_tokens: 4000
      timeout: 60
```

**Settings Explained**:
- `api_key`: OpenAI API key (use env var)
- `max_tokens`: Maximum response length
- `timeout`: API request timeout

**Environment Variable Expansion**:
```yaml
api_key: "${OPENAI_API_KEY}"  # Expands to env var value
```

#### Claude Configuration

```yaml
llm:
  providers:
    claude:
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        fast: "claude-3-haiku-20240307"
        standard: "claude-3-sonnet-20240229"
        powerful: "claude-3-opus-20240229"
      default_temperature: 0.1
      max_tokens: 4000
      timeout: 60
```

**Model Selection**:
- `haiku`: Fastest, cheapest
- `sonnet`: Balanced
- `opus`: Best quality, highest cost

#### Perplexity Configuration

```yaml
llm:
  providers:
    perplexity:
      api_key: "${PERPLEXITY_API_KEY}"
      base_url: "https://api.perplexity.ai"
      models:
        fast: "llama-3.1-sonar-small-128k-online"
        standard: "llama-3.1-sonar-large-128k-online"
        powerful: "llama-3.1-sonar-huge-128k-online"
      default_temperature: 0.2
      max_tokens: 4000
      search_recency_filter: "month"  # Perplexity-specific
      timeout: 90
```

**Perplexity-Specific Settings**:
- `search_recency_filter`: "day", "week", "month", "year"
- `return_citations`: true/false
- `return_images`: true/false

### 14. Agent Configuration

Configure each agent individually.

#### Per-Agent Settings

```yaml
agents:
  coordinator:
    provider: "ollama"           # Which LLM provider
    model: "llama3.1"            # Which model
    temperature: 0.1             # Creativity level
    fallback_provider: "openai"  # If primary fails
    fallback_model: "gpt-4"      # Fallback model
```

**Settings Explained**:
- `provider`: LLM provider to use (ollama/openai/claude/perplexity)
- `model`: Specific model name
- `temperature`: 0-1, higher = more creative
- `fallback_provider`: Backup if primary fails
- `fallback_model`: Model to use on fallback

#### Example: Budget Configuration

Use free Ollama for most agents, paid for critical ones:

```yaml
agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1:8b"

  trend_scout:
    provider: "ollama"
    model: "llama3.1:8b"

  historian:
    provider: "ollama"
    model: "llama3.1:8b"

  scholar:
    provider: "ollama"
    model: "llama3.1:8b"

  journalist:
    provider: "ollama"
    model: "llama3.1:8b"

  bibliophile:
    provider: "ollama"
    model: "llama3.1:8b"

  reporter:
    provider: "openai"         # Use paid for final report
    model: "gpt-4"
```

#### Example: Premium Configuration

Use best models for everything:

```yaml
agents:
  coordinator:
    provider: "openai"
    model: "gpt-4"

  trend_scout:
    provider: "perplexity"
    model: "llama-3.1-sonar-huge-128k-online"

  historian:
    provider: "claude"
    model: "claude-3-opus-20240229"

  scholar:
    provider: "claude"
    model: "claude-3-opus-20240229"

  journalist:
    provider: "perplexity"
    model: "llama-3.1-sonar-huge-128k-online"

  bibliophile:
    provider: "claude"
    model: "claude-3-opus-20240229"

  reporter:
    provider: "claude"
    model: "claude-3-opus-20240229"
```

### 15. Research Parameters

Control research depth and breadth.

#### Trend Scout Parameters

```yaml
research:
  trend_scout:
    max_trends: 5              # Number of trends to identify
    timeframe: "2024-2025"     # Time period to analyze
```

**Recommendations**:
- `max_trends: 3` for quick overview
- `max_trends: 5` for balanced research
- `max_trends: 10` for comprehensive analysis

#### Historian Parameters

```yaml
research:
  historian:
    depth: "comprehensive"     # or "standard", "brief"
    min_sources: 5             # Minimum sources to find
```

**Depth Levels**:
- `brief`: High-level overview
- `standard`: Balanced detail
- `comprehensive`: Deep dive

#### Scholar Parameters

```yaml
research:
  scholar:
    min_papers: 5              # Minimum papers to find
    max_papers: 15             # Maximum papers to analyze
    recency_years: 3           # How recent (years)
```

**Recommendations**:
- Fast research: `min: 3, max: 8`
- Balanced: `min: 5, max: 15`
- Comprehensive: `min: 10, max: 30`

#### Journalist Parameters

```yaml
research:
  journalist:
    min_articles: 10           # Minimum articles
    max_articles: 25           # Maximum articles
    days_back: 90              # How far back (days)
```

**Recommendations**:
- Recent only: `days_back: 30`
- Balanced: `days_back: 90`
- Historical: `days_back: 365`

#### Bibliophile Parameters

```yaml
research:
  bibliophile:
    min_books: 5               # Minimum books
    max_books: 10              # Maximum books
```

### 16. Output Configuration

Control report generation and storage.

```yaml
output:
  default_format: "markdown"              # Output format
  include_metadata: true                  # Include metadata
  include_reference_tables: true          # Include citations
  include_url_validation: true            # Validate URLs
  save_intermediate_results: true         # Save JSON files
  output_directory: "./reports"           # Where to save
```

**Settings Explained**:
- `default_format`: Currently only "markdown" supported
- `include_metadata`: Add timestamps, versions
- `include_reference_tables`: Generate citation tables
- `include_url_validation`: Check URL validity (slow)
- `save_intermediate_results`: Save per-phase JSON
- `output_directory`: Report save location

### 17. Logging Configuration

Control logging behavior.

```yaml
logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
  file: "./logs/orchestrator.log"  # Log file location
  console: true                    # Also log to console
  include_timestamps: true         # Add timestamps
  track_costs: true                # Track API costs
```

**Log Levels**:
- `DEBUG`: Everything (verbose)
- `INFO`: General information
- `WARNING`: Warnings only
- `ERROR`: Errors only

**Recommendations**:
- Development: `level: "DEBUG"`
- Production: `level: "INFO"`
- Troubleshooting: `level: "DEBUG", console: true`

---

## Part 4: Using Cardinal Biggles

### 18. CLI Commands

Cardinal Biggles provides several CLI commands.

#### `research` Command

Main command for running research.

**Syntax**:
```bash
python -m cli.main research [OPTIONS] TOPIC
```

**Options**:
- `--config, -c PATH`: Config file (default: config/config.yaml)
- `--output, -o PATH`: Output file path
- `--provider TEXT`: Override provider for all agents
- `--model TEXT`: Override model for all agents
- `--hil / --no-hil`: Enable/disable HIL mode
- `--auto-approve`: Auto-approve all checkpoints (testing)
- `--help`: Show help message

**Examples**:
```bash
# Basic research
python -m cli.main research "AI Trends 2025"

# Custom config
python -m cli.main research "AI Trends" --config config/local.yaml

# Custom output
python -m cli.main research "AI Trends" --output reports/ai_trends.md

# Local mode only
python -m cli.main research "AI Trends" --provider ollama

# With HIL
python -m cli.main research "AI Trends" --hil

# Auto-approve (testing)
python -m cli.main research "AI Trends" --hil --auto-approve
```

#### `show-config` Command

Display current configuration.

**Syntax**:
```bash
python -m cli.main show-config [OPTIONS]
```

**Options**:
- `--config, -c PATH`: Config file to display

**Example**:
```bash
python -m cli.main show-config --config config/local_ollama.yaml
```

**Output**:
```
Configuration: config/local_ollama.yaml
+-------------+----------+-------------+
| Agent       | Provider | Model       |
+-------------+----------+-------------+
| coordinator | ollama   | llama3.1:8b |
| trend_scout | ollama   | llama3.1:8b |
| ...
```

#### `test-providers` Command

Test all configured LLM providers.

**Syntax**:
```bash
python -m cli.main test-providers [OPTIONS]
```

**Options**:
- `--config, -c PATH`: Config file to test

**Example**:
```bash
python -m cli.main test-providers --config config/config.yaml
```

**Output**:
```
Testing LLM Providers

Provider Test Results
+-------------+-------------------+--------+---------------+
| Provider    | Model             | Status | Response Time |
+-------------+-------------------+--------+---------------+
| ollama      | llama3.1:8b       | OK     | 2.34s         |
| openai      | gpt-4             | OK     | 1.23s         |
| claude      | claude-3-sonnet   | OK     | 1.87s         |
| perplexity  | llama-3.1-sonar   | OK     | 1.45s         |
+-------------+-------------------+--------+---------------+
```

#### `init-config` Command

Create a default configuration file.

**Syntax**:
```bash
python -m cli.main init-config [OUTPUT_PATH]
```

**Default**: `config/config.yaml`

**Example**:
```bash
python -m cli.main init-config config/my_config.yaml
```

**Output**:
```
Created default config at config/my_config.yaml

Don't forget to set your API keys:
  export OPENAI_API_KEY='your-key'
  export ANTHROPIC_API_KEY='your-key'
  export PERPLEXITY_API_KEY='your-key'
```

### 19. Running Research

Detailed guide to running research projects.

#### Basic Research

**Simplest Form**:
```bash
python -m cli.main research "Your Topic Here"
```

**What Happens**:
1. Loads default config (`config/config.yaml`)
2. Initializes agents with configured providers
3. Runs 6-phase workflow
4. Saves report to auto-generated filename
5. Displays summary

**Auto-Generated Filename**:
```
./reports/your_topic_here_report_20251014_153045.md
```

#### Custom Output Location

**Specify Output File**:
```bash
python -m cli.main research "AI Trends" \
  --output reports/ai_trends_2025.md
```

**Specify Output Directory**:
```yaml
# In config
output:
  output_directory: "./reports/custom"
```

#### Using Custom Config

```bash
python -m cli.main research "Topic" \
  --config config/local_ollama.yaml
```

**Use Cases**:
- Local-only mode
- Budget configuration
- Premium configuration
- Testing configuration

#### Overriding Providers

**Override All Agents**:
```bash
python -m cli.main research "Topic" --provider ollama
```

**Override Model**:
```bash
python -m cli.main research "Topic" \
  --provider openai \
  --model gpt-3.5-turbo
```

**Note**: CLI overrides apply to ALL agents.

#### Monitoring Progress

**Console Output**:
```
Initializing Research Agents...
Created ollama LLM for trend_scout
...

Starting research workflow for: AI Trends

Phase 1: Scouting market trends...
[Progress updates]

Phase 2: Researching history...
Phase 3: Finding white papers...
[Parallel execution]

Phase 6: Generating report...

Research Complete!
Report saved to: ./reports/...
```

**Log File**:
```bash
tail -f logs/orchestrator.log
```

#### Interpreting Results

**Success**:
```
Research Complete!
Report saved to: /path/to/report.md

Research Summary
+------------------+----------+---------------+
| Phase            | Status   | Sources Found |
+------------------+----------+---------------+
| Trends           | Complete | 0             |
| History          | Complete | 0             |
| White Papers     | Complete | 0             |
| News             | Complete | 0             |
| Books            | Complete | 0             |
+------------------+----------+---------------+
```

**Note**: "Sources Found: 0" is normal for local mode (no web search).

### 20. Local Mode (No API Keys)

Run Cardinal Biggles entirely locally with Ollama.

#### Setup

**1. Install Ollama**:
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com
```

**2. Start Ollama**:
```bash
ollama serve
```

**3. Pull Model**:
```bash
ollama pull llama3.1:8b
```

**4. Verify**:
```bash
ollama list
# Should show llama3.1:8b
```

#### Running Research

```bash
python -m cli.main research "Your Topic" \
  --config config/local_ollama.yaml \
  --no-hil
```

#### What to Expect

**Pros**:
- **Free**: No API costs
- **Private**: All data stays local
- **Offline**: Works without internet

**Cons**:
- **Slower**: 20-30 minutes vs 5-10
- **No Web Search**: Limited to model knowledge
- **Lower Quality**: Not as polished as GPT-4/Claude

**Performance**:
| Phase | Duration (llama3.1:8b) |
|-------|------------------------|
| Phase 1 | 1-2 min |
| Phases 2-5 | 6-8 min each |
| Phase 6 | 8-15 min |
| **Total** | **20-35 min** |

#### Optimization Tips

**1. Use Faster Model**:
```bash
ollama pull phi3  # Smaller, faster
```

```yaml
# In config
agents:
  reporter:
    model: "phi3"
```

**2. Reduce Research Depth**:
```yaml
research:
  scholar:
    min_papers: 2
    max_papers: 5
  journalist:
    min_articles: 3
    max_articles: 8
```

**3. GPU Acceleration**:
- Ollama auto-detects NVIDIA GPUs
- 3-5x faster with GPU
- Verify: `nvidia-smi`

#### Troubleshooting

See [Local Setup Guide](LOCAL_SETUP.md#troubleshooting) for detailed troubleshooting.

### 21. Cloud Mode (API Keys)

Use cloud providers for faster, higher-quality research.

#### Setup

**1. Get API Keys**:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Perplexity**: https://www.perplexity.ai/settings/api

**2. Set Environment Variables**:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."
```

**Or Create .env File**:
```bash
echo "OPENAI_API_KEY=sk-..." > .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
echo "PERPLEXITY_API_KEY=pplx-..." >> .env
```

**3. Verify Config**:
```bash
python -m cli.main show-config
```

#### Running Research

```bash
python -m cli.main research "Your Topic"
```

**Uses default config with cloud providers**.

#### What to Expect

**Pros**:
- **Fast**: 5-10 minutes
- **High Quality**: Best models
- **Web Search**: Current information (Perplexity)

**Cons**:
- **Costs Money**: $18-29 per research
- **Requires Internet**: Must be online
- **Less Private**: Data sent to providers

**Performance**:
| Phase | Duration (Cloud) |
|-------|------------------|
| Phase 1 | 0.5-1 min |
| Phases 2-5 | 1-2 min each |
| Phase 6 | 2-5 min |
| **Total** | **5-10 min** |

#### Cost Estimation

**Typical Research** ($18-29):
- Phase 1 (Trend Scout): $1-2
- Phase 2 (Historian): $1-2
- Phase 3 (Scholar): $3-5
- Phase 4 (Journalist): $1-2
- Phase 5 (Bibliophile): $2-3
- Phase 6 (Reporter): $10-15

**Budget Options**:
```yaml
# Use cheaper models
agents:
  reporter:
    provider: "openai"
    model: "gpt-3.5-turbo"  # Cheaper than gpt-4
```

#### Rate Limits

**Common Limits**:
- OpenAI: 3,500 requests/minute (paid tier)
- Claude: 50 requests/minute
- Perplexity: Varies by plan

**If You Hit Limits**:
- Add delays between phases
- Use multiple API keys
- Upgrade to higher tier

### 22. Hybrid Mode (Mixed Providers)

Mix local and cloud providers for optimal cost/quality.

#### Strategy

**Use Local For**:
- Coordination (cheap routing logic)
- Initial trend scouting
- Historical research (knowledge-based)

**Use Cloud For**:
- Academic research (Claude excels)
- Final report (quality matters)
- Web search (Perplexity needed)

#### Example Configuration

```yaml
agents:
  coordinator:
    provider: "ollama"          # Free routing
    model: "llama3.1:8b"

  trend_scout:
    provider: "perplexity"      # Web search needed
    model: "llama-3.1-sonar-large-128k-online"

  historian:
    provider: "ollama"          # Knowledge-based
    model: "llama3.1:8b"

  scholar:
    provider: "claude"          # Quality analysis
    model: "claude-3-sonnet-20240229"

  journalist:
    provider: "perplexity"      # Current news
    model: "llama-3.1-sonar-large-128k-online"

  bibliophile:
    provider: "ollama"          # Books are knowledge-based
    model: "llama3.1:8b"

  reporter:
    provider: "claude"          # Quality report
    model: "claude-3-opus-20240229"
```

**Cost**: ~$12-18 (vs $18-29 full cloud)
**Time**: ~12-18 min (vs 5-10 min full cloud)
**Quality**: High where it matters

#### Cost/Quality Tradeoffs

| Configuration | Cost | Time | Quality |
|---------------|------|------|---------|
| Full Local | $0 | 25 min | Good |
| Hybrid | $12-18 | 15 min | Very Good |
| Full Cloud | $25 | 7 min | Excellent |

### 23. Human-in-the-Loop Mode

Review and approve outputs at key checkpoints.

#### Enabling HIL

**Via CLI**:
```bash
python -m cli.main research "Topic" --hil
```

**Via Config**:
```yaml
hil:
  enabled: true
```

**CLI overrides config**.

#### Checkpoints

**Checkpoint 1: Trend Review**
- **When**: After Phase 1 (Trend Scouting)
- **Why**: Review trends before deeper research
- **Decision**: Approve, edit, regenerate, or quit

**Checkpoint 2: Research Review**
- **When**: After Phases 2-5 (All Research)
- **Why**: Review findings before report generation
- **Decision**: Approve, edit, or quit

**Checkpoint 3: Report Review**
- **When**: After Phase 6 (Report Generation)
- **Why**: Final review before saving
- **Decision**: Approve, edit, regenerate, or save

#### Checkpoint Interface

```
+---------------------------------------+
| Checkpoint: Trend Scouting            |
| Type: trend_review                    |
+---------------------------------------+

Identified Trends:
1. Quantum Error Correction (9/10)
2. Topological Qubits (8/10)
3. Quantum ML (7.5/10)
...

Available Actions:
  [A] Approve & Continue
  [E] Edit Data
  [R] Regenerate
  [S] Skip to Next Phase
  [Q] Quit

Choose action [A]: _
```

#### Actions Explained

**[A] Approve**:
- Accept results as-is
- Continue to next phase
- No changes made

**[E] Edit**:
- Manually modify the output
- Opens in text editor
- Continue with edited version

**[R] Regenerate**:
- Re-run the phase
- May produce different results
- Useful if output is poor

**[S] Skip**:
- Proceed without changes
- Don't regenerate
- Similar to approve

**[Q] Quit**:
- Exit workflow early
- Save partial results
- Knowledge store persisted

#### Configuration

```yaml
hil:
  enabled: false              # Enable HIL mode
  auto_approve: false         # Auto-approve (testing)
  checkpoints:
    trend_review:
      enabled: true           # Enable this checkpoint
      timeout: 300            # Auto-approve after 5 min (0=never)
    research_review:
      enabled: true
      timeout: 600            # 10 minutes
    report_review:
      enabled: true
      timeout: 0              # Never auto-approve
  allow_editing: true         # Allow manual edits
  allow_regeneration: true    # Allow regeneration
  save_checkpoints: true      # Save checkpoint data
  checkpoint_file: "./data/hil_checkpoints.json"
```

#### Auto-Approve Mode

For testing or CI/CD:

```bash
python -m cli.main research "Topic" --hil --auto-approve
```

**What It Does**:
- Pauses at checkpoints
- Automatically approves
- Logs checkpoint data
- Continues immediately

**Use Cases**:
- Automated testing
- CI/CD pipelines
- Unattended execution
- Checkpoint logging

#### HIL Summary

After completion:
```
HIL Checkpoint Summary:
  Total Checkpoints: 3
  Approvals: 2
  Edits: 1
  Regenerations: 0
```

---

*Due to length constraints, I'll continue with the remaining sections in my next message. The manual is comprehensive and covers all aspects of using Cardinal Biggles.*

---

## Part 5: Advanced Topics

(Continuing in next message...)
