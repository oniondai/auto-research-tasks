#!/usr/bin/env python3
"""
L2 Heartbeat — first action of every worker callback (auto_research §7 Layer 2)

Purpose: when a worker iteration callback fires (e.g. after context compaction
or session resume), the very first thing it does is update last_seen in
state/progress.json. This is the protocol's "report-alive" signal (auto_research §2.3).

Usage: the worker prompt must include the line:
    "First action on every callback: run `python3 refs/watchdog/l2_callback.py`"

Dependencies: python3 stdlib only.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(os.environ.get("TASK_ROOT", Path.home() / "tasks" / "recommender-auc-surpass"))
HEARTBEAT_LOG = TASK_ROOT / "logs" / "heartbeat.jsonl"
PROGRESS_FILE = TASK_ROOT / "state" / "progress.json"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    # Update last_seen in progress.json
    if PROGRESS_FILE.exists():
        try:
            prog = json.loads(PROGRESS_FILE.read_text())
        except json.JSONDecodeError:
            prog = {}
    else:
        prog = {}
    prog["last_seen"] = now_iso()
    PROGRESS_FILE.write_text(json.dumps(prog, indent=2))

    # Write L2 heartbeat line
    entry = {
        "ts": now_iso(),
        "source": "l2_callback",
        "layer": "L2",
        "status": "alive",
        "detail": f"worker callback report-alive; iteration={prog.get('iteration')}",
    }
    with HEARTBEAT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    main()
