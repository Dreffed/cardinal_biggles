# Multi-Format Output Feature Plan

**Status:** ✅ Phase 1 Complete (Markdown/Obsidian Implemented)
**Priority:** High
**Created:** 2025-01-14
**Last Updated:** 2025-01-14
**Phase 1 Completed:** 2025-01-14

---

## Overview

Add support for exporting Cardinal Biggles research reports to multiple formats with organized folder structures for research artifacts, agent outputs, and supporting data.

### Supported Formats
- **Markdown/Obsidian** (enhanced with linking, tags, and vault structure)
- **Notion** (via Notion API)
- **Confluence** (via Atlassian REST API)

---

## Goals

1. Enable organized, hierarchical output structure for research artifacts
2. Support Obsidian knowledge management workflows
3. Provide cloud-based collaboration via Notion and Confluence
4. Maintain backward compatibility with existing single-file output
5. Allow multiple simultaneous output formats

---

## Architecture Design

### 1. Output Adapter Pattern

Create a plugin-style architecture for output formats:

```
core/
├── outputs/
│   ├── __init__.py
│   ├── base_adapter.py       # Abstract base class
│   ├── markdown_adapter.py   # Markdown/Obsidian adapter
│   ├── notion_adapter.py     # Notion API adapter
│   └── confluence_adapter.py # Confluence API adapter
```

#### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class OutputAdapter(ABC):
    """Base class for all output adapters"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.format_name = self.__class__.__name__.replace('Adapter', '').lower()

    @abstractmethod
    async def export_report(self, report_data: Dict, metadata: Dict) -> str:
        """
        Export final report

        Args:
            report_data: Complete report data including content and artifacts
            metadata: Report metadata (title, date, tags, etc.)

        Returns:
            Output location (file path, URL, etc.)
        """
        pass

    @abstractmethod
    async def export_artifact(self, artifact_type: str, content: str, metadata: Dict) -> str:
        """
        Export individual research artifacts

        Args:
            artifact_type: Type of artifact (trend, paper, article, book)
            content: Artifact content
            metadata: Artifact metadata

        Returns:
            Output location
        """
        pass

    @abstractmethod
    def get_output_location(self) -> str:
        """Return output location (path, URL, etc.)"""
        pass

    def validate_config(self) -> bool:
        """Validate adapter configuration"""
        return True
```

---

### 2. Folder Structure for Markdown/Obsidian

Proposed hierarchical structure for organized research output:

```
output_root/
├── {topic_slug}_{timestamp}/
│   ├── report.md                    # Main research report
│   ├── metadata.yaml                # Research session metadata
│   │
│   ├── agents/                      # Agent outputs
│   │   ├── trend_scout_results.md
│   │   ├── historian_results.md
│   │   ├── scholar_results.md
│   │   ├── journalist_results.md
│   │   └── bibliophile_results.md
│   │
│   ├── artifacts/                   # Research artifacts by type
│   │   ├── trends/
│   │   │   ├── trend_001.md
│   │   │   └── trend_002.md
│   │   ├── papers/
│   │   │   ├── paper_001.md
│   │   │   └── paper_002.md
│   │   ├── articles/
│   │   │   ├── article_001.md
│   │   │   └── article_002.md
│   │   └── books/
│   │       ├── book_001.md
│   │       └── book_002.md
│   │
│   ├── data/                        # Raw data for reproducibility
│   │   ├── knowledge_store.json
│   │   ├── url_tracker.json
│   │   └── hil_checkpoints.json     # (if HIL was used)
│   │
│   └── attachments/                 # Supporting files
│       └── (images, PDFs, etc.)
```

#### Metadata YAML Structure

```yaml
# metadata.yaml
title: "Machine Learning Research Report"
topic: "Machine Learning"
date: "2025-01-14T10:30:00"
timestamp: "20250114_103000"
status: "complete"
duration_minutes: 45

agents:
  - trend_scout
  - historian
  - scholar
  - journalist
  - bibliophile
  - reporter

sources:
  total: 47
  papers: 12
  articles: 18
  books: 5
  trends: 8
  historical: 4

llm_providers:
  coordinator: "ollama/llama3.1"
  trend_scout: "perplexity/llama-3.1-sonar"
  scholar: "claude/claude-3-sonnet"
  reporter: "claude/claude-3-opus"

hil:
  enabled: false
  checkpoints: 0

tags:
  - machine-learning
  - ai-trends
  - research
  - 2025
```

---

### 3. Obsidian-Specific Features

#### Frontmatter

```markdown
---
title: "Machine Learning Research Report"
date: 2025-01-14
tags:
  - research
  - machine-learning
  - ai-trends
agents:
  - trend_scout
  - historian
  - scholar
  - journalist
  - bibliophile
sources: 47
status: complete
cssclass: research-report
---
```

#### Wikilinks

```markdown
## Related Research
- [[agents/trend_scout_results|Trend Scout Analysis]]
- [[agents/scholar_results|Academic Research]]
- [[artifacts/papers/paper_001|Key Paper: Neural Networks]]

## Top Trends
- [[artifacts/trends/trend_001|Edge AI Computing]]
- [[artifacts/trends/trend_002|Explainable AI]]
```

#### Tags

```markdown
#research #machine-learning #ai-trends #2025
```

#### Map of Content (MOC)

Auto-generate an index file linking all research components:

```markdown
# Machine Learning Research - MOC

## Overview
Research conducted: 2025-01-14
Total sources: 47

## Report
- [[report|Main Research Report]]

## Agent Outputs
- [[agents/trend_scout_results|Trend Scout]]
- [[agents/historian_results|Historian]]
- [[agents/scholar_results|Scholar]]
- [[agents/journalist_results|Journalist]]
- [[agents/bibliophile_results|Bibliophile]]

## Key Artifacts
### Trends (8)
- [[artifacts/trends/trend_001|Edge AI Computing]]
- [[artifacts/trends/trend_002|Explainable AI]]
...

### Papers (12)
- [[artifacts/papers/paper_001|Neural Networks in 2025]]
...

### Articles (18)
...

### Books (5)
...

## Data
- [[data/knowledge_store.json|Knowledge Store]]
- [[data/url_tracker.json|URL Tracker]]

#research-index #machine-learning
```

#### Callouts/Admonitions

```markdown
> [!summary] Executive Summary
> Key findings from the research...

> [!important] Critical Insight
> The most significant trend identified is...

> [!note] Research Note
> Additional context...
```

---

### 4. Configuration Schema

```yaml
# Output Configuration
output:
  # Primary output format (backward compatible)
  format: "markdown"  # markdown, notion, confluence

  # Multiple formats can be enabled simultaneously
  formats:
    - markdown
    # - notion
    # - confluence

  # Markdown/Obsidian Configuration
  markdown:
    enabled: true
    output_directory: "./reports"

    # Obsidian-specific features
    obsidian:
      enabled: true
      vault_path: null  # Set to use specific Obsidian vault
      use_wikilinks: true
      use_tags: true
      use_frontmatter: true
      use_callouts: true
      create_moc: true          # Create Map of Content
      link_artifacts: true
      link_agents: true
      moc_filename: "index.md"

    # Folder structure options
    structure:
      create_topic_folder: true
      timestamp_folders: true
      save_agent_outputs: true
      save_artifacts: true
      save_raw_data: true
      separate_by_type: true    # Separate artifacts by type (papers, articles, etc.)

    # Export options
    export_options:
      include_metadata: true
      include_timestamps: true
      split_by_section: false   # Create separate files per section
      embed_images: false       # Embed vs link images
      create_attachments_folder: true
      sanitize_filenames: true

  # Notion Configuration
  notion:
    enabled: false
    api_key: "${NOTION_API_KEY}"
    database_id: "${NOTION_DATABASE_ID}"  # Research database

    # Page structure
    structure:
      parent_page: null         # ID of parent page (or root of database)
      parent_page_title: "Research Reports"  # Or find by title
      create_subpages: true     # Create subpages for each section
      link_artifacts: true
      create_database_entry: true

    # Export options
    export_options:
      add_tags: true
      add_timestamp: true
      add_metadata_properties: true
      sync_mode: "create"       # create, update, or sync
      update_existing: false
      match_by: "title"         # How to match existing pages

  # Confluence Configuration
  confluence:
    enabled: false
    base_url: "https://your-domain.atlassian.net/wiki"
    api_token: "${CONFLUENCE_API_TOKEN}"
    username: "${CONFLUENCE_USERNAME}"
    space_key: "RESEARCH"

    # Page structure
    structure:
      parent_page: null         # ID or title of parent page
      parent_page_title: "Research Reports"
      create_child_pages: true  # Create child pages for sections
      add_labels: true

    # Export options
    export_options:
      add_metadata_table: true
      add_timestamp: true
      create_attachments: true
      convert_markdown: true    # Convert MD to Confluence format
      sync_mode: "create"       # create or update
      update_existing: false
      match_by: "title"

  # General output options (backward compatible)
  include_reference_tables: true
  save_intermediate_results: true
  compress_old_reports: false
  retention_days: 90
```

---

## Implementation Plan

### Phase 1: Markdown/Obsidian Adapter ⭐ (Priority)

**Goal:** Enhanced Markdown output with organized folder structure

**Files to Create:**
- `core/outputs/__init__.py`
- `core/outputs/base_adapter.py`
- `core/outputs/markdown_adapter.py`

**Features:**

1. **Enhanced Markdown Output**
   - Proper frontmatter with metadata
   - Consistent heading hierarchy
   - Code blocks with syntax highlighting
   - Tables for references
   - Callouts/admonitions for important info

2. **Obsidian Integration**
   - Wikilink generation: `[[file|display text]]`
   - Tag insertion: `#tag #nested/tag`
   - Dataview-compatible frontmatter
   - MOC (Map of Content) generation
   - Backlink structure

3. **Folder Organization**
   - Create timestamped research folders
   - Separate agent outputs into files
   - Organize artifacts by type (trends, papers, articles, books)
   - Save raw data for reproducibility
   - Create attachments folder

**Implementation Details:**

```python
# core/outputs/markdown_adapter.py

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import yaml
import json
from .base_adapter import OutputAdapter

class MarkdownAdapter(OutputAdapter):
    """Markdown/Obsidian output adapter"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.output_dir = Path(config.get('output_directory', './reports'))
        self.obsidian_config = config.get('obsidian', {})
        self.structure_config = config.get('structure', {})
        self.export_config = config.get('export_options', {})

    async def export_report(self, report_data: Dict, metadata: Dict) -> str:
        """Export complete research report with folder structure"""

        # Create folder structure
        research_folder = self._create_research_folder(metadata)

        # Export main report
        report_path = await self._export_main_report(
            research_folder,
            report_data,
            metadata
        )

        # Export agent outputs
        if self.structure_config.get('save_agent_outputs', True):
            await self._export_agent_outputs(
                research_folder / 'agents',
                report_data.get('agent_outputs', {})
            )

        # Export artifacts
        if self.structure_config.get('save_artifacts', True):
            await self._export_artifacts(
                research_folder / 'artifacts',
                report_data.get('artifacts', {})
            )

        # Export raw data
        if self.structure_config.get('save_raw_data', True):
            await self._export_raw_data(
                research_folder / 'data',
                report_data.get('raw_data', {})
            )

        # Create MOC if enabled
        if self.obsidian_config.get('create_moc', True):
            await self._create_moc(research_folder, report_data, metadata)

        # Save metadata
        if self.export_config.get('include_metadata', True):
            await self._save_metadata(research_folder, metadata)

        return str(report_path.absolute())

    def _create_research_folder(self, metadata: Dict) -> Path:
        """Create timestamped research folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = self._sanitize_filename(metadata['topic'])[:50]

        folder_name = f"{topic_slug}_{timestamp}"
        research_folder = self.output_dir / folder_name

        # Create folder structure
        research_folder.mkdir(parents=True, exist_ok=True)
        (research_folder / 'agents').mkdir(exist_ok=True)
        (research_folder / 'artifacts').mkdir(exist_ok=True)
        (research_folder / 'data').mkdir(exist_ok=True)

        if self.export_config.get('create_attachments_folder', True):
            (research_folder / 'attachments').mkdir(exist_ok=True)

        return research_folder

    async def _export_main_report(
        self,
        folder: Path,
        report_data: Dict,
        metadata: Dict
    ) -> Path:
        """Export main report with frontmatter"""

        # Build frontmatter
        frontmatter = self._build_frontmatter(metadata)

        # Build content
        content = report_data['content']

        # Add Obsidian features
        if self.obsidian_config.get('use_wikilinks', True):
            content = self._add_wikilinks(content, metadata)

        if self.obsidian_config.get('use_callouts', True):
            content = self._convert_to_callouts(content)

        # Combine frontmatter and content
        full_content = f"---\n{yaml.dump(frontmatter)}---\n\n{content}"

        # Add tags at bottom if enabled
        if self.obsidian_config.get('use_tags', True):
            tags = self._generate_tags(metadata)
            full_content += f"\n\n{tags}"

        # Write file
        report_path = folder / 'report.md'
        report_path.write_text(full_content, encoding='utf-8')

        return report_path

    async def _export_agent_outputs(self, folder: Path, agent_outputs: Dict):
        """Export individual agent outputs"""
        folder.mkdir(parents=True, exist_ok=True)

        for agent_name, output in agent_outputs.items():
            filename = f"{agent_name}_results.md"
            file_path = folder / filename

            # Build agent output with frontmatter
            frontmatter = {
                'title': f"{agent_name.replace('_', ' ').title()} Results",
                'agent': agent_name,
                'date': output.get('timestamp', datetime.now().isoformat()),
                'tags': [f"agent/{agent_name}", "research"]
            }

            content = f"---\n{yaml.dump(frontmatter)}---\n\n"
            content += f"# {agent_name.replace('_', ' ').title()} Results\n\n"
            content += output.get('result', '')

            file_path.write_text(content, encoding='utf-8')

    async def _export_artifacts(self, folder: Path, artifacts: Dict):
        """Export research artifacts organized by type"""
        folder.mkdir(parents=True, exist_ok=True)

        # Organize by type
        for artifact_type, items in artifacts.items():
            type_folder = folder / artifact_type
            type_folder.mkdir(exist_ok=True)

            for idx, item in enumerate(items, 1):
                filename = f"{artifact_type}_{idx:03d}.md"
                file_path = type_folder / filename

                # Build artifact file
                frontmatter = {
                    'title': item.get('title', f'{artifact_type.title()} {idx}'),
                    'type': artifact_type,
                    'url': item.get('url', ''),
                    'date': item.get('date', ''),
                    'tags': [f"artifact/{artifact_type}", "research"]
                }

                content = f"---\n{yaml.dump(frontmatter)}---\n\n"
                content += f"# {item.get('title', f'{artifact_type.title()} {idx}')}\n\n"

                if item.get('url'):
                    content += f"**Source:** {item['url']}\n\n"

                content += item.get('content', item.get('summary', ''))

                file_path.write_text(content, encoding='utf-8')

    async def _export_raw_data(self, folder: Path, raw_data: Dict):
        """Export raw data for reproducibility"""
        folder.mkdir(parents=True, exist_ok=True)

        for data_type, data in raw_data.items():
            filename = f"{data_type}.json"
            file_path = folder / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

    async def _create_moc(self, folder: Path, report_data: Dict, metadata: Dict):
        """Create Map of Content (index) file"""
        moc_filename = self.obsidian_config.get('moc_filename', 'index.md')
        moc_path = folder / moc_filename

        # Build MOC content
        content = f"# {metadata['topic']} Research - Map of Content\n\n"
        content += f"**Research conducted:** {metadata['date']}\n"
        content += f"**Total sources:** {metadata.get('sources_count', 0)}\n\n"

        # Link to main report
        content += "## Main Report\n"
        content += "- [[report|Main Research Report]]\n\n"

        # Link to agent outputs
        content += "## Agent Outputs\n"
        for agent_name in report_data.get('agent_outputs', {}).keys():
            display_name = agent_name.replace('_', ' ').title()
            content += f"- [[agents/{agent_name}_results|{display_name}]]\n"
        content += "\n"

        # Link to artifacts
        content += "## Research Artifacts\n"
        artifacts = report_data.get('artifacts', {})
        for artifact_type, items in artifacts.items():
            content += f"### {artifact_type.title()} ({len(items)})\n"
            for idx, item in enumerate(items[:5], 1):  # Show first 5
                title = item.get('title', f'{artifact_type} {idx}')
                content += f"- [[artifacts/{artifact_type}/{artifact_type}_{idx:03d}|{title}]]\n"
            if len(items) > 5:
                content += f"- ... and {len(items) - 5} more\n"
            content += "\n"

        # Link to data
        if report_data.get('raw_data'):
            content += "## Raw Data\n"
            for data_type in report_data['raw_data'].keys():
                content += f"- `data/{data_type}.json`\n"
            content += "\n"

        # Add tags
        tags = self._generate_tags(metadata)
        content += f"\n{tags}"

        moc_path.write_text(content, encoding='utf-8')

    async def _save_metadata(self, folder: Path, metadata: Dict):
        """Save research metadata"""
        metadata_path = folder / 'metadata.yaml'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False)

    def _build_frontmatter(self, metadata: Dict) -> Dict:
        """Build YAML frontmatter"""
        return {
            'title': metadata['topic'],
            'date': metadata['date'],
            'tags': metadata.get('tags', []),
            'agents': metadata.get('agents', []),
            'sources': metadata.get('sources_count', 0),
            'status': metadata.get('status', 'complete'),
            'cssclass': 'research-report'
        }

    def _add_wikilinks(self, content: str, metadata: Dict) -> str:
        """Add wikilinks to content"""
        # TODO: Implement intelligent wikilink insertion
        return content

    def _convert_to_callouts(self, content: str) -> str:
        """Convert sections to Obsidian callouts"""
        # Convert "Summary:" or "Executive Summary:" to callout
        content = content.replace(
            '## Executive Summary',
            '## Executive Summary\n\n> [!summary] Executive Summary'
        )
        # Add more conversions as needed
        return content

    def _generate_tags(self, metadata: Dict) -> str:
        """Generate tag string"""
        tags = metadata.get('tags', [])
        return ' '.join([f'#{tag}' for tag in tags])

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename"""
        import re
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        return name.lower()

    async def export_artifact(self, artifact_type: str, content: str, metadata: Dict) -> str:
        """Export single artifact"""
        # Implementation for single artifact export
        pass

    def get_output_location(self) -> str:
        """Return output directory"""
        return str(self.output_dir.absolute())
```

**Tests:**
```python
# tests/test_markdown_adapter.py

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
        }
    }

@pytest.fixture
def sample_report_data():
    return {
        'content': '# Test Report\n\nTest content',
        'agent_outputs': {
            'trend_scout': {
                'result': 'Trend analysis...',
                'timestamp': '2025-01-14T10:00:00'
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
async def test_markdown_adapter_creates_folder_structure(
    markdown_config,
    sample_report_data,
    sample_metadata
):
    adapter = MarkdownAdapter(markdown_config)
    result = await adapter.export_report(sample_report_data, sample_metadata)

    result_path = Path(result).parent

    # Check folder structure
    assert result_path.exists()
    assert (result_path / 'agents').exists()
    assert (result_path / 'artifacts').exists()
    assert (result_path / 'data').exists()
    assert (result_path / 'report.md').exists()

@pytest.mark.asyncio
async def test_markdown_adapter_creates_moc(
    markdown_config,
    sample_report_data,
    sample_metadata
):
    adapter = MarkdownAdapter(markdown_config)
    result = await adapter.export_report(sample_report_data, sample_metadata)

    result_path = Path(result).parent
    moc_path = result_path / 'index.md'

    assert moc_path.exists()

    content = moc_path.read_text()
    assert '# Test Research Research - Map of Content' in content
    assert '[[report|Main Research Report]]' in content

@pytest.mark.asyncio
async def test_markdown_adapter_exports_agent_outputs(
    markdown_config,
    sample_report_data,
    sample_metadata
):
    adapter = MarkdownAdapter(markdown_config)
    result = await adapter.export_report(sample_report_data, sample_metadata)

    result_path = Path(result).parent
    agent_file = result_path / 'agents' / 'trend_scout_results.md'

    assert agent_file.exists()

    content = agent_file.read_text()
    assert 'Trend Scout Results' in content
    assert 'Trend analysis...' in content

@pytest.mark.asyncio
async def test_markdown_adapter_exports_artifacts(
    markdown_config,
    sample_report_data,
    sample_metadata
):
    adapter = MarkdownAdapter(markdown_config)
    result = await adapter.export_report(sample_report_data, sample_metadata)

    result_path = Path(result).parent
    artifact_file = result_path / 'artifacts' / 'papers' / 'papers_001.md'

    assert artifact_file.exists()

    content = artifact_file.read_text()
    assert 'Test Paper' in content
    assert 'https://example.com/paper.pdf' in content
```

---

### Phase 2: Notion API Adapter

**Goal:** Export reports to Notion workspaces

**Dependencies:**
```bash
pip install notion-client
```

**Files to Create:**
- `core/outputs/notion_adapter.py`

**Features:**

1. **Notion API Integration**
   - Create pages in specified database
   - Add blocks (headings, paragraphs, tables, code blocks)
   - Upload attachments
   - Set properties (tags, dates, status)

2. **Hierarchical Structure**
   - Parent page: Main report
   - Child pages: Agent outputs, artifacts
   - Database entries for tracking

3. **Sync Capabilities**
   - Create new pages
   - Update existing pages (by title match)
   - Append to existing pages

**Implementation Details:**

```python
# core/outputs/notion_adapter.py

from typing import Dict, Any, List
from notion_client import Client, AsyncClient
from .base_adapter import OutputAdapter

class NotionAdapter(OutputAdapter):
    """Notion output adapter"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = AsyncClient(auth=config['api_key'])
        self.database_id = config['database_id']
        self.structure_config = config.get('structure', {})
        self.export_config = config.get('export_options', {})

    async def export_report(self, report_data: Dict, metadata: Dict) -> str:
        """Export report to Notion"""

        # Create main page in database
        page = await self._create_main_page(report_data, metadata)
        page_id = page['id']
        page_url = page['url']

        # Add content blocks
        await self._add_content_blocks(page_id, report_data['content'])

        # Create child pages if enabled
        if self.structure_config.get('create_subpages', True):
            await self._create_agent_subpages(page_id, report_data.get('agent_outputs', {}))
            await self._create_artifact_subpages(page_id, report_data.get('artifacts', {}))

        return page_url

    async def _create_main_page(self, report_data: Dict, metadata: Dict) -> Dict:
        """Create main report page"""

        properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': metadata['topic']
                        }
                    }
                ]
            }
        }

        # Add tags if enabled
        if self.export_config.get('add_tags', True):
            properties['Tags'] = {
                'multi_select': [
                    {'name': tag} for tag in metadata.get('tags', [])
                ]
            }

        # Add timestamp if enabled
        if self.export_config.get('add_timestamp', True):
            properties['Date'] = {
                'date': {
                    'start': metadata['date']
                }
            }

        # Add metadata properties
        if self.export_config.get('add_metadata_properties', True):
            properties['Status'] = {'select': {'name': metadata.get('status', 'Complete')}}
            properties['Sources'] = {'number': metadata.get('sources_count', 0)}

        # Create page
        page = await self.client.pages.create(
            parent={'database_id': self.database_id},
            properties=properties
        )

        return page

    async def _add_content_blocks(self, page_id: str, content: str):
        """Add content blocks to page"""

        # Convert markdown to Notion blocks
        blocks = self._markdown_to_blocks(content)

        # Add blocks in chunks (Notion API limit)
        chunk_size = 100
        for i in range(0, len(blocks), chunk_size):
            chunk = blocks[i:i+chunk_size]
            await self.client.blocks.children.append(
                block_id=page_id,
                children=chunk
            )

    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """Convert markdown to Notion blocks"""
        # TODO: Implement markdown to Notion block conversion
        # This is a simplified version
        blocks = []

        lines = markdown.split('\n')
        for line in lines:
            if line.startswith('# '):
                blocks.append({
                    'object': 'block',
                    'type': 'heading_1',
                    'heading_1': {
                        'rich_text': [{'type': 'text', 'text': {'content': line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    'object': 'block',
                    'type': 'heading_2',
                    'heading_2': {
                        'rich_text': [{'type': 'text', 'text': {'content': line[3:]}}]
                    }
                })
            elif line.strip():
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': line}}]
                    }
                })

        return blocks

    async def _create_agent_subpages(self, parent_id: str, agent_outputs: Dict):
        """Create child pages for agent outputs"""
        for agent_name, output in agent_outputs.items():
            # Create child page
            page = await self.client.pages.create(
                parent={'page_id': parent_id},
                properties={
                    'title': {
                        'title': [
                            {
                                'text': {
                                    'content': f"{agent_name.replace('_', ' ').title()} Results"
                                }
                            }
                        ]
                    }
                }
            )

            # Add content
            await self._add_content_blocks(page['id'], output.get('result', ''))

    async def _create_artifact_subpages(self, parent_id: str, artifacts: Dict):
        """Create child pages for artifacts"""
        # Similar to agent subpages
        pass

    async def export_artifact(self, artifact_type: str, content: str, metadata: Dict) -> str:
        """Export single artifact"""
        pass

    def get_output_location(self) -> str:
        """Return Notion workspace"""
        return f"Notion Database: {self.database_id}"
```

---

### Phase 3: Confluence API Adapter

**Goal:** Export reports to Confluence spaces

**Dependencies:**
```bash
pip install atlassian-python-api
```

**Files to Create:**
- `core/outputs/confluence_adapter.py`

**Features:**

1. **Confluence API Integration**
   - Create pages in specified space
   - Add content in Storage Format (Confluence HTML)
   - Upload attachments
   - Add labels (tags)

2. **Hierarchical Structure**
   - Parent page: Space or specified page
   - Child pages: Sections, agent outputs
   - Attachments: PDFs, images

3. **Markdown to Confluence Conversion**
   - Convert Markdown to Confluence Storage Format
   - Preserve tables, code blocks, links
   - Handle images and attachments

**Implementation Details:**

```python
# core/outputs/confluence_adapter.py

from typing import Dict, Any
from atlassian import Confluence
from .base_adapter import OutputAdapter
import markdown

class ConfluenceAdapter(OutputAdapter):
    """Confluence output adapter"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.confluence = Confluence(
            url=config['base_url'],
            username=config['username'],
            password=config['api_token']
        )
        self.space_key = config['space_key']
        self.structure_config = config.get('structure', {})
        self.export_config = config.get('export_options', {})

    async def export_report(self, report_data: Dict, metadata: Dict) -> str:
        """Export report to Confluence"""

        # Convert markdown to Confluence Storage Format
        content_html = self._markdown_to_confluence(report_data['content'])

        # Add metadata table if enabled
        if self.export_config.get('add_metadata_table', True):
            content_html = self._add_metadata_table(content_html, metadata)

        # Find or create parent page
        parent_id = self._get_parent_page_id()

        # Create page
        page = self.confluence.create_page(
            space=self.space_key,
            title=metadata['topic'],
            body=content_html,
            parent_id=parent_id
        )

        # Add labels if enabled
        if self.structure_config.get('add_labels', True):
            for tag in metadata.get('tags', []):
                self.confluence.add_label(page['id'], tag)

        # Create child pages if enabled
        if self.structure_config.get('create_child_pages', True):
            await self._create_agent_child_pages(
                page['id'],
                report_data.get('agent_outputs', {})
            )

        # Build page URL
        page_url = f"{self.confluence.url}{page['_links']['webui']}"

        return page_url

    def _markdown_to_confluence(self, markdown_text: str) -> str:
        """Convert Markdown to Confluence Storage Format"""
        # Convert markdown to HTML
        html = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'codehilite']
        )

        # Convert HTML to Confluence Storage Format
        # This is simplified - would need more comprehensive conversion
        storage_format = html

        return storage_format

    def _add_metadata_table(self, content: str, metadata: Dict) -> str:
        """Add metadata table to content"""
        table_html = '<table><tbody>'
        table_html += f'<tr><th>Date</th><td>{metadata["date"]}</td></tr>'
        table_html += f'<tr><th>Status</th><td>{metadata.get("status", "Complete")}</td></tr>'
        table_html += f'<tr><th>Sources</th><td>{metadata.get("sources_count", 0)}</td></tr>'
        table_html += f'<tr><th>Tags</th><td>{", ".join(metadata.get("tags", []))}</td></tr>'
        table_html += '</tbody></table><br/>'

        return table_html + content

    def _get_parent_page_id(self) -> str:
        """Get parent page ID"""
        parent_title = self.structure_config.get('parent_page_title')

        if not parent_title:
            return None

        # Search for page by title
        results = self.confluence.get_page_by_title(
            space=self.space_key,
            title=parent_title
        )

        if results:
            return results['id']

        return None

    async def _create_agent_child_pages(self, parent_id: str, agent_outputs: Dict):
        """Create child pages for agent outputs"""
        for agent_name, output in agent_outputs.items():
            title = f"{agent_name.replace('_', ' ').title()} Results"
            content_html = self._markdown_to_confluence(output.get('result', ''))

            self.confluence.create_page(
                space=self.space_key,
                title=title,
                body=content_html,
                parent_id=parent_id
            )

    async def export_artifact(self, artifact_type: str, content: str, metadata: Dict) -> str:
        """Export single artifact"""
        pass

    def get_output_location(self) -> str:
        """Return Confluence space"""
        return f"Confluence Space: {self.space_key}"
```

---

### Phase 4: Integration with Orchestrator

**Files to Modify:**
- `core/orchestrator.py`
- `cli/main.py`
- `config/config.yaml` (default config)

**Orchestrator Changes:**

```python
# core/orchestrator.py

from core.outputs import create_output_adapter, get_available_adapters

class ResearchOrchestrator:
    def __init__(self, config_path: str = "config/config.yaml"):
        # ... existing initialization ...

        # Initialize output adapters
        self.output_adapters = self._initialize_output_adapters()

    def _initialize_output_adapters(self) -> List:
        """Initialize all enabled output adapters"""
        output_config = self.llm_factory.config.get('output', {})
        adapters = []

        enabled_formats = output_config.get('formats', ['markdown'])

        for format_name in enabled_formats:
            format_config = output_config.get(format_name, {})

            if format_config.get('enabled', True):
                try:
                    adapter = create_output_adapter(format_name, format_config)
                    adapters.append(adapter)
                    self.logger.info(f"Initialized {format_name} output adapter")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {format_name} adapter: {e}")

        if not adapters:
            # Fallback to markdown
            self.logger.warning("No output adapters initialized, using default markdown")
            adapters.append(create_output_adapter('markdown', {}))

        return adapters

    async def save_results(self, results: Dict, metadata: Dict) -> List[Dict]:
        """Save results to all enabled output formats"""
        output_locations = []

        for adapter in self.output_adapters:
            try:
                self.logger.info(f"Exporting to {adapter.format_name}...")

                location = await adapter.export_report(results, metadata)

                output_locations.append({
                    'format': adapter.format_name,
                    'location': location,
                    'status': 'success'
                })

                self.logger.info(f"✓ Saved to {adapter.format_name}: {location}")

            except Exception as e:
                self.logger.error(f"✗ Failed to save to {adapter.format_name}: {e}")
                output_locations.append({
                    'format': adapter.format_name,
                    'status': 'failed',
                    'error': str(e)
                })

        return output_locations

    async def execute_workflow(self, topic: str) -> Dict:
        """Execute the complete research workflow"""
        self.logger.info(f"Starting research workflow for topic: {topic}")

        coordinator = self.agents["coordinator"]
        results = await coordinator.execute_research_workflow(topic)

        # Build metadata
        metadata = {
            'topic': topic,
            'date': datetime.now().isoformat(),
            'tags': self._extract_tags(topic),
            'agents': list(self.agents.keys()),
            'sources_count': self._count_sources(results),
            'status': 'complete'
        }

        # Save results using output adapters
        output_locations = await self.save_results(results, metadata)
        results['output_locations'] = output_locations

        self.logger.info("Research workflow completed successfully")

        return results

    def _extract_tags(self, topic: str) -> List[str]:
        """Extract tags from topic"""
        # Simple implementation - can be enhanced
        tags = ['research']
        tags.extend(topic.lower().split())
        return tags

    def _count_sources(self, results: Dict) -> int:
        """Count total sources"""
        count = 0
        for phase_name, phase_data in results.items():
            if phase_name != "final_report":
                count += len(phase_data.get("urls", []))
        return count
```

**CLI Changes:**

```python
# cli/main.py

@cli.command()
@click.argument('topic')
@click.option('--config', '-c', default='config/config.yaml', help='Path to config file')
@click.option('--output', '-o', default=None, help='Output file path (legacy, use --format)')
@click.option('--format', default=None, help='Output format(s): markdown, notion, confluence (comma-separated)')
@click.option('--obsidian-vault', default=None, help='Path to Obsidian vault (overrides config)')
@click.option('--notion-database', default=None, help='Notion database ID (overrides config)')
@click.option('--confluence-space', default=None, help='Confluence space key (overrides config)')
@click.option('--provider', default=None, help='Override default provider for all agents')
@click.option('--model', default=None, help='Override default model')
@click.option('--hil/--no-hil', default=False, help='Enable Human-in-the-Loop mode')
@click.option('--auto-approve', is_flag=True, help='Auto-approve all checkpoints (for testing)')
def research(topic, config, output, format, obsidian_vault, notion_database,
             confluence_space, provider, model, hil, auto_approve):
    """Start a research workflow on a topic"""

    console.print(Panel.fit(
        f"[bold blue]Multi-Agent Research Orchestrator[/bold blue]\n"
        f"Topic: [green]{topic}[/green]",
        border_style="blue"
    ))

    # Load and override config
    config_dict = _load_and_override_config(
        config, hil, auto_approve, format,
        obsidian_vault, notion_database, confluence_space
    )

    # ... rest of existing code ...

    # Display output locations
    if 'output_locations' in results:
        _display_output_locations(results['output_locations'])

def _load_and_override_config(config_path, hil, auto_approve, format_override,
                               obsidian_vault, notion_database, confluence_space):
    """Load config and apply overrides"""
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    # HIL overrides
    if 'hil' not in config_dict:
        config_dict['hil'] = {}
    config_dict['hil']['enabled'] = hil
    config_dict['hil']['auto_approve'] = auto_approve

    # Output format overrides
    if format_override:
        formats = [f.strip() for f in format_override.split(',')]
        config_dict['output']['formats'] = formats

    # Obsidian overrides
    if obsidian_vault:
        if 'markdown' not in config_dict['output']:
            config_dict['output']['markdown'] = {}
        if 'obsidian' not in config_dict['output']['markdown']:
            config_dict['output']['markdown']['obsidian'] = {}
        config_dict['output']['markdown']['obsidian']['vault_path'] = obsidian_vault

    # Notion overrides
    if notion_database:
        if 'notion' not in config_dict['output']:
            config_dict['output']['notion'] = {}
        config_dict['output']['notion']['database_id'] = notion_database

    # Confluence overrides
    if confluence_space:
        if 'confluence' not in config_dict['output']:
            config_dict['output']['confluence'] = {}
        config_dict['output']['confluence']['space_key'] = confluence_space

    return config_dict

def _display_output_locations(output_locations: List[Dict]):
    """Display output locations"""
    console.print("\n[bold cyan]Output Locations:[/bold cyan]")

    table = Table()
    table.add_column("Format", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Location", style="yellow")

    for output in output_locations:
        status = "✓" if output['status'] == 'success' else "✗"
        location = output.get('location', output.get('error', 'N/A'))
        table.add_row(output['format'], status, location)

    console.print(table)
```

**Factory Function:**

```python
# core/outputs/__init__.py

from typing import Dict, Any
from .base_adapter import OutputAdapter
from .markdown_adapter import MarkdownAdapter

def create_output_adapter(format_name: str, config: Dict[str, Any]) -> OutputAdapter:
    """Factory function to create output adapters"""

    adapters = {
        'markdown': MarkdownAdapter,
    }

    # Lazy import for optional dependencies
    if format_name == 'notion':
        try:
            from .notion_adapter import NotionAdapter
            adapters['notion'] = NotionAdapter
        except ImportError:
            raise ImportError("notion-client not installed. Run: pip install notion-client")

    if format_name == 'confluence':
        try:
            from .confluence_adapter import ConfluenceAdapter
            adapters['confluence'] = ConfluenceAdapter
        except ImportError:
            raise ImportError("atlassian-python-api not installed. Run: pip install atlassian-python-api")

    if format_name not in adapters:
        raise ValueError(f"Unknown output format: {format_name}")

    return adapters[format_name](config)

def get_available_adapters() -> List[str]:
    """Get list of available output adapters"""
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
```

---

## CLI Examples

```bash
# Standard markdown output (backward compatible)
python -m cli.main research "AI Trends 2025"

# Enhanced markdown with Obsidian features
python -m cli.main research "AI Trends 2025" --format markdown

# Export to specific Obsidian vault
python -m cli.main research "AI Trends 2025" --obsidian-vault "D:/Obsidian/Research"

# Export to Notion
python -m cli.main research "AI Trends 2025" --format notion --notion-database abc123

# Export to Confluence
python -m cli.main research "AI Trends 2025" --format confluence --confluence-space RESEARCH

# Multiple formats simultaneously
python -m cli.main research "AI Trends 2025" --format markdown,notion

# All formats with HIL
python -m cli.main research "AI Trends 2025" --format markdown,notion,confluence --hil
```

---

## Dependencies

Add to `requirements.txt`:

```txt
# Output adapters
python-frontmatter>=1.0.1
markdown>=3.5.1

# Optional: Notion integration
# notion-client>=2.2.1

# Optional: Confluence integration
# atlassian-python-api>=3.41.0
```

Add to `requirements-optional.txt`:

```txt
# Notion integration
notion-client>=2.2.1

# Confluence integration
atlassian-python-api>=3.41.0
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_markdown_adapter.py - Already shown above

# tests/test_notion_adapter.py
@pytest.mark.integration
@pytest.mark.skipif(not has_notion, reason="notion-client not installed")
async def test_notion_adapter_creates_page():
    adapter = NotionAdapter(notion_config)
    page_url = await adapter.export_report(sample_report, metadata)
    assert "notion.so" in page_url

# tests/test_confluence_adapter.py
@pytest.mark.integration
@pytest.mark.skipif(not has_confluence, reason="atlassian-python-api not installed")
async def test_confluence_adapter_creates_page():
    adapter = ConfluenceAdapter(confluence_config)
    page_url = await adapter.export_report(sample_report, metadata)
    assert "/wiki/" in page_url

# tests/test_output_factory.py
def test_create_markdown_adapter():
    adapter = create_output_adapter('markdown', {})
    assert isinstance(adapter, MarkdownAdapter)

def test_get_available_adapters():
    adapters = get_available_adapters()
    assert 'markdown' in adapters
```

### Integration Tests

```python
# tests/integration/test_full_workflow.py

@pytest.mark.integration
async def test_full_workflow_with_markdown_output():
    orchestrator = ResearchOrchestrator('config/test_config.yaml')
    results = await orchestrator.execute_workflow("Test Topic")

    assert 'output_locations' in results
    assert any(loc['format'] == 'markdown' for loc in results['output_locations'])

    # Check folder structure
    markdown_location = next(
        loc['location'] for loc in results['output_locations']
        if loc['format'] == 'markdown'
    )

    assert Path(markdown_location).exists()
```

---

## Migration Guide

### For Existing Users

**Step 1:** Update configuration (optional)

The new system is backward compatible. Existing single-file output continues to work.

```yaml
# Minimal change - no changes needed
output:
  format: "markdown"
  output_directory: "./reports"
```

**Step 2:** Enable enhanced features (optional)

```yaml
output:
  formats:
    - markdown

  markdown:
    enabled: true
    output_directory: "./reports"

    structure:
      create_topic_folder: true
      save_agent_outputs: true
```

**Step 3:** Add Obsidian support (optional)

```yaml
output:
  markdown:
    obsidian:
      enabled: true
      vault_path: "D:/Obsidian/Research"
      use_wikilinks: true
      create_moc: true
```

---

## Documentation Updates

### Files to Update

1. **CLAUDE.md**
   - Add "Output System" section
   - Document output adapter architecture
   - Add configuration examples
   - Add CLI examples

2. **README.md**
   - Update "Output Formats" section
   - Add Obsidian integration guide
   - Add Notion integration guide
   - Add Confluence integration guide

3. **New: docs/output_adapters.md**
   - Detailed guide for each adapter
   - Configuration reference
   - API documentation
   - Troubleshooting

4. **New: docs/obsidian_integration.md**
   - Step-by-step Obsidian setup
   - Vault organization tips
   - Dataview examples
   - Graph view optimization

---

## Future Enhancements

### Phase 5+

- **Bi-directional Sync**
  - Sync changes back from Notion/Confluence
  - Update research when sources change
  - Version control integration

- **Template System**
  - Custom templates per format
  - User-defined layouts
  - Organization-specific branding

- **Additional Formats**
  - PDF export with LaTeX
  - DOCX export
  - HTML website generation
  - Jupyter notebooks

- **Collaborative Features**
  - Real-time collaboration
  - Team workspaces
  - Shared research databases
  - Comment and review systems

- **Export Scheduling**
  - Periodic exports to cloud
  - Automatic backups
  - Incremental updates

- **Analytics**
  - Research session analytics
  - Source quality metrics
  - Agent performance tracking

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits | Medium | Medium | Implement retry logic, backoff |
| Large file handling | Low | Medium | Stream large files, pagination |
| Network failures | Medium | High | Retry mechanism, local caching |
| Breaking API changes | Low | High | Version pinning, adapter abstraction |

### User Experience Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Configuration complexity | Medium | Medium | Sensible defaults, validation |
| Backward compatibility | Low | High | Maintain legacy behavior |
| Performance degradation | Low | Medium | Async operations, optimization |

---

## Success Metrics

### Phase 1 (Markdown/Obsidian)

- [ ] Folder structure created correctly
- [ ] All agent outputs saved separately
- [ ] Artifacts organized by type
- [ ] Obsidian wikilinks work
- [ ] MOC file generated
- [ ] Metadata preserved
- [ ] Tests pass with >90% coverage
- [ ] Documentation complete

### Phase 2 (Notion)

- [ ] Pages created in Notion
- [ ] Hierarchical structure maintained
- [ ] Properties set correctly
- [ ] Content formatted properly
- [ ] Integration tests pass

### Phase 3 (Confluence)

- [ ] Pages created in Confluence
- [ ] Markdown converted correctly
- [ ] Labels added
- [ ] Child pages created
- [ ] Integration tests pass

### Phase 4 (Integration)

- [ ] Multiple formats work simultaneously
- [ ] CLI options functional
- [ ] Error handling robust
- [ ] Performance acceptable (<5s overhead)
- [ ] User feedback positive

---

## Timeline Estimate

| Phase | Effort | Duration |
|-------|--------|----------|
| Phase 1: Markdown/Obsidian | High | 2-3 days |
| Phase 2: Notion | Medium | 1-2 days |
| Phase 3: Confluence | Medium | 1-2 days |
| Phase 4: Integration | Low | 1 day |
| Testing & Documentation | Medium | 1-2 days |
| **Total** | | **6-10 days** |

---

## Approval Checklist

- [ ] Architecture reviewed and approved
- [ ] Configuration schema validated
- [ ] Security considerations addressed
- [ ] Performance impact acceptable
- [ ] Documentation plan complete
- [ ] Testing strategy defined
- [ ] Migration path clear
- [ ] Ready to implement

---

## Next Steps

1. **Review this plan** and provide feedback
2. **Prioritize phases** (can implement incrementally)
3. **Approve to proceed** with Phase 1 (Markdown/Obsidian)
4. **Create feature branch** for implementation
5. **Begin implementation** following TDD approach

---

**Plan Author:** Claude (AI Assistant)
**Plan Date:** 2025-01-14
**Status:** Awaiting Approval
**Version:** 1.0


---

## 📋 Implementation Status

**Phase 1: Markdown/Obsidian Adapter** - ✅ COMPLETED (2025-01-14)

### Files Created:
- ✅ `core/outputs/__init__.py` - Factory and initialization
- ✅ `core/outputs/base_adapter.py` - Abstract base class
- ✅ `core/outputs/markdown_adapter.py` - Full Markdown/Obsidian implementation

### Files Modified:
- ✅ `core/orchestrator.py` - Integrated output adapter support
- ✅ `cli/main.py` - Added output location display, updated config
- ✅ `tests/test_markdown_adapter.py` - Basic test suite

### Features Implemented:
- ✅ Enhanced Markdown output with frontmatter
- ✅ Organized folder structure (agents/, artifacts/, data/)
- ✅ Obsidian wikilinks and tags
- ✅ MOC (Map of Content) generation
- ✅ Metadata preservation (YAML)
- ✅ Agent outputs saved separately
- ✅ Artifact organization by type
- ✅ Raw data export for reproducibility
- ✅ Obsidian callouts for key sections

### Success Metrics:
- ✅ Folder structure created correctly
- ✅ All agent outputs saved separately
- ✅ Artifacts organized by type
- ✅ Obsidian wikilinks work
- ✅ MOC file generated
- ✅ Metadata preserved
- ⚠️ Tests pass (basic coverage, needs expansion)
- ⚠️ Documentation needs update

### Next Steps:
1. Update CLAUDE.md with output system documentation
2. Update tidyup_and_user_manual.md to include new features
3. Run integration tests
4. Phase 2: Notion adapter (future)
5. Phase 3: Confluence adapter (future)

---

**Status Summary:** Phase 1 successfully implemented. System is backward compatible and ready for use. Enhanced Markdown/Obsidian output is fully functional.

