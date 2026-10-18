---
name: house-keeping
description: >
  Sweep the documentation corpora: verify every *-index.md under docs/ against disk, fix dead
  links and verifiable stale facts on the spot, review ADRs and design docs for staleness, and
  flag ideas and research notes left unreferenced past an age threshold. Use on "run
  housekeeping", "clean up the docs", "are the indexes stale", "find dead links", or as a
  periodic pass. Reports findings; never commits.
tags: [documentation, index, process, skill]
---

# House-Keeping

A periodic maintenance pass over `docs/`. The mechanical half proves what a search can prove (rows against files, link targets, path references). The editorial half judges content against the project's current state. Everything the developer must decide lands in one report at the end.

## Procedure

1. **Inventory.** List every `*-index.md` under `docs/` (`rg --files docs -g '*-index.md'`). Each one is a corpus to verify. Note the corpora with no index; a corpus of more than a handful of records with no index is a finding.
2. **Index against disk.** For each index, both directions:
   - **Row without file.** A row links a path that does not exist. Fix the link if the file moved; otherwise report the orphan row.
   - **File without row.** A record in the corpus directory has no row. Add the row in the index's existing format if the record's frontmatter gives the facts; otherwise report it.
   - **Status drift.** The row's status disagrees with the record's frontmatter or Metadata. The record is the authority; correct the row toward it.
3. **Dead links.** Check every relative markdown link under `docs/` resolves to a real file (and anchor, where one is given). Exclude vendored doc mirrors the project names. Fix each dead link whose correct target is findable; report the rest.
4. **Stale facts.** Fix on the spot any stale fact the repo can verify: a wrong count, a moved path, a renamed skill, a superseded status. A contradiction with no verifiable answer goes to the report instead.
5. **ADR review.** Open `docs/adr/adr-index.md`, then sweep for:
   - backticked file paths an ADR cites that no longer exist (resolve from the repo root and from `docs/adr/`);
   - rows whose status or synopsis no longer matches the code or a later ADR.
   Judge each against the code and the project's stated goal, where one is recorded. Fix a dead path or stale cross-reference directly. Never rewrite a decision: one that no longer holds becomes a proposed amendment or supersession in the report.
6. **Design-doc staleness.** For each `docs/design/{slug}-design.md`, check that the code it describes exists and that its `## Built log` is not contradicted by later ADRs or code. A design doc whose system was absorbed, cut, or redesigned without an update is a finding; route it to the developer or the owning pipeline stage.
7. **Aged ideas and research notes.** Flag each idea or research note older than N days (default 30; ask if the project sets its own) that no other record references (`rg -l <filename-or-slug> docs`). Propose one of: graduate it into a record, refine it, or mark it superseded. This step surfaces candidates only; the developer decides.
8. **Close.** Run the project's validation commands, where any exist, and deliver the report.

## The report

Inline in the session unless the developer asks for a saved copy. In order:

- What was fixed on the spot, one line each, with the path.
- ADRs needing attention: the specific staleness and the proposed remedy.
- Stale design docs and aged unreferenced notes, each with a proposed disposition.
- Everything found but not fixable without a decision.

End with one suggested commit subject (`docs: ...`). Never commit.

## Gotchas

- Absence of a dead path is not proof an ADR is current; step 5's editorial pass still runs.
- Skip shorthand path references whose base directory the prose does not state; flag only paths anchored at a real top-level directory.
- A generated index is fixed by rerunning its generator, never by hand. If the project has one, use it and say so.
- Age uses the document's own dates first (frontmatter `updated`, then `created`), then the git commit date as a last resort. Name which source each flag used.

## Boundaries

- Fixes words, links, rows, and verifiable facts. Never changes an ADR's decision, a business rule, or code without developer approval.
- Does not edit `.github/instructions/` or `.claude/rules/` (`agent-guardrails`).
- Debt rows belong to `tech-debt`, refactor rows to `refactor-ledger`. Report their drift; route the edit.
- Every touched doc follows `concise-documentation`. Never commits.
