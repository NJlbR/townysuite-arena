#!/usr/bin/env python3
"""Compatibility entry point for the canonical, fully synchronized plugin release build."""
from pathlib import Path
import subprocess
import sys

repo_root = Path(__file__).resolve().parent
build_script = repo_root / "build_and_package.py"
result = subprocess.run([sys.executable, str(build_script)], cwd=repo_root)
raise SystemExit(result.returncode)
