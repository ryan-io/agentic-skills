# Agent Guardrails Guide

Companion to `agent-guardrails.instructions.md`. Read this when making architectural changes or editing instruction files.

## Architecture Preservation: Rationale

The load-bearing directories are a contract. The entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) and the sync script both depend on their current locations. Moving, renaming, or merging them breaks that contract, so a structural change needs an ADR first.

The specific dependencies: the sync expects `.github/instructions/` as source and `.claude/rules/` as mirror, and `.github/skills/` as source and `.claude/skills/` as mirror. Skills resolve by directory name.

## Instruction File Integrity

When an agent identifies a convention gap or a rule that should change, propose it to the developer and get sign-off, or flag it in a PR comment. Do not self-modify the rules you operate under.

## Commit Workflow: Shared Branch Rules

Do not amend or force-push commits that have already been pushed to a shared branch. Keep changes aligned with the existing pull-request and review flow described in `pr-review.instructions.md`.

## Templates

- **ADR**: `.github/docs/adr-template.md`, validated by `adr-pr-review.instructions.md`.
- **Business rule**: `.github/docs/br-template.md`, validated by `br-review.instructions.md`.

## Speed and Latency

**Prompt cache ordering.** Claude caches prompt prefixes. Instruction files are static and form a stable prefix. Avoid reordering instruction file lists between sessions; append new files rather than inserting.

**Parallel subagents.** Skills with independent subtasks should declare parallelizable steps so the orchestrator dispatches them concurrently. Where subagents are unavailable, the steps run inline in sequence.

**Model selection.** Use faster models for mechanical work (formatting, boilerplate, lookups). Reserve the strongest model for architectural decisions and complex refactoring.

## Regeneration Policy

Regenerate or update `agent-guardrails.instructions.md` when repository conventions materially change: new instruction files are added, skills are created or retired, or the directory structure evolves. The trigger is manual: a developer request or an audit finding. Review the file at least once per quarter to confirm it still reflects the project's actual constraints.
