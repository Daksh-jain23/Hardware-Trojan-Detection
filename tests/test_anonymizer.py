import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from anonymizer import anonymize_evidence


def test_anonymizer_replaces_identifiers_and_lexical_clues():
    evidence = {
        "nodes": [{"gate": "troj01U1", "outputs": ["normal_gate"]}],
        "note": "trojan payload uses troj_signal",
    }

    anonymized, mapping = anonymize_evidence(evidence)

    assert mapping["troj01U1"].startswith("NODE_")
    assert anonymized["nodes"][0]["gate"].startswith("NODE_")
    assert "troj" not in anonymized["note"].lower()
