---
applyTo: "**/*.cs"
paths:
  - "**/*.cs"
---

# XML Documentation

Extends `csharp-code-standards.instructions.md`; governs `///` doc comments. Prose documents belong to the `concise-documentation` skill; code doc comments are exempt from it, so their standard lives here. `pipeline-stg6-implementation` applies this file at its Drive step.

## What an XML doc is for

An XML doc states the contract: what a type or member does, what the caller passes, what comes back, what can go wrong. It is a tooltip label for someone deciding whether to call the thing, not an explanation of how it works.

## Rules

- Hard cap: two sentences per tag. One-sentence `<summary>` is the default.
- `<summary>`: one plain declarative sentence, present tense, third person. "Advances the simulation by one tick." Member summaries start with a verb; type summaries with a noun phrase.
- No em dashes. No run-on sentences. A comma splice or three-clause chain becomes two sentences.
- Describe behavior, not mechanism. What the thing does and guarantees, not how it is built. Implementation detail, rationale, and design history live in the design docs, cited by id.
- All declaration-level documentation lives inside the XML tags, never split between `///` and `//`. `//` is for implementation notes inside method bodies.
- Meet the caps by deleting what the code, a named record, or the design docs already state.
- No buzzwords. No marketing adjectives ("robust", "seamless"), no throat-clearing ("This class is responsible for..."), no restating the identifier ("Gets or sets the Name"). If the name says it, keep the summary to the one fact the name omits.
- The main failure: a summary stacking construction steps, invariants, and history. Keep the fact a caller needs; delete the rest.
- `<param>`, `<returns>`, `<exception>`: only when they add what the signature does not. Skip `<param name="count">The count.</param>`. Document a parameter when its units, range, null behavior, or ownership are not obvious.
- Reference code with `<see cref="..."/>` so renames stay linked. Cite a governing ADR by id in `<remarks>`, not `<summary>`.
- `<remarks>`: one short sentence; two only when a caveat and a governing id must both appear (an ADR, design, or volatility id, or one caller-facing caveat). Mechanism and rationale belong in the design docs. An overlong `<remarks>` is the most common way these docs bloat.

## Example

Before:

```csharp
/// <summary>
/// The single pure-C# Engine. Advances on a fixed tick driven from the edge (the delta
/// arrives as a plain number; the Engine never learns a time scale exists). Each tick
/// drains commands, advances logic, captures undo history, and flushes events. No
/// UI-framework reference exists here by construction.
/// </summary>
```

After:

```csharp
/// <summary>Pure simulation engine. Advances one fixed tick at a time: drains queued
/// commands, runs logic, records undo history, emits events.</summary>
/// <remarks>Edge-driven, holds no UI-framework reference. Design: {slug}-design.md.</remarks>
```

The mechanism (delta as a plain number, "by construction") drops to the design doc.

A `<remarks>` bloats the same way. Before:

```csharp
/// <remarks>
/// A marker whose effective state (baseline plus edit delta) is inactive is dormant;
/// dormancy derives from current state, never stored. Deterministic. adr-arch-item-dispatch.
/// </remarks>
```

After: `/// <remarks>Dormant when the item's effective state is inactive (adr-arch-item-dispatch).</remarks>`. The derivation and the "never stored" rationale drop to the design doc.
