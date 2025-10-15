"""
Base class for output adapters
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class OutputAdapter(ABC):
    """Base class for all output adapters"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize adapter with configuration

        Args:
            config: Configuration dictionary for this adapter
        """
        self.config = config
        self.format_name = self.__class__.__name__.replace('Adapter', '').lower()

    @abstractmethod
    async def export_report(self, report_data: Dict, metadata: Dict) -> str:
        """
        Export final report

        Args:
            report_data: Complete report data including:
                - content: Main report content (markdown)
                - agent_outputs: Dictionary of agent results
                - artifacts: Dictionary of research artifacts by type
                - raw_data: Raw data (knowledge_store, url_tracker, etc.)
            metadata: Report metadata including:
                - topic: Research topic
                - date: ISO format date
                - tags: List of tags
                - agents: List of agent names
                - sources_count: Total number of sources
                - status: Completion status

        Returns:
            Output location (file path, URL, etc.)

        Raises:
            Exception: If export fails
        """
        pass

    @abstractmethod
    async def export_artifact(
        self,
        artifact_type: str,
        content: str,
        metadata: Dict
    ) -> str:
        """
        Export individual research artifact

        Args:
            artifact_type: Type of artifact (trend, paper, article, book)
            content: Artifact content
            metadata: Artifact metadata

        Returns:
            Output location

        Raises:
            Exception: If export fails
        """
        pass

    @abstractmethod
    def get_output_location(self) -> str:
        """
        Return output location (path, URL, etc.)

        Returns:
            Location string
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate adapter configuration

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        return True
