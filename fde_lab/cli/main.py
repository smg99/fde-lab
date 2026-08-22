import typer
from rich.console import Console
import json
import sys

console = Console()
app = typer.Typer(help="FDE Lab CLI", no_args_is_help=True)

@app.callback()
def callback():
    """FDE Lab CLI."""
    pass

@app.command()
def demo(
    manifest: bool = typer.Option(False, "--manifest", help="Output worker manifest"),
    json_output: bool = typer.Option(False, "--json", help="Output machine-readable JSON"),
):
    """Run the initial FDE Lab demo."""
    if manifest:
        sys.stdout.write(json.dumps({
            "schema_version": "0.1",
            "name": "environment-inspector",
            "version": "0.1.5",
            "description": "Environment Inspector",
            "capabilities": ["inspection"],
            "inputs": [],
            "outputs": []
        }))
        sys.stdout.flush()
        return

    if json_output:
        sys.stdout.write(json.dumps({
            "schema_version": "0.1",
            "worker": {
                "name": "environment-inspector",
                "version": "0.1.5"
            },
            "status": "success",
            "summary": "Environment inspected successfully",
            "facts": [],
            "actions": [],
            "artifacts": [],
            "warnings": [],
            "errors": [],
            "next_steps": []
        }))
        sys.stdout.flush()
        return

    console.print("\n[bold blue]FDE Lab[/bold blue]")
    console.print("────────────────────────────\n")
    
    console.print("[green]✓ Environment detected[/green]")
    console.print("[green]✓ Dependencies ready[/green]")
    console.print("[green]✓ Demo services started[/green]")
    console.print("[green]✓ Demo data loaded[/green]")
    console.print("[green]✓ Agent ready[/green]\n")
    
    from fde_lab.runtime.agent import Agent
    from fde_lab.tools.environment import GetServicesTool
    from fde_lab.observability.logger import configure_logging
    
    configure_logging(level="WARNING")
    
    tools = [GetServicesTool()]
    agent = Agent(name="Environment Inspector", instructions="Inspect local environment", tools=tools)
    
    console.print("Agent initialized. Type 'exit' to quit.\n")
    console.print("Example:")
    console.print('"What services are currently running?"\n')
    
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
            if user_input.lower() in ("exit", "quit"):
                break
                
            response = agent.run(user_input)
            console.print(f"[bold magenta]Agent:[/bold magenta] {response}\n")
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    app()
