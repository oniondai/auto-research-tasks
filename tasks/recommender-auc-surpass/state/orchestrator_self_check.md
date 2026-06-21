# Orchestrator Self-Check (run before each iteration launch)

> Per auto_research §2 (5 constraints) and §7 anti-temptation rules. Answer honestly; this is the protocol's separation-of-duties enforcement point. If any answer is "no" or "I want to skip", halt and write the decision to `logs/orchestrator.jsonl` before proceeding.

## Pre-launch checklist

1. **[zero-interaction]** Will this iteration require user input mid-run?
   - Expected answer: NO. If yes, redesign the iteration to resolve ambiguity internally and log it.

2. **[ready-means-execute]** Am I about to launch a worker that will prepare-then-ask-permission?
   - Expected answer: NO. Workers must execute training / eval / paper-draft operations without confirmation gates.

3. **[callback-report-alive]** Does the worker callback path update `state/progress.json.last_seen` as its FIRST action?
   - Expected answer: YES. If not, fix the worker prompt before launching.

4. **[persist-to-files]** Will all progress land in `state/` and `logs/` files (not just chat)?
   - Expected answer: YES. If work is happening only in conversation, abort and rewrite the prompt.

5. **[guardian-separation]** Is the heartbeat watchdog I am about to launch only doing liveness-check / restart / nudge?
   - Expected answer: YES. It must NOT read task data, modify `state/findings.jsonl`, or report on the task's behalf.

## Anti-temptation reminders (auto_research §7)

- The next direction must differ from every tried direction on a structural axis
- Do not stop after the first positive signal — diversity requirement stands until ≥ 3 structural directions are tried
- Do not skip validation — every iter must end with a test/compile/check that writes to `runs/<iter>/<check>.log`
- Citation-bearing claims (model numbers, AUC deltas cited from papers) must be verified every 20 entries

## Stall check (auto_research §6)

Read `state/progress.json`:
- If `stale_count >= 2`: forced pivot. Change a **structural** constraint, not a parameter
- If `stale_count >= 4`: flag for human attention, write to `blocking_issues`

## Diversity gate

Read `state/directions_tried.json.directions[]`:
- If `directions_tried_count < 3`: do not drill deeper on current direction; pick next from `research_backlog.md`
- If `directions_tried_count >= 3` AND none yield significant AUC gain: declare stall, mark in `progress.json`, do not silently retry

## Output

After self-check passes, write a one-line decision to `logs/orchestrator.jsonl`:
`{"ts":"...", "source":"orchestrator", "level":"decision", "event":"iteration_<N>_launch", "detail":"direction=D?, dataset=?, worker=?"}`

If self-check fails, write:
`{"ts":"...", "source":"orchestrator", "level":"warn", "event":"iteration_<N>_BLOCKED", "detail":"<which rule failed and why>"}`
