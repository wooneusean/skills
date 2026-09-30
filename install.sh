#!/usr/bin/env bash
# Installs all skills to ~/.claude/skills/ as <skill-name>/SKILL.md directories

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SKILLS_DIR"

# Bundle skills: <category>/<skill-name>/SKILL.md alongside supporting files.
# The whole directory is copied, so scripts and references travel with the skill.
find "$REPO_DIR" -name "SKILL.md" \
  ! -path "*/.git/*" | while read -r skill_md; do

  src_dir="$(dirname "$skill_md")"
  skill_name="$(basename "$src_dir")"
  dest_dir="$SKILLS_DIR/$skill_name"

  rm -rf "$dest_dir"
  cp -R "$src_dir" "$dest_dir"

  echo "  installed: $skill_name (bundle)"
done

# True when the file sits inside a bundle directory (an ancestor holds SKILL.md).
in_bundle() {
  local dir
  dir="$(dirname "$1")"
  while [ "$dir" != "$REPO_DIR" ] && [ "$dir" != "/" ]; do
    [ -f "$dir/SKILL.md" ] && return 0
    dir="$(dirname "$dir")"
  done
  return 1
}

# Flat skills: <category>/<skill-name>.md
# Markdown inside a bundle (references, templates) belongs to that bundle.
find "$REPO_DIR" -name "*.md" \
  ! -path "*/templates/*" \
  ! -path "*/.git/*" \
  ! -name "SKILL.md" \
  ! -name "README.md" \
  ! -name "CLAUDE.md" | while read -r md_file; do

  in_bundle "$md_file" && continue

  skill_name="$(basename "$md_file" .md)"
  dest_dir="$SKILLS_DIR/$skill_name"

  mkdir -p "$dest_dir"
  cp "$md_file" "$dest_dir/SKILL.md"

  echo "  installed: $skill_name"
done

echo "Done. Skills installed to $SKILLS_DIR"
