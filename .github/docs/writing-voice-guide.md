# Writing Voice Guide

The project's writing standard. The always-on anchor is the Concise Technical Writing section of `CLAUDE.md` / `.github/copilot-instructions.md`; the `concise-documentation` skill applies it to existing docs (the former `writing-voice.instructions.md` rule was folded in here, 2026-08-11). Read this before writing documentation, ADR narratives, or prose-heavy content.

## Specifics: Examples

"C# and C++", not "modern programming languages". "MATLAB scripts to determine root cause failures for testing fixtures", not "analytical scripts". "Leading Self Program in 2018", not "a recognized leadership program."

A concrete noun and a date will usually carry more conviction than three adjectives.

## What to Cut: Examples

Filler transitions to eliminate: "Moreover," "Furthermore," "It is worth noting that," "Additionally," "In conclusion."

Hedge-adverbs to replace with specifics: "very," "really," "quite," "significantly," "extremely."

If a paragraph opens with "I think" or "It is important to note," delete the opener. The sentence is stronger without it.

## What's Allowed

Standard professional phrases are fine when they fit. "Valuable asset to the team," "strong leader and collaborator," "takes ownership of his work" are reasonable in their place. The goal is clarity and brevity, not novelty or austerity. Avoid them only when they replace a specific that would carry more weight.

When a limitation or gap exists, name it directly and pivot to what compensates. Do not omit it or bury it. In an ADR this means stating trade-offs plainly. In a PR comment it means saying "this doesn't cover X" rather than hoping nobody notices.

## Format: When to Use Structure

Prefer headers with bullet points over paragraphs (developer directive, 2026-08-11). For most content, a header naming the topic plus a bullet per point is more concise, more technical, and easier to consume than prose, for agents and humans alike. Break a section that stacks multiple points, forces, or reasons into bullets; each bullet still leads with its claim.

Paragraphs have their place: genuinely narrative content, a causal chain, or an argument whose sentences depend on each other. If bulleting would fragment the reasoning, keep the paragraph, and keep it short: three or four sentences, one topic, claim first.

## Conversational Style

In informal contexts (chat, casual notes, PR comments) the voice drops formality. Functional, not decorative. Don't replicate typos in formal output, but match the directness. Short, lowercase sentence openers are fine in chat. In formal deliverables, standard capitalization applies.

## Voice: The Active Register (added 2026-10-18, made swappable 2026-10-19)

Developer directive, 2026-10-18: agent output keeps every concision rule in this guide and adds a human register. Developer directive, 2026-10-19: the register is swappable at will. Each register is one file under `.github/docs/voices/`; the active one is generated into `voice.instructions.md` in both rule trees by `scripts/set-voice.sh` or the `voice` skill (`/voice <name>`). Default: `jarvis` (Iron Man): a calm, dry, unflappable colleague who is candid without ceremony. Library table and file contract: `.github/docs/voices/README.md`.

Invariants that hold in every voice:

- The concision rules in this guide and the entry points bind. A voice changes tone, never the word budget.
- Formal records (ADRs, business rules, plans, design docs, system nodes) keep the neutral documentary voice.
- Scope is human-readable prose: agent responses and chat, not code comments, structured output, or metadata.
- Destructive-action confirmations carry no wit.
- Tone, not words: if a flourish and a fact compete for the sentence, the fact stays.

## Conciseness: The Guard Against Verbose Docs

This section is the deeper how of the conciseness guard. The project's failure mode is the opposite of most writing advice: docs here grow long, dense, and self-referential, not terse. ADRs restate their own context three ways, plans pad decisions with hedges, architecture notes bury the claim under a paragraph of setup. The fixes below are standard technical-writing practice, not house invention. The `concise-documentation` skill applies them to an existing document on demand.

### Bottom line up front (BLUF)

Lead with the conclusion, then support it. A reader should get the decision from the first sentence of a section, not the last. This is the single highest-leverage move: it lets a reader stop early and forces you to know your own point.

Before: "There are several factors to weigh here. The current cache is in-process, the service scales to three nodes next quarter, and session state must survive a node restart. Given all of this, we will not keep session state in memory."

After: "We will not keep session state in memory. The service scales to three nodes next quarter, and sessions must survive a node restart."

### Cut nominalizations: verbs, not noun-phrases

A nominalization is a verb turned into a noun, which then needs a weak helper verb. It is almost always longer and vaguer than the verb it came from.

- "make a decision" -> "decide"
- "perform a validation of" -> "validate"
- "provide an explanation" -> "explain"
- "due to the fact that" -> "because"
- "in order to" -> "to"
- "has the ability to" -> "can"
- "is responsible for managing" -> "manages"

### Cut buzzwords and empty intensifiers

Name the thing by what it does. Buzzwords signal effort, not meaning, and the reader reads them as noise.

Cut on sight: leverage, robust, seamless, powerful, cutting-edge, best-in-class, holistic, synergy, streamlined, frictionless, first-class (unless it is the project's defined term). Intensifiers that add nothing: very, really, quite, extremely, significantly, highly, incredibly.

Before: "This provides a robust, seamless mechanism for leveraging the powerful capabilities of the service layer."

After: "This routes commands through the service layer's one entry point."

### Common wordy phrases and their fix

- "at this point in time" -> "now"
- "in the event that" -> "if"
- "for the purpose of" -> "for" / "to"
- "a large number of" -> "many"
- "in the process of" -> (drop it)
- "it should be noted that" -> (drop it)
- "the reason for this is that" -> "because"

### Say it once

The densest source of bloat in this project's docs is restatement: a paragraph makes a point, then a second sentence makes the same point in different words "for emphasis", then a parenthetical makes it a third time. Keep the clearest one. If two sentences carry the same fact, delete the weaker.

### Plain sentences: density is also fluff (added 2026-07-08)

Developer feedback, 2026-07-08: session outputs were verbose, sentences needlessly complicated, hard to follow. The failure was not padding but density. Stacked clauses, parentheticals, and chained record codenames compress many facts into sentences nobody can parse. The fixes:

- One idea per sentence. Split anything past ~20 words or with stacked clauses.
- Plain words before record ids: "admin accounts are exempt from the login rate limit (BR-7)", never the codename alone. A reply must be understandable without opening what it cites.
- A session summary is a few short sentences and a short list, not a mirror of the document just written.
- A document-sized response gets the `concise-documentation` treatment before sending.

Before: "AV5, the order-outcome-to-loyalty mapping, insulates open Q-10 via the ledger's V1 accrual data." After: "What an order feeds into loyalty points sits behind one mapping (AV5). The open points-expiry question (Q-10) can resolve later without touching the design."

### Sound human (added 2026-07-25)

Developer feedback, 2026-07-25, tuning the voice further: sentences must read as human-written, not model-compressed. Three additions:

- No run-on sentences, a hard rule alongside the em-dash ban. A comma splice or a three-clause chain becomes two sentences.
- The read-aloud test: if you would not say the sentence to a teammate across a desk, rewrite it. Grammatical is not the bar; natural is.
- C# XML doc comments are capped at one or two sentences per tag (`xml-documentation.instructions.md`): summary defaults to one sentence, `<remarks>` to one, and the em-dash and run-on bans follow prose into doc comments.

The developer's own writing is the model for the voice: short declarative sentences, concrete nouns, a point per sentence, no ornament.

### Cut 40 to 60 percent (added 2026-10-19)

Developer directive, 2026-10-19: output was still too long. Every response gets a cutting pass that removes about half its words. Plain language, no fluff, say more with less.

- Draft, then cut 40 to 60 percent before sending. Facts survive; words go.
- Aim for 12 words a sentence; 20 is the ceiling, not the target.
- One sentence per bullet. Five bullets max.
- Drop the setup sentence that announces what the next sentence says.

Before (31 words): "Write access gets broader. Every added directory gets the same read and edit permissions as the working directory. One mistaken edit can land in a repo you only meant to reference."
After (14 words): "Every added directory is writable. One wrong edit can land in a reference repo."

The Jarvis voice was retuned the same day to match: short status lines with a number in them. Grounding: his lines in [Iron Man (2008), Wikiquote](https://en.wikiquote.org/wiki/Iron_Man_(film)) run under 12 words ("The render is complete."), and commentary describes the delivery as calm, measured, and dry ([joshworth.com](https://joshworth.com/hal/3/)).

### Conciseness without loss is the hard constraint

This is the line the project cares about most, from the developer: more concise and better formatted, never at the cost of detail, quality, or intent. Conciseness is cutting words, not cutting information. Every fact, number, file path, decision, trade-off, caveat, and named constraint must survive the edit. If a shorter phrasing would drop a detail, the detail wins and you cut words somewhere else. A tightened doc says the same things in fewer words, never fewer things.

### The self-check before saving

Read the draft once more and ask: does each paragraph lead with its point? Can any sentence be cut without losing a fact? Is any nominalization, buzzword, or restatement still here? Is any sentence over ~25 words that should be two? Fix what the pass surfaces, then save.

### Sources

Standard plain-language and technical-writing practice, not house rules:

- Federal plain-language guidelines, [archives.gov 10 principles](https://www.archives.gov/open/plain-writing/10-principles.html) (omit needless words, verbs over nominalizations, active voice, everyday words).
- [Plain Language Advances Technical Communication](https://centerforplainlanguage.org/plain-language-advances-technical-communication/), Center for Plain Language.
- BLUF (bottom line up front): lead with the essential message before the detail and qualifiers.
