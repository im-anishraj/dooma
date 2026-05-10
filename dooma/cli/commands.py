import typer
import shutil
import time
from pathlib import Path
from rich.console import Console
from dooma.core.workspace import WorkspaceManager
from dooma.registry.parser import RegistrySync, ProblemPuller
from dooma.db.manager import DatabaseManager
from dooma.runner.executor import TestRunner

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

def test_problem(problem_path: str):
    """Tests the solution in the specified directory."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized.[/red]")
        raise typer.Exit(1)
        
    problem_dir = Path(problem_path).resolve()
    if not problem_dir.is_dir():
        console.print(f"[red]Path '{problem_path}' is not a directory.[/red]")
        raise typer.Exit(1)
        
    problem_id = problem_dir.name
    
    with console.status("[bold yellow]Running tests...[/bold yellow]"):
        start_time = time.time()
        success, message = TestRunner.run_tests(problem_dir)
        end_time = time.time()
        
    if not success:
        console.print(f"[red]❌ {message}[/red]")
        raise typer.Exit(1)
        
    console.print(f"[green]✅ {message}[/green]")
    
    # Auto-updater logic
    # Move from active/ to solved/
    if "active" in problem_dir.parts:
        solved_dir = cwd / "solved" / problem_id
        if solved_dir.exists():
            shutil.rmtree(solved_dir) # Overwrite if exists
        shutil.move(str(problem_dir), str(solved_dir))
        console.print(f"[bold cyan]Moved '{problem_id}' to solved/[/bold cyan]")
        
        # Update SQLite DB
        db_path = dooma_dir / "state.db"
        db = DatabaseManager(db_path)
        conn = db.connect()
        cursor = conn.cursor()
        
        # Update progress
        time_taken_ms = int((end_time - start_time) * 1000)
        cursor.execute("""
            INSERT OR REPLACE INTO progress (problem_id, status, attempts, solved_at, time_taken_ms)
            VALUES (?, 'solved', 
                COALESCE((SELECT attempts + 1 FROM progress WHERE problem_id = ?), 1),
                CURRENT_TIMESTAMP, ?)
        """, (problem_id, problem_id, time_taken_ms))
        
        conn.commit()
        db.close()
        
        console.print("[bold green]Progress saved! 🎉[/bold green]")
