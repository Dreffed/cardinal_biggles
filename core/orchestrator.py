"""
Orchestrator for CB workflows
"""
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime
from core.llm_factory import LLMFactory
from core.knowledge_store import SimpleKnowledgeStore
from core.hil_controller import HILController, create_hil_controller
from core.outputs import create_output_adapter
from agents.coordinator import CoordinatorAgent
from agents.trend_scout import TrendScoutAgent
from agents.historian import HistorianAgent
from agents.scholar import ScholarAgent
from agents.journalist import JournalistAgent
from agents.bibliophile import BibliophileAgent
from agents.reporter import ReporterAgent
import logging

class ResearchOrchestrator:
    """Main orchestrator with multi-provider support"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.llm_factory = LLMFactory(config_path)
        self.knowledge_store = SimpleKnowledgeStore()

        # Setup logging
        self._setup_logging()

        # Initialize HIL controller
        self.hil_controller = create_hil_controller(self.llm_factory.config)

        # Initialize output adapters
        self.output_adapters = self._initialize_output_adapters()

        # Initialize agents with provider-specific LLMs
        self.agents = self._initialize_agents()

        self.logger.info("Research Orchestrator initialized")
        self._log_agent_configurations()

    def _setup_logging(self):
        """Setup logging based on config"""
        log_config = self.llm_factory.get_logging_config()

        logging.basicConfig(
            level=getattr(logging, log_config['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config['file']),
                logging.StreamHandler() if log_config['console'] else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_agents(self) -> Dict:
        """Initialize all agents with their configured LLM providers"""

        print("\nInitializing Research Agents...\n")

        agents = {}

        # Trend Scout - Using Perplexity for web search
        agents["trend_scout"] = TrendScoutAgent(
            agent_id="trend_scout_1",
            role="trend_scout",
            llm=self.llm_factory.create_agent_llm("trend_scout"),
            knowledge_store=self.knowledge_store
        )

        # Historian - Using Perplexity for historical research
        agents["historian"] = HistorianAgent(
            agent_id="historian_1",
            role="historian",
            llm=self.llm_factory.create_agent_llm("historian"),
            knowledge_store=self.knowledge_store
        )

        # Scholar - Using Claude for academic analysis
        agents["scholar"] = ScholarAgent(
            agent_id="scholar_1",
            role="scholar",
            llm=self.llm_factory.create_agent_llm("scholar"),
            knowledge_store=self.knowledge_store
        )

        # Journalist - Using Perplexity for current news
        agents["journalist"] = JournalistAgent(
            agent_id="journalist_1",
            role="journalist",
            llm=self.llm_factory.create_agent_llm("journalist"),
            knowledge_store=self.knowledge_store
        )

        # Bibliophile - Using Claude for book analysis
        agents["bibliophile"] = BibliophileAgent(
            agent_id="bibliophile_1",
            role="bibliophile",
            llm=self.llm_factory.create_agent_llm("bibliophile"),
            knowledge_store=self.knowledge_store
        )

        # Reporter - Using Claude Opus for final synthesis
        agents["reporter"] = ReporterAgent(
            agent_id="reporter_1",
            role="reporter",
            llm=self.llm_factory.create_agent_llm("reporter"),
            knowledge_store=self.knowledge_store
        )

        # Coordinator - Using Ollama (doesn't need expensive models)
        coordinator_llm = self.llm_factory.create_agent_llm("coordinator")
        agents["coordinator"] = CoordinatorAgent(
            llm=coordinator_llm,
            knowledge_store=self.knowledge_store,
            agents=agents,
            hil_controller=self.hil_controller
        )

        print("\nAll agents initialized successfully\n")

        return agents

    def _log_agent_configurations(self):
        """Log agent configurations for transparency"""
        self.logger.info("Agent Configurations:")
        for agent_name, agent in self.agents.items():
            if agent_name != "coordinator":
                self.logger.info(f"  {agent_name}: {agent.llm.__class__.__name__}")

    def _initialize_output_adapters(self) -> List:
        """Initialize all enabled output adapters"""
        output_config = self.llm_factory.config.get('output', {})
        adapters = []

        # Get enabled formats (default to markdown)
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

        # Fallback to markdown if no adapters
        if not adapters:
            self.logger.warning("No output adapters initialized, using default markdown")
            default_config = output_config.get('markdown', {
                'output_directory': output_config.get('output_directory', './reports')
            })
            adapters.append(create_output_adapter('markdown', default_config))

        return adapters

    async def execute_workflow(self, topic: str) -> Dict:
        """Execute the complete research workflow"""
        self.logger.info(f"Starting research workflow for topic: {topic}")

        coordinator = self.agents["coordinator"]
        results = await coordinator.execute_research_workflow(topic)

        # Build metadata
        metadata = self._build_metadata(topic, results)

        # Save results using output adapters
        output_locations = await self.save_results(results, metadata)
        results['output_locations'] = output_locations

        # Save intermediate results if configured (legacy)
        output_config = self.llm_factory.get_output_config()
        if output_config.get('save_intermediate_results'):
            self._save_intermediate_results(results, topic)

        self.logger.info("Research workflow completed successfully")

        return results

    def _build_metadata(self, topic: str, results: Dict) -> Dict:
        """Build metadata for the research session"""
        metadata = {
            'topic': topic,
            'date': datetime.now().isoformat(),
            'tags': self._extract_tags(topic),
            'agents': [name for name in self.agents.keys() if name != "coordinator"],
            'sources_count': self._count_sources(results),
            'status': results.get('status', 'complete')
        }

        # Add HIL summary if available
        if 'hil_summary' in results:
            metadata['hil'] = results['hil_summary']

        return metadata

    def _extract_tags(self, topic: str) -> List[str]:
        """Extract tags from topic"""
        tags = ['research']
        # Add topic words as tags
        words = topic.lower().split()
        tags.extend([word for word in words if len(word) > 3])
        return tags[:10]  # Limit to 10 tags

    def _count_sources(self, results: Dict) -> int:
        """Count total sources from all phases"""
        count = 0
        for phase_name, phase_data in results.items():
            if phase_name not in ["final_report", "output_locations", "hil_summary", "status"]:
                if isinstance(phase_data, dict):
                    count += len(phase_data.get("urls", []))
        return count

    async def save_results(self, results: Dict, metadata: Dict) -> List[Dict]:
        """Save results to all enabled output formats"""
        output_locations = []

        # Prepare report data
        report_data = {
            'content': results.get('final_report', ''),
            'agent_outputs': self._extract_agent_outputs(results),
            'artifacts': self._extract_artifacts(results),
            'raw_data': self._extract_raw_data(results)
        }

        for adapter in self.output_adapters:
            try:
                self.logger.info(f"Exporting to {adapter.format_name}...")

                location = await adapter.export_report(report_data, metadata)

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

    def _extract_agent_outputs(self, results: Dict) -> Dict:
        """Extract agent outputs from results"""
        agent_outputs = {}
        for phase_name, phase_data in results.items():
            if phase_name in ["trends", "history", "white_papers", "news", "books"]:
                agent_outputs[phase_name] = phase_data
        return agent_outputs

    def _extract_artifacts(self, results: Dict) -> Dict:
        """Extract artifacts from results"""
        artifacts = {
            'trends': self._parse_trends(results.get('trends', {})),
            'papers': self._parse_papers(results.get('white_papers', {})),
            'articles': self._parse_articles(results.get('news', {})),
            'books': self._parse_books(results.get('books', {}))
        }
        return artifacts

    def _parse_trends(self, trend_results: Dict) -> List[Dict]:
        """Parse trends from TrendScoutAgent results"""
        import re

        trends = []
        result_text = trend_results.get('result', '')
        urls = trend_results.get('urls', [])

        if not result_text:
            return trends

        # Split by trend sections - look for patterns like "Trend Name:" or numbered trends
        trend_blocks = re.split(r'\n(?=(?:Trend\s+(?:Name|#?\d+)[:\s])|(?:\d+\.\s+\*\*[A-Z]))', result_text)

        for idx, block in enumerate(trend_blocks):
            if not block.strip():
                continue

            trend = {}

            # Try multiple patterns for trend extraction
            # Pattern 1: "Trend Name: ..." format
            name_match = re.search(r'Trend\s+Name:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            if not name_match:
                # Pattern 2: "1. **Trend Name**" format
                name_match = re.search(r'^\d+\.\s+\*\*([^*]+)\*\*', block)
            if not name_match:
                # Pattern 3: "Trend #1:" format
                name_match = re.search(r'Trend\s+#?\d+:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)

            if name_match:
                trend['title'] = name_match.group(1).strip()

                # Extract additional fields if available
                category_match = re.search(r'Category:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
                if category_match:
                    trend['category'] = category_match.group(1).strip()

                impact_match = re.search(r'Impact\s+Score:\s*(\d+)', block, re.IGNORECASE)
                if impact_match:
                    trend['impact_score'] = int(impact_match.group(1))

                adoption_match = re.search(r'Adoption\s+Phase:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
                if adoption_match:
                    trend['adoption_phase'] = adoption_match.group(1).strip()

                # Store full content
                trend['content'] = block.strip()

                # Try to match URLs (simple heuristic: match if trend title words appear in URL)
                if 'title' in trend and urls:
                    title_words = [w.lower() for w in trend['title'].split() if len(w) > 3]
                    for url in urls[:10]:  # Check first 10 URLs
                        url_lower = url.lower()
                        if any(word in url_lower for word in title_words):
                            trend['url'] = url
                            break

                trends.append(trend)

        return trends

    def _parse_papers(self, scholar_results: Dict) -> List[Dict]:
        """Parse papers from ScholarAgent results"""
        import re

        papers = []
        result_text = scholar_results.get('result', '')
        urls = scholar_results.get('urls', [])

        if not result_text:
            return papers

        # Look for various citation patterns
        # Pattern 1: "Title" by Authors (Year)
        pattern1 = r'"([^"]+)"\s+by\s+([^(]+)\s+\((\d{4})\)'
        for match in re.finditer(pattern1, result_text):
            paper = {
                'title': match.group(1).strip(),
                'authors': match.group(2).strip(),
                'year': match.group(3),
                'content': match.group(0)
            }
            self._match_url_to_artifact(paper, urls)
            papers.append(paper)

        # Pattern 2: **Paper Title** - Authors, Journal/Conference
        pattern2 = r'\*\*([^*]+)\*\*\s*[-–]\s*([^,\n]+)(?:,\s*([^,\n]+))?'
        for match in re.finditer(pattern2, result_text):
            if not any(p['title'] == match.group(1).strip() for p in papers):  # Avoid duplicates
                paper = {
                    'title': match.group(1).strip(),
                    'authors': match.group(2).strip() if match.group(2) else '',
                    'journal': match.group(3).strip() if match.group(3) else '',
                    'content': match.group(0)
                }
                self._match_url_to_artifact(paper, urls)
                papers.append(paper)

        # Pattern 3: Paper: Title (fallback for simpler formats)
        pattern3 = r'Paper:\s+([^,\n]+)'
        for match in re.finditer(pattern3, result_text):
            title = match.group(1).strip()
            if not any(p['title'] == title for p in papers):  # Avoid duplicates
                paper = {
                    'title': title,
                    'content': match.group(0)
                }
                self._match_url_to_artifact(paper, urls)
                papers.append(paper)

        return papers

    def _parse_articles(self, journalist_results: Dict) -> List[Dict]:
        """Parse articles from JournalistAgent results"""
        import re

        articles = []
        result_text = journalist_results.get('result', '')
        urls = journalist_results.get('urls', [])

        if not result_text:
            return articles

        # Pattern 1: Article: "Title" from Source
        pattern1 = r'Article:\s+"([^"]+)"(?:\s+from\s+([^,\n]+))?'
        for match in re.finditer(pattern1, result_text):
            article = {
                'title': match.group(1).strip(),
                'source': match.group(2).strip() if match.group(2) else '',
                'content': match.group(0)
            }
            self._match_url_to_artifact(article, urls)
            articles.append(article)

        # Pattern 2: **Article Title** - Source
        pattern2 = r'\*\*([^*]+)\*\*\s*[-–]\s*([^,\n]+)'
        for match in re.finditer(pattern2, result_text):
            title = match.group(1).strip()
            if not any(a['title'] == title for a in articles):  # Avoid duplicates
                article = {
                    'title': title,
                    'source': match.group(2).strip(),
                    'content': match.group(0)
                }
                self._match_url_to_artifact(article, urls)
                articles.append(article)

        # Pattern 3: Numbered list of articles "1. Title..."
        pattern3 = r'^\d+\.\s+([^:\n]+):?\s*([^\n]+)?'
        for match in re.finditer(pattern3, result_text, re.MULTILINE):
            title = match.group(1).strip()
            # Filter out section headers
            if len(title) > 10 and not title.endswith(':') and not any(a['title'] == title for a in articles):
                article = {
                    'title': title,
                    'summary': match.group(2).strip() if match.group(2) else '',
                    'content': match.group(0)
                }
                self._match_url_to_artifact(article, urls)
                articles.append(article)

        return articles

    def _parse_books(self, bibliophile_results: Dict) -> List[Dict]:
        """Parse books from BibliophileAgent results"""
        import re

        books = []
        result_text = bibliophile_results.get('result', '')
        urls = bibliophile_results.get('urls', [])

        if not result_text:
            return books

        # Pattern 1: "Book Title" by Author
        pattern1 = r'"([^"]+)"\s+by\s+([^,\n]+)'
        for match in re.finditer(pattern1, result_text):
            book = {
                'title': match.group(1).strip(),
                'author': match.group(2).strip(),
                'content': match.group(0)
            }
            self._match_url_to_artifact(book, urls)
            books.append(book)

        # Pattern 2: **Book Title** - Author
        pattern2 = r'\*\*([^*]+)\*\*\s*[-–]\s*([^,\n]+)'
        for match in re.finditer(pattern2, result_text):
            title = match.group(1).strip()
            if not any(b['title'] == title for b in books):  # Avoid duplicates
                book = {
                    'title': title,
                    'author': match.group(2).strip(),
                    'content': match.group(0)
                }
                self._match_url_to_artifact(book, urls)
                books.append(book)

        # Pattern 3: Book: Title
        pattern3 = r'Book:\s+([^,\n]+)'
        for match in re.finditer(pattern3, result_text):
            title = match.group(1).strip()
            if not any(b['title'] == title for b in books):  # Avoid duplicates
                book = {
                    'title': title,
                    'content': match.group(0)
                }
                self._match_url_to_artifact(book, urls)
                books.append(book)

        return books

    def _match_url_to_artifact(self, artifact: Dict, urls: List[str]) -> None:
        """Helper method to match URLs to artifacts based on title keywords"""
        if 'title' not in artifact or not urls:
            return

        # Extract significant words from title (>3 chars)
        title_words = [w.lower() for w in artifact['title'].split() if len(w) > 3]

        # Try to find a matching URL
        for url in urls:
            url_lower = url.lower()
            # Check if any title words appear in the URL
            if any(word in url_lower for word in title_words[:3]):  # Check first 3 significant words
                artifact['url'] = url
                return

    def _extract_raw_data(self, results: Dict) -> Dict:
        """Extract raw data for reproducibility"""
        raw_data = {}

        # Save knowledge store if available
        if hasattr(self.knowledge_store, 'export_to_dict'):
            raw_data['knowledge_store'] = self.knowledge_store.export_to_dict()

        # Add HIL checkpoints if available
        if 'hil_summary' in results:
            raw_data['hil_checkpoints'] = results['hil_summary']

        return raw_data

    def _save_intermediate_results(self, results: Dict, topic: str):
        """Save intermediate results if configured"""
        output_dir = Path(self.llm_factory.get_output_config()['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each phase result
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = topic.replace(" ", "_").lower()[:50]

        for phase_name, phase_data in results.items():
            if phase_name != "final_report":
                file_path = output_dir / f"{topic_slug}_{phase_name}_{timestamp}.json"
                with open(file_path, 'w') as f:
                    json.dump(phase_data, f, indent=2, default=str)
                self.logger.info(f"Saved {phase_name} results to {file_path}")
