"""
Tests for LLM Factory
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock


@pytest.mark.unit
class TestLLMFactory:
    """Test LLM Factory functionality"""

    def test_factory_initialization(self, config_file):
        """Test factory initializes with config"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)

        assert factory.config is not None
        assert 'llm' in factory.config
        assert 'providers' in factory.config['llm']

    def test_load_config(self, config_file):
        """Test config loading"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)

        assert factory.config['llm']['default_provider'] == 'ollama'
        assert 'ollama' in factory.config['llm']['providers']

    def test_environment_variable_expansion(self, test_config_dir):
        """Test environment variable expansion in config"""
        import yaml
        import os
        from core.llm_factory import LLMFactory

        # Set test environment variable
        os.environ['TEST_API_KEY'] = 'test-key-12345'

        # Create config with env var
        config = {
            'llm': {
                'default_provider': 'test',
                'providers': {
                    'test': {
                        'api_key': '${TEST_API_KEY}'
                    }
                }
            }
        }

        config_path = test_config_dir / "env_test_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        factory = LLMFactory(str(config_path))

        assert factory.config['llm']['providers']['test']['api_key'] == 'test-key-12345'

    @pytest.mark.requires_ollama
    def test_create_ollama_llm(self, config_file):
        """Test Ollama LLM creation"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)
        llm = factory.create_llm(provider='ollama', model='llama3.1')

        assert llm is not None
        assert hasattr(llm, 'ainvoke') or hasattr(llm, 'invoke')

    def test_create_agent_llm(self, config_file):
        """Test agent-specific LLM creation"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)
        llm = factory.create_agent_llm('test_agent')

        assert llm is not None

    def test_get_research_config(self, config_file):
        """Test getting research config for agent"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)
        config = factory.get_research_config('test_agent')

        assert config is not None
        assert config.get('max_results') == 5

    def test_missing_config_file(self):
        """Test error handling for missing config"""
        from core.llm_factory import LLMFactory

        with pytest.raises(FileNotFoundError):
            LLMFactory('nonexistent_config.yaml')

    def test_invalid_provider(self, config_file):
        """Test error handling for invalid provider"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)

        with pytest.raises(ValueError):
            factory.create_llm(provider='invalid_provider')


@pytest.mark.integration
@pytest.mark.requires_ollama
class TestLLMFactoryIntegration:
    """Integration tests for LLM Factory"""

    @pytest.mark.asyncio
    async def test_ollama_invoke(self, config_file):
        """Test actual Ollama invocation"""
        from core.llm_factory import LLMFactory

        factory = LLMFactory(config_file)
        llm = factory.create_llm(provider='ollama', model='llama3.1')

        response = await llm.ainvoke("Say 'test' and nothing else")

        assert response is not None
        assert hasattr(response, 'content')
        assert len(response.content) > 0
