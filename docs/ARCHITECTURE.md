# Cardinal Biggles - Architecture Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Component Architecture](#component-architecture)
- [Multi-Agent System](#multi-agent-system)
- [LLM Provider System](#llm-provider-system)
- [Knowledge Management](#knowledge-management)
- [Workflow Engine](#workflow-engine)
- [Tool System](#tool-system)
- [CLI Interface](#cli-interface)
- [Data Flow](#data-flow)
- [Configuration System](#configuration-system)
- [Error Handling & Resilience](#error-handling--resilience)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Extension Points](#extension-points)

---

## System Overview

Cardinal Biggles is a **multi-agent research orchestration system** designed to conduct comprehensive, multi-source research using multiple Large Language Model (LLM) providers.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                             │
│                    (Click + Rich UI)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Research Orchestrator                          │
│         (Workflow Management + Agent Coordination)               │
└─────────┬───────────────────────────────────────────┬───────────┘
          │                                           │
          ▼                                           ▼
┌──────────────────────┐                    ┌─────────────────────┐
│    LLM Factory       │                    │  Knowledge Store    │
│ (Provider Management)│                    │  (Document Storage) │
└──────────┬───────────┘                    └──────────┬──────────┘
           │                                           │
           ▼                                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Agent Layer                                │
│  Coordinator │ TrendScout │ Historian │ Scholar │ Journalist │   │
│                  Bibliophile │ Reporter                           │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Tool Layer                                 │
│         WebSearch │ URLTracker │ Citations │ Validation          │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Patterns

1. **Agent-Based Architecture**: Specialized agents for different research tasks
2. **Provider Abstraction**: LangChain-based abstraction over multiple LLM providers
3. **Knowledge Store Pattern**: Centralized knowledge management with semantic search
4. **Workflow Orchestration**: Coordinator-driven multi-phase research workflow
5. **Tool Composition**: Agents compose multiple tools for complex tasks
6. **Configuration-Driven**: YAML-based configuration for all system parameters

---

## Architecture Principles

### 1. Modularity

Every component is **loosely coupled** and can be replaced independently:
- Agents can be added/removed without affecting others
- LLM providers can be swapped via configuration
- Tools can be composed in different ways

### 2. Extensibility

The system is designed for extension:
- New agents inherit from `ResearchAgent` base class
- New providers are added to `LLMFactory`
- New tools implement standard interfaces

### 3. Separation of Concerns

Clear boundaries between layers:
- **CLI Layer**: User interaction and presentation
- **Orchestration Layer**: Workflow management
- **Agent Layer**: Research task execution
- **Tool Layer**: Primitive operations (search, validation)
- **Storage Layer**: Knowledge persistence

### 4. Configuration Over Code

Most behavior is configurable:
- Agent-to-provider mappings
- Research parameters (depth, breadth)
- Output formats and locations
- Logging and debugging

### 5. Fail-Safe Design

Graceful degradation and fallbacks:
- Provider fallbacks (if primary fails, use secondary)
- Validation with error recovery
- Checkpoints for Human-in-the-Loop (HIL) review
- Comprehensive error logging

### 6. Observable

Built-in observability:
- Structured logging at all layers
- Progress tracking and reporting
- Performance metrics
- Debugging hooks

---

## Component Architecture

### Core Components

#### 1. ResearchOrchestrator

**Location**: `core/orchestrator.py`

**Responsibilities**:
- Initialize all agents with configured LLM providers
- Manage research workflow execution
- Coordinate inter-agent communication
- Handle result aggregation and storage

**Key Methods**:
```python
class ResearchOrchestrator:
    def __init__(self, config: Dict[str, Any])
    async def run_research(self, topic: str) -> Dict[str, Any]
    def save_report(self, report: str, filepath: str)
```

**Interactions**:
- Creates agents via LLMFactory
- Delegates workflow to CoordinatorAgent
- Stores results in KnowledgeStore
- Saves final report to filesystem

#### 2. LLMFactory

**Location**: `core/llm_factory.py`

**Responsibilities**:
- Create LLM instances for different providers
- Handle provider-specific configuration
- Manage API keys and authentication
- Implement fallback logic

**Supported Providers**:
- **Ollama**: Local models (llama3.1, mistral, etc.)
- **OpenAI**: GPT-3.5, GPT-4, GPT-4-turbo
- **Anthropic Claude**: Claude 3 Sonnet, Opus
- **Perplexity**: Sonar models with web search

**Key Methods**:
```python
class LLMFactory:
    def create_llm(self, provider: str, model: str, **kwargs) -> BaseChatModel
    def create_agent_llm(self, agent_name: str) -> BaseChatModel
    def test_provider(self, provider: str) -> bool
```

**Provider Selection Logic**:
```
1. Check agent-specific configuration
2. Use agent's configured provider and model
3. If not configured, use default provider
4. If provider fails, use fallback_provider (if configured)
5. Apply provider-specific parameters (temperature, timeout, etc.)
```

#### 3. KnowledgeStore

**Location**: `core/knowledge_store.py`

**Responsibilities**:
- Store research findings from all agents
- Enable semantic search across documents
- Categorize and tag documents
- Export knowledge in multiple formats

**Storage Model**:
```python
@dataclass
class Document:
    id: str                    # Unique identifier
    content: str               # Document text
    document_type: DocumentType  # Type classification
    source: str                # Source agent or URL
    created_at: datetime       # Timestamp
    metadata: Dict[str, Any]   # Arbitrary metadata
    tags: List[str]            # Search tags
    embedding: Optional[List[float]]  # Semantic embedding
    parent_id: Optional[str]   # Hierarchical structure
```

**Document Types**:
- `RESEARCH_FINDING`: Research results from agents
- `AGENT_OUTPUT`: Raw agent responses
- `WEB_CONTENT`: Scraped web content
- `ACADEMIC_PAPER`: Paper summaries
- `NEWS_ARTICLE`: News article content
- `BOOK_SUMMARY`: Book summaries
- `REPORT`: Final generated reports

**Key Features**:
- **In-Memory Storage**: Fast access during research
- **Optional Embeddings**: Semantic search using sentence-transformers
- **Persistence**: JSON export/import for session resumption
- **Multiple Indices**: By source, type, tag for fast lookup

---

## Multi-Agent System

### Agent Architecture

All agents inherit from `ResearchAgent` base class:

```python
class ResearchAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        role: str,
        llm: BaseChatModel,
        knowledge_store: KnowledgeStore
    )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt"""

    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute a research task using the LLM"""

    def _store_knowledge(self, content: str, doc_type: DocumentType):
        """Store results in knowledge base"""

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
```

### Agent Roster

#### 1. CoordinatorAgent

**Provider**: Ollama (local, cost-effective)
**Role**: Orchestrate the research workflow

**System Prompt**:
```
You are the Research Coordinator for a multi-agent research system.
Your role is to:
1. Understand the research topic
2. Plan the research workflow
3. Coordinate specialized agents
4. Synthesize results
5. Ensure comprehensive coverage
```

**Workflow Phases**:
```python
async def execute_research_workflow(self, topic: str):
    # Phase 1: Trend Scouting
    trends = await trend_scout.scout_trends(topic)

    # Phase 2-5: Parallel Research
    results = await asyncio.gather(
        historian.research_history(topic),
        scholar.research_whitepapers(topic),
        journalist.research_news(topic),
        bibliophile.research_books(topic)
    )

    # Phase 6: Report Generation
    report = await reporter.generate_report(all_research_data)
    return report
```

#### 2. TrendScoutAgent

**Provider**: Perplexity (built-in web search)
**Role**: Identify current market trends

**Output Structure**:
```yaml
Trend:
  name: "AI-Powered Code Generation"
  category: "Technology/Developer Tools"
  impact_score: 9/10
  adoption_phase: "Early Majority"
  key_evidence:
    - Evidence point 1
    - Evidence point 2
  recommended_action: "Monitor closely, consider early adoption"
```

**Search Strategy**:
- Uses Perplexity's online search models
- Filters by recency (configurable: day, week, month)
- Focuses on current events and emerging patterns

#### 3. HistorianAgent

**Provider**: Perplexity (web search across all time periods)
**Role**: Research historical context

**Research Areas**:
- Origins and evolution
- Key milestones and dates
- Historical figures and organizations
- Timeline of developments
- Lessons from history

#### 4. ScholarAgent

**Provider**: Claude (excellent for long-form analysis)
**Role**: Analyze academic papers and white papers

**Search Sources**:
- Google Scholar
- arXiv
- IEEE Xplore
- ResearchGate
- ACM Digital Library

**Analysis Framework**:
```
For each paper:
1. Citation (APA format)
2. Key findings
3. Methodology
4. Relevance to topic
5. Notable citations
```

#### 5. JournalistAgent

**Provider**: Perplexity (best for current news)
**Role**: Review news articles and industry reports

**Search Strategy**:
- Recent news (configurable days_back)
- Industry publications
- Press releases
- Expert commentary

**Output Format**:
```
Article:
  title: "..."
  source: "Publication Name"
  date: "YYYY-MM-DD"
  url: "..."
  summary: "..."
  key_quotes: [...]
  relevance: "High/Medium/Low"
```

#### 6. BibliophileAgent

**Provider**: Claude (good at long-form analysis)
**Role**: Research books and comprehensive resources

**Search Sources**:
- Google Books
- Amazon
- Library catalogs
- Publisher websites

**Book Analysis**:
```
Book:
  title: "..."
  author: "..."
  year: YYYY
  isbn: "..."
  summary: "..."
  key_concepts: [...]
  target_audience: "..."
  relevance_score: X/10
```

#### 7. ReporterAgent

**Provider**: Claude Opus (best synthesis and writing)
**Role**: Generate comprehensive final reports

**Report Structure**:
```markdown
# Research Report: [Topic]

## Executive Summary
(2-3 paragraphs synthesizing findings)

## 1. Trend Overview
(Trends identified by TrendScout)

## 2. Historical Context
(Historical research from Historian)

## 3. Academic Research
(Papers analyzed by Scholar)

## 4. News & Industry Analysis
(Articles reviewed by Journalist)

## 5. Books & Resources
(Books researched by Bibliophile)

## 6. Key Insights
(Cross-cutting themes and patterns)

## 7. Recommendations
(Actionable next steps)

## References
(Comprehensive citation table)
```

**Citation Management**:
- Extracts all URLs from agent outputs
- Validates URLs (HTTP status checks)
- Categorizes by source type
- Generates reference tables

---

## LLM Provider System

### Provider Abstraction

The system uses **LangChain** as the provider abstraction layer:

```python
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
```

### Provider Implementations

#### Ollama (Local)

```python
def _create_ollama(self, model: str, **kwargs) -> BaseChatModel:
    return ChatOllama(
        base_url=self.config["providers"]["ollama"]["base_url"],
        model=model,
        temperature=kwargs.get("temperature", 0.1),
        num_ctx=kwargs.get("num_ctx", 8192)
    )
```

**Advantages**:
- Free (no API costs)
- Privacy (data stays local)
- No rate limits
- Offline capable

**Disadvantages**:
- Requires local hardware
- Slower than cloud APIs
- Limited to models that fit in RAM

#### OpenAI

```python
def _create_openai(self, model: str, **kwargs) -> BaseChatModel:
    return ChatOpenAI(
        api_key=self.config["providers"]["openai"]["api_key"],
        model=model,
        temperature=kwargs.get("temperature", 0.1),
        max_tokens=kwargs.get("max_tokens")
    )
```

**Advantages**:
- Fast inference
- High-quality outputs (GPT-4)
- Wide model selection
- Good documentation

**Disadvantages**:
- API costs ($$$)
- Data sent to external service
- Rate limits
- Requires internet

#### Anthropic Claude

```python
def _create_claude(self, model: str, **kwargs) -> BaseChatModel:
    return ChatAnthropic(
        api_key=self.config["providers"]["claude"]["api_key"],
        model=model,
        temperature=kwargs.get("temperature", 0.1),
        max_tokens=kwargs.get("max_tokens", 4096)
    )
```

**Advantages**:
- Excellent for long-form analysis
- Large context windows (100k+ tokens)
- High-quality reasoning
- Good at following complex instructions

**Disadvantages**:
- API costs ($$$)
- Data sent to external service
- Limited model selection
- Requires internet

#### Perplexity

```python
def _create_perplexity(self, model: str, **kwargs) -> BaseChatModel:
    return ChatOpenAI(  # Perplexity uses OpenAI-compatible API
        api_key=self.config["providers"]["perplexity"]["api_key"],
        base_url="https://api.perplexity.ai",
        model=model,
        temperature=kwargs.get("temperature", 0.3)
    )
```

**Advantages**:
- Built-in web search
- Current information (real-time)
- Automatic citations
- Good for research tasks

**Disadvantages**:
- API costs ($$)
- Limited control over search
- Requires internet
- Narrower use case

### Provider Selection Strategy

**Recommended Configuration**:

```yaml
agents:
  coordinator:
    provider: "ollama"      # Free coordination
  trend_scout:
    provider: "perplexity"  # Current trends (web search)
  historian:
    provider: "perplexity"  # Historical web search
  scholar:
    provider: "claude"      # Long-form analysis
  journalist:
    provider: "perplexity"  # Current news
  bibliophile:
    provider: "claude"      # Book analysis
  reporter:
    provider: "claude"      # Best synthesis
```

**Cost Optimization**:
- Use Ollama for coordination (free)
- Use Perplexity only where web search is critical
- Use Claude Opus only for final report
- Use Claude Sonnet for intermediate analysis

**Performance Optimization**:
- Use faster models for simple tasks
- Use powerful models for complex synthesis
- Enable parallel execution where possible

---

## Knowledge Management

### Knowledge Store Architecture

```
┌──────────────────────────────────────────────┐
│          Knowledge Store                      │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │     In-Memory Storage               │    │
│  │  (Fast access during research)      │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │     Document Indexing               │    │
│  │  - By Source (agent ID, URL)        │    │
│  │  - By Type (research, news, etc.)   │    │
│  │  - By Tags (topic-specific)         │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │  Semantic Search (Optional)         │    │
│  │  - Sentence Transformers            │    │
│  │  - Vector similarity                │    │
│  └────────────────────────────────────┘    │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │     Persistence                     │    │
│  │  - JSON export/import               │    │
│  │  - Markdown export                  │    │
│  └────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### Document Lifecycle

1. **Creation**: Agent produces research finding
2. **Storage**: Stored in KnowledgeStore with metadata
3. **Indexing**: Multiple indices updated (source, type, tag)
4. **Embedding** (Optional): Generate semantic embedding
5. **Retrieval**: Other agents query via search/filter
6. **Aggregation**: ReporterAgent synthesizes all documents
7. **Export**: Final report + knowledge JSON

### Search Capabilities

**Exact Search**:
```python
# Get all documents from a specific agent
docs = knowledge_store.search(source="trend_scout_1")

# Get all documents of a type
docs = knowledge_store.get_by_type(DocumentType.ACADEMIC_PAPER)

# Get all documents with a tag
docs = knowledge_store.get_by_tag("machine_learning")
```

**Semantic Search** (if embeddings enabled):
```python
# Find semantically similar documents
docs = knowledge_store.semantic_search(
    query="deep learning architectures",
    k=10  # Top 10 results
)
```

### Export Formats

**Markdown**:
```python
knowledge_store.export_markdown("knowledge_base.md")
```

**JSON**:
```python
knowledge_store.export_json("knowledge_base.json")
```

---

## Workflow Engine

### Workflow Phases

Cardinal Biggles executes research in **6 phases**:

```
Phase 1: Planning
   │
   ├─> Coordinator analyzes topic
   └─> Plans research workflow

Phase 2: Trend Scouting
   │
   └─> TrendScout identifies current trends

Phase 3-6: Parallel Research
   │
   ├─> Historian: Historical context
   ├─> Scholar: Academic papers
   ├─> Journalist: News articles
   └─> Bibliophile: Books

Phase 7: Report Generation
   │
   ├─> Reporter synthesizes all findings
   └─> Generates final markdown report
```

### Human-in-the-Loop (HIL) Mode

At each phase, the system can pause for human review:

```python
if hil_enabled:
    console.print(Panel(
        f"[yellow]Phase {phase} complete. Results:[/yellow]\n\n{results}"
    ))
    if not Confirm.ask("Continue to next phase?"):
        sys.exit(0)
```

**Use Cases**:
- Review trend selection before deep research
- Validate source quality
- Adjust research direction mid-workflow
- Cost control (stop early if not useful)

### Parallel Execution

Phases 3-6 run in parallel using `asyncio.gather()`:

```python
# Launch all research tasks concurrently
history_task = asyncio.create_task(historian.research_history(topic))
papers_task = asyncio.create_task(scholar.research_whitepapers(topic))
news_task = asyncio.create_task(journalist.research_news(topic))
books_task = asyncio.create_task(bibliophile.research_books(topic))

# Wait for all to complete
results = await asyncio.gather(
    history_task,
    papers_task,
    news_task,
    books_task
)
```

**Benefits**:
- 3-4x faster than sequential execution
- Better resource utilization
- Independent failure (one task failing doesn't block others)

---

## Tool System

### WebSearchTool

**Location**: `tools/web_search.py`

**Supported Backends**:
1. **DuckDuckGo** (Primary, Free)
   - No API key required
   - Good quality results
   - Rate limited

2. **Serper** (Google Search, Paid)
   - Google search results
   - High quality
   - Requires API key

3. **Brave Search** (Paid)
   - Privacy-focused
   - Good quality
   - Requires API key

4. **Tavily** (Paid)
   - Optimized for AI/LLM use
   - High quality
   - Requires API key

**Fallback Chain**:
```
Try DuckDuckGo
  ├─> Success: Return results
  └─> Failure: Try Serper
        ├─> Success: Return results
        └─> Failure: Try next backend...
```

**Academic Search**:
```python
# Search Semantic Scholar
results = web_search.search_academic("machine learning")

# Search arXiv
results = web_search._search_arxiv("neural networks")
```

**News Search**:
```python
# Search recent news (last 7 days)
results = web_search.search_news("AI regulation", days_back=7)
```

### URLTracker

**Location**: `tools/url_tracker.py`

**Features**:
- URL deduplication using MD5 hashing
- Automatic categorization (webpage, PDF, academic paper, etc.)
- HTTP validation (check if URL is accessible)
- Status tracking (pending, valid, broken)
- Metadata extraction (content-type, status code)

**URL Types**:
```python
class URLType(Enum):
    WEBPAGE = "webpage"
    PDF = "pdf"
    ACADEMIC_PAPER = "academic_paper"
    NEWS_ARTICLE = "news_article"
    BOOK = "book"
    VIDEO = "video"
    API = "api"
    UNKNOWN = "unknown"
```

**Validation**:
```python
# Add URLs
tracker.add_url("https://example.com/paper.pdf", url_type=URLType.PDF)

# Validate all (makes HTTP HEAD requests)
await tracker.validate_all()

# Get broken links
broken = tracker.get_by_status(URLStatus.BROKEN)
```

**Export**:
```python
# Export as markdown table
markdown_table = tracker.export_markdown_table()

# Export as JSON
json_data = tracker.export_json()
```

---

## CLI Interface

### CLI Architecture

```
┌──────────────────────────────────────┐
│         Click Framework              │
│    (Command Routing)                 │
└──────────┬───────────────────────────┘
           │
           ├─> research
           ├─> show-config
           ├─> test-providers
           └─> init-config
                    │
                    ▼
         ┌──────────────────────┐
         │    Rich Console      │
         │ (Formatting & UI)    │
         └──────────────────────┘
```

### Commands

#### 1. research

```bash
python -m cli.main research "Topic" [OPTIONS]
```

**Options**:
- `--config, -c PATH`: Configuration file path
- `--output, -o PATH`: Output file path
- `--no-hil`: Disable Human-in-the-Loop mode

**Flow**:
1. Load configuration
2. Display research panel
3. Initialize orchestrator
4. Run research workflow (with optional HIL checkpoints)
5. Save report
6. Display summary

#### 2. show-config

```bash
python -m cli.main show-config [--config PATH]
```

Displays:
- LLM provider configuration
- Agent assignments
- Research parameters
- Output settings

#### 3. test-providers

```bash
python -m cli.main test-providers [--config PATH]
```

Tests all configured LLM providers:
- Connection test
- Simple inference test
- Response time measurement
- Error reporting

#### 4. init-config

```bash
python -m cli.main init-config [OUTPUT_PATH]
```

Creates a default configuration file with:
- All supported providers
- Default agent assignments
- Standard research parameters

### UI Components

**Panels**: Used for important messages
```python
console.print(Panel.fit(
    f"Research Topic: {topic}\nConfiguration: {config_path}",
    border_style="cyan"
))
```

**Progress**: For long-running operations
```python
with Progress() as progress:
    task = progress.add_task("Running research...", total=100)
    # ... work ...
    progress.update(task, advance=20)
```

**Tables**: For structured data display
```python
table = Table(title="LLM Providers")
table.add_column("Provider")
table.add_column("Model")
table.add_column("Status")
console.print(table)
```

---

## Data Flow

### Research Workflow Data Flow

```
1. User Input (Topic)
   │
   ▼
2. Configuration Loading
   │
   ▼
3. Orchestrator Initialization
   │
   ├─> LLMFactory creates agent LLMs
   └─> KnowledgeStore initialized
   │
   ▼
4. Coordinator Planning
   │
   └─> Stored in KnowledgeStore
   │
   ▼
5. TrendScout Research
   │
   ├─> Uses Perplexity (web search)
   ├─> Extracts trends
   └─> Stored in KnowledgeStore
   │
   ▼
6. Parallel Research (4 agents)
   │
   ├─> Historian ────> Perplexity ────> KnowledgeStore
   ├─> Scholar ─────> Claude ────────> KnowledgeStore
   ├─> Journalist ──> Perplexity ────> KnowledgeStore
   └─> Bibliophile ─> Claude ────────> KnowledgeStore
   │
   ▼
7. Reporter Synthesis
   │
   ├─> Reads all documents from KnowledgeStore
   ├─> Uses Claude Opus for synthesis
   ├─> Generates markdown report
   └─> Extracts and validates URLs
   │
   ▼
8. Output
   │
   ├─> Markdown report saved to file
   ├─> KnowledgeStore exported to JSON
   └─> Summary displayed in CLI
```

### URL Flow

```
1. Agent produces text with URLs
   │
   ▼
2. _extract_urls() extracts URLs via regex
   │
   ▼
3. URLTracker.add_url() stores each URL
   │
   ├─> Deduplication (MD5 hash)
   ├─> Categorization (URL pattern matching)
   └─> Metadata storage
   │
   ▼
4. URLTracker.validate_all() validates URLs
   │
   ├─> HTTP HEAD request
   ├─> Status code check
   └─> Content-type extraction
   │
   ▼
5. ReporterAgent includes URLs in report
   │
   └─> Generated as markdown reference tables
```

---

## Configuration System

### Configuration Hierarchy

```
1. Default Configuration (hardcoded in code)
   │
   ▼
2. Config File (YAML)
   │
   ├─> Loaded from --config flag
   └─> Merged with defaults
   │
   ▼
3. Environment Variables
   │
   ├─> API keys (${OPENAI_API_KEY})
   └─> Expanded at runtime
   │
   ▼
4. CLI Flags (highest priority)
   │
   └─> Override config file values
```

### Configuration Schema

```yaml
# LLM Provider Configuration
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
      num_ctx: 8192

    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        fast: "gpt-3.5-turbo"
        standard: "gpt-4"
        powerful: "gpt-4-turbo"
      default_temperature: 0.1
      max_tokens: 4096

    claude:
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        standard: "claude-3-sonnet-20240229"
        powerful: "claude-3-opus-20240229"
      default_temperature: 0.1
      max_tokens: 4096

    perplexity:
      api_key: "${PERPLEXITY_API_KEY}"
      models:
        standard: "llama-3.1-sonar-large-128k-online"
      search_recency_filter: "month"

# Agent Configuration
agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1"
    temperature: 0.1

  trend_scout:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    temperature: 0.3

  historian:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"

  scholar:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    fallback_provider: "openai"
    fallback_model: "gpt-4"

  journalist:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"

  bibliophile:
    provider: "claude"
    model: "claude-3-sonnet-20240229"

  reporter:
    provider: "claude"
    model: "claude-3-opus-20240229"

# Research Parameters
research:
  max_iterations: 3
  parallel_execution: true
  enable_citations: true

  trend_scout:
    max_trends: 5
    min_impact_score: 6
    recency_filter: "month"

  historian:
    time_periods: ["origins", "evolution", "milestones", "recent"]
    min_sources: 5

  scholar:
    min_papers: 5
    max_papers: 15
    sources: ["google_scholar", "arxiv", "semantic_scholar"]
    min_citations: 10

  journalist:
    min_articles: 10
    max_articles: 25
    days_back: 90
    sources: ["news", "industry", "blogs"]

  bibliophile:
    min_books: 5
    max_books: 10
    include_chapters: true
    min_rating: 3.5

# Output Configuration
output:
  format: "markdown"
  include_metadata: true
  include_urls: true
  include_statistics: true
  url_validation: true

# Logging Configuration
logging:
  level: "INFO"
  console: true
  file: "./logs/cardinal_biggles.log"
  rotation: "1 day"
  retention: "7 days"
```

---

## Error Handling & Resilience

### Error Handling Strategy

1. **Provider Fallback**:
```python
try:
    llm = factory.create_llm(provider="claude")
except Exception as e:
    logger.warning(f"Primary provider failed: {e}")
    llm = factory.create_llm(provider=fallback_provider)
```

2. **Graceful Degradation**:
```python
try:
    results = await search_tool.search(query)
except Exception as e:
    logger.error(f"Search failed: {e}")
    results = []  # Continue with empty results
```

3. **Retry Logic**:
```python
for attempt in range(max_retries):
    try:
        response = await llm.ainvoke(messages)
        break
    except RateLimitError:
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

4. **Validation**:
```python
# URL validation with error recovery
try:
    response = requests.head(url, timeout=5)
    status = response.status_code
except requests.RequestException as e:
    status = URLStatus.BROKEN
```

### Logging Strategy

**Log Levels**:
- `DEBUG`: Detailed tracing (development)
- `INFO`: Normal operations (production default)
- `WARNING`: Recoverable errors (fallbacks, retries)
- `ERROR`: Serious errors (failures)
- `CRITICAL`: System-level failures

**Log Structure**:
```python
logger.info(
    "Research phase complete",
    extra={
        "phase": "trend_scouting",
        "agent": "trend_scout_1",
        "duration_seconds": 45.2,
        "results_count": 5
    }
)
```

---

## Performance Optimization

### Parallel Execution

**Agent-Level Parallelism**:
- Phases 3-6 run concurrently
- 4 agents working simultaneously
- 3-4x speedup vs sequential

**Tool-Level Parallelism**:
- Web searches in parallel
- URL validation in parallel

### Caching

**LLM Response Caching**:
- LangChain built-in caching
- Reduces redundant API calls
- Especially useful for repeated queries

**Web Search Caching**:
- Cache search results (optional)
- Configurable TTL (time-to-live)

### Resource Management

**Connection Pooling**:
- HTTP connection reuse
- Reduces latency

**Memory Management**:
- Documents stored in-memory during research
- Optional persistence to disk
- Embeddings computed on-demand

### Cost Optimization

**Model Selection**:
- Use cheaper models for simple tasks
- Use expensive models only for critical tasks

**Token Optimization**:
- Concise system prompts
- Limit output length where appropriate
- Avoid redundant context

---

## Security Considerations

### API Key Management

**Environment Variables**:
```bash
# .env file (not committed to git)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
```

**Variable Expansion**:
```yaml
# Config file
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"  # Expanded at runtime
```

### URL Validation

**Domain Filtering**:
```python
# Exclude malicious domains
excluded_domains = ["malicious.com", "spam.net"]
if any(domain in url for domain in excluded_domains):
    return URLStatus.BLOCKED
```

**HTTP Validation**:
- Validate URLs before including in reports
- Check status codes
- Identify broken links

### Input Sanitization

**Query Sanitization**:
```python
# Remove potentially harmful characters
safe_query = re.sub(r'[^\w\s\-]', '', query)
```

### Rate Limiting

**Provider Rate Limits**:
- Respect API rate limits
- Implement exponential backoff
- Distribute load across providers

---

## Extension Points

### Adding a New Agent

1. **Create Agent Class**:
```python
from agents.base_agent import ResearchAgent

class CustomAgent(ResearchAgent):
    def get_system_prompt(self) -> str:
        return """You are a custom research agent..."""

    async def custom_research(self, topic: str):
        task = f"Research {topic} with custom approach"
        return await self.execute_task(task)
```

2. **Add to Configuration**:
```yaml
agents:
  custom_agent:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
```

3. **Initialize in Orchestrator**:
```python
custom_agent = CustomAgent(
    agent_id="custom_1",
    role="custom",
    llm=self.llm_factory.create_agent_llm("custom_agent"),
    knowledge_store=self.knowledge_store
)
```

4. **Integrate in Workflow**:
```python
custom_results = await custom_agent.custom_research(topic)
```

### Adding a New LLM Provider

1. **Add Provider Configuration**:
```yaml
providers:
  new_provider:
    api_key: "${NEW_PROVIDER_API_KEY}"
    models:
      standard: "model-name"
```

2. **Implement Factory Method**:
```python
def _create_new_provider(self, model: str, **kwargs):
    from langchain_new_provider import ChatNewProvider
    return ChatNewProvider(
        api_key=self.config["providers"]["new_provider"]["api_key"],
        model=model,
        **kwargs
    )
```

3. **Add to Factory Router**:
```python
def create_llm(self, provider: str, model: str, **kwargs):
    if provider == "new_provider":
        return self._create_new_provider(model, **kwargs)
    # ... existing providers ...
```

### Adding a New Tool

1. **Create Tool Class**:
```python
class CustomTool:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def custom_operation(self, input_data: str):
        # Tool implementation
        return result
```

2. **Integrate in Agent**:
```python
class CustomAgent(ResearchAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.custom_tool = CustomTool(config)

    async def custom_research(self, topic: str):
        tool_result = await self.custom_tool.custom_operation(topic)
        # Use tool result in research
```

### Adding a New Document Type

1. **Add to Enum**:
```python
class DocumentType(Enum):
    # ... existing types ...
    CUSTOM_TYPE = "custom_type"
```

2. **Store Documents**:
```python
self.knowledge_store.add_document(
    content=result,
    source=self.agent_id,
    document_type=DocumentType.CUSTOM_TYPE
)
```

3. **Query Documents**:
```python
custom_docs = knowledge_store.get_by_type(DocumentType.CUSTOM_TYPE)
```

---

## Conclusion

Cardinal Biggles is built on a **modular, extensible architecture** that separates concerns, enables parallel execution, and provides multiple layers of abstraction.

**Key Architectural Strengths**:
1. **Modularity**: Components can be replaced independently
2. **Extensibility**: Easy to add new agents, providers, tools
3. **Resilience**: Fallbacks and error recovery at all levels
4. **Performance**: Parallel execution and caching
5. **Observability**: Comprehensive logging and progress tracking
6. **Flexibility**: Configuration-driven behavior

**Design Trade-offs**:
1. **Complexity vs. Flexibility**: More components = more flexibility but more complexity
2. **Cost vs. Quality**: Cloud APIs = better quality but higher cost
3. **Speed vs. Thoroughness**: Parallel execution = faster but potentially less coherent
4. **Privacy vs. Performance**: Local models = privacy but slower

This architecture enables Cardinal Biggles to conduct comprehensive, multi-source research efficiently while remaining flexible, extensible, and maintainable.

---

**For more information**:
- [User Manual](USER_MANUAL.md) - End-user documentation
- [Local Setup Guide](LOCAL_SETUP.md) - Running with Ollama
- [Development Guide](../CLAUDE.md) - Code-level documentation
- [README](../README.md) - Project overview

---

*Last Updated: 2025-10-14*
*Cardinal Biggles - Multi-Agent Research Orchestration System*
