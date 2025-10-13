from typing import Dict
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from core.knowledge_store import SimpleKnowledgeStore
from agents.coordinator import CoordinatorAgent
from agents.trend_scout import TrendScoutAgent
from agents.historian import HistorianAgent
from agents.scholar import ScholarAgent
from agents.journalist import JournalistAgent
from agents.bibliophile import BibliophileAgent
from agents.reporter import ReporterAgent

class ResearchOrchestrator:
    """Main orchestrator for the research system"""

    def __init__(self, llm_provider: str = "ollama", model_name: str = "llama3.1"):
        self.llm = self._initialize_llm(llm_provider, model_name)
        self.knowledge_store = SimpleKnowledgeStore()
        self.agents = self._initialize_agents()

    def _initialize_llm(self, provider: str, model: str):
        """Initialize LLM based on provider"""
        if provider == "ollama":
            return Ollama(model=model, base_url="http://localhost:11434")
        elif provider == "openai":
            return ChatOpenAI(model=model)
        elif provider == "claude":
            return ChatAnthropic(model=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _initialize_agents(self) -> Dict:
        """Initialize all research agents"""
        agents = {
            "trend_scout": TrendScoutAgent(
                agent_id="trend_scout_1",
                role="trend_scout",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            ),
            "historian": HistorianAgent(
                agent_id="historian_1",
                role="historian",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            ),
            "scholar": ScholarAgent(
                agent_id="scholar_1",
                role="scholar",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            ),
            "journalist": JournalistAgent(
                agent_id="journalist_1",
                role="journalist",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            ),
            "bibliophile": BibliophileAgent(
                agent_id="bibliophile_1",
                role="bibliophile",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            ),
            "reporter": ReporterAgent(
                agent_id="reporter_1",
                role="reporter",
                llm=self.llm,
                knowledge_store=self.knowledge_store
            )
        }

        # Create coordinator with access to all agents
        agents["coordinator"] = CoordinatorAgent(
            llm=self.llm,
            knowledge_store=self.knowledge_store,
            agents=agents
        )

        return agents

    async def execute_workflow(self, topic: str) -> Dict:
        """Execute the complete research workflow"""
        coordinator = self.agents["coordinator"]
        return await coordinator.execute_research_workflow(topic)
