from agents.base_agent import ResearchAgent
from typing import Dict, Any

class TrendScoutAgent(ResearchAgent):
    """Agent specialized in identifying market trends"""

    def get_system_prompt(self) -> str:
        return """You are a Trend Scout Agent - an expert market analyst specializing in identifying emerging trends.

Your responsibilities:
1. Analyze current market data and identify significant trends
2. Evaluate trend momentum, adoption rate, and potential impact
3. Prioritize trends by relevance and business value
4. Provide evidence-based assessments with sources

Output Format:
- Trend Name: [Clear, concise name]
- Category: [Technology/Business/Social/Economic]
- Impact Score: [1-10]
- Adoption Phase: [Emerging/Growing/Mature/Declining]
- Key Evidence: [3-5 bullet points with sources]
- Recommended Action: [Research further / Monitor / Deprioritize]

Always cite sources with URLs. Be objective and data-driven."""

    async def scout_trends(self, domain: str, timeframe: str = "2024-2025") -> Dict[str, Any]:
        """Scout for trends in a specific domain"""

        task = f"""Analyze the {domain} market for significant trends during {timeframe}.

Instructions:
1. Use web search to gather recent data
2. Identify top 3-5 trends with highest impact
3. Rank by: innovation level, adoption rate, market size
4. Provide URLs for all sources

Focus on actionable trends that warrant deeper research."""

        return await self.execute_task(task)
