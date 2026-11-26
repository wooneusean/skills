---
name: fresh-eyes-review
description: The fresh-eyes review every MR or PR gets before it merges, from a model that didn't write the change. Pick ONE reviewer tier (a standard reviewer by default, a deep one for complex or crucial changes), write a review prompt built on concrete inputs, run it read-only, triage the findings by how likely they are in real use, and send the fixes back for about two rounds. Use this whenever a branch, MR or PR is ready for review or about to merge, when the user asks for a second-opinion or cross-model review, when a review's findings come back and need sorting, or when deciding whether another round is worth it, even if the user only says "review it", "get it reviewed" or "is it ready to merge".
---

# Fresh-eyes review

The author of a change, whether you or a builder you spawned, reads it through the reasoning that produced it and misses what that reasoning missed. A reviewer that didn't write the change reads it cold. Every MR or PR gets one such review before it merges.

Two rules keep this from eating the day:

- **One tier per MR.** Stacking several reviewers on one MR turns a review into hours.
- **Triage by likelihood.** A reviewer can construct a failure for almost any code. Chasing every one turns two rounds into five.

## 1. Pick the tier

| Change | Reviewer |
|---|---|
| Default, including any few-line change | **Standard:** a fast, capable model, ideally from a different provider or model family than the author |
| Complex or crucial: permission and notification logic, who gets mentioned or pinged, data migrations, shared contracts and grammars, races, procedures run against production | **Deep:** the strongest model available, at high reasoning effort |

- **Ask the user once which model fills each tier**, and keep the answer for the session. With a single provider, a fresh-context instance of the same model still works: it carries none of the author's reasoning.
- **Mind the deep tier's budget.** When it draws on a plan whose usage limit is running low, use the deep tier from another provider instead, or the standard tier at high effort. Read usage from the tool when it exposes it; Claude Code, for example, passes `rate_limits` to a status-line command, which can save it to a file for agents to read. Otherwise ask the user.
- **Decide by complexity and how crucial it is to get right**, never by repository. A few-line change in a large codebase gets the standard tier.
- **Reviewers only review.** They never edit, build, commit or push.
- **Name the tier and why** in the status you give the user.

## 2. Write the prompt

Save it as a file, e.g. `prompts/<lane>-r<round>.txt`, so a later round can cite it:

```text
Review branch <branch> in <worktree> against origin/main (`git diff
origin/main...HEAD`; MR <ref>). Read-only: change no files, start no servers,
make no network calls, never run tools that touch production. Reading code and
running at most a few single targeted test files is fine; no builds, no whole
suites.

Context: <what the product does here, in three or four lines, and the settled
rule the change implements; point at the plan's decisions if there is one>.
- <each commit's behaviour change, one bullet each>

Check, with concrete inputs:
- <each behaviour that must hold, phrased so a concrete input could break it>
- <coupling risks: old and new code side by side, shared contracts, every
  consumer of a changed export>
- <data safety, if anything writes, deletes or migrates>
- the tests are deterministic (no fixed delays) and prove what their names say.
Classify findings as (a) a likely regression, data-safety problem or wrong
<mention | push | write> with a concrete input, or (b) an edge case. Say
plainly if (a) is empty.
```

- **Concrete inputs.** "Check correctness" gets vague answers; "a name two roles share stays typed" gets a probe.
- **Settled decisions are context, not review targets.** Say what was decided, so the reviewer checks the change against it instead of reopening it.
- **Runbooks and procedures get the same treatment.** For an MR description that someone will follow against production, ask the reviewer to check every command, path and expected output against the code, the order of steps, and every partial state a rollback can start from.
- **A later round reviews only the fix commits** (`git diff <old>..<new>`). Name the findings they answer, and ask whether each is fixed and whether the fix adds a problem.

## 3. Run it

- **Read-only, from the worktree under review,** with network access and tool servers off.
- **As a subagent** of your own harness: tell it, "You are a code reviewer. Read <prompt file> and do exactly what it says. You review only: never edit, commit, push or build, never start servers, never run tools that touch production. Your final message is the review; also save it to <reviews dir>/<name>.md." For round 2, continue the same agent so it keeps its probes and context.
- **As an external CLI**, through a runner script that takes the prompt file and writes the review, the log and the exit code to an output directory. The `orchestrated-agent-run` skill's `roles.md` has the runner contract and example invocations. With Codex, for example:

  ```bash
  codex exec -m <model> -s read-only -C <worktree> -o <out-dir>/<name>.md \
    "$(cat <prompt-file>)" </dev/null > <out-dir>/<name>.log 2>&1
  echo "exit $?" > <out-dir>/<name>.exit
  ```

- **Keep the output beside the work, never inside the worktree under review,** for example a `reviews/` folder next to the prompts. Read the exit code before trusting the review.
- **Run it in the background** through the harness, so its completion wakes you.
- **GUI work:** give the reviewer a headless browser and screenshots against a running build of the branch.
- **Sandboxes that can't create temp directories** fail tests that need one before any assertion runs. Take the builder's own pasted test output as the proof instead.

## 4. Triage

Sort every finding by how likely it is in real use, not by whether the reviewer could construct it.

- **Fix:**
  - regressions against main;
  - data-safety problems that real traffic can hit;
  - wrong behaviour that ordinary use reaches, such as the wrong person pinged, a lost write, or a misleading count;
  - a cheap guard against losing data, even when the path is unusual.
- **Skip:**
  - cases that need contrived input or several unlikely events at once;
  - pre-existing behaviour on main, unless the fix is trivial and in scope.

  Say which findings you skipped and why.
- **File, don't fold.** A real bug next door becomes its own task, not part of this MR. Every added line gives the next round new surface.

Send the builder only the findings that pass:

```text
Review of <branch> (<sha>): <n> findings to fix, each as its own commit on top
(no rebase or force-push once pushed), each with a regression test that fails
without the fix (show break-the-fix).

1. <title>. Where: `<path:line>`. Failure: <input and what goes wrong>.
   Fix: <the fix or its options>.

Skipped: <finding> (<why>).
Rerun the gates the fixes touch, push, and send me the new head.
```

## 5. Rounds and merge

- **About two rounds per MR.** The second covers only the fix commits.
- **A third round needs a real, likely problem behind it.** If round 2 brings back only edge cases, or only cases round 1 already skipped, the MR is done.
- **Merge when the last round's (a) is empty,** or holds only findings you consciously skipped, and the pipeline is green.
- **When main has moved,** merge main into the branch. Never force-push a branch under review.
