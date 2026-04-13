from typer import Typer 
from ..shared import console, exec_file
from subprocess import CompletedProcess

app = Typer()

@app.command()
def run(file: str) -> None:
    data: CompletedProcess = exec_file(file)

    console.print(
        f"Exit Code: {data.returncode}\n"
        f"STDOUT: {data.stdout.strip() or '_EMPTY_'}\n"
        f"STDERR: {data.stderr.strip() or '_EMPTY_'}"
    )    