---
name: concise-technical-writing
description: >
  Tighten an existing document for concision and formatting without losing detail, quality, or
  intent. Use for "make this doc concise", "tighten this plan", "cut the buzzwords", or any
  editorial pass on a doc: bottom line up front, verbs over nominalizations, no buzzwords,
  split long sentences. Preserves every fact, number, path, decision, trade-off, and caveat,
  and overwrites only after developer confirmation.
---

# Concise Technical Writing

Project documentation grows verbose, not terse: decision records restate their own context, plans pad decisions with hedges, architecture notes bury the claim under setup. This skill retrofits an existing document to be concise and well formatted without dropping a single detail. The full standard is inlined below; the skill stands alone.

## The standard

- **No em dashes.** A hard rule, not a preference. Use a comma, a colon, parentheses, or a separate sentence instead. The same applies to the en dash used as sentence punctuation; reserve the en dash for numeric ranges.
- **Shape of a paragraph.** Short: three or four sentences, one topic. Open with the claim, follow with supporting specifics, close.
- **Sentence structure.** Plain declarative: subject, verb, object. Sentences vary in length but lean medium-short; stacked subordinate clauses get broken in two. First person is normal ("I am writing to recommend," "I have observed"); contractions are fine. The voice is professional but not stiff.
- **Specifics.** Name things by what they actually are. Be concrete: names, dates, versions, file paths.
- **One idea per paragraph.** Each paragraph makes one point. If a paragraph lists multiple forces, constraints, or reasons, split it. Multi-point paragraphs disguised as prose are the most common source of bloat in decision records and design docs.
- **What to cut.** Filler transitions, hedge-adverbs, throat-clearing openers ("This is one of the most important..."), and sentences that exist to show the writer is thinking rather than to communicate. If a sentence can be deleted without information loss, delete it.
- **Format.** Default to flowing paragraphs. Headers and bullets only when the content is genuinely a parallel set of items.
- **Agent responses.** Output follows these same rules. Be direct. If the answer is uncertain, say so and ask rather than guess.
- **Scope and exceptions.** Applies to human-readable prose. Does not apply to code comments (terse and technical is fine), generated structured output (JSON, YAML, CSV), lists that are genuinely parallel sets, or frontmatter and metadata blocks.

## The one hard constraint

Conciseness without loss. The edit cuts words, never information. Every fact, number, file path, decision, trade-off, caveat, and named constraint in the original must survive in the rewrite. If a shorter phrasing would drop a detail, the detail wins and you cut words elsewhere. A tightened document says the same things in fewer words, never fewer things. This is the line the developer cares about most: more concise and better formatted, never at the cost of detail, quality, or intent.

What this skill never does: invent content, soften or change a recorded decision, alter a status or a date, reorder a templated document's sections, or restructure an architecture. It edits prose. If tightening surfaces a real problem in the content (a contradiction, a stale fact, a wrong count), fix it on the spot when the correct fact is verifiable against the code or the governing records, and name the fix in the report. If the fact cannot be established, flag it to the developer instead of guessing.

## Calibrate to the developer's voice

The developer's own writing is the reference for "natural language". Before rewriting, sample how the developer actually writes: their prompts in this session, recent commit messages, or a document they point to as the target tone. Match that register, direct, plain, concrete, not a generic corporate-doc voice. When unsure whether a phrasing fits, prefer the one closer to how the developer phrases things.

## Procedure

1. **Resolve the target.** Confirm the file or set of files. For a set, process one at a time so each diff is reviewable. Read each file in full before touching it.

2. **Ground the content.** If the document follows a template or a required structure (a decision record, a business rule, an implementation plan), know its required sections so the edit preserves them. The structure is content; only the prose inside is in scope unless the developer asks for reformatting too.

3. **Inventory the details.** Before rewriting, list the load-bearing specifics the rewrite must keep: every decision, number, path, version, date, trade-off, and caveat. This is the checklist the rewrite is verified against in step 6.

4. **Rewrite for concision.** Apply the guard:
   - **Bottom line up front.** Open each section with its conclusion, then support it.
   - **Verbs, not nominalizations.** "decide", not "make a decision"; "because", not "due to the fact that".
   - **No buzzwords or empty intensifiers.** Cut "leverage", "robust", "seamless", "powerful", "very", "significantly". Name the thing plainly.
   - **Say it once.** Delete restatement kept "for emphasis".
   - **Split long sentences.** Over ~25 words or three stacked clauses, break or trim.
   - **Format only where it earns it.** Convert a buried parallel set into a list; convert a list that reads as prose back into a paragraph. Do not restructure beyond what concision and readability need.
   - Honor the hard rules: no em dashes, one idea per paragraph.

5. **Report the change.** Show the developer what changed before overwriting:
   - The length delta (before/after word or character count).
   - A short list of what was cut and why (buzzwords removed, restatement collapsed, sentences split), or a section-by-section before/after for a heavy edit.
   - An explicit confirmation that the detail inventory from step 3 is fully present in the rewrite.

6. **Verify no loss, then confirm.** Re-check the rewrite against the step-3 inventory: every detail accounted for. State that it holds. Then ask the developer to confirm before overwriting. Save to the same path; do not rename unless asked.

## Boundaries

This skill is the retrofit tool for prose already on disk; writing new prose to this standard in the first place is what keeps docs from needing it. It does not own any document's structure: the pipeline artifacts under `docs/{system-slug}/` answer to the skill that writes each one (`behavioral-requirements`, `volatility-decomposition`, `architecture-layering`, `composable-design`, `implementation-planning`, `sequence-diagram`). Run it after a doc is written or when an old doc reads long, and route any structural or content problem it surfaces back to the owning skill rather than fixing it inside the prose pass.
