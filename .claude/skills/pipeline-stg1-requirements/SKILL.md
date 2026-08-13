---
name: pipeline-stg1-requirements
description: >
  Stage 1 of the design pipeline: interactively captures requirements as required behavior, not
  functionality. Elicits use cases (sequences of activities), draws activity diagrams for nested
  conditionals, and flags solutions masquerading as requirements. Use for "use cases", "required
  behavior", "behavior not functionality", "capture requirements", or "what should the system
  do". Writes the ## Requirements section of docs/design/{slug}-design.md; its output feeds
  pipeline-stg2-volatilities.
tags: [design-pipeline, requirements, skill]
---

# Pipeline Stage 1: Behavioral Requirements

Interactive session. Ask questions, draw out required behavior, record it as use cases.

The rule: **capture required behavior, not required functionality.**

- "The system should do A" leaves implementation open to interpretation.
- "When X happens, the system does B then C" says how the system operates.

Pipeline: pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture -> pipeline-stg4-validation -> pipeline-stg5-implementation-planning -> pipeline-stg6-implementation, gated by pipeline-stage-review.

Do not aim for a complete use-case set. Requirements change; that is what they do. The use cases become the validation set the architecture composes against (`pipeline-stg4-validation`), not a component list for the design to mirror.

## Ground first

- Read what is already decided: ADRs, prior design documents, `docs/design/` from earlier runs.
- An unresolved conflict in those records is a blocker to surface, not something to write past.

## The artifact

One document carries the whole pipeline: `docs/design/{slug}-design.md`.

- Sections in order: `## Requirements` (stage 1), `## Volatilities` (stage 2), `## Architecture` (stage 3), `## Validation` (stage 4), `## Implementation Plan` (stage 5), `## Built log` (stage 6).
- Each skill owns its section and preserves the others.
- Sequence diagrams (`sequence-diagram-creation`) have no section of their own. They sit inline in whichever section their flow belongs to.
- Standalone runs included: check for the doc first. If it exists, modify only this skill's section. If not, create it with only this skill's section.

This skill writes the `## Requirements` section. If the section already exists, this is a revision: read it first, apply the change, preserve everything else, confirm before overwriting.

## Starting the session

- Ask one question at a time. Do not lecture about the method.
- Opening: "What system, feature, or problem do you want to capture requirements for?"
- Derive a kebab-case `{slug}` from the answer and confirm it.

## Phase 1: Elicit required behavior

Requirements arrive as functionality, because that is how customers and management talk. Convert each one to behavior.

- For each stated need, ask: "Walk me through what happens. Who or what starts it, what sequence of activities occurs, what is the end state?"
- Record the answer as a use case: a sequence of activities that accomplishes work and adds value.
- Use cases can cover end-user interactions, system-to-system interactions, or back-end processing.

## Phase 2: Choose a representation

- Capture use cases as text or diagrams. Prefer diagrams for anything with branching.
- Rule of thumb: **if a use case contains a nested "if", draw it.** Nobody parses a sentence with a nested conditional.
- Prefer activity diagrams: they capture sequence and timing. Use-case diagrams do not.
- Draw activity diagrams as Mermaid `flowchart` blocks inline in the section.
- For interaction flows between participants (request/response, messages), hand off to `sequence-diagram-creation`. It records the diagram inline beside the use case in `## Requirements`.

## Phase 3: Flag solutions masquerading as requirements

Stated requirements are full of solutions disguised as needs. Mark them; do not resolve them here (the drilling technique lives in `pipeline-stg2-volatilities`).

- For each use case, ask once: "Is this the actual need, or one way of meeting a deeper need?"
- Where the answer is "one way," add it to a "Solutions to scrub" list for stage 2.

## Phase 4: Write the section

Confirm the consolidated use-case list with the user, then write `## Requirements`:

1. Problem statement: the originating ask, quoted verbatim. Every later stage traces back to it.
2. System summary, one or two sentences.
3. Use cases: numbered behaviors, with activity diagrams where Phase 2 called for them. `pipeline-stg4-validation` later marks the core ones beside their headings.
4. "Solutions to scrub": the flags from Phase 3.
5. References.

Write in short, plain, concrete prose.

## Handoff

Offer the next stage: "These use cases are ready. Want me to run pipeline-stg2-volatilities to find what is likely to change?" That skill reads the `## Requirements` section as its input.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
