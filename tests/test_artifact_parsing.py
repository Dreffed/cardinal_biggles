"""
Tests for artifact parsing functionality in orchestrator
"""

import pytest
from core.orchestrator import ResearchOrchestrator
from unittest.mock import Mock, patch


class TestArtifactParsing:
    """Test artifact extraction methods"""

    @pytest.fixture
    def orchestrator_mock(self):
        """Create a mock orchestrator for testing parsing methods"""
        # We only need the parsing methods, not full initialization
        orchestrator = Mock(spec=ResearchOrchestrator)

        # Bind the actual parsing methods to the mock
        orchestrator._parse_trends = ResearchOrchestrator._parse_trends.__get__(orchestrator)
        orchestrator._parse_papers = ResearchOrchestrator._parse_papers.__get__(orchestrator)
        orchestrator._parse_articles = ResearchOrchestrator._parse_articles.__get__(orchestrator)
        orchestrator._parse_books = ResearchOrchestrator._parse_books.__get__(orchestrator)
        orchestrator._match_url_to_artifact = ResearchOrchestrator._match_url_to_artifact.__get__(orchestrator)
        orchestrator._extract_artifacts = ResearchOrchestrator._extract_artifacts.__get__(orchestrator)

        return orchestrator

    def test_parse_trends_with_structured_format(self, orchestrator_mock):
        """Test parsing trends with structured format"""
        trend_results = {
            'result': """
Trend Name: Edge AI Computing
Category: Technology
Impact Score: 9
Adoption Phase: Early Adoption

Trend Name: Explainable AI
Category: AI Ethics
Impact Score: 8
Adoption Phase: Growth
            """,
            'urls': ['https://example.com/edge-ai', 'https://example.com/explainable-ai']
        }

        artifacts = orchestrator._parse_trends(trend_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Edge AI Computing'
        assert artifacts[0]['category'] == 'Technology'
        assert artifacts[0]['impact_score'] == 9
        assert artifacts[0]['adoption_phase'] == 'Early Adoption'

        assert artifacts[1]['title'] == 'Explainable AI'
        assert artifacts[1]['category'] == 'AI Ethics'
        assert artifacts[1]['impact_score'] == 8

    def test_parse_trends_with_numbered_format(self, orchestrator):
        """Test parsing trends with numbered format"""
        trend_results = {
            'result': """
1. **Quantum Machine Learning** - This trend shows...
2. **Federated Learning** - Privacy-preserving approach...
            """,
            'urls': []
        }

        artifacts = orchestrator._parse_trends(trend_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Quantum Machine Learning'
        assert artifacts[1]['title'] == 'Federated Learning'

    def test_parse_papers_with_citations(self, orchestrator):
        """Test parsing papers with citation format"""
        scholar_results = {
            'result': '''
"Deep Learning" by Goodfellow et al. (2016)
"Attention Is All You Need" by Vaswani et al. (2017)
            ''',
            'urls': ['https://arxiv.org/deep-learning', 'https://arxiv.org/attention']
        }

        artifacts = orchestrator._parse_papers(scholar_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Deep Learning'
        assert artifacts[0]['authors'] == 'Goodfellow et al.'
        assert artifacts[0]['year'] == '2016'

        assert artifacts[1]['title'] == 'Attention Is All You Need'
        assert artifacts[1]['authors'] == 'Vaswani et al.'
        assert artifacts[1]['year'] == '2017'

    def test_parse_papers_with_markdown_format(self, orchestrator):
        """Test parsing papers with markdown bold format"""
        scholar_results = {
            'result': '''
**Neural Networks in 2025** - Smith et al., Nature
**Transformers at Scale** - Johnson et al., ICML 2025
            ''',
            'urls': []
        }

        artifacts = orchestrator._parse_papers(scholar_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Neural Networks in 2025'
        assert artifacts[0]['authors'] == 'Smith et al.'
        assert artifacts[0]['journal'] == 'Nature'

    def test_parse_articles_with_quotes(self, orchestrator):
        """Test parsing articles with quoted titles"""
        journalist_results = {
            'result': '''
Article: "AI Breakthrough in Healthcare" from TechCrunch
Article: "New ML Framework Released" from Wired
            ''',
            'urls': ['https://techcrunch.com/ai-healthcare']
        }

        artifacts = orchestrator._parse_articles(journalist_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'AI Breakthrough in Healthcare'
        assert artifacts[0]['source'] == 'TechCrunch'

        assert artifacts[1]['title'] == 'New ML Framework Released'
        assert artifacts[1]['source'] == 'Wired'

    def test_parse_articles_with_markdown_format(self, orchestrator):
        """Test parsing articles with markdown format"""
        journalist_results = {
            'result': '''
**GPT-5 Announcement** - OpenAI Blog
**Meta's New AI Model** - Facebook Research
            ''',
            'urls': []
        }

        artifacts = orchestrator._parse_articles(journalist_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'GPT-5 Announcement'
        assert artifacts[0]['source'] == 'OpenAI Blog'

    def test_parse_books_with_quotes(self, orchestrator):
        """Test parsing books with quoted format"""
        bibliophile_results = {
            'result': '''
"Machine Learning Yearbook" by Andrew Ng
"AI Safety Fundamentals" by Stuart Russell
            ''',
            'urls': []
        }

        artifacts = orchestrator._parse_books(bibliophile_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Machine Learning Yearbook'
        assert artifacts[0]['author'] == 'Andrew Ng'

        assert artifacts[1]['title'] == 'AI Safety Fundamentals'
        assert artifacts[1]['author'] == 'Stuart Russell'

    def test_parse_books_with_markdown_format(self, orchestrator):
        """Test parsing books with markdown format"""
        bibliophile_results = {
            'result': '''
**Deep Learning Book** - Ian Goodfellow
**Pattern Recognition** - Christopher Bishop
            ''',
            'urls': []
        }

        artifacts = orchestrator._parse_books(bibliophile_results)

        assert len(artifacts) == 2
        assert artifacts[0]['title'] == 'Deep Learning Book'
        assert artifacts[0]['author'] == 'Ian Goodfellow'

    def test_url_matching_to_artifacts(self, orchestrator):
        """Test URL matching based on title keywords"""
        artifact = {'title': 'Deep Learning Neural Networks'}
        urls = [
            'https://example.com/statistics',
            'https://example.com/deep-learning-guide',
            'https://example.com/other'
        ]

        orchestrator._match_url_to_artifact(artifact, urls)

        assert 'url' in artifact
        assert 'deep-learning' in artifact['url']

    def test_parse_empty_results(self, orchestrator):
        """Test parsing with empty results"""
        empty_results = {'result': '', 'urls': []}

        trends = orchestrator._parse_trends(empty_results)
        papers = orchestrator._parse_papers(empty_results)
        articles = orchestrator._parse_articles(empty_results)
        books = orchestrator._parse_books(empty_results)

        assert len(trends) == 0
        assert len(papers) == 0
        assert len(articles) == 0
        assert len(books) == 0

    def test_extract_artifacts_integration(self, orchestrator):
        """Test full artifact extraction from results"""
        results = {
            'trends': {
                'result': 'Trend Name: AI Safety\nCategory: Ethics\nImpact Score: 9',
                'urls': []
            },
            'white_papers': {
                'result': '"Safety in AI" by Smith (2025)',
                'urls': []
            },
            'news': {
                'result': 'Article: "New AI Regulations" from BBC',
                'urls': []
            },
            'books': {
                'result': '"AI Ethics Handbook" by Johnson',
                'urls': []
            }
        }

        artifacts = orchestrator._extract_artifacts(results)

        assert len(artifacts['trends']) == 1
        assert len(artifacts['papers']) == 1
        assert len(artifacts['articles']) == 1
        assert len(artifacts['books']) == 1

        assert artifacts['trends'][0]['title'] == 'AI Safety'
        assert artifacts['papers'][0]['title'] == 'Safety in AI'
        assert artifacts['articles'][0]['title'] == 'New AI Regulations'
        assert artifacts['books'][0]['title'] == 'AI Ethics Handbook'

    def test_duplicate_prevention(self, orchestrator):
        """Test that duplicate artifacts are not added"""
        scholar_results = {
            'result': '''
**Deep Learning** - Goodfellow et al., Nature
**Deep Learning** - Goodfellow et al., MIT Press
            ''',
            'urls': []
        }

        artifacts = orchestrator._parse_papers(scholar_results)

        # Should only have one entry (duplicates prevented)
        assert len(artifacts) == 1
        assert artifacts[0]['title'] == 'Deep Learning'
