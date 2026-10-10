---
name: orchestrated-agent-run
description: Use when a queue of several code changes is to be landed by AI agents with little or no supervision, such as an overnight or unattended run, a multi-item backlog, or work split between planner, implementer and reviewer agents or models from one or more providers.
---

# Orchestrated Agent Run

## Overview

One orchestrator session runs a queue of items through **plan → pre-flight →
implement → gate and commit → review → fold in**. Planning and reviewing run
in parallel. Implementation is serial, one item at a time on the main
working tree. The orchestrator writes no product code. It dispatches jobs,
checks what comes back, commits, and carries review findings forward into
the next item, so the pipeline never waits on a re-review loop.

Use it for several items that each end as their own reviewed commit, in a
git repository with a runnable dev environment. Skip it for a single small
change, or for exploratory work with no settled plan.

## Step 0: Ask which model handles each role

Ask the user before anything else, and don't assume which providers they
have. Many developers have a single provider, and every role still works
with fresh-context instances of one model. `roles.md` has the role table,
the exact question to ask, ready-made configurations and the runner contract
for external CLIs. Record the answers in the tracker.

## Step 1: Brief, tracker and wake-up

- **Approved plan:** the user's design document for the work the queue
  covers, approved by the user before the run starts. When none exists,
  the brief's item paragraphs are the approved plan. Each item also gets an
  *item plan* from a planner during the run.
- **Brief:** a doc in the repo that agents read. Commit it before the run
  starts. Agents never edit it. The orchestrator writes the Report into it
  in one commit at the end, and the user deletes it after reviewing the
  Report. It holds:
  - the goal;
  - the queue in priority order, one paragraph per item, each naming the
    earlier items it builds on;
  - rules for every item: tests, the browser or runtime check, an evidence
    directory, docs;
  - hard limits: no push or deploy, data safety, dependencies, migrations;
  - how undecided questions are settled when the user can't be reached:
    the order given under Pre-flight below;
  - an empty Report section.
- **Tracker:** the orchestrator's state, kept outside the repo. It holds:
  - the role assignments and runner paths;
  - each item's progress with its commit SHAs;
  - each finding and the item it was folded into;
  - notes for the user and lessons.

  Re-read it after every context compaction, and update it at every step.
- **Wake-up:** a recurring heartbeat if the harness has one ("re-read the
  tracker; advance the pipeline if no job is running"). Add a sleep
  inhibitor (`systemd-inhibit`, `caffeinate`) and stop both at the end.
  Without a heartbeat, rely on the harness's completion notifications for
  background jobs, and never leave the session waiting on a job that cannot
  notify it.
- **Budget:** a time limit per job and for the whole run. Don't start an
  item that the remaining budget can't finish and verify; one finished item
  is worth more than several half-done ones.

## Step 2: The pipeline

1. **Plan:** one read-only planner per item writes its item plan, ahead of
   implementation and in parallel. An item that builds on unlanded items is
   planned after they commit, or re-checked against what actually landed.
2. **Pre-flight:** a separate checker verifies the plan against the current
   code and live data, read-only. It measures what the plan guessed and
   writes numbered amendments that override the item plan. Questions for
   the user come out here. Settle each one in this order:
   - from the approved plan's text, where it answers the question;
   - otherwise ask the user before implementation starts;
   - if the user can't be reached, take the checker's suggested default
     when it stays within the hard limits and is easy to reverse, and note
     it for the Report;
   - otherwise skip the item and the items that build on it.
3. **Implement:** one implementer at a time, unattended, leaving its changes
   uncommitted. The prompt is assembled from:
   - the standing rules;
   - the item text;
   - the amendments;
   - the item plan;
   - fold-ins.
4. **Gate and commit:** read the implementer's report and the diff.
   - Check scope, and look for edits to forbidden files (the brief,
     lockfiles, migrations).
   - Look for formatter churn, and for the run's name or evidence paths in
     committed files.
   - Check for leftover processes or stubs, and that every environment
     override is restored.

   Then unstage everything (`git reset`) and stage by path: one logical
   change per commit, with fold-in fixes in their own commits. When a
   fold-in fix and the item share a file, split them by hunk: write the
   diff to a patch, keep the fold-in hunks, and stage it with
   `git apply --cached`. If they can't be separated, commit them together
   and say so in the message. Build or type-check each split commit on its
   own.
5. **Review:** two independent reviewers run in parallel with the next
   item's implementation.
   - A **diff reviewer** works in a worktree pinned to the commit.
   - A **live reviewer** exercises the running app at that commit. It uses
     its own dev server from the pinned worktree, or the main one while no
     implementer is running; the main one saves memory on a smaller
     machine. Both servers use the shared dev backend and database, so the
     reviewer stays read-only. Review an item that carries a migration only
     after that migration is applied.

   Every finding names a severity and a concrete failure scenario.
6. **Fold in:** findings go into the next implementer prompt as a FOLD-IN
   section. For each finding the implementer reports one of: already fixed,
   fixed, or rejected with a reason. Cap re-reviews of the same code at two
   or three rounds.

   A P0 or P1 finding on an item that later items build on stops the line.
   A dependent item that is already implementing finishes and goes through
   the gate. The fix then runs as a dedicated job, reviewed like any item,
   before anything else that depends on the item launches. Re-check the
   finished dependent and the `[recheck]` amendments against the fix.
7. **Finish:**
   - Run one fix round for the last item's findings, and review it.
   - Write the Report into the brief:
     - one line per item: its commit SHAs (fold-in commits too), what
       changed, the test and review results;
     - then skipped items with their questions, the defaults that were
       taken, and the findings left open.
   - Stop the heartbeat and the inhibitor, remove the worktrees, and record
     the lessons.

`prompts.md` holds the prompt skeleton for each role.

## Safety rules for every agent

- **Real data:** verification writes go only through a write-rejecting stub
  or through clearly named fixtures that are removed afterwards. A
  write-rejecting stub fails every non-GET request and never forwards it.
  - Never enter values in settings or forms that save on change.
  - Back up before any database write.
  - Run DB-backed tests on a scratch database, behind a name guard.
- **Read-only roles stay read-only.** A "quick check" POST is a write,
  and so is a query-plan command that executes its statement (SQL
  `EXPLAIN ANALYZE`).
- **Live dev stack:**
  - Never run a build that cleans the output directory a running dev
    server is serving from.
  - Restore any backend URL or other override that was pointed at a stub.
- **Heavy processes:** an agent that starts a browser, simulator,
  emulator, dev server, container or stub stops it when its check is done.
  After every job, the orchestrator looks for processes the job left
  behind and stops them. Leftovers like these outlive the job that started
  them and pile up across a long run. Size parallelism to the machine: how
  many agents run checks at once depends on the memory those checks take.
- **Docs:** run code formatters only on code files. Over markdown they
  reflow tables and re-quote frontmatter. Never edit the brief.

## When a job dies

1. **Clean up first.** Stop the processes the job left behind (browsers,
   simulators, dev servers, stubs), and point anything that was aimed at a
   dead stub back at the real backend.
2. **Decide whether to relaunch.** A job that hits its own time limit
   counts as a death.
   - If the system killed the job for resources and the user can be
     reached, ask before relaunching.
   - Otherwise relaunch once, with less parallelism (pause the reviews
     first).
3. **Relaunch as a continuation.** Use the same prompt plus a hand-over
   section that gives the `git status` and tells the job to treat the
   partial diff as its own draft.
4. **A second death** skips the item and the items that build on it.
   Save its partial diff as a patch next to the tracker. Then restore a
   clean tree (`git stash push -u`, or check out the files it touched).
   Record why in the Report, and continue with the independent items.

## Common mistakes

| Mistake | Fix |
|---|---|
| Implementing several items at once on one stack | Run implementers serially. Parallelise planning and reviews. |
| Re-reviewing until clean before the next item starts | Fold findings into the next item and cap the rounds. |
| Only a diff review | Add the live reviewer, which finds the user-visible bugs. |
| Committing a path that was already staged | Run `git reset` before staging by path. |
| A split commit that imports a later commit's symbol | Build or type-check each commit in a worktree. |
| Agents leave browsers, simulators or dev servers running after their checks | Make stopping them part of every agent's finish, and sweep for leftovers after each job. |
| Settling questions for the user inside the implementation | Surface them at pre-flight. |
