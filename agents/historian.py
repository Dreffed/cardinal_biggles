from agents.base_agent import ResearchAgent
from tools.web_search import WebSearchTool, SearchQuery
from tools.url_tracker import URLTracker
from typing import Dict, Any, List

class HistorianAgent(ResearchAgent):
    """Agent specialized in historical research and trend evolution"""

    def get_system_prompt(self) -> str:
        return """You are a Historian Agent - an expert in analyzing the evolution of trends, technologies, and market movements.

Your responsibilities:
1. Research the historical development of identified trends
2. Identify key milestones, inflection points, and pattern changes
3. Analyze success/failure factors from similar past trends
4. Provide timeline context and lessons learned

Output Format:
- Historical Timeline: [Year-by-year or phase-based breakdown]
- Key Milestones: [Major events that shaped the trend]
- Similar Past Trends: [Analogous historical examples]
- Success Factors: [What worked in the past]
- Failure Factors: [What didn't work]
- Lessons Learned: [Actionable insights]

Always provide historical sources with URLs. Look for academic papers, industry reports, and credible archives."""

    async def research_history(self, trend_name: str, depth: str = "comprehensive") -> Dict:
        """Research the historical context of a trend"""

        task = f"""Research the history and evolution of: {trend_name}

Instructions:
1. Search for historical data, academic papers, and industry reports
2. Build a timeline from inception to present
3. Identify similar trends from the past
4. Extract lessons learned

Depth: {depth} - {'Provide detailed analysis with 10+ sources' if depth == 'comprehensive' else 'Provide summary with 5+ sources'}

Include URLs for all historical sources."""

        return await self.execute_task(task)
