#!/usr/bin/env python3
"""
L1 Heartbeat — hourly durable cron (auto_research §7 Layer 1)

Purpose: every hour, check:
  (1) all loops' last_seen (heartbeat.jsonl) — restart timed-out loops
  (2) all tasks' progress (state/progress.json) — detect stalls > 2h, nudge

Constraint (auto_research §2.5): may only liveness-check, restart, nudge.
  May NOT read findings.jsonl, modify state files, or report on task's behalf.

Dependencies: python3 stdlib only.
Invocation: register with hermes cronjob tool (see README §"Wire L1") OR
            install as /etc/cron.hourly/recommender-auc-surpass-l1
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(os.environ.get("TASK_ROOT", Path.home() / "tasks" / "recommender-auc-surpass"))
HEARTBEAT_LOG = TASK_ROOT / "logs" / "heartbeat.jsonl"
PROGRESS_FILE = TASK_ROOT / "state" / "progress.json"
STALL_THRESHOLD_SEC = 2 * 3600  # 2h per auto_research §7

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def write_l1_entry(check, status, detail):
    entry = {
        "ts": now_iso(),
        "source": "l1_cron",
        "layer": "L1",
        "check": check,
        "status": status,
        "detail": detail,
    }
    with HEARTBEAT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def check_stall():
    """Read progress.json. If last_seen is null or > 2h old, write a nudge entry.
    Per auto_research §2.5 we do NOT modify progress.json — only log the nudge."""
    if not PROGRESS_FILE.exists():
        write_l1_entry("stall_check", "missing_state", "progress.json absent")
        return
    try:
        prog = json.loads(PROGRESS_FILE.read_text())
    except json.JSONDecodeError:
        write_l1_entry("stall_check", "error", "progress.json unparseable")
        return
    last_seen = prog.get("last_seen")
    if last_seen is None:
        write_l1_entry("stall_check", "alive", "no last_seen (loop not running yet)")
        return
    try:
        ts = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
    except Exception:
        write_l1_entry("stall_check", "error", f"unparseable last_seen: {last_seen!r}")
        return
    age = (datetime.now(timezone.utc) - ts).total_seconds()
    stale = prog.get("stale_count", 0)
    if age > STALL_THRESHOLD_SEC:
        # Auto_research §7: 3 consecutive nudges = structurally stuck, stop nudging
        if stale >= 3:
            write_l1_entry("stall_check", "stuck", f"stale_count={stale}; stop nudging, reopen with new direction")
        else:
            write_l1_entry("stall_check", "nudged", f"no progress for {int(age/60)} min; stale_count would increment")
    else:
        write_l1_entry("stall_check", "alive", f"last seen {int(age/60)} min ago; iteration={prog.get('iteration')}")

def main():
    write_l1_entry("l1_tick", "alive", f"L1 hourly run from {TASK_ROOT}")
    check_stall()

if __name__ == "__main__":
    main()
