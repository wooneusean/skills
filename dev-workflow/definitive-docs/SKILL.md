---
name: definitive-docs
description: Write and repair documentation, code comments, READMEs, and CLAUDE.md/AGENTS.md files so they state what is true rather than narrating how they got edited. Use this skill whenever creating or modifying any doc file, comment, docstring, README, changelog-adjacent prose, or agent instruction file — and especially when a doc contains change narration ("X should be Y because...", "now uses...", "based on a search of..."), hedging ("this probably handles..."), or rot-prone temporal words ("currently", "the new API"). Also use when the user asks to clean up, tighten, "definitize", de-hedge, or remove AI-generated cruft from docs. Apply it opportunistically (boy-scout style) to any doc file already being touched for another reason, not just when cleanup is the explicit request.
---

# Definitive Docs

Documentation describes **the present state of the system**. It does not describe the history of the document, the process that produced it, or the conversation that prompted the edit.

An agent editing docs mid-conversation has a lot of context in its head — the old value, the search it just ran, the user's correction — and leaks that context into the prose. The result reads like a diff comment stapled into a reference manual:

> The timeout should be 30s instead of 10s, because based on a search of the gateway config, the upstream drops connections at 35s.

A reader opening this file for the first time has never seen `10s`, did not watch that search happen, and gains nothing from either. The definitive form:

> Timeout is 30s. The upstream gateway drops connections at 35s.

The rationale survives because it points at a durable property of the system. The narration dies because it pointed at an editing episode.

## The two tests

Apply both to every sentence written or reviewed.

**Fresh-reader test** — Read it as someone who has never seen the previous version of the file, the conversation, or the commit that produced it. Does it reference something they cannot see? A prior value, a search you ran, a decision "we" made, a question they asked? If so, it is broken.

**Twelve-month test** — Will this still be true a year from now with no edits? "Currently uses Postgres 14" rots. "Requires Postgres 14 or later" does not. Anchor to versions, dates, and thresholds rather than to the moment of writing.

## What to fix

### Change narration
The most common failure. Prose that describes a delta between the current state and some previous state the reader has no access to.

| Instead of | Write |
|---|---|
| The default should be 5, not 3 | Default: 5 |
| Now uses the v2 endpoint instead of v1 | Calls `POST /v2/sessions` |
| This was updated to accept a list | Accepts a list of IDs |
| No longer requires an API key | Authentication: none |
| We switched to structured logging | Logs are JSON, one object per line |

Delta language belongs in commit messages, changelogs, and migration guides — files whose entire purpose is history. Not in reference docs.

### Research narration
Prose that reports how the fact was established rather than the fact.

| Instead of | Write |
|---|---|
| Based on a grep of the handlers, retries are capped at 3 | Retries are capped at 3 |
| After checking the docs, the correct flag appears to be `--strict` | Use `--strict` |
| Per your clarification, batches are processed in order | Batches are processed in order |

The provenance is real work and it matters — while you are doing it. It has no place in the artifact. Put it in your response to the user, or in the commit message, and let the doc assert the finding.

### Hedging
Docs assert. A hedged doc transfers your uncertainty to every future reader, who is worse equipped to resolve it than you are.

Critically: **the fix for hedging is not to delete the hedge word.** "I believe this uses Redis" → "Uses Redis" converts an honest doubt into a confident falsehood. Instead, pick one:

1. **Verify, then assert.** Read the code, run the thing, check the config. Then state it flatly. This is almost always the right move and usually takes seconds.
2. **Delete the claim.** If it cannot be verified cheaply and is not load-bearing, an absent sentence beats a wrong one.
3. **Attribute the limit precisely.** If the uncertainty is a real property of the system rather than of your knowledge, say what the system actually guarantees: "Ordering within a partition is guaranteed; across partitions it is not." That is definitive.

Never convert uncertainty into confident prose without doing (1).

### Temporal rot
Words that were true at the instant of writing: `currently`, `recently`, `newly`, `for now`, `at present`, `the new X`, `latest`, `going forward`, `soon`, `temporarily`.

| Instead of | Write |
|---|---|
| Currently supports three providers | Supports AWS, GCP, and Azure |
| The new caching layer | The Redis caching layer |
| Recently added `--dry-run` | `--dry-run` prints the plan without applying it |
| Temporarily pinned to 1.4 | Pinned to 1.4 pending the fix in [#812](...) |

Note the last one: when a state genuinely is temporary, the definitive form names the condition that ends it, so a future reader can check whether it has.

### Conversational residue
`As requested`, `you asked for`, `let me know if`, `hope this helps`, `as we discussed`, `feel free to`. A doc has no interlocutor. Delete these outright.

### Document self-reference
`This section was added to clarify...`, `Fixed a bug where...`, `The earlier version of this doc said...`, `Expanded per review feedback`. The document does not narrate its own maintenance. Version control does that.

### Deferred uncertainty
A bare `TODO: verify this is still accurate` is hedging with extra steps — it announces that the doc may be lying and assigns the problem to nobody. Either verify it now, delete the claim, or make the TODO actionable with an owner and a link: `TODO(@dana): confirm against the 3.0 schema — #1204`.

## What to leave alone

Over-application is the failure mode of this skill. Be genuinely conservative here.

**Durable rationale.** "Batch size is 500 because the API rejects payloads above 1MB" is not change narration — the `because` points at an enduring constraint. Keep every one of these. When a doc explains *why* in terms of a fact that is still true, that explanation is often the most valuable line in the file. The distinction is not "does it say because," it is **does the reason point at the system or at the edit.**

**Real deprecation notices.** These are load-bearing; readers need them. Just state them as facts rather than events: not "we recently deprecated `parse()`" but "Deprecated since 2.4. Use `parseStrict()`."

**Genuinely dated facts** where the date is the content: "Security patches through April 2027", "Requires Node 20+". Dates and versions are anchors, not rot.

**Files whose purpose is history.** Do not "definitize" these — you would be destroying their reason for existing:

- `CHANGELOG.md`, `HISTORY.md`, `NEWS`, `RELEASE_NOTES*`
- Migration and upgrade guides (`UPGRADING.md`, `docs/migration/*`)
- Architecture decision records (`docs/adr/*`, `docs/decisions/*`) — an ADR is *supposed* to say "we chose X over Y because Z, rejecting W"
- Post-mortems, retrospectives, RFCs, design docs with an explicit history section
- Commit messages and PR descriptions

**Prose that only looks like a violation.** "The parser should reject empty input" is a specification, not a hedge. "New connections are pooled" uses `new` as a domain term. Read for meaning before rewriting.

## Boy-scout cleanup

When touching a doc file for any reason, clean the definitiveness violations you encounter — but keep the blast radius proportionate to the errand.

**Scope rules:**
- Always clean the sections you are already editing.
- In a file under ~200 lines, clean the whole file.
- In a larger file, clean the sections you touched plus any egregious cases nearby. Do not silently rewrite 400 lines because you fixed a typo — a diff that big stops getting reviewed, and unreviewed doc rewrites are how errors get laundered into the record.
- Never expand into other files unless asked.

**Report, don't hide.** After cleanup, tell the user plainly: what you fixed, and what you found but left (out-of-scope files, claims you could not verify, cases where you were unsure whether a `because` was durable). If cleanup makes the diff noticeably larger than the requested change, offer to split it into a separate commit so the substantive change stays reviewable.

**When you cannot verify, ask rather than guess.** If a doc says "this probably retries on 502" and confirming means reading code you do not have, surface it: "line 44 hedges on retry behavior — I couldn't confirm it; want me to check the handler, or drop the claim?" Guessing here writes falsehoods with full confidence, which is strictly worse than the hedge you replaced.

## CLAUDE.md and agent instruction files

These files drift worst, because they accumulate as sediment across sessions. Same principles, plus:

- **Imperative present tense.** Not "the user prefers tabs" or "we decided to use pnpm" — write "Use tabs." "Use pnpm; do not run npm install."
- **No session memory.** `Remember that last time we...`, `The user corrected me about...`, `As established earlier...` — all of it goes. Every instruction reads as a standing rule with no backstory.
- **No transcript of superseded rules.** When a rule changes, replace it. Leaving "previously we used X, now use Y" gives a future agent two instructions and a puzzle.
- **Instructions, not autobiography.** If a line does not tell the agent what to do or state a fact about the repo, it is not earning its context window.

## Scanning an existing tree

`scripts/scan_docs.py` greps for the patterns above and prints candidates grouped by file and category. It skips history files and fenced code blocks by default. Check this skill's folder for the script, if it doesn't exist, skip this step but let the user know that it doesn't exist.

```bash
python scripts/scan_docs.py docs/ CLAUDE.md README.md
python scripts/scan_docs.py . --category hedging,change_narration
python scripts/scan_docs.py . --include-source   # also scan comments in code files
python scripts/scan_docs.py . --format json
```

Exit code is 1 when candidates are found and 0 when clean, so it can gate a pre-commit hook — though as an advisory check, since false positives are expected.

It is a **candidate finder, not an authority.** It cannot tell durable rationale from change narration, and it will flag legitimate prose. Every hit needs the two tests applied by hand. Use it to find work, never to decide what to rewrite — and never bulk-apply regex substitutions to its output.
