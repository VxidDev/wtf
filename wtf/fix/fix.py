from typer import Typer 
from ..shared import console, check_api_key, get_client, set_api_key_notice, read_file, write_file, exec_file
import subprocess

app = Typer()

@app.command()
def fix(file: str, error: str = None) -> None:
    if not check_api_key():
        set_api_key_notice()
        return

    file_content: str | None = read_file(file)
    if file_content is None:
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
                "content": (
                    "You are a senior software engineer specializing in code debugging. "
                    "Your job is to fix bugs that cause crashes, undefined behavior, or incorrect execution. "
                    "You must prioritize correctness, safety, and minimal changes. "
                    "Do not refactor or improve style unless required to fix the bug."
                )
            },
            {
                "role": "user",
                "content": (
                    "Fix the following program.\n\n"
                    "Rules:\n"
                    "- The program must compile and run without undefined behavior\n"
                    "- You MUST eliminate the cause of crashes, not just change values\n"
                    "- If there is a NULL pointer dereference, you MUST add a safety check or restructure logic\n"
                    "- Fix control flow if needed (do NOT only change assignments)\n"
                    "- Preserve behavior only when it is safe\n"
                    "- Prefer fixing the root cause (incorrect initialization) over adding null checks, if possible.\n"
                    "- Apply minimal but COMPLETE fix (minimal changes allowed, but must fully fix the bug)\n"
                    "- Do NOT refactor unrelated code\n"
                    "- Do NOT add comments or explanations\n"
                    "- Return ONLY valid source code. No backticks, no markdown.\n\n"
                    f"Error context:\n{content}\n\n"
                    f"Code:\n{file_content}\n"
                )
            }
        ],

        temperature=0.1
    )

    console.print(f"[bold cyan]{response.output[0].content[0].text.strip()}[/bold cyan]\n\n")

    while True:
        console.print("[bold][white]Accept following changes?[/white]\n[green]Y[/green][white]/[/white][red]N[/red]:[/bold] ")
        user_input = input().lower()

        if user_input == "y":
            write_file(file, response.output[0].content[0].text.strip())
            return

        elif user_input == "n":
            console.print("wtf: [bold white]Changes discarded.[/bold white]")
            return 