# Roles and models

## The roles

| Role | Does | Access | Runs |
|---|---|---|---|
| Orchestrator | Writes the brief and tracker. Dispatches jobs, gates and commits, folds findings forward. Writes no product code. | Full, in the user's session | This session |
| Planner | Writes one item's plan: facts with `path:line`, changes, tests, verification, risks, questions for the user. | Read-only | Ahead of implementation, several at once |
| Pre-flight checker | Verifies the plan against the current code and live data, measures what the plan guessed, and writes binding amendments. | Read-only: code, GET requests, SELECT queries | After its plan, before its implementation |
| Implementer | Builds one item: code, tests, docs, browser or runtime checks. Leaves its changes uncommitted. | Full, unattended | One at a time, on the main tree |
| Diff reviewer | Reviews the commit's diff for correctness, contracts, tests, docs and scope. | Read-only, in a worktree pinned to the commit | In parallel with the next implementation |
| Live reviewer | Exercises the running app at the commit and compares it with the design and the requirements. | Read-only; writes only through a stub or in-page interception | In parallel with the diff reviewer |

**Independence:** use different models for the implementer and the diff
reviewer. When only one model is available, run each reviewer as a
fresh-context instance that sees the brief, the plan and the diff, but not
the implementer's reasoning.

**Capability:**
- **Implementer:** the strongest coding model, at high reasoning effort.
- **Pre-flight checker and live reviewer:** a model that is good at tool
  use, since they query live data and drive the running app.
- **Planner and diff reviewer:** these tolerate a cheaper model better
  than the implementer does.

## Asking the user

Ask before writing the brief, in two rounds. Use the harness's question
tool if it has one.

1. **What is available.** "Which models or agents can this run use? For
   example, subagents of this session, or another provider's CLI such as
   Codex or Gemini. Give the model names, and the CLI command for each
   external one."
2. **The assignment.** Propose a mapping from the configurations below and
   show it as a table: role, model, how it runs (subagent or CLI) and
   effort. Then ask the user to confirm it or change any row. Also ask:
   - the time or usage limit per job and for the whole run;
   - whether they can be reached during the run, and how;
   - whether external CLIs may run unsandboxed when their sandbox blocks
     what the checks need (a browser, a simulator, git).

When the user has only a few minutes, combine both rounds into one
message: ask which models are available, and offer the single-model mapping
as the default for them to confirm or edit.

Record the final table in the tracker. Ask again only when a model becomes
unavailable during the run.

## Configurations

| Available | Orchestrator | Planner | Pre-flight | Implementer | Diff reviewer | Live reviewer |
|---|---|---|---|---|---|---|
| One model | session | subagent | subagent | subagent | subagent (fresh context) | subagent |
| Two providers, A in session | A | B | A subagent | B | A subagent, or B in a fresh context | A subagent |
| Three or more | A | B | A subagent | B | C | A subagent |

Keep the pre-flight checker and the live reviewer on the session's own
subagents whenever possible. They need the same live-environment access
that the orchestrator has.

## Running external CLI jobs

When a role runs on an external CLI, wrap each job in a small runner script
with this contract:

- **Input:** `<job-name> <model> <access-level> [effort] [timeout]`, with the
  prompt read from `prompts/<job-name>.md`.
- **Output:** the final message goes to `out/<job-name>.md` and the full
  transcript to `logs/<job-name>.log`. The script prints a one-line summary:
  exit code, minutes, output size.
- **Behaviour:**
  - stdin comes from `/dev/null`;
  - it runs under `timeout`;
  - the working directory can be overridden through an environment
    variable, so a reviewer can be pointed at a pinned worktree.
- **Launching:** start it as a background task that the harness tracks, so
  completion wakes the orchestrator. A detached `nohup` job gives no
  completion signal.
- **Editing the runner:** replace it with `mv` rather than editing it in
  place, because running jobs may still be reading it.

Example invocations; check the installed versions with `--help`:

```bash
# Codex CLI
codex exec -m <model> -c model_reasoning_effort=<effort> -s <read-only|workspace-write|danger-full-access> \
  -C <dir> -o out/<job>.md "$(cat prompts/<job>.md)" </dev/null > logs/<job>.log 2>&1

# Claude Code, non-interactive
claude -p --model <model> "$(cat prompts/<job>.md)" </dev/null > out/<job>.md 2> logs/<job>.log
```

Grant unattended edit permissions only in the mode the user approved in
round 2.
