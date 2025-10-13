# Cardinal Biggles - System Architecture

**Version**: 1.0
**Last Updated**: 2025-01-13

---

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Agent Architecture](#agent-architecture)
5. [Communication Patterns](#communication-patterns)
6. [Storage Architecture](#storage-architecture)
7. [Scalability Considerations](#scalability-considerations)
8. [Security Architecture](#security-architecture)

---

## 1. Overview

Cardinal Biggles is a multi-agent research orchestration system built on an event-driven, async-first architecture. The system coordinates specialized AI agents to conduct comprehensive research across multiple domains.

### Architectural Principles

1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Loose Coupling**: Agents communicate through standardized interfaces
3. **Async-First**: All I/O operations are non-blocking
4. **Configuration-Driven**: Behavior controlled via YAML configuration
5. **Extensible**: New agents, tools, and providers easily added

---

## 2. System Components

### 2.1 Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     CLI      │  │   REST API   │  │    Web UI    │     │
│  │   (Click)    │  │  (FastAPI)   │  │   (React)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Orchestration Layer                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │         ResearchOrchestrator                       │    │
│  │  - Workflow coordination                           │    │
│  │  - Agent lifecycle management                      │    │
│  │  - Result aggregation                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         LLMFactory                                 │    │
│  │  - Multi-provider LLM instantiation                │    │
│  │  - Configuration management                        │    │
│  │  - Fallback handling                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         HILController (v0.2.0)                     │    │
│  │  - Human-in-the-Loop checkpoints                   │    │
│  │  - Interactive approval workflow                   │    │
│  │  - User action handling (A/E/R/S/Q)                │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      Agent Layer                             │
│  ┌──────────┐  ┌───────────┐  ┌────────┐  ┌──────────┐   │
│  │Coordinator│  │TrendScout │  │Historian│ │ Scholar  │   │
│  │          │  │           │  │        │  │          │   │
│  │(Ollama)  │  │(Perplexity)│ │(Pplx)  │  │(Claude)  │   │
│  └──────────┘  └───────────┘  └────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌───────────┐  ┌────────────────────────┐ │
│  │Journalist│  │Bibliophile│  │      Reporter          │ │
│  │(Pplx)    │  │(Claude)   │  │    (Claude Opus)       │ │
│  └──────────┘  └───────────┘  └────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                       Tool Layer                             │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────────┐   │
│  │WebSearch  │  │URLTracker │  │  KnowledgeStore      │   │
│  │- DuckDuck │  │- Dedup    │  │  - Documents         │   │
│  │- Semantic │  │- Validate │  │  - Search            │   │
│  │- arXiv    │  │- Categorize│ │  - Persistence       │   │
│  └───────────┘  └───────────┘  └──────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    External Services                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Ollama  │  │  OpenAI  │  │  Claude  │  │Perplexity│  │
│  │  (Local) │  │   (API)  │  │   (API)  │  │   (API)  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │DuckDuckGo│  │ Semantic │  │  arXiv   │                 │
│  │          │  │ Scholar  │  │          │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| **CLI** | User interaction, command parsing | Click, Rich |
| **ResearchOrchestrator** | Agent coordination, workflow execution | LLMFactory, Agents |
| **LLMFactory** | LLM instantiation, configuration | LangChain providers |
| **HILController** | Human-in-the-Loop workflow management | Rich (UI), asyncio |
| **Agents** | Specialized research tasks | LLMs, Tools, KnowledgeStore |
| **WebSearchTool** | Web search across multiple backends | aiohttp, duckduckgo-search |
| **URLTracker** | URL management, validation | aiohttp |
| **KnowledgeStore** | Document storage, retrieval | JSON/ChromaDB |

---

## 3. Data Flow

### 3.1 Request Flow

```text
User Input
    │
    ├─> CLI Parser
    │       │
    │       ├─> Command Validation
    │       └─> Parameter Extraction
    │
    ├─> ResearchOrchestrator
    │       │
    │       ├─> Load Configuration
    │       ├─> Initialize LLMFactory
    │       └─> Initialize Agents
    │
    ├─> Workflow Execution
    │       │
    │       ├─> Phase 1: Trend Scouting (Sequential)
    │       │       └─> TrendScout Agent
    │       │               ├─> Web Search
    │       │               ├─> LLM Analysis
    │       │               └─> Store Results
    │       │
    │       ├─> [CHECKPOINT 1: Trend Review] (if HIL enabled)
    │       │       ├─> Display trends to user
    │       │       ├─> Wait for approval (A/E/R/S/Q)
    │       │       └─> Process user action
    │       │
    │       ├─> Phase 2-5: Research (Parallel)
    │       │       ├─> Historian Agent
    │       │       ├─> Scholar Agent
    │       │       ├─> Journalist Agent
    │       │       └─> Bibliophile Agent
    │       │           (Each agent follows same pattern)
    │       │
    │       ├─> [CHECKPOINT 2: Research Review] (if HIL enabled)
    │       │       ├─> Display research summary
    │       │       ├─> Wait for approval
    │       │       └─> Process user action
    │       │
    │       ├─> Phase 6: Report Generation (Sequential)
    │       │       └─> Reporter Agent
    │       │               ├─> Aggregate Results
    │       │               ├─> Synthesize Findings
    │       │               └─> Generate Markdown
    │       │
    │       └─> [CHECKPOINT 3: Report Review] (if HIL enabled)
    │               ├─> Display report preview
    │               ├─> Wait for approval
    │               └─> Process user action
    │
    └─> Output
            ├─> Save Report File
            ├─> Display Summary
            └─> Export Reference Tables
```

### 3.2 Agent Execution Pattern

```text
Agent.execute_task(task, context)
    │
    ├─> 1. Prepare Context
    │       ├─> Load from KnowledgeStore
    │       ├─> Format dependencies
    │       └─> Build prompt
    │
    ├─> 2. Tool Invocation (if needed)
    │       ├─> WebSearch for information
    │       ├─> URLTracker to store URLs
    │       └─> Cache results
    │
    ├─> 3. LLM Invocation
    │       ├─> Build message array
    │       │   ├─> System Prompt
    │       │   ├─> Context (if any)
    │       │   └─> User Task
    │       │
    │       ├─> Call LLM.ainvoke()
    │       └─> Parse response
    │
    ├─> 4. Post-Processing
    │       ├─> Extract URLs
    │       ├─> Parse structured data
    │       └─> Validate output
    │
    ├─> 5. Storage
    │       ├─> Store in KnowledgeStore
    │       ├─> Update agent memory
    │       └─> Track URLs
    │
    └─> 6. Return Result
            └─> Structured Dict with metadata
```

### 3.3 Information Flow Between Agents

```text
User Query: "Research Multi-Agent AI Systems"
    │
    ▼
┌─────────────────────────────────────┐
│  Phase 1: TREND SCOUTING            │
│  Agent: TrendScout                  │
│  Input: Raw query                   │
│  Output: Top 3-5 trends identified  │
└─────────────────┬───────────────────┘
                  │
                  ├─> KnowledgeStore (stores findings)
                  │
                  ├─> URLTracker (collects URLs)
                  │
                  ▼
    ┌─────────────────────────────────┐
    │ Extract Top Trend:              │
    │ "Multi-Agent Orchestration"     │
    └─────────────┬───────────────────┘
                  │
    ┌─────────────┴─────────────────────────────────┐
    │                                               │
    ▼                                               ▼
┌───────────────────┐                    ┌──────────────────┐
│ Phase 2: HISTORY  │                    │ Phase 3: ACADEMIC│
│ Agent: Historian  │                    │ Agent: Scholar   │
│ Input: Top trend  │                    │ Input: Top trend │
│ + Context         │                    │ + Context        │
│ Output: Timeline  │                    │ Output: Papers   │
└─────────┬─────────┘                    └────────┬─────────┘
          │                                       │
          ├─> KnowledgeStore                     ├─> KnowledgeStore
          ├─> URLTracker                         ├─> URLTracker
          │                                      │
    ▼                                      ▼
┌───────────────────┐                    ┌──────────────────┐
│ Phase 4: NEWS     │                    │ Phase 5: BOOKS   │
│ Agent: Journalist │                    │ Agent: Bibliophile│
│ Input: Top trend  │                    │ Input: Top trend │
│ + Context         │                    │ + Context        │
│ Output: Articles  │                    │ Output: Books    │
└─────────┬─────────┘                    └────────┬─────────┘
          │                                       │
          └───────────────┬───────────────────────┘
                          │
                          ▼
            ┌──────────────────────────────┐
            │  All agents write to:        │
            │  - KnowledgeStore (findings) │
            │  - URLTracker (sources)      │
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌───────────────────────────────────┐
            │  Phase 6: SYNTHESIS               │
            │  Agent: Reporter                  │
            │  Input: All accumulated findings  │
            │  - Read from KnowledgeStore       │
            │  - Read from URLTracker           │
            │  Output: Comprehensive report     │
            └───────────────────────────────────┘
```

---

## 4. Agent Architecture

### 4.1 Agent Lifecycle

```text
Initialization
    │
    ├─> Load Configuration
    │       └─> Get agent-specific settings
    │
    ├─> Create LLM Instance
    │       ├─> Determine provider (Ollama/OpenAI/Claude/Perplexity)
    │       ├─> Load model
    │       └─> Set parameters (temperature, etc.)
    │
    ├─> Initialize Tools
    │       ├─> WebSearch
    │       ├─> URLTracker
    │       └─> Custom tools (agent-specific)
    │
    ├─> Setup Memory
    │       └─> ConversationBufferMemory (last 10 exchanges)
    │
    └─> Register with Orchestrator

Task Execution (see 3.2 above)

Shutdown
    │
    ├─> Flush Memory
    ├─> Close Connections
    └─> Save State (if persistent)
```

### 4.2 Agent Communication

**Direct Communication** (not implemented yet):

```python
# Future feature
await agent1.send_message(agent2, "Need clarification on X")
response = await agent1.wait_for_response(agent2)
```

**Indirect Communication** (current):

```python
# Via Knowledge Store
await agent1.knowledge_store.add_document(finding)
results = await agent2.knowledge_store.search(query)
```

### 4.3 Agent State Management

```text
Agent State:
    ├─> agent_id: Unique identifier
    ├─> role: Agent's role/specialization
    ├─> llm: LLM instance
    ├─> knowledge_store: Shared store reference
    ├─> tools: Available tools
    ├─> memory: Conversation history (last 10)
    └─> metadata: Custom agent data

State Persistence:
    └─> Currently: In-memory only
    └─> Future: Redis/Database backing
```

---

## 5. Communication Patterns

### 5.1 Synchronous vs Asynchronous

**Synchronous Operations**:

- Configuration loading
- Agent initialization
- Local data transformations
- In-memory operations

**Asynchronous Operations**:

- All LLM API calls
- Web searches
- URL validation
- File I/O operations
- Network requests

### 5.2 Parallel Execution Pattern

```python
# Research phases 2-5 execute in parallel
results = await asyncio.gather(
    historian.research_history(trend),
    scholar.research_whitepapers(trend),
    journalist.research_news(trend),
    bibliophile.research_books(trend),
    return_exceptions=True  # Don't fail all if one fails
)

# Process results
for result in results:
    if isinstance(result, Exception):
        logger.error(f"Agent failed: {result}")
    else:
        # Process successful result
        pass
```

### 5.3 Error Propagation

```text
Agent Error
    │
    ├─> Try Primary LLM Provider
    │       └─> Failed?
    │           └─> Try Fallback Provider
    │               └─> Failed?
    │                   └─> Raise LLMProviderError
    │
    ├─> Caught by Orchestrator
    │       └─> Log error
    │       └─> Continue with other agents
    │           (don't fail entire workflow)
    │
    └─> Report Generation
            └─> Note failures in report
            └─> Generate partial results
```

---

## 6. Storage Architecture

### 6.1 Knowledge Store Architecture

```text
SimpleKnowledgeStore (Current)
    │
    ├─> In-Memory Storage
    │       ├─> documents: Dict[str, Document]
    │       ├─> Index by source
    │       ├─> Index by type
    │       └─> Index by tags
    │
    ├─> Search Methods
    │       ├─> Text-based (keyword matching)
    │       └─> Semantic (with embeddings)
    │
    ├─> Persistence
    │       └─> JSON file
    │           ├─> Save on each operation (auto_save)
    │           └─> Load on initialization
    │
    └─> Scalability Limit
            └─> ~10,000 documents

ChromaDB/Qdrant (Future)
    │
    ├─> Vector Database
    │       ├─> Efficient similarity search
    │       └─> Scalable to millions of documents
    │
    ├─> Built-in Embeddings
    │       └─> Automatic vectorization
    │
    └─> Advanced Features
            ├─> Filtering
            ├─> Metadata queries
            └─> Hybrid search
```

### 6.2 Data Persistence Strategy

```text
Development Mode:
    └─> JSON files (simple, easy to debug)
        └─> ./data/knowledge_store.json

Production Mode:
    ├─> Primary: Vector Database (ChromaDB/Qdrant)
    │       └─> For semantic search
    │
    ├─> Secondary: PostgreSQL + pgvector
    │       └─> For relational queries
    │
    └─> Cache: Redis
            └─> For frequently accessed data
```

### 6.3 URL Tracking Storage

```text
URLTracker:
    ├─> In-Memory Indices
    │       ├─> urls: Dict[hash, TrackedURL]
    │       ├─> by_domain: Dict[domain, List[hash]]
    │       ├─> by_agent: Dict[agent_id, List[hash]]
    │       └─> by_type: Dict[URLType, List[hash]]
    │
    └─> Export Formats
            ├─> JSON (programmatic access)
            └─> Markdown (human-readable)
```

---

## 7. Scalability Considerations

### 7.1 Current Limitations

| Component | Current Limit | Bottleneck |
|-----------|--------------|------------|
| Knowledge Store | ~10K docs | In-memory storage |
| Concurrent Agents | 10 parallel | asyncio limitations |
| URL Tracking | ~1K URLs | In-memory storage |
| Report Size | ~100 pages | LLM context window |

### 7.2 Horizontal Scaling Strategy

```text
Single Instance (Current):
    └─> One orchestrator
        └─> All agents in one process
        └─> Shared memory

Multi-Instance (Future):
    ├─> Load Balancer
    │       └─> Distribute requests
    │
    ├─> Multiple Orchestrator Instances
    │       ├─> Instance 1: Topic A
    │       ├─> Instance 2: Topic B
    │       └─> Instance 3: Topic C
    │
    ├─> Shared Services
    │       ├─> Redis (caching)
    │       ├─> PostgreSQL (relational data)
    │       └─> ChromaDB (vector search)
    │
    └─> Message Queue (RabbitMQ/Kafka)
            └─> Agent task distribution
```

### 7.3 Vertical Scaling Strategy

```text
Resource Allocation:
    ├─> CPU
    │       └─> Parallel agent execution
    │           └─> asyncio.gather() with worker pool
    │
    ├─> Memory
    │       └─> Knowledge store size
    │           └─> Implement memory-mapped files
    │
    └─> I/O
            └─> Async operations
            └─> Connection pooling
```

---

## 8. Security Architecture

### 8.1 Authentication & Authorization

```text
Current (Development):
    └─> No authentication
        └─> Local execution only

Future (Production):
    ├─> User Authentication
    │       ├─> JWT tokens
    │       └─> OAuth 2.0
    │
    ├─> API Key Management
    │       ├─> Encrypted storage
    │       └─> Key rotation
    │
    └─> Role-Based Access Control (RBAC)
            ├─> Admin: Full access
            ├─> Researcher: Execute workflows
            └─> Viewer: Read reports only
```

### 8.2 Data Security

```text
Secrets Management:
    ├─> Development
    │       └─> .env file (not committed)
    │
    └─> Production
            ├─> AWS Secrets Manager
            ├─> HashiCorp Vault
            └─> Azure Key Vault

Data Encryption:
    ├─> At Rest
    │       └─> Encrypted database files
    │
    └─> In Transit
            └─> TLS 1.3 for all API calls
```

### 8.3 Input Validation

```text
Validation Layers:
    ├─> CLI Input
    │       ├─> Command validation
    │       └─> Parameter sanitization
    │
    ├─> Agent Tasks
    │       ├─> Task description validation
    │       └─> Context sanitization
    │
    └─> Tool Inputs
            ├─> URL validation
            ├─> Query sanitization
            └─> File path validation
```

---

## 9. Monitoring & Observability

### 9.1 Logging Architecture

```text
Application Logs:
    ├─> Development
    │       ├─> Console output (colorized)
    │       └─> File: ./logs/cardinal.log
    │
    └─> Production
            ├─> Structured JSON logs
            ├─> Centralized: ELK Stack / CloudWatch
            └─> Log levels: DEBUG, INFO, WARN, ERROR

Metrics Collection:
    ├─> Application Metrics
    │       ├─> Request count
    │       ├─> Response time
    │       ├─> Error rate
    │       └─> Agent execution time
    │
    └─> System Metrics
            ├─> CPU usage
            ├─> Memory usage
            └─> Disk I/O
```

### 9.2 Tracing

```text
LangSmith Integration:
    └─> Trace each agent execution
        ├─> LLM calls
        ├─> Token usage
        ├─> Latency
        └─> Cost tracking
```

---

## 10. Future Architecture Enhancements

### Phase 2 (Q2 2025)

- REST API layer
- WebSocket for real-time updates
- Async task queue (Celery/RQ)

### Phase 3 (Q3 2025)

- Microservices architecture
- Agent containerization (Docker)
- Kubernetes orchestration

### Phase 4 (Q4 2025)

- Multi-tenant support
- Global agent marketplace
- Edge deployment capabilities

---
