# Comprehensive CLI & Flag Reference Manual

This document provides a complete guide for running every file and component in the Hardware Trojan Detection Framework, with detailed descriptions of all command-line arguments and configuration parameters.

---

## 1. GNN Training (`src/train_gnn.py`)

Trains the Graph Attention Network (GAT) to classify individual gates as Trojan or Normal based on 41 topological features.

### Command Syntax
```bash
python src/train_gnn.py [OPTIONS]
```

### Full Arguments & Flags
| Argument | Type | Default | Description |
|---|---|---|---|
| `--files` | `str [str ...]` | `None` | Explicit list of netlist files (`.v`) to build the dataset from. |
| `--data-dir` | `path [path ...]`| `None` | Root directory or directories to search for `.v` netlists (e.g., `data/TRIT-TS`). |
| `--train-families` | `str [str ...]` | `s13207 s1423` | Benchmark families assigned to the training split when using `--split-by family`. |
| `--val-families` | `str [str ...]` | `s15850` | Benchmark families assigned to the validation split for threshold tuning. |
| `--test-families` | `str [str ...]` | `s35932` | Benchmark families assigned to the test split (unseen evaluation). |
| `--split-by` | `{family, file}` | `family` | Splitting strategy: `family` prevents cross-circuit leakage; `file` splits by file count. |
| `--split-ratio` | `float float float` | `0.70 0.15 0.15` | Proportions for Train / Validation / Test when using `--split-by file`. |
| `--epochs` | `int` | `100` | Number of training epochs over the graph dataset. |
| `--lr` | `float` | `0.001` | Learning rate for the Adam optimizer. |
| `--hidden-dim` | `int` | `64` | Dimensionality of hidden GAT layers. |
| `--checkpoint` | `path` | `checkpoints/trojan_gnn.pt` | Output file path to save trained model weights. |
| `--max-samples` | `int` | `None` | Limit total number of netlists loaded (useful for rapid debugging). |

### Example Usages
```bash
# 1. Standard Benchmark Family Split (Recommended)
python src/train_gnn.py \
  --data-dir data/TRIT-TS \
  --train-families s13207 \
  --val-families s1423 \
  --test-families s35932 \
  --epochs 35

# 2. Train on Specific Files Across Multiple Datasets
python src/train_gnn.py \
  --files \
    data/TRIT-TS/s13207_T400/s13207_T400.v \
    data/TRIT-TS/s13207_T401/s13207_T401.v \
    data/TRIT-TS/original_designs/s13207scan.v \
    data/TRIT-TC/s1423_T400/s1423_T400.v \
    data/TRIT-TC/original_designs/s1423scan.v \
    data/TjFree/DDR2_Controller-master/design/ddr2_controller.v \
  --split-by file \
  --split-ratio 0.60 0.20 0.20 \
  --epochs 30
```

---

## 2. Controlled A/B Evaluation Framework (`src/ab_evaluation.py`)

Chains GNN node predictions into candidate extraction, builds matched clean controls, anonymizes both regions, runs counter-balanced trials (Trial 1 & Trial 2 swapped) through the Heuristic Baseline, the Standard LLM, and the Actor-Critic LLM, and prints the 3-way comparative evaluation table.

### Command Syntax
```bash
python src/ab_evaluation.py [OPTIONS]
```

### Full Arguments & Flags
| Argument | Type | Default | Description |
|---|---|---|---|
| `--circuit` | `path` | `None` | Evaluate a single Verilog netlist file. |
| `--files` | `path [path ...]` | `None` | Evaluate an explicit cohort of Verilog netlist files. |
| `--data-dir` | `path` | `None` | Batch evaluate all `.v` files found under a directory. |
| `--checkpoint` | `path` | `checkpoints/trojan_gnn.pt` | Path to the trained GNN model weights. |
| `--gnn-threshold` | `float` | `0.95` | Confidence threshold for selecting suspicious seed gates from the GNN. |
| `--hops` | `int` | `2` | Graph expansion radius (k-hop) around seed gates to extract the candidate region. |
| `--output-dir` | `path` | `results/ab_evaluation` | Directory where per-circuit JSON files, prompts, and `ab_metrics_summary.json` are written. |
| `--max-circuits` | `int` | `None` | Cap on the number of circuits evaluated when using `--data-dir`. |
| `--skip-llm` | `flag` | `False` | Skip all LLM calls; generate prompts and evaluate only the heuristic baseline. |
| `--enable-critic` | `flag` | `False` | Enable the full multi-turn Actor-Critic verification loop with deterministic pre-audit. |

### Example Usages
```bash
# 1. Evaluate a Cohort Across All 3 Models (Heuristic vs LLM Standard vs LLM Critic)
python src/ab_evaluation.py \
  --files \
    data/TRIT-TS/s35932_T428/s35932_T428.v \
    data/TRIT-TS/s35932_T431/s35932_T431.v \
    data/TRIT-TS/s13207_T421/s13207_T421.v \
    data/TRIT-TS/original_designs/s13207scan.v \
    data/TjFree/DDR2_Controller-master/design/SSTL18DDR2INTERFACE_RTL.v \
  --checkpoint checkpoints/trojan_gnn.pt

# 2. Fast Baseline Evaluation (Skips LLM calls)
python src/ab_evaluation.py \
  --data-dir data/TRIT-TS \
  --max-circuits 15 \
  --skip-llm

# 3. Single Circuit Detailed Run
python src/ab_evaluation.py \
  --circuit data/TRIT-TS/s13207_T421/s13207_T421.v \
  --checkpoint checkpoints/trojan_gnn.pt
```

---

## 3. Single-Region Pipeline (`src/pipeline.py`)

Runs the GNN, extracts only the primary suspicious candidate region, verifies it with the heuristic, anonymizes it, and queries the LLM for an in-depth hardware security report (identifying trigger counters, flip-flop state logic, and payload muxes).

### Command Syntax
```bash
python src/pipeline.py [netlist] [OPTIONS]
```

### Full Arguments & Flags
| Argument | Type | Default | Description |
|---|---|---|---|
| `netlist` | `positional path` | `None` | Path to a single netlist file (`.v`). |
| `--files` | `path [path ...]` | `None` | List of netlist files to process sequentially. |
| `--data-dir` | `path` | `None` | Directory of netlists to batch process. |
| `--checkpoint` | `path` | `checkpoints/trojan_gnn.pt` | Path to GNN model checkpoint. |
| `--gnn-threshold` | `float` | `0.95` | Seed confidence threshold. |
| `--heuristic-threshold` | `float` | `0.60` | Anomaly threshold for the heuristic baseline detector. |
| `--llm-provider` | `{ollama, gemini}` | `ACTIVE_PROVIDER` | Override LLM inference backend for this run. |
| `--ab-test` | `flag` | `False` | Trigger A/B trial testing inside the pipeline. |
| `--output-dir` | `path` | `results` | Root results directory for evidence, anonymized, and LLM JSON outputs. |

### Example Usages
```bash
python src/pipeline.py \
  data/TRIT-TS/s13207_T421/s13207_T421.v \
  --checkpoint checkpoints/trojan_gnn.pt
```

---

## 4. Evidence Extraction & Feature Engineering

### `src/evidence.py`
Extracts structural graph features (density, boundary exits, sequential gates, gate distribution):
```bash
python src/evidence.py data/TRIT-TS/s13207_T421/s13207_T421.v
```
- Writes output to: `results/evidence/s13207_T421_evidence.json`

### `src/anonymizer.py`
Performs zero-leakage mathematical sanitization (`troj_0U11` $\to$ `NODE_0001`):
```bash
python src/anonymizer.py results/evidence/s13207_T421_evidence.json
```
- Writes sanitized JSON to: `results/anonymized/s13207_T421_evidence_anonymized.json`
- Writes secret mapping (never sent to LLM) to: `results/anonymized/s13207_T421_evidence_mapping.json`

---

## 5. LLM Provider Configuration (`src/llm.py`)

Configure the LLM engine in [`src/llm.py`](file:///home/daksh-jain/Code/Minor-Project/Hardware%20trojan%20detection/src/llm.py):
```python
# Switch between "ollama" and "gemini"
ACTIVE_PROVIDER = "gemini"

# Models
OLLAMA_MODEL = "qwen3:4b"
GEMINI_MODEL = "gemini-3.8-flash"
```

For Gemini, store your API key in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 6. Testing & Quality Assurance

Run the complete automated unit test suite (17 tests covering parsers, features, leakage assertions, and the Critic loop):
```bash
python -m unittest discover tests
```

