# Hardware Trojan Detection, Localization, and Explanation System: Architecture

## 1. System Overview & Core Philosophy

This system is an end-to-end research-grade framework designed to detect, localize, and explain Hardware Trojans in gate-level Verilog netlists. The architecture adheres to strict scientific separation of concerns:

```
                                 ┌────────────────────────┐
                                 │  Gate-Level Verilog    │
                                 │        Netlist         │
                                 └───────────┬────────────┘
                                             │
                                [Netlist Parser (src/parser.py)]
                                             │
                                             ▼
                               Directed Graph G = (V, E)
                                             │
                             [41 Node Features (src/features.py)]
                                             │
                                             ▼
                        41-Dimensional Node Feature Matrix X ∈ ℝ^{|V| × 41}
                                             │
              ┌──────────────────────────────┴──────────────────────────────┐
              │                                                             │
              ▼                                                             ▼
       ┌──────────────────────────────┐                      ┌──────────────────────────────┐
       │   PRIMARY DETECTOR: GNN      │                      │  INDEPENDENT BASELINE:       │
       │   (src/gnn.py, train_gnn.py) │                      │  Deterministic Heuristic     │
       │   2-layer Graph Attention    │                      │  (src/heuristic.py)          │
       └──────────────┬───────────────┘                      └──────────────┬───────────────┘
                      │                                                     │
                      ▼                                                     ▼
              Node Trojan Scores                                    Standalone Anomaly Score
                      │                                             & Baseline Verdict
       ┌──────────────┴──────────────┐
       │                             │
       ▼                             ▼
[ PARADIGM 1: PURE GNN ]    GNN Suspicious Seeds
Raw GNN probabilities       (p(v) ≥ Threshold)
& Direct Thresholding                │
                                     ▼
                           [ Region Localization ]
                           (src/region.py, 2 hops)
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
         ▼                                                       ▼
[ PARADIGM 2: GNN -> HEURISTIC ]                [ Structured Evidence Extraction ]
(src/heuristic.py)                              (src/evidence.py)
Structural Verification Filter:                                  │
- Seed internal clustering density                               ▼
- Trigger-to-sequential loop links              [ Zero-Leakage Anonymization ]
- Boundary exit stealthiness                    (src/anonymizer.py)
- Prunes false-alarm seeds                                       │
         │                                                       ▼
         ▼                                      [ Prompt Formulation ]
Filtered Candidates & Verification              (src/llm_prompt.py)
Verdict (CONFIRMED / PRUNED)                                     │
                                                                 ▼
                                                [ PARADIGM 3: GNN -> LLM ]
                                                (src/llm.py)
                                                - Authoritative numerical facts
                                                - Topological interpretation
                                                - Natural language explanation
         │                                                       │
         └───────────────────────────┬───────────────────────────┘
                                     │
                                     ▼
                   [ 3-WAY COMPARATIVE EVALUATION ]
             Pure GNN  vs.  GNN -> Heuristic  vs.  GNN -> LLM
```

---

## 2. Component Specifications

### 2.1 Netlist Parsing (`src/parser.py`)
- Parses structural gate-level Verilog netlists into a directed NetworkX graph $G = (V, E)$.
- Vertices $V$ represent logic gates, primary inputs (PI), and primary outputs (PO).
- Directed edges $E$ represent interconnect nets flowing from driver gates to driven inputs.
- Ground-truth labels are derived exclusively from benchmark structural annotations (`troj*`, `counter_reg*`, `trojan_out*`), stripped from downstream pipeline reasoning.

### 2.2 41-Dimensional Node Feature Representation (`src/features.py`)
Each node $v \in V$ is mapped to a normalized 41-dimensional feature vector:
1. **Gate Category One-Hot (Dimensions 0–14)**:
   - Primary Input, Primary Output, Inverter/Buffer, AND, NAND, OR, NOR, XOR, XNOR, MUX, D-Flip-Flop (DFF), Latch, Complex/AOI/OAI, Constant (VDD/GND), Unknown.
2. **Local Structural Connectivity (Dimensions 15–20)**:
   - In-degree (fan-in), Out-degree (fan-out), Total degree, Ratio of fan-in to fan-out, Sequential input count, Sequential output count.
3. **Topological Depth & Position (Dimensions 21–24)**:
   - Normalized topological depth from primary inputs (longest and shortest paths).
   - Normalized distance to primary outputs (longest and shortest paths).
4. **Structural Centrality Proxies (Dimensions 25–30)**:
   - Local clustering coefficient.
   - 1-hop and 2-hop neighborhood sizes.
   - Pagerank score on the directed graph.
   - Betweenness centrality proxy (subgraph-bounded).
   - Eigenvector centrality proxy.
5. **Sequential Proximity & Loop Characteristics (Dimensions 31–36)**:
   - Distance to nearest DFF input and output.
   - Participation in feedback loops / cycles.
   - Number of flip-flops reachable within 2 hops.
   - Sequential cluster density.
6. **Controllability & Observability Proxies (Dimensions 37–40)**:
   - Combinational Controllability 0 (CC0) proxy.
   - Combinational Controllability 1 (CC1) proxy.
   - Combinational Observability (CO) proxy.
   - Transition stealthiness proxy (fanout / loop isolation).

### 2.3 Primary Detector: Graph Attention Network (`src/gnn.py`, `src/train_gnn.py`)
- **Model Architecture**: 2-layer Graph Attention Network (GAT) with multi-head attention.
  - Layer 1: `GATConv(41, 64, heads=4)` with ELU activation and dropout ($p=0.2$).
  - Layer 2: `GATConv(256, 64, heads=1)` with linear projection to binary Trojan logits.
- **Circuit-Family Split Strategy**: To prevent intra-circuit node leakage, data is partitioned strictly by circuit families:
  - **Training Set**: `s13207`, `s1423`
  - **Validation Set**: `s15850` (Used for optimal decision threshold tuning)
  - **Test Set**: `s35932` (Completely unseen circuit family)
- **Primary Detector Guarantee**: The GNN produces probabilities $p(v) \in [0, 1]$ for every gate. Gates with $p(v) \ge \tau$ (e.g., $\tau = 0.95$) are flagged as suspicious seeds.

### 2.4 Suspicious Region Localization (`src/region.py`)
- Uses GNN seeds as centers to extract a structurally bounded suspicious neighborhood.
- Expands outwards via breadth-first search along forward (successors) and backward (predecessors) interconnects up to $k$ hops (default: 2 hops).
- Implements strict maximum size capping (default: 50 nodes) to prevent entire circuit flooding.

### 2.5 Structured Evidence Extraction (`src/evidence.py`)
Extracts verifiable topological metrics:
- **Global Context**: Total circuit gate count, total nets, GNN score distribution (min, max, mean, seeds $\ge 0.95$, seeds $\ge 0.99$).
- **Regional Connectivity**:
  - `internal_edges`: Edges where both source and destination belong to the region.
  - `boundary_edges`: Nets crossing the region boundary.
  - `region_exits`: Specific internal gates that drive external logic outside the region.
- **Sequential Relations**: Count and gate types of internal sequential storage elements (DFFs, latches).
- **Local Structural Patterns**:
  - High-score internal edge count (connectivity among GNN-positive seeds).
  - High-score to sequential gate connections (trigger-to-payload or trigger-counter relations).
  - Region fan-in and fan-out profiles.

### 2.6 Anonymization Engine & Zero-Leakage Boundary (`src/anonymizer.py`)
- Replaces all netlist names (`s13207`, `troj21_*`, `counter_reg_*`, `U1234`) with neutral identifiers (`NODE_0001`, `NODE_0002`).
- Replaces benchmark labels with neutral circuit IDs.
- Validated by automated assertion: `assert_no_leakage(text_or_json)` which raises an immediate exception if any forbidden substring (`troj`, `counter_reg`, `trojan_out`, or unmapped original gate names) is detected.

### 2.7 Downstream LLM Reasoning (`src/llm.py`, `src/llm_prompt.py`)
- **Strict Role Separation**:
  - The LLM does **not** detect raw features.
  - The LLM does **not** recalculate numbers.
  - The LLM receives **Authoritative Numerical Facts** as immutable ground truth.
  - The LLM interprets the structural cohesiveness, state-dependent sequential coupling, and boundary stealthiness to output structured decisions (`SUSPICIOUS`, `NORMAL`, `UNCERTAIN`) and confidence (`HIGH`, `MEDIUM`, `LOW`).
- **Supported Providers**:
  - Cloud: Google Gemini API (`gemini-3.5-flash-lite`) with exponential backoff.
  - Local/Offline: Ollama (`qwen3:4b`) with automatic fallback.

### 2.8 Independent Structural Heuristic Baseline (`src/heuristic.py`)
- Deterministic structural baseline independent of machine learning or LLMs.
- Analyzes three structural anomaly criteria:
  1. Low fan-in / high fan-out trigger gates.
  2. Isolated sequential clusters (e.g. counters or activation registers).
  3. Stealthy boundary connectivity (high internal density with minimal region exits).
- **Strict Isolation**: Heuristic scores, decisions, and anomalous node lists are **never** passed to the LLM or GNN.

### 2.9 Controlled A/B Swap-Consistency Evaluation (`src/ab_evaluation.py`)
- Scientifically tests whether the LLM's structural reasoning evaluates genuine topological patterns rather than presentation order or hallucination.
- Extracts a ground-truth Trojan region and a matched clean region of identical size and depth.
- **Trial 1**: Region A = Trojan, Region B = Clean.
- **Trial 2**: Region A = Clean, Region B = Trojan (Swapped).
- Computes:
  - **Swap Consistency**: True if the LLM correctly tracks the Trojan across the swap.
  - **Position Bias**: Detected if the LLM defaults to "Region A" regardless of contents.
  - **Leakage Check**: Verified by `assert_no_leakage(prompt)`.

### 2.10 Multi-Circuit Quantitative Evaluation (`src/eval_gnn_llm_quantitative.py`)
- Evaluates the GNN $\to$ LLM pipeline quantitatively across cohorts of Trojan-infected (`TRIT-TS`, `TRIT-TC`) and matched clean designs (`original_designs`, `TjFree`):
  1. **Multi-Circuit A/B Accuracy & Swap Consistency**: Quantifies selection accuracy (**100.00%**) and swap-consistency rate (**100.00%**) across circuit pairs with **0.0% position bias**.
  2. **Circuit-Level Binary Classification**: Evaluates Precision (**100.00%** vs. Pure GNN 50.00%), Recall (66.67%), F1-Score (**80.00%**), and False Alarm Suppression Rate (**100.0%** of clean-circuit false alarms pruned).
  3. **Node-Level Classification (12,070 gates)**: Precision jumps from **36.99% $\to$ 79.41%** (+42.42% boost) and F1-Score from **49.09% $\to$ 76.06%** (+26.97% boost).

### 2.11 Addressing the Base Rate Fallacy & Scan-Chain Discrimination
- **The Base Rate Dilemma**: In real digital netlists, Trojan gates account for only $\sim 0.3\%$ of all logic. Even an exceptionally accurate GNN with a 99.4% True Negative Rate produces dozens of raw false-positive gates on clean circuits ($0.6\% \times 6,435 \approx 46$ false positives), dragging raw node precision down to $36.99\%$.
- **Scan-Chain Ambiguity**: Test-mode scan chains feature long sequential flip-flop paths that locally mimic Trojan counter registers when viewed through a 2-hop GNN receptive field.
- **Topological Ratio Solutions**:
  1. `internal_seed_edge_density`: Ratio of direct edges between candidate seeds to total seeds. Real Trojans have dense clustering ($\ge 0.70$); scan chains are sparse linear lines ($< 0.50$).
  2. `region_exit_ratio`: Ratio of outgoing boundary exits to total region nodes. Real Trojans are stealthy ($\le 0.35$); scan chains broadcast across the entire circuit datapath ($> 0.35$).
- **Impact**: Incorporating these topological ratios and strict discrimination rules into downstream verification eliminated 100% of clean-circuit false alarms and boosted node-level precision to **79.41%**.

---

## 3. Directory Structure

```
.
├── checkpoints/
│   └── trojan_gnn.pt              # Trained GNN weights
├── data/
│   └── TRIT-TS/                   # Trust-HUB Hardware Trojan Benchmarks
│       ├── s13207_T421/
│       ├── s1423_T100/
│       ├── s15850_T100/
│       └── s35932_T100/
├── docs/
│   └── architecture.md            # System Architecture Specification
├── results/
│   ├── gnn/                       # GNN evaluation metrics
│   ├── heuristic/                 # Heuristic baseline metrics
│   ├── evidence/                  # Extracted JSON structural evidence
│   ├── anonymized/                # Anonymized JSON evidence
│   ├── llm/                       # Generated prompts and LLM outputs
│   ├── ab_evaluation/             # Controlled A/B experiment outputs
│   ├── gnn_llm_quantitative_metrics.json # Multi-circuit quantitative metrics
│   └── final_metrics.json         # Consolidated evaluation report
├── src/
│   ├── parser.py                  # Gate-level Verilog to graph parser
│   ├── features.py                # 41-dimensional feature extractor
│   ├── dataset.py                 # PyTorch Geometric dataset converter
│   ├── gnn.py                     # 2-layer Graph Attention Network
│   ├── train_gnn.py               # GNN training pipeline
│   ├── region.py                  # Suspicious region localization
│   ├── evidence.py                # Structural evidence extraction
│   ├── anonymizer.py              # Zero-leakage anonymization engine
│   ├── llm_prompt.py              # Strict reasoning prompt builder
│   ├── llm.py                     # Gemini / Ollama LLM interface
│   ├── heuristic.py               # Independent deterministic baseline
│   ├── pipeline.py                # End-to-end detection & explanation
│   ├── ab_evaluation.py           # Controlled A/B swap evaluation
│   ├── eval_gnn_llm_quantitative.py # Multi-circuit quantitative benchmark
│   └── run_experiments.py         # Consolidated experiment suite
└── tests/
    ├── test_parser.py             # Parser unit tests
    ├── test_features.py           # 41-feature dimension tests
    ├── test_region.py             # Region expansion & capping tests
    ├── test_anonymizer.py         # Leakage prevention tests
    ├── test_heuristic.py          # Heuristic determinism tests
    └── test_ab_evaluation.py      # Controlled A/B & swap consistency tests
```
