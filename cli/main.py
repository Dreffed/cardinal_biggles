import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import yaml
from core.orchestrator import ResearchOrchestrator

console = Console()

@click.group()
def cli():
    """Research Orchestrator CLI - Multi-Provider Multi-Agent Research System"""
    pass

@cli.command()
@click.argument('topic')
@click.option('--config', '-c', default='config/config.yaml', help='Path to config file')
@click.option('--output', '-o', default=None, help='Output file path (overrides config)')
@click.option('--provider', default=None, help='Override default provider for all agents')
@click.option('--model', default=None, help='Override default model')
def research(topic, config, output, provider, model):
    """Start a research workflow on a topic"""

    console.print(Panel.fit(
        f"[bold blue]🔬 Multi-Agent Research Orchestrator[/bold blue]\n"
        f"Topic: [green]{topic}[/green]",
        border_style="blue"
    ))

    # Load and display config
    _display_config(config)

    # Initialize orchestrator
    try:
        orchestrator = ResearchOrchestrator(config_path=config)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"[yellow]Creating default config at {config}...[/yellow]")
        _create_default_config(config)
        return
    except Exception as e:
        console.print(f"[red]Error initializing orchestrator: {e}[/red]")
        return

    # Run research workflow
    try:
        with console.status("[bold green]Running research workflow...", spinner="dots"):
            results = asyncio.run(orchestrator.execute_workflow(topic))
    except Exception as e:
        console.print(f"[red]Error during research: {e}[/red]")
        return

    # Determine output path
    if output is None:
        output_config = orchestrator.llm_factory.get_output_config()
        output_dir = Path(output_config['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = topic.replace(" ", "_").lower()[:50]
        output = output_dir / f"{topic_slug}_report_{timestamp}.md"
    else:
        output = Path(output)

    # Save report
    output.write_text(results["final_report"])

    console.print(f"\n[bold green]✓ Research Complete![/bold green]")
    console.print(f"Report saved to: [cyan]{output.absolute()}[/cyan]\n")

    # Display summary stats
    _display_summary(results)

@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Path to config file')
def show_config(config):
    """Display current configuration"""
    _display_config(config, detailed=True)

@cli.command()
@click.option('--config', '-c', default='config/config.yaml', help='Path to config file')
def test_providers(config):
    """Test all configured LLM providers"""

    console.print("[bold blue]🧪 Testing LLM Providers[/bold blue]\n")

    from core.llm_factory import LLMFactory

    try:
        factory = LLMFactory(config)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return

    providers_config = factory.config['llm']['providers']

    table = Table(title="Provider Test Results")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Response Time", style="magenta")

    for provider_name in providers_config.keys():
        try:
            import time
            start = time.time()

            llm = factory.create_llm(provider=provider_name)

            # Simple test
            response = llm.invoke("Say 'test successful' and nothing else.")

            elapsed = time.time() - start

            status = "✓ OK" if "test successful" in response.content.lower() else "⚠ Warning"
            table.add_row(
                provider_name,
                providers_config[provider_name]['models'].get('standard', 'default'),
                status,
                f"{elapsed:.2f}s"
            )
        except Exception as e:
            table.add_row(
                provider_name,
                "N/A",
                f"✗ Failed: {str(e)[:30]}",
                "N/A"
            )

    console.print(table)

@cli.command()
@click.argument('output_path', default='config/config.yaml')
def init_config(output_path):
    """Create a default configuration file"""
    _create_default_config(output_path)
    console.print(f"[green]✓ Created default config at {output_path}[/green]")
    console.print("[yellow]Don't forget to set your API keys in environment variables:[/yellow]")
    console.print("  export OPENAI_API_KEY='your-key'")
    console.print("  export ANTHROPIC_API_KEY='your-key'")
    console.print("  export PERPLEXITY_API_KEY='your-key'")

def _display_config(config_path: str, detailed: bool = False):
    """Display configuration summary"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"[red]Config file not found: {config_path}[/red]")
        return

    table = Table(title=f"Configuration: {config_path}")
    table.add_column("Agent", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")

    agents_config = config.get('agents', {})
    default_provider = config['llm']['default_provider']

    for agent_name, agent_config in agents_config.items():
        provider = agent_config.get('provider', default_provider)
        model = agent_config.get('model', 'default')
        table.add_row(agent_name, provider, model)

    console.print(table)
    console.print()

def _display_summary(results: Dict):
    """Display research summary statistics"""
    table = Table(title="Research Summary")
    table.add_column("Phase", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Sources Found", style="yellow")

    for phase_name, phase_data in results.items():
        if phase_name != "final_report":
            urls = phase_data.get("urls", [])
            table.add_row(
                phase_name.replace("_", " ").title(),
                "✓ Complete",
                str(len(urls))
            )

    console.print(table)

def _create_default_config(output_path: str):
    """Create a default config file"""
    default_config = """# Global LLM Configuration
llm:
  default_provider: "ollama"
  default_model: "llama3.1"

  providers:
    ollama:
      base_url: "http://localhost:11434"
      models:
        fast: "llama3.1:8b"
        standard: "llama3.1"
        powerful: "llama3.1:70b"
      default_temperature: 0.1
      timeout: 120

    openai:
      api_key: "${OPENAI_API_KEY}"
      models:
        fast: "gpt-3.5-turbo"
        standard: "gpt-4"
        powerful: "gpt-4-turbo"
      default_temperature: 0.1
      max_tokens: 4000
      timeout: 60

    claude:
      api_key: "${ANTHROPIC_API_KEY}"
      models:
        fast: "claude-3-haiku-20240307"
        standard: "claude-3-sonnet-20240229"
        powerful: "claude-3-opus-20240229"
      default_temperature: 0.1
      max_tokens: 4000
      timeout: 60

    perplexity:
      api_key: "${PERPLEXITY_API_KEY}"
      base_url: "https://api.perplexity.ai"
      models:
        fast: "llama-3.1-sonar-small-128k-online"
        standard: "llama-3.1-sonar-large-128k-online"
        powerful: "llama-3.1-sonar-huge-128k-online"
      default_temperature: 0.2
      max_tokens: 4000
      search_recency_filter: "month"
      timeout: 90

# Agent-Specific Configuration
agents:
  coordinator:
    provider: "ollama"
    model: "llama3.1"
    temperature: 0.1

  trend_scout:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    temperature: 0.2
    search_recency_filter: "month"
    return_citations: true

  historian:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    temperature: 0.1

  scholar:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    temperature: 0.1
    fallback_provider: "openai"
    fallback_model: "gpt-4"

  journalist:
    provider: "perplexity"
    model: "llama-3.1-sonar-large-128k-online"
    temperature: 0.2
    search_recency_filter: "month"

  bibliophile:
    provider: "claude"
    model: "claude-3-sonnet-20240229"
    temperature: 0.1

  reporter:
    provider: "claude"
    model: "claude-3-opus-20240229"
    temperature: 0.2
    fallback_provider: "openai"
    fallback_model: "gpt-4-turbo"

# Research Configuration
research:
  trend_scout:
    max_trends: 5
    timeframe: "2024-2025"

  historian:
    depth: "comprehensive"
    min_sources: 5

  scholar:
    min_papers: 5
    max_papers: 15
    recency_years: 3

  journalist:
    min_articles: 10
    max_articles: 25
    days_back: 90

  bibliophile:
    min_books: 5
    max_books: 10

# Output Configuration
output:
  default_format: "markdown"
  include_reference_tables: true
  save_intermediate_results: true
  output_directory: "./reports"

# Logging
logging:
  level: "INFO"
  file: "./logs/orchestrator.log"
  console: true
  track_costs: true
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(default_config)

if __name__ == '__main__':
    cli()
