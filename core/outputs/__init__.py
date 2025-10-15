"""
Output adapters for exporting research reports to multiple formats
"""
from typing import Dict, Any, List
from .base_adapter import OutputAdapter
from .markdown_adapter import MarkdownAdapter

def create_output_adapter(format_name: str, config: Dict[str, Any]) -> OutputAdapter:
    """
    Factory function to create output adapters

    Args:
        format_name: Name of the format (markdown, notion, confluence)
        config: Configuration dictionary for the adapter

    Returns:
        OutputAdapter instance

    Raises:
        ValueError: If format is unknown
        ImportError: If required dependencies are missing
    """
    adapters = {
        'markdown': MarkdownAdapter,
    }

    # Lazy import for optional dependencies
    if format_name == 'notion':
        try:
            from .notion_adapter import NotionAdapter
            adapters['notion'] = NotionAdapter
        except ImportError:
            raise ImportError(
                "notion-client not installed. Run: pip install notion-client"
            )

    if format_name == 'confluence':
        try:
            from .confluence_adapter import ConfluenceAdapter
            adapters['confluence'] = ConfluenceAdapter
        except ImportError:
            raise ImportError(
                "atlassian-python-api not installed. "
                "Run: pip install atlassian-python-api"
            )

    if format_name not in adapters:
        raise ValueError(f"Unknown output format: {format_name}")

    return adapters[format_name](config)

def get_available_adapters() -> List[str]:
    """
    Get list of available output adapters

    Returns:
        List of adapter names
    """
    available = ['markdown']

    try:
        import notion_client
        available.append('notion')
    except ImportError:
        pass

    try:
        import atlassian
        available.append('confluence')
    except ImportError:
        pass

    return available

__all__ = [
    'OutputAdapter',
    'MarkdownAdapter',
    'create_output_adapter',
    'get_available_adapters'
]
