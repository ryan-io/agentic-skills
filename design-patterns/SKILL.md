---
name: design-patterns
description: >
  Resolve a software design question to the right Gang of Four pattern, and apply a per-stage
  pattern lens across the design pipeline. Use for "which pattern fits this", "is this Strategy
  or State", or any of the 23 patterns by name. Invoke implicitly at the start of any design,
  planning, or implementation stage to check whether a known pattern solves the problem first.
  A pattern that becomes new cross-cutting structure is a decision for the developer, not a
  default.
---

# Design Patterns (the catalog and the per-stage pattern lens)

This skill does two jobs. First, it answers pattern questions from the Gang of Four catalog: the 23 patterns, what each solves, when to use it, and how it lands in a C#/WPF codebase built on Löwy layers, Contracts interfaces, and composition-root DI. Second, it carries a per-stage pattern lens the pipeline invokes: at each stage it asks one question in that stage's vocabulary, and it adds no design logic of its own.

The question the lens carries is: **is there a named pattern that already solves this, and does the design name it correctly?** Catching that early prevents two failures. The first is reinvention: hand-rolling a `switch` that is a Strategy, or a manual save-and-restore that is a Memento, so the code loses the vocabulary that would have told the next reader what it is. The second is misnaming: calling something a Strategy when it is a State, so the design promises one thing and the code does another.

## How to answer a pattern question

Lead with the pattern, then its project fit. For "what does X solve" or "Strategy or State here," give the intent, the distinguishing trait (State objects drive their own transitions; Strategy keeps algorithms independent), and a small reworked C# example. For "should this seam be a Factory," the catalog is supporting evidence and the project's own decision records are the source of truth: cite the pattern's intent, then defer the call to the project's records, and apply the boundary below before recommending a new pattern.

The catalog, for triage:

- **Creational:** Factory Method, Abstract Factory, Builder, Prototype, Singleton.
- **Structural:** Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy.
- **Behavioral:** Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor.

## The lens, by stage

Apply the check for the stage that is running.

### volatility-decomposition (volatility-decomposition.md)

A volatility is an axis of change, and many axes have a pattern that encapsulates them. When an axis is "the algorithm varies," name the candidate (Strategy); "the created type varies," (Factory Method or Abstract Factory); "behavior varies by mode," (State); "the same state must be captured and restored," (Memento). Naming the pattern that fits a volatility is a hint for layering, not a decision to build it. Do not invent a volatility to justify a pattern; the axis must be real.

### architecture-layering (architecture-layering.md)

This is the lens's main stage. As each volatility becomes a seam, check the catalog for the pattern that fits, and name the seam with it: a swappable algorithm is a Strategy behind a Contracts interface; a WPF or framework type meeting the pure tier is an Adapter in the Adapters project; a simple interface over a subsystem is a Facade (the ResourceAccess seams); lazy or guarded access behind an interface is a Proxy; two independent axes are a Bridge. Apply two rules: a pattern's collaboration interface is a Contracts interface (Dependency Inversion), and the concrete choice is made in the composition root, not by a `switch` in the consumer. Flag the Singleton smell on sight: a single shared instance is a container lifetime, never a static global.

### implementation-planning (the plan)

Write the named patterns into the plan as the shape each service takes, so the build inherits the vocabulary. Where a service is "a Strategy behind `IThing`," say so, and record the Contracts interface and the composition-root registration as plan steps. If the plan would introduce a pattern that is new cross-cutting structure for the project (not an already-settled convention), that is a decision for the developer first; flag it, do not bury it.

### implementation (the code)

Build the pattern the plan named, in the C#-native idiom. Prefer the C# and DI-native form over the textbook OO form: a delegate or `Func<>` for a one-method Strategy; `IEnumerable<T>` and `yield` for an Iterator; C# `event` or a pub/sub library for an Observer; pattern matching instead of a full Visitor when the operations are few; `IDisposable` scopes or middleware for a Decorator chain. Watch the smells: a Singleton creeping in as a static, a Strategy interface with one implementation and no second one in sight (speculative generality), a Visitor where a `switch` expression would read better.

### gate-review (Gates A, B, C)

The independent reviewer uses the catalog as a checklist at every gate, most of all at Gate C over the built code: does each seam's named pattern match what the code does, and is any hand-rolled mechanism an unnamed instance of a pattern that would read better named? A misnamed or reinvented pattern is a fidelity finding, routed back to the owning stage like any other.

## Boundary: this skill names patterns, it does not mandate them

A pattern is a tool for a problem the project actually has, not a goal: do not add an interface, layer, or Strategy seam to satisfy a pattern (the speculative-generality smell). When two stable variants and an `if` solve the problem, the `if` wins; a clean check, no pattern needed, is a valid result.

A pattern that is new cross-cutting structure for the project is a decision, not a default: propose it and get developer sign-off before building it. Conventions the project has already settled (its Strategy seams, its Adapters layer, its established Facades) need no new sign-off.

## Recording an adopted pattern

When a catalog pattern becomes a committed project convention, record it in the project's decision records with the project's real code as the example, under developer approval. The catalog stays the teaching reference; the decision record is the commitment.

## References

- Gamma, Helm, Johnson, Vlissides. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.
- Refactoring.Guru, https://refactoring.guru/design-patterns/csharp (rework examples; never copy).
- The pipeline skills that invoke this lens: `volatility-decomposition`, `architecture-layering`, `implementation-planning`, `implementation`, `gate-review`.
