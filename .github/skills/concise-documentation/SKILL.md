---
name: concise-documentation
description: >
  Tighten an existing document for concision and formatting without losing detail, quality, or
  intent. Use for "make this doc concise", "tighten this plan", "cut the buzzwords", or any
  editorial pass on a doc: bottom line up front, headers with bullets over paragraphs, verbs over
  nominalizations, no buzzwords, split long sentences. Preserves every fact, number, path,
  decision, trade-off, and caveat, and overwrites only after developer confirmation.
tags: [documentation, writing, skill]
---

# Concise Documentation

Documentation grows verbose, not terse. This skill retrofits an existing document to be concise and well formatted without dropping a single detail. The full standard is inlined below; the skill stands alone.

## The standard

- **No em dashes.** Hard rule. Use a comma, colon, parentheses, or a new sentence. Same for the en dash as sentence punctuation; reserve it for numeric ranges.
- **Paragraph shape.** Three or four sentences, one topic. Open with the claim, support it, close.
- **Sentences.** Plain declarative: subject, verb, object. Medium-short. Break stacked subordinate clauses in two. First person and contractions are fine. Professional, not stiff.
- **Specifics.** Name things: names, dates, versions, file paths.
- **One idea per paragraph.** A paragraph listing multiple forces or reasons gets split. Multi-point paragraphs disguised as prose are the top source of bloat.
- **What to cut.** Filler transitions, hedge-adverbs, throat-clearing openers, sentences that show the writer thinking. If deleting a sentence loses nothing, delete it.
- **Format.** Prefer headers with bullets over paragraphs. Keep a flowing paragraph only for genuinely narrative content.
- **Agent responses follow the same rules.** Be direct. Uncertain? Say so and ask.
- **Scope.** Human-readable prose only. Not code comments (`xml-documentation.instructions.md` governs those), generated structured output, genuinely parallel lists, or frontmatter.

## Consumable output

For agent responses and action-oriented docs (plans, work orders, test plans), minimize the gap between reading and acting:

- Lead with the action or conclusion.
- Number multi-step work; one bounded action per step.
- End with one concrete next step.
- Suppress tangents; offer secondary problems separately.
- Restate state when work spans turns ("step 3 of 5 done: schema updated").
- Specific estimates (minutes, not "a bit").
- Make wins visible: what now works and how to try it.
- Matter-of-fact errors: cause and fix, no drama.
- Cap lists at 5; split longer into "do now" vs "later".
- No preamble, no recap, no closers.

Break these for genuine explanation, destructive actions, or real ambiguity. The no-loss constraint below still wins.

## The one hard constraint

**Conciseness without loss.** The edit cuts words, never information.

- Every fact, number, path, decision, trade-off, caveat, and named constraint survives the rewrite.
- A shorter phrasing that drops a detail loses; the detail wins.
- Never: invent content, soften a recorded decision, alter a status or date, reorder a templated document's sections, or restructure an architecture. This skill edits prose.
- Tightening surfaced a real problem (contradiction, stale fact, wrong count)? Fix it when verifiable against the code or the records, and name the fix in the report. Otherwise flag it; don't guess.

## Calibrate to the developer's voice

- The developer's own writing is the reference. Sample it: their prompts, recent commit messages, or a document they name.
- Match that register: direct, plain, concrete. Not corporate-doc voice. When unsure, prefer their phrasing.

## Procedure

1. **Resolve the target.** Confirm the file(s). Process a set one at a time so each diff is reviewable. Read each file in full first.
2. **Ground the content.** If the document follows a template (an ADR, an implementation plan), know its required sections. Structure is content; only the prose inside is in scope unless reformatting is requested.
3. **Inventory the details.** List the load-bearing specifics the rewrite must keep: every decision, number, path, version, date, trade-off, caveat. This is the checklist for step 6.
4. **Rewrite for concision.**
   - Bottom line up front: open each section with its conclusion.
   - Verbs, not nominalizations: "decide", not "make a decision".
   - No buzzwords or empty intensifiers: cut "leverage", "robust", "seamless", "very", "significantly".
   - Say it once. Delete restatement kept "for emphasis".
   - Split sentences over ~25 words or three stacked clauses.
   - Headers and bullets over prose; restructuring never drops a detail.
   - Apply the consumable-output rules to action-oriented docs.
   - Honor the hard rules: no em dashes, one idea per paragraph.
5. **Report the change.** Before overwriting, show: the length delta; what was cut and why (or section-by-section before/after for a heavy edit); confirmation the step-3 inventory survives.
6. **Verify no loss, then confirm.** Re-check against the inventory. State that it holds. Get the developer's confirmation before overwriting. Same path; no renames unless asked.

## Boundaries

- This skill retrofits prose already on disk. Writing to the standard in the first place is what keeps docs from needing it.
- It owns no document's structure. The sections of `docs/design/{slug}-design.md` answer to the skill that writes each one: `pipeline-stg1-requirements`, `pipeline-stg2-volatilities`, `pipeline-stg3-architecture`, `pipeline-stg4-validation`, `pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`, `sequence-diagram-creation`. Route structural or content problems to the owner; fix only prose here.
