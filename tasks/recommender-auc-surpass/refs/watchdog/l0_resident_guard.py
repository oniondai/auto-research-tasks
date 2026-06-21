#!/usr/bin/env python3
"""
L0 Heartbeat — resident shell guard (auto_research §7 Layer 0)

Purpose: detect heartbeat.jsonl L1 staleness. If the L1 (hourly cron) hasn't
written in > 2 hours, spin up an emergency patrol via a headless agent.

Constraint (auto_research §2.5 guardian/worker separation):
  This script may only: read heartbeat.jsonl last_seen, run `date` for
  current time, write one line to heartbeat.jsonl, and trigger a patrol.
  It must NOT read state/findings.jsonl, state/progress.json, or
  work.jsonl, and must NOT report findings on the task's behalf.

Dependencies: python3 stdlib only. No external packages.
Cron-style invocation: this is a *resident* script, not a cron job. Either:
  (a) run as systemd --user service: see refs/watchdog/l0.service
  (b) run in foreground inside a tmux/screen session (debug only)
  (c) run via `nohup ... &` (NOT recommended; no auto-restart)
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(os.environ.get("TASK_ROOT", Path.home() / "tasks" / "recommender-auc-surpass"))
HEARTBEAT_LOG = TASK_ROOT / "logs" / "heartbeat.jsonl"
L1_STALE_THRESHOLD_SEC = 2 * 3600  # 2 hours
L0_CHECK_INTERVAL_SEC = 5 * 60     # check every 5 minutes

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def parse_ts(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None

def get_l1_last_seen():
    """Find most recent L1 line in heartbeat.jsonl."""
    if not HEARTBEAT_LOG.exists():
        return None
    last = None
    with HEARTBEAT_LOG.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("layer") == "L1":
                last = e
    return last

def write_heartbeat(status, detail):
    entry = {
        "ts": now_iso(),
        "source": "l0_guard",
        "layer": "L0",
        "status": status,
        "detail": detail,
    }
    with HEARTBEAT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def trigger_patrol():
    """Spawn a headless emergency patrol. Real implementation: invoke
    `hermes delegate_task` or similar. This stub logs the intent."""
    write_heartbeat("patrol_triggered", "L1 stale > 2h; spawning headless patrol")
    # Real implementation:
    # subprocess.run(["hermes", "delegate_task", "--goal", "..."])

def main():
    print(f"[L0] starting resident guard for {TASK_ROOT} (interval={L0_CHECK_INTERVAL_SEC}s)")
    while True:
        last = get_l1_last_seen()
        if last:
            ts = parse_ts(last.get("ts", ""))
            if ts:
                age = (datetime.now(timezone.utc) - ts).total_seconds()
                if age > L1_STALE_THRESHOLD_SEC:
                    write_heartbeat("stalled", f"L1 last seen {int(age/60)} min ago (>2h)")
                    trigger_patrol()
                else:
                    write_heartbeat("alive", f"L1 last seen {int(age/60)} min ago")
        else:
            write_heartbeat("alive", "no L1 entries yet; pre-loop state")
        time.sleep(L0_CHECK_INTERVAL_SEC)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[L0] stopped")
        sys.exit(0)
