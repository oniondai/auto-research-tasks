# Security Policy

## Reporting

If you discover a security issue in this repository, please report it privately via GitHub Security Advisories rather than opening a public issue.

## Scope

This repo contains research task scaffolds. The actual data, models, and training runs are NOT committed (see `.gitignore`). The committed material is:

- Markdown spec files
- JSON state snapshots
- Python scripts for watchdog / heartbeat monitoring (3-layer guard per Deli_AutoResearch §7)
- Bibliography BibTeX

No secrets, no credentials, no model checkpoints, no training data should ever be committed. If you accidentally commit something sensitive:

```bash
git filter-repo --path <file> --invert-paths  # or use BFG Repo-Cleaner
git push --force
# ROTATE THE SECRET IMMEDIATELY — removing it from history does not invalidate it
```

## Code execution safety

Python scripts under `tasks/*/refs/watchdog/` are intended to run on the owner's own machine, with read-only access to their own task state. They must not be run on untrusted environments:

- `l0_resident_guard.py` runs continuously (intended as systemd --user service)
- `l1_hourly_patrol.py` runs from cron and writes only to `logs/heartbeat.jsonl`
- `l2_callback.py` is called by worker agents and updates `state/progress.json.last_seen`

None of these scripts accept network input or read user-controlled files beyond the task's own `state/` and `logs/` directories.

## Supported versions

This repo follows the Deli_AutoResearch protocol as documented. Breaking changes to the protocol will be called out in commit messages with a `BREAKING:` prefix.