# Hardware Trojan Detection System: Comprehensive File-by-File Guide

This document explains the exact purpose, inputs, outputs, key functions/classes, and design constraints for every file in the project.

---

## 1. Core Source Code (`src/`)

### `src/parser.py`
- **Purpose**: Parses gate-level structural Verilog netlists (`.v`) into directed NetworkX graphs ($G = (V, E)$).
- **Inputs**: Gate-level Verilog files (e.g. from `data/TRIT-TS/`).
- **Outputs**: `nx.DiGraph` where nodes are gates/inputs/outputs and edges are interconnect nets.
- **Key Functions**:
  - `parse_netlist(file_path)`: Scans modules, wire definitions, gate instantiations, and pin assignments.
  - `is_trojan_gate(gate_name)`: Ground-truth labeling helper checking benchmark naming conventions (`troj*`, `counter_reg*`, `trojan_out*`).
- **Design Rule**: Strips Trojan naming annotations before topological evidence generation.

---

### `src/features.py`
- **Purpose**: Computes a normalized 41-dimensional structural and topological feature vector for every gate in the circuit graph.
- **Inputs**: `nx.DiGraph` from `parser.py`.
- **Outputs**: NumPy feature matrix $X \in \mathbb{R}^{|V| \times 41}$ and aligned node identifier list.
- **Key Functions**:
  - `compute_node_features(graph)`: Calculates:
    - *Dims 0–14*: Gate Type One-Hot (PI, PO, AND, NAND, OR, NOR, XOR, XNOR, DFF, Latch, etc.).
    - *Dims 15–20*: Local Degree & Connectivity (fan-in, fan-out, degree ratio, sequential input/output).
    - *Dims 21–24*: Topological Depth (shortest/longest distances from inputs and to outputs).
    - *Dims 25–30*: Centrality Proxies (clustering coefficient, 1-hop & 2-hop neighborhood size, PageRank, betweenness).
    - *Dims 31–36*: Sequential Dynamics (distance to nearest DFF, cycle/feedback loops, 2-hop DFF counts).
    - *Dims 37–40*: Controllability/Observability Proxies (CC0, CC1, CO, transition stealthiness).
- **Design Rule**: Strictly deterministic; identical graphs always produce identical feature representations.

---

### `src/dataset.py`
- **Purpose**: Converts NetworkX circuit graphs into PyTorch Geometric (`Data`) objects suitable for Graph Neural Network training.
- **Inputs**: Netlists from `data/TRIT-TS/`.
- **Outputs**: PyTorch Geometric `Data` objects containing `x` (features), `edge_index` (connectivity), and `y` (binary Trojan label).
- **Key Functions**:
  - `graph_to_pyg(graph)`: Maps NetworkX nodes to tensor indices and formats tensors.
  - `build_node_level_dataset()`: Discovers and parses all netlists across all benchmark families.
  - `find_netlists()`, `get_family(path)`: Discovers netlists and extracts family names (`s13207`, `s1423`, `s15850`, `s35932`).
- **Design Rule**: Retains each circuit as a separate graph object to prevent intra-circuit message-passing leakage.

---

### `src/gnn.py`
- **Purpose**: Defines the Graph Attention Network (GAT) architecture used as the primary detector and localizer.
- **Inputs**: Node features $X$ and edge tensor `edge_index`.
- **Outputs**: Per-node binary logits and Trojan probabilities $\hat{y}_v \in [0, 1]$.
- **Key Classes**:
  - `TrojanGNN(nn.Module)`:
    - Layer 1: `GATConv(41, 64, heads=4)` with ELU activation and dropout ($p = 0.2$).
    - Layer 2: `GATConv(256, 64, heads=1)` with linear output projection.
- **Design Rule**: Primary detector. Outputs raw probabilities without relying on heuristic scores or LLM reasoning.

---

### `src/train_gnn.py`
- **Purpose**: Trains the GAT detector using BCEWithLogitsLoss with positive class-imbalance weighting.
- **Inputs**: Benchmark netlists (`data/TRIT-TS/`).
- **Outputs**: Trained model weights saved to `checkpoints/trojan_gnn.pt`.
- **Supported Split Strategies**:
  - `--split-strategy family` (Default): Trains on `s13207` & `s1423`, validates on `s15850`, and tests on `s35932`.
  - `--split-strategy stratified`: Pools all 338 netlists and splits them (70% train, 15% val, 15% test) proportionally across families.
  - `--split-strategy random`: Pools all 338 netlists and performs random split.
- **Key Functions**:
  - `train_one_epoch()`: Executes forward/backward passes.
  - `find_best_threshold()`: Tunes decision threshold $\tau$ strictly on validation set.
  - `evaluate()`: Calculates Precision, Recall, and F1 on test data.

---

### `src/evaluation.py`
- **Purpose**: Standalone evaluation script to assess a trained GNN checkpoint on test netlists.
- **Inputs**: `checkpoints/trojan_gnn.pt` and test family netlists.
- **Outputs**: Node-level and circuit-level evaluation metrics printed and saved to `results/gnn/`.
- **Key Functions**:
  - `evaluate_family(model, family, threshold)`: Computes ROC-AUC, Average Precision, F1, Confusion Matrix.

---

### `src/region.py`
- **Purpose**: Localizes suspicious regions by expanding around GNN-predicted positive seeds.
- **Inputs**: Circuit graph and GNN probability scores.
- **Outputs**: Set of localized region node names.
- **Key Functions**:
  - `select_suspicious_seeds(graph, probs, threshold)`: Flags gates with $p(v) \ge \tau$ (e.g. 0.95).
  - `expand_suspicious_region(graph, seeds, hops=2, max_size=50)`: Performs bidirectional breadth-first search up to $k$ hops, bounded by a strict size cap to prevent runaway neighborhood flooding.

---

### `src/evidence.py`
- **Purpose**: Extracts structured topological and contextual metrics from the localized region.
- **Inputs**: Graph, GNN scores, seeds, and localized region.
- **Outputs**: `results/evidence/<circuit>_evidence.json`.
- **Metrics Extracted**:
  - Circuit-wide facts: total nodes, edges, seed score distribution (min, max, mean, count $\ge 0.95$, count $\ge 0.99$).
  - Boundary facts: `internal_edges`, `boundary_edges`, `region_exits`.
  - Sequential facts: count and gate types of DFFs/latches.
  - `local_structural_patterns`: high-score internal edge density, direct connections from seeds to sequential elements, fan-in/fan-out profiles.

---

### `src/anonymizer.py`
- **Purpose**: Strips all benchmark metadata and original gate identifiers to prevent data/benchmark leakage into the LLM.
- **Inputs**: Raw evidence dictionary from `evidence.py`.
- **Outputs**: Anonymized dictionary (`results/anonymized/<circuit>_evidence_anonymized.json`) and mapping dictionary.
- **Key Functions**:
  - `anonymize_evidence(data)`: Replaces benchmark name with neutral label (`CIRCUIT_EVAL`) and maps gates to `NODE_0001`, `NODE_0002`, etc.
  - `assert_no_leakage(text_or_json, original_mapping)`: Automated security check raising `ValueError` if `troj*`, `counter_reg*`, `trojan_out*`, or original unmapped IDs appear.

---

### `src/llm_prompt.py`
- **Purpose**: Formulates the rigorous, neutral prompt provided to downstream reasoning models.
- **Inputs**: Anonymized evidence dictionary.
- **Outputs**: Text prompt file (`results/llm/<circuit>_prompt.txt`).
- **Core Sections Built**:
  1. *Critical Numerical Rule*: Forbids LLM from recalculating counts or inventing numbers.
  2. *Authoritative Numerical Facts*: JSON block of ground-truth pipeline statistics.
  3. *Expanded Region Summary & Structural Evidence*: Boundary edges, exits, sequential elements.
  4. *Local Structural Patterns*: High-score internal density and sequential connections.
  5. *Strict Reasoning Procedure & Output Format*: Enforces explicit sections (`DECISION`, `CONFIDENCE`, `OBSERVED_EVIDENCE`, `STRUCTURAL_INTERPRETATION`, `COUNTER_EVIDENCE`, `REASONING`).

---

### `src/llm.py`
- **Purpose**: Executes downstream LLM reasoning and parses structured verdicts.
- **Inputs**: Generated prompt text file.
- **Outputs**: Structured JSON response (`results/llm/<circuit>_<provider>_llm.json`).
- **Supported Providers**:
  - `ACTIVE_PROVIDER = "gemini"`: Uses Google Gemini API (`gemini-3.5-flash-lite`) with retry/backoff.
  - `ACTIVE_PROVIDER = "ollama"`: Uses local Ollama (`qwen3:4b`) with `num_ctx: 8192` and `num_predict: 1024`.
  - Automatic fallback: If Gemini hits quota exhaustion, it automatically switches to local Ollama.
- **Key Functions**:
  - `run_llm(prompt)`: Dispatches prompt to active provider.
  - `extract_decision(text)`, `extract_confidence(text)`: Regex extraction of `SUSPICIOUS|NORMAL|UNCERTAIN` and `HIGH|MEDIUM|LOW`.

---

### `src/heuristic.py`
- **Purpose**: Independent deterministic baseline detector that identifies structural anomalies without machine learning or LLMs.
- **Inputs**: Netlist file path.
- **Outputs**: `results/heuristic/<circuit>_heuristic.json`.
- **Heuristic Criteria**:
  - Fan-in / Fan-out anomaly scoring.
  - Sequential cluster isolation (isolated counter registers).
  - Boundary stealthiness (internal loop density vs. external exits).
- **Isolation Rule**: Heuristic scores and verdicts are strictly isolated and never provided to the LLM.

---

### `src/pipeline.py`
- **Purpose**: Complete end-to-end integration orchestrator.
- **Inputs**: Path to Verilog netlist (`.v`).
- **Outputs**: Coordinates parsing $\to$ feature computation $\to$ GNN inference $\to$ seed selection $\to$ region expansion $\to$ evidence extraction $\to$ anonymization $\to$ prompt building $\to$ LLM reasoning.
- **Key Functions**:
  - `run_pipeline(netlist_path, checkpoint_path, skip_llm)`: Returns complete execution summary dictionary.

---

### `src/ab_evaluation.py`
- **Purpose**: Controlled scientific framework evaluating LLM structural reasoning, swap consistency, and position bias on individual netlists.
- **Inputs**: Netlist file path containing ground-truth Trojan.
- **Outputs**: `results/ab_evaluation/<circuit>_ab_result.json`.
- **Evaluation Mechanism**:
  - Extracts ground-truth Trojan region and a matched clean region of identical size.
  - **Trial 1**: Region A = Trojan, Region B = Clean.
  - **Trial 2 (Swapped)**: Region A = Clean, Region B = Trojan.
  - Evaluates whether the LLM reliably selects the Trojan region regardless of presentation order.

---

### `src/eval_gnn_llm_quantitative.py`
- **Purpose**: Multi-circuit quantitative evaluation framework for GNN $\to$ LLM reasoning.
- **Inputs**: Trojan benchmark cohort (`TRIT-TS`, `TRIT-TC`) and matched clean designs (`original_designs`, `TjFree`).
- **Outputs**: `results/gnn_llm_quantitative_metrics.json`.
- **Evaluations Executed**:
  1. *Multi-Circuit Controlled A/B Benchmark*: Measures selection accuracy (83.33%), swap-consistency rate (66.67%), position bias rate, and binomial statistical significance.
  2. *End-to-End Binary Classification Benchmark*: Measures circuit-level Accuracy (66.67%), Precision (66.67% vs Pure GNN 50.00%), Recall, F1, and False Alarm Suppression Rate (66.7%).
  3. *Confidence Calibration*: Brier calibration score (0.1825).

---

### `src/run_experiments.py`
- **Purpose**: Unified experiment runner executing Experiments A, B, C, D, E, or all consolidated.
- **Inputs**: CLI argument `--experiment {A, B, C, D, E, all}`.
- **Outputs**: Consolidates results into `results/final_metrics.json`.
  - Experiment A: Standalone GNN evaluation on unseen family `s35932`.
  - Experiment B: Independent heuristic baseline evaluation on `s35932`.
  - Experiment C: Full GNN + Evidence + LLM explanation pipeline.
  - Experiment D: Controlled A/B swap-consistency evaluation on reference circuit.
  - Experiment E: Multi-circuit quantitative evaluation of GNN $\to$ LLM.

---

## 2. Test Suite (`tests/`)

- **`tests/test_parser.py`**: Verifies Verilog netlist parsing, gate connectivity, and ground-truth Trojan labeling.
- **`tests/test_features.py`**: Verifies that `compute_node_features` produces exact 41-dimensional vectors with expected value bounds.
- **`tests/test_region.py`**: Validates seed selection, $k$-hop expansion, and enforcement of the `max_size` cap.
- **`tests/test_anonymizer.py`**: Tests complete replacement of identifiers and verifies that `assert_no_leakage` catches unmapped IDs or Trojan naming tokens.
- **`tests/test_heuristic.py`**: Validates deterministic output, schema structure, and anomaly scoring of the heuristic baseline.
- **`tests/test_ab_evaluation.py`**: Tests Trojan and clean region extraction, A/B prompt formatting, zero-leakage assertions, LLM response parsing, and swap-consistency / position-bias logic.

---

## 3. Configuration & Artifact Files

- **`architecture.md`**: Complete system architecture specification, mathematical feature descriptions, and design principles.
- **`HOW_TO_RUN.md`**: Markdown run guide covering training, evaluation, comparison, and provider switching.
- **`HOW_TO_RUN.txt`**: Plain-text terminal execution and reproduction manual.
- **`FILES_EXPLAINED.md`**: This document (file-by-file reference).
- **`.vscode/settings.json`**: Configures Python analysis search paths (`src`) for VS Code, Pylance, and Pyrefly.
- **`.env`**: Local environment configuration storing `GEMINI_API_KEY`.
- **`requirements.txt`**: Required Python packages (torch, torch-geometric, networkx, scikit-learn, google-genai, ollama).
- **`checkpoints/trojan_gnn.pt`**: Saved PyTorch model checkpoint (model state dictionary, input dimension, hidden dimension, validation F1, and optimal threshold).
- **`results/final_metrics.json`**: Consolidated performance metrics across all experiments.
