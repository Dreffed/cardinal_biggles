# Cardinal Biggles - Claude.md Documentation

## Project Overview

**Cardinal Biggles** is a sophisticated multi-agent research orchestration system that leverages multiple LLM providers (Ollama, OpenAI, Claude, Perplexity) to conduct comprehensive market research, analyze trends, and generate detailed reports with citations.

**Key Features:**
- Multi-agent architecture with specialized research agents
- Multi-provider LLM support with flexible configuration
- Intelligent web search with citation tracking
- Knowledge store with semantic search capabilities
- URL tracking and validation
- Automated report generation with reference tables

---

## Architecture Overview

### System Flow

```
CLI Interface → ResearchOrchestrator → CoordinatorAgent → Specialized Agents → ReporterAgent → Markdown Report
                     ↓                                            ↓
                LLMFactory                              KnowledgeStore
                     ↓                                            ↓
            Provider-specific                          Document Storage
            LLM instances                              & Semantic Search
```

### Core Components

1. **ResearchOrchestrator** ([core/orchestrator.py](core/orchestrator.py))
   - Main entry point for research workflows
   - Initializes all agents with provider-specific LLMs
   - Manages workflow execution and result storage

2. **LLMFactory** ([core/llm_factory.py](core/llm_factory.py))
   - Creates LLM instances for different providers
   - Handles provider-specific configurations
   - Supports fallback mechanisms
   - Environment variable expansion for API keys

3. **KnowledgeStore** ([core/knowledge_store.py](core/knowledge_store.py))
   - In-memory document storage with persistence
   - Semantic search using sentence-transformers
   - Document categorization and tagging
   - Export to Markdown and JSON

---

## Agent Architecture

### Base Agent Class

All agents inherit from `ResearchAgent` ([agents/base_agent.py](agents/base_agent.py:7-97))

**Key Methods:**
- `get_system_prompt()`: Returns agent-specific system prompt (abstract)
- `execute_task()`: Executes research task with LLM
- `_store_knowledge()`: Stores results in knowledge base
- `_extract_urls()`: Extracts URLs from content

### Specialized Agents

#### 1. CoordinatorAgent ([agents/coordinator.py](agents/coordinator.py))
**Role:** Orchestrates the research workflow
**Provider:** Ollama (local, cost-effective)
**Key Method:** `execute_research_workflow(topic)` - Coordinates all research phases

**Workflow Phases:**
1. Trend Scouting
2. Historical Research (parallel)
3. White Paper Research (parallel)
4. News Research (parallel)
5. Book Research (parallel)
6. Report Generation

#### 2. TrendScoutAgent ([agents/trend_scout.py](agents/trend_scout.py))
**Role:** Identifies market trends
**Provider:** Perplexity (built-in web search)
**Key Method:** `scout_trends(domain, timeframe)`

**Output Format:**
- Trend Name
- Category
- Impact Score (1-10)
- Adoption Phase
- Key Evidence
- Recommended Action

#### 3. ScholarAgent ([agents/scholar.py](agents/scholar.py))
**Role:** Analyzes academic papers and white papers
**Provider:** Claude (excellent for long-form analysis)
**Key Method:** `research_whitepapers(topic, min_papers)`

**Search Sources:**
- Google Scholar
- arXiv
- IEEE Xplore
- ResearchGate

#### 4. JournalistAgent ([agents/journalist.py](agents/journalist.py))
**Role:** Reviews news articles and industry reports
**Provider:** Perplexity (best for current news)
**Key Method:** `research_news(topic, days_back, min_articles)`

#### 5. BibliophileAgent ([agents/bibliophile.py](agents/bibliophile.py))
**Role:** Researches books and comprehensive resources
**Provider:** Claude (good at long-form analysis)
**Key Method:** `research_books(topic, min_books)`

#### 6. HistorianAgent ([agents/historian.py](agents/historian.py))
**Role:** Researches historical context
**Provider:** Perplexity (web search across all periods)
**Key Method:** `research_history(topic)`

#### 7. ReporterAgent ([agents/reporter.py](agents/reporter.py))
**Role:** Generates final comprehensive reports
**Provider:** Claude Opus (best synthesis and writing)
**Key Method:** `generate_report(research_data)`

**Report Structure:**
- Executive Summary
- Trend Overview
- Historical Context
- Academic Research Findings
- News & Industry Analysis
- Books & Resources
- Key Insights & Recommendations
- Reference Tables

---

## Tool Systems

### WebSearchTool ([tools/web_search.py](tools/web_search.py))

**Supported Backends:**
- DuckDuckGo (free, primary)
- Serper (paid, Google results)
- Brave (paid)
- Tavily (paid)

**Features:**
- Automatic fallback between backends
- Academic search (Semantic Scholar, arXiv)
- News-specific search
- Structured SearchResult objects

**Key Methods:**
- `search(query)`: General web search
- `search_academic(query)`: Academic paper search
- `_search_semantic_scholar(query)`: Semantic Scholar API
- `_search_arxiv(query)`: arXiv API

### URLTracker ([tools/url_tracker.py](tools/url_tracker.py))

**Features:**
- URL deduplication using MD5 hashing
- Automatic URL categorization
- URL validation with HTTP HEAD requests
- Export to Markdown tables and JSON

**URL Types:**
- Webpage
- PDF
- Academic Paper
- News Article
- Book
- Video
- API

**Key Methods:**
- `add_url(url, ...)`: Add URL with metadata
- `validate_all()`: Validate all pending URLs
- `get_by_type(url_type)`: Filter by type
- `export_markdown_table()`: Export as table

---

## Configuration System

### Config File Structure ([cli/main.py](cli/main.py:189-323))

```yaml
llm:
  default_provider: "ollama"

  providers:
    ollama:
      base_url: "http://localhost:11434"
      models:
        fast: "llama3.1:8b"
        standard: "llama3.1"
        powerful: "llama3.1:70b"
      default_temperature: 0.1

    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        fast: "gpt-3.5-turbo"
        standard: "gpt-4"
        powerful: "gpt-4-turbo"

    claude:
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        standard: "claude-3-sonnet-20240229"
        powerful: "claude-3-opus-20240229"

    perplexity:
      api_key: "${PERPLEXITY_API_KEY}"
      models:
        standard: "llama-3.1-sonar-large-128k-online"
      search_recency_filter: "month"

agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1"

  trend_scout:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    search_recency_filter: "month"

  scholar:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    fallback_provider: "openai"

  reporter:
    provider: "claude"
    model: "claude-3-opus-20240229"
```

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
OLLAMA_BASE_URL=http://localhost:11434  # Optional
```

---

## CLI Interface

### Commands

#### Research Command
```bash
python -m cli.main research "Topic" [OPTIONS]
```

**Options:**
- `--config, -c`: Path to config file (default: `config/config.yaml`)
- `--output, -o`: Output file path
- `--provider`: Override default provider
- `--model`: Override default model

#### Show Config
```bash
python -m cli.main show-config [--config PATH]
```

#### Test Providers
```bash
python -m cli.main test-providers [--config PATH]
```

Tests all configured LLM providers and displays results.

#### Initialize Config
```bash
python -m cli.main init-config [OUTPUT_PATH]
```

Creates a default configuration file.

---

## Data Models

### Document ([core/knowledge_store.py](core/knowledge_store.py:33-58))

```python
@dataclass
class Document:
    id: str
    content: str
    document_type: DocumentType
    source: str
    created_at: datetime
    metadata: Dict[str, Any]
    tags: List[str]
    embedding: Optional[List[float]]
    parent_id: Optional[str]
```

**Document Types:**
- RESEARCH_FINDING
- AGENT_OUTPUT
- WEB_CONTENT
- ACADEMIC_PAPER
- NEWS_ARTICLE
- BOOK_SUMMARY
- REPORT

### SearchResult ([tools/web_search.py](tools/web_search.py:28-41))

```python
@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str]
    relevance_score: Optional[float]
    metadata: Dict[str, Any]
```

### TrackedURL ([tools/url_tracker.py](tools/url_tracker.py:43-78))

```python
@dataclass
class TrackedURL:
    url: str
    title: Optional[str]
    description: Optional[str]
    source_agent: Optional[str]
    url_type: URLType
    status: URLStatus
    http_status: Optional[int]
    content_type: Optional[str]
    metadata: Dict[str, Any]
    tags: List[str]
```

---

## Testing

### Test Structure

Tests are organized in [tests/](tests/) directory:
- [test_llm_factory.py](tests/test_llm_factory.py): LLM factory tests
- [test_knowledge_store.py](tests/test_knowledge_store.py): Knowledge store tests
- [test_web_search.py](tests/test_web_search.py): Web search tool tests
- [test_url_tracker.py](tests/test_url_tracker.py): URL tracker tests
- [conftest.py](tests/conftest.py): Pytest fixtures

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_llm_factory.py

# With coverage
pytest --cov=cardinal_biggles --cov-report=html

# Skip integration tests
pytest -m "not integration"

# Only unit tests
pytest -m unit
```

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.requires_ollama`: Requires Ollama running
- `@pytest.mark.asyncio`: Async tests

---

## Development Patterns

### Adding a New Agent

1. **Create Agent Class**
```python
from agents.base_agent import ResearchAgent

class CustomAgent(ResearchAgent):
    def get_system_prompt(self) -> str:
        return """You are a Custom Agent..."""

    async def custom_method(self, param: str):
        task = f"Your task: {param}"
        return await self.execute_task(task)
```

2. **Add to Orchestrator** ([core/orchestrator.py](core/orchestrator.py:48-113))
```python
agents["custom"] = CustomAgent(
    agent_id="custom_1",
    role="custom",
    llm=self.llm_factory.create_agent_llm("custom"),
    knowledge_store=self.knowledge_store
)
```

3. **Add Configuration**
```yaml
agents:
  custom:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    temperature: 0.1
```

### Error Handling

The system uses a fallback mechanism for LLM providers:

```python
try:
    llm = factory.create_llm(provider=provider, model=model)
except Exception:
    if 'fallback_provider' in config:
        llm = factory.create_llm(
            provider=config['fallback_provider'],
            model=config.get('fallback_model')
        )
```

### Async Patterns

Most research operations are async:

```python
# Sequential execution
result1 = await agent1.execute_task(task1)
result2 = await agent2.execute_task(task2)

# Parallel execution
task1 = asyncio.create_task(agent1.execute_task(...))
task2 = asyncio.create_task(agent2.execute_task(...))
result1, result2 = await asyncio.gather(task1, task2)
```

---

## Dependencies

### Core Dependencies ([requirements.txt](requirements.txt))

**LangChain Ecosystem:**
- `langchain`: Core framework
- `langchain-core`: Core abstractions
- `langchain-ollama`: Ollama integration
- `langchain-openai`: OpenAI integration
- `langchain-anthropic`: Claude integration
- `langchain-community`: Community integrations

**Knowledge Management:**
- `chromadb`: Vector database
- `sentence-transformers`: Embeddings

**Web Search:**
- `duckduckgo-search`: Free web search
- `beautifulsoup4`: HTML parsing
- `requests`: HTTP requests
- `aiohttp`: Async HTTP

**CLI & UI:**
- `click`: CLI framework
- `rich`: Terminal formatting
- `pyyaml`: YAML parsing

**Utilities:**
- `python-dotenv`: Environment variables
- `pydantic`: Data validation

### Dev Dependencies

```bash
pytest
pytest-cov
pytest-asyncio
black
flake8
mypy
```

---

## Performance Considerations

### Cost Optimization

**Provider Strategy:**
- Use Ollama (free) for coordination and routing
- Use Perplexity for web search (built-in search)
- Use Claude for complex analysis (best quality)
- Use fallbacks to manage costs

**Typical Research Session Costs:**
- Trend Scouting: $1-2
- Historical Research: $1-2
- Academic Research: $3-5
- News Analysis: $1-2
- Book Research: $2-3
- Report Generation: $10-15
- **Total: $18-29**

### Parallel Execution

The coordinator runs multiple research phases in parallel:

```python
# Parallel research (phases 2-5)
history_task = asyncio.create_task(historian.research_history(...))
papers_task = asyncio.create_task(scholar.research_whitepapers(...))
news_task = asyncio.create_task(journalist.research_news(...))
books_task = asyncio.create_task(bibliophile.research_books(...))

results = await asyncio.gather(history_task, papers_task, news_task, books_task)
```

### Knowledge Store Optimization

- **In-Memory Storage**: Fast access during research session
- **Optional Embeddings**: Enable for semantic search (requires sentence-transformers)
- **Persistence**: Auto-save to JSON for session resumption
- **Indexing**: Multiple indices (source, type, tag) for fast lookup

---

## File Structure

```
cardinal_biggles/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── coordinator.py          # Workflow coordinator
│   ├── trend_scout.py          # Trend identification
│   ├── historian.py            # Historical research
│   ├── scholar.py              # Academic research
│   ├── journalist.py           # News analysis
│   ├── bibliophile.py          # Book research
│   └── reporter.py             # Report generation
├── core/
│   ├── __init__.py
│   ├── orchestrator.py         # Main orchestrator
│   ├── llm_factory.py          # LLM provider factory
│   └── knowledge_store.py      # Knowledge management
├── tools/
│   ├── __init__.py
│   ├── web_search.py           # Web search tool
│   └── url_tracker.py          # URL tracking
├── cli/
│   ├── __init__.py
│   └── main.py                 # CLI interface
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_agents.py
│   ├── test_llm_factory.py
│   ├── test_knowledge_store.py
│   ├── test_web_search.py
│   └── test_url_tracker.py
├── config/
│   └── config.yaml             # Main configuration
├── reports/                    # Generated reports
├── logs/                       # Log files
├── data/                       # Knowledge store persistence
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── .coveragerc                 # Coverage configuration
├── README.md                   # Project documentation
└── claude.md                   # This file
```

---

## Common Patterns

### 1. Agent Communication

Agents communicate via the knowledge store:

```python
# Agent 1 stores knowledge
await self.knowledge_store.add_document(
    content=result,
    source=self.agent_id,
    document_type=DocumentType.RESEARCH_FINDING
)

# Agent 2 retrieves knowledge
context_docs = await self.knowledge_store.search(
    query="relevant topic",
    source="agent_1"
)
```

### 2. URL Extraction and Tracking

```python
# Extract URLs from LLM response
urls = self._extract_urls(response.content)

# Add to URL tracker
for url in urls:
    tracker.add_url(
        url=url,
        source_agent=self.agent_id,
        tags=[topic]
    )

# Validate all URLs
await tracker.validate_all()
```

### 3. Provider Fallback

```python
try:
    llm = factory.create_llm(provider="claude")
    response = await llm.ainvoke(messages)
except Exception as e:
    logger.warning(f"Primary provider failed: {e}")
    llm = factory.create_llm(provider="openai")
    response = await llm.ainvoke(messages)
```

### 4. Structured Output

Agents return structured dictionaries:

```python
result = {
    "agent_id": self.agent_id,
    "role": self.role,
    "task": task_description,
    "result": response.content,
    "timestamp": datetime.now().isoformat(),
    "urls": extracted_urls
}
```

---

## Troubleshooting

### Common Issues

**1. Ollama Connection Error**
```
Error: Could not connect to Ollama at http://localhost:11434
```
Solution: Start Ollama (`ollama serve`)

**2. API Key Not Found**
```
Warning: OPENAI_API_KEY not set in environment
```
Solution: Set environment variable or update `.env` file

**3. Model Not Found**
```
Error: Model llama3.1:70b not found
```
Solution: Pull the model (`ollama pull llama3.1:70b`)

**4. Import Errors**
```
ImportError: Could not import langchain_ollama
```
Solution: Install required package (`pip install langchain-ollama`)

### Debug Mode

Enable detailed logging in config:

```yaml
logging:
  level: "DEBUG"
  console: true
  file: "./logs/debug.log"
```

---

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files for sensitive data
3. **URL Validation**: URLs are validated before inclusion in reports
4. **Domain Filtering**: Exclude malicious domains via configuration
5. **Rate Limiting**: Implement rate limiting for production deployments

---

## Future Enhancements

Based on [README.md](README.md:470-481):

- [ ] Web UI for visualization and interaction
- [ ] REST API with FastAPI
- [ ] Slack/Teams/Discord integrations
- [ ] n8n workflow support
- [ ] Real-time collaborative research
- [ ] Human-in-the-loop review
- [ ] Advanced cost tracking and budgets
- [ ] Multi-language support
- [ ] Custom agent marketplace

---

## Key Insights for Claude

### When to Use Which Provider

**Ollama (Free, Local):**
- Coordination and routing logic
- Simple text processing
- Development and testing
- When privacy is critical

**Perplexity (Paid, Web Search):**
- Trend scouting (needs current data)
- News analysis (real-time information)
- Historical research (broad web search)
- When you need citations

**Claude (Paid, Anthropic):**
- Academic paper analysis (long context)
- Book research (comprehensive summaries)
- Report generation (best synthesis)
- When you need nuanced understanding

**OpenAI (Paid):**
- Fallback for Claude
- When GPT-4 specific features needed
- When Claude is rate-limited

### Code Quality Notes

- Strong separation of concerns
- Comprehensive async/await usage
- Good error handling with fallbacks
- Well-structured configuration system
- Extensive documentation
- Good test coverage patterns

### Extension Points

1. **New Agents**: Inherit from `ResearchAgent`
2. **New Providers**: Add to `LLMFactory._create_*()` methods
3. **New Search Backends**: Add to `WebSearchTool._search_*()` methods
4. **New Document Types**: Add to `DocumentType` enum
5. **New Output Formats**: Extend `ReporterAgent._generate_*()` methods

---

## Contact & Support

- **Repository**: https://github.com/Dreffed/cardinal_biggles
- **Issues**: GitHub Issues
- **Documentation**: This file and [README.md](README.md)

---

*Last Updated: 2025-10-13*
*Cardinal Biggles - Named after the legendary character, bringing thoroughness and wit to AI research.*
