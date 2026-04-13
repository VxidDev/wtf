from ..shared import update_config
from typer import Typer

app = Typer()

@app.command(name="set-key")
def set_api_key(key: str) -> None:
    update_config(
        {
            "OPENAI_API_KEY": key
        }
    )

    console.print("wtf: [bold green]Updated API key successfully.[/bold green]")

@app.command(name="clear-key")
def clear_api_key() -> None:
    update_config(delete=True)
    console.print("wtf: [bold green]Cleared the API key data successfully.[/bold green]")