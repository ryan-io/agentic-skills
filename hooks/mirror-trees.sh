#!/bin/sh
# Mirror the source trees into their Claude Code counterparts inside THIS repo.
# .github/skills -> .claude/skills ; .github/instructions -> .claude/rules
# Run after editing any skill or instruction file, before committing:
#   sh hooks/mirror-trees.sh [--check]
# --check exits 1 if the mirrors differ instead of copying. Agents are not
# mirrored (per-ecosystem frontmatter). POSIX sh only.
set -e
cd "$(dirname "$0")/.."
status=0
sync_tree() {
    src="$1"; dst="$2"
    if [ "$CHECK" = 1 ]; then
        diff -r --exclude=__pycache__ "$src" "$dst" >/dev/null 2>&1 || { echo "DRIFT: $src vs $dst"; status=1; }
    else
        mkdir -p "$dst"
        (cd "$src" && find . -type f ! -path '*/__pycache__/*' -print) | while IFS= read -r f; do
            mkdir -p "$dst/$(dirname "$f")"
            cp "$src/$f" "$dst/$f"
        done
        echo "mirrored $src -> $dst"
    fi
}
[ "$1" = "--check" ] && CHECK=1
sync_tree .github/skills .claude/skills
sync_tree .github/instructions .claude/rules
exit $status
