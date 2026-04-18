import dotenv 

from rich.console import Console
from openai import OpenAI
from os import getenv
from pathlib import Path
from subprocess import run, CompletedProcess

from typing import Any

import json, shutil

from .runners import _RUNNERS

dotenv.load_dotenv()

lang_map: dict[str, str] = {
    "py": "py",
    "python": "py",
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "rust": "rs",
    "rs": "rs"
}

console = Console()

CONFIG_PATH = Path.home() / ".wtf"

def get_api_key():
    key = getenv("OPENAI_API_KEY")

    if key:
        return key
        
    try:
        with open(CONFIG_PATH / "config.json", "r") as file:
            content = json.load(file)
        return content.get("OPENAI_API_KEY")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def check_api_key() -> bool:
    return bool(get_api_key())

def set_api_key_notice() -> None:
    console.print("wtf: [bold yellow]API key not set. set API key via 'wtf set-key <api_key>'[/bold yellow]")

def get_client() -> OpenAI | None:
    key = get_api_key()

    if not key:
        return None

    return OpenAI(api_key=key)

def update_config(content: dict | None = None, delete: bool = False) -> bool:
    if delete:
        if CONFIG_PATH.exists():
            shutil.rmtree(CONFIG_PATH)
        return True

    path = CONFIG_PATH / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    config = {}
    if path.exists():
        try:
            with open(path, "r") as file:
                config = json.load(file)
        except json.JSONDecodeError:
            console.print("wtf: [bold yellow]Config file is malformed, starting with empty config.[/bold yellow]")
            config = {}
        except FileNotFoundError:
            pass # Should not happen if path.exists() is true

    if content is not None:
        config.update(content) # Use update to merge dictionaries

    try:
        with open(path, "w") as file:
            json.dump(config, file, indent=4) # Use indent for readability
        return True
    except IOError: # Catch more general IO errors for writing
        console.print("wtf: [bold red]Failed to write to config file.[/bold red]")
        return False

def remove_config_value(key: str) -> None:
    path = Path(CONFIG_PATH / "config.json")

    config: dict[str] | None = get_config()

    if config is None:
        console.print("wtf: [bold green]Empty config, no need for changes.[/bold green]")
        return 

    try:
        config.pop(key)
    except KeyError:
        console.print(f'wtf: [bold red]Value "{key}" not found.[/bold red]')
        return

    try:
        with open(path, "w") as file:
            json.dump(config, file)

        console.print(f"wtf: [bold green]Removed value successfully.[/bold green]")
        return

    except FileNotFoundError:
        console.print("wtf: [bold red]Failed to update config.[/bold red]")
        return

def get_config() -> dict[str] | None:
    path = Path(CONFIG_PATH / "config.json")

    try:
        with open(path, "r") as file:
            content: dict[str] = json.load(file)

        return content   
    except (FileNotFoundError, json.JSONDecodeError):
        console.print("wtf: [bold red]Config not found[/bold red]")
        return None

def read_file(file: str) -> str | None:
    try:
        with open(file, "r") as f:
            file_content: str = f.read()

        return file_content
    except FileNotFoundError:
        console.print("wtf: [bold red]File not found.[/bold red]")
        return None

def write_file(file: str, content: str) -> bool:
    try:
        with open(file, "w") as f:
            f.write(content)
            
        return True
    except FileNotFoundError:
        console.print("wtf: [bold red]File not found.[/bold red]")
        return False

def exec_file(file: str, args: list[str] = None) -> CompletedProcess[Any] | None:
    ext = Path(file).suffix

    executor = _RUNNERS.get(ext, None)

    config: dict[str] = get_config()

    if config is None:
        return

    runner: str | None = config.get(f"{ext[1:]}_runner", None) 

    if executor is None:
        console.print("wtf: [bold red]Unknown file format.[/bold red]")
        return

    try:
        return executor.run(file, runner, args if args is not None else [])
    except FileNotFoundError as e:
        console.print("wtf: [bold red]File or runner not found[/bold red]")
        return None
        
    except Exception as e:
        console.print(f"wtf: [bold red]Execution failed[/bold red]")
        return None

def compile_file(file: str, args: list[str] = None) -> CompletedProcess[Any] | None:
    ext = Path(file).suffix 


