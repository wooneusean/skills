# Skills

A curated library of AI skills — reusable prompt templates and instructions for automating common tasks with Claude Code and other AI tools.

## Structure

```
skills/
├── decision-making/  # Multi-perspective analysis and decision frameworks
├── dev-workflow/     # General software development workflow skills
├── data/             # Data science and analysis skills
├── learning/         # Teaching, tutoring, and knowledge-building skills
└── templates/        # Authoring templates for new skills
```

## What is a skill?

A skill is a markdown file containing a structured prompt or instruction set that can be invoked in an AI session to perform a well-defined task. Skills are designed to be reusable, composable, and easy to share.

## Installation

Clone the repo and run the install script to package all skills and install them to `~/.claude/skills/`:

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

Skills are stored as plain markdown in this repo and packaged into the `.skill` format that Claude Code expects during installation.

## Using skills

Once installed, skills are available in Claude Code sessions. Trigger them by saying the phrases described in each skill's `description` frontmatter field.

## Adding a new skill

1. Choose the appropriate category directory (or create one if none fits)
2. Copy `templates/skill-template.md` as your starting point
3. Fill in the metadata and prompt body
4. Test the skill in a Claude Code session before committing

## Categories

| Directory | Purpose |
|---|---|
| `decision-making/` | Multi-perspective analysis and decision frameworks |
| `dev-workflow/` | Code review, debugging, refactoring, and general dev tasks |
| `data/` | Data exploration, analysis, and visualization tasks |
| `learning/` | Teaching, tutoring, and knowledge-building skills |
| `templates/` | Boilerplate for authoring new skills |
