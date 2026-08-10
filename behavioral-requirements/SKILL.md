---
name: behavioral-requirements
description: >
  Interactively captures requirements as required behavior, not functionality: elicits use cases
  (sequences of activities), draws activity diagrams for nested conditionals, and flags solutions
  masquerading as requirements. Use for "use cases", "required behavior", "behavior not
  functionality", or "what should the system do". Front end of the design pipeline; its output
  feeds volatility-decomposition.
---

# Behavioral Requirements

This skill runs as an interactive session: the agent asks questions to draw out required behavior and records it as use cases. It is the first stage of the design pipeline: behavioral-requirements -> volatility-decomposition -> architecture-layering.

The guiding rule: **requirements should capture required behavior, not required functionality.** "The system should do A" leaves implementation open to interpretation. "When X happens, the system does B then C" specifies how the system operates.

Requirements change; that is what requirements do. No one has ever had time to correctly spec a system's full use-case set upfront, so do not try for completeness here. The design prime directive downstream is never design against the requirements: the use cases captured here become the validation set the architecture composes against (`composable-design`), not a component list for the design to mirror.

## Ground first

Before eliciting, ground in what is already decided so the requirements do not contradict settled architecture: read any existing design records for the area (decision records, prior design documents, anything under `docs/{system-slug}/` from earlier pipeline runs). An unresolved conflict in those records is a blocker to surface to the developer, not a requirement to write past.

## Output

A use-case spec saved to `docs/{system-slug}/behavioral-requirements.md`, where `{system-slug}` is a kebab-case name for the system. Phase 4 defines the contents.

If `docs/{system-slug}/behavioral-requirements.md` already exists, this is a revision. Read it first, apply the requested change, preserve all other content and the conventions below, confirm before overwriting, and save to the same path unless the user renames it.

## Starting the Session

Ask one question at a time. Do not monologue about the method.

Opening: "What system, feature, or problem do you want to capture requirements for?" Derive a kebab-case `{system-slug}` from the answer and confirm it. All pipeline artifacts for this work live in `docs/{system-slug}/`, one document per pipeline stage, named for the stage: `docs/{system-slug}/{skill-slug}.md`.

## Phase 1: Elicit Required Behavior

Requirements arrive as functionality, because that is the language of customers, management, and marketing: "the system should do this and that." Your job is to convert each into behavior.

For each stated need, ask: "Walk me through what happens. Who or what initiates it, what sequence of activities occurs, and what is the end state?" Capture the answer as a use case: a particular sequence of activities that accomplishes work and adds value. Use cases can describe end-user interactions, system-to-system interactions, or back-end processing.

## Phase 2: Choose a Representation

Capture use cases textually or graphically. Prefer graphical for anything with branching.

Rule of thumb: **if a use case contains a nested "if", draw it.** No reader parses a sentence with a nested conditional.

Prefer **activity diagrams** because they capture time-critical and sequential aspects of behavior. Do not confuse them with use-case diagrams, which are user-centric and carry no notion of time or sequence.

Capture activity diagrams as Mermaid `flowchart` blocks inline in the spec; they render in most markdown viewers. For interaction flows between participants (request/response, message passing), hand the use case to the `sequence-diagram` skill; it records the diagram in `docs/{system-slug}/sequence-diagram.md`.

## Phase 3: Flag Solutions Masquerading as Requirements

Stated requirements are usually full of solutions disguised as needs. You do not have to resolve these here; the drilling technique lives in the `volatility-decomposition` skill. Your job is only to mark them.

For each use case, ask once: "Is this the actual need, or one way of meeting a deeper need?" Where the answer is "one way," note the candidate in a "Solutions to scrub" list so volatility-decomposition can drill into it.

## Phase 4: Write the Spec

Present the consolidated use-case list back to the user for confirmation, then write `docs/{system-slug}/behavioral-requirements.md`:

1. Problem statement: the originating ask quoted verbatim, the pinned baseline every later stage traces to.
2. System summary (one or two sentences).
3. Use cases: each as a numbered behavior, with an activity diagram where Phase 2 warranted one. `composable-design` later marks the core use cases beside their headings.
4. "Solutions to scrub": the flagged candidates from Phase 3.
5. References section.

Write in short, plain, concrete prose.

## Handoff

After saving, offer the next stage: "These use cases are ready. Want me to run volatility-decomposition against them to find what is likely to change?" If yes, that skill reads `docs/{system-slug}/behavioral-requirements.md` as its input.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
