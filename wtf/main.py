from typer import Typer
from .shared import console

from .fix import fix
from .explain import explain
from .config import config
from .run import run
from .diagnose import diagnose
from .compile import compiler

app = Typer(pretty_exceptions_enable=False)

app.add_typer(fix.app)
app.add_typer(explain.app)
app.add_typer(config.app)
app.add_typer(run.app)
app.add_typer(diagnose.app)
app.add_typer(compiler.app)

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        console.print(f"wtf-fatal: [bold red]{str(e)}[/bold red]")