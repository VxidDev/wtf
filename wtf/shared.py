import dotenv 

from rich.console import Console
from openai import OpenAI
from os import getenv
from pathlib import Path

import json, shutil

dotenv.load_dotenv()

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

def update_config(content: dict | None = None, delete: bool = False) -> None:
    if delete:
        if CONFIG_PATH.exists():
            shutil.rmtree(CONFIG_PATH)

        return

    path = Path(CONFIG_PATH / "config.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        console.print("wtf: [bold red]Failed to update config.[/bold red]")
        return 

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
