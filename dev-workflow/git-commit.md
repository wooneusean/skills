---
name: git-commit
description: "Write and create a well-formatted git commit from currently staged changes, following the Conventional Commits specification. Use whenever the user asks to commit, wants a commit message generated, or invokes /git-commit. Operates only on already-staged changes."
allowed-tools: "Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)"
---

# Git Commit

Generate a Conventional Commits-style message from staged changes and create the commit.

## Procedure

1. **Confirm there is something to commit.** Run `git diff --staged --stat`. If nothing is staged, stop and tell the user — do not run `git add`. Staging is the user's decision.
2. **Read the actual change.** Run `git diff --staged` and read it. Base the message on what the diff does, not on file names alone.
3. **Match the repo's convention.** Run `git log --oneline -15` and follow the existing style (scope names, casing, whether bodies are used).
4. **Compose the message** per the format below.
5. **Commit.** Use `git commit -m "<subject>" -m "<body>"` — separate `-m` flags preserve the blank line between subject and body. Do not push.

Never amend, rebase, stage, or push unless the user explicitly asks.

## Message format

```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type** (required) — one of the types below.
- **scope** (optional) — the affected area, e.g. `auth`, `api`, `deps`.
- **subject** (required) — imperative mood ("add", not "added"/"adds"), lowercase, no trailing period, ≤ 50 characters.
- **body** (optional) — explain *what* changed and *why*, not *how*. Wrap at 72 columns; use bullets for multiple distinct changes. Include it when the subject isn't self-explanatory.
- **footer** (optional) — issue references (`Closes #123`) and breaking-change notes.

## Types

| Type | Use for |
|------|---------|
| feat | A new feature |
| fix | A bug fix |
| docs | Documentation only |
| style | Formatting/whitespace, no behavior change |
| refactor | Code change that neither fixes a bug nor adds a feature |
| perf | A performance improvement |
| test | Adding or correcting tests |
| build | Build system or dependency changes |
| ci | CI configuration and scripts |
| chore | Maintenance that doesn't touch src or tests |
| revert | Reverting a previous commit |

## Breaking changes

Signal a breaking change with either (or both):

- A `!` after the type/scope — `feat(api)!: drop support for v1 tokens`
- A footer — `BREAKING CHANGE: <what broke and the migration path>`

## Guidance

- One logical change per commit. If the staged diff spans unrelated concerns, say so and suggest splitting it rather than writing a vague catch-all subject.
- Pick the most specific accurate type: `perf` over `refactor` for a speedup, `fix` over `chore` when behavior actually changed.
- The subject should make sense without the diff open.

## Example

```
feat(auth): add password reset flow

- Add forgot-password form and validation
- Send verification email via the notifications service
- Expose POST /auth/reset endpoint

Closes #214
```
