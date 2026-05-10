import typer
from pathlib import Path
from rich.console import Console
from dooma.core.workspace import WorkspaceManager

console = Console()


def init_workspace():
    """Initializes a new Dooma workspace in the current directory."""
    cwd = Path.cwd()
    workspace = WorkspaceManager(cwd)

    if workspace.is_initialized():
        console.print(f"[yellow]Workspace is already initialized at {cwd}[/yellow]")
        return

    workspace.initialize()
    console.print(f"[green]Successfully initialized Dooma workspace at {cwd}![/green]")
    console.print(
        "Directories created: [bold cyan]active/[/bold cyan], [bold cyan]solved/[/bold cyan], [bold cyan]archive/[/bold cyan]"
    )
    console.print("Run [bold]dooma sync[/bold] to pull questions.")
