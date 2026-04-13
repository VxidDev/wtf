import subprocess
from pathlib import Path

def run_python(file: str):
    return subprocess.run(
        ["python3", file],
        capture_output=True,
        text=True
    )

def run_c(file: str):
    exe = Path(file).stem

    compile = subprocess.run(
        ["gcc", file, "-o", exe],
        capture_output=True,
        text=True
    )

    if compile.returncode != 0:
        return compile

    return subprocess.run(
        ["./" + exe],
        capture_output=True,
        text=True
    )

def run_cpp(file: str):
    exe = Path(file).stem

    compile = subprocess.run(
        ["g++", file, "-o", exe],
        capture_output=True,
        text=True
    )

    if compile.returncode != 0:
        return compile

    return subprocess.run(
        ["./" + exe],
        capture_output=True,
        text=True
    )

_RUNNERS: callable[str] = {
    ".py": run_python,
    ".c": run_c,
    ".cpp": run_cpp
} 
