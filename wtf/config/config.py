from ..shared import update_config, console, _RUNNERS, get_config, remove_config_value, lang_map
from typer import Typer, Option

import json

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

    extension = lang_map.get(lang)

    if not extension:
        console.print("wtf: [bold red]Unknown language.[/bold red]")
        return

    key = f".{extension}"

    if key not in _RUNNERS:
        console.print("wtf: [bold red]No runner registered for this language.[/bold red]")
        return

    update_config({f"{extension}_runner": command if not clear else None})

def _check_if_content(content: str) -> bool:
    if content is None:
        console.print("wtf: [bold red]Content must not be empty.[/bold red]")
        return False

    return True 

@app.command()
def config(action: str, target: str, content: str | None = Option(None, "--content", "-c")):
    action = action.lower()

    if action == "get":
        config: dict[str] | None = get_config()

        if config is None:
            return 

        value: str | None = config.get(target, None)

        if value is None:
            console.print(f'wtf: [bold red]Value "{target}" not found.[/bold red]')
            return 

        console.print(f"[bold][aqua]Value of \"{target}\":[/aqua] {config.get(target, None)}[/bold]")

    elif action == "set":
        if not _check_if_content(content):
            return

        update_config({
            target: content
        })

        console.print(f"wtf: [bold green]Updated \"{target}\"'s value successfully.[/bold green]")

    elif action == "remove":
        remove_config_value(target)
    else:
        console.print("wtf: [bold red]Unknown action.[/bold red]")

@app.command(name="get-config")
def get_cfg() -> None:
    config: dict[str] = get_config()

    if config is None:
        return 

    console.print_json(data=config)