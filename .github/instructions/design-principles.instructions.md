---
applyTo: "**"
---

# Design Principles

> **Full guidance:** `.github/docs/design-principles-guide.md`

Heuristics for better code, not hard rules. They guide design alongside `code-standards` (how code is written) and `pattern-fidelity` (whether a pattern belongs here). The hard rules live in `code-standards` and the language standards; this file states the judgment behind them.

These are suggestions, not gates. Follow them by default; break them deliberately when the practical cost outweighs the benefit. The failure mode is the inverse: adding interfaces, layers, or indirection only to satisfy a principle. Do not add complexity to align with a principle. When a principle and simplicity conflict on a small, local change, prefer simplicity and say why.

- **Single Responsibility.** One reason to change per type, defined by function not line count. Maps onto the Lowy layering: Engine computes, Managers orchestrate, Access seams reach resources.
- **Separation of Concerns.** The layer counterpart of Single Responsibility: each concern lives in the layer that owns it, and never bleeds sideways. UI code carries no business logic (`code-standards` holds the hard rule); an Engine never orchestrates; a Manager never computes domain state.
- **Open/Closed.** Extend without modifying working code, through the DI graph and the Contracts interfaces, not speculative abstraction. Let volatility decomposition, not guesswork, decide where to leave a seam.
- **Liskov Substitution.** A subtype honors the contract it stands in for: same guarantees, no surprise exceptions, no narrowed input. If it cannot, fix or split the contract.
- **Interface Segregation.** Small, focused interfaces over wide ones; a consumer depends only on the verbs it uses.
- **Dependency Inversion.** Depend on abstractions, not concretions. Settled practice: composition-root constructor injection against Contracts interfaces, no service-locator lookups in business logic.
- **Don't Repeat Yourself.** The second occurrence is the signal; extract genuine shared meaning into one stateless Utilities helper. Candidate, not mandate, per the simplicity guard: leave coincidental resemblance or sites likely to diverge, and record a deliberate deferral as tracked debt.
- **Keep It Simple (KISS).** The simplest design that meets the named requirement wins. Two stable variants and an `if` beat a Strategy interface; add structure when a real axis of change demands it, not before.
- **You Aren't Gonna Need It (YAGNI).** Build for the requirement in front of you, not an imagined one. Volatility decomposition names the futures worth a seam; an interface, layer, or abstraction outside that list is speculation (`pattern-fidelity`).

The guide carries the full rationale and examples for each principle.
