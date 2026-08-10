---
name: sequence-diagram
description: >
  Create a Mermaid sequence diagram from a structured spec or natural-language
  description. Guides the user through participants, messages, and interaction
  patterns (loops, conditionals, parallel flows), then records the diagram as a
  titled section with a Mermaid code block. Use for "sequence diagram", "interaction
  diagram", "message flow", "call sequence", or a workflow between actors or
  components that the user wants diagrammed.
---

# Sequence Diagram Creation

Create a Mermaid sequence diagram from user input. The agent asks targeted questions to clarify participants, message flow, and interaction patterns, then records the diagram in the system's diagram document.

## Output

All diagrams for a system live in one document: `docs/{system-slug}/sequence-diagram.md`, where `{system-slug}` is the kebab-case name the pipeline uses for the system (confirm it with the user; derive it from the subject if this skill runs standalone). Create the file on first use with a one-line header naming the system.

Each diagram is one titled section:

1. A `## seq-{kebab-case-title}` heading.
2. A brief description of the interaction being modeled.
3. A Mermaid `sequenceDiagram` fenced code block.
4. A References line, if the diagram derives from a book, paper, or external source.

Keep the description short and plain. Message labels stay concise per Step 5. Other skills link a diagram by its section: `docs/{system-slug}/sequence-diagram.md#seq-{kebab-case-title}`.

## Workflow

### Step 1: Understand the Interaction

Ask what interaction the user wants to diagram. If they've already described it, skip ahead.

"What interaction do you want to diagram? Describe the workflow at a high level: who initiates it, what systems or components are involved, and what the end state is."

### Step 2: Identify Participants

Extract participants from the description. Confirm with the user.

"Here are the participants I see: [list]. Are these correct? Should any be added, removed, or renamed?"

Decide participant types with the user:

- `participant` for services, systems, databases, queues.
- `actor` for humans or external callers.

Use aliases when full names are long: `participant GW as API Gateway`.

When the diagram maps a call chain from the design pipeline (`composable-design`), the participants are the services `architecture-layering.md` names, and the chain must obey that skill's call rules; do not invent participants the architecture does not contain.

### Step 3: Map the Message Flow

Walk through the interaction step by step. For each message, clarify:

- **Direction:** Who sends to whom?
- **Synchronous or asynchronous?** Solid arrow (`->>`) for sync, open arrow (`-)`) for async. Dashed arrows (`-->>`) for responses.
- **Label:** What is the message? Use concise labels: `POST /orders`, `validate()`, `OrderCreated event`, not full sentences.

Present the message list back to the user for confirmation before generating.

### Step 4: Identify Interaction Patterns

Ask whether any of these patterns apply. Do not assume they do.

- **Activations:** "Are there points where a participant is actively processing (waiting for a response before continuing)?"
- **Loops:** "Does any part of this flow repeat? Retry logic, polling, batch processing?"
- **Conditionals:** "Are there branching paths? Success vs. failure, different response types?"
- **Parallel flows:** "Do any messages happen concurrently?"
- **Notes:** "Are there any clarifying details that should appear as annotations on the diagram?"

Only include patterns the user confirms.

### Step 5: Generate the Diagram

Produce the Mermaid code block. Follow these conventions:

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

- Always include `autonumber` unless the user opts out.
- Indent message lines for readability.
- Group related messages with `rect rgb(...)` blocks sparingly, only when the user has identified logical groupings.
- Use `Note over` for annotations that span participants, `Note right of` for single-participant context.
- Keep message labels short. If a label exceeds roughly 40 characters, shorten it and add a Note with the full detail.
- **Avoid Mermaid control characters in label, note, and participant-alias text.** A semicolon (`;`) is a statement separator and `+`/`-` are activation tokens, so prose like `propertyChanged; LoadStatus = ""` or `Register + filter` makes the parser fail mid-line. Use a comma, "and", or "then" instead, and rephrase `count++` to `count incremented`. This is the most common cause of a diagram that will not render. It applies only inside the fenced ```mermaid block; the surrounding markdown prose may use any punctuation. (`:` after the first one, `()`, `.`, `/`, `~`, `<br/>`, and a spaced `->` inside label text are fine.)

### Step 6: Validate, Review, and Save

Validate that the diagram parses before saving, by careful review of the Mermaid source:

- Every label, note, and participant-alias line obeys Step 5's reserved-character rule (a `;` or a `+`/`-` in label text is the most common cause of a diagram that will not render).
- Every `loop`, `alt`/`else`, `par`/`and`, `critical`/`option`, and `rect` block closes with `end`.
- Every `activate` has a matching `deactivate`, or the `+`/`-` arrow shorthand is used consistently instead.
- Every message line references a declared participant or alias, spelled exactly as declared.

Do not save a diagram that fails the review.

Then present the generated diagram to the user. Ask:

"Does this capture the interaction correctly? Anything to add, remove, or reorder?"

Iterate until the user confirms. Then save the section into `docs/{system-slug}/sequence-diagram.md`, appending it if the document exists, creating the document if it does not. Re-validate after any later revision (Step 7).

### Step 7: Revise an Existing Diagram

Use this step when the user wants to change a diagram that is already saved, whether from this session or an earlier one.

Read the existing section from `docs/{system-slug}/sequence-diagram.md` first. Work from its current contents, not from memory.

Apply the requested change. Common revisions:

- **Wording:** Adjust message labels, the section title, or the description prose.
- **Participants:** Add, remove, or rename a participant. When renaming, update every message line that references the old alias.
- **Message flow:** Add, remove, or reorder messages, or change arrow types.
- **Patterns:** Add or remove a loop, conditional, parallel block, activation, or note.

Keep all other sections of the document unchanged. Preserve the conventions from Step 5 (autonumber, indentation, alias usage).

Present the revised diagram and confirm before overwriting, same as Step 6. Save to the same section. Rename the section only if the user renames the diagram, and update any pipeline artifact that links the old section name (the plan's Referenced diagrams, the architecture's `## Validation` rows).

## Mermaid Syntax Reference

Quick reference for the agent. Do not recite this to the user.

### Arrow Types

| Arrow | Meaning |
|---|---|
| `->>` | Synchronous request (solid, filled head) |
| `-->>` | Synchronous response (dashed, filled head) |
| `-)` | Asynchronous message (solid, open head) |
| `--)` | Async response (dashed, open head) |

### Interaction Blocks

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

### Notes

```
Note right of A: Single participant note
Note over A,B: Spans both participants
Note left of B: Left-side note
```

### Activations

```
activate A
deactivate A

%% Shorthand: +/- suffix on arrows
A->>+B: request
B-->>-A: response
```

## References

- [Mermaid Sequence Diagram Syntax](https://mermaid.js.org/syntax/sequenceDiagram.html)
