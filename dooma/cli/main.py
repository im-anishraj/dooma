import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.columns import Columns

app = typer.Typer(add_completion=False)
console = Console()

def load_data():
    dataset_path = Path(__file__).parent.parent / "dataset" / "companies.json"
    if not dataset_path.exists():
        console.print(f"[red]Dataset not found at {dataset_path}![/red]")
        raise typer.Exit(1)
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.callback(invoke_without_command=True)
def interactive_loop(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    
    data = load_data()
    companies = sorted(list(data.keys()))
    
    # Group companies by first letter
    groups = {}
    for company in companies:
        first_char = company[0].upper()
        if not first_char.isalpha():
            first_char = '#'
            
        if first_char not in groups:
            groups[first_char] = []
        groups[first_char].append(company)
        
    sorted_letters = sorted(list(groups.keys()))
    
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Welcome to Dooma - Your Ultimate DSA Preparation Companion[/bold cyan]"))
        console.print("[bold magenta]--- Step 1: Select the First Letter of the Company You Want to Prepare For ---[/bold magenta]\n")
        
        # Display letters nicely
        letter_display = []
        for letter in sorted_letters:
            count = len(groups[letter])
            letter_display.append(f"[bold yellow]{letter}[/bold yellow] [dim]({count})[/dim]")
            
        console.print(Columns(letter_display, expand=True, equal=True))
        
        console.print("\n[dim]Options:[/dim]")
        console.print("[dim]- Type a letter to explore companies (e.g., 'A', 'G', '#')[/dim]")
        console.print("[dim]- Enter '0' to safely exit the application[/dim]")
        
        choice = Prompt.ask("\nYour choice", default="")
        choice = choice.upper().strip()
        
        if choice == "0":
            console.print("[green]Goodbye![/green]")
            raise typer.Exit()
        elif choice in groups:
            show_company_list(choice, groups[choice], data)
        else:
            console.print("[red]Invalid letter. Please select a letter from the list above.[/red]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]")

def show_company_list(letter, group_companies, data):
    page = 0
    items_per_page = 30
    
    while True:
        console.clear()
        console.print(Panel(f"[bold cyan]Step 2: Choose Your Target Company (Starting with '{letter}')[/bold cyan]"))
        console.print(f"[bold magenta]--- Page {page + 1} ---[/bold magenta]\n")
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(group_companies))
        
        for i in range(start_idx, end_idx):
            console.print(f"  [bold yellow]{i + 1}.[/bold yellow] {group_companies[i]}")
            
        console.print("\n[dim]Options:[/dim]")
        console.print("[dim]- Type the number next to the company name to view its questions[/dim]")
        if end_idx < len(group_companies):
            console.print("[dim]- Enter 'n' for the next page[/dim]")
        if page > 0:
            console.print("[dim]- Enter 'p' for the previous page[/dim]")
        console.print("[dim]- Enter '0' to go one step back to the alphabet menu[/dim]")
        
        choice = Prompt.ask("\nYour choice", default="0")
        
        if choice == "0":
            return
        elif choice.lower() == 'n' and end_idx < len(group_companies):
            page += 1
        elif choice.lower() == 'p' and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(group_companies):
                company_name = group_companies[idx]
                show_company_questions(company_name, data[company_name])
            else:
                console.print("[red]Invalid selection.[/red]")
                Prompt.ask("[dim]Press Enter to continue...[/dim]")
        else:
            console.print("[red]Invalid input.[/red]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]")

def show_company_questions(company_name, questions):
    page = 0
    items_per_page = 15
    
    while True:
        console.clear()
        table = Table(
            title=f"Step 3: Interview Questions for [bold cyan]{company_name}[/bold cyan] (Page {page + 1})", 
            show_header=True, 
            header_style="bold magenta",
            expand=True
        )
        table.add_column("No.", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Difficulty", style="white")
        table.add_column("Frequency", style="yellow")
        table.add_column("URL", style="blue")
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(questions))
        
        for i in range(start_idx, end_idx):
            q = questions[i]
            diff = q.get("difficulty", "N/A")
            if diff == "Easy":
                diff_color = "green"
            elif diff == "Medium":
                diff_color = "yellow"
            elif diff == "Hard":
                diff_color = "red"
            else:
                diff_color = "white"
            
            diff_formatted = f"[{diff_color}]{diff}[/{diff_color}]"
            
            table.add_row(
                str(i + 1),
                q.get("title", "N/A"),
                diff_formatted,
                q.get("frequency", "N/A"),
                q.get("url", "N/A")
            )
            
        console.print(table)
        
        console.print("\n[dim]Options:[/dim]")
        if end_idx < len(questions):
            console.print("[dim]- Enter 'n' for the next page of questions[/dim]")
        if page > 0:
            console.print("[dim]- Enter 'p' for the previous page of questions[/dim]")
        console.print("[dim]- Enter '0' to go one step back to the company list[/dim]")
        
        choice = Prompt.ask("\nYour choice", default="0")
        
        if choice == "0":
            return # Go back to company list
        elif choice.lower() == 'n' and end_idx < len(questions):
            page += 1
        elif choice.lower() == 'p' and page > 0:
            page -= 1
        else:
            console.print("[red]Invalid input.[/red]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]")

if __name__ == "__main__":
    app()
