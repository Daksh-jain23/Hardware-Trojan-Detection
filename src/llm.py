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

Supported providers:
    - Ollama / Qwen3 local
    - Gemini API

Change ACTIVE_PROVIDER below to switch models.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import ollama
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

# CHANGE ONLY THIS LINE TO SWITCH PROVIDERS
#
# "ollama"  -> local Qwen3
# "gemini"  -> Gemini API
#
ACTIVE_PROVIDER = "gemini"


# ------------------------------------------------------------
# Ollama configuration
# ------------------------------------------------------------

OLLAMA_MODEL = "qwen3:4b"


# ------------------------------------------------------------
# Gemini configuration
# ------------------------------------------------------------

# Change this if you want to test another Gemini model.
GEMINI_MODEL = "gemini-3.6-flash"


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = ROOT / "results" / "llm"

ENV_FILE = ROOT / ".env"


# Load .env if it exists.
load_dotenv(ENV_FILE)


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

    # Fallback: find standalone classifications.
    matches = re.findall(
        r"\b(SUSPICIOUS|NORMAL|UNCERTAIN)\b",
        text.upper(),
    )

    if matches:

        # Prefer the last classification because the conclusion
        # normally appears near the end.
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

def run_ollama(prompt: str) -> str:

    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=prompt,
        options={
            "temperature": 0.0,
            "seed": 42,
            "num_ctx": 32768,
        },
    )

    return response.get("response", "")


# ============================================================
# Gemini
# ============================================================

def run_gemini(prompt: str) -> str:

    try:
        from google import genai
    except ImportError:
        raise RuntimeError(
            "Gemini SDK is not installed.\n"
            "Install it with:\n"
            "  pip install google-genai"
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set.\n\n"
            "Add it to your .env file:\n"
            "GEMINI_API_KEY=your_api_key_here"
        )

    client = genai.Client(
        api_key=api_key
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text or ""


# ============================================================
# Unified LLM interface
# ============================================================

def run_llm(prompt: str) -> str:

    if ACTIVE_PROVIDER == "ollama":

        return run_ollama(prompt)

    elif ACTIVE_PROVIDER == "gemini":

        return run_gemini(prompt)

    else:

        raise ValueError(
            f"Unknown ACTIVE_PROVIDER: {ACTIVE_PROVIDER}\n"
            f"Use 'ollama' or 'gemini'."
        )


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

    # --------------------------------------------------------
    # Determine active model
    # --------------------------------------------------------

    if ACTIVE_PROVIDER == "ollama":

        active_model = OLLAMA_MODEL

    elif ACTIVE_PROVIDER == "gemini":

        active_model = GEMINI_MODEL

    else:

        raise ValueError(
            f"Invalid ACTIVE_PROVIDER: {ACTIVE_PROVIDER}"
        )

    # --------------------------------------------------------
    # Console
    # --------------------------------------------------------

    print(
        "========== HARDWARE TROJAN LLM =========="
    )

    print(
        "Provider:",
        ACTIVE_PROVIDER,
    )

    print(
        "Model   :",
        active_model,
    )

    print(
        "Prompt  :",
        prompt_path,
    )

    print(
        "Prompt length:",
        len(prompt),
        "characters",
    )

    print()
    print(
        f"Running {ACTIVE_PROVIDER}..."
    )

    # --------------------------------------------------------
    # Run model
    # --------------------------------------------------------

    response = run_llm(prompt)

    # --------------------------------------------------------
    # Extract result
    # --------------------------------------------------------

    decision = extract_decision(response)

    confidence = extract_confidence(response)

    # --------------------------------------------------------
    # Result object
    # --------------------------------------------------------

    result = {

        "task":
            "hardware_trojan_detection",

        "provider":
            ACTIVE_PROVIDER,

        "model":
            active_model,

        "decision":
            decision,

        "confidence":
            confidence,

        "response":
            response,

        "prompt_file":
            str(prompt_path.resolve()),

        "llm_constraints": {

            "temperature":
                0.0,

            "seed":
                42 if ACTIVE_PROVIDER == "ollama"
                else None,

            "heuristic_output_used":
                False,

            "node_names_used_for_decision":
                False,
        },
    }

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_name = (
        prompt_path.stem
        .replace("_prompt", "")
        + f"_{ACTIVE_PROVIDER}_llm.json"
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
    # Console result
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LLM RESULT")
    print("=" * 60)

    print(
        "Provider   :",
        ACTIVE_PROVIDER,
    )

    print(
        "Model      :",
        active_model,
    )

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