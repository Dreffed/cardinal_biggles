"""
Tests for Base Agent
"""

import pytest


@pytest.mark.unit
class TestBaseAgent:
    """Test Base Agent functionality"""

    @pytest.mark.asyncio
    async def test_agent_creation(self, base_agent):
        """Test agent creation"""
        assert base_agent.agent_id == "test_agent"
        assert base_agent.role == "test"
        assert base_agent.llm is not None
        assert base_agent.knowledge_store is not None

    @pytest.mark.asyncio
    async def test_execute_task(self, base_agent):
        """Test task execution"""
        result = await base_agent.execute_task(
            task_description="Test task",
            context={"key": "value"}
        )

        assert result is not None
        assert 'agent_id' in result
        assert 'result' in result
        assert result['agent_id'] == "test_agent"

    @pytest.mark.asyncio
    async def test_memory_storage(self, base_agent):
        """Test that agent stores results in memory"""
        initial_memory_len = len(base_agent.memory)

        await base_agent.execute_task("Test task")

        assert len(base_agent.memory) > initial_memory_len

    def test_get_system_prompt(self, base_agent):
        """Test system prompt retrieval"""
        prompt = base_agent.get_system_prompt()

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
