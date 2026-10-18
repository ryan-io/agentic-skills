---
name: pipeline-stg3-architecture
description: >
  Stage 3 of the design pipeline: classifies identified volatilities into a layered architecture.
  Applies the Four Questions (who/what/how/how/where), assigns components to Client, Business
  Logic, ResourceAccess, and Resource layers plus the Utilities bar, and distinguishes Managers
  (sequence volatility) from Engines (activity volatility). Use for "the four questions",
  "Manager Engine ResourceAccess", "which layer", or "name this service". Consumes the design
  doc's Volatilities section; writes its Architecture section (docs/design/{slug}-design.md).
tags: [architecture, design-pipeline, skill]
---

# Pipeline Stage 3: Architecture Layering

Interactive session. Takes the identified volatilities and structures them into a layered architecture. This stage produces system architecture, not detailed design: classification and naming, not implementation.

Pipeline position: pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture -> pipeline-stg4-validation.

## Ground first

- Read the project's existing architecture documents and ADRs for the area, so a new service fits the established taxonomy instead of coining a synonym.
- Survey the existing code for seams already in place.
- An unresolved conflict in the records is a blocker to raise, not a detail to layer past.
- As each volatility becomes a seam, invoke `design-patterns` to name it: a swappable algorithm is a Strategy behind a Contracts interface; a UI-framework type meeting the pure tier is an Adapter; a subsystem behind a simple interface is a Facade; two independent axes are a Bridge. The pattern's interface lives in Contracts; the concrete choice is made in the composition root, never by a `switch` in the consumer.

## Input and output

- Input: the `## Volatilities` section of `docs/design/{slug}-design.md` when it exists. Otherwise, ask the user to enumerate the volatilities (and suggest running pipeline-stg2-volatilities first).
- Output: the `## Architecture` section of the same doc: layer assignment table, named services, classification rationale.
- Standalone runs included: check for the doc first. If it exists, modify only this section. If not, create it with only this section.
- If the section already exists, this is a revision: read it first, apply the change, preserve everything else, confirm before overwriting.

## The Four Questions

Sort each volatility by the question it answers. The two hows split business activities (Engines) from resource access (ResourceAccess).

- **Who** interacts with the system -> Client layer
- **What** is required of the system -> Managers
- **How** the system performs business activities -> Engines
- **How** the system accesses resources -> ResourceAccess
- **Where** the system state lives -> Resources

The result won't be perfect; crossover happens. If the encapsulation is justified, trust it. Litmus: Clients are purely "who," Managers purely "what." A name that feels wrong against its question usually means a wrong classification.

## Layering

Four horizontal layers plus one vertical bar:

1. **Client**: entry points. End-user apps or other systems.
2. **Business Logic**: Managers (orchestration) above Engines (domain logic).
3. **ResourceAccess**: abstraction over the resources.
4. **Resource**: data stores and external systems.
5. **Utilities** (vertical): Security, Logging, Diagnostics, Pub/Sub, Message Bus, Hosting. A shared slice every layer can use, not a fifth layer.

Rules:

- Layers give layered encapsulation; services inside a layer also encapsulate volatility from each other. Even simple systems should be layered. Use a handful, ending at physical resources.
- The architecture is **closed**: a component calls only into the adjacent lower layer. Never up, never sideways. Calling up is the worst sin (it imports a higher layer's volatility downward); sideways is second (it couples peers).
- Open architectures (anything calls anything) trade encapsulation for flexibility; a bad trade. Semi-closed (skipping layers down) is justified only for performance-critical infrastructure or code that never changes; a business system is neither.
- Closed layering is relaxed in exactly four ways: every layer calls Utilities; Managers and Engines both call ResourceAccess; Managers call Engines directly (Engines sit in an orthogonal plane, an expression of Strategy); a Manager reaches a peer Manager only through a queued call.
- The full call-rule list lives in `pipeline-stg4-validation`.

## Phase 1: Client layer

- Called "client", not "presentation": consumers aren't only humans; a client can be another system. Same entry points, same security, same data types for all consumers.
- Often the most volatile part of the system.
- Ask: "Which volatilities are about who consumes the system, or how they reach it?"

## Phase 2: Business logic, Managers vs Engines

A use case changes in exactly two orthogonal ways:

- The **sequence** of activities changes -> **Managers** encapsulate it (orchestration, workflow). A Manager owns a family of related use cases.
- The **activities themselves** change -> **Engines** encapsulate it (domain logic, computation). Narrower scope.

Pattern mapping: a Manager is an Orchestrator/Mediator (sequences calls, holds no domain logic). An Engine is a Strategy/Domain Service (computes, unaware of workflow).

Dependency rules:

- Managers call Engines and ResourceAccess.
- A Manager reaches a peer Manager only as a queued, fire-and-forget handoff that starts the next workflow. Never a synchronous request inside its own use case. At most one queued Manager per use case.
- **Engines never call Managers and never call each other.** A chained Engine call questions whether the second activity was separately volatile at all; it's likely functional decomposition.
- ResourceAccess services never call each other.
- Engines are shared across Managers because activities recur across use cases. Design Engines for reuse.

Duplicate-Engine smell: two Managers using two different Engines for the same activity is either functional decomposition (Engines named by caller; consolidate) or a missed activity volatility. Litmus: if swapping one Engine for the other breaks nothing, it's duplication.

Per Manager candidate, ask: "Does the ordering of steps change independently of the steps themselves?" Sequence volatility justifies the Manager. Then: "Does any activity inside it have an unknown number of ways of being done?" Only then does an Engine exist.

## Phase 3: ResourceAccess and Resource

- **ResourceAccess** encapsulates how a resource is accessed, plus volatility in the resource itself (local DB vs cloud, durable vs in-memory). A resource change always changes ResourceAccess.
- Watch for leaky contracts: CRUD verbs (`Select`, `Insert`, `Delete`) or IO verbs (`Open`, `Read`, `Write`, `Seek`) betray the resource type. A leaky contract change ripples into every Engine and Manager using it.
- Phrase operations as **atomic business verbs**: the lowest-level business operations that can't be expressed by any other (credit and debit for a transfer). Atomicity is defined by the business, even if one verb takes several system steps.
- ResourceAccess is shared by Managers and Engines; design it for reuse.
- **Resource** holds the physical resources: databases, file systems, caches, queues. A Resource may be an entire external system, or a framework subsystem wrapped behind an Access seam.
- **Check the API reality before placing a seam.** When a decision turns on whether a framework capability exists, verify against the documentation for the installed version. A seam justified by an API gap that doesn't exist is built on a guess.

## Phase 4: Utilities

- Cross-cutting infrastructure: Security, Logging, Diagnostics, Instrumentation, Pub/Sub, Message Bus, Hosting.
- Different rules from layered components; available to every layer.
- Identity propagation across a call chain (OAuth2 token exchange, JWT claims, mTLS headers) lives here: the mechanism is volatile, the need for identity flow is stable.

## Phase 5: Name the services

Naming is where the taxonomy is most easily faked; a taxonomy used in name only still produces functional decomposition.

- Two-part compound words in PascalCase.
- Suffix is the type: `Manager`, `Engine`, or `Access`.
- Prefix by type: Manager takes a noun for the use-case volatility (`TradeManager`); Engine a noun for the activity (`PricingEngine`); Access a noun for the resource (`AccountAccess`).
- **Gerunds (-ing) are valid only for Engines.** Engines do things: aggregate, validate, calculate. `CalculatingEngine` is fine. A gerund on a Manager or Access signals functional decomposition.
- Atomic business verbs belong in ResourceAccess operation names, never in service names.
- Good: `AccountManager`, `AccountAccess`, `PricingEngine`. Smells: `BillingManager`, `BillingAccess` (gerund-flavored "doing"), `AccountEngine` (no activity volatility; reads as domain decomposition).
- Validate each name against its question: Manager reads as "what," Engine as "how (business)," Access as "how (access)."

## Phase 6: Sanity checks

- **Manager-to-Engine ratio.** Expect few Engines. An Engine exists only for real operational volatility: an unknown number of ways of doing something. Many Engines signals functional decomposition. A correctly scoped Manager usually implies zero or one Engine; several Engines under one Manager may mean a god service hiding several use-case families.
- **Functional decomposition is fine at code level only.** Inside a component, normal OOP factoring (extract method, helpers, SRP) is expected. The mistake is promoting a helper to an architectural Engine without volatility, or relabeling a functional decomposition with Method terms. No volatility, no Engine; the Manager holds the logic inline. That is correct design.
- **The top-down gradient.** Volatility decreases going down the layers; reuse increases. Clients: most volatile, hardly reusable. Managers change with use cases. Engines change only when the business changes an activity. ResourceAccess: least volatile, most reusable. An Engine more volatile than its Manager, or a Client expected to be reused, signals a wrong layer.
- **Manager expendability.** Expensive Manager: too much logic; likely a god service. Expendable Manager: encapsulates no use-case volatility, exists to satisfy the taxonomy; always a flaw. Well-designed Manager: almost expendable; it merely orchestrates. Litmus: a use-case change should require contemplative adaptation, not a rewrite.
- **Symmetry.** Expect repeated call patterns across use cases and Managers. If three of four use cases publish an event and the fourth doesn't, ask why: something is missing, something is overdone, or the Manager has no real volatility.
- **When someone wants to open the architecture.** Developers will try to call sideways or up. Don't brush it aside or demand blind compliance: the urge almost always signals a real need. Meet the need compliantly: queue the Manager-to-Manager call (the second use case rarely must run immediately); route Manager-to-Client notification through a Pub/Sub Utility (that urge surfaced volatility in who notifies and who receives). The usual reason someone argues for a violation is a functional decomposition they've convinced themselves isn't one. Treat any violation of the `pipeline-stg4-validation` call rules as a red flag.

## Phase 7: Write the section

Present the layer assignment, then write `## Architecture`:

1. Layer assignment table: each service, its layer, the volatility it encapsulates, the question it answers, and its target project and namespace (the layer fixes the project; the namespace follows the folder path). Recording placement here means the plan and `pipeline-stg6-implementation` build into the right place from the first file.
2. Named services, one-line rationale each.
3. Sanity-check notes: ratio, gradient, Manager expendability, anything left unencapsulated on purpose.
4. Tuning surface: per service, the tunable parameters it exposes (name, unit, expected range) and the configuration seam that owns each as authored data. A knob is a design output, not an implementation afterthought. A service with nothing tunable says so in one line.
5. References, if the design cites external sources.

Write in short, plain, concrete prose.

Group each cohesive set (a Manager with its Engines and ResourceAccess) as a **subsystem**: a vertical slice, the unit of extensibility. Extend the system by adding slices; never by opening up what is already built.

Then validate: invoke `pipeline-stg4-validation` to designate the core use cases, compose each as a call chain through the named services, and record the design doc's `## Validation` section. An architecture that has not been composed against its core use cases is named, not validated. `pipeline-stg4-validation` closes by invoking `pipeline-stage-review` at Gate A.

Next stages: `pipeline-stg5-implementation-planning` (the pre-build gate, then Gate B), then `pipeline-stg6-implementation` pair-programs the services into code.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
