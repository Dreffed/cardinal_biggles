"""
Pytest configuration and shared fixtures for Cardinal Biggles
"""

import pytest
import asyncio
import os
from pathlib import Path
from typing import Dict, Any
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Session-level fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config_dir(tmp_path_factory):
    """Create temporary config directory"""
    config_dir = tmp_path_factory.mktemp("config")
    return config_dir


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create temporary data directory"""
    data_dir = tmp_path_factory.mktemp("data")
    return data_dir


# ============================================================================
# Configuration fixtures
# ============================================================================

@pytest.fixture
def basic_config(test_config_dir) -> Dict[str, Any]:
    """Basic configuration for testing"""
    return {
        'llm': {
            'default_provider': 'ollama',
            'default_model': 'llama3.1',
            'providers': {
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'models': {
                        'fast': 'llama3.1:8b',
                        'standard': 'llama3.1',
                        'powerful': 'llama3.1:70b'
                    },
                    'default_temperature': 0.1,
                    'timeout': 120
                }
            }
        },
        'agents': {
            'test_agent': {
                'provider': 'ollama',
                'model': 'llama3.1',
                'temperature': 0.1
            }
        },
        'research': {
            'test_agent': {
                'max_results': 5
            }
        },
        'output': {
            'default_format': 'markdown',
            'output_directory': './reports'
        },
        'logging': {
            'level': 'INFO',
            'console': False,
            'file': './logs/test.log'
        }
    }


@pytest.fixture
def config_file(basic_config, test_config_dir):
    """Create a config file for testing"""
    import yaml

    config_path = test_config_dir / "test_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(basic_config, f)

    return str(config_path)


# ============================================================================
# Mock LLM fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Mock LLM that returns predefined responses"""
    mock = AsyncMock()

    async def mock_invoke(messages):
        # Return mock response
        response = Mock()
        response.content = "This is a mock response from the LLM."
        return response

    mock.ainvoke = mock_invoke
    return mock


@pytest.fixture
def mock_llm_with_responses():
    """Mock LLM with customizable responses"""
    class MockLLMWithResponses:
        def __init__(self):
            self.responses = []
            self.call_count = 0

        def add_response(self, response: str):
            self.responses.append(response)

        async def ainvoke(self, messages):
            if self.call_count < len(self.responses):
                content = self.responses[self.call_count]
            else:
                content = "Default mock response"

            self.call_count += 1

            response = Mock()
            response.content = content
            return response

        def reset(self):
            self.call_count = 0

    return MockLLMWithResponses()


# ============================================================================
# Knowledge Store fixtures
# ============================================================================

@pytest.fixture
async def knowledge_store(test_data_dir):
    """Create a test knowledge store"""
    from core.knowledge_store import SimpleKnowledgeStore

    store = SimpleKnowledgeStore(
        persist_path=str(test_data_dir / "test_knowledge.json"),
        auto_save=False,
        enable_embeddings=False
    )

    yield store

    # Cleanup
    store.clear()


@pytest.fixture
async def populated_knowledge_store(knowledge_store):
    """Knowledge store with sample data"""
    from core.knowledge_store import DocumentType

    # Add sample documents
    await knowledge_store.add_document(
        content="Multi-agent systems are AI systems with multiple agents.",
        source="test_agent",
        document_type=DocumentType.RESEARCH_FINDING,
        tags=["ai", "multi-agent"]
    )

    await knowledge_store.add_document(
        content="LangChain is a framework for LLM applications.",
        source="test_agent",
        document_type=DocumentType.RESEARCH_FINDING,
        tags=["langchain", "llm"]
    )

    await knowledge_store.add_document(
        content="Vector databases enable semantic search.",
        source="research_agent",
        document_type=DocumentType.WEB_CONTENT,
        tags=["vector-db", "search"]
    )

    return knowledge_store


# ============================================================================
# URL Tracker fixtures
# ============================================================================

@pytest.fixture
def url_tracker():
    """Create a test URL tracker"""
    from tools.url_tracker import URLTracker

    tracker = URLTracker(
        validate_urls=False,  # Don't validate during tests
        auto_categorize=True
    )

    return tracker


@pytest.fixture
def populated_url_tracker(url_tracker):
    """URL tracker with sample data"""
    urls = [
        "https://arxiv.org/abs/2103.00020",
        "https://techcrunch.com/ai-news",
        "https://www.amazon.com/ai-book",
        "https://example.com/research.pdf"
    ]

    for url in urls:
        url_tracker.add_url(
            url=url,
            title=f"Document from {url}",
            source_agent="test_agent",
            tags=["test"]
        )

    return url_tracker


# ============================================================================
# Web Search fixtures
# ============================================================================

@pytest.fixture
def mock_search_results():
    """Mock search results"""
    from tools.web_search import SearchResult

    return [
        SearchResult(
            title="Test Result 1",
            url="https://example.com/1",
            snippet="This is a test result about AI agents.",
            source="test",
            relevance_score=0.9
        ),
        SearchResult(
            title="Test Result 2",
            url="https://example.com/2",
            snippet="Another test result about multi-agent systems.",
            source="test",
            relevance_score=0.8
        )
    ]


@pytest.fixture
def mock_web_search_tool(mock_search_results):
    """Mock web search tool"""
    from tools.web_search import WebSearchTool

    tool = WebSearchTool()

    # Replace search method with mock
    async def mock_search(query):
        return mock_search_results

    tool.search = mock_search
    return tool


# ============================================================================
# Agent fixtures
# ============================================================================

@pytest.fixture
async def base_agent(mock_llm, knowledge_store):
    """Create a base test agent"""
    from agents.base_agent import ResearchAgent

    class TestAgent(ResearchAgent):
        def get_system_prompt(self) -> str:
            return "You are a test agent."

    agent = TestAgent(
        agent_id="test_agent",
        role="test",
        llm=mock_llm,
        knowledge_store=knowledge_store
    )

    return agent


@pytest.fixture
def mock_agent_llm():
    """Mock LLM for agent testing with URL support"""
    from unittest.mock import AsyncMock, Mock

    llm = AsyncMock()
    response = Mock()
    response.content = "Mock LLM response"
    llm.ainvoke = AsyncMock(return_value=response)
    return llm


@pytest.fixture
def test_agent(mock_agent_llm, knowledge_store):
    """Create a test agent instance for unit tests"""
    from agents.base_agent import ResearchAgent

    class ConcreteTestAgent(ResearchAgent):
        def get_system_prompt(self) -> str:
            return "Test agent for testing purposes"

    return ConcreteTestAgent(
        agent_id="test_agent",
        role="tester",
        llm=mock_agent_llm,
        knowledge_store=knowledge_store
    )


@pytest.fixture
async def populated_agent_store(knowledge_store):
    """Knowledge store with agent-generated documents"""
    from core.knowledge_store import DocumentType

    await knowledge_store.add_document(
        content="Agent research finding 1",
        source="test_agent",
        document_type=DocumentType.AGENT_OUTPUT,
        tags=["test", "research"]
    )
    await knowledge_store.add_document(
        content="Agent research finding 2",
        source="test_agent",
        document_type=DocumentType.AGENT_OUTPUT,
        tags=["test", "analysis"]
    )

    return knowledge_store


# ============================================================================
# Markers and conditional skips
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


@pytest.fixture
def skip_if_no_ollama():
    """Skip test if Ollama is not running"""
    import socket

    def check():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()
            if result != 0:
                pytest.skip("Ollama is not running on localhost:11434")
        except Exception:
            pytest.skip("Cannot connect to Ollama")

    return check


@pytest.fixture
def skip_if_no_api_key():
    """Skip test if required API keys are not set"""
    def check(provider: str):
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'perplexity': 'PERPLEXITY_API_KEY'
        }

        env_var = key_map.get(provider.lower())
        if not env_var or not os.getenv(env_var):
            pytest.skip(f"API key for {provider} not set")

    return check


# ============================================================================
# Cleanup fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test"""
    yield

    # Remove temporary test files
    temp_files = [
        "test_knowledge_store.json",
        "url_tracking.json"
    ]

    for file in temp_files:
        if Path(file).exists():
            Path(file).unlink()


@pytest.fixture
def temp_dir():
    """Create and cleanup temporary directory"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)
