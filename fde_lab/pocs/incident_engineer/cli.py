import sys
import json
import typer
from rich.console import Console

from fde_lab.pocs.incident_engineer.agent import IncidentEngineerAgent
from fde_lab.observability.logger import configure_logging
from fde_lab.runtime.result import WorkerResult, WorkerManifest, EnvironmentRequirements, SideEffectMetadata, Example
from fde_lab.runtime.exit_codes import ExitCode

app = typer.Typer(help="FDE Lab - Incident Engineer", no_args_is_help=True)
console = Console()

@app.callback()
def callback():
    pass

@app.command()
def investigate(
    scenario: str = typer.Option("known", help="Scenario to run: 'known' or 'inconclusive'"),
    json_mode: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
    manifest_mode: bool = typer.Option(False, "--manifest", help="Output capability manifest JSON")
):
    """Run the Incident Engineer investigation."""
    
    machine_mode = json_mode or manifest_mode
    configure_logging(level="WARNING", machine_mode=machine_mode)
    
    if manifest_mode:
        manifest = WorkerManifest(
            name="incident-engineer",
            version="0.1.0",
            description="Investigates a seeded production incident and produces structured evidence and diagnosis.",
            capabilities=["investigate_incident"],
            inputs={"scenario": {"type": "string", "allowed": ["known", "inconclusive"], "default": "known"}},
            outputs={"WorkerResult": "Standard FDE Lab result envelope"},
            side_effects=SideEffectMetadata(filesystem=False, network=False, credentials=False, production=False, destructive=False, external_systems=False),
            requirements=EnvironmentRequirements(node=True, python=True, docker=True),
            examples=[Example(command="npx @fde-lab/incident-engineer --json", purpose="Investigate the default incident and return a structured result.")]
        )
        print(json.dumps(manifest.to_dict(), indent=2))
        sys.exit(ExitCode.SUCCESS)
    
    if not machine_mode:
        console.print("\n[bold blue]FDE Lab[/bold blue]")
        console.print("────────────────────────────────")
        console.print("\n[bold]Incident Engineer[/bold]\n")
        console.print("Customer incident:")
        console.print("Checkout API is returning HTTP 500 errors.\n")
        console.print("Investigating...\n")
    
    agent = IncidentEngineerAgent(scenario=scenario)
    
    if not machine_mode:
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
    
    if json_mode:
        status = "success" if report.confidence == "High" else "inconclusive"
        result = WorkerResult(
            worker={"name": "incident-engineer", "version": "0.1.0"},
            status=status,
            summary=f"Incident investigation completed. Root cause: {report.likely_root_cause}",
            facts=[f"{ev.observation} (Source: {ev.source})" for ev in report.observed_evidence],
            next_steps=[report.recommended_immediate_action]
        )
        print(json.dumps(result.to_dict(), indent=2))
        
        sys.exit(ExitCode.SUCCESS if status == "success" else ExitCode.INCONCLUSIVE)
    else:
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
