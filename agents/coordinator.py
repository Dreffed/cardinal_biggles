from agents.base_agent import ResearchAgent
from typing import Dict, Any, List
import asyncio

class CoordinatorAgent(ResearchAgent):
    """Coordinator agent that orchestrates the research workflow"""

    def __init__(self, llm, knowledge_store, agents: Dict[str, ResearchAgent]):
        super().__init__(
            agent_id="coordinator",
            role="coordinator",
            llm=llm,
            knowledge_store=knowledge_store
        )
        self.agents = agents

    def get_system_prompt(self) -> str:
        return """You are a Coordinator Agent - responsible for orchestrating complex research workflows.

Your responsibilities:
1. Break down research requests into agent-specific tasks
2. Determine optimal task execution order
3. Monitor progress and handle errors
4. Synthesize results from multiple agents
5. Ensure comprehensive coverage of the research topic

Available Agents:
- TrendScout: Identifies market trends
- Historian: Researches historical context
- Scholar: Analyzes white papers and academic research
- Journalist: Reviews news and industry articles
- Bibliophile: Researches books and comprehensive resources
- Reporter: Generates final reports

Your role is strategic coordination, not content research."""

    async def execute_research_workflow(self, topic: str) -> Dict[str, Any]:
        """Execute the complete research workflow"""

        print(f"\n🚀 Starting research workflow for: {topic}\n")

        results = {}

        # Phase 1: Trend Scouting
        print("📊 Phase 1: Scouting market trends...")
        trend_result = await self.agents["trend_scout"].scout_trends(topic)
        results["trends"] = trend_result
        print(f"✓ Found trends. Analysis complete.\n")

        # Extract top trend for deeper research
        top_trend = await self._extract_top_trend(trend_result)

        # Phase 2: Historical Research (parallel with Phase 3-5)
        print(f"📜 Phase 2: Researching history of '{top_trend}'...")
        history_task = asyncio.create_task(
            self.agents["historian"].research_history(top_trend)
        )

        # Phase 3: White Paper Research
        print(f"🎓 Phase 3: Finding white papers on '{top_trend}'...")
        papers_task = asyncio.create_task(
            self.agents["scholar"].research_whitepapers(top_trend, min_papers=5)
        )

        # Phase 4: News Research
        print(f"📰 Phase 4: Analyzing recent news on '{top_trend}'...")
        news_task = asyncio.create_task(
            self.agents["journalist"].research_news(top_trend, days_back=90, min_articles=10)
        )

        # Phase 5: Book Research
        print(f"📚 Phase 5: Finding books on '{top_trend}'...")
        books_task = asyncio.create_task(
            self.agents["bibliophile"].research_books(top_trend, min_books=5)
        )

        # Wait for all parallel research to complete
        history_result, papers_result, news_result, books_result = await asyncio.gather(
            history_task, papers_task, news_task, books_task
        )

        results["history"] = history_result
        results["white_papers"] = papers_result
        results["news"] = news_result
        results["books"] = books_result

        print("✓ All research phases complete.\n")

        # Phase 6: Report Generation
        print("📝 Phase 6: Generating comprehensive report...")
        report = await self.agents["reporter"].generate_report(results)
        results["final_report"] = report
        print("✓ Report generated.\n")

        return results

    async def _extract_top_trend(self, trend_result: Dict) -> str:
        """Extract the top trend from trend scout results"""
        # Parse LLM response to get top trend
        # For seed code, use simple extraction
        content = trend_result.get("result", "")

        # Simple extraction (in production, use structured parsing)
        task = f"""From this trend analysis, extract ONLY the name of the top-ranked trend:

{content}

Return only the trend name, nothing else."""

        messages = [{"role": "user", "content": task}]
        response = await self.llm.ainvoke(messages)

        return response.content.strip()
