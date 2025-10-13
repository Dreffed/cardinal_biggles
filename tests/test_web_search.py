"""
Tests for Web Search Tool
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock


@pytest.mark.unit
class TestWebSearchTool:
    """Test Web Search Tool"""

    def test_search_tool_initialization(self):
        """Test search tool initializes correctly"""
        from tools.web_search import WebSearchTool, SearchBackend

        tool = WebSearchTool(
            primary_backend=SearchBackend.DUCKDUCKGO
        )

        assert tool.primary_backend == SearchBackend.DUCKDUCKGO

    @pytest.mark.asyncio
    async def test_search_query_object(self):
        """Test SearchQuery object creation"""
        from tools.web_search import SearchQuery

        query = SearchQuery(
            query="test query",
            max_results=5,
            search_type="general"
        )

        assert query.query == "test query"
        assert query.max_results == 5
        assert query.search_type == "general"


@pytest.mark.integration
@pytest.mark.requires_network
class TestWebSearchIntegration:
    """Integration tests for web search"""

    @pytest.mark.asyncio
    async def test_duckduckgo_search(self):
        """Test actual DuckDuckGo search"""
        from tools.web_search import WebSearchTool, SearchQuery

        tool = WebSearchTool()

        query = SearchQuery(
            query="Python programming",
            max_results=3
        )

        results = await tool.search(query)

        assert len(results) > 0
        assert all(hasattr(r, 'title') for r in results)
        assert all(hasattr(r, 'url') for r in results)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_academic_search(self):
        """Test academic search (Semantic Scholar + arXiv)"""
        from tools.web_search import WebSearchTool

        tool = WebSearchTool()

        results = await tool.search_academic(
            query="machine learning",
            max_results=3
        )

        assert len(results) > 0
        # Check for academic-specific fields
        assert any(
            'semantic_scholar' in r.source or 'arxiv' in r.source
            for r in results
        )
