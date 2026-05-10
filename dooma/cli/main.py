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
app.command(name="sync")(commands.sync_registry)
app.command(name="pull")(commands.pull_problem)

if __name__ == "__main__":
    app()
