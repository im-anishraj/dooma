import typer
from dooma.cli import commands

app = typer.Typer(
    name="dooma",
    help="Dooma: A professional developer workspace for DSA practice.",
    no_args_is_help=True,
)

@app.callback()
def callback():
    """
    Dooma: A professional developer workspace for DSA practice.
    """
    pass

# Register commands
app.command(name="init")(commands.init_workspace)

if __name__ == "__main__":
    app()
