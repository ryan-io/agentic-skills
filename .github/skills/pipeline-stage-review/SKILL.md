---
name: pipeline-stage-review
description: >
  Run an independent adversarial critique at the gates a design crosses toward code: Gate A over
  the design, Gate B over the implementation plan, Gate C over built code (design fidelity plus
  plan completeness). Use on "critique this design", "review the plan before we build", "gate
  review", or "poke holes in the decomposition". Spawns the role-bound reviewer agent
  (gate-a-reviewer, gate-b-reviewer, gate-c-reviewer) where subagents are available; otherwise
  runs the gate inline with an optional standalone handoff. The reviewer gets only the design
  doc and governing records, never the author's rationale. Writes no design or code; returns a
  verdict the pipeline acts on.
tags: [design-pipeline, critique, skill]
---

# Pipeline Stage Review (the adversarial gates)

A design reaches code through the pipeline: pipeline-stg1-requirements, pipeline-stg2-volatilities, pipeline-stg3-architecture, pipeline-stg4-validation, pipeline-stg5-implementation-planning, pipeline-stg6-implementation. An independent adversary judges the work at three gates.

- **Gate A** (after stage 4): judges the design. A fault here is a markdown edit; the same fault in code is a refactor.
- **Gate B** (after stage 5): judges the plan. A design sound at Gate A does not always survive being turned into a plan.
- **Gate C** (after stage 6): judges the built code against the design it claims to build. A fault here is a same-session fix before the increment closes: drifted code, a purity-boundary leak, a lifecycle fault the design forbade.

The gate does not stop the workflow. It returns findings; the originating agent fixes them through the owning stage skill and re-runs the gate. The block is local: close the must-fix, re-run, proceed.

This skill adds no design or code substance. It carries the gate invocation and routing. The full reviewer briefs live in the agent definitions at `.claude/agents/` (Claude Code) and `.github/agents/*.agent.md` (GitHub Copilot).

## The independence rule (read this first)

A reviewer that shares the author's mental model is not an adversary; the agent that wrote the design will confirm it if asked to critique it. So the reviewer runs on a deliberately starved context.

Give the reviewer exactly two things:

- the work under review (per gate, below), and
- the governing records to hold it against.

Never give it the author's rationale, session narration, chat history, or the conclusion the design argued for. The reviewer re-derives what the design is trying to do from the doc, then judges whether it does it.

Reviewer tool access: read-only for Gates A and B; Gate C adds build-and-test (`dotnet build`, `dotnet test` on the default stack).

## Invoking the reviewer, per environment

- **Can spawn subagents (Claude Code): spawn.** The ideal path. Spawn the role-bound reviewer from `.claude/agents/`; the fresh subagent context is the starved context. Pass only the design doc path (`docs/design/{slug}-design.md`), the diff at Gate C, and the record list.
- **Cannot spawn subagents (Copilot chat): run the gate inline.**
  - Adopt the reviewer's brief (the gate sections below and the matching agent definition).
  - Re-derive intent from the design doc and records alone; set aside the session's own authoring rationale as far as possible.
  - Return the verdict in the reviewer's vocabulary, stating that it ran inline. Inline review is weaker than an independent context.
  - Then offer the developer a standalone review as an option: output a **handoff artifact** holding the reviewer brief, the design doc path `docs/design/{slug}-design.md` (or the doc's content when the standalone session cannot read files), the diff at Gate C, and the governing-record list. Nothing else.
  - The developer pastes it into a fresh chat with `@gate-a-reviewer` / `@gate-b-reviewer` / `@gate-c-reviewer` (defined in `.github/agents/*.agent.md`, also in the agent picker) and carries the verdict back. A standalone verdict supersedes the inline one.

## Ground first

- Gather what binds the design: the project's ADRs (always obeyed), instruction files (code and testing standards), and prior design artifacts. Open only what applies.
- This is the record set the reviewer receives.
- The reviewer grounds independently, never from the author's narration. The critique invents no constraint the records do not contain.

## Gate A: after architecture, before planning

- Fires once `docs/design/{slug}-design.md` carries `## Requirements`, `## Volatilities`, `## Architecture`, and `## Validation` (the last from `pipeline-stg4-validation`). A standalone `pipeline-stg4-validation` run over a partial doc still invokes the gate; a missing upstream section is a reviewer finding, not a reason to skip the gate.
- Hand `gate-a-reviewer` the design doc path (inline diagrams included) and the record list.
- Its brief weights volatility fidelity above the other lenses (use-case fidelity, layering and seam soundness, simplicity and proportion, lifecycle soundness, impact and problem fit).
- Verdict: READY or REVISE.

## Gate B: after the plan, before implementation

- Fires once `pipeline-stg5-implementation-planning` has written the design doc's `## Implementation Plan` section.
- Hand `gate-b-reviewer` the design doc path and the record list.
- It checks plan-vs-design fidelity: every architecture service in the backlog with the right layer and placement; every named knob surviving into the tuning surface; every governing record honored as a checkable constraint; nothing in the plan contradicting the design.
- Verdict: READY or REVISE.

## Gate C: after implementation, the post-build review

- Fires once the build is green (default stack: `dotnet build` clean, NUnit suite passing via `dotnet test`).
- Hand `gate-c-reviewer` the diff, the built-code entry points, the design doc (including `## Implementation Plan` and `## Built log`), and the record list.
- Lenses: correctness, design fidelity, plan completeness, the purity boundary (no pure-tier UI-framework reference), static-lifecycle safety (no static mutable state), robustness and test gaps, the tuning surface (no knob hardcoded that the plan put on a config seam), impact and problem fit, simplicity.
- Verdict: CONFIRMED or REFUTED. The reviewer never fixes.

## The verdict

The reviewer returns findings, not edits. The originating agent acts on them. Sort every finding:

- **Must-fix.** The work is wrong against a use case, a volatility, a layer boundary, a governing record, or (Gate C) the design it was built from. Route to the owner: `pipeline-stg2-volatilities` for a decomposition fault; `pipeline-stg3-architecture` for a layering or seam fault; `pipeline-stg4-validation` for a composition-proof fault (a chain breaking a call rule, a use case the proof omits); `pipeline-stg5-implementation-planning` for a plan fault; `pipeline-stg6-implementation` for a code fault (with a regression test where the gap was a missing test). Never proceed past the gate with an open must-fix. Fix-and-continue, not a halt.
- **Tracked debt.** A real weakness not worth blocking on. Record it in the reviewed section or the plan's open items, pointing at the governing record.
- **Question.** The reviewer cannot tell whether the work is right. Surface it to the developer; a question the doc cannot answer is a gap in the doc.

Every line the verdict leaves in a record states the defect, the evidence, and the owner, in short plain sentences.

A clean gate is a valid and common result. Note that it ran, and proceed.

## Boundaries

- This skill critiques. It owns no artifact or code and writes none.
- It invents no requirement, volatility, constraint, or fix the records do not contain. Inventing the answer is the same failure as the author confirming their own design.
- It complements the author's own composition proof (`pipeline-stg4-validation`), which runs before Gate A: the gate checks a proof, it does not supply one.
- The pattern catalog (`design-patterns`) doubles as a critique checklist at every gate: a hand-rolled mechanism that is an unnamed known pattern, or a seam whose named pattern doesn't match the code, is a fidelity finding.

## References

- The reviewer agent definitions: `.claude/agents/gate-a-reviewer.md`, `gate-b-reviewer.md`, `gate-c-reviewer.md` (Claude Code) and `.github/agents/gate-a-reviewer.agent.md`, `gate-b-reviewer.agent.md`, `gate-c-reviewer.agent.md` (GitHub Copilot): the briefs and tools (model bindings on the Claude side).
- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
- The pipeline it gates: `pipeline-stg1-requirements`, `pipeline-stg2-volatilities`, `pipeline-stg3-architecture`, `pipeline-stg4-validation`, `pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`.
