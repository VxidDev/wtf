import subprocess
from pathlib import Path
import os
import shlex

from subprocess import CompletedProcess

from rich.console import Console 

console = Console()

compiled_lang_map: dict[str, str] = {
    "c": "c",
    "cpp": "cpp",
    "c++": "cpp",
    "rust": "rs",
    "rs": "rs"
}

def _extract_file_data(file: str) -> dict[str, str]:
    path = Path(file)

    return {
        "name": path.stem,
        "ext": path.suffix.lstrip("."),
        "ext_with_dot": path.suffix,
        "full": path.name
    }

_DEFAULT_RUNNER_STRINGS = {
    ".py": "python3 {file}",
    ".c": "gcc {file} -o {exe}",
    ".cpp": "g++ {file} -o {exe}",
    ".rs": "rustc {file} -o {exe}"
}

class Compiler:
    def __init__(self, compiler_string: str) -> None:
        self.compiler_string: str = compiler_string # compiler_string must have {file} and {exe} placeholders.

    def __call__(self, file: str, args: list[str] | None = None) -> CompletedProcess | None:
        file_data: dict[str, str] = _extract_file_data(file)

        if file_data["ext"] not in compiled_lang_map:
            console.print(f"wtf: [bold red].{file_data['ext']} files do not support compilation.[/bold red]")
            return 

        cmd = shlex.split(self.compiler_string.format(file=file, exe=file_data["name"]))

        if args is None:
            args = []

        compile_proc = subprocess.run(
            cmd + args,
            capture_output=True,
            text=True
        )

        return compile_proc

class Runner:
    def __init__(self, compile: bool = False, cleanup: bool = True) -> None:
        self.compile = compile
        self.cleanup = cleanup

    def run(self, file: str, runner: str | None = None, arguments: list[str] | None = None) -> CompletedProcess | None:
        file_data: dict[str, str] = _extract_file_data(file)

        if runner is None:
            runner: str | None = _DEFAULT_RUNNER_STRINGS.get(file_data["ext_with_dot"])

            if runner is None:
                console.print("wtf: [bold red]Runner string not found.[/bold red]")
                return 

        format_args: dict[str, str] = {
            "file": file
        }

        if self.compile:
            format_args["exe"] = file_data.get("name")

        cmd = shlex.split(runner.format(**format_args))

        if arguments is None:
            arguments = []

        if self.compile:
            compile_proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if compile_proc.returncode != 0:
                return compile_proc

            exe = format_args["exe"]

            value = subprocess.run(
                ["./" + exe] + arguments,
                capture_output=True,
                text=True
            )

            if self.cleanup:
                try:
                    os.remove(exe)
                except Exception:
                    pass
        else:
            return subprocess.run(
                cmd + arguments,
                capture_output=True,
                text=True
            )

        return value

_RUNNERS: dict[str, Runner] = {
    ".py": Runner(),
    ".c": Runner(True),
    ".cpp": Runner(True),
    ".rs": Runner(True)
} 
