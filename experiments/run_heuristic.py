"""Run the independent heuristic baseline from repository root."""

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "src" / "heuristic.py"), run_name="__main__")
