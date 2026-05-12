#!/usr/bin/env bash
# Installs all skills to ~/.claude/skills/ as <skill-name>/SKILL.md directories

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SKILLS_DIR"

find "$REPO_DIR" -name "*.md" \
  ! -path "*/templates/*" \
  ! -name "README.md" | while read -r md_file; do

  skill_name="$(basename "$md_file" .md)"
  dest_dir="$SKILLS_DIR/$skill_name"

  mkdir -p "$dest_dir"
  cp "$md_file" "$dest_dir/SKILL.md"

  echo "  installed: $skill_name"
done

echo "Done. Skills installed to $SKILLS_DIR"
