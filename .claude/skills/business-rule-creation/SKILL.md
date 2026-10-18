---
name: business-rule-creation
description: >
  Interactively create a Business Rule document. Invoke implicitly when the developer states a
  domain constraint ("an order can never ship before payment clears", "a user may hold at most
  one active session") that no record carries: offer to capture it. Explicitly on "new business
  rule", "create a business rule", "document a domain constraint", or "capture a business
  requirement". Walks each section to capture the rule's intent, conditions, and exceptions,
  saves to docs/business-rules/, and adds the docs/business-rules/br-index.md row. Also revises
  a saved rule.
tags: [business-rule, process, skill]
---

# Business Rule Creation

Create a complete business rule document by walking the developer through each section interactively.

## Prerequisites

Read the template first: `.github/docs/br-template.md`. The review policy (`br-review.instructions.md`) auto-loads when working in `docs/business-rules/`. Prose follows `.github/docs/writing-voice-guide.md`: plain declarative sentences, no em dashes.

## File conventions

- Filename lowercase: `br-{project}-{kebab-case-title}.md`.
- Heading uppercase: `# BR-PROJECT: [Short Title]`.
- Save to `docs/business-rules/`.

## Workflow

### Step 1: Identify the rule

Ask:

- What is the business rule? (short title, imperative phrase)
- What is the project prefix? (e.g., `SOC`, `GRID`, `APP`)
- What domain or feature area does it belong to?

Derive the filename: `br-{project}-{kebab-case-title}.md`.

### Step 2: Discovery

Ground the rule index-first; never scrape a directory. A new rule that contradicts an Active ADR or duplicates an existing rule is the failure this step prevents.

- `docs/business-rules/br-index.md`: a rule already covering the domain is extended, not duplicated.
- `docs/adr/adr-index.md`: the Active decisions the rule must stay consistent with.
- `docs/systems/systems-index.md` (`system-map`): the systems the rule constrains.
- `docs/design/`: a design doc's `## Requirements` may hold the rationale the rule should cite.

Then surface the rule's intent with three questions:

1. **What business outcome does this rule protect?** Revenue, compliance, data integrity, user safety.
2. **What triggers this rule?** A user action, a system event, a time condition, a data state.
3. **What happens if this rule is violated?** The business impact of non-compliance.

### Step 3: Walk through sections

Present each section one at a time. Draft it from the developer's input and confirm before moving on.

- **Metadata.** Date today. Ask for Authors, Status (`Active` or `Archived`, default `Active`), Domain, and Related ADRs (default "None"). An optional `| Tags | [...] |` row holds free-text keywords, lowercase and sorted.
- **Description.** Plain-language statement of the rule. Specific and unambiguous. One rule per document.
- **Conditions.** When the rule applies: the triggering context, inputs, and preconditions.
- **Expected Behavior.** What must happen when the rule triggers. Define the outcome precisely.
- **Exceptions.** Cases where the rule does not apply. If none, write "None".

### Step 4: Validate and save

Validate against `br-review.instructions.md`:

- All required sections present with substantive content.
- No placeholder text remains.
- Filename lowercase and matches `br-{project}-{kebab-case-title}.md`.

Save to `docs/business-rules/` and confirm the path to the developer.

### Step 4b: Update the business rule index

Append one row to `docs/business-rules/br-index.md` so the rule is discoverable without loading it.

- Index absent? Create it with a title and this header row: `| Rule | Status | Domain | Related ADRs | Synopsis | Tags |`.
- Row cells: the rule name as a relative link, its Status, Domain, and Related ADRs (copied from Metadata), a one-sentence synopsis of what it governs, and its Tags (or empty).
- Read the index first. Touch no other row. Replace a `_None yet._` placeholder row when adding the first rule.

### Step 5: Revise an existing business rule

- Read the saved file from `docs/business-rules/` first. Work from its contents, not memory.
- Apply the change. Keep every other section and the metadata intact. A change that introduces a second rule becomes a separate file.
- Re-validate against Step 4. Confirm before overwriting. Save to the same path; a title change derives a new lowercase filename, and tell the developer the old file is orphaned.
- Status, Domain, Related ADRs, scope, or filename changed? Update the index row in the same pass. A row never drifts from its file.

## Boundaries

- This skill records a rule the developer states; it never invents one. An unclear condition or exception is a question.
- A rule that would contradict an Active ADR stops here and goes to the developer.
- Never commit. Suggest a commit subject (`docs(br): ...`) and stop.
