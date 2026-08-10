---
name: composable-design
description: >
  Validate a layered architecture: designate core use cases, compose each as a call chain through
  the named services, and show the same small set of services satisfies them all. Use for
  "validate the architecture", "compose the use cases", "draw the call chains", or "is this the
  smallest set of services". Invoke at the end of architecture-layering, before Gate A, and when a
  new use case arrives against a settled architecture. It is the author's proof, distinct from
  gate-review's adversarial pass.
---

# Composable Design (architecture validation)

In *Righting Software*, an architecture is not done when the services are named. It is valid only when the core use cases are each satisfied by composing the same small set of services, demonstrated as call chains. This skill carries that validation step, which the pipeline otherwise skips: `architecture-layering` ends at naming, and nothing proves composition until the Gate A adversary traces it. The proof belongs to the author first; the adversary re-checks a proof, it does not supply one.

Why validate by composition rather than by coverage: requirements change, that is what requirements do, and no one has ever had time to correctly spec the full use-case set upfront. The design prime directive is **never design against the requirements**. The architecture encapsulates volatilities; the use cases are what it must compose, not a list it mirrors. A design that maps components to requirements is invalidated by the next requirement; a design that composes them survives it.

## When it runs

At the end of `architecture-layering`, after the layer table and names exist and before `gate-review` runs Gate A. Also standalone over an existing `docs/{system-slug}/` artifact set, and whenever a new use case lands against a settled architecture: the composability test for change is the same test.

## Step 1: Designate the core use cases

Read `docs/{system-slug}/behavioral-requirements.md`. A core use case represents the essence of the required behavior: a distinct family of behavior, not a variation on another use case. Most designs have two to five; the rest are supporting variations a composed chain already covers. Mark each core use case in `behavioral-requirements.md` beside its heading. When the designation is not obvious from the artifacts, ask the developer rather than guessing: which families of behavior, if unsupported, make the system pointless?

## Step 2: Compose the call chains

For each core use case, write the call chain using only services `architecture-layering.md` names, top to bottom: Client, Manager, Engine and ResourceAccess, Resource. Hand any chain with branching, three or more participants, or a load-bearing seam (a save/load path, a cross-service workflow handoff, an undo/redo path) to the `sequence-diagram` skill; it records the diagram in `docs/{system-slug}/sequence-diagram.md`, one titled section per diagram, so Gate A and the implementation plan can read it.

The chains must obey the closed layering call rules:

- Clients call only Managers, and only one Manager per use case. A Client stitching multiple Managers together is doing orchestration that belongs in a Manager.
- Managers call Engines and ResourceAccess. A Manager reaches a peer Manager only as a queued, fire-and-forget handoff to start the next workflow, never a synchronous request inside its own use case, and queues to at most one Manager per use case.
- Engines call only ResourceAccess. Engines never call Managers and never call each other; a chained Engine call means the second activity was probably not separately volatile.
- ResourceAccess services never call each other.
- Queued calls target Managers only. Engines and ResourceAccess do not receive queued calls; they are utilitarian executors for a Manager.
- Only Managers publish events (through the Pub/Sub Utility), and only Clients and Managers subscribe: processing an event is almost always the start of a use case, so it lands where use cases start.
- Nothing calls up, nothing skips a layer down to a Resource directly, and every layer may use Utilities.

A chain that cannot be drawn without breaking a rule is a layering fault, not a diagramming problem. Route it back to `architecture-layering`, which also carries the resolution move: a rule violation almost always signals a real underlying need, met compliantly (a queued call, a Pub/Sub Utility), never by opening the architecture.

## Step 3: Apply the composition tests

- **Same set.** Every core use case is satisfied by the same services interacting differently. A use case that demands its own dedicated service is functional decomposition surfacing; route it back to `volatility-decomposition`.
- **Smallest set.** Fewer interacting services is better. If removing a service still leaves every chain composable, it encapsulates nothing the behavior needs; justify it by a named volatility or cut it.
- **Change test.** For the top axes in `volatility-decomposition.md`, ask what the change does to the chains. A contained change swaps one service's internals; a change that re-wires several chains means the volatility is not actually encapsulated.
- **No orphans.** A service no chain touches is either a speculative seam or evidence the use cases are incomplete. Either way it is a finding, not a leftover.
- **Symmetry.** The same call patterns should recur across the chains; expect it, and treat its absence as a finding. If three of a Manager's four use cases publish an event and the fourth does not, ask why the fourth differs: something is missing, something is overdone, or the Manager is a functionally decomposed component without real use-case volatility.

## Step 4: Record the validation

Append a `## Validation` section to `docs/{system-slug}/architecture-layering.md`: one row per core use case with its call chain, the diagram link where one exists, and the verdict, in short plain prose. Composition failures route to the owning stage skill and the validation reruns after the fix. Gate A then reads this section, so the design arrives at the gate already proven by its author.

If a `## Validation` section already exists, this is a revision: read it first, apply the change, preserve the rest, confirm before overwriting.

## Boundaries

This skill proves composition; it does not decompose, layer, or critique. It is distinct from `gate-review` (an independent adversary with starved context; this skill is the author's own proof and runs before it) and from `sequence-diagram` (the drawing tool this skill directs). It adds no speculative seams: every seam a chain touches must trace to a named volatility. An un-designatable core set is a question for the developer, never a guess.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019 (composable design and architecture validation).
- The stages it brackets: `architecture-layering` (before), `gate-review` Gate A (after).
