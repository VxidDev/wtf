from typer import Typer 
from ..shared import console, check_api_key, get_client, set_api_key_notice, exec_file
import subprocess

app = Typer()

@app.command()
def explain(error: str = None, file: str = None) -> None:
    if not check_api_key():
        set_api_key_notice()
        return

    if not error and not file:
        console.print("wtf: [bold red]Either --error or --file must be passed.[/bold red]")
        return

    if error:
        content = error 
    else:
        result = exec_file(file)

        content = f"[EXIT CODE] {result.returncode}\n[STDOUT] {result.stdout or 'empty'}\n[STDERR] {result.stderr or 'empty'}"

    response = get_client().responses.create(
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