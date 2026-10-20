# agentic-skills

A generic agent harness: a principal-engineer operating stance, a staged volatility-based design pipeline, record and ledger skills, research and knowledge skills that fire implicitly, adversarial gate reviewers, and the instruction files that bind them. Serves Claude Code, GitHub Copilot (VS 2026, VS Code, CLI, coding agent), Copilot code review on pull requests, and plain terminal or chat sessions that can read a `CLAUDE.md`.

## Setup

1. Add as a submodule: `git submodule add <central-repo-url> <submodule-path>`.
2. Wire the sync into the project's git hooks:
   - Existing hook infrastructure: after `git submodule update`, add `sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path>` (in post-merge, post-checkout, and post-rewrite; `git pull --rebase` fires post-rewrite, not post-merge).
   - Otherwise: copy `hooks/git-hooks/post-merge`, `post-checkout`, and `post-rewrite` into a committed hooks dir and run `git config core.hooksPath <dir>` once per clone. The hook files need no edits, but must stay executable (`git update-index --chmod=+x <dir>/post-merge <dir>/post-checkout <dir>/post-rewrite`); git silently skips a non-executable hook.
   - Add `<dir>/* text eol=lf` and `.github/skills/**/*.sh text eol=lf` to the project's `.gitattributes`; the second line keeps the synced `set-voice.sh` runnable under sh. This repo's own attribute protects only the submodule checkout; without the consumer-side rule, a fresh Windows clone with `core.autocrlf=true` checks the copied hooks out CRLF and they fail under POSIX sh.
3. Run the first sync manually; adding the submodule fires no hook: `sh <submodule-path>/hooks/sync-agentic-skills.sh <submodule-path>`.
4. Commit synced changes. Never gitignore them: Copilot on github.com only sees committed content.
5. Fill `research.instructions.md` Repo Signals (language, framework, build and test commands, architecture style) in the consuming project's own copy of the rule, or in a project-own `repo-signals.instructions.md`. Name the stack profile there too: `csharp`, `lua`, or `generic`.
6. Commit a CI drift check (recommended for teams). No hook fires on a fast-forward `git pull --rebase`, and a clone that never ran `git config core.hooksPath` drifts silently; CI catches both:

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

For a chat-only or non-git context, copy `CLAUDE.md` alone: it carries the operating stance, the writing standard, and the skill triggers.

Sync semantics (`hooks/sync-agentic-skills.sh`, git + tar only):

- Overwrites only files this repo ships; deletes nothing. Project-own files under `.github/` and `.claude/` survive; give additions distinct names.
- Seeds `CLAUDE.md`, `.github/copilot-instructions.md`, and the generated `voice.instructions.md` (both trees) only when absent; a project's own copies are never overwritten. Merge central updates into the entry points manually; re-run `/voice <name>` to pick up a changed voice file.
- Migration (2026-10-19): a project synced before this date may hold a `.claude/settings.json` with a SessionStart hook calling `scripts/link-harness.ps1`, which consumers do not have. Delete that hook; the sync no longer ships the file.
- Edit synced files in this repo only; the next sync overwrites local edits, except the seed-once files above.

```text
.github/
  copilot-instructions.md  <- Copilot entry point (seeded once)
  skills/                  <- skills (SOURCE OF TRUTH); ledger skills carry a stdlib Python script + tests
  agents/                  <- Copilot custom agents (*.agent.md)
  instructions/            <- instruction files (SOURCE OF TRUTH)
  docs/                    <- templates (ADR, business rule) and companion guides
  docs/voices/             <- voice library; one file per register, README holds the contract
.claude/
  skills/                  <- mirror of .github/skills
  agents/                  <- Claude Code subagents
  rules/                   <- mirror of .github/instructions
CLAUDE.md                  <- Claude Code entry point (seeded once)
hooks/                     <- sync script, mirror script, hook files (never synced into projects)
scripts/                   <- link-harness.ps1 (machine-wide junctions; never synced into projects)
```

## Discovery: who reads what

| Consumer | Skills | Agents | Instructions | Entry point |
|---|---|---|---|---|
| Claude Code | `.claude/skills` | `.claude/agents` (subagents) | `.claude/rules` (`paths:`) | `CLAUDE.md` |
| Copilot IDE / CLI / coding agent | both skills trees | `.github/agents/*.agent.md` (`@name`) | `.github/instructions` (`applyTo:`) | `.github/copilot-instructions.md` |
| Copilot code review (PRs) | `.github/skills` only | not used | `.github/instructions` | `.github/copilot-instructions.md` |

Both skills trees are required (Claude Code reads only `.claude/`; PR review reads only `.github/`). The mirrors are byte-identical, so double discovery is harmless; drift is the only risk. Path-scoped instruction files carry both keys (`applyTo:` Copilot, `paths:` Claude), each side ignoring the other's; universal files (`agent-guardrails`, `code-standards`, `design-principles`, `research`, `pattern-fidelity`, `navigation`) carry `applyTo: "**"` alone so Claude Code loads them unconditionally.

Version floors: custom agents need VS 2026 18.4+; agent skills need VS 2026 18.5+. Visual Studio loads instruction files only after the opt-in at Tools > Options > GitHub > Copilot > Copilot Chat > "Enable custom instructions".

## The entry points

`CLAUDE.md` and `.github/copilot-instructions.md` carry the same stance in two dialects: who the agent is (principal staff engineer and architect: research first, options with tradeoffs, data over opinion, simplest solution), the non-negotiables (ADRs bind, never commit, mirrors move together), the pipeline, the implicit skill triggers, delegation, stack defaults, and the Concise Technical Writing standard with a swappable voice register (default `jarvis`; see Voice below). Deeper writing guidance: `.github/docs/writing-voice-guide.md`.

## The design pipeline

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
| final | `pipeline-final-validation` | `docs/reviews/{date}-{slug}-pipeline-validation.md` + a `## Built log` entry |

Front doors: `design-autopilot` runs stages 1 to 5 autonomously, halting only on genuine uncertainty; `post-impl` continues into stage 6 (via `impl-worker` where subagents exist), Gate C, and `pipeline-final-validation`, then closes the records on a PASS. `architecture-design-pipeline` runs stages 1 to 4 interactively and ends at Gate A. `deliver-change` is the maintenance door for a fix, refactor, or `TD-NNN` paydown on existing code: index-first grounding, a behavior-pinning test, Gate C, ledgers updated. `pair-programming` is the ungoverned live session; `impact-analysis` runs before any artifact closes. Architecture touches always go through the pipeline: no plan, no code.

## Skills

Implicit skills fire on a situation; the description's first clause says when. On-demand skills run when asked.

| Skill | Fires when | Owns |
|---|---|---|
| `idea-crucible` | a half-formed idea or "what if" | `docs/ideas/{date}-{slug}.md` |
| `concept-propagation` | a new term is coined or confirmed | `docs/glossary.md`, routes edits |
| `system-context` | work leans on a library, framework, or external fact | `docs/research/` + index |
| `system-map` | a task touches a backend system | `docs/systems/systems-index.md` + nodes |
| `doc-reconcile` | a landed decision is summarized by a synthesis doc | the synthesis doc |
| `tech-debt` | work defers something incomplete | `docs/debt/debt-index.md` (`debt.py`) |
| `refactor-ledger` | a restructuring is out of scope | `docs/refactor/refactor-ledger.md` (`refactor.py`) |
| `to-do` | "later", "remind me" | `docs/todo/todo-ledger.md` (`todo.py`) |
| `future-system` | a design is settled but the build deferred | `docs/future-systems/` |
| `adr-creation` | a pattern, concern, or dependency lands with no record | `docs/adr/` + `adr-index.md` |
| `business-rule-creation` | a domain constraint stated with no record | `docs/business-rules/` + `br-index.md` |
| `impact-analysis` | an artifact is about to close | findings only |
| `concise-documentation` | a doc is about to be saved, or reads long | the named doc |
| `lua-best-practices` | a `.lua` file is created or edited | review, setup scaffolds |
| `reverse-engineering` | work depends on code or a system the repo does not document | `docs/reverse-engineering/` + `re-index.md`; guides per input kind in `.github/docs/` |
| `design-patterns`, `sequence-diagram-creation`, `unit-test-creation`, `test-plan-creation` | on request | diagrams, tests, `docs/test-plans/` |
| `voice` | `/voice <name>`, "be more terse", "add a voice" | `voice.instructions.md` (generated), `.github/docs/voices/` |
| `discover` | `/discover`, "what can you do", `/discover <name>` | one-screen catalog of the harness, self-checked against disk |
| `scribble-triage` | `scribble.md` at the repo root has content | routes each line |
| `house-keeping`, `audit-and-critique`, `architecture-conformance`, `system-review` | periodic, on request | `docs/reviews/` |

Ledger scripts are stdlib Python, run from the repo root (`python .github/skills/tech-debt/debt.py list`); every ledger skill states its row format so the table can be edited by hand where Python is unavailable. Tests: `python -m unittest discover -s .github/skills/<name>/tests -p "test_*.py"`.

## Agents

Reviewers get a starved context: artifacts plus governing records, never the author's rationale. At Gates A and B a verifier checks the reviewer's findings in the same context; only confirmed findings are acted on, and a refuted one is dropped with its reason recorded.

| Agent | Role |
|---|---|
| `gate-a-reviewer`, `gate-b-reviewer`, `gate-c-reviewer` | adversarial gates over design, plan, built code |
| `design-review-verifier`, `plan-review-verifier` | verify each Gate A / Gate B finding (CONFIRMED, REFUTED, UNVERIFIABLE); verdict STANDS or REVISE-REVIEW |
| `pipeline-validator` | end-to-end check after Gate C: requirements to tested code, PASS or FAIL with a traceability matrix |
| `impl-worker` | builds a gated `## Implementation Plan`; never commits or spawns |
| `records-worker` | executes decided record edits; never decides content |
| `grounding-scout` | index-first sweeps, compact pointers only |
| `concise-editor` | word-level tightening of a named doc or `///` comments |
| `audit-reader` | one bounded read-only audit lane |
| `docs-scout` | doc lookup over local corpora and vendor docs |

- Can spawn subagents (Claude Code): spawn the role agent; the orchestrator keeps judgment, the agent executes.
- Cannot spawn subagents (Copilot chat, terminal): the skill runs the step inline and says so, then offers a handoff to the standalone `@name` chat where one helps; a standalone gate verdict supersedes the inline one.
- Gate C and the two workers have no Copilot `tools` allowlist so they can run build and test commands; the read-only agents carry both the VS 2026 names (`code_search`, `readfile`, `find_references`) and GitHub's aliases (`read`, `search`). Known VS 2026 quirk: a custom agent's tool groups can show as disabled after selection; re-enable them in the chat window's Tools panel.

## Instruction files

Universal (load everywhere): `agent-guardrails`, `code-standards`, `design-principles`, `research`, `pattern-fidelity`, `navigation`, and the generated `voice`. Path-scoped: `testing`, `pr-review`, `csharp-code-standards`, `xml-documentation`, `lua-code-standards`, `adr-template` and `adr-pr-review` (`docs/adr/**`), `br-review` (`docs/business-rules/**`). Companion guides and templates live in `.github/docs/`.

## Conventions

- **ADRs bind.** `docs/adr/` is always obeyed; conflicts are blockers, and in review a contradiction is a must-fix.
- **Mirror rule.** Edit under `.github/`, then `sh hooks/mirror-trees.sh` (or `--check` to verify) before committing. Agents are not mirrors (per-ecosystem frontmatter).
- **Guardrails.** Ask-do-not-guess, options before answers, pipeline first, commit workflow, load-bearing paths, subagent spawning, coding delegation (all code is written by an Opus 5.5 worker with a fresh context, never by the orchestrator seat): `agent-guardrails.instructions.md`.
- **Stack profiles.** Stack-neutral by default. A project names its profile in `research.instructions.md` Repo Signals: `csharp` (`csharp-code-standards.instructions.md` plus the guide's Stack profile section), `lua`, or `generic` (`code-standards` alone). The layered architecture vocabulary (Client / Managers / Engines / ResourceAccess / Resources + Utilities, composition-root DI against `Contracts`, a pure business tier) is language-neutral. Project ADRs and instruction files override.
- **Writing.** Concise Technical Writing section of the entry points; `.github/docs/writing-voice-guide.md`; no em dashes; tags in skill frontmatter sorted.
- **Voice.** The conversational register is one generated rule, `voice.instructions.md`, built from `.github/docs/voices/<name>.md`. Swap with `/voice <name>` in a session, or `sh .github/skills/voice/set-voice.sh <name>` (`--list`, `--current`). The script ships with the skill, so a consuming project can swap too, and its choice survives the sync. Shipped: `jarvis` (default), `neutral`, `terse`, `mentor`. Invariants every voice obeys: `.github/docs/voices/README.md`.

## Extending

1. Create `<skill-name>/SKILL.md` under `.github/skills/` (kebab-case folder; frontmatter `name` equals folder name; `tags` sorted).
2. Write a trigger-rich `description`; open with "Invoke implicitly when ..." if the skill should fire on a situation.
3. Skills that save a file include a revision step (read, change, preserve the rest, confirm).
4. Reference sibling skills by folder name; run `sh hooks/mirror-trees.sh` in the same commit.

## References

- Löwy, *Righting Software* (2019). Gamma et al., *Design Patterns* (1994).
- [Agent Skills spec](https://agentskills.io), [Copilot agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code memory](https://code.claude.com/docs/en/memory).
