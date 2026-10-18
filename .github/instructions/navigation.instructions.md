---
applyTo: "**"
---

# Navigation: Index-First, Never Scrape

Reach the one record, symbol, or section a task needs through an index. A full-file read is the last resort.

## Records

- Before reading records, open the corpus index: `docs/adr/adr-index.md`, `docs/business-rules/br-index.md`, `docs/debt/debt-index.md`, `docs/refactor/refactor-ledger.md`, a listing of `docs/design/`, `docs/glossary.md`.
- Triage by the index row (status, context, synopsis), then open only the record that governs the change.
- Never read a whole record directory to find one answer.

## Source

- Before reading source to learn a shape, use the editor's symbol search, or `rg` for a definition or its references.
- Read the span the search points to, not the whole file.
- Open the full file only for a body the search did not give.

## Boundaries

- An index row that drifts from its record is fixed in the same change, never left stale.
- External facts (versions, APIs, tradeoffs) follow `research`; decisions live in ADRs and business rules.
