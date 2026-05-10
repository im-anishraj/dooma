import typer
from pathlib import Path
from rich.console import Console
from dooma.core.workspace import WorkspaceManager
from dooma.registry.parser import RegistrySync, ProblemPuller
from dooma.db.manager import DatabaseManager

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

def sync_registry():
    """Syncs the latest problems from the open-source registry."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized. Run `dooma init` first.[/red]")
        raise typer.Exit(1)
        
    db_path = dooma_dir / "state.db"
    db = DatabaseManager(db_path)
    
    with console.status("[bold green]Syncing problem registry...[/bold green]"):
        RegistrySync.sync_to_db(db)
        
    console.print("[green]Registry synced successfully![/green]")

def pull_problem(problem_id: str):
    """Pulls a problem by its ID and sets it up in the active directory."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    active_dir = cwd / "active"
    
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized. Run `dooma init` first.[/red]")
        raise typer.Exit(1)
        
    success = ProblemPuller.pull(problem_id, dooma_dir, active_dir)
    if not success:
        console.print(f"[red]Problem '{problem_id}' not found in local registry. Did you run `dooma sync`?[/red]")
        raise typer.Exit(1)
        
    console.print(f"[green]Successfully pulled '{problem_id}' into active/{problem_id}[/green]")
    console.print("Happy coding!")
