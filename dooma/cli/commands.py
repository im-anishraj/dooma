import typer
import shutil
import time
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
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
    console.print(Panel(
        "[bold green]Workspace Initialized Successfully![/bold green]\n\n"
        "Directories created:\n"
        " 📁 [cyan]active/[/cyan]  - For currently unsolved problems\n"
        " 📁 [cyan]solved/[/cyan]  - For your completed solutions\n"
        " 📁 [cyan]archive/[/cyan] - For inactive problems\n\n"
        "Run [bold yellow]dooma pull <id>[/bold yellow] or [bold yellow]dooma prep start <company>[/bold yellow] to begin.",
        title="[bold]Dooma Workspace[/bold]",
        border_style="cyan",
        expand=False
    ))

def _format_problem_md(data: dict) -> str:
    diff_color = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(data.get("difficulty"), "⚪")
    difficulty = data.get("difficulty", "Unknown")
    topics = ", ".join(data.get("topics", []))
    companies = ", ".join(data.get("companies", {}).keys())
    
    md = f"# {data.get('title', 'Problem')}\n\n"
    md += f"**Difficulty:** {diff_color} {difficulty} | "
    if topics: md += f"**Topics:** {topics} | "
    if companies: md += f"**Companies:** {companies}"
    md += "\n\n---\n\n"
    md += data.get("description", "")
    return md

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
    
    (target_dir / "problem.md").write_text(_format_problem_md(problem_data), encoding="utf-8")
    (target_dir / "solution.py").write_text(problem_data.get('stub', ''), encoding="utf-8")
    (target_dir / ".tests.json").write_text(json.dumps(problem_data.get('tests', []), indent=2), encoding="utf-8")
    
    console.print(Panel(
        f"🚀 Successfully pulled [bold cyan]{problem_data.get('title', problem_id)}[/bold cyan]!\n\n"
        f"📁 Directory: [green]active/{problem_id}[/green]\n"
        f"🎯 Difficulty: {problem_data.get('difficulty', 'Unknown')}",
        title="Problem Scaffolded",
        border_style="green",
        expand=False
    ))

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
        console.print(Panel(f"[bold red]❌ {message}[/bold red]", title="Test Failed", border_style="red", expand=False))
        raise typer.Exit(1)
        
    console.print(Panel(f"[bold green]✅ {message}[/bold green]", title="Test Passed", border_style="green", expand=False))
    
    # Auto-updater logic
    # Move from active/ to solved/
    if "active" in problem_dir.parts:
        solved_dir = cwd / "solved" / problem_id
        if solved_dir.exists():
            shutil.rmtree(solved_dir) # Overwrite if exists
        shutil.move(str(problem_dir), str(solved_dir))
        
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
        
        console.print(Panel(
            f"🎉 [bold cyan]{problem_id}[/bold cyan] is now solved!\n"
            f"Moved to [green]solved/[/green]\n"
            f"⏱ Time Taken: [yellow]{time_taken_ms}ms[/yellow]",
            title="Progress Saved",
            border_style="magenta",
            expand=False
        ))

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
    
    console.print(Panel(
        f"[bold green]Started preparation campaign for {company}![/bold green]\n\n"
        f"Run [bold cyan]dooma prep next[/bold cyan] to pull your first problem.",
        title="Campaign Mode",
        border_style="blue",
        expand=False
    ))

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
        console.print(Panel(
            f"[bold green]Congratulations![/bold green] You have solved all available [bold cyan]{company}[/bold cyan] problems.",
            title="Campaign Complete",
            border_style="green",
            expand=False
        ))
        return
        
    problem_id = problem_row["id"]
    
    try:
        problem_data = DatasetLoader.fetch_problem(problem_id)
    except FileNotFoundError:
        console.print(f"[red]Problem '{problem_id}' not found in packaged dataset.[/red]")
        raise typer.Exit(1)
        
    target_dir = cwd / "active" / problem_id
    target_dir.mkdir(parents=True, exist_ok=True)
    
    (target_dir / "problem.md").write_text(_format_problem_md(problem_data), encoding="utf-8")
    (target_dir / "solution.py").write_text(problem_data.get('stub', ''), encoding="utf-8")
    (target_dir / ".tests.json").write_text(json.dumps(problem_data.get('tests', []), indent=2), encoding="utf-8")
        
    console.print(Panel(
        f"🚀 Successfully pulled [bold cyan]{problem_data.get('title', problem_id)}[/bold cyan] for [bold yellow]{company}[/bold yellow]!\n\n"
        f"📁 Directory: [green]active/{problem_id}[/green]\n"
        f"🎯 Difficulty: {problem_data.get('difficulty', 'Unknown')}",
        title="Next Campaign Problem",
        border_style="blue",
        expand=False
    ))

