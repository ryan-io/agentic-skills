---
name: concise-technical-writing
description: >
  Tighten an existing document for concision and formatting without losing detail, quality, or
  intent. Use for "make this doc concise", "tighten this plan", "cut the buzzwords", or any
  editorial pass on a doc: bottom line up front, headers with bullets over paragraphs, verbs over
  nominalizations, no buzzwords, split long sentences. Preserves every fact, number, path,
  decision, trade-off, and caveat, and overwrites only after developer confirmation.
---

# Concise Technical Writing

Project documentation grows verbose, not terse: decision records restate their own context, plans pad decisions with hedges, architecture notes bury the claim under setup. This skill retrofits an existing document to be concise and well formatted without dropping a single detail. The full standard is inlined below; the skill stands alone.

## The standard

- **No em dashes.** A hard rule, not a preference. Use a comma, a colon, parentheses, or a separate sentence instead. The same applies to the en dash used as sentence punctuation; reserve the en dash for numeric ranges.
- **Shape of a paragraph.** Short: three or four sentences, one topic. Open with the claim, follow with supporting specifics, close.
- **Sentence structure.** Plain declarative: subject, verb, object. Sentences lean medium-short; stacked subordinate clauses get broken in two. First person is normal ("I am writing to recommend," "I have observed"); contractions are fine. Professional but not stiff.
- **Specifics.** Name things by what they actually are: names, dates, versions, file paths.
- **One idea per paragraph.** If a paragraph lists multiple forces, constraints, or reasons, split it. Multi-point paragraphs disguised as prose are the most common source of bloat in decision records and design docs.
- **What to cut.** Filler transitions, hedge-adverbs, throat-clearing openers ("This is one of the most important..."), and sentences that show the writer thinking rather than communicate. If a sentence can be deleted without information loss, delete it.
- **Format.** Prefer headers with bullet points over paragraphs. Break a section that stacks multiple points into a header plus bullets; keep a flowing paragraph only where the content is genuinely narrative and a list would fragment it.
- **Agent responses.** Output follows these same rules. Be direct. If the answer is uncertain, say so and ask rather than guess.
- **Scope and exceptions.** Applies to human-readable prose. Not to code comments (terse and technical is fine), generated structured output (JSON, YAML, CSV), genuinely parallel lists, or frontmatter and metadata blocks.

## Consumable output

Working memory is limited, so output must minimize the gap between reading and acting. Applies to agent responses and action-oriented docs (plans, work orders, test plans):

- Lead with the action or conclusion, not context.
- Number multi-step work; each step is one bounded action.
- End with one concrete next step.
- Suppress tangents: finish the current issue, offer secondary problems separately.
- Restate state when work spans turns ("step 3 of 5 done: schema updated").
- Give specific estimates (minutes, not "a bit").
- Make wins visible: show what now works and how to try it.
- Matter-of-fact errors: cause and fix, no drama.
- Cap lists at 5 items; split longer ones into "do now" vs "later".
- No preamble, no recap, no closers.

Break these for genuine explanation, destructive actions, or real ambiguity. The conciseness-without-loss constraint below still wins.

## The one hard constraint

Conciseness without loss. The edit cuts words, never information.

- Every fact, number, file path, decision, trade-off, caveat, and named constraint in the original survives the rewrite.
- If a shorter phrasing would drop a detail, the detail wins; cut words elsewhere.
- A tightened document says the same things in fewer words, never fewer things.

Never: invent content, soften or change a recorded decision, alter a status or a date, reorder a templated document's sections, or restructure an architecture. This skill edits prose.

If tightening surfaces a real problem (a contradiction, a stale fact, a wrong count), fix it when the correct fact is verifiable against the code or the governing records, and name the fix in the report. If the fact cannot be established, flag it instead of guessing.

## Calibrate to the developer's voice

The developer's own writing is the reference for "natural language". Before rewriting, sample it: their prompts in this session, recent commit messages, or a document they name as the target tone. Match that register, direct, plain, concrete, not a generic corporate-doc voice. When unsure, prefer the phrasing closer to how the developer phrases things.

## Procedure

1. **Resolve the target.** Confirm the file or set of files. For a set, process one at a time so each diff is reviewable. Read each file in full before touching it.

2. **Ground the content.** If the document follows a template or required structure (a decision record, a business rule, an implementation plan), know its required sections so the edit preserves them. The structure is content; only the prose inside is in scope unless the developer asks for reformatting too.

3. **Inventory the details.** List the load-bearing specifics the rewrite must keep: every decision, number, path, version, date, trade-off, and caveat. This is the checklist verified against in step 6.

4. **Rewrite for concision.** Apply the guard:
   - **Bottom line up front.** Open each section with its conclusion, then support it.
   - **Verbs, not nominalizations.** "decide", not "make a decision"; "because", not "due to the fact that".
   - **No buzzwords or empty intensifiers.** Cut "leverage", "robust", "seamless", "powerful", "very", "significantly". Name the thing plainly.
   - **Say it once.** Delete restatement kept "for emphasis".
   - **Split long sentences.** Over ~25 words or three stacked clauses, break or trim.
   - **Headers and bullets over prose.** Convert a prose section that stacks points into a header plus bullets; keep a paragraph only for genuinely narrative content. Restructuring never drops a detail.
   - **Consumable output.** For action-oriented docs (plans, work orders, test plans), apply the consumable-output rules above: action first, numbered bounded steps, one concrete next step, lists capped at 5.
   - Honor the hard rules: no em dashes, one idea per paragraph.

5. **Report the change.** Show the developer what changed before overwriting:
   - The length delta (before/after word or character count).
   - What was cut and why (buzzwords removed, restatement collapsed, sentences split), or a section-by-section before/after for a heavy edit.
   - Explicit confirmation that the step-3 inventory is fully present in the rewrite.

6. **Verify no loss, then confirm.** Re-check the rewrite against the step-3 inventory: every detail accounted for. State that it holds. Ask the developer to confirm before overwriting. Save to the same path; do not rename unless asked.

## Boundaries

This skill retrofits prose already on disk; writing to the standard in the first place is what keeps docs from needing it.

It owns no document's structure. The pipeline artifacts under `docs/{system-slug}/` answer to the skill that writes each one: `behavioral-requirements`, `volatility-decomposition`, `architecture-layering`, `composable-design`, `implementation-planning`, `sequence-diagram`. Run this skill after a doc is written or when an old doc reads long, and route any structural or content problem back to the owning skill rather than fixing it inside the prose pass.
