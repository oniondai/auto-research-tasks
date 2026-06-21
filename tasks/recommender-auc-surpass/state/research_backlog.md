# Research Direction Backlog

> **Protocol:** auto_research §3 enforced direction diversity — a new direction must differ from every tried direction in ≥ 1 structural axis. Filling out `state/directions_tried.json` is the authoritative record; this file is the human-readable plan for the worker.

## Structural Axes (the diversity space)

- **interaction-mechanism:** explicit cross (DCN-style) / implicit attention / frequency-domain / gate/MoE
- **depth-strategy:** discrete layers / continuous-depth (ODE) / adaptive-depth / searched-depth
- **sparsity-pattern:** dense / top-k routed / block-diagonal / low-rank
- **regularization:** cross-entropy / calibration-aware / PAC-Bayes / contrastive
- **input-modality:** tabular-only / tabular+sequence / tabular+text

## Backlog (priority = novelty-risk ratio)

### D1 — Sparse Mixture-of-Experts Cross-Network  *(P0, do first)*
- **Why first:** lowest engineering risk, most direct extension of DCN-V2, fastest iteration
- **Structural axes hit:** sparsity-pattern + interaction-mechanism
- **Minimum viable experiment:** swap DCN-V2 cross layers for Switch-style MoE; test on Avazu (smaller, faster); 3 seeds; 5 epochs
- **Diversity check:** differs from DeepFM (no MoE) and DCN-V2 (no MoE) on sparsity axis ✓

### D2 — Frequency-Domain Feature Interaction (FFT-DCN)  *(P1)*
- **Why second:** higher theoretical novelty, harder to make work, but high-reward if it does
- **Structural axes hit:** interaction-mechanism (frequency vs spatial)
- **Minimum viable experiment:** replace cross-network with FFT-mixing layers; test on Criteo Kaggle (more features, more interactions to mix)
- **Diversity check:** differs from D1 on interaction-mechanism axis ✓

### D3 — Neural-ODE Interest Evolution  *(P1)*
- **Why third:** high-risk high-reward; continuous-depth is a different structural axis entirely
- **Structural axes hit:** depth-strategy (continuous-depth)
- **Minimum viable experiment:** wrap cross-network output in Neural-ODE block; test on MovieLens-25M (sequential data validates the "interest evolution" framing)
- **Diversity check:** differs from D1 (sparsity) and D2 (frequency) on depth axis ✓

### D4 — Differentiable Architecture Search  *(P2, run if D1-D3 all stall)*
- **Why last:** search cost is enormous; only worth it if D1-D3 collectively saturate
- **Structural axes hit:** interaction-mechanism (searched)
- **Diversity check:** differs from all on the "searched" axis

### D5 — PAC-Bayes Calibrated Cross-Network  *(P2, optional cross-cutting)*
- **Why cross-cutting:** this is a regularization axis, not a new architecture; can be layered onto D1/D2/D3
- **Structural axes hit:** regularization
- **Diversity check:** orthogonal; do not count as one of the 3 required structural directions

## Decision Gates (auto_research §6 stall detection)

| Condition | Action |
|-----------|--------|
| D1 iter returns 0 new findings (no AUC delta vs DCN-V2 baseline) | stale_count += 1; do not abort yet |
| D1 + D2 both 0 new findings | stale_count >= 2 → forced pivot: try D3 with same iteration budget |
| D1 + D2 + D3 all 0 new findings | stale_count >= 4 → flag for human attention in `progress.json.blocking_issues` |
| D5 PAC-Bayes regularization improves calibration ECE on ANY architecture | record as secondary finding, do not count as a structural direction |

## Anti-temptation Notes (per auto_research §7 anti-temptation rules)

- Do NOT run D1 with 5 random seeds "to be sure" before trying D2 — diversity > depth
- Do NOT abandon D2 after 1 iter if early loss is high — frequency-domain models often have slower early training
- Do NOT mark a direction "tried" unless at least 1 full training run completed on at least 1 dataset with metrics written
