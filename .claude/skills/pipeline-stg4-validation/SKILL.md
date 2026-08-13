---
name: pipeline-stg4-validation
description: >
  Stage 4 of the design pipeline: validate a layered architecture by composition. Designate core
  use cases, compose each as a call chain through the named services, and show the same small set
  of services satisfies them all. Use for "validate the architecture", "compose the use cases",
  "draw the call chains", or "is this the smallest set of services". Runs at the end of
  pipeline-stg3-architecture, before Gate A, and when a new use case arrives against a settled
  architecture. The author's proof, distinct from pipeline-stage-review's adversarial pass.
tags: [design-pipeline, validation, skill]
---

# Pipeline Stage 4: Composable Design (architecture validation)

An architecture is not done when the services are named. It is valid only when the core use cases are each satisfied by composing the same small set of services, shown as call chains. This stage carries that proof.

- The proof belongs to the author. The Gate A adversary re-checks a proof; it does not supply one.
- Why composition, not coverage: requirements change, and nobody ever specs the full use-case set upfront. The prime directive is **never design against the requirements**. A design that maps components to requirements dies with the next requirement; a design that composes them survives it.

## When it runs

- At the end of `pipeline-stg3-architecture`, after the layer table and names exist, before Gate A.
- Standalone over an existing `docs/design/{slug}-design.md`.
- Whenever a new use case lands against a settled architecture. The composability test for change is the same test.

## Step 1: Designate the core use cases

- Read `docs/design/{slug}-design.md`.
- A core use case is a distinct family of behavior, the essence of what's required; not a variation on another use case. Most designs have two to five.
- Mark each core use case in the design doc's `## Requirements` section, beside its heading.
- Not obvious from the artifacts? Ask the developer: "Which families of behavior, if unsupported, make the system pointless?" Never guess.

## Step 2: Compose the call chains

For each core use case, write the call chain using only services the design doc's `## Architecture` section names, top to bottom: Client, Manager, Engine and ResourceAccess, Resource.

Hand any chain with branching, three or more participants, or a load-bearing seam (a save/load path, a workflow handoff, an undo/redo path) to `sequence-diagram-creation`. It records the diagram inline beside the chain in `## Validation`, one titled subsection per diagram.

The chains must obey the closed-layering call rules:

- Clients call only Managers, one Manager per use case. A Client stitching Managers together is doing a Manager's orchestration.
- Managers call Engines and ResourceAccess. A Manager reaches a peer Manager only as a queued, fire-and-forget handoff starting the next workflow; never synchronously inside its own use case; at most one per use case.
- Engines call only ResourceAccess. Engines never call Managers or each other; a chained Engine call means the second activity probably wasn't separately volatile.
- ResourceAccess services never call each other.
- Queued calls target Managers only. Engines and ResourceAccess never receive them.
- Only Managers publish events (through the Pub/Sub Utility); only Clients and Managers subscribe. Processing an event is almost always the start of a use case.
- Nothing calls up. Nothing skips down to a Resource directly. Every layer may use Utilities.

A chain that can't be drawn without breaking a rule is a layering fault, not a diagramming problem. Route it back to `pipeline-stg3-architecture`. A violation almost always signals a real need; meet it compliantly (a queued call, a Pub/Sub Utility), never by opening the architecture.

## Step 3: Apply the composition tests

- **Same set.** Every core use case is satisfied by the same services interacting differently. A use case demanding its own dedicated service is functional decomposition surfacing; route to `pipeline-stg2-volatilities`.
- **Smallest set.** Fewer interacting services is better. If removing a service leaves every chain composable, it encapsulates nothing the behavior needs: justify it by a named volatility or cut it.
- **Change test.** For the top axes in the design doc's `## Volatilities` section, ask what the change does to the chains. Contained: one service's internals swap. Re-wiring several chains: the volatility is not actually encapsulated.
- **No orphans.** A service no chain touches is a speculative seam or evidence the use cases are incomplete. Either way, a finding.
- **Symmetry.** The same call patterns should recur across chains. If three of a Manager's four use cases publish an event and the fourth doesn't, ask why: something is missing, overdone, or the Manager has no real volatility.

## Step 4: Record the validation

- Append a `## Validation` section to `docs/design/{slug}-design.md`, touching no other section (create the doc first when running standalone against artifacts that live elsewhere).
- One row per core use case: its call chain, the diagram link where one exists, the verdict. Short plain prose.
- Composition failures route to the owning stage skill; re-run the validation after the fix.
- If the section already exists, this is a revision: read it first, apply the change, preserve the rest, confirm before overwriting.

## Step 5: Invoke Gate A

With `## Validation` recorded, invoke `pipeline-stage-review` at Gate A as this skill's final step; a gate with no owner never fires.

- Close every must-fix through the owning stage skill and re-run the gate.
- The design moves to `pipeline-stg5-implementation-planning` only when Gate A is clean.

## Boundaries

- This skill proves composition. It does not decompose, layer, or critique.
- Distinct from `pipeline-stage-review` (independent adversary; runs after this) and `sequence-diagram-creation` (the drawing tool this skill directs).
- It adds no speculative seams: every seam a chain touches must trace to a named volatility.
- An undesignatable core set is a question for the developer, never a guess.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019 (composable design and architecture validation).
- The stages it brackets: `pipeline-stg3-architecture` (before), `pipeline-stage-review` Gate A (after).
