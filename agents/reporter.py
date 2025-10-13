from agents.base_agent import ResearchAgent
from typing import Dict, List, Any
import json

class ReporterAgent(ResearchAgent):
    """Agent specialized in generating comprehensive research reports"""

    def get_system_prompt(self) -> str:
        return """You are a Reporter Agent - an expert in synthesizing research into comprehensive, well-structured reports.

Your responsibilities:
1. Synthesize findings from all research agents
2. Create a coherent narrative from diverse sources
3. Generate executive summaries and detailed sections
4. Maintain proper citations and reference tables
5. Identify gaps, contradictions, and opportunities

Report Structure:
1. Executive Summary (1-2 pages)
2. Trend Overview
3. Historical Context
4. Academic Research Findings
5. News & Industry Analysis
6. Books & Comprehensive Resources
7. Key Insights & Recommendations
8. Reference Tables (organized by source type)
9. Appendices

Writing Style: Professional, clear, evidence-based, actionable."""

    async def generate_report(self, research_data: Dict[str, Any]) -> str:
        """Generate a comprehensive research report"""

        # Extract data from all agents
        trend_data = research_data.get("trends", {})
        history_data = research_data.get("history", {})
        papers_data = research_data.get("white_papers", {})
        news_data = research_data.get("news", {})
        books_data = research_data.get("books", {})

        task = f"""Generate a comprehensive research report synthesizing all findings.

Research Data Available:
{json.dumps(research_data, indent=2, default=str)[:5000]}

Instructions:
1. Create an executive summary highlighting key findings
2. Synthesize information from all sources
3. Identify patterns, contradictions, and insights
4. Generate actionable recommendations
5. Include complete reference tables with hyperlinks

Format: Markdown with proper headers, lists, and hyperlinks.
Length: Comprehensive (10-20 pages equivalent)"""

        result = await self.execute_task(task)

        # Generate reference tables
        ref_tables = self._generate_reference_tables(research_data)

        # Combine report and tables
        full_report = result["result"] + "\n\n---\n\n" + ref_tables

        return full_report

    def _generate_reference_tables(self, research_data: Dict) -> str:
        """Generate formatted reference tables"""

        tables = ["# Reference Tables\n"]

        # White Papers Table
        if "white_papers" in research_data:
            tables.append("\n## White Papers & Academic Research\n")
            tables.append("| Title | Authors | Year | Quality | URL | Relevance |")
            tables.append("|-------|---------|------|---------|-----|-----------|")
            # Parse and add entries
            papers = self._parse_papers(research_data["white_papers"])
            for paper in papers:
                tables.append(f"| {paper['title']} | {paper['authors']} | {paper['year']} | {paper['quality']}/10 | [{paper['url']}]({paper['url']}) | {paper['relevance']}/10 |")

        # News Articles Table
        if "news" in research_data:
            tables.append("\n## News Articles & Industry Reports\n")
            tables.append("| Headline | Source | Date | Credibility | URL | Impact |")
            tables.append("|----------|--------|------|-------------|-----|--------|")
            # Parse and add entries
            articles = self._parse_articles(research_data["news"])
            for article in articles:
                tables.append(f"| {article['headline']} | {article['source']} | {article['date']} | {article['credibility']} | [{article['url']}]({article['url']}) | {article['impact']} |")

        # Books Table
        if "books" in research_data:
            tables.append("\n## Books & Comprehensive Resources\n")
            tables.append("| Title | Author | Publisher | Year | Quality | URL |")
            tables.append("|-------|--------|-----------|------|---------|-----|")
            # Parse and add entries
            books = self._parse_books(research_data["books"])
            for book in books:
                tables.append(f"| {book['title']} | {book['author']} | {book['publisher']} | {book['year']} | {book['quality']}/10 | [{book['url']}]({book['url']}) |")

        return "\n".join(tables)

    def _parse_papers(self, papers_data: Dict) -> List[Dict]:
        """Parse white papers data into structured format"""
        # Implementation would parse the LLM response
        # For seed code, return empty list
        return []

    def _parse_articles(self, news_data: Dict) -> List[Dict]:
        """Parse news articles into structured format"""
        return []

    def _parse_books(self, books_data: Dict) -> List[Dict]:
        """Parse books data into structured format"""
        return []
