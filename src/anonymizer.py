"""
Evidence anonymizer for Hardware Trojan detection.

Purpose:
    Remove lexical clues from node/net names before evidence is sent
    to the LLM.

Example:

    troj21_0U11  -> NODE_0001
    PI_troj21_0n6 -> NODE_0002

The anonymized evidence preserves:
    - GNN scores
    - gate types
    - fanin/fanout
    - graph structure
    - suspicious regions
    - sequential gates
    - region exits

It removes:
    - Trojan-related names
    - original identifiers
    - textual naming clues

The original -> anonymized mapping is saved separately and should
NOT be provided to the LLM.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


# ============================================================
# Configuration
# ============================================================

DEFAULT_OUTPUT_DIR = Path("results/anonymized")


# ============================================================
# Identifier anonymization
# ============================================================

def anonymize_identifier(identifier: str, index: int) -> str:
    """
    Convert an original hardware identifier into a neutral ID.

    Example:
        troj21_0U11 -> NODE_0001
        PI_troj21_0n6 -> NODE_0002
    """

    return f"NODE_{index:04d}"


# ============================================================
# Recursive replacement
# ============================================================

def collect_identifiers(value: Any, identifiers: set[str]) -> None:
    """
    Recursively collect strings that look like hardware identifiers.

    We collect identifiers from evidence rather than inventing a
    separate node list.
    """

    if isinstance(value, dict):

        for key, item in value.items():

            # Keys such as "node", "source", "target", "name"
            # frequently contain identifiers.
            if key.lower() in {
                "node",
                "name",
                "source",
                "target",
                "gate",
                "id",
                "node_id",
            }:

                if isinstance(item, str):
                    identifiers.add(item)

            collect_identifiers(item, identifiers)

    elif isinstance(value, list):

        for item in value:
            collect_identifiers(item, identifiers)


def build_mapping(evidence: dict) -> dict[str, str]:
    """
    Build a deterministic mapping from original identifiers
    to anonymous node identifiers.
    """

    identifiers: set[str] = set()

    collect_identifiers(evidence, identifiers)

    # Sort so anonymization is deterministic across runs.
    ordered = sorted(identifiers)

    return {
        identifier: anonymize_identifier(identifier, i + 1)
        for i, identifier in enumerate(ordered)
    }


def replace_identifiers(
    value: Any,
    mapping: dict[str, str],
) -> Any:
    """
    Recursively replace identifiers inside nested dictionaries/lists.
    """

    if isinstance(value, dict):

        result = {}

        for key, item in value.items():

            # Keys themselves are normally structural field names,
            # so do not anonymize them.
            result[key] = replace_identifiers(item, mapping)

        return result

    if isinstance(value, list):

        return [
            replace_identifiers(item, mapping)
            for item in value
        ]

    if isinstance(value, str):

        # Exact identifier replacement.
        if value in mapping:
            return mapping[value]

        # Replace identifiers embedded inside larger strings.
        result = value

        # Longest first prevents partial replacement.
        for original in sorted(
            mapping,
            key=len,
            reverse=True,
        ):

            result = result.replace(
                original,
                mapping[original],
            )

        return result

    return value


# ============================================================
# Remove lexical Trojan clues
# ============================================================

def sanitize_text(text: str) -> str:
    """
    Remove obvious Trojan-specific lexical clues from free text.

    This is intentionally conservative.

    Structural information is retained.
    """

    if not isinstance(text, str):
        return text

    patterns = [
        (r"\btrojan\b", "SUSPICIOUS"),
        (r"\btroj[a-zA-Z0-9_]*\b", "SUSPICIOUS"),
        (r"\btrigger\b", "TRIGGER_SIGNAL"),
        (r"\bpayload\b", "PAYLOAD_SIGNAL"),
    ]

    result = text

    for pattern, replacement in patterns:

        result = re.sub(
            pattern,
            replacement,
            result,
            flags=re.IGNORECASE,
        )

    return result


def sanitize_text_fields(value: Any) -> Any:
    """
    Recursively sanitize textual fields.

    Identifier replacement happens separately.
    """

    if isinstance(value, dict):

        return {
            key: sanitize_text_fields(item)
            for key, item in value.items()
        }

    if isinstance(value, list):

        return [
            sanitize_text_fields(item)
            for item in value
        ]

    if isinstance(value, str):

        return sanitize_text(value)

    return value


# ============================================================
# Main anonymization
# ============================================================

def anonymize_evidence(
    evidence: dict,
) -> tuple[dict, dict[str, str]]:
    """
    Anonymize evidence.

    Returns:
        anonymized_evidence
        original_to_anonymous_mapping
    """

    mapping = build_mapping(evidence)

    anonymized = replace_identifiers(
        evidence,
        mapping,
    )

    anonymized = sanitize_text_fields(
        anonymized
    )

    # Add explicit metadata so downstream LLM code knows
    # that identifiers have been anonymized.
    anonymized["anonymization"] = {
        "enabled": True,
        "identifier_scheme": "NODE_XXXX",
        "original_identifiers_removed": True,
        "lexical_trojan_clues_removed": True,
        "mapping_available_to_llm": False,
    }

    return anonymized, mapping


# ============================================================
# File processing
# ============================================================

def anonymize_file(
    input_path: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> tuple[Path, Path]:

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.exists():

        raise FileNotFoundError(
            f"Evidence file not found: {input_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as f:

        evidence = json.load(f)

    anonymized, mapping = anonymize_evidence(
        evidence
    )

    output_path = (
        output_dir
        / f"{input_path.stem}_anonymized.json"
    )

    mapping_path = (
        output_dir
        / f"{input_path.stem}_mapping.json"
    )

    # --------------------------------------------------------
    # Save anonymized evidence
    # --------------------------------------------------------

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            anonymized,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Save mapping separately.
    #
    # IMPORTANT:
    # This file must NOT be passed to the LLM.
    # --------------------------------------------------------

    with mapping_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            mapping,
            f,
            indent=2,
        )

    return output_path, mapping_path


# ============================================================
# Command-line interface
# ============================================================

def main() -> None:

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "  python src/anonymizer.py "
            "<evidence.json>"
        )

        sys.exit(1)

    input_path = sys.argv[1]

    print(
        "========== EVIDENCE ANONYMIZATION =========="
    )

    print(
        "Input:",
        input_path,
    )

    output_path, mapping_path = anonymize_file(
        input_path
    )

    print()
    print(
        "Anonymized evidence:",
        output_path,
    )

    print(
        "Private mapping:",
        mapping_path,
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "The mapping file must NOT be sent to the LLM."
    )


if __name__ == "__main__":
    main()