---
applyTo: "**"
---

# Pattern Fidelity

> **Full guidance:** `.github/docs/pattern-fidelity-guide.md`

Match the project. Before introducing any pattern, abstraction, coding standard, library, or architectural approach, ground it in what this project already does, and prefer the project's established way over a generic best-practice from memory. `code-standards` governs how code is written; this file governs whether a pattern belongs here at all.

## Ground before you build

Check for precedent in this order, stop at the first that answers: (1) the language code standards and any adopted-pattern ADR; (2) decisions via the triage indexes first (`docs/adr/adr-index.md`, `docs/business-rules/br-index.md`) by status and context, then open only the governing record, never whole record dirs; (3) neighboring code solving the same shape of problem. If precedent exists, follow it; do not refactor toward a different style just because you would reach for it by default.

## When no precedent exists

Do not silently invent. State that no precedent was found, name the options, recommend one, and get the developer's confirmation before adding it (`agent-guardrails` "Ask, Do Not Guess" applied to design choices). A new architectural pattern, cross-cutting concern, or third-party dependency requires an ADR; propose it, do not assume it.

## Resist generic solutions

Do not reach for a textbook abstraction the project never asked for (a repository layer over direct queries, an event bus where a call suffices, a config framework for three constants, an interface with one implementation). Solve the problem the project actually has, at its actual scale. Match the domain's vocabulary, and mirror the existing layering, error-handling, and dependency style rather than importing a foreign one.

## Scope

Applies to design and implementation choices across all files: source, tests, docs, configuration. It does not forbid new patterns; it forbids introducing them without grounding or confirmation. The guide carries the fuller examples and how a confirmed pattern becomes precedent (instruction files, ADRs).
