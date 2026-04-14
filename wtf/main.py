from typer import Typer
from .shared import console

from .fix import fix
from .explain import explain
from .config import config
from .run import run

app = Typer(pretty_exceptions_enable=False)

app.add_typer(fix.app)
app.add_typer(explain.app)
app.add_typer(config.app)
app.add_typer(run.app)

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        console.print(f"wtf-fatal: [bold red]{str(e)}[/bold red]")