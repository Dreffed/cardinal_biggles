"""
Orchestrator for CB workflows
"""
from typing import Dict, Optional
from pathlib import Path
from core.llm_factory import LLMFactory
from core.knowledge_store import SimpleKnowledgeStore
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

        print("\n🤖 Initializing Research Agents...\n")

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
            agents=agents
        )

        print("\n✓ All agents initialized successfully\n")

        return agents

    def _log_agent_configurations(self):
        """Log agent configurations for transparency"""
        self.logger.info("Agent Configurations:")
        for agent_name, agent in self.agents.items():
            if agent_name != "coordinator":
                self.logger.info(f"  {agent_name}: {agent.llm.__class__.__name__}")

    async def execute_workflow(self, topic: str) -> Dict:
        """Execute the complete research workflow"""
        self.logger.info(f"Starting research workflow for topic: {topic}")

        coordinator = self.agents["coordinator"]
        results = await coordinator.execute_research_workflow(topic)

        # Save report if configured
        output_config = self.llm_factory.get_output_config()
        if output_config.get('save_intermediate_results'):
            self._save_intermediate_results(results, topic)

        self.logger.info("Research workflow completed successfully")

        return results

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
