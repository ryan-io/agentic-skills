---
name: system-context
description: >
  Invoke implicitly when work leans on a library, framework, package version, API behavior, or
  external fact the repo does not answer, before coding or designing against it. Explicitly on
  "what version of X", "does X support Y", "why does X break when", "where is X decided",
  "research X". Resolves through docs/research/research-index.md first and opens one note; when
  no note answers, gathers primary-source evidence with dates into docs/research/{slug}.md and
  indexes it. Notes are evidence, not decisions: ADRs win.
tags: [research, skill]
---

# System Context

Answer questions about dependencies and external facts from notes in `docs/research/`; add a note when none answers. A note holds the evidence behind a decision (version, API surface, tradeoffs, gotchas); the decision lives in an ADR or design doc.

## When it applies

- **Implicitly**, before coding or designing against a library, framework, or external behavior, when memory is not enough. Versions shift; notes carry a `verified` date.
- **Explicitly**, when the developer asks what the current facts are or where something is decided.

## Index first

Read `docs/research/research-index.md` first. Match the question to one row, then open only what it points to. One note usually answers, sometimes with its ADR. Never scrape the directory.

Index row format (one table, edit by hand):

```markdown
| Note | Topic | Governing record | Verified | Synopsis |
|------|-------|------------------|----------|----------|
| [<slug>](<slug>.md) | <library or concern> | <ADR path, or -> | YYYY-MM-DD | <one line> |
```

A question spanning more than research ("everything we know and decided about caching")? Open `docs/adr/adr-index.md` and `docs/systems/systems-index.md` (`system-map`) alongside, then return here for the evidence.

## How to answer

- Lead with the project's decision, then the external facts behind it.
- "How should I build X": the ADR or design doc is authoritative; the note is supporting evidence. Cite both.
- "What is the current version or API": the note is authoritative. Quote names and versions exactly; give the source URL from the note's Sources list.
- Check the `verified` date. A stale date on a version-sensitive answer means re-verify before relying on it.
- An unverified assumption flagged in a note travels into the answer as a caveat, not a settled fact.
- Label claims known (cited), inferred, or assumed.

## Write a new note

When no note answers and the fact matters to the work:

1. Gather primary sources first: official docs for the installed version, release notes, changelogs, the source repository, issue trackers. Confirm the installed version from the project's package manifest before researching.
2. Write `docs/research/{slug}.md`:

   ```markdown
   ---
   title: <topic>
   verified: YYYY-MM-DD
   governing_record: <ADR path, or none>
   tags: [<sorted>]
   ---

   ## Summary          (the answer in three lines)
   ## Facts            (version, API surface, behavior; each with its source)
   ## Tradeoffs        (options and their costs, where relevant)
   ## Open questions
   ## Sources          (URL, publisher, date accessed)
   ```

3. Add the index row. Confirm with the developer before saving.
4. A new third-party dependency is a decision, not research: the note supports an ADR (`adr-creation`); it never substitutes for one.

## Revise an existing note

- Read the note and its index row first.
- Refresh the facts, bump `verified`, and confirm the index synopsis still holds. Preserve the frontmatter and the Sources convention.
- Confirm with the developer before overwriting; save to the same path.

## Boundaries

- Notes are external evidence, not decisions. Never restate or amend a decision from a note.
- A note and an ADR disagree? The ADR wins and the note needs a fix. Surface it; do not silently follow the note.
- It never commits; at most it suggests a commit subject and stops.
