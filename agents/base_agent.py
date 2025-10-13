from typing import List, Dict, Any, Optional
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from core.knowledge_store import DocumentType

class ResearchAgent(ABC):
    """Base class for all research agents"""

    def __init__(
        self,
        agent_id: str,
        role: str,
        llm,
        knowledge_store,
        tools: List = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.llm = llm
        self.knowledge_store = knowledge_store
        self.tools = tools or []
        self.memory: List[Dict] = []

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    async def execute_task(
        self,
        task_description: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a research task"""

        # Build messages
        messages = [
            SystemMessage(content=self.get_system_prompt()),
        ]

        # Add context if provided
        if context:
            context_msg = f"Context from previous research:\n{self._format_context(context)}"
            messages.append(HumanMessage(content=context_msg))

        # Add task
        messages.append(HumanMessage(content=task_description))

        # Execute with LLM
        response = await self.llm.ainvoke(messages)

        # Store in memory
        result = {
            "agent_id": self.agent_id,
            "role": self.role,
            "task": task_description,
            "result": response.content,
            "timestamp": datetime.now().isoformat(),
            "urls": self._extract_urls(response.content)
        }

        self.memory.append(result)

        # Store in knowledge base
        doc_id = await self._store_knowledge(result)
        result["knowledge_doc_id"] = doc_id

        return result

    def _format_context(self, context: Dict) -> str:
        """Format context for LLM consumption"""
        formatted = []
        for key, value in context.items():
            if isinstance(value, list):
                formatted.append(f"{key}:\n" + "\n".join(f"  - {v}" for v in value))
            else:
                formatted.append(f"{key}: {value}")
        return "\n\n".join(formatted)

    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from content"""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, content)

    async def _store_knowledge(self, result: Dict) -> str:
        """
        Store research result in knowledge base

        Fixed: 2025-01-13 - Added missing source and document_type parameters
        See: dev_plans/fix_store_knowledge_method.md

        Args:
            result: Dictionary containing task results with keys:
                    - result: The actual content to store
                    - agent_id: Source agent identifier
                    - role: Agent role
                    - timestamp: ISO format timestamp
                    - urls: List of extracted URLs

        Returns:
            str: Document ID from knowledge store

        Raises:
            KeyError: If required keys missing from result dict
        """
        doc_id = await self.knowledge_store.add_document(
            content=result["result"],
            source=self.agent_id,
            document_type=DocumentType.AGENT_OUTPUT,
            metadata={
                "agent_id": self.agent_id,
                "role": self.role,
                "timestamp": result["timestamp"],
                "urls": result["urls"]
            },
            tags=[self.role, "research"]
        )
        return doc_id
