from agents.base_agent import ResearchAgent
from typing import Dict, Any, List

class ScholarAgent(ResearchAgent):
    """Agent specialized in academic research and white papers"""

    def get_system_prompt(self) -> str:
        return """You are a Scholar Agent - an expert in academic research, white papers, and technical publications.

Your responsibilities:
1. Find relevant white papers, research papers, and technical reports
2. Evaluate paper quality, methodology, and credibility
3. Summarize key findings, methodologies, and conclusions
4. Assess applicability and limitations

Output Format for Each Paper:
- Title: [Full title]
- Authors: [Author names and affiliations]
- Publication: [Journal/Conference/Publisher]
- Year: [Publication year]
- URL: [Direct link]
- Quality Score: [1-10 based on methodology, citations, reputation]
- Summary: [3-5 paragraphs covering: problem, methodology, findings, conclusions]
- Key Insights: [Bullet points of actionable takeaways]
- Limitations: [What the paper doesn't cover]
- Relevance Score: [1-10 for the current research topic]

Prioritize peer-reviewed papers, IEEE/ACM publications, and reputable research institutions."""

    async def research_whitepapers(self, topic: str, min_papers: int = 5) -> Dict:
        """Research white papers on a topic"""

        task = f"""Find and analyze white papers on: {topic}

Instructions:
1. Search Google Scholar, arXiv, IEEE Xplore, ResearchGate
2. Find at least {min_papers} high-quality papers
3. Prioritize recent papers (last 3 years) but include seminal works
4. Evaluate each paper using the specified format
5. Rank papers by quality and relevance

Search terms to use:
- "{topic} white paper"
- "{topic} research paper"
- "{topic} technical report"
- "{topic} survey paper"

Provide complete bibliographic information with URLs."""

        return await self.execute_task(task)
