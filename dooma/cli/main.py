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
app.command(name="pull")(commands.pull_problem)
app.command(name="test")(commands.test_problem)

# Prep commands
prep_app = typer.Typer(name="prep", help="Company preparation campaign mode.")
app.add_typer(prep_app)
prep_app.command(name="start")(commands.prep_start)
prep_app.command(name="next")(commands.prep_next)

if __name__ == "__main__":
    app()
