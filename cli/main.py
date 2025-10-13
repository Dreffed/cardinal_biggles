import click
import asyncio
from rich.console import Console
from rich.progress import Progress
from core.orchestrator import ResearchOrchestrator
from pathlib import Path

console = Console()

@click.group()
def cli():
    """Research Orchestrator CLI"""
    pass

@cli.command()
@click.argument('topic')
@click.option('--output', '-o', default='report.md', help='Output file path')
@click.option('--provider', default='ollama', help='LLM provider (ollama/openai/claude)')
@click.option('--model', default='llama3.1', help='Model name')
def research(topic, output, provider, model):
    """Start a research workflow on a topic"""

    console.print(f"\n[bold blue]🔬 Research Orchestrator[/bold blue]")
    console.print(f"Topic: [green]{topic}[/green]")
    console.print(f"Provider: [yellow]{provider}[/yellow] | Model: [yellow]{model}[/yellow]\n")

    # Initialize orchestrator
    orchestrator = ResearchOrchestrator(
        llm_provider=provider,
        model_name=model
    )

    # Run research workflow
    results = asyncio.run(orchestrator.execute_workflow(topic))

    # Save report
    report_path = Path(output)
    report_path.write_text(results["final_report"])

    console.print(f"\n[bold green]✓ Research complete![/bold green]")
    console.print(f"Report saved to: [cyan]{report_path.absolute()}[/cyan]\n")

@cli.command()
def serve():
    """Start API server (future implementation)"""
    console.print("[yellow]API server not yet implemented[/yellow]")
    console.print("Coming soon: REST API, Slack, MS Teams, n8n integrations")

if __name__ == '__main__':
    cli()
