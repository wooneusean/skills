---
name: orchestrated-agent-run
description: Use when a queue of several code changes is to be landed by AI agents with little or no supervision, such as an overnight or unattended run, a multi-item backlog, or work split between planner, implementer and reviewer agents or models from one or more providers.
---

# Orchestrated Agent Run

## Overview

One orchestrator session lands a queue of items as **build jobs**. A job
builds two to four related items in order and commits each item itself.
While it builds:

- the orchestrator pre-flights the next job;
- a diff reviewer reviews each item commit as soon as it lands, and its
  findings go straight to the running builder;
- the previous job's live review runs on a production build.

The builder is the only critical path. Nothing waits on a re-review loop or
a dedicated fix job. The orchestrator writes no product code.

Why this shape: one project ran the same queue both ways. One item per job,
with orchestrator commits and dedicated fix jobs, took 21 h 40 min for 8
items. Batched jobs took 12 h 50 min for 11 items, with the same review
depth. Most of the saving came from three places:

- no fix jobs (they had taken a fifth of the earlier run);
- one internal review per job instead of per item;
- browser suites run once per job instead of after every change.

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
  the brief's item paragraphs are the approved plan. Items the approved plan
  doesn't detail get an *item plan* from a planner during the run.
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
- **Tracker:** the orchestrator's state, kept outside the repo. Re-read it
  after every context compaction, and update it at every step. Keep it
  short enough to re-read cheaply: start a new tracker for each phase and
  archive the old one. It holds:
  - the role assignments and runner paths;
  - the job table: each job's items in build order, its pre-flight and its
    reviews;
  - the queue: one row per item with its amendments count, commits, diff
    review and live review;
  - the minor-findings list, which feeds the minor-bug pass;
  - progress lines with times and commit SHAs;
  - decisions taken for the user, and lessons.
- **Wake-up:** a recurring heartbeat if the harness has one ("re-read the
  tracker; advance the pipeline for any free slot"). Add a sleep inhibitor
  (`systemd-inhibit`, `caffeinate`) and stop both at the end. Without a
  heartbeat, rely on the harness's completion notifications for background
  jobs, and never leave the session waiting on a job that cannot notify it.
- **Budget:** a time limit per job and for the whole run. Don't start a job
  that the remaining budget can't finish and verify; one finished job is
  worth more than several half-done ones.
- **Effort:** where a model offers reasoning levels, the orchestrator picks
  one per job to fit the job:
  - the highest for planners and complex items (races, cache coordination,
    changes across several surfaces);
  - high for ordinary jobs;
  - medium for docs-only jobs and small targeted fixes.

  Running every job at the highest level costs hours over a run and buys
  little on simple jobs.
- **Prompts:** every prompt states the scope and the quality bar, never
  urgency. An agent told to be quick cuts its verification. A run gets
  faster from its shape (batched jobs, reviews off the critical path, checks
  run once), not from rushing the agents.

## Step 2: The pipeline

1. **Group the queue into jobs.**
   - Items that share code go in one job.
   - An item that later items plug into (a shared mechanism, a component
     the next items extend) runs alone, early.
   - Order the jobs so that everything a job consumes has landed before it
     starts.
   - Two to four items per job. A larger job will likely compact its context
     once; per-item commits make that safe.
2. **Plan:** a read-only planner writes the item plan for each item that
   needs one, ahead and in parallel.
3. **Pre-flight, one per job:** a separate checker verifies the plans of
   all the job's items against the current code and live data, read-only.
   - It measures what the plans guessed and writes one amendments file per
     item; the amendments override the item plan.
   - It runs while the previous job builds. It marks `[recheck]` every
     amendment that depends on a job that hasn't landed.
   - Questions for the user come out here. Settle each one in this order:
     - from the approved plan's text, where it answers the question;
     - otherwise ask the user before the job starts;
     - if the user can't be reached, take the checker's suggested default
       when it stays within the hard limits and is easy to reverse, and
       note it for the Report;
     - otherwise skip the item and the items that build on it.
4. **Build:** one builder at a time, on the main working tree.
   - **The prompt** is the standing rules, then a job section (the prompt
     file's own path, the start commit and the items in build order), then
     for each item its brief text, amendments and plan, then the fold-ins,
     then orchestrator notes.
   - **The notes** say what actually landed since the pre-flight (commits,
     names that shipped, moved line numbers), and they list the decisions
     taken for the user that bind the job.
   - **Item by item:** the builder builds the items in order. Before each
     commit it runs the type check, lint, the formatter check and the
     item's affected tests. Then it commits the item itself, staging by
     path. Fixes go in their own fix commits.
   - **After a compaction:** it re-reads its prompt file and
     `git log <start>..HEAD`, and resumes at the first item without a
     commit.
   - **At the end of the job:** it runs the full unit suite and each touched
     browser suite once. While working it runs only affected specs, and
     re-runs only the browser tests that failed.
   - **Before reporting:** it runs one internal review over the whole job:
     a single fresh-context agent that exercises the running app. It
     launches that reviewer through the harness's own subagent mechanism,
     never through a CLI with a permission-bypass flag. Then it fixes the
     findings in fix commits.
5. **Diff review, per item commit:** on every heartbeat, check
   `git log <start>..HEAD`.
   - Pin a worktree to each new item commit, and launch a diff reviewer on
     it at once, while the builder works on its next item.
   - While the builder is still running, send it the findings by message:
     "fix these after the item you're on and before your internal review,
     each as its own fix commit with a regression test". After it has
     reported, they go to the next builder as fold-ins.
   - Review the fix commits for one finding round as well; see the fix
     policy below.
6. **Check each job** when its builder reports:
   - Read the report, and save it where the live reviewer can read it.
   - Check scope and forbidden files (the brief, lockfiles, migrations),
     and look for the run's name or evidence paths in committed files.
   - Sweep for leftovers: browser sessions, stubs, servers, worktrees and
     background shells. A wait loop on `pgrep -f "<pattern>"` matches its
     own command line, so it never exits; stop such loops by PID after
     reading them.
   - Check that every environment override is restored and the dev stack
     is healthy.
7. **Live review, per job:** one reviewer exercises every item's flows
   while the next job builds. Where the app has a production mode, it uses
   a production build of the job's last commit, served from a pinned
   worktree on its own port. A job that touches must-be-correct code
   (guards for unsaved work, deletes, data safety) gets the strongest
   reviewer model.
8. **Fix policy:** each job gets one fix round.
   - P0–P2 findings in app code are fixed when real use can reach them.
   - **Weigh likelihood before every fix round.** Before a finding goes to
     a builder, the orchestrator finds out how often its trigger occurs:
     it checks the real data for the input the failure needs (a scan of the
     stored files or rows is usually minutes), or names the normal use
     that produces it. A finding that no real input or normal use reaches,
     and that loses no data, goes to the Report as a known limit, whatever
     its severity label. A review round spent on an input that never
     occurs costs as much as one spent on a real bug.
   - A second round happens only for a P0–P2 in the first round's own fix,
     checked with one diff review.
   - P3 findings and test-helper limits go to the tracker's minor list.
   - By a third round, the findings on fixes are usually narrow edge cases;
     record them for the Report instead.
   - A P0 or P1 on code that later jobs build on stops the line: fix it
     before the next job that depends on it starts.
9. **Minor-bug pass:** after the last job, the orchestrator triages the
   minor list.
   - **Fix:** what users would hit in daily use (on the device they mostly
     use) and what breaks something (a failing suite, a wrong doc).
   - **Leave:** everything else goes into the Report, one line each.
   - **How it runs:** it is a build job like the others. The orchestrator
     writes it as groups of fixes, each with its evidence. Each group gets
     its own commit and a diff review, and the pass gets one live review.
10. **Finish:**
    - Write the Report into the brief:
      - one line per item: its commits (fix commits too), what changed, the
        test and review results;
      - then the checks the user should make on a real device, the timings
        against the previous run, the decisions taken for the user and the
        known minor issues.
    - Stop the heartbeat and the inhibitor, remove the worktrees, and
      record the lessons.

**Slots:** one builder runs on the main tree. Beside it runs at most one
other agent that drives a browser or simulator, either a pre-flight or a
live review. Read-only diff reviews run freely. Pre-flights and live
reviews take 20–50 minutes each and stay off the critical path.

`prompts.md` holds the prompt skeleton for each role.

## Safety rules for every agent

- **Real data:** ask the user whether the dev environment's data is
  disposable, and record the answer in the brief.
  - **Disposable:** builders and live reviewers may write to it during
    checks.
  - **Not disposable:** verification writes go only through a
    write-rejecting stub, through request interception that fails closed,
    or through clearly named fixtures that are removed afterwards.
    - A write-rejecting stub fails every non-GET request and never forwards
      it. On its own it can't show success states (a save, a toggle that
      persists, an undo). An opt-in mode that applies writes in memory to
      the stub's own synthetic fixtures, never forwarding any, makes them
      visible. Have the stub count forwarded writes, and require zero.
    - Interception matches by method, answers synchronously, and never
      holds a non-GET request. Probe it before every click that writes, and
      compare a read-only database snapshot before and after.
  - **Either way:**
    - never enter values in settings or forms that save on change, since
      they change how the app runs;
    - back up before a migration or a bulk write;
    - run DB-backed tests on a scratch database, behind a name guard;
    - tell live reviewers exactly which keys and controls write. A key
      that resets zoom in one view can set a rating in another.
- **Read-only roles stay read-only.** Planners, pre-flight checkers and
  diff reviewers never write. A "quick check" POST is a write, and so is a
  query-plan command that executes its statement (SQL `EXPLAIN ANALYZE`).
- **Live dev stack:**
  - Never run a build that cleans the output directory a running dev
    server is serving from.
  - Restore any backend URL or other override that was pointed at a stub.
- **Servers:** start long-lived servers detached from the agent's shell, and
  stop each by its own PID (the one listening on its port, after checking
  its working directory). Never kill a parent PID, a process group or
  anything matched by name: a parent can be the orchestrator's session.
- **Heavy processes:** an agent that starts a browser, simulator,
  emulator, dev server, container or stub stops it when its check is done.
  After every job, the orchestrator sweeps for what the job left behind.
  Size parallelism to the machine.
- **Test runners:** most start one worker per core by default. Next to a
  dev stack and a browser, that can freeze the machine and time tests out.
  Every agent caps the worker count (two is a safe start) and runs tests at
  lower priority (`nice`). Never run two heavy jobs at once, such as a full
  suite and a production build.
- **Permissions:** agents never add permission-bypass flags to the tools
  they launch. Name each launch exactly in the prompt; a builder left to
  improvise its reviewer launch reached for one.
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
3. **Relaunch as a continuation.** Use the same prompt. The committed items
   stand. Add a hand-over section with the `git status`, and tell the job to
   treat any uncommitted diff as its own draft for the first item without a
   commit.
4. **A second death** skips the remaining items of the job and the items
   that build on them. Save the partial diff as a patch next to the tracker,
   restore a clean tree, record why in the Report, and continue with the
   independent jobs.

## Common mistakes

| Mistake | Fix |
|---|---|
| One item per job, with the orchestrator committing | Batch related items into a job, and let the builder commit each item. |
| A dedicated fix job after every review | Send diff-review findings to the running builder, and fold live-review findings into the next job. |
| Re-reviewing fixes of fixes until clean | One fix round per job, a second only for a serious finding in that fix, and the rest to the Report. |
| Sending every P1 or P2 back for a fix by its label alone | Check how often real data or normal use reaches its trigger first; record an unreachable one that loses no data as a known limit. |
| Fixing every minor finding inside its job | Collect them for one minor-bug pass at the end, triaged by daily-use impact. |
| Browser suites re-run after every change | Affected specs while working, every touched suite once at the end of the job. |
| Building several jobs at once on one stack | Run builders serially. Parallelise pre-flights and reviews. |
| Nested reviews: internal diff reviewers, re-review rounds, reviewers spawning agents | One internal live review per job, and one pass per external reviewer. |
| Every job at the highest reasoning effort | Pick the effort per job. |
| Telling agents to hurry | State the scope and the quality bar. |
| A builder rejecting a finding by citing the plan | It lists the finding under Disputed, and the orchestrator settles it. |
| Only a diff review | Add the live reviewer, which finds the user-visible bugs. |
| A live review on a second dev server | Serve a production build from the pinned worktree. |
| Default test-runner parallelism on a shared machine | Cap the workers and lower the priority. |
| Leaving a builder to choose how it launches its reviewer | Name the launch; never allow permission-bypass flags. |
| Agents leave browsers, servers or wait loops running after their checks | Make stopping them part of every agent's finish, and sweep after each job. |
| Settling questions for the user inside the build | Surface them at pre-flight. |
