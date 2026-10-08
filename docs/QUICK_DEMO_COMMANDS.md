# Quick Demonstration & Execution Runbook

This document contains copy-pasteable commands to demonstrate the entire pipeline quickly in under 5 minutes.

---

## 🚀 30-Second Fast Verification (Skip LLM Inference)

To verify that the entire GNN extraction, graph parsing, matched clean control pairing, zero-leakage anonymization, and heuristic baseline work cleanly without waiting for LLM network latency:

```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --files \
    data/TRIT-TS/s13207_T421/s13207_T421.v \
    data/TRIT-TS/original_designs/s13207scan.v \
  --checkpoint checkpoints/trojan_gnn.pt \
  --skip-llm
```

---

## 🎯 1-Minute Single Circuit Deep Analysis (Full Hardware Trojan Report)

Extract the candidate region, compute structural evidence, and generate the in-depth hardware security analysis report:

```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/pipeline.py \
  data/TRIT-TS/s13207_T421/s13207_T421.v \
  --checkpoint checkpoints/trojan_gnn.pt
```

**Where to view the generated report**:
```bash
cat results/llm/s13207_T421_evidence_anonymized_llm.json
```

---

## 📊 3-Minute A/B Evaluation: Heuristic vs. LLM vs. Critic (3-Way Comparison)

Run the full Controlled A/B Evaluation across 4 circuits (Infected and Clean) to generate the complete 3-way comparative evaluation table:

```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --files \
    data/TRIT-TS/s35932_T428/s35932_T428.v \
    data/TRIT-TS/s35932_T431/s35932_T431.v \
    data/TRIT-TS/s13207_T421/s13207_T421.v \
    data/TRIT-TS/original_designs/s13207scan.v \
  --checkpoint checkpoints/trojan_gnn.pt
```

**What this outputs in your terminal**:
1. Single-circuit summaries with LLM explanations for Trial 1 & Trial 2 swapped.
2. The final 3-way comparative metrics table:
   - **Column 1**: Heuristic Baseline
   - **Column 2**: LLM (Without Critic)
   - **Column 3**: LLM (With Critic)
3. Saves full numerical data to `results/ab_evaluation/ab_metrics_summary.json`.

---

## 🏋️ 2-Minute GNN Retraining on Benchmark Families

Train a fresh GNN model across benchmark circuit families (`s13207`, `s1423`, and `s35932`):

```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/train_gnn.py \
  --data-dir data/TRIT-TS \
  --train-families s13207 \
  --val-families s1423 \
  --test-families s35932 \
  --epochs 20 \
  --checkpoint checkpoints/trojan_gnn.pt
```

---

## 🧪 5-Second Test Suite Verification

Run the full automated test suite to verify parsers, anonymizers, feature calculations, and the Critic loop:

```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 -m unittest discover tests
```

