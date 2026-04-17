import subprocess
from pathlib import Path
import os
import shlex

from subprocess import CompletedProcess

_DEFAULT_RUNNER_STRINGS = {
    ".py": "python3 {file}",
    ".c": "gcc {file} -o {exe}",
    ".cpp": "g++ {file} -o {exe}",
    ".rs": "rustc {file} -o {exe}"
}

class Runner:
    def __init__(self, compile: bool = False, cleanup: bool = True) -> None:
        self.compile = compile
        self.cleanup = cleanup

    @staticmethod
    def _extract_file_data(file: str) -> dict[str, str]:
        path = Path(file)

        return {
            "name": path.stem,
            "ext": path.suffix.lstrip("."),
            "ext_with_dot": path.suffix,
            "full": path.name
        }

    def run(self, file: str, runner: str | None = None, arguments: list[str] | None = None) -> CompletedProcess | None:
        file_data: dict[str, str] = self._extract_file_data(file)

        if runner is None:
            runner: str | None = _DEFAULT_RUNNER_STRINGS.get(file_data["ext_with_dot"])

            if runner is None:
                print("wtf: Runner string not found.")
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
