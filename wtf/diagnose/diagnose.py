from typer import Typer, Option 
from ..shared import lang_map, console, get_config

from ..runners import _DEFAULT_RUNNER_STRINGS, Compiler, compiled_lang_map

from subprocess import run, CompletedProcess
from pathlib import Path

import os

app = Typer()

@app.command()
def diagnose(lang: str, file: str | None = None, args: list[str] | None = Option(None, "--argument", "-a"), cleanup: bool = Option(False, "--cleanup", "-c")) -> None:
    language: str | None = lang_map.get(lang, None)

    if language is None:
        console.print("wtf: [bold red]Unrecognized language.[/bold red]")
        return 

    config: dict[str, str] | None = get_config()

    if config is None:
        return 

    runner_string: str | None = config.get(f"{language}_runner", None)

    if runner_string is None:
        runner_string = _DEFAULT_RUNNER_STRINGS.get(f".{language}", None)

        if runner_string is None:
            console.print(f"wtf: [bold red]Couldn't find runner string for {language}.[/bold red]")
            return

    executable = runner_string.split()[0]

    try:
        result = run([executable, "--version"], capture_output=True)
    except FileNotFoundError:
        console.print(f"wtf: [bold yellow]{executable} not found, can't run any {language} files.[/bold yellow]")
        return 

    if result.returncode != 0:
        console.print(f"wtf: [bold yellow]{executable} exists but may be misconfigured.[/bold yellow]")
        return

    console.print(f"wtf: [bold cyan]{executable} is available. {language} is ready.[/bold cyan]")

    if not file:
        return

    path = Path(file) 
    
    if not path.exists():
        console.print(f"wtf: [bold red]File not found.[/bold red]")
        return

    extension: str = path.suffix.lstrip('.')

    if extension not in compiled_lang_map:
        console.print(f"wtf: [bold cyan].{extension} files do not support compilation, skipping compilation test.[/bold cyan]")
        return   

    compiler_string: str | None = config.get(f"{extension}_runner")

    if compiler_string is None:
        compiler_string: str | None = _DEFAULT_RUNNER_STRINGS.get(f"{path.suffix}")

        if compiler_string is None:
            console.print(f"wtf: [bold red]Unrecognized language.[/bold red]")
            return 

    compiler = Compiler(compiler_string)
    result: CompletedProcess | None = compiler(file, args)

    if result is None:
        console.print(f"\n[bold]State: [red]FAIL[/red][/bold]\nwtf: [bold red]Compilation result is None.[/bold red]")
        return
    
    success: bool = result.returncode == 0

    console.print(
        f"\n[bold]State: {'[green]SUCCESS[/green]' if success else '[red]FAIL[/red]'}[/bold]\n"
        f"[bold]Exit Code:[/bold] {result.returncode}\n\n"
        f"[bold cyan]STDOUT:[/bold cyan]\n{result.stdout.strip() or '[dim]_EMPTY_[/dim]'}\n"
        f"[bold red]STDERR:[/bold red]\n{result.stderr.strip() or '[dim]_EMPTY_[/dim]\n'}"
    )

    if cleanup:
        try:
            os.remove(path.stem)
        except Exception:
            pass 

    console.print(
        f"wtf: [bold]{f'[green]Compilation succeeded, [/green][cyan]{file}[/cyan] [green]can be ran.[/green]' if success else f'[red]Compilation failed. [/red][cyan]{file}[/cyan][red] cannot be ran.[/red]'}[/bold]"
    )

