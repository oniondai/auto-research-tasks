# Recommender-Architecture AUC-Surpass — Auto-Research Scaffold

> **Status:** Scaffolded manually. Loop not yet running. This README is the protocol-binding doc for anyone (or any agent) touching this directory.

## What this is

A long-horizon autonomous research task targeting a publishable CTR-prediction architecture that beats DeepFM / DCN-V2 on AUC/LogLoss across Criteo Kaggle, Avazu, and MovieLens-25M. Targets RecSys / KDD / IEEE TKDE / TNNLS.

Built per **Deli_AutoResearch** v1.0 (installed at `~/.hermes/skills/auto_research/SKILL.md`).

## What this is NOT

- Not a finished paper. Not even a finished experiment.
- Not autonomous yet — the heartbeat loop is wired but the orchestrator/worker pair has not been launched.
- Not "running now" — invoking any tool on this directory will not start work; that requires an explicit "run auto_research on this task" command.

## Directory layout (auto_research §4)

```
recommender-auc-surpass/
├── README.md                       # this file
├── state/                          # persisted task state (single source of truth)
│   ├── task_spec.md                # goal, milestones, success criteria, baselines, datasets
│   ├── progress.json               # iteration count, stale_count, last_seen, best_result
│   ├── directions_tried.json       # structural directions + diversity rule + backlog
│   ├── research_backlog.md         # human-readable plan for the worker
│   ├── orchestrator_self_check.md  # pre-launch checklist (auto_research §2 + §7)
│   ├── findings.jsonl              # append-only findings log
│   └── iteration_log.jsonl         # per-iteration summary
├── logs/                           # append-only event logs (auto_research §4)
│   ├── work.jsonl                  # work agent decisions + metrics
│   ├── orchestrator.jsonl          # orchestrator launch / pivot / abort decisions
│   └── heartbeat.jsonl             # 3-layer heartbeat events
├── runs/                           # training run artifacts (one subdir per iteration)
│   └── (empty — populated by workers)
└── refs/                           # reference materials
    ├── watchdog/                   # L0 / L1 / L2 heartbeat scripts (python3 stdlib)
    │   ├── l0_resident_guard.py    # systemd-style resident (Layer 0)
    │   ├── l0.service              # systemd --user unit file
    │   ├── l1_hourly_patrol.py     # hourly cron (Layer 1)
    │   └── l2_callback.py          # first-action worker callback (Layer 2)
    ├── dataset_manifest.json       # dataset MD5s (filled at iter 1)
    ├── dataset_licenses.md         # public-research-use license notes
    ├── papers.bib                  # bibliography (verified every 20 entries)
    ├── baselines/<name>/           # re-implementation per baseline
    └── venue_guides/               # RecSys / KDD / IEEE template notes
```

## Protocol-binding — where each auto_research constraint is enforced

| Constraint (auto_research §) | Enforced by |
|------------------------------|-------------|
| §2.1 Zero interaction | `state/orchestrator_self_check.md` Q1 |
| §2.2 Ready-means-execute | `state/orchestrator_self_check.md` Q2 + anti-temptation §7 |
| §2.3 Callback-report-alive | `refs/watchdog/l2_callback.py` (first action of every worker callback) |
| §2.4 Persist to files | All progress lands in `state/*.json` + `logs/*.jsonl`; never in conversation |
| §2.5 Guardian-worker separation | L0/L1 scripts are read-mostly: only write to heartbeat.jsonl, never to state/findings.jsonl |
| §3 Diversity | `state/directions_tried.json.diversity_rule` + `state/research_backlog.md` structural-axes table |
| §4 State files | This directory layout |
| §6 Stall detection & pivoting | `state/progress.json.stale_count` + `state/orchestrator_self_check.md` "Stall check" |
| §7 Anti-temptation | `state/orchestrator_self_check.md` "Anti-temptation reminders" |
| §9.1 ≤ 5 large files / 300 lines | Worker prompt must enforce; orchestrator pre-launch check |
| §9.3 Validation between iters | Every iter must end with `runs/<iter>/<check>.log` |
| §9.4 Verify citations every 20 entries | `refs/papers.bib` review queue |
| §9.5 Diversity > depth | Same as §3 |

## How to launch (when ready)

This scaffold is **passive**. To make it run, three things need to happen — explicitly:

### 1. Wire L1 (hourly cron)

Use the hermes cronjob tool (one-time setup, survives across sessions). Example prompt:

```
Schedule an hourly cron job. Prompt:
  "Run the L1 heartbeat for the recommender-auc-surpass task.
   Execute: python3 /home/victor/tasks/recommender-auc-surpass/refs/watchdog/l1_hourly_patrol.py
   Then append a summary to logs/orchestrator.jsonl.
   Zero interaction with the user. Auto-research framework constraints apply."
Schedule: 0 * * * *  (every hour, on the hour)
Name: recommender-auc-surpass-l1
Deliver: local  (silent watchdog, no chat spam)
```

Alternative (if hermes cronjob unavailable): install the script as `/etc/cron.hourly/recommender-auc-surpass-l1` and `chmod +x` it.

### 2. Wire L0 (resident guard)

```bash
mkdir -p ~/.config/systemd/user
cp refs/watchdog/l0.service ~/.config/systemd/user/recommender-auc-surpass-l0.service
systemctl --user daemon-reload
systemctl --user enable --now recommender-auc-surpass-l0.service
systemctl --user status recommender-auc-surpass-l0.service   # verify running
```

(Requires systemd --user session; on systems without it, run `nohup python3 refs/watchdog/l0_resident_guard.py &` in a tmux session — less robust.)

### 3. Launch the first worker

Tell the active Hermes session:

> Use auto_research on `~/tasks/recommender-auc-surpass/`. Start iter 1: landscape scan per `state/research_backlog.md` (M1). Worker must:
> 1. First action: `python3 refs/watchdog/l2_callback.py` (L2 report-alive)
> 2. Web-search arXiv 2023–2025 for CTR / feature-interaction / cross-network papers
> 3. Append each finding as one JSONL line to `state/findings.jsonl`
> 4. After 5–8 findings or 15 rounds / 30 min (whichever first), write iter summary to `state/iteration_log.jsonl`
> 5. Update `state/progress.json.iteration += 1`
> 6. Do not run any training in iter 1 (research only)

That's it. The orchestrator (the active session) reads `state/research_backlog.md` next time it's invoked, picks the next direction, and launches the next worker.

## How to STOP / inspect

```bash
# Tail heartbeat (latest events)
tail -f logs/heartbeat.jsonl

# Show current state
cat state/progress.json | python3 -m json.tool

# Show all findings so far
cat state/findings.jsonl | python3 -c "import sys,json; [print(json.loads(l).get('detail','')[:120]) for l in sys.stdin if l.strip()]"

# Pause the loop (without losing state)
# Just don't launch the next worker. Heartbeat keeps running; that's fine.
```

## Recovery notes

- **Session died mid-iter:** L0/L1 detect via missing last_seen updates. Orchestrator reopens with state injection (file read, not resume).
- **Disk fills:** `logs/*.jsonl` and `state/findings.jsonl` grow unbounded; add a `git gc` or rotation in the worker prompt if it persists > 7 days.
- **Worker diverges from protocol:** orchestrator reads `state/orchestrator_self_check.md` next launch; if worker is irrecoverable, kill it and start fresh — per auto_research §3 (fresh session over resume).
