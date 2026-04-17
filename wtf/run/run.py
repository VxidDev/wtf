from typer import Typer, Argument
from ..shared import console, exec_file
from subprocess import CompletedProcess

from rich.panel import Panel

import time 

app = Typer()

@app.command()
def run(file: str, args: list[str] = Argument([])) -> None:
    start = time.perf_counter()

    data: CompletedProcess | None = exec_file(file, args)
    if data is None:
        return

    duration = time.perf_counter() - start

    stdout = data.stdout.strip() or "[dim]_EMPTY_[/dim]"
    stderr = data.stderr.strip() or "[dim]_EMPTY_[/dim]"

    console.print(
        Panel.fit(
            f"[bold]Exit Code:[/bold] {data.returncode}\n"
            f"[bold]Time:[/bold] {duration:.3f}s\n\n"
            f"[bold cyan]STDOUT:[/bold cyan]\n{stdout}\n\n"
            f"[bold red]STDERR:[/bold red]\n{stderr}",
            title="Execution Result",
            border_style="blue"
        )
    )  