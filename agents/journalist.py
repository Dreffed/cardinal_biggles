from agents.base_agent import ResearchAgent
from typing import Dict, Any, List

class JournalistAgent(ResearchAgent):
    """Agent specialized in news analysis and current events"""

    def get_system_prompt(self) -> str:
        return """You are a Journalist Agent - an expert in analyzing news articles, press releases, and current events.

Your responsibilities:
1. Find relevant news articles from credible sources
2. Evaluate source credibility and potential bias
3. Summarize key points and extract factual information
4. Identify trends and sentiment in news coverage

Output Format for Each Article:
- Headline: [Original headline]
- Source: [Publication name]
- Date: [Publication date]
- URL: [Direct link]
- Credibility: [High/Medium/Low + justification]
- Bias Assessment: [Left/Center/Right or Balanced + evidence]
- Summary: [2-3 paragraphs of key facts]
- Key Quotes: [Notable quotes with attribution]
- Impact Assessment: [How this news affects the trend]
- Sentiment: [Positive/Neutral/Negative toward the topic]

Prioritize: Reuters, Bloomberg, IEEE Spectrum, TechCrunch, Wired, MIT Technology Review, reputable industry publications."""

    async def research_news(self, topic: str, days_back: int = 90, min_articles: int = 10) -> Dict:
        """Research recent news on a topic"""

        task = f"""Find and analyze recent news articles on: {topic}

Instructions:
1. Search for articles from the last {days_back} days
2. Find at least {min_articles} articles from diverse sources
3. Prioritize major tech/business publications
4. Evaluate each article for credibility and bias
5. Identify patterns and themes in coverage

Search queries to use:
- "{topic} news"
- "{topic} announcement"
- "{topic} industry"
- "{topic} market"

Include publication dates and direct URLs."""

        return await self.execute_task(task)
