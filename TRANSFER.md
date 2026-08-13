# Central repo transfer checklist

This sandbox repo is not the central agentic-skills repo. Use this checklist to
move the artifact set into the central repository. Delete this file after the
transfer; it is not part of the shipped set.

## What to copy

- `README.md`, `CLAUDE.md`, `.gitattributes`
- `.github/` (copilot-instructions.md, agents/, instructions/, skills/)
- `.claude/` (agents/, rules/, skills/)
- `hooks/` (sync-agentic-skills.sh, git-hooks/post-checkout, git-hooks/post-merge,
  git-hooks/post-rewrite)
- Do NOT copy: `.git/`, `.vs/`, any staging or scratch dirs, this file.

## First commit (from Windows)

1. Create `.gitignore` in the central repo with at least `.vs/` (Visual Studio
   recreates it the moment the repo is opened) plus any local scratch dirs.
2. `git add -A`
3. Mark the hook files executable in the index; a Windows commit stores them
   `100644`, and git on macOS/Linux silently skips a non-executable hook:
   `git update-index --chmod=+x hooks/git-hooks/post-checkout hooks/git-hooks/post-merge hooks/git-hooks/post-rewrite`
4. Verify: `git ls-files -s hooks/git-hooks/` shows `100755` on all three files.
5. Commit and push. The sync exports `git archive HEAD`: only committed content
   ever reaches a consumer, so uncommitted central changes never propagate.

## Smoke test (once, scratch consumer repo)

1. `git init scratch`, add any dummy commit.
2. `git submodule add <central-repo-url> tools/agentic-skills`
3. `sh tools/agentic-skills/hooks/sync-agentic-skills.sh tools/agentic-skills`
4. Verify: `.github/` and `.claude/` populated; `CLAUDE.md` and
   `.github/copilot-instructions.md` seeded; a pre-existing project-own file
   under `.github/` survives a re-run; a project's own
   `.github/copilot-instructions.md` is not overwritten.
5. Copy the git-hooks into a committed dir, `git config core.hooksPath <dir>`,
   move the submodule pointer in a second clone, `git pull`, confirm post-merge
   fires and syncs.

## Consumer rollout reminders

- Per clone: `git config core.hooksPath <dir>` (hooks config is never cloned).
- The consumer's `.gitattributes` needs `<hooks-dir>/* text eol=lf` (README Setup
  step 2); the central repo's attribute does not travel with copied hook files.
- The first sync after `git submodule add` is manual (README Setup step 3);
  no hook fires on submodule add.
- Synced files are committed in the consumer, never gitignored: Copilot on
  github.com reads only committed content.
