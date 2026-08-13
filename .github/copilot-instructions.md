# Project agent guide (GitHub Copilot)

This project uses the agentic-skills design pipeline: a staged, volatility-based design method. Path-scoped instructions load from `.github/instructions/`; skills from `.github/skills/`; the gate reviewer custom agents from `.github/agents/`.

## Non-negotiables

- ADRs in `docs/adr/` are always obeyed. A conflict with an Active ADR is a blocker to surface, never something to code past. In code review, code contradicting an Active ADR is a must-fix finding.
- Ask, do not guess (see `.github/instructions/agent-guardrails.instructions.md`). Never commit autonomously; suggest a commit subject and stop.
- `.github/` and `.claude/` trees are mirrors (skills and instructions); change both in the same change set. A mirror pair that differs is a finding.

## The design pipeline

pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture -> pipeline-stg4-validation -> pipeline-stg5-implementation-planning -> pipeline-stg6-implementation, gated by pipeline-stage-review (Gate A after stage 4, Gate B after stage 5, Gate C after stage 6). Copilot cannot spawn subagents: run the gate inline per pipeline-stage-review (state that it ran inline), and offer a handoff artifact for an optional standalone @gate-a-reviewer / @gate-b-reviewer / @gate-c-reviewer chat, feeding it docs/design/{slug}-design.md and the governing records; a standalone verdict supersedes the inline one.

One document per system: `docs/design/{slug}-design.md`. Sections in order: `## Requirements`, `## Volatilities`, `## Architecture`, `## Validation`, `## Implementation Plan`, `## Built log`; sequence diagrams live inline in whichever section their flow belongs to. Architecture touches always go through the pipeline: no plan, no code (run pipeline-stg5-implementation-planning first).

## Review guidance (including Copilot code review on pull requests)

Hold changes against: the layering call rules (closed architecture; Engines never call Managers or each other; ResourceAccess speaks atomic business verbs, never CRUD/IO verbs), the purity boundary (pure tier never references a UI-framework assembly), no static mutable state, knobs as authored configuration rather than hardcoded constants, `///` doc comments per `xml-documentation.instructions.md`, and tests that verify outcomes at owned boundaries per `testing.instructions.md`.

## Stack defaults

C# with layered architecture (Client / Managers / Engines / ResourceAccess / Resources + Utilities), composition-root DI against `Contracts` interfaces, NUnit 4 + Moq. Project ADRs and the instruction files override these defaults.
