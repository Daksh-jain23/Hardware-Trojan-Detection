"""
Hardware Trojan LLM reasoning stage.

Input:
    results/llm/*_prompt.txt

Output:
    results/llm/*_llm.json

The LLM is a downstream reasoning component.

It does NOT receive heuristic output.
It only receives the structured/anonymized evidence generated
by the preceding stages.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import ollama


# ============================================================
# Configuration
# ============================================================

MODEL = "qwen3:4b"

ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = ROOT / "results" / "llm"


# ============================================================
# Decision extraction
# ============================================================

VALID_DECISIONS = {
    "SUSPICIOUS",
    "NORMAL",
    "UNCERTAIN",
}


def extract_decision(text: str) -> str:

    # Prefer explicit required format.
    match = re.search(
        r"DECISION\s*:\s*(SUSPICIOUS|NORMAL|UNCERTAIN)",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        return match.group(1).upper()

    # Fallback: find a standalone decision.
    matches = re.findall(
        r"\b(SUSPICIOUS|NORMAL|UNCERTAIN)\b",
        text.upper(),
    )

    if matches:

        # Prefer the last classification because the model
        # normally states its conclusion near the end.
        for value in reversed(matches):

            if value in VALID_DECISIONS:
                return value

    return "UNCERTAIN"


# ============================================================
# Confidence extraction
# ============================================================

def extract_confidence(text: str) -> str:

    match = re.search(
        r"CONFIDENCE\s*:\s*(LOW|MEDIUM|HIGH)",
        text,
        flags=re.IGNORECASE,
    )

    if match:

        return match.group(1).upper()

    return "LOW"


# ============================================================
# Ollama
# ============================================================

def run_llm(prompt: str):

    response = ollama.generate(
        model=MODEL,
        prompt=prompt,
        options={
            "temperature": 0.0,
            "seed": 42,
            "num_ctx": 32768,
        },
    )

    return response.get("response", "")


# ============================================================
# Main
# ============================================================

def main():

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "  python src/llm.py <prompt.txt>"
        )

        sys.exit(1)

    prompt_path = Path(sys.argv[1])

    if not prompt_path.exists():

        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}"
        )

    prompt = prompt_path.read_text(
        encoding="utf-8"
    )

    print(
        "========== HARDWARE TROJAN LLM =========="
    )

    print(
        "Model  :",
        MODEL,
    )

    print(
        "Prompt :",
        prompt_path,
    )

    print(
        "Prompt length:",
        len(prompt),
        "characters",
    )

    print()
    print("Running Ollama...")

    response = run_llm(prompt)

    decision = extract_decision(response)

    confidence = extract_confidence(response)

    # --------------------------------------------------------
    # Result object
    # --------------------------------------------------------

    result = {
        "task": "hardware_trojan_detection",

        "model": MODEL,

        "decision": decision,

        "confidence": confidence,

        "response": response,

        "prompt_file": str(
            prompt_path.resolve()
        ),

        "llm_constraints": {
            "temperature": 0.0,
            "seed": 42,
            "heuristic_output_used": False,
            "node_names_used_for_decision": False,
        },
    }

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_name = (
        prompt_path.stem
        .replace("_prompt", "")
        + "_llm.json"
    )

    output_path = (
        RESULTS_DIR
        / output_name
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Console
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LLM RESULT")
    print("=" * 60)

    print(
        "Decision   :",
        decision,
    )

    print(
        "Confidence :",
        confidence,
    )

    print()
    print("MODEL RESPONSE")
    print("-" * 60)

    print(response)

    print()
    print(
        "Saved to:",
        output_path.resolve(),
    )


if __name__ == "__main__":
    main()