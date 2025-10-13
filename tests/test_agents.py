"""
Tests for Research Agents
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime


@pytest.mark.unit
class TestResearchAgent:
    """Test base ResearchAgent functionality"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        llm = AsyncMock()
        # Mock response object
        response = Mock()
        response.content = "Test response from LLM"
        llm.ainvoke = AsyncMock(return_value=response)
        return llm

    @pytest.fixture
    def mock_knowledge_store(self):
        """Mock knowledge store for testing"""
        store = AsyncMock()
        store.add_document = AsyncMock(return_value="doc-123")
        return store

    @pytest.fixture
    def concrete_agent(self, mock_llm, mock_knowledge_store):
        """Create a concrete implementation of ResearchAgent for testing"""
        from agents.base_agent import ResearchAgent

        class TestAgent(ResearchAgent):
            def get_system_prompt(self) -> str:
                return "You are a test agent."

        return TestAgent(
            agent_id="test_agent_1",
            role="test_agent",
            llm=mock_llm,
            knowledge_store=mock_knowledge_store
        )

    @pytest.mark.asyncio
    async def test_agent_initialization(self, concrete_agent):
        """Test agent initializes with correct attributes"""
        assert concrete_agent.agent_id == "test_agent_1"
        assert concrete_agent.role == "test_agent"
        assert concrete_agent.llm is not None
        assert concrete_agent.knowledge_store is not None
        assert isinstance(concrete_agent.memory, list)
        assert len(concrete_agent.memory) == 0

    @pytest.mark.asyncio
    async def test_execute_task_basic(self, concrete_agent, mock_llm):
        """Test basic task execution"""
        task = "Analyze this topic"

        result = await concrete_agent.execute_task(task)

        # Verify LLM was called
        assert mock_llm.ainvoke.called

        # Verify result structure
        assert isinstance(result, dict)
        assert "agent_id" in result
        assert "role" in result
        assert "task" in result
        assert "result" in result
        assert "timestamp" in result
        assert "urls" in result
        assert "knowledge_doc_id" in result

        # Verify values
        assert result["agent_id"] == "test_agent_1"
        assert result["role"] == "test_agent"
        assert result["task"] == task
        assert result["result"] == "Test response from LLM"
        assert result["knowledge_doc_id"] == "doc-123"

    @pytest.mark.asyncio
    async def test_execute_task_with_context(self, concrete_agent, mock_llm):
        """Test task execution with context"""
        task = "Analyze this topic"
        context = {
            "previous_finding": "Important data",
            "trends": ["trend1", "trend2"]
        }

        result = await concrete_agent.execute_task(task, context=context)

        # Verify LLM was called with context
        assert mock_llm.ainvoke.called
        call_args = mock_llm.ainvoke.call_args[0][0]

        # Should have 3 messages: system, context, task
        assert len(call_args) == 3

        # Verify context was formatted correctly
        context_message = call_args[1]
        assert "Context from previous research:" in context_message.content
        assert "previous_finding" in context_message.content
        assert "trends" in context_message.content

    @pytest.mark.asyncio
    async def test_store_knowledge_called(self, concrete_agent, mock_knowledge_store):
        """Test that _store_knowledge is called with correct parameters - CRITICAL TEST"""
        from core.knowledge_store import DocumentType

        task = "Test task"
        result = await concrete_agent.execute_task(task)

        # Verify add_document was called with correct parameters
        assert mock_knowledge_store.add_document.called

        call_kwargs = mock_knowledge_store.add_document.call_args[1]

        # Verify all required parameters are present
        assert "content" in call_kwargs
        assert "source" in call_kwargs              # TESTS THE FIX
        assert "document_type" in call_kwargs       # TESTS THE FIX

        # Verify parameter values
        assert call_kwargs["source"] == "test_agent_1"
        assert call_kwargs["document_type"] == DocumentType.AGENT_OUTPUT
        assert "metadata" in call_kwargs

        # Verify metadata structure
        metadata = call_kwargs["metadata"]
        assert "agent_id" in metadata
        assert "role" in metadata
        assert "timestamp" in metadata
        assert "urls" in metadata

        # Verify tags were added
        assert "tags" in call_kwargs
        assert "test_agent" in call_kwargs["tags"]
        assert "research" in call_kwargs["tags"]

    @pytest.mark.asyncio
    async def test_extract_urls(self, concrete_agent):
        """Test URL extraction from content"""
        content = """
        Check out these resources:
        https://example.com/article
        http://research.org/paper.pdf
        Visit https://github.com/project for code
        """

        urls = concrete_agent._extract_urls(content)

        assert len(urls) == 3
        assert "https://example.com/article" in urls
        assert "http://research.org/paper.pdf" in urls
        assert "https://github.com/project" in urls

    @pytest.mark.asyncio
    async def test_extract_urls_none_found(self, concrete_agent):
        """Test URL extraction when no URLs present"""
        content = "This text has no URLs"

        urls = concrete_agent._extract_urls(content)

        assert len(urls) == 0
        assert isinstance(urls, list)

    @pytest.mark.asyncio
    async def test_format_context_dict(self, concrete_agent):
        """Test context formatting with dict values"""
        context = {
            "key1": "value1",
            "key2": "value2"
        }

        formatted = concrete_agent._format_context(context)

        assert "key1: value1" in formatted
        assert "key2: value2" in formatted

    @pytest.mark.asyncio
    async def test_format_context_list(self, concrete_agent):
        """Test context formatting with list values"""
        context = {
            "trends": ["trend1", "trend2", "trend3"]
        }

        formatted = concrete_agent._format_context(context)

        assert "trends:" in formatted
        assert "trend1" in formatted
        assert "trend2" in formatted
        assert "trend3" in formatted

    @pytest.mark.asyncio
    async def test_memory_storage(self, concrete_agent):
        """Test that results are stored in agent memory"""
        task1 = "First task"
        task2 = "Second task"

        result1 = await concrete_agent.execute_task(task1)
        result2 = await concrete_agent.execute_task(task2)

        # Verify memory contains both results
        assert len(concrete_agent.memory) == 2
        assert concrete_agent.memory[0]["task"] == task1
        assert concrete_agent.memory[1]["task"] == task2

    @pytest.mark.asyncio
    async def test_timestamp_format(self, concrete_agent):
        """Test that timestamp is in ISO format"""
        result = await concrete_agent.execute_task("Test")

        timestamp = result["timestamp"]

        # Verify ISO format by parsing
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    @pytest.mark.asyncio
    async def test_urls_included_in_result(self, concrete_agent, mock_llm):
        """Test that URLs from LLM response are extracted and included"""
        # Mock LLM to return content with URLs
        response = Mock()
        response.content = "Check https://example.com and http://test.org"
        mock_llm.ainvoke = AsyncMock(return_value=response)

        result = await concrete_agent.execute_task("Test")

        assert "urls" in result
        assert len(result["urls"]) == 2
        assert "https://example.com" in result["urls"]
        assert "http://test.org" in result["urls"]


@pytest.mark.integration
class TestResearchAgentIntegration:
    """Integration tests with real knowledge store"""

    @pytest.fixture
    def real_knowledge_store(self):
        """Create a real knowledge store for integration testing"""
        from core.knowledge_store import SimpleKnowledgeStore
        return SimpleKnowledgeStore(
            persist_path=None,  # Don't persist
            auto_save=False,
            enable_embeddings=False
        )

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for integration tests"""
        llm = AsyncMock()
        response = Mock()
        response.content = "Integration test response with https://example.com"
        llm.ainvoke = AsyncMock(return_value=response)
        return llm

    @pytest.fixture
    def test_agent(self, mock_llm, real_knowledge_store):
        """Create test agent with real knowledge store"""
        from agents.base_agent import ResearchAgent

        class TestAgent(ResearchAgent):
            def get_system_prompt(self) -> str:
                return "Test agent system prompt"

        return TestAgent(
            agent_id="integration_test_agent",
            role="test",
            llm=mock_llm,
            knowledge_store=real_knowledge_store
        )

    @pytest.mark.asyncio
    async def test_full_workflow(self, test_agent, real_knowledge_store):
        """Test complete workflow: execute task -> store knowledge -> retrieve - CRITICAL TEST"""
        from core.knowledge_store import DocumentType

        # Execute task
        result = await test_agent.execute_task("Analyze integration testing")

        # Verify document was stored
        docs = real_knowledge_store.get_by_source("integration_test_agent")
        assert len(docs) == 1

        doc = docs[0]
        assert doc.document_type == DocumentType.AGENT_OUTPUT
        assert doc.source == "integration_test_agent"
        assert "Integration test response" in doc.content

        # Verify metadata
        assert "agent_id" in doc.metadata
        assert doc.metadata["agent_id"] == "integration_test_agent"
        assert "urls" in doc.metadata
        assert "https://example.com" in doc.metadata["urls"]

        # Verify tags
        assert "test" in doc.tags
        assert "research" in doc.tags

    @pytest.mark.asyncio
    async def test_multiple_tasks_storage(self, test_agent, real_knowledge_store):
        """Test that multiple tasks are all stored correctly"""
        from core.knowledge_store import DocumentType

        tasks = [
            "Task 1: Analyze trends",
            "Task 2: Research papers",
            "Task 3: Synthesize findings"
        ]

        for task in tasks:
            await test_agent.execute_task(task)

        # Verify all documents were stored
        docs = real_knowledge_store.get_by_source("integration_test_agent")
        assert len(docs) == 3

        # Verify all are agent outputs
        for doc in docs:
            assert doc.document_type == DocumentType.AGENT_OUTPUT
            assert doc.source == "integration_test_agent"

    @pytest.mark.asyncio
    async def test_search_stored_knowledge(self, test_agent, real_knowledge_store):
        """Test that stored knowledge is searchable"""
        await test_agent.execute_task("Research machine learning algorithms")

        # Search for the stored content (using words that appear in the mock response)
        results = await real_knowledge_store.search(
            query="Integration test response",
            max_results=5
        )

        assert len(results) > 0
        assert "Integration test response" in results[0].content


@pytest.mark.unit
class TestSpecificAgents:
    """Test specific agent implementations"""

    @pytest.mark.asyncio
    async def test_scholar_agent_system_prompt(self):
        """Test ScholarAgent has appropriate system prompt"""
        from agents.scholar import ScholarAgent
        from core.knowledge_store import SimpleKnowledgeStore

        store = SimpleKnowledgeStore(persist_path=None, auto_save=False)
        agent = ScholarAgent(
            agent_id="scholar_1",
            role="scholar",
            llm=AsyncMock(),
            knowledge_store=store
        )

        prompt = agent.get_system_prompt()

        assert "Scholar Agent" in prompt
        assert "academic" in prompt.lower() or "paper" in prompt.lower()
        assert len(prompt) > 100  # Should be comprehensive

    @pytest.mark.asyncio
    async def test_reporter_agent_system_prompt(self):
        """Test ReporterAgent has appropriate system prompt"""
        from agents.reporter import ReporterAgent
        from core.knowledge_store import SimpleKnowledgeStore

        store = SimpleKnowledgeStore(persist_path=None, auto_save=False)
        agent = ReporterAgent(
            agent_id="reporter_1",
            role="reporter",
            llm=AsyncMock(),
            knowledge_store=store
        )

        prompt = agent.get_system_prompt()

        assert "Reporter Agent" in prompt
        assert "report" in prompt.lower() or "synthesis" in prompt.lower()
        assert "Executive Summary" in prompt
