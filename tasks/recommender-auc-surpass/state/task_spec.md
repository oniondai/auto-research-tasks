# Task Specification — Recommender Architecture Surpassing DeepFM / DCN-V2

> **Framework:** Deli_AutoResearch v1.0 (long-horizon autonomous research protocol)
> **Protocol constraints in effect:** zero-interaction, ready-means-execute, callback-report-alive, persist-to-files, guardian-worker-separation.
> **Created:** 2026-06-21 (manual scaffolding; not yet loop-running)

## 1. Goal

Design and validate a **novel click-through-rate (CTR) prediction architecture** that **statistically significantly outperforms** DeepFM (2017) and DCN-V2 (2020) on at least two of three benchmark datasets — Criteo 1TB (or Criteo Kaggle subset), Avazu CTR, and MovieLens-25M — on **AUC** and **LogLoss** as primary metrics, **calibrated LogLoss** (post-calibration ECE ≤ 0.01) as secondary metric, while remaining **parameter-efficient** (≤ 1.2× the parameter count of DCN-V2 at matched embedding dim).

The architecture must be **publishable** at a top venue (RecSys / KDD / IEEE TKDE/TNNLS) — meaning reproducible, with strong baselines, ablations, theoretical motivation, and either empirical novelty (new architecture family) or theoretical novelty (proof of why current cross-networks saturate).

## 2. Hard Constraints (auto_research §9 + venue policy)

- **Engineering:** ≤ 5 large files per iteration, no single file over 300 lines (auto_research §9.1)
- **State-only:** progress persisted to files under `state/`, not conversation (auto_research §2.4)
- **Validate between iterations:** every iteration runs test/compile/check before writing findings (auto_research §9.3)
- **Citation cadence:** verify citations every 20 entries, never batch (auto_research §9.4)
- **Diversity over depth:** ≥ 3 structurally distinct directions tried before drilling (auto_research §9.5)
- **Reproducibility:** random seeds, configs checked in, datasets pinned to MD5
- **No external data leakage:** test set only at final reporting, never during iteration selection
- **Ethics:** no scraping of user data; benchmark datasets only; if human-subjects study needed, IRB approval logged before run

## 3. Success Criteria (venue-tuned)

### Primary (must satisfy ALL to declare "publishable draft")

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| AUC gain over DCN-V2 on Criteo Kaggle | ≥ +0.001 absolute, p < 0.01 (paired bootstrap, 1000 resamples) | reported in `runs/<iter>/criteo_kaggle_eval.json` |
| AUC gain over DeepFM on Avazu | ≥ +0.0008 absolute, p < 0.01 | `runs/<iter>/avazu_eval.json` |
| LogLoss improvement over best baseline | ≥ 1.0% relative reduction | same eval files |
| Calibrated LogLoss ECE | ≤ 0.01 post-temperature-scaling | `runs/<iter>/calibration.json` |
| Parameter overhead vs DCN-V2 | ≤ 1.2× | `runs/<iter>/params.json` |
| Statistical significance | 5-seed mean ± std, paired bootstrap CI excludes zero | `runs/<iter>/significance.json` |

### Secondary (target ≥ 3 of 5)

- Beats DCN-V2 on at least 1 long-sequence dataset (MovieLens-25M with sequence features)
- Novel architectural primitive (e.g., new attention variant, new cross-network, new frequency-domain interaction)
- Theoretical contribution: at least one of (a) gradient-flow proof, (b) implicit-depth equivalence, (c) expressiveness gap lemma
- Training-time reduction ≥ 15% vs DCN-V2 at matched AUC
- Inference latency at batch=1 ≤ DCN-V2 on identical hardware

### Venue-fit signals

- **RecSys:** strong empirical results + clear practical contribution (latency or parameter efficiency) over algorithmic novelty
- **KDD:** balanced empirical + theoretical; demands ≥ 2 datasets including one industry-scale; reproducibility appendix required
- **IEEE TKDE / TNNLS:** heavier theoretical component acceptable; longer paper (12-14 pages); well-defined problem formulation + ablation completeness matter most

## 4. Datasets (pinned)

| Dataset | Size | Features | Splits (MD5-pinned) | Used for |
|---------|------|----------|---------------------|----------|
| Criteo Kaggle (subset) | ~46M rows | 13 int + 26 cat | train/val/test 8:1:1, seed=42 | Primary CTR |
| Avazu CTR | ~40M rows | 23 fields | temporal split (last 10% test) | Primary CTR |
| MovieLens-25M | 25M ratings | user/item/timestamp | leave-one-out temporal | Sequence-aware variant |

Manifest: `refs/dataset_manifest.json` (to be filled at iter 1)
License note: all three are public-research-use; record in `refs/dataset_licenses.md`.

## 5. Baselines (must compare head-to-head)

| Baseline | Year | Source | Re-implement? |
|----------|------|--------|---------------|
| LR | – | sklearn | ✓ |
| FM | 2010 | libFM-style | ✓ |
| DeepFM | 2017 | original impl | ✓ (re-train to control features) |
| DCN-V2 | 2020 | original impl | ✓ |
| xDeepFM | 2018 | original impl | ✓ |
| AutoInt | 2019 | original impl | ✓ |
| FiBiNET | 2019 | original impl | ✓ |
| (latest SOTA) | 2024–2025 | arXiv | scan in iter 1 |

Each baseline gets its own training script under `refs/baselines/<name>/`.

## 6. Milestones (not iteration-bound)

- **M0 — Scaffolding (this task)** ✓ Manual scaffold complete; auto_research protocol ready
- **M1 — Landscape scan (iter 1)** Survey 2023–2025 SOTA, pick 3 structurally distinct directions
- **M2 — Direction lockdown (iter 2–3)** Implement all 3 directions to functional baseline
- **M3 — Architecture freeze (iter 4–6)** Pick best direction, run ablations, lock hyperparameters
- **M4 — Full benchmark (iter 7–8)** All 3 datasets, 5 seeds, all baselines
- **M5 — Theory (iter 9–10)** Whichever theoretical contribution fits the winning architecture
- **M6 — Paper draft (iter 11+)** RecSys-style 9-page main + appendix; or KDD-style 10-page + reproducibility appendix; or IEEE 12-page
- **M7 — Submission prep** Venue-specific template, code release, reproducibility checklist (RecSys requires reproducibility track artifact)

## 7. Anti-temptation Rules (orchestrator self-check)

Read `state/orchestrator_self_check.md` before each iteration. Common failure modes:
- Refusing to run training because "results might be negative" → training is the deliverable, run it
- Stopping at first direction because "it's working" → run all 3 directions before declaring winner
- Adding unrelated improvements (training tricks not in baselines) → must add same trick to baselines for fair comparison
- Premature paper drafting → paper only after M5 (theory) is solid

## 8. Out of Scope

- Multi-task or multi-modal recommenders
- Reinforcement-learning recommenders (different problem class)
- Sequential-only models (RNN/Tx-only); can use sequence features but core is CTR
- Industry private data (we only use public benchmarks)

## 9. Reference Materials (to be collected in `refs/`)

- `refs/papers.bib` — bibliography (BibTeX, verified every 20 entries per auto_research §9.4)
- `refs/dataset_manifest.json` — dataset MD5s, splits, stats
- `refs/baselines/` — re-implementation code per baseline
- `refs/sota_scan_<date>.md` — rolling landscape notes
- `refs/venue_guides/` — RecSys/KDD/IEEE template & policy notes

## 10. Initial State Snapshot

- **iteration:** 0 (scaffolded)
- **stale_count:** 0
- **directions_tried:** [] (none yet — filled at iter 1)
- **next_action:** scan 2023–2025 SOTA papers (see `research_backlog.md`)
- **last_seen:** not yet loop-running (heartbeat inactive)
