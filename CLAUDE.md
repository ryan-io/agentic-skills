# Project agent guide (Claude Code)

This project uses the agentic-skills design pipeline: a staged, volatility-based design method. Topic rules load from `.claude/rules/`; skills from `.claude/skills/`; the gate reviewer subagents from `.claude/agents/`.

## Non-negotiables

- ADRs in `docs/adr/` are always obeyed. A conflict with an Active ADR is a blocker to surface, never something to code past.
- Ask, do not guess (see `.claude/rules/agent-guardrails.instructions.md`). Never commit; suggest a commit subject and stop.
- `.claude/` and `.github/` trees are mirrors (skills and instructions); change both in the same change set.

## The design pipeline

pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture -> pipeline-stg4-validation -> pipeline-stg5-implementation-planning -> pipeline-stg6-implementation, gated by pipeline-stage-review (Gate A after stage 4, Gate B after stage 5, Gate C after stage 6; reviewers spawn as subagents gate-a/b/c-reviewer).

One document per system: `docs/design/{slug}-design.md`. Sections in order: `## Requirements`, `## Volatilities`, `## Architecture`, `## Validation`, `## Implementation Plan`, `## Built log`; sequence diagrams live inline in whichever section their flow belongs to. Architecture touches always go through the pipeline: no plan, no code (run pipeline-stg5-implementation-planning first).

Supporting skills: `design-patterns`, `sequence-diagram-creation`, `unit-test-creation`, `concise-documentation`.

## Stack defaults

C# with layered architecture (Client / Managers / Engines / ResourceAccess / Resources + Utilities), composition-root DI against `Contracts` interfaces, pure tier free of UI-framework references, NUnit 4 + Moq. Project ADRs and the rules files override these defaults.
