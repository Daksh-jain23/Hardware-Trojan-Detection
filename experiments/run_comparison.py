"""Evaluate a saved GNN checkpoint from the repository root."""

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "src" / "evaluation.py"), run_name="__main__")
