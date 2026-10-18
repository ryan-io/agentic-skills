# Design Principles Guide

This is the deep companion to `../instructions/design-principles.instructions.md`. The thin rule carries each principle's one-line statement and the simplicity guard. This guide carries the full rationale and examples. Read it when you are actively weighing a design choice against a principle.

These are heuristics, not gates. Skilled engineers follow them by default and break them deliberately when the practical cost outweighs the benefit. The failure mode is the inverse: adding interfaces, layers, or indirection only to satisfy a principle. Do not introduce arbitrary complexity to align with a principle. A principle that makes the code harder to read or change, with no real decoupling gain, is not serving its purpose here. When a principle and simplicity conflict on a small, local change, prefer simplicity and say why.

## Single Responsibility

A class, struct, or service should do one thing and do it well. Define "one thing" by its function and its reason to change, not by a line count. A type that computes domain state, formats it for the UI, and writes it to disk has three reasons to change; split it. A long type that does one job well is fine.

This is the type-level form of "Separation of Concerns" in `code-standards`. It maps onto the Lowy layering: Engine computes, Managers orchestrate, Access seams reach resources.

## Open/Closed

Prefer designs open to extension without modifying working code. That openness comes from architecture and the DI graph, not from speculative abstraction. A new strategy registers behind an existing interface; a new implementation fulfills a contract in the Contracts assembly.

Do not pre-build extension points for changes you cannot name. Volatility decomposition already identifies what is likely to change. Let that, not guesswork, decide where to leave a seam.

## Separation of Concerns

This is the layer counterpart of Single Responsibility. Each concern lives in the layer that owns it and does not bleed sideways. Presentation stays in Views and ViewModels, orchestration in Managers, computation in Engines, resource mechanics behind Access seams.

The hard rule (UI code must not contain business logic) lives in `code-standards`; this principle carries the judgment behind it. A ViewModel that starts deciding business outcomes, or a Manager that starts computing domain state, is a concern leaking across the Lowy mapping. That is a signal to move the logic, not to widen the type.

## Liskov Substitution

A subtype must honor the contract of the type it stands in for. Any implementation of an interface or base must satisfy what callers expect: same guarantees, no surprise exceptions, no narrowing of accepted input. If an implementation cannot honor the contract, the abstraction is wrong. Fix the contract or split it rather than forcing the substitution.

## Interface Segregation

Favor small, well-defined interfaces over broad ones. A consumer should depend only on the verbs it actually uses. Many focused interfaces beat one wide interface that forces implementers to stub methods they do not need. This keeps the Contracts seams honest. It also pairs with Single Responsibility: a fat interface is usually a type with too many reasons to change.

## Dependency Inversion

High-level code depends on abstractions, not concretions; details depend on the abstraction. Apply it through composition-root constructor injection against Contracts interfaces: registration in the composition root, no service-locator lookups in business logic (`code-standards` "Decoupling", `csharp-code-standards` "Dependency Injection"). This one is settled practice, not an aspiration.

## Don't Repeat Yourself

The second occurrence is the signal. When the same logic appears twice or more, flag it as a candidate to extract into one shared home. That home is usually a stateless helper in the Utilities layer (Lowy's Utilities bar), so the behavior has one definition and one place to change. Name the helper for what it computes, not for the callers it serves.

Extraction is a candidate, not a mandate: the preamble's simplicity guard decides. Extract when the repetition is genuine shared meaning. Leave it when the resemblance is coincidental or the two sites are likely to diverge; `pattern-fidelity` "Resist Generic Solutions" warns against a Utility the project never asked for. A deliberate deferral is fine when it is recorded as tracked debt, not left silent.

## Keep It Simple

The simplest design that meets the named requirement wins. The `design-patterns` skill states the bar: when two stable variants and an `if` solve the problem, the `if` wins. Reach for a pattern only when a real axis of change or a real collaboration problem calls for it.

Example: a report needs a PDF export and a CSV export, and no third format is named. An `if` on the format beats an `IExportStrategy` with a registry. Revisit when a third format arrives with a real requirement behind it. Simplicity is also why the preamble's guard exists: when a principle and simplicity conflict on a small, local change, simplicity wins and the choice is said out loud.

## You Aren't Gonna Need It

Do not build for a change nobody named. Volatility decomposition is the YAGNI instrument: the design doc's `## Volatilities` section names the validated axes of change worth a seam, and anything outside that list is speculation. The `pipeline-stg2-volatilities` skill carries the warning directly: a design that accumulates a building block for every imagined change is itself a sign of bad design.

The smells to catch, per `pattern-fidelity` "Resist Generic Solutions":

- A Strategy interface with one implementation and no second in sight.
- An interface with one implementer added "for testability" that a mock at the seam already provides.
- A config axis no record asked to vary.
