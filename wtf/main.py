import typer, sys, openai, dotenv, subprocess, os, pathlib, json, shutil  
from rich.console import Console

dotenv.load_dotenv()

app = typer.Typer()
CONFIG_PATH = pathlib.Path().home() / ".wtf"

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    try:
        with open(CONFIG_PATH / "config.json", "r") as file:
            content = json.load(file)
        API_KEY = content.get("OPENAI_API_KEY")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

if not API_KEY:
    client = None
else: 
    client = openai.OpenAI(api_key=API_KEY)

console = Console()

def check_api_key() -> bool:
    return bool(API_KEY)

def set_api_key_notice() -> None:
    console.print("wtf: [bold yellow]API key not set. set API key via 'wtf set-key <api_key>'[/bold yellow]")

def update_config(content: dict | None = None, delete: bool = False) -> None:
    if delete:
        if CONFIG_PATH.exists():
            shutil.rmtree(CONFIG_PATH)

        return

    path = pathlib.Path(CONFIG_PATH / "config.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(path, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        console.print("wtf: [bold red]Failed to update config.[/bold red]")
        return 

@app.command(name="set-key")
def set_api_key(key: str) -> None:
    global API_KEY

    update_config(
        {
            "OPENAI_API_KEY": key
        }
    )
    console.print("wtf: [bold green]Updated API key successfully.[/bold green]")

    API_KEY = key

@app.command(name="clear-key")
def clear_api_key() -> None:
    update_config(delete=True)
    console.print("wtf: [bold green]Cleared the API key data successfully.[/bold green]")

@app.command()
def explain(error: str = None, file: str = None) -> None:
    if not check_api_key() or client is None:
        set_api_key_notice()
        return

    if not error and not file:
        console.print("wtf: [bold red]Either --error or --file must be passed.[/bold red]")
        return

    if error:
        content = error 
    else:
        result = subprocess.run(
            ["./" + file.split(".")[0]],
            capture_output=True,
            text=True
        )

        content = f"[EXIT CODE] {result.returncode}\n[STDOUT] {result.stdout or 'empty'}\n[STDERR] {result.stderr or 'empty'}"

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": "You are a senior software engineer. Be concise and practical."
            },
            {
                "role": "user",
                "content": f"Explain this error:\n{content}"
            }
        ]
    )

    console.print(f"{response.output[0].content[0].text.strip()}")

@app.command()
def fix(file: str, error: str = None) -> None:
    if not check_api_key() or client is None:
        set_api_key_notice()
        return

    try:
        with open(file, "r") as f:
            file_content = f.read()
    except FileNotFoundError:
        console.print("wtf: [bold red]File not found.[/bold red]")
        return 

    if error:
        content = error 
    else:
        result = subprocess.run(
            ["./" + file.split(".")[0]],
            capture_output=True,
            text=True
        )

        content = f"[EXIT CODE] {result.returncode}\n[STDOUT] {result.stdout or 'empty'}\n[STDERR] {result.stderr or 'empty'}"

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": "You are a senior software engineer. Be concise and practical."
            },
            {
                "role": "user",
                "content": f"Fix following issue: {content}\n\nCode: {file_content}\n\nReturn ONLY fixed code. No markdown. No explanation."
            }
        ]
    )

    console.print(f"[bold cyan]{response.output[0].content[0].text.strip()}[/bold cyan]\n\n")

    while True:
        console.print("[bold][white]Accept following changes?[/white]\n[green]Y[/green][white]/[/white][red]N[/red]:[/bold] ")
        user_input = input().lower()

        if user_input == "y":
            try:
                with open(file, "w") as f:
                    f.write(response.output[0].content[0].text.strip())
                break 
            except FileNotFoundError:
                console.print("wtf: [bold red]File not found.[/bold red]")
                break
        elif user_input == "n":
            console.print("wtf: [bold white]Changes discarded.[/bold white]")
            break 

if __name__ == "__main__":
    app()