import typer
import shutil
import time
import json
from pathlib import Path
from rich.console import Console
from dooma.core.workspace import WorkspaceManager
from dooma.db.manager import DatabaseManager
from dooma.runner.executor import TestRunner
from dooma.dataset.loader import DatasetLoader

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
    console.print("Run [bold]dooma pull <id>[/bold] or [bold]dooma prep start[/bold] to begin.")

def pull_problem(problem_id: str):
    """Pulls a problem by its ID and sets it up in the active directory."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    active_dir = cwd / "active"
    
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized. Run `dooma init` first.[/red]")
        raise typer.Exit(1)
        
    try:
        problem_data = DatasetLoader.fetch_problem(problem_id)
    except FileNotFoundError:
        console.print(f"[red]Problem '{problem_id}' not found in packaged dataset.[/red]")
        raise typer.Exit(1)
        
    target_dir = active_dir / problem_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    (target_dir / "problem.md").write_text(f"# {problem_data.get('title', problem_id)}\n\n{problem_data.get('description', '')}")
    (target_dir / "solution.py").write_text(problem_data.get('stub', ''))
    (target_dir / ".tests.json").write_text(json.dumps(problem_data.get('tests', []), indent=2))
    
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

def prep_start(company: str):
    """Starts a new preparation campaign for a specific company."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized.[/red]")
        raise typer.Exit(1)
        
    db_path = dooma_dir / "state.db"
    db = DatabaseManager(db_path)
    conn = db.connect()
    cursor = conn.cursor()
    
    # Create campaign
    cursor.execute("INSERT INTO campaigns (target_company) VALUES (?)", (company,))
    conn.commit()
    db.close()
    
    console.print(f"[bold green]Started preparation campaign for {company}![/bold green]")
    console.print(f"Run [bold cyan]dooma prep next[/bold cyan] to pull your first problem.")

def prep_next():
    """Pulls the next unsolved problem for the active campaign."""
    cwd = Path.cwd()
    dooma_dir = cwd / ".dooma"
    if not dooma_dir.exists():
        console.print("[red]Workspace not initialized.[/red]")
        raise typer.Exit(1)
        
    db_path = dooma_dir / "state.db"
    db = DatabaseManager(db_path)
    conn = db.connect()
    cursor = conn.cursor()
    
    # Get latest campaign
    cursor.execute("SELECT target_company FROM campaigns ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        console.print("[red]No active campaign found. Run `dooma prep start <company>`.[/red]")
        raise typer.Exit(1)
        
    company = row["target_company"]
    
    # Find next unsolved problem for this company
    search_str = f'%"{company}"%'
    
    cursor.execute("""
        SELECT id, title FROM problems 
        WHERE companies LIKE ?
        AND id NOT IN (SELECT problem_id FROM progress WHERE status='solved')
        LIMIT 1
    """, (search_str,))
    problem_row = cursor.fetchone()
    
    db.close()
    
    if not problem_row:
        console.print(f"[bold green]Congratulations! You have solved all available {company} problems.[/bold green]")
        return
        
    problem_id = problem_row["id"]
    console.print(f"[yellow]Pulling next problem for {company}: {problem_row['title']}[/yellow]")
    
    # Call the existing pull command logic directly instead of invoking ProblemPuller
    try:
        problem_data = DatasetLoader.fetch_problem(problem_id)
    except FileNotFoundError:
        console.print(f"[red]Problem '{problem_id}' not found in packaged dataset.[/red]")
        raise typer.Exit(1)
        
    target_dir = cwd / "active" / problem_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    (target_dir / "problem.md").write_text(f"# {problem_data.get('title', problem_id)}\n\n{problem_data.get('description', '')}")
    (target_dir / "solution.py").write_text(problem_data.get('stub', ''))
    (target_dir / ".tests.json").write_text(json.dumps(problem_data.get('tests', []), indent=2))
        
    console.print(f"[bold green]Successfully pulled '{problem_id}' into active/[/bold green]")

