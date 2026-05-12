#!/usr/bin/env bash
# Packages all skill markdown files and installs them to ~/.claude/skills/

set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="$(mktemp -d)"

mkdir -p "$SKILLS_DIR"

installed=0

find "$REPO_DIR" -name "*.md" \
  ! -path "*/templates/*" \
  ! -name "README.md" | while read -r md_file; do

  skill_name="$(basename "$md_file" .md)"
  skill_file="$SKILLS_DIR/${skill_name}.skill"

  # Package as skillname/SKILL.md inside the zip (remove first for a clean replace)
  mkdir -p "$TMP_DIR/$skill_name"
  cp "$md_file" "$TMP_DIR/$skill_name/SKILL.md"
  rm -f "$skill_file"
  (cd "$TMP_DIR" && zip -q "${skill_file}" "${skill_name}/SKILL.md")
  rm -rf "$TMP_DIR/$skill_name"

  echo "  installed: ${skill_name}.skill"
  installed=$((installed + 1))
done

rm -rf "$TMP_DIR"
echo "Done. Skills installed to $SKILLS_DIR"
