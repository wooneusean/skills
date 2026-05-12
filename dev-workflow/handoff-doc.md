---
name: handoff-doc
description: Write a handoff.md file that preserves context at the end of a coding session so the next session can resume without losing state or repeating dead ends. Use this skill whenever the user says any of "end the session", "wrap up", "before we end", "before I sign off", "stop for the day", "save state", "create a handoff", "write a handoff", "pass this off", or mentions a handoff.md / handoff document. Also trigger proactively when the user signals the session is winding down and the work is unfinished — a good handoff is cheap to write and saves real time later.
---

# Handoff Doc

Write a `handoff.md` file so the next session — a future Claude run, or a human teammate — can pick up exactly where this one stopped, without redoing failed work.

## Before writing

Reconstruct context from the current session before asking the user anything. You already know:
- What was discussed and decided
- What files were opened, read, or edited
- What commands were run and their output
- What approaches were tried and abandoned

Pull on those threads first. Only ask the user for input if something critical is genuinely missing (e.g., the goal was never stated explicitly).

Optionally run `git status` and `git diff --stat` to ground the "files in flight" section in the actual working tree.

## What to capture

Use exactly these five sections, in this order:

### 1. Goal
What we're working toward. One or two sentences. The *outcome*, not the steps. If there's a broader goal and a narrower current sub-goal, name both.

### 2. Current state
Where things stand right now. What works, what doesn't, what's half-done. If tests pass or fail, say which. If the code runs but produces wrong output, describe actual vs expected. Be specific — file paths, function names, exact error messages.

### 3. Files in flight
The files actively being edited and what's changing in each. Bullet list:
- `path/to/file.py` — added the X handler, still need to wire it into Y
- `path/to/other.ts` — refactored the parser, broke two tests in `parser.test.ts`

Include uncommitted changes.

### 4. What was tried and didn't work
The most important section. List approaches attempted and rejected with a brief reason for each, so the next session does not re-run the same dead ends.
- Tried X — failed because Y
- Considered Z — ruled out because W

Include error messages or stack traces when they pinpoint the issue. Be concrete. If nothing has been tried and rejected yet, say so in one line — do not pad.

### 5. Next step
The single most promising next action, written so the next session can act immediately. Not "figure out the bug" — "add a null check in `parseConfig` at line 47, then re-run `pytest tests/test_config.py`."

If there are 2–3 viable next moves, list them in priority order with a short note on each.

## Style

- Past tense for what happened, present tense for current state, imperative for next steps.
- Terse. Bullets over prose. Code references in backticks.
- No preambles like "In this session we…" — jump straight to content.
- If a section is genuinely short, keep it short.

## Where to write it

Default to `./handoff.md` in the current working directory.

If `handoff.md` already exists, prepend the new entry above the old content under a `## YYYY-MM-DD HH:MM` header, pushing older entries down. Do not silently overwrite — old handoffs often have context the new one didn't capture.

## After writing

Show the user the path and a one-line summary of what was captured. Do not paste the full file back into chat — they can open it.

