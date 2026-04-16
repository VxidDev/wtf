import subprocess
from pathlib import Path
import os
import shlex

_DEFAULT_RUNNER_STRINGS = {
    ".py": "python3 {file}",
    ".c": "gcc {file} -o {exe}",
    ".cpp": "g++ {file} -o {exe}"
}

def run_python(file: str, runner: str | None = None, arguments: list[str] | None = None):
    if runner is None:
        runner = _DEFAULT_RUNNER_STRINGS.get(".py")

    cmd = shlex.split(runner.format(file=file))

    if arguments is None:
        arguments = []

    return subprocess.run(
        cmd + arguments,
        capture_output=True,
        text=True
    )

def run_c(file: str, runner: str | None = None, arguments: list[str] | None = None):
    if runner is None:
        runner = _DEFAULT_RUNNER_STRINGS.get(".c")

    exe = Path(file).stem
    cmd = shlex.split(runner.format(file=file, exe=exe))

    compile = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if compile.returncode != 0:
        return compile

    value = subprocess.run(
        ["./" + exe] + arguments,
        capture_output=True,
        text=True
    )

    try:
        os.remove(exe)
    except Exception:
        pass

    return value

def run_cpp(file: str, runner: str | None = None, arguments: list[str] | None = None):
    if runner is None:
        runner = _DEFAULT_RUNNER_STRINGS.get(".cpp")

    exe = Path(file).stem
    cmd = shlex.split(runner.format(file=file, exe=exe))

    compile = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if compile.returncode != 0:
        return compile

    value = subprocess.run(
        ["./" + exe] + arguments,
        capture_output=True,
        text=True
    )

    try:
        os.remove(exe)
    except Exception:
        pass

    return value

_RUNNERS: dict[callable[str, str]] = {
    ".py": run_python,
    ".c": run_c,
    ".cpp": run_cpp
} 
