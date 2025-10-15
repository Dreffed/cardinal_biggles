"""
Markdown/Obsidian output adapter
"""
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import yaml
import json
import re
from .base_adapter import OutputAdapter

class MarkdownAdapter(OutputAdapter):
    """Markdown/Obsidian output adapter with organized folder structure"""

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
        if self.structure_config.get('timestamp_folders', True):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_slug = self._sanitize_filename(metadata['topic'])[:50]
            folder_name = f"{topic_slug}_{timestamp}"
        else:
            folder_name = self._sanitize_filename(metadata['topic'])[:50]

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
        content = report_data.get('content', report_data.get('final_report', ''))

        # Add Obsidian features
        if self.obsidian_config.get('use_wikilinks', True):
            content = self._add_wikilinks(content, metadata)

        if self.obsidian_config.get('use_callouts', True):
            content = self._convert_to_callouts(content)

        # Combine frontmatter and content
        full_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n{content}"

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
            if agent_name == "coordinator":
                continue  # Skip coordinator

            filename = f"{agent_name}_results.md"
            file_path = folder / filename

            # Build agent output with frontmatter
            frontmatter = {
                'title': f"{agent_name.replace('_', ' ').title()} Results",
                'agent': agent_name,
                'date': output.get('timestamp', datetime.now().isoformat()),
                'tags': [f"agent/{agent_name}", "research"]
            }

            content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
            content += f"# {agent_name.replace('_', ' ').title()} Results\n\n"

            # Get result content
            result_content = output.get('result', '')
            if isinstance(result_content, dict):
                result_content = json.dumps(result_content, indent=2, default=str)

            content += result_content

            # Add URLs if present
            urls = output.get('urls', [])
            if urls:
                content += "\n\n## Sources\n\n"
                for url in urls[:10]:  # Limit to first 10
                    content += f"- {url}\n"
                if len(urls) > 10:
                    content += f"\n*... and {len(urls) - 10} more sources*\n"

            file_path.write_text(content, encoding='utf-8')

    async def _export_artifacts(self, folder: Path, artifacts: Dict):
        """Export research artifacts organized by type"""
        folder.mkdir(parents=True, exist_ok=True)

        # Organize by type
        for artifact_type, items in artifacts.items():
            if not items:
                continue

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

                content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n"
                content += f"# {item.get('title', f'{artifact_type.title()} {idx}')}\n\n"

                if item.get('url'):
                    content += f"**Source:** {item['url']}\n\n"

                if item.get('date'):
                    content += f"**Date:** {item['date']}\n\n"

                content += item.get('content', item.get('summary', item.get('description', '')))

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
        content += f"**Research conducted:** {metadata.get('date', 'N/A')}\n"
        content += f"**Total sources:** {metadata.get('sources_count', 0)}\n"
        content += f"**Status:** {metadata.get('status', 'complete')}\n\n"

        content += "---\n\n"

        # Link to main report
        content += "## Main Report\n"
        content += "- [[report|Main Research Report]]\n\n"

        # Link to agent outputs
        agent_outputs = report_data.get('agent_outputs', {})
        if agent_outputs:
            content += "## Agent Outputs\n"
            for agent_name in agent_outputs.keys():
                if agent_name == "coordinator":
                    continue
                display_name = agent_name.replace('_', ' ').title()
                content += f"- [[agents/{agent_name}_results|{display_name}]]\n"
            content += "\n"

        # Link to artifacts
        artifacts = report_data.get('artifacts', {})
        if artifacts:
            content += "## Research Artifacts\n"
            for artifact_type, items in artifacts.items():
                if not items:
                    continue
                content += f"### {artifact_type.title()} ({len(items)})\n"
                for idx, item in enumerate(items[:5], 1):  # Show first 5
                    title = item.get('title', f'{artifact_type} {idx}')
                    content += f"- [[artifacts/{artifact_type}/{artifact_type}_{idx:03d}|{title}]]\n"
                if len(items) > 5:
                    content += f"- ... and {len(items) - 5} more\n"
                content += "\n"

        # Link to data
        raw_data = report_data.get('raw_data', {})
        if raw_data:
            content += "## Raw Data\n"
            for data_type in raw_data.keys():
                content += f"- `data/{data_type}.json`\n"
            content += "\n"

        # Add tags
        tags = self._generate_tags(metadata)
        content += f"\n---\n\n{tags}"

        moc_path.write_text(content, encoding='utf-8')

    async def _save_metadata(self, folder: Path, metadata: Dict):
        """Save research metadata"""
        metadata_path = folder / 'metadata.yaml'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, default_flow_style=False)

    def _build_frontmatter(self, metadata: Dict) -> Dict:
        """Build YAML frontmatter"""
        return {
            'title': metadata.get('topic', 'Research Report'),
            'date': metadata.get('date', datetime.now().isoformat()),
            'tags': metadata.get('tags', []),
            'agents': metadata.get('agents', []),
            'sources': metadata.get('sources_count', 0),
            'status': metadata.get('status', 'complete'),
            'cssclass': 'research-report'
        }

    def _add_wikilinks(self, content: str, metadata: Dict) -> str:
        """Add wikilinks to content (basic implementation)"""
        # This is a placeholder - could be enhanced with intelligent linking
        return content

    def _convert_to_callouts(self, content: str) -> str:
        """Convert sections to Obsidian callouts"""
        # Convert "Executive Summary" to callout
        content = re.sub(
            r'^## Executive Summary\s*$',
            '## Executive Summary\n\n> [!summary] Executive Summary',
            content,
            flags=re.MULTILINE
        )

        # Convert "Key Insights" to callout
        content = re.sub(
            r'^## Key Insights\s*$',
            '## Key Insights\n\n> [!important] Key Insights',
            content,
            flags=re.MULTILINE
        )

        return content

    def _generate_tags(self, metadata: Dict) -> str:
        """Generate tag string"""
        tags = metadata.get('tags', [])
        if not tags:
            return ""
        return ' '.join([f'#{tag.replace(" ", "-")}' for tag in tags])

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename"""
        # Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        return name.lower()

    async def export_artifact(
        self,
        artifact_type: str,
        content: str,
        metadata: Dict
    ) -> str:
        """Export single artifact"""
        # Create artifacts folder
        artifacts_folder = self.output_dir / 'artifacts' / artifact_type
        artifacts_folder.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = self._sanitize_filename(metadata.get('title', artifact_type))[:30]
        filename = f"{title_slug}_{timestamp}.md"
        file_path = artifacts_folder / filename

        # Build content with frontmatter
        frontmatter = {
            'title': metadata.get('title', artifact_type),
            'type': artifact_type,
            'date': metadata.get('date', datetime.now().isoformat()),
            'tags': [f"artifact/{artifact_type}"]
        }

        full_content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n{content}"

        file_path.write_text(full_content, encoding='utf-8')

        return str(file_path.absolute())

    def get_output_location(self) -> str:
        """Return output directory"""
        return str(self.output_dir.absolute())
