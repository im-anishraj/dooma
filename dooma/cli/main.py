import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

app = typer.Typer(add_completion=False)
console = Console()

def load_data():
    """Load the bundled company-question dataset.

    Returns:
        dict: Mapping of company names to their interview question lists.

    Raises:
        typer.Exit: If the dataset file is missing.
    """
    dataset_path = Path(__file__).parent.parent / "dataset" / "companies.json"
    if not dataset_path.exists():
        panel = Panel(
            f"[bold #E74C3C]Dataset Not Found![/bold #E74C3C]\n\n"
            f"The dataset file is missing at:\n[bold]{dataset_path}[/bold]\n\n"
            f"[#F7CA18]To fix this:[/#F7CA18]\n"
            f"1. Run [bold]python scripts/build_dataset.py[/bold] to download the dataset\n"
            f"2. Or manually place a [bold]companies.json[/bold] file in the dataset folder"
        )
        console.print(panel)
        raise typer.Exit(1)
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.callback(invoke_without_command=True)
def interactive_loop(ctx: typer.Context):
    """Run the interactive company and question browser.

    Args:
        ctx: Typer invocation context used to skip the browser when a
            subcommand is invoked.

    Returns:
        None
    """
    if ctx.invoked_subcommand is not None:
        return
    
    try:
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
            
            logo = Text.from_markup(
                "[#F39C12]██████████████[/]\n"
                "[#F39C12]██[/][#E74C3C]████████████[/][#F7CA18]▄▄[/]\n"
                "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
                "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
                "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
                "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
                "[#F39C12]██[/][#E74C3C]████████████[/][#F7CA18]▀▀[/]\n"
                "[#F39C12]██████████████[/]"
            )
            welcome_panel = Panel("[bold #F39C12]Welcome to Dooma - Your Ultimate DSA Preparation Companion[/bold #F39C12]")
            
            grid = Table.grid(padding=(0, 2))
            grid.add_column(justify="center", vertical="middle")
            grid.add_column(justify="left", vertical="middle")
            grid.add_row(logo, welcome_panel)
            
            console.print(grid)
            console.print("\n[bold #E74C3C]--- Step 1: Select the First Letter of the Company You Want to Prepare For ---[/bold #E74C3C]\n")
            
            # Display letters nicely
            letter_display = []
            for letter in sorted_letters:
                count = len(groups[letter])
                letter_display.append(f"[bold #F7CA18]{letter}[/bold #F7CA18] [dim #FAD7A1]({count})[/dim #FAD7A1]")
                
            console.print(Columns(letter_display, expand=True, equal=True))
            
            console.print("\n[dim #FAD7A1]Options:[/dim #FAD7A1]")
            console.print("[dim #FAD7A1]- Type a letter to explore companies (e.g., 'A', 'G', '#')[/dim #FAD7A1]")
            console.print("[dim #FAD7A1]- Enter '0' to safely exit the application[/dim #FAD7A1]")
            
            choice = Prompt.ask("\nYour choice", default="")
            choice = choice.upper().strip()
            
            if choice == "0":
                console.print("[bold #F39C12]Goodbye![/bold #F39C12]")
                raise typer.Exit()
            elif choice in groups:
                show_company_list(choice, groups[choice], data)
            else:
                console.print("[bold #E74C3C]Invalid letter. Please select a letter from the list above.[/bold #E74C3C]")
                Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")
    except KeyboardInterrupt:
        console.print("\n[bold #F39C12]Goodbye! See you next time! 🚀[/bold #F39C12]")
        raise typer.Exit(0)

def show_company_list(letter, group_companies, data):
    """Display a paginated company list for a selected starting letter.

    Args:
        letter: Selected alphabet bucket shown in the page heading.
        group_companies: Company names that belong to the selected bucket.
        data: Full dataset mapping company names to question lists.

    Returns:
        None
    """
    page = 0
    items_per_page = 30
    
    while True:
        console.clear()
        console.print(Panel(f"[bold #F39C12]Step 2: Choose Your Target Company (Starting with '{letter}')[/bold #F39C12]"))
        console.print(f"[bold #E74C3C]--- Page {page + 1} ---[/bold #E74C3C]\n")
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(group_companies))
        
        for i in range(start_idx, end_idx):
            console.print(f"  [bold #F7CA18]{i + 1}.[/bold #F7CA18] {group_companies[i]}")
            
        console.print("\n[dim #FAD7A1]Options:[/dim #FAD7A1]")
        console.print("[dim #FAD7A1]- Type the number next to the company name to view its questions[/dim #FAD7A1]")
        if end_idx < len(group_companies):
            console.print("[dim #FAD7A1]- Enter 'n' for the next page[/dim #FAD7A1]")
        if page > 0:
            console.print("[dim #FAD7A1]- Enter 'p' for the previous page[/dim #FAD7A1]")
        console.print("[dim #FAD7A1]- Enter '0' to go one step back to the alphabet menu[/dim #FAD7A1]")
        
        choice = Prompt.ask("\nYour choice", default="")
        choice = choice.strip()
        
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
                console.print("[bold #E74C3C]Invalid selection.[/bold #E74C3C]")
                Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")
        else:
            console.print("[bold #E74C3C]Invalid input.[/bold #E74C3C]")
            Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")

def show_company_questions(company_name, questions):
    """Display paginated interview questions for a company.

    Args:
        company_name: Name of the selected company.
        questions: Question dictionaries associated with the selected company.

    Returns:
        None
    """
    page = 0
    items_per_page = 15
    
    while True:
        console.clear()
        table = Table(
            title=f"Step 3: Interview Questions for [bold #F39C12]{company_name}[/bold #F39C12] (Page {page + 1})", 
            show_header=True, 
            header_style="bold #E74C3C",
            expand=True
        )
        table.add_column("No.", justify="right", style="#F39C12", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Difficulty", style="white")
        table.add_column("Frequency", style="#F7CA18")
        table.add_column("URL", style="blue")
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(questions))
        
        for i in range(start_idx, end_idx):
            q = questions[i]
            diff = q.get("difficulty", "N/A")
            if diff == "Easy":
                diff_color = "green"
            elif diff == "Medium":
                diff_color = "#F7CA18"
            elif diff == "Hard":
                diff_color = "#E74C3C"
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
        
        console.print("\n[dim #FAD7A1]Options:[/dim #FAD7A1]")
        if end_idx < len(questions):
            console.print("[dim #FAD7A1]- Enter 'n' for the next page of questions[/dim #FAD7A1]")
        if page > 0:
            console.print("[dim #FAD7A1]- Enter 'p' for the previous page of questions[/dim #FAD7A1]")
        console.print("[dim #FAD7A1]- Enter '0' to go one step back to the company list[/dim #FAD7A1]")
        console.print("[dim #FAD7A1]- Enter the question number (e.g., '1') to open it in your browser[/dim #FAD7A1]")
        
        choice = Prompt.ask("\nYour choice", default="")
        choice = choice.strip()
        
        if choice == "0":
            return # Go back to company list
        elif choice.lower() == 'n' and end_idx < len(questions):
            page += 1
        elif choice.lower() == 'p' and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(questions):
                url = questions[idx].get("url")
                if url and url != "N/A":
                    import webbrowser
                    console.print(f"[bold #F7CA18]Opening... {url}[/bold #F7CA18]")
                    webbrowser.open(url)
                else:
                    console.print("[bold #E74C3C]No URL available for this question.[/bold #E74C3C]")
                    Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")
            else:
                console.print("[bold #E74C3C]Invalid question number.[/bold #E74C3C]")
                Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")
        else:
            console.print("[bold #E74C3C]Invalid input.[/bold #E74C3C]")
            Prompt.ask("[dim #FAD7A1]Press Enter to continue...[/dim #FAD7A1]")

if __name__ == "__main__":
    app()
