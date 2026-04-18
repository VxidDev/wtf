from typer import Typer, Argument 

from ..shared import console, get_config 
from ..runners import Compiler, _DEFAULT_RUNNER_STRINGS 

from pathlib import Path

app = Typer()

@app.command(name="compile")
def compile_file(file: str, args: list[str] = Argument([])) -> None:
    path = Path(file)

    if not path.exists():
        console.print("wtf: [bold red]File not found.[/bold red]")
        return 

    extension = path.suffix.lstrip('.')
    
    config: dict[str, str] | None = get_config()

    if config is None:
        return 

    compiler_string: str | None = config.get(f"{extension}_runner")

    if compiler_string is None:
        compiler_string = _DEFAULT_RUNNER_STRINGS.get(path.suffix)

        if compiler_string is None:
            console.print("wtf: [bold red]Unrecognized language.[/bold red]")
            return 

    compiler = Compiler(compiler_string)
    result = compiler(file, args)

    if result is None:
        return

    success = result.returncode == 0

    console.print(
        f"[bold]State: {'[green]SUCCESS[/green]' if success else '[red]FAIL[/red]'}[/bold]\n"
        f"[bold]Exit Code:[/bold] {result.returncode}\n\n"
        f"[bold cyan]STDOUT:[/bold cyan]\n{result.stdout.strip() or '[dim]_EMPTY_[/dim]'}\n"
        f"[bold red]STDERR:[/bold red]\n{result.stderr.strip() or '[dim]_EMPTY_[/dim]'}"
    )