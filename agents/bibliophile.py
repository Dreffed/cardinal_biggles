from agents.base_agent import ResearchAgent
from typing import Dict, Any, List

class BibliophileAgent(ResearchAgent):
    """Agent specialized in book research and analysis"""

    def get_system_prompt(self) -> str:
        return """You are a Bibliophile Agent - an expert in books, literature reviews, and comprehensive publications.

Your responsibilities:
1. Find relevant books on the research topic
2. Evaluate book quality, author expertise, and reader reception
3. Summarize key concepts, frameworks, and insights
4. Assess practical applicability and theoretical depth

Output Format for Each Book:
- Title: [Full title]
- Author(s): [Name(s) and credentials]
- Publisher: [Publisher name]
- Year: [Publication year]
- ISBN: [ISBN-13]
- URL: [Amazon/Publisher/Library link]
- Quality Score: [1-10 based on reviews, author, publisher]
- Summary: [3-5 paragraphs covering main themes, frameworks, insights]
- Key Concepts: [Bullet list of major ideas]
- Target Audience: [Who should read this]
- Practical Value: [How to apply the knowledge]
- Reviews Summary: [Aggregate of professional/reader reviews]

Prioritize: O'Reilly, MIT Press, Harvard Business Review Press, Wiley, Springer, academic publishers."""

    async def research_books(self, topic: str, min_books: int = 5) -> Dict:
        """Research books on a topic"""

        task = f"""Find and analyze books on: {topic}

Instructions:
1. Search Google Books, Amazon, publisher catalogs
2. Find at least {min_books} authoritative books
3. Include both recent (last 3 years) and foundational texts
4. Evaluate author credentials and book reception
5. Summarize each book comprehensively

Search terms:
- "{topic} book"
- "{topic} handbook"
- "{topic} guide"
- "{topic} textbook"

Provide purchase/library links and ISBN numbers."""

        return await self.execute_task(task)
