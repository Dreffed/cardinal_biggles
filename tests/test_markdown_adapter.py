"""
Tests for Markdown/Obsidian output adapter
"""
import pytest
from pathlib import Path
from core.outputs.markdown_adapter import MarkdownAdapter

@pytest.fixture
def markdown_config():
    return {
        'output_directory': './test_reports',
        'obsidian': {
            'enabled': True,
            'use_wikilinks': True,
            'use_tags': True,
            'create_moc': True
        },
        'structure': {
            'create_topic_folder': True,
            'save_agent_outputs': True,
            'save_artifacts': True
        },
        'export_options': {
            'include_metadata': True
        }
    }

@pytest.fixture
def sample_report_data():
    return {
        'content': '# Test Report\n\nTest content',
        'agent_outputs': {
            'trend_scout': {
                'result': 'Trend analysis...',
                'timestamp': '2025-01-14T10:00:00',
                'urls': ['https://example.com']
            }
        },
        'artifacts': {
            'papers': [
                {
                    'title': 'Test Paper',
                    'url': 'https://example.com/paper.pdf',
                    'content': 'Paper summary'
                }
            ]
        },
        'raw_data': {
            'knowledge_store': {'documents': []}
        }
    }

@pytest.fixture
def sample_metadata():
    return {
        'topic': 'Test Research',
        'date': '2025-01-14',
        'tags': ['test', 'research'],
        'agents': ['trend_scout'],
        'sources_count': 10,
        'status': 'complete'
    }

@pytest.mark.asyncio
async def test_markdown_adapter_initialization(markdown_config):
    """Test adapter initialization"""
    adapter = MarkdownAdapter(markdown_config)
    assert adapter.format_name == 'markdown'
    assert adapter.output_dir == Path('./test_reports')

@pytest.mark.asyncio
async def test_markdown_adapter_export(
    markdown_config,
    sample_report_data,
    sample_metadata,
    tmp_path
):
    """Test basic export functionality"""
    # Use temp directory
    markdown_config['output_directory'] = str(tmp_path)
    adapter = MarkdownAdapter(markdown_config)

    # Export report
    result = await adapter.export_report(sample_report_data, sample_metadata)

    # Verify output exists
    result_path = Path(result)
    assert result_path.exists()
    assert result_path.name == 'report.md'

    # Verify folder structure
    research_folder = result_path.parent
    assert (research_folder / 'agents').exists()
    assert (research_folder / 'artifacts').exists()
    assert (research_folder / 'data').exists()

@pytest.mark.asyncio
async def test_markdown_adapter_creates_moc(
    markdown_config,
    sample_report_data,
    sample_metadata,
    tmp_path
):
    """Test MOC (Map of Content) creation"""
    markdown_config['output_directory'] = str(tmp_path)
    adapter = MarkdownAdapter(markdown_config)

    result = await adapter.export_report(sample_report_data, sample_metadata)
    research_folder = Path(result).parent

    moc_path = research_folder / 'index.md'
    assert moc_path.exists()

    content = moc_path.read_text()
    assert 'Map of Content' in content
    assert '[[report|Main Research Report]]' in content

@pytest.mark.asyncio
async def test_markdown_adapter_exports_agent_outputs(
    markdown_config,
    sample_report_data,
    sample_metadata,
    tmp_path
):
    """Test agent output file creation"""
    markdown_config['output_directory'] = str(tmp_path)
    adapter = MarkdownAdapter(markdown_config)

    result = await adapter.export_report(sample_report_data, sample_metadata)
    research_folder = Path(result).parent

    agent_file = research_folder / 'agents' / 'trend_scout_results.md'
    assert agent_file.exists()

    content = agent_file.read_text()
    assert 'Trend Scout Results' in content
    assert 'Trend analysis...' in content

@pytest.mark.asyncio
async def test_markdown_adapter_exports_artifacts(
    markdown_config,
    sample_report_data,
    sample_metadata,
    tmp_path
):
    """Test artifact file creation"""
    markdown_config['output_directory'] = str(tmp_path)
    adapter = MarkdownAdapter(markdown_config)

    result = await adapter.export_report(sample_report_data, sample_metadata)
    research_folder = Path(result).parent

    artifact_file = research_folder / 'artifacts' / 'papers' / 'papers_001.md'
    assert artifact_file.exists()

    content = artifact_file.read_text()
    assert 'Test Paper' in content
    assert 'https://example.com/paper.pdf' in content

def test_markdown_adapter_sanitize_filename(markdown_config):
    """Test filename sanitization"""
    adapter = MarkdownAdapter(markdown_config)

    assert adapter._sanitize_filename("Test:File") == "testfile"
    assert adapter._sanitize_filename("Test File") == "test_file"
    assert adapter._sanitize_filename("Test  Multiple  Spaces") == "test_multiple_spaces"
