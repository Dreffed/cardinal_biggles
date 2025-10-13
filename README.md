# Cardinal Biggles 🎩🔍

## Multi-Agent Research Orchestration System with Multi-Provider LLM Support

*Cardinal Biggles is an advanced AI-powered research system that uses specialized agents to conduct comprehensive market research, analyze trends, and generate detailed reports with citations.*

## Overview

``` mermaid
graph TB
    CLI[CLI Interface] --> Coordinator[Coordinator Agent]

    Coordinator --> TrendScout[Trend Scout Agent]
    Coordinator --> Historian[History Researcher Agent]
    Coordinator --> Scholar[Academic Scholar Agent]
    Coordinator --> Journalist[News Analyst Agent]
    Coordinator --> Bibliophile[Book Researcher Agent]
    Coordinator --> Reporter[Report Generator Agent]

    TrendScout --> WebSearch[Web Search Tool]
    Historian --> WebSearch
    Scholar --> WebSearch
    Journalist --> WebSearch
    Bibliophile --> WebSearch

    TrendScout --> KnowledgeStore[(Knowledge Store)]
    Historian --> KnowledgeStore
    Scholar --> KnowledgeStore
    Journalist --> KnowledgeStore
    Bibliophile --> KnowledgeStore
    Reporter --> KnowledgeStore

    Reporter --> ReportOutput[Markdown Report + URL Table]
```

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for different research tasks
- **Multi-Provider LLM Support**: Ollama, OpenAI, Claude, and Perplexity
- **Intelligent Web Search**: Built-in web search with citation tracking
- **Comprehensive Research**: White papers, news, books, and historical analysis
- **Automatic Report Generation**: Markdown reports with reference tables
- **Flexible Configuration**: Per-agent provider and model selection
- **Cost Optimization**: Use free local models where appropriate, paid APIs where needed

## 🏗️ Architecture

```text
Cardinal Biggles
├── Coordinator Agent (orchestrates workflow)
├── Trend Scout Agent (identifies market trends)
├── Historian Agent (researches historical context)
├── Scholar Agent (analyzes academic papers)
├── Journalist Agent (reviews news articles)
├── Bibliophile Agent (researches books)
└── Reporter Agent (generates final reports)
```

### Agent Provider Strategy

| Agent | Default Provider | Rationale |
|-------|-----------------|-----------|
| Coordinator | Ollama | Local, free, sufficient for routing |
| Trend Scout | Perplexity | Built-in web search, current data |
| Historian | Perplexity | Web search across all periods |
| Scholar | Claude | Excellent analysis, long context |
| Journalist | Perplexity | Best for current news |
| Bibliophile | Claude | Good at long-form analysis |
| Reporter | Claude Opus | Best synthesis and writing |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Ollama installed (optional, for local models)
- API keys for OpenAI, Anthropic, and/or Perplexity (optional)

### Installation

Clone the repository
```bash
git clone https://github.com/yourusername/cardinal-biggles.git
cd cardinal-bigglesCreate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activateInstall dependencies
pip install -r requirements.txtCreate default configuration
python -m cli.main init-configSet up environment variables
cp .env.example .env
Edit .env with your API keys
```

### Environment Variables

Create a .env file in the project root:

```bash
# Optional - only needed if using these providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...

# Optional - if using custom Ollama URL
OLLAMA_BASE_URL=http://localhost:11434
```

## Basic Usage

```bash
# Run research on a topic
python -m cli.main research "Multi-Agent AI Systems 2025"

# Show current configuration
python -m cli.main show-config

# Test all LLM providers
python -m cli.main test-providers

# Use custom config file
python -m cli.main research "Vector Databases" --config config/custom.yaml
```

## 📚 Detailed Usage

Research Command

```bash
python -m cli.main research [OPTIONS] TOPIC

Options:
  --config, -c PATH    Path to config file [default: config/config.yaml]
  --output, -o PATH    Output file path (overrides config)
  --provider TEXT      Override default provider for all agents
  --model TEXT         Override default model
  --help              Show this message and exit
```

### Examples

```bash
# Basic research
python -m cli.main research "Quantum Computing Trends"

# Custom output location
python -m cli.main research "AI Ethics" --output reports/ai_ethics.md

# Use specific config
python -m cli.main research "Blockchain" --config config/budget.yaml

# Override provider globally (for testing)
python -m cli.main research "IoT Security" --provider ollama
```

## ⚙️ Configuration

Cardinal Biggles uses YAML configuration files. The default config is at config/config.yaml.

### Configuration Structure

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

    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        fast: "gpt-3.5-turbo"
        standard: "gpt-4"
        powerful: "gpt-4-turbo"

    # ... other providers

agents:
  trend_scout:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    temperature: 0.2

  # ... other agents

research:
  scholar:
    min_papers: 5
    max_papers: 15
    recency_years: 3

  # ... other research parameters
```

### Per-Agent Configuration

Each agent can have its own provider, model, and parameters:

```yaml
agents:
  scholar:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    temperature: 0.1
    fallback_provider: "openai"
    fallback_model: "gpt-4"
    ```

### Configuration Presets

#### Budget Mode (Free/Low Cost):

```yaml
# Use Ollama for everything except final report
agents:
  coordinator: {provider: "ollama"}
  trend_scout: {provider: "ollama"}
  historian: {provider: "ollama"}
  scholar: {provider: "ollama"}
  journalist: {provider: "ollama"}
  bibliophile: {provider: "ollama"}
  reporter: {provider: "openai", model: "gpt-4"}
```

#### Premium Mode (Best Quality):

```yaml
# Use best models for everything
agents:
  coordinator: {provider: "openai", model: "gpt-4"}
  trend_scout: {provider: "perplexity", model: "llama-3.1-sonar-huge-128k-online"}
  historian: {provider: "claude", model: "claude-3-opus-20240229"}
  scholar: {provider: "claude", model: "claude-3-opus-20240229"}
  journalist: {provider: "perplexity", model: "llama-3.1-sonar-huge-128k-online"}
  bibliophile: {provider: "claude", model: "claude-3-opus-20240229"}
  reporter: {provider: "openai", model: "gpt-4-turbo"}
```

## 📊 Output

Report Structure
Generated reports include:

- **Executive Summary** - High-level overview
- **Trend Analysis** - Current market trends
- **Historical Context** - Evolution and background
- **Academic Research** - White papers and studies
- **News Analysis** - Recent articles and developments
- **Books & Resources** - Comprehensive literature
- **Key Insights** - Synthesized findings
- **Recommendations** - Actionable next steps
- **Reference Tables** - Organized by source type

*Reference Tables*
Each report includes detailed reference tables:

```markdown
## White Papers & Academic Research

| Title | Authors | Year | Quality | URL | Relevance |
|-------|---------|------|---------|-----|-----------|
| ... | ... | ... | ... | [...](url) | ... |

## News Articles & Industry Reports

| Headline | Source | Date | Credibility | URL | Impact |
|----------|--------|------|-------------|-----|--------|
| ... | ... | ... | ... | [...](url) | ... |
```

## 🛠️ Development

Project Structure

```text
cardinal-biggles/
├── agents/
│   ├── base_agent.py          # Base agent class
│   ├── coordinator.py          # Workflow coordinator
│   ├── trend_scout.py          # Trend identification
│   ├── historian.py            # Historical research
│   ├── scholar.py              # Academic research
│   ├── journalist.py           # News analysis
│   ├── bibliophile.py          # Book research
│   └── reporter.py             # Report generation
├── core/
│   ├── orchestrator.py         # Main orchestrator
│   ├── llm_factory.py          # LLM provider factory
│   └── knowledge_store.py      # Knowledge management
├── tools/
│   ├── web_search.py           # Web search tool
│   └── url_tracker.py          # URL tracking/validation
├── cli/
│   └── main.py                 # CLI interface
├── config/
│   └── config.yaml             # Main configuration
├── tests/
│   ├── test_agents.py
│   ├── test_llm_factory.py
│   └── test_tools.py
├── requirements.txt
├── .env.example
└── README.md
```

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=cardinal_biggles --cov-report=html
```

## Adding Custom Agents

1. Create new agent class inheriting from ResearchAgent
1. Implement get_system_prompt() method
1. Add agent-specific methods
1. Register in orchestrator.py
1. Add configuration in config.yaml

Example:

```python
from agents.base_agent import ResearchAgent

class CustomAgent(ResearchAgent):
    def get_system_prompt(self) -> str:
        return """You are a Custom Agent specialized in..."""

    async def custom_method(self, param: str):
        task = f"Your task description: {param}"
        return await self.execute_task(task)

```

## 🔧 Troubleshooting

### Common Issues

1. Ollama Connection Error

```bash
Error: Could not connect to Ollama at http://localhost:11434
```

Solution: Ensure Ollama is running (ollama serve)

2. API Key Not Found

```bash
Warning: OPENAI_API_KEY not set in environment
```

Solution: Set environment variable or update .env file

3. Model Not Found

```bash
Error: Model llama3.1:70b not found
```

Solution: Pull the model first (ollama pull llama3.1:70b)

4. Rate Limit Errors

```bash
Error: Rate limit exceeded for provider
```

Solution: Implement retry logic or switch to different provider

### Debug Mode

Enable detailed logging:

```yaml
logging:
  level: "DEBUG"
  console: true
  file: "./logs/debug.log"
```

## 📈 Performance & Costs

### Typical Research Session

| Phase | Agents | Avg Time | Tokens (Est.) | Cost (Est.) |
|-------|--------|----------|---------------|-------------|
| Trend Scouting | 1 | 30-60s | 5K-10K | $1-2 |
| Historical Research | 1 | 60-90s | 10K-15K | $1-2 |
| Academic Research | 1 | 90-120s | 15K-25K | $3-5 |
| News Analysis | 1 | 60-90s | 10K-15K | $1-2 |
| Book Research | 1 | 60-90s | 10K-15K | $2-3 |
| Report Generation | 1 | 120-180s | 20K-40K | $10-15 |
| Total | 6 | 7-10 min | 70K-120K | $18-29 |

### Cost Optimization Tips

1. Use Ollama for drafts: Test workflows with local models first
1. Batch research: Combine multiple topics in one session
1. Adjust parameters: Reduce min_papers, max_articles in config
1. Cache results: Enable intermediate result saving
1. Use smaller models: Switch to fast models for non-critical agents

## 🔐 Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Review generated reports before sharing (may contain sensitive info)
- Implement rate limiting for production deployments

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
1. Create a feature branch (git checkout -b feature/amazing-feature)
1. Commit your changes (git commit -m 'Add amazing feature')
1. Push to the branch (git push origin feature/amazing-feature)
1. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/cardinal-biggles.git
cd cardinal-biggles
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with LangChain
- Inspired by AutoGen, CrewAI, and other multi-agent frameworks
- Perplexity AI for web search capabilities
- Anthropic Claude for analysis excellence

## 📞 Support

Issues: GitHub Issues
Discussions: GitHub Discussions
Email: <support@cardinalbiggles.example.com>

## 🗺️ Roadmap

- [ ] Web UI for visualization and interaction
- [ ] REST API with FastAPI
- [ ] Slack/Teams/Discord integrations
- [ ] n8n workflow support
- [ ] Real-time collaborative research
- [ ] Human-in-the-loop review
- [ ] Advanced cost tracking and budgets
- [ ] Multi-language support
- [ ] Custom agent marketplace

## 📚 Additional Resources

- LangChain Documentation
- Ollama Documentation
- Perplexity API Docs
- Blog: Building Multi-Agent Systems

---

Cardinal Biggles - Named after the legendary character, bringing thoroughness and wit to AI research.
"Research is what I'm doing when I don't know what I'm doing." - Wernher von Braun
