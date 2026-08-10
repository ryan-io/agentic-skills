---
name: architecture-layering
description: >
  Classifies identified volatilities into a layered architecture: applies the Four Questions
  (who/what/how/how/where), assigns components to Client, Business Logic, ResourceAccess, and
  Resource layers plus the Utilities bar, and distinguishes Managers (sequence volatility) from
  Engines (activity volatility). Use for "the four questions", "Manager Engine ResourceAccess",
  "which layer", or "name this service". Back end of the design pipeline, consuming the output of
  volatility-decomposition.
---

# Architecture Layering

This skill runs as an interactive session. It takes a set of identified volatilities and structures them into a layered architecture. It is the final stage of the design pipeline: behavioral-requirements -> volatility-decomposition -> architecture-layering.

This stage produces system architecture, not detailed design: classification and naming, not implementation. Done well, the layering makes the architecture readable and the boundaries defensible.

## Ground first

Before classifying, confirm the existing layer assignments and names so a new service fits the established taxonomy rather than coining a synonym: read the project's existing architecture documents and decision records for the area, and survey the existing code for the seams already in place. An unresolved conflict in those records is a blocker to raise, not a detail to layer past.

As each volatility becomes a seam, invoke `design-patterns` to name it with the GoF pattern that fits: a swappable algorithm is a Strategy behind a Contracts interface, a WPF or framework type meeting the pure tier is an Adapter, a subsystem behind a simple interface is a Facade, two independent axes are a Bridge. The pattern's collaboration interface lives in the Contracts project; its concrete choice is made in the composition root, never by a `switch` in the consumer.

## Input and Output

Input: a volatilities list. If `docs/{system-slug}/volatility-decomposition.md` exists, read it as the starting point. Otherwise ask the user to enumerate the volatilities (and suggest running volatility-decomposition first).

Output: a layered architecture saved to `docs/{system-slug}/architecture-layering.md` containing the layer assignment table, the named services, and the classification rationale.

If `docs/{system-slug}/architecture-layering.md` already exists, this is a revision. Read it first, apply the requested change, preserve all other content and the conventions below, confirm before overwriting, and save to the same path unless the user renames it.

## The Four Questions

The Four Questions sort each volatility by who/what/how/how/where. The two hows split how the system performs business activities (Engines) from how it accesses resources (ResourceAccess). Use the questions as the first cut: bin each volatility by which one it answers.

- **Who** interacts with the system -> Client layer
- **What** is required of the system -> Managers
- **How** the system performs business activities -> Engines
- **How** the system accesses resources -> ResourceAccess
- **Where** the system state lives -> Resources

The result will not be perfect. Not every "what" maps one-to-one to a Manager, and crossover happens. If the volatility encapsulation is justified, trust it.

Litmus test as you go: are all Clients purely "who" with no "what"? Are all Managers purely "what" with no "who" or "where"? If a name feels wrong against its question, the classification is probably off.

## Layering

Four horizontal layers, top to bottom, with one cross-cutting vertical bar:

1. **Client** entry points: end-user apps or other systems.
2. **Business Logic**, in two tiers: Managers (orchestration) above Engines (domain logic).
3. **ResourceAccess**: abstraction over the actual resources.
4. **Resource**: data stores and external systems.
5. **Utilities** (vertical): Security, Logging, Diagnostics, Pub/Sub, Message Bus, Hosting. Spans all layers; not a fifth layer, a shared slice every layer can use.

Layers enable layered encapsulation: services inside a layer encapsulate volatility from each other. Even simple systems should be layered. Use only a handful, terminating at a layer of physical resources.

The architecture is **closed**: a component calls only into the adjacent lower layer, never up and never sideways. An open architecture (anything calls anything) trades encapsulation for flexibility, a bad trade in software; with it there is hardly any benefit to having layers at all. Calling up is the worst sin (it imports a higher layer's volatility downward), calling sideways the second (it couples peers inside a layer). Semi-closed architectures (calling more than one layer down) are justified only for performance-critical infrastructure or a codebase that never changes, and a business system is neither. The Method relaxes closed layering in exactly four ways: every layer calls Utilities; Managers and Engines both call ResourceAccess (same layer); Managers call Engines directly (Engines sit in an orthogonal plane, an expression of Strategy); and a Manager reaches a peer Manager only through a queued call. The full call-rule list the chains are checked against lives in `composable-design`.

## Phase 1: Client Layer

The layer is called "client", not "presentation", because consumers are not only humans; a client can be another system. Calling it the client layer equalizes all consumers: same entry points, same access security, same data types. The client layer encapsulates volatility in clients and is often the most volatile part of the system.

Ask: "Which volatilities are about who consumes the system, or how they reach it?" Those are Client candidates.

## Phase 2: Business Logic, Managers vs Engines

The business logic layer implements the system's required behavior, best expressed as use cases. A use case changes in only two ways, and the two are orthogonal:

- The **sequence** of activities changes (parallel, sequential, conditional ordering).
- The **activities themselves** change.

That split drives the two component types:

- **Managers** encapsulate volatility in the *sequence* (orchestration, workflow). A Manager tends to own a family of related use cases.
- **Engines** encapsulate volatility in the *activities* (business rules, computation). Engines have narrower scope.

Mapping to known patterns: a Manager is an Orchestrator / Mediator / Saga orchestrator (it sequences calls, holds no domain logic). An Engine is a Strategy / Domain Service (it computes, unaware of workflow context).

Dependency rule: Managers call Engines and ResourceAccess. A Manager reaches a peer Manager only as a queued, fire-and-forget handoff to start the next workflow, never a synchronous request inside its own use case, and queues to at most one Manager per use case. **Engines never call Managers and never call each other**: a chained Engine call questions whether the second activity was separately volatile at all, and is likely functional decomposition. ResourceAccess services never call each other either. Managers use zero or more Engines; Engines are shared across Managers because the same activity recurs across use cases. Design Engines for reuse.

Duplicate-Engine smell: if two Managers use two different Engines for the same activity, it is either functional decomposition (Engines named by caller, not by volatility, so consolidate) or missed activity volatility (the Engines differ but the axis was not named). Litmus: if swapping one Engine for the other breaks nothing, it is duplication.

Ask, for each Manager candidate: "Does the ordering of steps change independently from the steps themselves?" Sequence volatility justifies the Manager. Then ask whether any activity inside it has "an unknown number of ways of being done." Only then does an Engine exist.

## Phase 3: ResourceAccess and Resource

**ResourceAccess** encapsulates volatility in *how* a resource is accessed, and the volatility in the resource itself (local DB vs cloud, durable vs in-memory). A resource change invariably changes ResourceAccess.

Watch for leaky contracts. Most access layers expose CRUD-like (`Select`, `Insert`, `Delete`) or IO-like (`Open`, `Read`, `Write`, `Seek`) operations that betray the resource type through the contract surface. Changing a leaky contract ripples to every Engine and Manager that depends on it. Phrase ResourceAccess operations in **atomic business verbs** instead: the lowest-level business operations that cannot be expressed by any other (e.g., credit and debit for a transfer). Atomicity is defined from the business perspective, even if a verb takes several system steps to implement.

ResourceAccess can be shared between Managers and Engines; design it for reuse.

**Resource** holds the actual physical resources: databases, file systems, caches, queues. A resource may be internal or an entire external system that, to yours, looks like just a Resource. A Resource is often a framework or third-party subsystem wrapped behind an Access seam.

**Check the API reality before you place a seam.** When a layering decision turns on whether a framework or library API exists or what it affords (a first-party capability you can lean on versus a gap you must encapsulate behind an interface), verify it against the actual documentation for the installed version, do not assume from memory. A seam justified by an API gap that does not actually exist is built on a guess.

## Phase 4: Utilities

Place cross-cutting infrastructure in the Utilities bar: Security, Logging, Diagnostics, Instrumentation, Pub/Sub, Message Bus, Hosting. These follow different rules from the layered components and are available to every layer. Identity propagation across a call chain (chain-of-trust: OAuth2 token exchange, JWT claim propagation, mTLS identity headers) lives here; the propagation mechanism is volatile, the need for identity flow is stable.

## Phase 5: Name the Services

A taxonomy used in name only still produces functional decomposition; naming is where it is most easily faked.

Conventions:

- Service names are two-part compound words in PascalCase.
- Suffix is the type: `Manager`, `Engine`, or `Access` (for ResourceAccess).
- Prefix by type: Manager takes a noun for the use-case volatility (`TradeManager`); Engine takes a noun for the activity (`PricingEngine`); ResourceAccess takes a noun for the resource provided (`AccountAccess`).
- **Gerunds (-ing) are valid only for Engines.** Engines "do" things: aggregate, validate, calculate, transform, translate, locate, search. `CalculatingEngine` is fine. A gerund prefix on a Manager or Access signals functional decomposition.
- Atomic business verbs do not belong in service names; reserve them for ResourceAccess operation names.

Good: `AccountManager`, `AccountAccess`, `PricingEngine`. Smells: `BillingManager`, `BillingAccess` (gerund-flavored "doing"), `AccountEngine` (no activity volatility; reads as domain decomposition).

Validate each name against its question: a Manager prefix should read as "what," an Engine prefix as "how (business)," a ResourceAccess prefix as "how (access)." If it does not, the classification is probably wrong.

## Phase 6: Sanity Checks

**Manager-to-Engine ratio.** Most designs end up with fewer Engines than expected. An Engine exists only where there is fundamental operational volatility, an unknown number of ways of doing something. Such volatilities are uncommon. A large number of Engines signals inadvertent functional decomposition. Orchestration complexity and activity complexity correlate: a single correctly scoped Manager usually implies zero or one Engine. Multiple Engines under one Manager may mean the Manager is a god service hiding several use-case families.

**Functional decomposition coexists, at the code level only.** Inside a component, normal OOP factoring (extract method, helper classes, SRP) is fine and expected. That is code-level functional decomposition. The mistake is promoting an internal helper to an architectural Engine without volatility justification, or decomposing the architecture functionally and relabeling it with these terms. No volatility means no Engine; the Manager holds the logic inline. That is correct design, not laziness.

**The top-down gradient.** In a well-designed system, volatility decreases going down the layers and reuse increases, the inverse of each other. Clients are the most volatile and hardly ever reusable. Managers change when use cases change. Engines change only when the business changes how it performs an activity, which is rarer. ResourceAccess is less volatile still and the most reusable, callable by both Engines and Managers. Validate the classification against the gradient: a proposed Engine more volatile than the Manager above it, or a Client expected to be reused, signals a wrong layer assignment.

**Manager expendability.** Managers fall into three categories: expensive, expendable, and almost expendable. An expensive Manager holds too much logic and is likely a god service hiding several use-case families. An expendable Manager encapsulates no real use-case volatility and exists only to satisfy the taxonomy; that is always a design flaw. A well-designed Manager is almost expendable: it merely orchestrates Engines and ResourceAccess, encapsulating sequence volatility. Litmus: a proposed use-case change should require only contemplative adaptation of the Manager, not a rewrite.

**Symmetry.** Good design shows repeated call patterns across use cases and across Managers; expect it, and treat its absence as a smell. If three of a Manager's four use cases publish an event and the fourth does not, ask why the fourth differs: something is missing, something is overdone, or that Manager is a functionally decomposed component without real volatility.

**When someone wants to open the architecture.** Developers will repeatedly try to call sideways, call up, or otherwise open the closed layering. Do not brush the transgression aside or demand blind compliance: it almost always signals a real underlying need, and the job is to meet that need compliantly. A second use case triggered by the first rarely must run immediately, so queue the Manager-to-Manager call. A Manager wanting to notify a Client has surfaced volatility in who notifies and who receives; encapsulate it in a Pub/Sub Utility the Manager can call, never a call up. The main reason people argue for a violation is a functional decomposition they have convinced themselves is not one; treat any violation of the `composable-design` call rules as a red flag and ask what is being missed.

## Phase 7: Write the Architecture

Present the layer assignment, then write `docs/{system-slug}/architecture-layering.md`:

1. Layer assignment table: each service, its layer, the volatility it encapsulates, the question it answers, and its target project and namespace (the layer fixes the project; the namespace follows the folder path). Recording placement here means the plan and `implementation` build into the right project and namespace from the first file.
2. Named services with one-line rationale each.
3. Sanity-check notes (ratio, gradient, Manager expendability, anything left unencapsulated on purpose).
4. Tuning surface: per service, the tunable parameters it exposes (name, unit, expected range) and the configuration seam that owns each as authored data. A knob is a design output, not an implementation afterthought; a service with nothing tunable says so in one line.
5. References, if the design cites external sources.

Write in short, plain, concrete prose.

Where a cohesive set of services (a Manager with its Engines and ResourceAccess) implements a family of use cases, group them in the document as a subsystem: a vertical slice of the system. Subsystems are the unit of extensibility: extend the system by adding slices while leaving existing components alone, never by opening up and hammering on what is already built.

Then validate before handing off: invoke `composable-design` to designate the core use cases and compose each as a call chain through the named services, recording the `## Validation` section in `architecture-layering.md`. It draws sequence diagrams for the flows worth a picture, since behavior emerges from how the encapsulated volatilities interact. An architecture that has not been composed against its core use cases is named, not validated.

When the developer is ready to build, the next stage is `implementation-planning` (the pre-build gate, followed by the Gate B critique); from its plan, `implementation` pair-programs these services into C#/WPF code.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
