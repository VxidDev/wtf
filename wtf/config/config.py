from ..shared import update_config, console, _RUNNERS
from typer import Typer, Option

app = Typer()

@app.command(name="set-key")
def set_api_key(key: str) -> None:
    if update_config({"OPENAI_API_KEY": key}):
        console.print("wtf: [bold green]Updated API key successfully.[/bold green]")

@app.command(name="clear-key")
def clear_api_key() -> None:
    if update_config({"OPENAI_API_KEY": None}):
        console.print("wtf: [bold green]Cleared the API key data successfully.[/bold green]")

@app.command()
def runner(lang: str, command: str = None, clear: bool = Option(False, "--clear", "-c")) -> None:
    if not command and not clear:
        console.print("wtf: [bold yellow]missing argument 'command'[/bold yellow]")

    lang_map: dict[str, str] = {
        "py": "py",
        "python": "py",
        "c": "c",
        "cpp": "cpp",
        "c++": "cpp",
    }

    extension = lang_map.get(lang)

    if not extension:
        console.print("wtf: [bold red]Unknown language.[/bold red]")
        return

    key = f".{extension}"

    if key not in _RUNNERS:
        console.print("wtf: [bold red]No runner registered for this language.[/bold red]")
        return

    update_config({f"{extension}_runner": command if not clear else None})