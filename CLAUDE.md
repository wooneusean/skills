# CLAUDE.md

This repository is a library of AI skills. Each skill is a markdown prompt with YAML frontmatter, stored under a category directory and installed to `~/.claude/skills/` by `install.sh`.

## Skill layout

A skill takes one of two forms:

- **Flat** — `<category>/<skill-name>.md`. Use this when the skill is only a prompt.
- **Bundle** — `<category>/<skill-name>/SKILL.md` plus supporting files. Use this when the skill ships scripts or references, so those files install alongside it.

The skill name comes from the filename (flat) or the directory name (bundle). It must match the `name` field in the frontmatter.

Frontmatter requires `name` and `description`. The `description` carries the trigger phrases that decide when the skill fires, so write it to be matched against, not skimmed.

## Adding or renaming a skill

When adding, removing, or renaming a skill, update the skill index table in `README.md` in the same change. The index is the only place the full set of skills is listed; a skill missing from it is invisible.

Place the skill in the category directory that fits its purpose. Create a new category only when no existing one applies, and add it to both the structure block and the categories table in `README.md`. Do not leave a category directory empty — delete it instead.

## Editing docs

`README.md`, `CLAUDE.md`, and skill bodies describe the present state. Use the `definitive-docs` skill when writing them.

## Verifying a change

Run `./install.sh` after changing skills or the install script, and confirm every expected skill is listed in the output.
