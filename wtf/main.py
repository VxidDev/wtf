from typer import Typer

from .fix import fix
from .explain import explain
from .config import config

app = Typer()

app.add_typer(fix.app)
app.add_typer(explain.app)
app.add_typer(config.app)

if __name__ == "__main__":
    app()