# Skills

A curated library of AI skills — reusable prompt templates and instructions for automating common tasks with Claude Code and other AI tools.

## Skill index

| Skill | Category | What it does |
|---|---|---|
| [`definitive-docs`](dev-workflow/definitive-docs/SKILL.md) | dev-workflow | Writes and repairs docs, comments, and CLAUDE.md files so they state what is true rather than narrating edits. Ships a scanner that finds candidate hedging and change narration. |
| [`git-commit`](dev-workflow/git-commit.md) | dev-workflow | Generates a Conventional Commits message from staged changes and creates the commit. |
| [`handoff-doc`](dev-workflow/handoff-doc.md) | dev-workflow | Writes a `handoff.md` capturing session state so the next session resumes without repeating dead ends. |
| [`phased-implementation`](dev-workflow/phased-implementation.md) | dev-workflow | Breaks a large change into phases that each end with the repository working, tracking deferred work in a plan file. |
| [`llm-council`](decision-making/llm-council.md) | decision-making | Runs a high-stakes decision past five AI advisors who analyze it from different angles, peer-review each other, and synthesize a verdict. |
| [`socratic-teacher`](learning/socratic-teacher.md) | learning | Teaches a topic through one guiding question per turn, never giving the full solution. |

## What is a skill?

A skill is a markdown file containing a structured prompt or instruction set that can be invoked in an AI session to perform a well-defined task. Skills are reusable, composable, and easy to share.

A skill takes one of two layouts:

- **Flat** — `<category>/<skill-name>.md`, for a skill that is only a prompt.
- **Bundle** — `<category>/<skill-name>/SKILL.md` plus supporting files, for a skill that ships scripts or references. The whole directory is installed, so those files travel with the skill.

## Structure

```
skills/
├── decision-making/  # Multi-perspective analysis and decision frameworks
├── dev-workflow/     # General software development workflow skills
├── learning/         # Teaching, tutoring, and knowledge-building skills
└── templates/        # Authoring templates for new skills
```

## Installation

Clone the repo and run the install script to install all skills to `~/.claude/skills/`:

```bash
git clone git@github.com:wooneusean/skills.git
cd skills
chmod +x install.sh
./install.sh
```

To update after pulling new changes:

```bash
git pull
./install.sh
```

Each skill is installed as `~/.claude/skills/<skill-name>/SKILL.md`, the layout Claude Code discovers. Installing a bundle replaces any existing directory of that name, so removed supporting files do not linger.

## Using skills

Once installed, skills are available in Claude Code sessions. Trigger them by saying the phrases described in each skill's `description` frontmatter field.

## Adding a new skill

1. Choose the appropriate category directory (or create one if none fits)
2. Copy `templates/skill-template.md` as your starting point
3. Fill in the metadata and prompt body
4. Add a row to the [skill index](#skill-index)
5. Test the skill in a Claude Code session before committing

## Categories

| Directory | Purpose |
|---|---|
| `decision-making/` | Multi-perspective analysis and decision frameworks |
| `dev-workflow/` | Code review, debugging, refactoring, and general dev tasks |
| `learning/` | Teaching, tutoring, and knowledge-building skills |
| `templates/` | Boilerplate for authoring new skills |
