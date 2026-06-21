# auto-research-tasks

Versioned scaffolds and iteration history for long-horizon autonomous research tasks, built per the **Deli_AutoResearch** protocol (installed in `~/.hermes/skills/auto_research/SKILL.md`).

This is a **companion repo** to [oniondai/hermes_awesome](https://github.com/oniondai/hermes_awesome) (which holds reusable Hermes Agent setup skills, scripts, and notes). The split:

| Repo | Holds |
|------|-------|
| `hermes_awesome` | Static skills, install scripts, config notes (Hermes setup) |
| `auto-research-tasks` | Long-horizon autonomous research task scaffolds and their iteration history (Deli_AutoResearch) |

## What is a task here?

A task is a **long-horizon autonomous research problem** that runs for days to weeks under the Deli_AutoResearch protocol. Each task is a self-contained directory under `tasks/<task-name>/` with:

- `state/` — single source of truth: `task_spec.md`, `progress.json`, `directions_tried.json`, `research_backlog.md`, `orchestrator_self_check.md`, `findings.jsonl` *(gitignored — local-only)*
- `logs/` — append-only event logs from work / orchestrator / heartbeat *(gitignored — local-only)*
- `runs/` — training run artifacts per iteration *(gitignored — too large / binary)*
- `refs/` — bibliography, dataset manifests, watchdog scripts, venue guides
- `README.md` — protocol-binding doc explaining how the auto_research constraints map to that task's files

## What gets versioned vs. what doesn't

**Versioned (public):**
- `state/task_spec.md`, `state/progress.json`, `state/directions_tried.json`, `state/research_backlog.md`, `state/orchestrator_self_check.md`
- `refs/` (watchdog scripts, papers.bib, dataset manifests, venue guides)
- `README.md`

**Not versioned (.gitignored):**
- `state/findings.jsonl`, `state/iteration_log.jsonl` — append-only machine logs, one JSONL line per worker decision / metric / event
- `logs/*.jsonl` — heartbeat / orchestrator / work agent runtime logs
- `runs/` — training artifacts (model checkpoints, eval JSONs); track in `state/progress.json.best_result` instead

Rationale: every iteration appends to the JSONL logs, which would create unbounded diff noise and force `--force` pushes. The versioned state files (`progress.json`, `directions_tried.json`) carry the **summary** that matters for the iteration history.

## Tasks in this repo

| Task | Venue target | Status | Started |
|------|--------------|--------|---------|
| [recommender-auc-surpass](tasks/recommender-auc-surpass/) | RecSys / KDD / IEEE | scaffolded (M0) | 2026-06-21 |

More tasks will be added as new long-horizon research problems are started.

## Iteration workflow

For each meaningful change to a task, commit + push with a message of the form:

```
tasks/<name>: <what changed and why>

e.g.
tasks/recommender-auc-surpass: lock direction D1 (Sparse MoE Cross-Network) as primary
tasks/recommender-auc-surpass: iter 3 — D2 FFT-DCN stale, pivot to D3 Neural-ODE
tasks/recommender-auc-surpass: M4 complete — full benchmark on Criteo/Avazu/MovieLens, 5 seeds
```

This gives a chronological iteration history per task in `git log -- tasks/<name>/`.

## Cross-references

- Protocol spec: `~/.hermes/skills/auto_research/SKILL.md` (local install; canonical source is [victorchen96/auto_research](https://victorchen96.github.io/auto_research/framework.html))
- Hermes setup repo (sister): [oniondai/hermes_awesome](https://github.com/oniondai/hermes_awesome)
- Hermes Agent itself: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

## License

MIT — see [LICENSE](LICENSE).