---
applyTo: "**"
---

# Agent Guardrails

> **Full guidance:** `.github/docs/agent-guardrails-guide.md`

Behavioral constraints for any agent working in this repository (GitHub Copilot, Copilot code review, Claude Code, spawned subagents). Establishes the boundaries the other instruction files and the skills assume. Loads unconditionally.

## Ask, Do Not Guess

When uncertain about intent, scope, approach, or the correct answer, ask the developer. Do not infer, assume, or fabricate. A wrong guess costs more than a clarifying question.

## Pipeline First

Every change to the codebase enters through a front door; code written outside one is a finding.

- **New feature, system, or any architecture touch:** `design-autopilot` (autonomous) or `architecture-design-pipeline` (interactive), then `pipeline-stg5-implementation-planning` and `pipeline-stg6-implementation`. No plan, no code.
- **Bug fix, behavior-preserving refactor, debt paydown:** `deliver-change` with its track (`fix`, `refactor`, `debt TD-NNN`). Its routing gate sends anything architectural back to the pipeline.
- **Live, exploratory session the developer asks for by name:** `pair-programming`. Its outcome still lands through one of the doors above before it is called done.

Before touching code, name the door you are using. Asked to "just fix it" or "add X" with no door named, pick the one above that fits and say so; it costs one sentence.

## Options Before Answers

A non-trivial design, tooling, or dependency choice is presented as two or three viable options with pros, cons, and cost, then a recommendation with its reason. Never present a single path as if no alternative existed. Quantify where it changes the decision and cite the file, command, or link each claim rests on (`research`). Prefer the simplest option that meets the named requirement (`design-principles`).

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
- `.github/docs/`: templates and companion guides
- `docs/adr/`: architecture decision records
- `docs/business-rules/`: business rule definitions
- `docs/debt/`: technical-debt registry
- `docs/refactor/`: refactor ledger
- `docs/design/`: design pipeline documents (`{slug}-design.md`)

## Instruction File Integrity

Agents must not edit files in `.github/instructions/` or `.claude/rules/` without explicit developer approval. Propose the change and get the developer's sign-off first. One exception: `voice.instructions.md` is generated from `.github/docs/voices/` by `.github/skills/voice/set-voice.sh`, and the `voice` skill regenerates it on a developer's `/voice <name>`. Hand edits go to the library file, never the generated one. Like the entry points, the generated file is seeded once and then owned by the consuming project; the sync never overwrites it. The two trees are mirrors, as are the two skills trees: when a change is approved for one, apply it to both in the same change set. A mirror pair that differs is itself a finding.

In a project consuming agentic-skills, the `.github/` and `.claude/` trees and `CLAUDE.md` are synced copies: the central repo's sync script overwrites local edits on the next run, except the seed-once files named below and `.claude/settings*.json`, which it never writes. Change them in the central agentic-skills repo, never in the consuming project. Project-specific skills, rules, and agents are additive files with distinct names; the sync never deletes them. The two entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) are seeded only when absent and never overwritten; merge central updates into a project's own copies manually.

## Subagent Spawning

Spawn a built-in agent type that carries no model binding with an explicit model: sonnet for research and exploration. An unbound spawn inherits the orchestrator's model and bills the most expensive bucket. Role agents under `.claude/agents/` carry their own bindings. Where subagents are unavailable (Copilot chat, terminal), run the step inline and say so.

## Coding Delegation

Coding work (writing or changing source, tests, build files) is always delegated to an Opus 5.5 agent with a fresh context; the orchestrator seat navigates, reviews, and decides, it does not type the code.

- **Fable orchestrator:** every coding step is spawned to an Opus-bound agent (`impl-worker`, or a general-purpose agent with `model: opus`). No exceptions for "small" edits; a one-line fix still goes through the worker.
- **Opus orchestrator:** spawn a new Opus subagent for the coding step anyway. The fresh context is the point: the builder works from the plan and the records, not from the conversation that produced them.
- **Subagents unavailable** (Copilot chat, terminal): run the step inline, say so, and keep the plan-first discipline the worker would have followed.
- The orchestrator still owns the build report, the gate, and the verdict. Delegation moves execution off the seat, never judgment.

## Skill Authoring

Skills whose output is a saved file must include a step for revising an existing artifact. That step reads the saved file first, applies the requested change, preserves all other content and the skill's generation conventions, confirms before overwriting, and saves to the same path unless the user renames the artifact.
