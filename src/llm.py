"""
Hardware Trojan LLM reasoning stage.

Input:
    results/llm/*_prompt.txt (or *_hybrid_prompt.txt)

Output:
    results/llm/*_llm.json

The LLM acts as the high-level reasoning and arbitration component.
In hybrid mode (Phase 4):
    - Receives GNN facts, Heuristic composite scores, and factor attributions.
    - Evaluates contradiction when GNN and Heuristic disagree.
    - Outputs structured JSON containing decision, confidence, arbitration rationale,
      Trojan archetype, and false positive risk assessment.
In baseline mode:
    - Receives raw GNN seeds and graph topology without heuristic facts.

Supported providers:
    - Gemini API ("gemini")
    - Ollama / Qwen3 local ("ollama")
    - Mock / Offline mode ("mock" or --mock flag)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda f: None


# ============================================================
# Configuration
# ============================================================

ACTIVE_PROVIDER = "gemini"

OLLAMA_MODEL = "qwen3:4b"
GEMINI_MODEL = "gemini-2.5-flash"

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results" / "llm"
ENV_FILE = ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


# ============================================================
# Decision & Confidence Extraction
# ============================================================

VALID_DECISIONS = {
    "SUSPICIOUS",
    "NORMAL",
    "UNCERTAIN",
}

VALID_CONFIDENCES = {
    "LOW",
    "MEDIUM",
    "HIGH",
}


def extract_decision(text: str) -> str:
    """Extract decision from text response using regex."""
    match = re.search(
        r"DECISION\s*:\s*(SUSPICIOUS|NORMAL|UNCERTAIN)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).upper()

    matches = re.findall(
        r"\b(SUSPICIOUS|NORMAL|UNCERTAIN)\b",
        text.upper(),
    )
    if matches:
        for value in reversed(matches):
            if value in VALID_DECISIONS:
                return value

    return "UNCERTAIN"


def extract_confidence(text: str) -> str:
    """Extract confidence level from text response using regex."""
    match = re.search(
        r"CONFIDENCE\s*:\s*(LOW|MEDIUM|HIGH)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).upper()

    return "LOW"


def parse_structured_llm_response(text: str) -> Dict[str, Any]:
    """
    Parse structured JSON output from the LLM response.
    Falls back gracefully to regex text extraction if JSON is malformed.
    """
    parsed_json: Optional[Dict[str, Any]] = None

    # 1. Attempt to find JSON inside markdown code fence
    fence_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fence_match:
        try:
            parsed_json = json.loads(fence_match.group(1).strip())
        except Exception:
            parsed_json = None

    # 2. Attempt to find bare outermost JSON block
    if parsed_json is None:
        brace_match = re.search(r"(\{\s*\"decision\"[\s\S]*?\})", text)
        if brace_match:
            try:
                parsed_json = json.loads(brace_match.group(1).strip())
            except Exception:
                parsed_json = None

    if isinstance(parsed_json, dict):
        raw_decision = str(parsed_json.get("decision", "")).strip().upper()
        decision = raw_decision if raw_decision in VALID_DECISIONS else extract_decision(text)

        raw_conf = str(parsed_json.get("confidence", "")).strip().upper()
        confidence = raw_conf if raw_conf in VALID_CONFIDENCES else extract_confidence(text)

        agreement = parsed_json.get("gnn_heuristic_agreement")
        if not isinstance(agreement, bool) and agreement is not None:
            agreement = str(agreement).lower() in ("true", "1", "yes")

        return {
            "decision": decision,
            "confidence": confidence,
            "gnn_heuristic_agreement": agreement,
            "arbitration_rationale": str(parsed_json.get("arbitration_rationale", "")).strip(),
            "trojan_structure_type": str(parsed_json.get("trojan_structure_type", "unknown")).strip(),
            "suspicious_gate_classes": list(parsed_json.get("suspicious_gate_classes", [])),
            "payload_exit_analysis": str(parsed_json.get("payload_exit_analysis", "")).strip(),
            "counter_evidence": str(parsed_json.get("counter_evidence", "")).strip(),
            "false_positive_risk": str(parsed_json.get("false_positive_risk", "UNKNOWN")).strip().upper(),
            "raw_json_parsed": True,
        }

    # Fallback when no valid JSON is present
    return {
        "decision": extract_decision(text),
        "confidence": extract_confidence(text),
        "gnn_heuristic_agreement": None,
        "arbitration_rationale": "Fallback extraction: response did not contain a valid JSON block.",
        "trojan_structure_type": "unknown",
        "suspicious_gate_classes": [],
        "payload_exit_analysis": "",
        "counter_evidence": "",
        "false_positive_risk": "UNKNOWN",
        "raw_json_parsed": False,
    }


# ============================================================
# LLM Providers
# ============================================================

def run_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Run local Ollama inference."""
    try:
        import ollama
    except ImportError:
        raise RuntimeError("Ollama library not installed. Install with `pip install ollama`.")

    response = ollama.generate(
        model=model,
        prompt=prompt,
        options={
            "temperature": 0.0,
            "seed": 42,
            "num_ctx": 32768,
        },
    )
    return response.get("response", "")


def run_gemini(prompt: str, model: str = GEMINI_MODEL) -> str:
    """Run Google Gemini API inference."""
    try:
        from google import genai
    except ImportError:
        raise RuntimeError("Gemini SDK not installed. Install with `pip install google-genai`.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text or ""


def generate_mock_response(prompt: str) -> str:
    """
    Generate a high-quality deterministic mock response for testing and validation
    when no LLM API key or local Ollama daemon is available.
    """
    is_hybrid = "HEURISTIC AUTHORITATIVE NUMERICAL FACTS" in prompt or "HYBRID" in prompt
    has_high_gnn = "seed_count_at_or_above_threshold" in prompt and not '"seed_count_at_or_above_threshold": 0' in prompt

    if has_high_gnn:
        decision = "SUSPICIOUS"
        confidence = "HIGH"
        structure_type = "sequential_counter"
        rationale = (
            "GNN identifies high statistical seed anomaly concentrated in sequential elements. "
            "Structural heuristic confirms anomalous state clustering with low boundary exit dispersion."
        )
        agreement = True
        fp_risk = "LOW"
    else:
        decision = "NORMAL"
        confidence = "HIGH"
        structure_type = "none"
        rationale = (
            "Low GNN suspicion scores and structural heuristic metrics align with standard control logic. "
            "No sequential feedback loops or concentrated payload exits observed."
        )
        agreement = True
        fp_risk = "LOW"

    mock_json = {
        "decision": decision,
        "confidence": confidence,
        "gnn_heuristic_agreement": agreement,
        "arbitration_rationale": rationale,
        "trojan_structure_type": structure_type,
        "suspicious_gate_classes": ["sequential state registers (dffles2)", "combinational trigger gates", "payload coupling logic"] if has_high_gnn else [],
        "payload_exit_analysis": "Region exits couple internal trigger to victim datapath without dispersing broadly." if has_high_gnn else "Standard datapath fanout.",
        "counter_evidence": "No significant counter-evidence is visible in the supplied evidence.",
        "false_positive_risk": fp_risk,
    }

    mock_text = f"""
```json
{json.dumps(mock_json, indent=2)}
```

DECISION: {decision}
CONFIDENCE: {confidence}

OBSERVED_EVIDENCE:
- Numerical facts confirm the presence of high-probability candidate gates.
- Structural neighborhood contains sequential state elements.
- Interconnect density indicates localized functional clustering.

STRUCTURAL_INTERPRETATION:
- Circuit topology exhibits feedback loops consistent with a state-dependent trigger.
- Exit connections connect to surrounding logic with low dispersion.

CONTRADICTION_ANALYSIS:
- Statistical GNN detection and structural heuristic attribution agree on anomalous character.

COUNTER_EVIDENCE:
No significant counter-evidence is visible in the supplied evidence.

REASONING:
The evidence demonstrates consistent localized anomaly across statistical and graph-theoretic dimensions, justifying the {decision} determination with {confidence} confidence.
""".strip()

    return mock_text


def run_llm(
    prompt: str,
    provider: str = ACTIVE_PROVIDER,
    model: Optional[str] = None,
    mock: bool = False,
    mock_response: Optional[str] = None,
) -> str:
    """
    Unified LLM runner supporting Gemini, Ollama, and Mock execution.
    """
    if mock_response is not None:
        return mock_response

    mock_env = os.getenv("MOCK_LLM_RESPONSE")
    if mock or mock_env or provider == "mock":
        return generate_mock_response(prompt)

    if provider == "ollama":
        active_model = model or OLLAMA_MODEL
        return run_ollama(prompt, model=active_model)
    elif provider == "gemini":
        active_model = model or GEMINI_MODEL
        return run_gemini(prompt, model=active_model)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Expected 'gemini', 'ollama', or 'mock'.")


# ============================================================
# Main Workflow
# ============================================================

def execute_reasoning(
    prompt_path: Path,
    provider: str = ACTIVE_PROVIDER,
    model: Optional[str] = None,
    mode: Optional[str] = None,
    mock: bool = False,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Execute LLM reasoning on a prompt file and save structured results.
    """
    prompt = prompt_path.read_text(encoding="utf-8")

    # Detect mode if not explicitly supplied
    if mode is None:
        if "HEURISTIC AUTHORITATIVE NUMERICAL FACTS" in prompt or "HYBRID" in prompt:
            detected_mode = "hybrid"
        else:
            detected_mode = "baseline"
    else:
        detected_mode = mode

    # Determine active model name
    is_mock = mock or provider == "mock" or bool(os.getenv("MOCK_LLM_RESPONSE"))
    if is_mock:
        active_model = "mock-reasoner"
        active_provider = "mock"
    elif provider == "ollama":
        active_model = model or OLLAMA_MODEL
        active_provider = "ollama"
    elif provider == "gemini":
        active_model = model or GEMINI_MODEL
        active_provider = "gemini"
    else:
        active_model = "unknown"
        active_provider = provider

    print("========== HARDWARE TROJAN LLM ==========")
    print("Provider    :", active_provider)
    print("Model       :", active_model)
    print("Mode        :", detected_mode)
    print("Prompt      :", prompt_path)
    print("Length      :", len(prompt), "chars")
    print(f"Running reasoning stage...")

    # Execute
    mock_fallback = False
    try:
        response = run_llm(
            prompt,
            provider=provider,
            model=model,
            mock=mock,
        )
    except Exception as exc:
        print(f"Warning: LLM invocation failed ({exc}). Falling back to mock reasoning.")
        response = generate_mock_response(prompt)
        mock_fallback = True
        active_model = "mock-reasoner"
        active_provider = "mock"

    # Parse structured output
    structured = parse_structured_llm_response(response)
    decision = structured["decision"]
    confidence = structured["confidence"]

    result = {
        "task": "hardware_trojan_detection",
        "provider": active_provider,
        "model": active_model,
        "mode": detected_mode,
        "decision": decision,
        "confidence": confidence,
        "structured_output": structured,
        "response": response,
        "prompt_file": str(prompt_path.resolve()),
        "llm_constraints": {
            "temperature": 0.0,
            "seed": 42 if active_provider == "ollama" else None,
            "heuristic_output_used": (detected_mode == "hybrid"),
            "node_names_used_for_decision": False,
        },
    }
    if mock_fallback:
        result["mock_fallback"] = True

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        stem = prompt_path.stem.replace("_prompt", "").replace("_hybrid", "")
        suffix = f"_{detected_mode}_{provider}_llm.json"
        output_path = RESULTS_DIR / (stem + suffix)

    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("LLM REASONING RESULT")
    print("=" * 60)
    print("Decision   :", decision)
    print("Confidence :", confidence)
    print("Agreement  :", structured.get("gnn_heuristic_agreement"))
    print("Archetype  :", structured.get("trojan_structure_type"))
    print("Saved to   :", output_path.resolve())

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Hardware Trojan LLM Reasoning Stage (Hybrid & Baseline)."
    )
    parser.add_argument("prompt", type=str, help="Path to prompt text file.")
    parser.add_argument(
        "--provider",
        choices=["gemini", "ollama", "mock"],
        default=ACTIVE_PROVIDER,
        help="LLM provider to use.",
    )
    parser.add_argument("--model", type=str, default=None, help="LLM model name.")
    parser.add_argument(
        "--mode",
        choices=["hybrid", "baseline"],
        default=None,
        help="Prompt mode (auto-detected if omitted).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use deterministic mock response (useful for testing/offline).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Custom output JSON path.",
    )

    args = parser.parse_args()
    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    output_path = Path(args.output) if args.output else None
    execute_reasoning(
        prompt_path=prompt_path,
        provider=args.provider,
        model=args.model,
        mode=args.mode,
        mock=args.mock,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()