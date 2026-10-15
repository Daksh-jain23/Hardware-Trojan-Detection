You're right. Here are the corrected complete commands with all 3 evaluation modes:

---

## METHOD 1 — Cross-Family Split

### Train
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/train_gnn.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --train-families s13207 s1423 c2670 c3540 \
  --val-families s15850 c5315 \
  --test-families s35932 c6288 \
  --epochs 150 \
  --checkpoint checkpoints/trojan_gnn_cross_family.pt
```

### Eval 1 — Heuristic only
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_cross_family.pt \
  --output-dir results/cross_family/ab_heuristic \
  --skip-llm
```

### Eval 2 — LLM without Critic
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_cross_family.pt \
  --output-dir results/cross_family/ab_llm_no_critic
```

### Eval 3 — LLM with Critic
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_cross_family.pt \
  --output-dir results/cross_family/ab_llm_critic \
  --enable-critic
```

---

## METHOD 2 — Random File-Level Split

### Train
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/train_gnn.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --split-by file \
  --split-ratio 0.70 0.15 0.15 \
  --epochs 150 \
  --checkpoint checkpoints/trojan_gnn_random_split.pt
```

### Eval 1 — Heuristic only
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_random_split.pt \
  --output-dir results/random_split/ab_heuristic \
  --skip-llm
```

### Eval 2 — LLM without Critic
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_random_split.pt \
  --output-dir results/random_split/ab_llm_no_critic
```

### Eval 3 — LLM with Critic
```bash
/home/daksh-jain/Code/Minor-Project/.venv/bin/python3 src/ab_evaluation.py \
  --data-dir data/TRIT-TS data/TRIT-TC \
  --checkpoint checkpoints/trojan_gnn_random_split.pt \
  --output-dir results/random_split/ab_llm_critic \
  --enable-critic
```

---

## Final folder structure

```
checkpoints/
├── trojan_gnn_cross_family.pt
└── trojan_gnn_random_split.pt

results/
├── cross_family/
│   ├── ab_heuristic/ab_metrics_summary.json      ← heuristic only
│   ├── ab_llm_no_critic/ab_metrics_summary.json  ← LLM, no critic
│   └── ab_llm_critic/ab_metrics_summary.json     ← LLM + critic
└── random_split/
    ├── ab_heuristic/ab_metrics_summary.json
    ├── ab_llm_no_critic/ab_metrics_summary.json
    └── ab_llm_critic/ab_metrics_summary.json
```

> **Time warning**: With Ollama, `ab_llm_no_critic` and `ab_llm_critic` will take many hours. Run heuristic evals first to verify everything works, then kick off the LLM evals overnight.