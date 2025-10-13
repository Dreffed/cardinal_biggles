"""
Tests for URL Tracker
"""

import pytest


@pytest.mark.unit
class TestURLTracker:
    """Test URL Tracker functionality"""

    def test_add_url(self, url_tracker):
        """Test adding a URL"""
        tracked = url_tracker.add_url(
            url="https://example.com/test",
            title="Test Page",
            source_agent="test_agent"
        )

        assert tracked is not None
        assert tracked.url == "https://example.com/test"
        assert len(url_tracker.urls) == 1

    def test_duplicate_url(self, url_tracker):
        """Test duplicate URL handling"""
        url = "https://example.com/test"

        url_tracker.add_url(url, source_agent="test_agent")
        url_tracker.add_url(url, source_agent="test_agent")

        assert len(url_tracker.urls) == 1
        assert url_tracker.stats['duplicates_found'] == 1

    def test_url_categorization(self, url_tracker):
        """Test automatic URL categorization"""
        from tools.url_tracker import URLType

        # Academic URL
        tracked = url_tracker.add_url(
            "https://arxiv.org/abs/2103.00020",
            source_agent="test"
        )
        assert tracked.url_type == URLType.ACADEMIC_PAPER

        # News URL
        tracked = url_tracker.add_url(
            "https://techcrunch.com/article",
            source_agent="test"
        )
        assert tracked.url_type == URLType.NEWS_ARTICLE

        # PDF
        tracked = url_tracker.add_url(
            "https://example.com/document.pdf",
            source_agent="test"
        )
        assert tracked.url_type == URLType.PDF

    def test_get_by_domain(self, populated_url_tracker):
        """Test getting URLs by domain"""
        urls = populated_url_tracker.get_by_domain("arxiv.org")

        assert len(urls) > 0
        assert all(url.domain == "arxiv.org" for url in urls)

    def test_get_by_agent(self, populated_url_tracker):
        """Test getting URLs by agent"""
        urls = populated_url_tracker.get_by_agent("test_agent")

        assert len(urls) > 0
        assert all(url.source_agent == "test_agent" for url in urls)

    def test_get_by_type(self, populated_url_tracker):
        """Test getting URLs by type"""
        from tools.url_tracker import URLType

        urls = populated_url_tracker.get_by_type(URLType.ACADEMIC_PAPER)

        assert len(urls) > 0
        assert all(url.url_type == URLType.ACADEMIC_PAPER for url in urls)

    def test_export_markdown_table(self, populated_url_tracker):
        """Test markdown table export"""
        table = populated_url_tracker.export_markdown_table()

        assert "| Title |" in table
        assert "| URL |" in table
        assert len(table.split('\n')) > 3

    def test_export_json(self, populated_url_tracker, temp_dir):
        """Test JSON export"""
        export_path = temp_dir / "urls.json"

        json_str = populated_url_tracker.export_json(str(export_path))

        assert export_path.exists()
        assert len(json_str) > 0
        assert '"urls"' in json_str

    def test_statistics(self, populated_url_tracker):
        """Test statistics generation"""
        stats = populated_url_tracker.get_statistics()

        assert 'total_urls' in stats
        assert stats['total_urls'] > 0
        assert 'by_type' in stats
        assert 'domains' in stats

    @pytest.mark.asyncio
    @pytest.mark.requires_network
    async def test_url_validation(self, url_tracker):
        """Test URL validation"""
        from tools.url_tracker import URLStatus

        url_tracker.validate_urls = True

        # Add a valid URL
        tracked = url_tracker.add_url(
            "https://www.python.org",
            source_agent="test"
        )

        # Validate
        await url_tracker.validate_all()

        # Check status
        assert tracked.status in [URLStatus.VALID, URLStatus.UNREACHABLE]
        assert tracked.validated_at is not None
