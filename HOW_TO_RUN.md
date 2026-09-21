# Execution Guide: Hardware Trojan Detection System

This guide explains how to run every phase of the project: training the GNN, evaluating the GNN, running the independent heuristic baseline, comparing GNN vs. Heuristic, running the GNN+LLM explanation pipeline, running the controlled A/B swap evaluation, and executing all automated tests.

---

## 1. Prerequisites and Environment Setup

Activate the Python virtual environment:
```bash
source /home/daksh-jain/Code/Minor-Project/.venv/bin/activate
cd "/home/daksh-jain/Code/Minor-Project/Hardware trojan detection"
```

Verify that all dependencies are installed:
```bash
python -c "import torch, torch_geometric, networkx, sklearn, google.genai, ollama; print('All packages ready.')"
```

If using Gemini API, ensure your `.env` contains:
```bash
GEMINI_API_KEY=your_key_here
```
*(If offline or without an API key, the system automatically falls back to local Ollama `qwen3:4b`)*.

---

## 2. Training the GNN Model

### Option 1: Family-Holdout Split (Default - Zero-Shot Inductive Evaluation)
The model is trained across benchmark families with zero intra-circuit leakage:
- **Training Families**: `s13207`, `s1423`
- **Validation Family**: `s15850` (used for checkpointing and threshold tuning)
- **Held-Out Test Family**: `s35932`

```bash
python src/train_gnn.py --split-strategy family
```

### Option 2: Whole-Dataset Train/Test Split (Stratified or Random)
To pool all 338 netlists across all circuit families and perform a stratified 70% Train, 15% Validation, 15% Test split:
```bash
python src/train_gnn.py \
    --split-strategy stratified \
    --train-ratio 0.70 \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --epochs 100 \
    --checkpoint checkpoints/trojan_gnn_whole_dataset.pt
```

For a simple random split across the whole dataset:
```bash
python src/train_gnn.py --split-strategy random --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15
```

---

## 3. Evaluating the Standalone GNN Model (Experiment A)

To evaluate the trained GNN checkpoint on the unseen test circuit family (`s35932`):
```bash
python src/run_experiments.py --experiment A
```
Or directly:
```bash
python src/evaluation.py
```

**Outputs Produced**:
- Saved metrics: `results/gnn/experiment_a_s35932.json`
- Metrics: Precision, Recall, F1-Score, ROC-AUC, Average Precision, Confusion Matrix.

---

## 4. Evaluating the Independent Heuristic Baseline (Experiment B)

The heuristic detector operates strictly on deterministic structural graph criteria (fan-in/fan-out anomalies, sequential cluster isolation, boundary connectivity) with zero GNN or LLM input:
```bash
python src/run_experiments.py --experiment B
```
Or directly on a specific netlist:
```bash
python src/heuristic.py data/TRIT-TS/s13207_T421/s13207_T421.v
```

**Outputs Produced**:
- Saved metrics: `results/heuristic/experiment_b_s35932.json`
- Single-circuit result: `results/heuristic/<netlist_name>_heuristic.json`

---

## 5. Quantitative Comparison: GNN vs. Heuristic

The table below summarizes the quantitative evaluation on the unseen test family `s35932` (86,732 gates, 211 ground-truth Trojan gates):

| Metric | Standalone GNN (Exp A) | Heuristic Baseline (Exp B) | Delta / Winner |
|---|:---:|:---:|:---:|
| **Precision** | **94.35%** (0.9435) | **100.00%** (1.0000) | Heuristic (+5.65%) |
| **Recall** | **79.15%** (0.7915) | **17.06%** (0.1706) | **GNN (+62.09%)** |
| **F1-Score** | **86.08%** (0.8608) | **29.15%** (0.2915) | **GNN (+56.93%)** |
| **ROC-AUC** | **99.70%** (0.9970) | **72.82%** (0.7282) | **GNN (+26.88%)** |
| **Average Precision** | **94.52%** (0.9452) | **18.89%** (0.1889) | **GNN (+75.63%)** |
| **Trojan Gates Detected** | **167 / 211** | **36 / 211** | **GNN (+131 gates)** |
| **False Positives** | **10 gates** | **0 gates** | Heuristic (-10 gates) |

**Key Takeaway**:
- The Heuristic baseline has perfect precision but suffers from extreme tunnel vision (17.06% recall), missing 83% of Trojans.
- The GNN generalizes robustly to unseen circuit structures, achieving an **86.08% F1-score** and **99.70% ROC-AUC**.

---

## 6. Running the End-to-End Pipeline: GNN + Evidence + LLM (Experiment C)

To run the complete 7-stage pipeline on a netlist:
```bash
python src/run_experiments.py --experiment C --circuit data/TRIT-TS/s13207_T421/s13207_T421.v
```
Or directly:
```bash
python src/pipeline.py data/TRIT-TS/s13207_T421/s13207_T421.v
```

**Stages Executed**:
1. Netlist parsing to directed graph.
2. 41-feature node matrix computation.
3. GNN scoring over all circuit gates.
4. Suspicious GNN seed extraction ($p \ge 0.95$).
5. 2-hop bounded region expansion around seeds.
6. Structured evidence extraction (global facts, boundary exits, local patterns).
7. Zero-leakage anonymization and prompt generation.
8. LLM structural interpretation and explanation.

**Outputs Generated**:
- Evidence: `results/evidence/<circuit>_evidence.json`
- Anonymized Evidence: `results/anonymized/<circuit>_evidence_anonymized.json`
- Prompt: `results/llm/<circuit>_prompt.txt`
- LLM Output: `results/llm/<circuit>_<provider>_llm.json`

---

## 7. Running Controlled A/B Swap-Consistency Evaluation (Experiment D)

To test the LLM for position bias and swap consistency:
```bash
python src/run_experiments.py --experiment D --circuit data/TRIT-TS/s13207_T421/s13207_T421.v
```
Or directly:
```bash
python src/ab_evaluation.py data/TRIT-TS/s13207_T421/s13207_T421.v
```

**Outputs Generated**:
- Results saved to: `results/ab_evaluation/<circuit>_ab_result.json`
- Shows Trial 1 decision, Trial 2 decision, whether swap-consistent (`True`), and position bias (`False`).

---

## 8. Running GNN -> LLM Quantitative Benchmark (Experiment E)

To evaluate the LLM quantitatively across benchmark cohorts (multi-circuit A/B accuracy, swap-consistency, precision, recall, false alarm suppression, and Brier calibration score):

```bash
# Run standalone quantitative evaluation across Trojan and Clean cohorts:
python src/eval_gnn_llm_quantitative.py --backend gemini

# Quick verification mode (2 Trojan + 2 Clean circuits):
python src/eval_gnn_llm_quantitative.py --quick --backend gemini

# Or via the experiment runner:
python src/run_experiments.py --experiment E
```

**Outputs Generated**:
- `results/gnn_llm_quantitative_metrics.json`:
  - `ab_evaluation_benchmark`: Multi-circuit A/B accuracy (83.33%), swap consistency rate (66.67%), position bias rate, binomial $p$-value.
  - `classification_benchmark`: Precision (66.67%), Recall (66.67%), F1 (66.67%), False Alarm Suppression Rate (66.7%), Brier score (0.1825).

---

## 9. Running the Complete Consolidated Experiment Suite

To execute all experiments (A, B, C, D, E) in a single run and generate `results/final_metrics.json`:
```bash
python src/run_experiments.py --experiment all
```

---

## 10. Running Automated Unit Tests

To run the full unit test suite (18 tests covering parser, features, region expansion, anonymizer, heuristic, GNN candidate evaluation, and A/B evaluation):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 11. Switching LLM Providers (Gemini vs. Ollama)

In `src/llm.py`:
- To use **Google Gemini API**:
  ```python
  ACTIVE_PROVIDER = "gemini"
  GEMINI_MODEL = "gemini-3.5-flash-lite"
  ```
- To use **Local Ollama Qwen3** (100% offline, zero rate limits):
  ```python
  ACTIVE_PROVIDER = "ollama"
  OLLAMA_MODEL = "qwen3:4b"
  ```
*(Note: If Gemini encounters daily quota exhaustion, the system automatically falls back to local Ollama).*
