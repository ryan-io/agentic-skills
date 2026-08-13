---
applyTo: "**"
---

# Agent Guardrails

Behavioral constraints for any agent working in this repository (GitHub Copilot, Copilot code review, Claude Code, spawned subagents). Establishes the boundaries the other instruction files and the skills assume. Loads unconditionally.

## Ask, Do Not Guess

When uncertain about intent, scope, approach, or the correct answer, ask the developer. Do not infer, assume, or fabricate. A wrong guess costs more than a clarifying question.

## ADRs Bind

Architecture decision records (`docs/adr/`) are always obeyed. An agent that finds its work conflicting with an Active ADR stops and surfaces the conflict; it does not code past it. Changing a decision means proposing a new or amended ADR for developer sign-off, never silently diverging. In review contexts, code that contradicts an Active ADR is a must-fix finding.

## Commit Workflow

Conventional commit prefixes: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `style`, `perf`, `build`. Subject: imperative, present tense, max 72 chars. Body wraps at 80 chars. Scope optional but encouraged for single-module changes.

Agents never commit on their own. The developer runs every commit; at most, suggest a single commit subject (and a body if the change warrants one) and stop.

## Architecture Preservation

The following paths are load-bearing; do not reorganize without an ADR:

- `.github/instructions/` and `.claude/rules/`: instruction files (source and mirror)
- `.github/skills/` and `.claude/skills/`: skill definitions (source and mirror)
- `.github/agents/` and `.claude/agents/`: reviewer agent definitions
- `docs/adr/`: architecture decision records
- `docs/design/`: design pipeline documents (`{slug}-design.md`)

## Instruction File Integrity

Agents must not edit files in `.github/instructions/` or `.claude/rules/` without explicit developer approval. Propose the change and get the developer's sign-off first. The two trees are mirrors, as are the two skills trees: when a change is approved for one, apply it to both in the same change set. A mirror pair that differs is itself a finding.

In a project consuming agentic-skills, the `.github/` and `.claude/` trees and `CLAUDE.md` are synced copies: the central repo's sync script overwrites local edits on the next run. Change them in the central agentic-skills repo, never in the consuming project. Project-specific skills, rules, and agents are additive files with distinct names; the sync never deletes them. The two entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) are seeded only when absent and never overwritten; merge central updates into a project's own copies manually.

## Skill Authoring

Skills whose output is a saved file must include a step for revising an existing artifact. That step reads the saved file first, applies the requested change, preserves all other content and the skill's generation conventions, confirms before overwriting, and saves to the same path unless the user renames the artifact.
