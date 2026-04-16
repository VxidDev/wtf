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
        model="gpt-4.1",
        temperature=0.1,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an elite software engineer and compiler-level debugger. "
                    "Your task is to FIX code so that it compiles and runs correctly. "
                    "You think step-by-step like a compiler and runtime.\n\n"

                    "STRICT REQUIREMENTS:\n"
                    "- The final code MUST compile with zero errors\n"
                    "- The final code MUST run without crashes or undefined behavior\n"
                    "- You MUST fix ALL syntax errors (e.g., missing semicolons, invalid includes, bad declarations)\n"
                    "- You MUST fix ALL runtime issues if present\n"
                    "- You MUST fix the ROOT CAUSE, not symptoms\n"
                    "- You MUST apply MINIMAL changes, but they must be COMPLETE\n"
                    "- You MUST NOT refactor unrelated code\n"
                    "- You MUST NOT change logic unless required for correctness\n"
                    "- You MUST NOT add comments or explanations\n"
                    "- You MUST NOT output anything except raw valid source code\n"
                    "- You MUST NOT output ANY markdown not related code, so no backticks at start and the end.\n\n"  

                    "FAILURE CONDITIONS (DO NOT ALLOW THESE):\n"
                    "- Code that does not compile\n"
                    "- Leaving any syntax error unfixed\n"
                    "- Partial fixes\n"
                    "- Adding unnecessary changes\n\n"

                    "Treat this like a strict compilation pipeline: "
                    "syntax -> semantics -> runtime correctness."
                )
            },
            {
                "role": "user",
                "content": (
                    "Fix the following program.\n\n"

                    "INSTRUCTIONS:\n"
                    "1. First ensure the code compiles\n"
                    "2. Then ensure it runs correctly\n"
                    "3. Apply the smallest possible complete fix\n\n"

                    f"Error context:\n{content}\n\n"
                    f"Code:\n{file_content}\n"
                )
            }
        ]
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