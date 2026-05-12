# Skills

A curated library of AI skills — reusable prompt templates and instructions for automating common tasks with Claude Code and other AI tools.

## Structure

```
skills/
├── claude-code/      # Skills specific to the Claude Code CLI
├── decision-making/  # Multi-perspective analysis and decision frameworks
├── dev-workflow/     # General software development workflow skills
├── data/             # Data science and analysis skills
└── templates/        # Authoring templates for new skills
```

## What is a skill?

A skill is a markdown file containing a structured prompt or instruction set that can be invoked in an AI session to perform a well-defined task. Skills are designed to be reusable, composable, and easy to share.

## Using skills

In Claude Code, skills can be invoked via slash commands if configured in your `.claude/settings.json`. See the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code) for setup instructions.

## Adding a new skill

1. Choose the appropriate category directory (or create one if none fits)
2. Copy `templates/skill-template.md` as your starting point
3. Fill in the metadata and prompt body
4. Test the skill in a Claude Code session before committing

## Categories

| Directory | Purpose |
|---|---|
| `claude-code/` | Skills that extend or automate Claude Code workflows |
| `decision-making/` | Multi-perspective analysis and decision frameworks |
| `dev-workflow/` | Code review, debugging, refactoring, and general dev tasks |
| `data/` | Data exploration, analysis, and visualization tasks |
| `templates/` | Boilerplate for authoring new skills |
