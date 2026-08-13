---
name: design-patterns
description: >
  Resolve a software design question to the right classic design pattern, and apply a per-stage
  pattern lens across the design pipeline. Use for "which pattern fits this", "is this Strategy
  or State", or any of the 23 patterns by name. Invoke implicitly at the start of any design,
  planning, or implementation stage to check whether a known pattern solves the problem first.
  A pattern that becomes new cross-cutting structure is a decision for the developer, not a
  default.
tags: [design-pipeline, patterns, skill]
---

# Design Patterns (the catalog and the per-stage lens)

Two jobs:

1. Answer pattern questions from the catalog of 23 classic patterns: what each solves, when to use it, and how it lands in a codebase built on the pipeline's layers, Contracts interfaces, and composition-root DI (examples default to C#).
2. Carry a per-stage lens the pipeline invokes. One question per stage, in that stage's vocabulary. No design logic of its own.

The lens question: **is there a named pattern that already solves this, and does the design name it correctly?** It prevents two failures:

- **Reinvention.** Hand-rolling a `switch` that is a Strategy, or a manual save-and-restore that is a Memento. The code loses the vocabulary that tells the next reader what it is.
- **Misnaming.** Calling something a Strategy when it is a State. The design promises one thing; the code does another.

## Answering a pattern question

- Lead with the pattern, then its project fit.
- "What does X solve" or "Strategy or State here": give the intent, the distinguishing trait (State objects drive their own transitions; Strategy keeps algorithms independent), and a small reworked C# example.
- "Should this seam be a Factory": the catalog is supporting evidence; the project's ADRs are the source of truth. Cite the intent, defer to the records, and apply the boundary below before recommending anything new.

The catalog, for triage:

- **Creational:** Factory Method, Abstract Factory, Builder, Prototype, Singleton.
- **Structural:** Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy.
- **Behavioral:** Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.

## The lens, by stage

### pipeline-stg2-volatilities (the design doc's `## Volatilities` section)

- Many axes of change have a pattern that encapsulates them: the algorithm varies -> Strategy; the created type varies -> Factory Method or Abstract Factory; behavior varies by mode -> State; state must be captured and restored -> Memento.
- Naming the pattern is a hint for layering, not a decision to build it.
- Never invent a volatility to justify a pattern. The axis must be real.

### pipeline-stg3-architecture (the design doc's `## Architecture` section)

The lens's main stage. As each volatility becomes a seam, name it with the pattern that fits:

- Swappable algorithm -> Strategy behind a Contracts interface.
- UI-framework type meeting the pure tier -> Adapter, in the Adapters project.
- Simple interface over a subsystem -> Facade (the ResourceAccess seams).
- Lazy or guarded access behind an interface -> Proxy.
- Two independent axes -> Bridge.

Two rules: the pattern's collaboration interface is a Contracts interface (Dependency Inversion), and the concrete choice is made in the composition root, never by a `switch` in the consumer. Flag the Singleton smell on sight: a single shared instance is a container lifetime, never a static global.

### pipeline-stg5-implementation-planning (the plan)

- Write the named patterns into the plan as the shape each service takes, so the build inherits the vocabulary.
- "A Strategy behind `IThing`": say so, and record the Contracts interface and the composition-root registration as plan steps.
- A pattern that would be new cross-cutting structure for the project is a developer decision first. Flag it; don't bury it.

### pipeline-stg6-implementation (the code)

Build the named pattern in the language-native idiom. Prefer the C#/DI-native form over the textbook OO form:

- One-method Strategy -> delegate or `Func<>`.
- Iterator -> `IEnumerable<T>` and `yield`.
- Observer -> C# `event` or a pub/sub library.
- Few operations -> pattern matching instead of a full Visitor.
- Decorator chain -> `IDisposable` scopes or middleware.

Smells: a Singleton creeping in as a static; a Strategy interface with one implementation and no second in sight (speculative generality); a Visitor where a `switch` expression reads better.

### pipeline-stage-review (Gates A, B, C)

The reviewer uses the catalog as a checklist, most of all at Gate C: does each seam's named pattern match what the code does, and is any hand-rolled mechanism an unnamed instance of a pattern that would read better named? A misnamed or reinvented pattern is a fidelity finding, routed to the owning stage.

## Boundary: name patterns, don't mandate them

- A pattern is a tool for a problem the project actually has, not a goal. Never add an interface, layer, or seam to satisfy a pattern (speculative generality).
- When two stable variants and an `if` solve the problem, the `if` wins. A clean check with no pattern needed is a valid result.
- A pattern that is new cross-cutting structure needs developer sign-off before it's built. Already-settled conventions (the project's Strategy seams, its Adapters layer, its Facades) need no new sign-off.

## Recording an adopted pattern

When a pattern becomes a committed project convention, record it as an ADR with the project's real code as the example, under developer approval. The catalog stays the teaching reference; the ADR is the commitment.

## References

- Gamma, Helm, Johnson, Vlissides. *Design Patterns*. Addison-Wesley, 1994.
- Refactoring.Guru, https://refactoring.guru/design-patterns/csharp (rework examples; never copy).
- The stages that invoke this lens: `pipeline-stg2-volatilities`, `pipeline-stg3-architecture`, `pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`, `pipeline-stage-review`.
