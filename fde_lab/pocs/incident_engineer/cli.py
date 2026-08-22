import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from fde_lab.pocs.incident_engineer.agent import IncidentEngineerAgent
from fde_lab.observability.logger import configure_logging

app = typer.Typer(help="FDE Lab - Incident Engineer", no_args_is_help=True)
console = Console()

@app.callback()
def callback():
    pass

@app.command()
def investigate(scenario: str = typer.Option("known", help="Scenario to run: 'known' or 'inconclusive'")):
    """Run the Incident Engineer investigation."""
    configure_logging(level="WARNING")
    
    console.print("\n[bold blue]FDE Lab[/bold blue]")
    console.print("────────────────────────────────")
    console.print("\n[bold]Incident Engineer[/bold]\n")
    
    console.print("Customer incident:")
    console.print("Checkout API is returning HTTP 500 errors.\n")
    
    console.print("Investigating...\n")
    
    agent = IncidentEngineerAgent(scenario=scenario)
    
    # Simulate tool usage output
    console.print("[green]✓ Application logs[/green]")
    console.print("[green]✓ Deployment history[/green]")
    console.print("[green]✓ Git history[/green]")
    console.print("[green]✓ Metrics[/green]")
    console.print("[green]✓ Service health[/green]\n")
    
    console.print("Correlating evidence...\n")
    console.print("[green]✓ Timeline constructed[/green]")
    console.print("[green]✓ Candidate causes evaluated[/green]\n")
    
    console.print("Investigation complete.\n")
    console.print("────────────────────────────────\n")
    
    report = agent.investigate("Checkout API returning 500 errors")
    
    console.print("[bold]LIKELY ROOT CAUSE[/bold]\n")
    console.print(f"{report.likely_root_cause}\n")
    
    color = "green" if report.confidence == "High" else ("yellow" if report.confidence == "Medium" else "red")
    console.print(f"Confidence: [{color} bold]{report.confidence.upper()}[/{color} bold]\n")
    
    console.print("[bold]KEY EVIDENCE[/bold]\n")
    for ev in report.observed_evidence:
        console.print(f"• {ev.observation} (Source: {ev.source})")
        
    console.print(f"\n[bold]RECOMMENDED ACTION[/bold]\n")
    console.print(f"{report.recommended_immediate_action}\n")
    
    console.print("[dim]No automatic action was taken.[/dim]\n")

if __name__ == "__main__":
    app()
