"""Run the configured LLM provider on a generated prompt."""

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "src" / "llm.py"), run_name="__main__")
