#!/usr/bin/env python3
"""Bootstrap development environment for PlanGEN.

This script creates a virtual environment using Python's built-in ``venv``
module and installs all runtime and development dependencies. It is intended
to be run whenever a new workspace is initialized so contributors can start
working immediately.
"""

from __future__ import annotations

import os
import subprocess
import venv
from pathlib import Path


def create_virtualenv(env_dir: Path) -> None:
    """Create a virtual environment at ``env_dir`` if it does not exist."""
    if env_dir.exists():
        print(f"Virtual environment already exists at {env_dir}")
        return
    print(f"Creating virtual environment at {env_dir}")
    venv.EnvBuilder(with_pip=True).create(env_dir)


def run_in_env(env_dir: Path, *args: str) -> None:
    """Run a command inside the virtual environment."""
    python_path = (
        env_dir
        / ("Scripts" if os.name == "nt" else "bin")
        / ("python.exe" if os.name == "nt" else "python")
    )
    subprocess.check_call([str(python_path), *args])


def install_dependencies(env_dir: Path) -> None:
    """Install project and development dependencies."""
    run_in_env(env_dir, "-m", "pip", "install", "--upgrade", "pip")
    requirements = Path("requirements.txt")
    if requirements.exists():
        run_in_env(env_dir, "-m", "pip", "install", "-r", str(requirements))
    else:
        # Fall back to installing the package in editable mode
        run_in_env(env_dir, "-m", "pip", "install", "-e", ".[dev]")
    # Ensure ruff is available for linting
    run_in_env(env_dir, "-m", "pip", "install", "ruff")


def main() -> None:
    env_dir = Path(".venv")
    create_virtualenv(env_dir)
    install_dependencies(env_dir)
    activation = (
        f"{env_dir}\\Scripts\\activate"
        if os.name == "nt"
        else f"source {env_dir}/bin/activate"
    )
    print("\nSetup complete. Activate the virtual environment with:\n  " + activation)


if __name__ == "__main__":
    main()
