import click
import asyncio
from typing import Dict, Any, Optional
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
@click.option('--hil/--no-hil', default=False, help='Enable Human-in-the-Loop mode')
@click.option('--auto-approve', is_flag=True, help='Auto-approve all checkpoints (for testing)')
def research(topic, config, output, provider, model, hil, auto_approve):
    """Start a research workflow on a topic"""

    console.print(Panel.fit(
        f"[bold blue]Multi-Agent Research Orchestrator[/bold blue]\n"
        f"Topic: [green]{topic}[/green]",
        border_style="blue"
    ))

    # Display HIL status if enabled
    if hil:
        console.print(Panel.fit(
            "[bold yellow]Human-in-the-Loop Mode ENABLED[/bold yellow]\n"
            "You will be prompted to review results at key checkpoints.",
            border_style="yellow"
        ))
        console.print()

    # Load config and override HIL settings
    try:
        with open(config, 'r') as f:
            config_dict = yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"[red]Config file not found: {config}[/red]")
        console.print(f"[yellow]Creating default config at {config}...[/yellow]")
        _create_default_config(config)
        return
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return

    # Override HIL settings from CLI
    if 'hil' not in config_dict:
        config_dict['hil'] = {}

    config_dict['hil']['enabled'] = hil
    config_dict['hil']['auto_approve'] = auto_approve

    # Save temporary config
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_dict, f)
            temp_config = f.name
    except Exception as e:
        console.print(f"[red]Error creating temp config: {e}[/red]")
        return

    # Load and display config
    _display_config(config)

    # Initialize orchestrator
    try:
        orchestrator = ResearchOrchestrator(config_path=temp_config)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error initializing orchestrator: {e}[/red]")
        import os
        if os.path.exists(temp_config):
            os.remove(temp_config)
        return

    # Run research workflow
    try:
        with console.status("[bold green]Running research workflow...", spinner="dots"):
            results = asyncio.run(orchestrator.execute_workflow(topic))
    except Exception as e:
        console.print(f"[red]Error during research: {e}[/red]")
        import os
        if os.path.exists(temp_config):
            os.remove(temp_config)
        return
    finally:
        # Clean up temp config file
        import os
        if 'temp_config' in locals() and os.path.exists(temp_config):
            try:
                os.remove(temp_config)
            except:
                pass

    # Check if workflow was cancelled
    if results.get("status") == "cancelled":
        console.print(f"\n[yellow]Workflow cancelled at: {results.get('phase', 'unknown')}[/yellow]")
        console.print("[yellow]Partial results were saved to knowledge store.[/yellow]")
        return

    # Legacy single-file output support
    if output is not None:
        output_path = Path(output)
        output_path.write_text(results["final_report"])
        console.print(f"\n[bold green]Research Complete![/bold green]")
        console.print(f"Report saved to: [cyan]{output_path.absolute()}[/cyan]\n")

    console.print(f"\n[bold green]Research Complete![/bold green]\n")

    # Display output locations from adapters
    if 'output_locations' in results:
        _display_output_locations(results['output_locations'])

    # Display summary stats
    _display_summary(results)

    # Display HIL summary if applicable
    if hil and "hil_summary" in results:
        hil_summary = results["hil_summary"]
        console.print(f"\n[bold cyan]HIL Checkpoint Summary:[/bold cyan]")
        console.print(f"  Total Checkpoints: {hil_summary['total_checkpoints']}")
        console.print(f"  Approvals: {hil_summary['approvals']}")
        console.print(f"  Edits: {hil_summary['edits']}")
        console.print(f"  Regenerations: {hil_summary['regenerations']}")

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

def _display_output_locations(output_locations: list):
    """Display output locations"""
    console.print("[bold cyan]Output Locations:[/bold cyan]")

    table = Table()
    table.add_column("Format", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Location", style="yellow")

    for output in output_locations:
        status = "✓" if output['status'] == 'success' else "✗"
        location = output.get('location', output.get('error', 'N/A'))
        table.add_row(output['format'], status, location)

    console.print(table)
    console.print()

def _display_summary(results: Dict):
    """Display research summary statistics"""
    table = Table(title="Research Summary")
    table.add_column("Phase", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Sources Found", style="yellow")

    for phase_name, phase_data in results.items():
        if phase_name not in ["final_report", "output_locations", "hil_summary", "status"]:
            if isinstance(phase_data, dict):
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
  # Output formats to use (can enable multiple)
  formats:
    - markdown

  # Default single-file output directory (legacy)
  output_directory: "./reports"
  include_reference_tables: true
  save_intermediate_results: true

  # Markdown/Obsidian Configuration
  markdown:
    enabled: true
    output_directory: "./reports"

    # Obsidian-specific features
    obsidian:
      enabled: true
      vault_path: null              # Set to your Obsidian vault path
      use_wikilinks: true
      use_tags: true
      use_frontmatter: true
      use_callouts: true
      create_moc: true              # Create Map of Content index
      moc_filename: "index.md"

    # Folder structure
    structure:
      create_topic_folder: true
      timestamp_folders: true
      save_agent_outputs: true
      save_artifacts: true
      save_raw_data: true

    # Export options
    export_options:
      include_metadata: true
      include_timestamps: true
      create_attachments_folder: true

# Logging
logging:
  level: "INFO"
  file: "./logs/orchestrator.log"
  console: true
  track_costs: true

# Human-in-the-Loop Configuration
hil:
  enabled: false
  auto_approve: false
  checkpoints:
    trend_review:
      enabled: true
      timeout: 300
    research_review:
      enabled: true
      timeout: 600
    report_review:
      enabled: true
      timeout: 0
  allow_editing: true
  allow_regeneration: true
  save_checkpoints: true
  checkpoint_file: "./data/hil_checkpoints.json"
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(default_config)

if __name__ == '__main__':
    cli()
