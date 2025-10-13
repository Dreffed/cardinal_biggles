"""
URL Tracker for Cardinal Biggles
Manages URL collection, validation, deduplication, and metadata
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from urllib.parse import urlparse, urljoin
from enum import Enum
import hashlib
import json
import asyncio
import aiohttp
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class URLStatus(Enum):
    """URL validation status"""
    VALID = "valid"
    INVALID = "invalid"
    UNREACHABLE = "unreachable"
    PENDING = "pending"
    EXCLUDED = "excluded"


class URLType(Enum):
    """Type of URL/resource"""
    WEBPAGE = "webpage"
    PDF = "pdf"
    ACADEMIC_PAPER = "academic_paper"
    NEWS_ARTICLE = "news_article"
    BOOK = "book"
    VIDEO = "video"
    API = "api"
    OTHER = "other"


@dataclass
class TrackedURL:
    """Tracked URL with metadata"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source_agent: Optional[str] = None
    url_type: URLType = URLType.WEBPAGE
    status: URLStatus = URLStatus.PENDING
    added_at: datetime = field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Computed fields
    domain: str = field(init=False)
    url_hash: str = field(init=False)

    def __post_init__(self):
        """Compute derived fields"""
        parsed = urlparse(self.url)
        self.domain = parsed.netloc
        self.url_hash = hashlib.md5(self.url.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert enums to strings
        data['url_type'] = self.url_type.value
        data['status'] = self.status.value
        # Convert datetime to ISO format
        data['added_at'] = self.added_at.isoformat()
        if self.validated_at:
            data['validated_at'] = self.validated_at.isoformat()
        return data


class URLTracker:
    """
    URL tracking and management system
    Handles deduplication, validation, categorization, and export
    """

    def __init__(
        self,
        validate_urls: bool = True,
        auto_categorize: bool = True,
        exclude_domains: List[str] = None,
        max_concurrent_validations: int = 10
    ):
        self.validate_urls = validate_urls
        self.auto_categorize = auto_categorize
        self.exclude_domains = set(exclude_domains or [])
        self.max_concurrent_validations = max_concurrent_validations

        # Storage
        self.urls: Dict[str, TrackedURL] = {}  # url_hash -> TrackedURL
        self.url_by_domain: Dict[str, List[str]] = {}  # domain -> [url_hashes]
        self.url_by_agent: Dict[str, List[str]] = {}  # agent_id -> [url_hashes]
        self.url_by_type: Dict[URLType, List[str]] = {t: [] for t in URLType}

        # Statistics
        self.stats = {
            'total_urls': 0,
            'valid_urls': 0,
            'invalid_urls': 0,
            'duplicates_found': 0,
            'domains': set()
        }

    def add_url(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        source_agent: Optional[str] = None,
        tags: List[str] = None,
        **metadata
    ) -> Optional[TrackedURL]:
        """
        Add a URL to tracking system

        Args:
            url: URL to track
            title: Optional title
            description: Optional description
            source_agent: Agent that found this URL
            tags: Optional tags
            **metadata: Additional metadata

        Returns:
            TrackedURL object if added, None if duplicate/excluded
        """
        # Clean URL
        url = self._clean_url(url)
        if not url:
            return None

        # Check if excluded
        if self._is_excluded(url):
            logger.debug(f"URL excluded: {url}")
            return None

        # Check for duplicates
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.urls:
            self.stats['duplicates_found'] += 1
            logger.debug(f"Duplicate URL: {url}")
            return self.urls[url_hash]

        # Create tracked URL
        tracked = TrackedURL(
            url=url,
            title=title,
            description=description,
            source_agent=source_agent,
            tags=tags or [],
            metadata=metadata
        )

        # Auto-categorize if enabled
        if self.auto_categorize:
            tracked.url_type = self._categorize_url(url)

        # Store
        self.urls[url_hash] = tracked

        # Index by domain
        if tracked.domain not in self.url_by_domain:
            self.url_by_domain[tracked.domain] = []
        self.url_by_domain[tracked.domain].append(url_hash)

        # Index by agent
        if source_agent:
            if source_agent not in self.url_by_agent:
                self.url_by_agent[source_agent] = []
            self.url_by_agent[source_agent].append(url_hash)

        # Index by type
        self.url_by_type[tracked.url_type].append(url_hash)

        # Update stats
        self.stats['total_urls'] += 1
        self.stats['domains'].add(tracked.domain)

        logger.info(f"Added URL: {url} (type: {tracked.url_type.value})")

        return tracked

    def add_urls_bulk(self, urls: List[str], **kwargs) -> List[TrackedURL]:
        """Add multiple URLs at once"""
        added = []
        for url in urls:
            tracked = self.add_url(url, **kwargs)
            if tracked:
                added.append(tracked)
        return added

    async def validate_all(self):
        """Validate all pending URLs"""
        if not self.validate_urls:
            logger.info("URL validation disabled")
            return

        pending_urls = [
            tracked for tracked in self.urls.values()
            if tracked.status == URLStatus.PENDING
        ]

        if not pending_urls:
            logger.info("No URLs to validate")
            return

        logger.info(f"Validating {len(pending_urls)} URLs...")

        # Validate in batches
        semaphore = asyncio.Semaphore(self.max_concurrent_validations)

        async def validate_with_semaphore(tracked: TrackedURL):
            async with semaphore:
                await self._validate_url(tracked)

        tasks = [validate_with_semaphore(t) for t in pending_urls]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Update stats
        self.stats['valid_urls'] = len([
            t for t in self.urls.values() if t.status == URLStatus.VALID
        ])
        self.stats['invalid_urls'] = len([
            t for t in self.urls.values() if t.status in [URLStatus.INVALID, URLStatus.UNREACHABLE]
        ])

        logger.info(f"Validation complete. Valid: {self.stats['valid_urls']}, Invalid: {self.stats['invalid_urls']}")

    async def _validate_url(self, tracked: TrackedURL):
        """Validate a single URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    tracked.url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    allow_redirects=True
                ) as response:
                    tracked.http_status = response.status
                    tracked.content_type = response.headers.get('Content-Type', '')

                    if 200 <= response.status < 400:
                        tracked.status = URLStatus.VALID
                    else:
                        tracked.status = URLStatus.INVALID

                    tracked.validated_at = datetime.now()

        except asyncio.TimeoutError:
            tracked.status = URLStatus.UNREACHABLE
            tracked.validated_at = datetime.now()
            logger.warning(f"URL timeout: {tracked.url}")
        except Exception as e:
            tracked.status = URLStatus.UNREACHABLE
            tracked.validated_at = datetime.now()
            logger.warning(f"URL validation error: {tracked.url} - {e}")

    def get_by_domain(self, domain: str) -> List[TrackedURL]:
        """Get all URLs from a specific domain"""
        url_hashes = self.url_by_domain.get(domain, [])
        return [self.urls[h] for h in url_hashes]

    def get_by_agent(self, agent_id: str) -> List[TrackedURL]:
        """Get all URLs found by a specific agent"""
        url_hashes = self.url_by_agent.get(agent_id, [])
        return [self.urls[h] for h in url_hashes]

    def get_by_type(self, url_type: URLType) -> List[TrackedURL]:
        """Get all URLs of a specific type"""
        url_hashes = self.url_by_type[url_type]
        return [self.urls[h] for h in url_hashes]

    def get_all_valid(self) -> List[TrackedURL]:
        """Get all valid URLs"""
        return [t for t in self.urls.values() if t.status == URLStatus.VALID]

    def get_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics"""
        stats = self.stats.copy()
        stats['domains'] = len(stats['domains'])

        # Add type breakdown
        stats['by_type'] = {
            url_type.value: len(url_hashes)
            for url_type, url_hashes in self.url_by_type.items()
        }

        # Add agent breakdown
        stats['by_agent'] = {
            agent: len(url_hashes)
            for agent, url_hashes in self.url_by_agent.items()
        }

        return stats

    def export_markdown_table(
        self,
        url_type: Optional[URLType] = None,
        agent_id: Optional[str] = None,
        status_filter: Optional[URLStatus] = None
    ) -> str:
        """
        Export URLs as Markdown table

        Args:
            url_type: Filter by type
            agent_id: Filter by agent
            status_filter: Filter by status

        Returns:
            Markdown table string
        """
        # Filter URLs
        urls = list(self.urls.values())

        if url_type:
            urls = [u for u in urls if u.url_type == url_type]
        if agent_id:
            urls = [u for u in urls if u.source_agent == agent_id]
        if status_filter:
            urls = [u for u in urls if u.status == status_filter]

        if not urls:
            return "No URLs found matching criteria."

        # Build table
        lines = [
            "| Title | Type | Source | URL | Status |",
            "|-------|------|--------|-----|--------|"
        ]

        for url in urls:
            title = url.title or url.url[:50]
            url_type_str = url.url_type.value
            source = url.source_agent or "unknown"
            status_icon = "✓" if url.status == URLStatus.VALID else "✗"

            lines.append(
                f"| {title} | {url_type_str} | {source} | [{url.url}]({url.url}) | {status_icon} |"
            )

        return "\n".join(lines)

    def export_json(self, filepath: Optional[str] = None) -> str:
        """Export all URLs to JSON"""
        data = {
            'urls': [url.to_dict() for url in self.urls.values()],
            'statistics': self.get_statistics(),
            'exported_at': datetime.now().isoformat()
        }

        json_str = json.dumps(data, indent=2)

        if filepath:
            Path(filepath).write_text(json_str)
            logger.info(f"Exported URLs to {filepath}")

        return json_str

    def _clean_url(self, url: str) -> Optional[str]:
        """Clean and normalize URL"""
        if not url:
            return None

        url = url.strip()

        # Remove markdown formatting
        url = url.replace('](', '').replace('[', '').replace(')', '')

        # Ensure scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Basic validation
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None

    def _is_excluded(self, url: str) -> bool:
        """Check if URL should be excluded"""
        parsed = urlparse(url)
        return parsed.netloc in self.exclude_domains

    def _categorize_url(self, url: str) -> URLType:
        """Automatically categorize URL by domain and extension"""
        url_lower = url.lower()
        parsed = urlparse(url_lower)
        domain = parsed.netloc

        # Academic domains
        academic_domains = [
            'arxiv.org', 'scholar.google', 'researchgate.net',
            'ieee.org', 'acm.org', 'springer.com', 'sciencedirect.com',
            'semanticscholar.org', 'pubmed.ncbi.nlm.nih.gov'
        ]
        if any(d in domain for d in academic_domains):
            return URLType.ACADEMIC_PAPER

        # News domains
        news_domains = [
            'nytimes.com', 'wsj.com', 'reuters.com', 'bloomberg.com',
            'techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com',
            'bbc.com', 'cnn.com', 'forbes.com'
        ]
        if any(d in domain for d in news_domains):
            return URLType.NEWS_ARTICLE

        # Book domains
        book_domains = [
            'amazon.com', 'goodreads.com', 'books.google',
            'oreilly.com', 'manning.com', 'packtpub.com'
        ]
        if any(d in domain for d in book_domains):
            return URLType.BOOK

        # Video domains
        video_domains = ['youtube.com', 'youtu.be', 'vimeo.com']
        if any(d in domain for d in video_domains):
            return URLType.VIDEO

        # Check file extension
        if url_lower.endswith('.pdf'):
            return URLType.PDF

        # Default
        return URLType.WEBPAGE


# Convenience function
def create_tracker(validate: bool = True) -> URLTracker:
    """Create a URL tracker with default settings"""
    return URLTracker(
        validate_urls=validate,
        auto_categorize=True,
        max_concurrent_validations=10
    )


# Example usage
if __name__ == "__main__":
    async def main():
        # Create tracker
        tracker = create_tracker(validate=True)

        # Add URLs
        urls = [
            "https://arxiv.org/abs/2103.00020",
            "https://techcrunch.com/ai-article",
            "https://www.amazon.com/book-title",
            "https://example.com/research.pdf",
            "https://example.com/research.pdf",  # Duplicate
        ]

        for url in urls:
            tracker.add_url(
                url,
                title=f"Document from {urlparse(url).netloc}",
                source_agent="test_agent",
                tags=["test"]
            )

        # Validate all URLs
        await tracker.validate_all()

        # Get statistics
        print("\nStatistics:")
        print(json.dumps(tracker.get_statistics(), indent=2))

        # Export as table
        print("\nMarkdown Table:")
        print(tracker.export_markdown_table())

        # Export to JSON
        tracker.export_json("url_tracking.json")

    asyncio.run(main())
