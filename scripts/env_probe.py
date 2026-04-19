#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import importlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


TOOL_COMMANDS: dict[str, list[list[str]]] = {
    "git": [["git", "--version"]],
    "make": [["make", "--version"]],
    "lean": [["lean", "--version"], ["lean", "-v"]],
    "lake": [["lake", "--version"], ["lake", "-v"]],
    "elan": [["elan", "--version"]],
    "gcc": [["gcc", "--version"]],
    "clang": [["clang", "--version"]],
}

PYTHON_PACKAGES = [
    "pytest",
    "numpy",
    "scipy",
    "sympy",
    "pandas",
    "matplotlib",
    "networkx",
    "mpmath",
    "numba",
    "jax",
    "torch",
]


def run_command(cmd: list[str]) -> tuple[bool, str | None, str | None]:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"

    output = (proc.stdout or proc.stderr or "").strip()
    first_line = output.splitlines()[0] if output else None
    if proc.returncode == 0:
        return True, first_line, None
    return False, first_line, f"exit={proc.returncode}"


def probe_tool(name: str, notes: list[str]) -> dict[str, Any]:
    tool_path = shutil.which(name)
    result: dict[str, Any] = {
        "available": bool(tool_path),
        "path": tool_path,
        "version": None,
        "error": None,
    }
    if not tool_path:
        return result

    for cmd in TOOL_COMMANDS.get(name, [[name, "--version"]]):
        ok, first_line, err = run_command(cmd)
        if first_line:
            result["version"] = first_line
        if ok:
            return result
        result["error"] = err
    notes.append(f"version probe had nonzero exit for tool '{name}'")
    return result


def probe_python_package(name: str) -> dict[str, Any]:
    info: dict[str, Any] = {
        "available": False,
        "version": None,
        "error": None,
    }
    try:
        module = importlib.import_module(name)
        info["available"] = True
        version = getattr(module, "__version__", None)
        if not version:
            try:
                version = importlib.metadata.version(name)
            except Exception:
                version = None
        info["version"] = version
    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def memory_info(notes: list[str]) -> dict[str, Any]:
    mem: dict[str, Any] = {"mem_total_bytes": None}
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        try:
            for line in meminfo.read_text(encoding="utf-8").splitlines():
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    kb = int(parts[1])
                    mem["mem_total_bytes"] = kb * 1024
                    return mem
        except Exception as exc:
            notes.append(f"failed to parse /proc/meminfo: {type(exc).__name__}")
    notes.append("memory probe unavailable or unsupported on this platform")
    return mem


def main() -> int:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    output_path = repo_root / "results" / "capability_matrix" / "env_probe.json"
    notes: list[str] = []

    report: dict[str, Any] = {
        "timestamp_utc": now,
        "platform": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version.replace("\n", " "),
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
            "implementation": platform.python_implementation(),
        },
        "paths": {
            "cwd": os.getcwd(),
            "script_path": str(script_path),
            "repo_root_assumption": str(repo_root),
        },
        "tools": {},
        "python_packages": {},
        "hardware": {
            "cpu_count": os.cpu_count(),
        },
        "notes": notes,
    }

    for tool in TOOL_COMMANDS:
        report["tools"][tool] = probe_tool(tool, notes)

    for pkg in PYTHON_PACKAGES:
        report["python_packages"][pkg] = probe_python_package(pkg)

    report["hardware"].update(memory_info(notes))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    available_pkgs = [k for k, v in report["python_packages"].items() if v["available"]]
    print(
        "env_probe complete | "
        f"python={report['python']['major']}.{report['python']['minor']}.{report['python']['micro']} | "
        f"os={report['platform']['system']} {report['platform']['release']} {report['platform']['machine']} | "
        f"packages={len(available_pkgs)}/{len(PYTHON_PACKAGES)} available | "
        f"output={output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
