---
name: phased-implementation
description: >-
  Implement large or multi-step changes as a sequence of phases, where every
  phase ends with the repository in a stable, working state and all deferred
  work is explicitly marked and tracked in a plan file. Use this skill whenever
  a task is too large to complete in one sitting, involves a migration,
  refactor, rewrite, or new feature touching multiple files or layers, or
  whenever the user mentions phases, milestones, increments, "step by step",
  "don't break anything", stopping points, or resuming earlier work. Also use
  it when picking up a codebase that contains a plan file or deferred-work
  markers (TODO(slug), MOCK(slug), STUB(slug)) from previous sessions.
---

# Phased Implementation

Break large changes into phases. The contract is simple:

> **Work can stop after any completed phase and the repository is not broken,
> not misleading, and not hiding unfinished work.**

Two rules enforce this contract:

1. **Stable state** — every phase ends with the repo building, tests passing,
   and the app runnable.
2. **Nothing swept under the rug** — every piece of deferred, mocked, or
   stubbed work carries a greppable marker AND an entry in the plan file.

If interrupted mid-phase, whatever exists is still governed by rule 2: mark it
before stopping, even if the phase is unfinished.

## When to phase (and when not to)

Phase when the task spans multiple files/layers, involves a migration or
refactor, can't be finished in one session, or the user asks for incremental
delivery. Do NOT add this ceremony to small tasks — a bug fix or a
single-function change is just done directly. If in doubt: would a second
engineer benefit from a written plan to resume this? If no, skip the process.

## Workflow

### 1. Plan before code

Before writing code, produce a phase plan and write it to a plan file in the
repo (see "The plan file" below). Get user approval on the plan for anything
non-trivial before starting phase 1.

Phase design rules:

- **Phase 1 is a walking skeleton**: the thinnest end-to-end slice that
  compiles, runs, and is exercised by at least one test. Not "half of
  everything" — all of a small thing.
- **Vertical slices over horizontal layers.** "User can create an account
  (no email verification yet)" is a phase. "All the DTOs" is not — a layer
  with no consumer is dead weight that can't be validated.
- **Each phase has an explicit exit condition** written in the plan, e.g.
  "old and new code paths both pass the integration suite with the flag off."
- **Order phases so risk lands early**: unknowns, integrations, and schema
  changes first; polish last.

### 2. Execute one phase at a time

Work strictly within the current phase. Do not write code for phase 3 while
in phase 1 — if you discover phase-3 work is needed now, either move it into
the current phase explicitly (update the plan) or leave a marker.

For changes that replace existing behavior, prefer **expand / migrate /
contract**:

- **Expand**: add the new path alongside the old (new column, new endpoint,
  new implementation behind a flag). Old behavior untouched. Stable.
- **Migrate**: switch consumers over, one phase or one consumer group at a
  time. Both paths work throughout. Stable.
- **Contract**: delete the old path only when nothing references it. Stable.

This applies to schemas (never drop/rename a column in the same phase that
adds its replacement), APIs, and internal interfaces alike. Avoid big-bang
rewrites; if the user asks for one, propose a phased equivalent.

### 3. Verify the stable state before closing a phase

A phase is not done until all of these hold:

- Build/compile succeeds cleanly.
- Full existing test suite passes (not just tests you touched).
- New functionality completed in this phase has tests, and they pass.
- The application starts and runs (where feasible to check).
- No dangling imports, unreachable code, or references to things that don't
  exist yet.
- No public API introduced solely for a future phase with no current caller.
- Database migrations, if any, are applied cleanly and are
  backward-compatible with the still-deployed code paths.
- Marker audit passes (next section).
- The plan file is updated: phase marked complete, marker inventory current.

If the project has no test runner or build step, state that explicitly in the
plan file and describe what "stable" was verified to mean (e.g. "script runs
end-to-end against sample input").

One phase should map to one commit (or one PR) where the environment allows
it, with the phase name in the message. This makes every stable state a
checkpoint you can bisect or revert to.

### 4. Report

After each phase, output a phase summary (format below) so the user can
decide whether to continue, stop, or re-plan. For multi-phase runs in one
session, still pause at phase boundaries unless the user has said to proceed
straight through.

## The marking protocol

Deferred work must be findable with one grep, and every marker must be
**self-contained**: readable and actionable by someone holding only the
source file, with no plan file, no ticket, and no chat history. Plans are
temporary — they get deleted, rewritten, or never committed. Markers are the
durable record, so they never reference plan files, phase numbers, ticket
IDs, or anything else that can disappear. The dependency is one-directional:
the plan may point at markers; markers never point back.

Use exactly these markers in code comments:

- `TODO(<slug>): <context>` — logic deliberately deferred.
- `STUB(<slug>): <context>` — a placeholder function/component that exists
  so the code compiles.
- `MOCK(<slug>): <context>` — hardcoded/fake data standing in for a real
  source.
- `FIXME(<slug>): <context>` — known technical debt or a deferred edge case
  that isn't part of the planned work.

`<slug>` is a short stable topic label (`auth-oidc`, `catalog-data`,
`report-pagination`) that groups related markers so they can be picked off
together — never a phase number, since phase numbers are meaningless outside
a specific plan.

`<context>` must answer three questions on its own:

1. **What is fake/missing here?**
2. **What should the real implementation be** (or what condition unblocks
   it — "once X exists")?
3. **Why was it deferred / what's the risk of leaving it?** (when not
   obvious)

Good — survives plan deletion:

```
// MOCK(catalog-data): returns a hardcoded 12-product list from fixtures.ts.
// Replace with a CatalogService HTTP client once the catalog API is
// deployed; until then, checkout totals computed from this data are fake.
```

Bad — dead references the moment the plan is gone:

```
// TODO(phase-3): see plan
// TODO: fix this later
```

Rules:

- **No anonymous markers.** A bare `TODO: fix this` is forbidden — it is
  rug-sweeping with a label on it.
- **Stubs fail loudly.** A reachable stub must never silently return fake
  success — that is the worst form of hidden incompleteness, because
  everything appears to work. A stub is acceptable only if it is (a)
  unreachable from any live code path, or (b) throws/returns an explicit
  "not implemented" error, or (c) is gated behind a feature flag that is off
  by default. If none of those fit, don't stub — implement the minimal real
  version or cut the API from this phase.
- **Mock data must be unable to reach production silently.** Isolate it
  (separate module/fixture, injected via config or flag) and mark it. If the
  runtime supports it cheaply, log a warning when a mock path is active.
- Follow the repo's existing marker convention if one already exists and is
  greppable; keep its markers equally self-contained.

Audit before closing any phase:

```
grep -rnE "(TODO|STUB|MOCK|FIXME)\(" --include=<source globs> .
```

Every hit must appear in the plan file's marker inventory, and every marker
whose slug the current phase was supposed to resolve (per the plan) is a
bug — resolve it or re-schedule it in the plan before closing. Spot-check
that each marker still reads as self-contained.

## The plan file

The plan lives **in the repository**, not in the conversation. Chat context
dies with the session; the repo is what the next agent or engineer actually
has. Default location: `docs/plans/<feature-slug>.md` (follow repo convention
if one exists, e.g. `.plans/` or `PLAN.md` for single-effort repos).

Template:

```markdown
# Plan: <feature/change name>

Status: phase 2 of 5 complete
Last updated: <date> by <agent/human>

## Goal
One paragraph: what this change accomplishes and why.

## Phases
- [x] Phase 1 — <name>: <scope>. Exit: <condition>. (commit <sha>)
- [x] Phase 2 — <name>: <scope>. Exit: <condition>. (commit <sha>)
- [ ] Phase 3 — <name>: <scope>. Exit: <condition>.
- [ ] Phase 4 — ...

## Marker inventory
| Marker slug | Location | Resolves in |
|---|---|---|
| catalog-data | src/catalog/fixtures.ts:12 | phase 3 |
| auth-oidc | src/auth/oidc.ts:8 | phase 4 |

## Debt register
- FIXME(report-pagination) src/report/export.ts:44 — pagination ignored
  above 10k rows; acceptable for internal use, revisit if customer-facing.

## Decisions & constraints
Notable choices made along the way that a resumer needs (chosen libraries,
rejected approaches and why, flags introduced and their defaults).
```

The slug→phase mapping ("Resolves in") lives only here — the plan schedules
markers, markers never cite the plan. This makes the plan safely disposable:
delete it and the markers still carry full context; regenerate a plan later
by grepping markers and re-scheduling their slugs.

Update this file as part of closing every phase — not as an afterthought at
the end of the whole effort. If scope changes mid-effort (phases added,
merged, reordered), edit the plan and note why under Decisions.

## Resuming work

When starting in a repo that may contain in-flight phased work:

1. Run the marker grep from the audit section. Markers are the source of
   truth for deferred work.
2. Look for plan files (`docs/plans/`, `.plans/`, `PLAN.md`).
3. **If a plan exists**, reconcile it against the grep: markers not in the
   plan, or plan entries pointing at resolved markers, get fixed first — the
   ledger must be truthful before new work starts. Then continue from the
   first unchecked phase.
4. **If no plan exists (deleted, never committed, or work arrived without
   one)**, the markers alone must suffice — this is exactly why they're
   self-contained. Group them by slug, and treat each slug as a candidate
   phase: its markers describe what's missing and what the real
   implementation should be. Write a fresh plan file from that inventory
   before resuming.
5. Either way, verify the stable state (build + tests) before assuming the
   previous session actually stopped cleanly.

## Scope reduction under pressure

When the requested work is too large for the available time/context: never
start everything and finish nothing. Complete the largest prefix of phases
that fits, leave the repo stable, and ensure the plan file lets anyone resume.
A finished phase 1 of 5 with an honest plan beats 80% of everything with
nothing runnable.

## Phase summary format

At the end of every completed phase, report:

```markdown
### Phase <N> complete — <name>
**State:** builds clean, <test count> tests passing, app runs.
**Done:** <bullet summary of the increment>
**Deferred (marked in code and plan):**
- MOCK(catalog-data) src/catalog/fixtures.ts — fake catalog data, resolves
  in phase 3
**Next:** Phase <N+1> — <one-line goal>. Plan file: docs/plans/<slug>.md
```

## Success criteria

- Every completed phase is safe to ship or stop on.
- Every incomplete thing is marked in code AND inventoried in the plan file —
  the grep and the plan agree.
- No reachable code path silently pretends to work.
- A different agent, given only the repository, can resume within minutes.
- Deleting the plan file loses scheduling, not context: every marker still
  fully explains itself, and a new plan can be rebuilt from the grep alone.
