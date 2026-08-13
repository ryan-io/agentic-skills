#!/bin/sh
# Copy agentic-skills content from this submodule into the consuming project root.
# Called by the superproject's git hooks after `git submodule update`; see
# hooks/git-hooks/ for ready-made hook files and the README for wiring.
#
#   sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path> [project-root]
#
# Semantics:
# - Exports the pinned submodule commit (never a dirty working tree).
# - Overwrites only files this repo ships under .github/ and .claude/.
# - Seeds CLAUDE.md and .github/copilot-instructions.md only when absent; a
#   project's own copies are never overwritten.
# - Deletes nothing: project-own files under .github/ and .claude/ survive.
#   Give project-specific additions distinct names to avoid collisions.
# - Synced files are edited in the central repo, never in a project.
#
# Portability: uses only POSIX sh, git, and tar flags common to GNU tar and
# bsdtar, so it behaves the same under Git for Windows, WSL, and macOS.

set -e
SUB="${1:?usage: sync-agentic-skills.sh <submodule-path> [project-root]}"
ROOT="${2:-.}"

# Owned trees: overwrite in place (entry point excluded; it is seed-once below).
git -C "$SUB" archive HEAD .github .claude \
    | tar -x -C "$ROOT" --exclude='.github/copilot-instructions.md'

# Entry points: seed only when absent; never overwrite a project's own copy.
[ -f "$ROOT/CLAUDE.md" ] \
    || git -C "$SUB" archive HEAD CLAUDE.md | tar -x -C "$ROOT"
[ -f "$ROOT/.github/copilot-instructions.md" ] \
    || git -C "$SUB" archive HEAD .github/copilot-instructions.md | tar -x -C "$ROOT"

echo "agentic-skills: synced from $SUB into $ROOT (commit any changes)"
