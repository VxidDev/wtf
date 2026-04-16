from typer import Typer, Argument
from ..shared import console, exec_file
from subprocess import CompletedProcess

app = Typer()

@app.command()
def run(file: str, args: list[str] = Argument([])) -> None:
    data: CompletedProcess | None = exec_file(file, args)

    if data is None:
        return

    console.print(
        f"Exit Code: {data.returncode}\n"
        f"STDOUT: {data.stdout.strip() or '_EMPTY_'}\n"
        f"STDERR: {data.stderr.strip() or '_EMPTY_'}"
    )    