# Cardinal Biggles - Technical Specification v1.0

**Project Name**: Cardinal Biggles
**Type**: Multi-Agent AI Research Orchestration System
**Language**: Python 3.9+
**Architecture**: Multi-Agent, Event-Driven, Async-First
**Last Updated**: 2025-01-13

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Agent Specifications](#agent-specifications)
5. [Data Models](#data-models)
6. [API Contracts](#api-contracts)
7. [Configuration System](#configuration-system)
8. [Testing Strategy](#testing-strategy)
9. [Extension Points](#extension-points)
10. [Performance Requirements](#performance-requirements)

---

## 1. Executive Summary

### Purpose

Cardinal Biggles is a multi-agent AI system that conducts comprehensive research on any topic by orchestrating specialized agents, each with distinct roles and LLM providers.

### Key Features

- **Multi-Provider LLM Support**: Ollama, OpenAI, Claude, Perplexity
- **Specialized Agents**: 7 agents (Coordinator, TrendScout, Historian, Scholar, Journalist, Bibliophile, Reporter)
- **Knowledge Management**: Persistent knowledge store with semantic search
- **URL Tracking**: Automatic URL collection, validation, deduplication
- **Report Generation**: Comprehensive markdown reports with citations

### Technology Stack

```yaml
Language: Python 3.9+
Core Framework: LangChain 0.1+
Async Runtime: asyncio
LLM Providers:
  - langchain-ollama (local models)
  - langchain-openai (GPT-3.5, GPT-4)
  - langchain-anthropic (Claude)
  - langchain-community (Perplexity)
Storage:
  - JSON (development)
  - ChromaDB (optional, semantic search)
CLI: Click + Rich
Testing: pytest + pytest-asyncio
```

---

## 2. System Architecture

### 2.1 High-Level Architecture

```text
CLI Layer (Click + Rich UI)
    ↓
Orchestrator Layer (ResearchOrchestrator)
    ↓
Agent Layer (7 specialized agents)
    ↓
Tool Layer (WebSearch, URLTracker, KnowledgeStore)
```

### 2.2 Execution Flow

```text
1. User Input (CLI)
2. Orchestrator initializes agents with LLM providers
3. Coordinator Agent receives task
4. Phase 1: TrendScout identifies trends
5. Phase 2-5: Parallel execution
   - Historian (historical context)
   - Scholar (academic papers)
   - Journalist (news articles)
   - Bibliophile (books)
6. Phase 6: Reporter synthesizes findings
7. Output: Markdown report with reference tables
```

---

## 3. Core Components

### 3.1 LLM Factory

**Purpose**: Multi-provider LLM instantiation with configuration management

**Contract**:

```python
class LLMFactory:
    def __init__(self, config_path: str)
    def create_llm(provider: str, model: str, temperature: float) -> LLM
    def create_agent_llm(agent_name: str) -> LLM
    def get_research_config(agent_name: str) -> Dict
```

### 3.2 Knowledge Store

**Purpose**: Persistent storage and retrieval of research findings

**Contract**:

```python
class SimpleKnowledgeStore:
    async def add_document(content: str, source: str, document_type: DocumentType) -> str
    async def search(query: str, max_results: int) -> List[Document]
    def get_by_source(source: str) -> List[Document]
```

### 3.3 Web Search Tool

**Purpose**: Multi-backend web search with automatic fallback

**Backend Support**:

- DuckDuckGo (primary, free)
- Serper (Google proxy, paid)
- Semantic Scholar (academic)
- arXiv (academic)

### 3.4 URL Tracker

**Purpose**: URL collection, validation, deduplication

**Contract**:

```python
class URLTracker:
    def add_url(url: str, title: str, source_agent: str) -> Optional[TrackedURL]
    async def validate_all() -> None
    def export_markdown_table() -> str
```

---

## 4. Agent Specifications

### 4.1 Base Agent

**Abstract Base Class**: All agents inherit from `ResearchAgent`

**Required Methods**:

```python
class ResearchAgent(ABC):
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    async def execute_task(self, task_description: str, context: Dict) -> Dict:
        pass
```

### 4.2 Coordinator Agent

**Role**: Orchestrates research workflow across agents

### 4.3 TrendScout Agent

**Role**: Identify and analyze market trends
**Recommended Provider**: Perplexity

### 4.4 Historian Agent

**Role**: Research historical context and evolution
**Recommended Provider**: Perplexity or Claude

### 4.5 Scholar Agent

**Role**: Find and analyze academic papers
**Recommended Provider**: Claude

### 4.6 Journalist Agent

**Role**: Analyze news articles and current events
**Recommended Provider**: Perplexity

### 4.7 Bibliophile Agent

**Role**: Research and analyze books
**Recommended Provider**: Claude

### 4.8 Reporter Agent

**Role**: Synthesize all findings into comprehensive report
**Recommended Provider**: Claude Opus

---

## 5. Data Models

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

@dataclass
class SearchQuery:
    query: str
    max_results: int = 10
    search_type: str = "general"
    time_range: Optional[str] = None

@dataclass
class TrackedURL:
    url: str
    title: Optional[str] = None
    source_agent: Optional[str] = None
    url_type: URLType = URLType.WEBPAGE
    status: URLStatus = URLStatus.PENDING
```

---

## 6. API Contracts

### Agent Interface

All agents must implement:

- `get_system_prompt() -> str`
- `execute_task(task_description: str, context: Dict) -> Dict`

### Tool Interface

Tools provide specialized functionality via `execute(**kwargs) -> Any`

---

## 7. Configuration System

### Configuration Hierarchy

1. Default values (hardcoded)
2. config.yaml (file-based)
3. Environment variables
4. Command-line overrides

### Environment Variables

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 8. Testing Strategy

### Test Categories

- `@pytest.mark.unit` - Fast, no external dependencies
- `@pytest.mark.integration` - May use external services
- `@pytest.mark.slow` - Takes > 1 second
- `@pytest.mark.requires_ollama` - Needs Ollama running

### Coverage Requirements

- Minimum overall: 80%
- Core modules: 90%+
- Agents: 75%+

---

## 9. Extension Points

### Adding New Agents

1. Create new file inheriting from `ResearchAgent`
2. Implement `get_system_prompt()` method
3. Register in `orchestrator.py`
4. Add configuration in `config.yaml`
5. Write tests

### Adding New LLM Providers

1. Add provider config to `config.yaml`
2. Add creation method in `llm_factory.py`
3. Add tests
4. Update documentation

---

## 10. Performance Requirements

### Response Time Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| LLM Factory init | < 100ms | 500ms |
| Single agent task (Ollama) | < 5s | 30s |
| Full research workflow | < 10min | 30min |
| Knowledge store search | < 100ms | 1s |

### Resource Limits

- Memory: < 500MB base operation
- Disk: < 1GB per research session
- Concurrent Tasks: Max 10 parallel

---

## 11. Error Handling

### Error Categories

```python
class CardinalBigglesError(Exception): pass
class LLMProviderError(CardinalBigglesError): pass
class ConfigurationError(CardinalBigglesError): pass
class SearchError(CardinalBigglesError): pass
```

### Error Handling Strategy

1. Fail Fast - Validate inputs early
2. Graceful Degradation - Use fallback providers
3. Retry Logic - Exponential backoff
4. Comprehensive Logging
5. Clear error messages

---

## 12. Security Considerations

### API Key Management

- Store in environment variables
- Use .env file for local development
- Never commit keys to version control
- Never log keys

### Input Validation

- Sanitize all user inputs
- Validate URLs before fetching
- Limit file sizes
- Escape special characters

---

## 13. Development Workflow

### Git Workflow

```bash
git checkout -b feature/new-agent
pytest tests/
git commit -m "feat: add new agent for X"
git push origin feature/new-agent
```

### Commit Message Convention

```text
<type>(<scope>): <subject>

Types: feat, fix, docs, test, refactor, style, chore
```

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| Agent | Specialized AI component with specific role |
| LLM | Large Language Model |
| RAG | Retrieval-Augmented Generation |
| Orchestrator | System that coordinates multiple agents |
| Provider | LLM API provider |
| Embedding | Vector representation of text |

---
