# agentic-skills

Agent skills that run a staged, volatility-based design pipeline, plus gate reviewers, instruction files, and entry points. Serves three consumers: Claude Code, GitHub Copilot (IDE, CLI, coding agent), and Copilot code review on pull requests.

## Setup

1. Add as a submodule: `git submodule add <central-repo-url> <submodule-path>`.
2. Wire the sync into the project's git hooks:
   - Existing hook infrastructure: after `git submodule update`, add `sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path>` (in post-merge, post-checkout, and post-rewrite; `git pull --rebase` fires post-rewrite, not post-merge).
   - Otherwise: copy `hooks/git-hooks/post-merge`, `post-checkout`, and `post-rewrite` into a committed hooks dir and run `git config core.hooksPath <dir>` once per clone. The hook files need no edits, but must stay executable (`git update-index --chmod=+x <dir>/post-merge <dir>/post-checkout <dir>/post-rewrite`); git silently skips a non-executable hook.
   - Add `<dir>/* text eol=lf` to the project's `.gitattributes`. This repo's own attribute protects only the submodule checkout; without the consumer-side rule, a fresh Windows clone with `core.autocrlf=true` checks the copied hooks out CRLF and they fail under POSIX sh.
3. Run the first sync manually; adding the submodule fires no hook: `sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path>`.
4. Commit synced changes. Never gitignore them: Copilot on github.com only sees committed content.
5. Commit a CI drift check (recommended for teams). No hook fires on a fast-forward `git pull --rebase`, and a clone that never ran `git config core.hooksPath` drifts silently; CI catches both:

   ```yaml
   # .github/workflows/agentic-skills-drift.yml
   name: agentic-skills drift
   on: [pull_request]
   jobs:
     drift:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with: { submodules: true }
         - run: |
             sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path>
             test -z "$(git status --porcelain)" || { git status; echo "::error::synced agentic-skills content drifted; run the sync and commit"; exit 1; }
   ```

6. In this repo, replace the two stubs with real content: `testing.instructions.md`, `csharp-code-standards.instructions.md`.

Sync semantics (`hooks/sync-agentic-skills.sh`, git + tar only):

- Overwrites only files this repo ships; deletes nothing. Project-own files under `.github/` and `.claude/` survive; give additions distinct names.
- Seeds `CLAUDE.md` and `.github/copilot-instructions.md` only when absent; a project's own copies are never overwritten. Merge central updates into them manually.
- Edit synced files in this repo only; the next sync overwrites local edits.
- `git status` moves only when this repo changed (identical overwrites are no-ops).

```text
.github/
  copilot-instructions.md  <- Copilot entry point (seeded once)
  skills/                  <- the 11 skills (SOURCE OF TRUTH)
  agents/                  <- Copilot reviewer agents (*.agent.md)
  instructions/            <- instruction files (SOURCE OF TRUTH)
.claude/
  skills/                  <- mirror of .github/skills
  agents/                  <- Claude Code reviewer agents
  rules/                   <- mirror of .github/instructions
CLAUDE.md                  <- Claude Code entry point (seeded once)
hooks/                     <- sync script + hook files (never synced into projects)
```

## Discovery: who reads what

| Consumer | Skills | Agents | Instructions | Entry point |
|---|---|---|---|---|
| Claude Code | `.claude/skills` | `.claude/agents` (subagents) | `.claude/rules` (`paths:`) | `CLAUDE.md` |
| Copilot IDE / CLI / coding agent | both skills trees | `.github/agents/*.agent.md` (`@name`) | `.github/instructions` (`applyTo:`) | `.github/copilot-instructions.md` |
| Copilot code review (PRs) | `.github/skills` only | not used | `.github/instructions` | `.github/copilot-instructions.md` |

Both skills trees are required (Claude Code reads only `.claude/`; PR review reads only `.github/`). The mirrors are byte-identical, so double discovery is harmless; drift is the only risk. Path-scoped instruction files carry both keys (`applyTo:` Copilot, `paths:` Claude), each side ignoring the other's; `agent-guardrails` loads everywhere via `applyTo: "**"` alone.

Version floors: custom agents need VS 2026 18.4+; agent skills need VS 2026 18.5+. Visual Studio loads instruction files only after the opt-in at Tools > Options > GitHub > Copilot > Copilot Chat > "Enable custom instructions".

## The pipeline

One artifact per system: `docs/design/{slug}-design.md`. Sections in order: `## Requirements`, `## Volatilities`, `## Architecture`, `## Validation`, `## Implementation Plan`, `## Built log`. Each skill owns its section and preserves the rest; sequence diagrams live inline in whichever section their flow belongs to.

| Stage | Skill | Writes |
|---|---|---|
| 1 | `pipeline-stg1-requirements` | `## Requirements` |
| 2 | `pipeline-stg2-volatilities` | `## Volatilities` |
| 3 | `pipeline-stg3-architecture` | `## Architecture` |
| 4 | `pipeline-stg4-validation` | `## Validation` |
| 5 | `pipeline-stg5-implementation-planning` | `## Implementation Plan` (+ empty `## Built log`) |
| 6 | `pipeline-stg6-implementation` | code + `## Built log` |
| gates | `pipeline-stage-review` | verdicts only (Gate A after 4, B after 5, C after 6) |

Every stage runs standalone off whatever upstream sections exist; `{slug}` is the system's kebab-case name. A standalone run checks for the design doc first: modify it if present (own section only), create it with just that section if not. Architecture touches always go through the pipeline: no plan, no code. Supporting skills: `design-patterns`, `sequence-diagram-creation`, `unit-test-creation`, `concise-documentation`.

## Gate reviews

Reviewers get a starved context: artifacts plus governing records, never the author's rationale.

- Can spawn subagents (Claude Code): spawn `gate-a/b/c-reviewer` -- the ideal path.
- Cannot spawn subagents (Copilot chat): the skill runs the gate inline (stating so), then offers a handoff artifact for an optional standalone `@gate-x-reviewer` chat fed `docs/design/{slug}-design.md`; a standalone verdict supersedes the inline one.
- Gate C's Copilot variant has no `tools` allowlist so it can run `dotnet build` / `dotnet test`; its brief forbids everything else. The A/B `tools` lists carry both the VS 2026 names (`code_search`, `readfile`, `find_references`) and GitHub's cross-surface aliases (`read`, `search`); surfaces ignore tool names they don't recognize, so the union works in VS 2026, VS Code, and on github.com. Known VS 2026 quirk: a custom agent's tool groups can show as disabled after selection; re-enable them in the chat window's Tools panel.

## Conventions

- **ADRs bind.** `docs/adr/` is always obeyed; conflicts are blockers, and in review a contradiction is a must-fix.
- **Mirror rule.** Edit under `.github/`, copy to the `.claude/` counterpart in the same commit. Agents are not mirrors (per-ecosystem frontmatter).
- **Guardrails.** Ask-do-not-guess, commit workflow, load-bearing paths: `agent-guardrails.instructions.md`.
- **Stack defaults.** C#, layered architecture (Client / Managers / Engines / ResourceAccess / Resources + Utilities), composition-root DI against `Contracts`, NUnit 4 + Moq. Project ADRs and instruction files override.

## Extending

1. Create `<skill-name>/SKILL.md` under `.github/skills/` (kebab-case folder; frontmatter `name` equals folder name).
2. Write a trigger-rich `description`; keep the body procedure-focused.
3. Skills that save a file include a revision step (read, change, preserve the rest, confirm).
4. Reference sibling skills by folder name; copy to `.claude/skills/` in the same commit.

## References

- Löwy, *Righting Software* (2019). Gamma et al., *Design Patterns* (1994).
- [Agent Skills spec](https://agentskills.io), [Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [Claude Code skills](https://code.claude.com/docs/en/skills).
