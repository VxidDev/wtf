from typer import Typer 
from ..shared import lang_map, console, get_config

from ..runners import _DEFAULT_RUNNER_STRINGS

from subprocess import run

app = Typer()

@app.command()
def diagnose(lang: str, file: str | None = None) -> None:
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

    if result.returncode == 127:
        console.print(f"wtf: [bold yellow]{executable} not found, can't run any {language} files.[/bold yellow]")
        return 

    if result.returncode != 0:
        console.print(f"wtf: [bold yellow]{executable} exists but may be misconfigured.[/bold yellow]")
        return

    console.print(f"wtf: [bold cyan]{executable} is available. {language} is ready.[/bold cyan]")