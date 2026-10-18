---
name: adr-creation
description: >
  Interactively create an Architecture Decision Record (ADR). Invoke implicitly when a new
  architectural pattern, cross-cutting concern, or third-party dependency is about to land
  without a record: offer the ADR before the code. Explicitly on "new ADR", "create an ADR",
  "document this architectural decision", or "record this design decision". Walks each section
  of the ADR template, validates against the ADR review policy, saves to docs/adr/, and adds
  the docs/adr/adr-index.md row. Also revises a saved ADR.
tags: [adr, process, skill]
---

# ADR Creation

Create a complete, policy-compliant ADR by walking the developer through each section interactively.

## Prerequisites

Read before starting:

- `.github/docs/adr-template.md`: section structure and placeholder guidance.
- `.github/docs/writing-voice-guide.md`: the writing standard for all prose drafted here.

Prose rules throughout: short paragraphs, plain declarative sentences, no em dashes, no filler. Every sentence earns its place.

The review policy (`adr-pr-review.instructions.md`) and template policy (`adr-template.instructions.md`) auto-load when working in `docs/adr/`.

## Ground first

Ground the decision so it neither duplicates nor contradicts the record. Index-first; never scrape a directory.

- `docs/adr/adr-index.md`: an Active or Proposed ADR already governing the area? Extend or supersede it rather than duplicate it.
- `docs/systems/systems-index.md` (`system-map`): the systems the decision binds.
- `docs/design/`: a design doc whose `## Architecture` or open questions the decision settles; cite it.

Open only the records that govern.

## Workflow

### Step 1: Identify the decision

Ask:

- What is the architectural decision? (short title, imperative phrase)
- What is the project prefix for the filename? (e.g., `SOC`, `GRID`, `APP`)

Derive the filename: `adr-{project}-{kebab-case-title}.md`.

### Step 2: Forces discovery

Before writing Context, surface the forces with three questions:

1. **What goes wrong if we do nothing?** Identify the pain. No cost to inaction may mean no ADR is needed.
2. **What constraints does our environment impose that a textbook wouldn't assume?** Desktop vs. web, team size, existing stack, deployment model.
3. **Where do quality attributes conflict?** Testability vs. simplicity, performance vs. maintainability, flexibility vs. cognitive load.

Every force creates tension the Decision resolves and the Consequences acknowledge. A force that does not connect to the decision does not belong.

### Step 3: Walk through sections

Present each section one at a time. Draft it from the developer's input and confirm before moving on.

- **Metadata.** Status `Active`, Date today. Ask for Authors (GitHub handle). An optional `| Tags | [...] |` row holds free-text keywords, lowercase and sorted. Never leave bracketed placeholders in a saved ADR.
- **Context.** Draft from the Step 2 forces: the problem space, constraints, and quality attributes. Reject vague or generic text; ask follow-ups. One force per paragraph.
- **Decision.** Active voice, explicit rationale referencing the Context tradeoffs. State what was chosen and why.
- **Other Considerations.** Each alternative evaluated: what it solves, why it was not chosen or how it complements the decision, whether it may be revisited. If only one option was viable, say so and why. One paragraph per alternative, bold lead.
- **Consequences.** Ask for pros, cons, and technical debt; write "None" if there is no debt. Every Context force appears here. Bullets for pros and cons; debt as prose. Debt with a revisit trigger also gets a `tech-debt` row.
- **Enforcement / Guidance.** Concrete and actionable. Ask: "How will the team verify conformance?" Linter rules, CI checks, review criteria, naming conventions, automated tests. Bullets fit here.

### Step 4: Validate and save

Validate against the rejection criteria in `adr-pr-review.instructions.md`:

- All required sections present with substantive content.
- No placeholder text remains.
- Status is `Active`, `Proposed`, or `Archived`.
- Filename matches `adr-{project}-{kebab-case-title}.md`.
- Prose meets the writing standard: no em dashes, no filler, short direct paragraphs.

Save to `docs/adr/` and confirm the path to the developer.

### Step 4b: Update the ADR index

Append one row to `docs/adr/adr-index.md` so the ADR is discoverable without loading it.

- Index absent? Create it with a title and this header row: `| ADR | Status | Context | Synopsis | Tags |`.
- Row cells: the ADR name as a relative link, its Status, its Context (the subsystem or concern, in the style of existing rows), a one-sentence synopsis of what it governs, and its Tags (copied from Metadata, or empty).
- Read the index first. Touch no other row. Replace a `_None yet._` placeholder row if present.

### Step 5: Revise an existing ADR

- Read the saved file from `docs/adr/` first. Work from its contents, not memory.
- Apply the change. Keep every other section, the metadata, and the writing conventions intact.
- Change alters the decision itself, not its wording? Raise whether Status moves to `Archived` with a new superseding ADR. Never silently rewrite history.
- Re-validate against Step 4. Confirm before overwriting. Save to the same path; a title change derives a new filename, and tell the developer the old file is orphaned.
- Status, Context, scope, or filename changed? Update the index row in the same pass. A row never drifts from its file.

## Boundaries

- This skill records decisions; it does not make them. Options and the recommendation come from the developer conversation; a choice the developer has not made is a question, not a draft.
- Never commit. Suggest a commit subject (`docs(adr): ...`) and stop.
