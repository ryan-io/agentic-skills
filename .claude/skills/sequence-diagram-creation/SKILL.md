---
name: sequence-diagram-creation
description: >
  Create a Mermaid sequence diagram from a structured spec or natural-language
  description. Guides the user through participants, messages, and interaction
  patterns (loops, conditionals, parallel flows), then records the diagram as a
  titled subsection with a Mermaid code block. Use for "sequence diagram", "interaction
  diagram", "message flow", "call sequence", or a workflow between actors or
  components that the user wants diagrammed. Records diagrams inline in
  docs/design/{slug}-design.md, inside the section their flow belongs to; serves the
  design pipeline (pipeline-stg4-validation call chains) and runs standalone.
tags: [design-pipeline, diagrams, skill]
---

# Sequence Diagram Creation

Create a Mermaid sequence diagram from user input. Ask targeted questions to pin down participants, message flow, and interaction patterns, then record the diagram in the design doc.

## Where diagrams live

- Inline in `docs/design/{slug}-design.md`, inside whichever section the flow belongs to: a use case's diagram beside it in `## Requirements`, a call chain's in `## Validation`, a build flow's in `## Implementation Plan`.
- `{slug}` is the kebab-case system name the pipeline uses. Confirm it with the user; derive it from the subject when running standalone.
- Confirm the host section with the user. If the design doc does not exist, create it and add only the host section.

Each diagram is one titled subsection inside its host section:

1. A `### seq-{kebab-case-title}` heading.
2. A brief description of the interaction.
3. A Mermaid `sequenceDiagram` fenced code block.
4. A References line, if the diagram derives from an external source.

Keep the description short. Other skills link a diagram by its subsection: `docs/design/{slug}-design.md#seq-{kebab-case-title}`.

## Workflow

### Step 1: Understand the interaction

Ask (skip if already described): "What interaction do you want to diagram? Who initiates it, what systems or components are involved, what is the end state?"

### Step 2: Identify participants

- Extract participants; confirm: "Here are the participants I see: [list]. Add, remove, or rename any?"
- `participant` for services, systems, databases, queues. `actor` for humans or external callers.
- Use aliases for long names: `participant GW as API Gateway`.
- When the diagram maps a pipeline call chain (`pipeline-stg4-validation`), participants are the services the design doc's `## Architecture` section names, and the chain must obey that skill's call rules. Never invent participants the architecture does not contain.

### Step 3: Map the message flow

Walk the interaction step by step. Per message:

- **Direction:** who sends to whom?
- **Sync or async?** `->>` sync, `-)` async, `-->>` responses.
- **Label:** concise (`POST /orders`, `validate()`, `OrderCreated event`), not a sentence.

Confirm the message list before generating.

### Step 4: Identify interaction patterns

Ask; do not assume:

- **Activations:** "Does a participant actively process while waiting for a response?"
- **Loops:** "Does any part repeat? Retries, polling, batches?"
- **Conditionals:** "Branching paths? Success vs failure?"
- **Parallel flows:** "Anything concurrent?"
- **Notes:** "Any clarifying annotations?"

Include only what the user confirms.

### Step 5: Generate the diagram

```
sequenceDiagram
    autonumber
    actor U as User
    participant A as Service A
    participant B as Service B

    U->>A: request
    activate A
    A->>B: downstream call
    activate B
    B-->>A: response
    deactivate B
    A-->>U: response
    deactivate A
```

Conventions:

- Always `autonumber` unless the user opts out.
- Indent message lines.
- `rect rgb(...)` groupings sparingly, only for user-identified groupings.
- `Note over` spans participants; `Note right of` for one participant.
- Labels over ~40 characters: shorten, and move detail to a Note.
- **Avoid Mermaid control characters in label, note, and alias text.** `;` is a statement separator; `+`/`-` are activation tokens. Prose like `propertyChanged; LoadStatus = ""` or `Register + filter` breaks the parser mid-line. Use a comma, "and", or "then"; rephrase `count++` as `count incremented`. This is the most common cause of a diagram that will not render. Applies only inside the fenced block. (`:` after the first one, `()`, `.`, `/`, `~`, `<br/>`, and a spaced `->` in label text are fine.)

### Step 6: Validate, review, save

Check the source before saving:

- Every label, note, and alias obeys the reserved-character rule above.
- Every `loop`, `alt`/`else`, `par`/`and`, `critical`/`option`, and `rect` closes with `end`.
- Every `activate` has a matching `deactivate`, or the `+`/`-` shorthand is used consistently.
- Every message line references a declared participant or alias, spelled exactly as declared.

Never save a diagram that fails the check.

Present the diagram: "Does this capture the interaction? Anything to add, remove, or reorder?" Iterate until confirmed. Then save the subsection into its host section in the design doc; create the doc or the host section if absent. Touch nothing outside the diagram subsection.

### Step 7: Revise an existing diagram

- Read the diagram's existing `### seq-` subsection first. Work from its contents, not memory.
- Common revisions: wording (labels, title, description); participants (add/remove/rename; a rename updates every message line using the old alias); message flow (add, remove, reorder, arrow types); patterns (loops, conditionals, parallel blocks, activations, notes).
- Keep everything else in the document unchanged. Preserve Step 5 conventions.
- Present and confirm before overwriting, as in Step 6. Re-validate. If the diagram is renamed, update anything that links the old subsection name (the plan's Referenced diagrams, the `## Validation` rows).

## Mermaid syntax reference (for the agent; don't recite)

### Arrows

| Arrow | Meaning |
|---|---|
| `->>` | Synchronous request (solid, filled head) |
| `-->>` | Synchronous response (dashed, filled head) |
| `-)` | Asynchronous message (solid, open head) |
| `--)` | Async response (dashed, open head) |

### Blocks

```
loop Description
    A->>B: message
end

alt Success
    A-->>B: 200 OK
else Failure
    A-->>B: 500 Error
end

par Task 1
    A->>B: message
and Task 2
    A->>C: message
end

critical Establish connection
    A->>B: connect
option Timeout
    A->>A: retry
end
```

### Notes and activations

```
Note right of A: Single participant note
Note over A,B: Spans both participants

activate A
deactivate A

%% Shorthand: +/- suffix on arrows
A->>+B: request
B-->>-A: response
```

## References

- [Mermaid Sequence Diagram Syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)
