from typing import Optional, Dict, Any
from enum import Enum
import os
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatPerplexity
import yaml
from pathlib import Path

class LLMProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"
    PERPLEXITY = "perplexity"

class LLMFactory:
    """Factory for creating LLM instances with provider-specific configurations"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self._validate_api_keys()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        # Expand environment variables
        config = self._expand_env_vars(config)
        return config

    def _expand_env_vars(self, config: Any) -> Any:
        """Recursively expand environment variables in config"""
        if isinstance(config, dict):
            return {k: self._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._expand_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        return config

    def _validate_api_keys(self):
        """Validate that required API keys are present"""
        providers = self.config['llm']['providers']

        # Check each provider that requires an API key
        for provider_name in ['openai', 'claude', 'perplexity']:
            if provider_name in providers:
                api_key = providers[provider_name].get('api_key', '')
                if api_key and api_key.startswith("${"):
                    print(f"⚠️  Warning: {provider_name.upper()} API key not set in environment")

    def create_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """Create an LLM instance based on provider"""

        # Use defaults if not specified
        if provider is None:
            provider = self.config['llm']['default_provider']
        if model is None:
            provider_config = self.config['llm']['providers'][provider]
            model = provider_config.get('default_model') or provider_config['models']['standard']
        if temperature is None:
            temperature = self.config['llm']['providers'][provider]['default_temperature']

        # Get provider-specific config
        provider_config = self.config['llm']['providers'][provider]

        # Create appropriate LLM
        if provider == "ollama":
            return self._create_ollama(model, temperature, provider_config, **kwargs)
        elif provider == "openai":
            return self._create_openai(model, temperature, provider_config, **kwargs)
        elif provider == "claude":
            return self._create_claude(model, temperature, provider_config, **kwargs)
        elif provider == "perplexity":
            return self._create_perplexity(model, temperature, provider_config, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _create_ollama(self, model: str, temperature: float, config: Dict, **kwargs):
        """Create Ollama LLM instance"""
        return Ollama(
            model=model,
            base_url=config['base_url'],
            temperature=temperature,
            timeout=config.get('timeout', 120),
            **kwargs
        )

    def _create_openai(self, model: str, temperature: float, config: Dict, **kwargs):
        """Create OpenAI LLM instance"""
        return ChatOpenAI(
            model=model,
            api_key=config['api_key'],
            temperature=temperature,
            max_tokens=config.get('max_tokens', 4000),
            timeout=config.get('timeout', 60),
            **kwargs
        )

    def _create_claude(self, model: str, temperature: float, config: Dict, **kwargs):
        """Create Claude LLM instance"""
        return ChatAnthropic(
            model=model,
            anthropic_api_key=config['api_key'],
            temperature=temperature,
            max_tokens=config.get('max_tokens', 4000),
            timeout=config.get('timeout', 60),
            **kwargs
        )

    def _create_perplexity(self, model: str, temperature: float, config: Dict, **kwargs):
        """Create Perplexity LLM instance"""
        # Perplexity-specific parameters
        pplx_kwargs = {
            'model': model,
            'pplx_api_key': config['api_key'],
            'temperature': temperature,
            'timeout': config.get('timeout', 90),
        }

        # Add Perplexity-specific search parameters if available
        if 'search_recency_filter' in config:
            pplx_kwargs['search_recency_filter'] = config['search_recency_filter']
        if 'search_domain_filter' in config:
            pplx_kwargs['search_domain_filter'] = config['search_domain_filter']
        if 'return_citations' in config:
            pplx_kwargs['return_citations'] = config['return_citations']
        if 'return_images' in config:
            pplx_kwargs['return_images'] = config['return_images']

        pplx_kwargs.update(kwargs)

        return ChatPerplexity(**pplx_kwargs)

    def create_agent_llm(self, agent_name: str, **override_kwargs):
        """Create LLM for a specific agent using agent-specific config"""

        # Get agent-specific config
        agent_config = self.config['agents'].get(agent_name, {})

        # Extract LLM parameters with fallback to defaults
        provider = agent_config.get('provider') or self.config['llm']['default_provider']
        model = agent_config.get('model')
        temperature = agent_config.get('temperature')

        # Merge agent-specific kwargs
        kwargs = {}

        # Add provider-specific parameters from agent config
        provider_config = self.config['llm']['providers'][provider]
        if provider == 'perplexity':
            for key in ['search_recency_filter', 'search_domain_filter', 'return_citations', 'return_images']:
                if key in agent_config:
                    kwargs[key] = agent_config[key]
                elif key in provider_config:
                    kwargs[key] = provider_config[key]

        # Override with any explicitly passed kwargs
        kwargs.update(override_kwargs)

        try:
            llm = self.create_llm(
                provider=provider,
                model=model,
                temperature=temperature,
                **kwargs
            )
            print(f"✓ Created {provider} LLM for {agent_name} (model: {model})")
            return llm
        except Exception as e:
            # Try fallback if configured
            if 'fallback_provider' in agent_config:
                print(f"⚠️  {provider} failed for {agent_name}, using fallback: {agent_config['fallback_provider']}")
                return self.create_llm(
                    provider=agent_config['fallback_provider'],
                    model=agent_config.get('fallback_model'),
                    temperature=temperature,
                    **kwargs
                )
            else:
                raise e

    def get_research_config(self, agent_name: str) -> Dict:
        """Get research configuration for an agent"""
        return self.config['research'].get(agent_name, {})

    def get_output_config(self) -> Dict:
        """Get output configuration"""
        return self.config['output']

    def get_logging_config(self) -> Dict:
        """Get logging configuration"""
        return self.config['logging']
