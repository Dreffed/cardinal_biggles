"""
Integration tests for complete workflows
"""

import pytest


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test end-to-end workflows"""

    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_simple_research_workflow(self, config_file):
        """Test a simple research workflow"""
        from core.orchestrator import ResearchOrchestrator

        orchestrator = ResearchOrchestrator(config_path=config_file)

        # This would be a full workflow test
        # For now, just test orchestrator creation
        assert orchestrator is not None
        assert orchestrator.agents is not None
        assert 'coordinator' in orchestrator.agents
