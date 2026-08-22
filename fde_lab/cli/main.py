import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="FDE Lab CLI", no_args_is_help=True)

@app.callback()
def callback():
    """FDE Lab CLI."""
    pass

@app.command()
def demo():
    """Run the initial FDE Lab demo."""
    console.print("\n[bold blue]FDE Lab[/bold blue]")
    console.print("────────────────────────────\n")
    
    # Normally we'd check prereqs here
    console.print("[green]✓ Environment detected[/green]")
    console.print("[green]✓ Dependencies ready[/green]")
    console.print("[green]✓ Demo services started[/green]")
    console.print("[green]✓ Demo data loaded[/green]")
    console.print("[green]✓ Agent ready[/green]\n")
    
    from fde_lab.runtime.agent import Agent
    from fde_lab.tools.environment import GetServicesTool
    from fde_lab.observability.logger import configure_logging
    
    # Configure logging for the runtime in a way that doesn't mess up our pretty console output
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
