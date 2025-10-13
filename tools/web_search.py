"""
Web Search Tool for Cardinal Biggles
Supports multiple search backends with fallback mechanisms
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import logging
from datetime import datetime
from urllib.parse import quote_plus
import json

logger = logging.getLogger(__name__)


class SearchBackend(Enum):
    """Supported search backends"""
    DUCKDUCKGO = "duckduckgo"
    SERPER = "serper"
    BRAVE = "brave"
    TAVILY = "tavily"


@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchQuery:
    """Structured search query"""
    query: str
    max_results: int = 10
    search_type: str = "general"  # general, news, academic, images
    time_range: Optional[str] = None  # day, week, month, year
    domain_filter: Optional[List[str]] = None
    language: str = "en"
    safe_search: bool = True


class WebSearchTool:
    """
    Unified web search tool supporting multiple backends
    """

    def __init__(
        self,
        primary_backend: SearchBackend = SearchBackend.DUCKDUCKGO,
        fallback_backends: List[SearchBackend] = None,
        api_keys: Dict[str, str] = None,
        timeout: int = 30
    ):
        self.primary_backend = primary_backend
        self.fallback_backends = fallback_backends or [SearchBackend.DUCKDUCKGO]
        self.api_keys = api_keys or {}
        self.timeout = timeout

        # Import search libraries as needed
        self._setup_backends()

    def _setup_backends(self):
        """Initialize search backend clients"""
        try:
            from duckduckgo_search import DDGS
            self.ddgs_client = DDGS()
        except ImportError:
            logger.warning("duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            self.ddgs_client = None

    async def search(self, query: Union[str, SearchQuery]) -> List[SearchResult]:
        """
        Perform web search with automatic fallback

        Args:
            query: Search query string or SearchQuery object

        Returns:
            List of SearchResult objects
        """
        # Convert string to SearchQuery if needed
        if isinstance(query, str):
            query = SearchQuery(query=query)

        logger.info(f"Searching for: {query.query} (backend: {self.primary_backend.value})")

        # Try primary backend
        try:
            results = await self._search_with_backend(query, self.primary_backend)
            if results:
                logger.info(f"Found {len(results)} results with {self.primary_backend.value}")
                return results
        except Exception as e:
            logger.warning(f"Primary backend {self.primary_backend.value} failed: {e}")

        # Try fallback backends
        for backend in self.fallback_backends:
            if backend == self.primary_backend:
                continue

            try:
                logger.info(f"Trying fallback backend: {backend.value}")
                results = await self._search_with_backend(query, backend)
                if results:
                    logger.info(f"Found {len(results)} results with fallback {backend.value}")
                    return results
            except Exception as e:
                logger.warning(f"Fallback backend {backend.value} failed: {e}")

        logger.error("All search backends failed")
        return []

    async def _search_with_backend(
        self,
        query: SearchQuery,
        backend: SearchBackend
    ) -> List[SearchResult]:
        """Execute search with specific backend"""

        if backend == SearchBackend.DUCKDUCKGO:
            return await self._search_duckduckgo(query)
        elif backend == SearchBackend.SERPER:
            return await self._search_serper(query)
        elif backend == SearchBackend.BRAVE:
            return await self._search_brave(query)
        elif backend == SearchBackend.TAVILY:
            return await self._search_tavily(query)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    async def _search_duckduckgo(self, query: SearchQuery) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        if not self.ddgs_client:
            raise RuntimeError("DuckDuckGo client not initialized")

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()

            # Choose search method based on type
            if query.search_type == "news":
                raw_results = await loop.run_in_executor(
                    None,
                    lambda: list(self.ddgs_client.news(
                        query.query,
                        max_results=query.max_results,
                        timelimit=query.time_range
                    ))
                )
            else:
                raw_results = await loop.run_in_executor(
                    None,
                    lambda: list(self.ddgs_client.text(
                        query.query,
                        max_results=query.max_results,
                        timelimit=query.time_range,
                        safesearch='on' if query.safe_search else 'off'
                    ))
                )

            # Convert to SearchResult objects
            results = []
            for idx, item in enumerate(raw_results):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('href', item.get('url', '')),
                    snippet=item.get('body', item.get('snippet', '')),
                    source='duckduckgo',
                    published_date=item.get('date'),
                    relevance_score=1.0 - (idx * 0.05),  # Simple relevance decay
                    metadata={'raw': item}
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            raise

    async def _search_serper(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Serper API"""
        api_key = self.api_keys.get('serper')
        if not api_key:
            raise ValueError("Serper API key not provided")

        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'q': query.query,
            'num': query.max_results,
            'gl': query.language
        }

        # Add time range if specified
        if query.time_range:
            time_map = {
                'day': 'd',
                'week': 'w',
                'month': 'm',
                'year': 'y'
            }
            payload['tbs'] = f"qdr:{time_map.get(query.time_range, 'm')}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Serper API error: {response.status}")

                data = await response.json()

                results = []
                for idx, item in enumerate(data.get('organic', [])):
                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        snippet=item.get('snippet', ''),
                        source='serper',
                        relevance_score=item.get('position', idx + 1),
                        metadata={'raw': item}
                    )
                    results.append(result)

                return results

    async def _search_brave(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Brave Search API"""
        api_key = self.api_keys.get('brave')
        if not api_key:
            raise ValueError("Brave API key not provided")

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            'X-Subscription-Token': api_key,
            'Accept': 'application/json'
        }

        params = {
            'q': query.query,
            'count': query.max_results,
            'safesearch': 'strict' if query.safe_search else 'off'
        }

        # Add time filter if specified
        if query.time_range:
            time_map = {
                'day': 'pd',
                'week': 'pw',
                'month': 'pm',
                'year': 'py'
            }
            params['freshness'] = time_map.get(query.time_range)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Brave API error: {response.status}")

                data = await response.json()

                results = []
                for idx, item in enumerate(data.get('web', {}).get('results', [])):
                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        snippet=item.get('description', ''),
                        source='brave',
                        published_date=item.get('age'),
                        relevance_score=1.0 - (idx * 0.05),
                        metadata={'raw': item}
                    )
                    results.append(result)

                return results

    async def _search_tavily(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Tavily API"""
        api_key = self.api_keys.get('tavily')
        if not api_key:
            raise ValueError("Tavily API key not provided")

        url = "https://api.tavily.com/search"

        payload = {
            'api_key': api_key,
            'query': query.query,
            'max_results': query.max_results,
            'search_depth': 'advanced' if query.search_type == 'academic' else 'basic',
            'include_domains': query.domain_filter if query.domain_filter else []
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Tavily API error: {response.status}")

                data = await response.json()

                results = []
                for idx, item in enumerate(data.get('results', [])):
                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        snippet=item.get('content', ''),
                        source='tavily',
                        relevance_score=item.get('score', 1.0 - (idx * 0.05)),
                        metadata={'raw': item}
                    )
                    results.append(result)

                return results

    async def search_academic(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search for academic papers using specialized sources

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of SearchResult objects
        """
        results = []

        # Try Semantic Scholar
        try:
            semantic_results = await self._search_semantic_scholar(query, max_results)
            results.extend(semantic_results)
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed: {e}")

        # Try arXiv if results are insufficient
        if len(results) < max_results:
            try:
                arxiv_results = await self._search_arxiv(query, max_results - len(results))
                results.extend(arxiv_results)
            except Exception as e:
                logger.warning(f"arXiv search failed: {e}")

        return results[:max_results]

    async def _search_semantic_scholar(self, query: str, max_results: int) -> List[SearchResult]:
        """Search Semantic Scholar API"""
        url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,abstract,authors,year,url,citationCount,venue'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"Semantic Scholar API error: {response.status}")

                data = await response.json()

                results = []
                for item in data.get('data', []):
                    authors = ', '.join([a.get('name', '') for a in item.get('authors', [])])

                    result = SearchResult(
                        title=item.get('title', ''),
                        url=item.get('url', f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}"),
                        snippet=item.get('abstract', '')[:500] if item.get('abstract') else '',
                        source='semantic_scholar',
                        published_date=str(item.get('year', '')),
                        relevance_score=min(1.0, item.get('citationCount', 0) / 100),
                        metadata={
                            'authors': authors,
                            'citations': item.get('citationCount', 0),
                            'venue': item.get('venue', '')
                        }
                    )
                    results.append(result)

                return results

    async def _search_arxiv(self, query: str, max_results: int) -> List[SearchResult]:
        """Search arXiv API"""
        url = "http://export.arxiv.org/api/query"

        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(f"arXiv API error: {response.status}")

                import xml.etree.ElementTree as ET
                xml_data = await response.text()
                root = ET.fromstring(xml_data)

                # Parse arXiv Atom feed
                ns = {'atom': 'http://www.w3.org/2005/Atom'}

                results = []
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns)
                    summary = entry.find('atom:summary', ns)
                    link = entry.find('atom:id', ns)
                    published = entry.find('atom:published', ns)

                    authors = entry.findall('atom:author', ns)
                    author_names = [a.find('atom:name', ns).text for a in authors if a.find('atom:name', ns) is not None]

                    result = SearchResult(
                        title=title.text.strip() if title is not None else '',
                        url=link.text if link is not None else '',
                        snippet=summary.text.strip()[:500] if summary is not None else '',
                        source='arxiv',
                        published_date=published.text[:10] if published is not None else None,
                        metadata={
                            'authors': ', '.join(author_names)
                        }
                    )
                    results.append(result)

                return results


# Convenience function
async def search_web(
    query: str,
    max_results: int = 10,
    backend: str = "duckduckgo",
    api_keys: Dict[str, str] = None
) -> List[SearchResult]:
    """
    Simple web search function

    Args:
        query: Search query
        max_results: Maximum results to return
        backend: Search backend to use
        api_keys: API keys for paid backends

    Returns:
        List of SearchResult objects
    """
    tool = WebSearchTool(
        primary_backend=SearchBackend[backend.upper()],
        api_keys=api_keys or {}
    )

    search_query = SearchQuery(query=query, max_results=max_results)
    return await tool.search(search_query)


# Example usage
if __name__ == "__main__":
    async def main():
        # Example 1: Simple search
        results = await search_web("multi-agent AI systems 2025", max_results=5)

        for result in results:
            print(f"\nTitle: {result.title}")
            print(f"URL: {result.url}")
            print(f"Snippet: {result.snippet[:100]}...")

        # Example 2: Advanced search with custom query
        tool = WebSearchTool()

        query = SearchQuery(
            query="machine learning papers",
            max_results=10,
            search_type="academic",
            time_range="year"
        )

        results = await tool.search(query)
        print(f"\nFound {len(results)} results")

        # Example 3: Academic search
        academic_results = await tool.search_academic(
            "transformer neural networks",
            max_results=5
        )

        for result in academic_results:
            print(f"\nPaper: {result.title}")
            print(f"Authors: {result.metadata.get('authors', 'Unknown')}")
            print(f"URL: {result.url}")

    asyncio.run(main())
