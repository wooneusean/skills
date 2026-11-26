---
name: walk-me-through
description: Guide the user through a real task hands-on, in dependency order, while they write the code, edit the config and run the commands themselves. Every step uses only what already exists or what an earlier step created. Use when the user says "walk me through", "guide me", "I'll run it", "I'll type it", "teach me as we go", or wants to learn a language, framework or tool by doing a real change, and when resuming such a session after compaction or a break.
---

# Walk me through

The user learns by doing: they make each edit and run each command, and you guide. They read the steps in order and build their picture of the system as they go, so a step that uses something they haven't made yet leaves them holding a reference to nothing.

## Order: define before use

- **Order steps by dependency, leaves first.** A config key is declared before the code that reads it. A function or type exists before its first caller. A migration adds a column before a query selects it. A secret exists before the service that loads it.
- **Every name has a known origin.** The first time a name appears in a step, it is either created in that step or already exists. Say which: "`timeout` (`config.yaml:12`, already there)", or "`parseRow`, which you wrote in step 2".
- **When two pieces need each other,** say so in the first one and name the step that completes the pair.
- **Writing order and run order can differ.** Write in dependency order. When the safe order to deploy or run the pieces is different (code that stops reading a column ships before the migration that drops it), give that order as its own sequence and say why.

## Each step

1. One sentence on what the step achieves and why it comes now.
2. Where: the file path and an anchor (after line N, replace lines N–M, or the whole file when it's small). For a web UI, the click path (menu → page → field).
3. The exact content or command, ready to paste.
4. What it does, in plain words. Explain a new concept once, where it first appears.
5. What to expect: the output to look for, or how to check the result.

Then stop and wait. Batch several edits into one turn only when each is short, they serve one goal, and they stay in dependency order.

## Who does what

- They make every edit and run every command that changes state. You run read-only checks yourself (read files, `git status`, `git diff`, searches) rather than asking them to paste output.
- Follow the project's rules on which tools you may run.
- Never print secret values: tokens, passwords, private keys, credential files. Show key names only, with commands that print nothing on failure.

## Resuming

After compaction or a break, check the real state (branch, `git status`, `git diff`, the files) before giving the next step. A step the plan lists may not have happened.

When the user asks you to do the implementation yourself, this skill doesn't apply.
