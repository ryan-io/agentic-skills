---
name: impact-analysis
description: >
  Invoke implicitly before any pipeline artifact or code change closes: each pipeline stage, gate,
  and delivery loop runs this lens to check blast radius and problem fit before it finishes.
  Explicit triggers: "what does this touch", "what is the blast radius", "will this break
  anything else", "does this actually solve the problem". Asks three questions (what other
  systems does this touch, what side effects could it cause there, does it solve the stated
  problem) from evidence, and annotates the artifact already being written.
tags: [design-pipeline, impact-analysis, skill]
---

# Impact Analysis (the per-stage impact lens)

A change that is locally correct and globally wrong is the failure this lens prevents:

- a design that shifts an assumption a neighboring system relies on;
- a refactor whose ripple lands in call sites nobody visited;
- an increment that ships a plausible neighbor of the problem it was opened for.

The delivery loops hunt these after the build in their step-back passes (`deliver-change` Phase 5b, `design-autopilot` Step 3b, `architecture-design-pipeline`'s step back). This lens asks the same three questions at authoring time, stage by stage, where a fault is a markdown edit instead of a refactor. It adds no design substance and writes no file of its own; it annotates the section the stage is writing.

## The stance

Apply the lens as a senior implementation engineer. The questions are architectural; the answers are concrete: named systems, symbols, call sites, data ownership, mutation and ordering. Think in the mechanisms where side effects live:

- shared state a second system reads;
- a value type copied where a reference was assumed;
- event and call ordering;
- allocation on a hot path;
- a serialization shape that persisted data already froze;
- static lifetime and static mutable state;
- determinism a consumer depends on.

"Nothing else is affected" is a claim to demonstrate (zero references found, no dependent systems), never to assert.

## The three questions (the floor)

1. **What other systems does this touch?** Enumerate from evidence: the touched systems' dependency edges in the system map (`system-map`) where the project keeps one, and every reference to each symbol the work defines or changes (`rg`, or the editor's find-references). The roster of touched systems is the first annotation; it scopes every later answer.
2. **Will it cause unintended side effects there?** For each touched system, name the assumption this work could shift: an invariant an ADR or business rule records, a contract a `Contracts` interface states, a behavior a test or sequence diagram pins. Name each risk and how the work avoids it, or flag it.
3. **Does it solve the original problem?** Re-read the problem source cold: the design doc's `## Requirements` problem statement, the `TD-NNN` row, the bug report, or the developer's framing. Trace the work back to it. Solving a plausible neighbor is the finding this question exists to catch.

These are the floor. Derive further questions from context: the touched systems' own concerns (a persistence-adjacent change asks about format tolerance; a concurrency-adjacent one about ordering), the hot paths, the records' open questions.

## Ground first

Answers come from the records and the code, never memory. Open the corpus indexes (`docs/adr/adr-index.md`, `docs/design/`, `docs/debt/debt-index.md`) and the touched systems' entries; trace symbols by search, not by scraping files. For question 3, fetch the problem statement from its owning record and quote it, so the trace is against the words, not a paraphrase.

## The lens, by stage

### pipeline-stg1-requirements (`## Requirements`)

Pin the problem statement: quote the originating ask verbatim, so every later stage and gate traces to the same words. Name the existing systems the required behavior composes with; an actor or activity implying a system the section never names is a gap to flag.

### pipeline-stg2-volatilities (`## Volatilities`)

For each volatility that crosses into an existing system, name that system and the assumption the new axis puts under pressure. A decomposition that moves or reshapes an existing seam is a side effect on every consumer of that seam; say so explicitly.

### pipeline-stg3-architecture (`## Architecture`)

Check the composition against the system map: every existing system the services call or are called by, with new or changed dependency edges stated. The smell is unintended coupling: a service reaching a system the use cases never mention, or a changed contract on an interface an unrelated system consumes. Confirm the architecture still answers the pinned problem, not a generalization of it.

### pipeline-stg5-implementation-planning (`## Implementation Plan`)

Fold the three answers into the plan: the touched-systems roster with edges, each side-effect risk as a checkable condition in Constraints to honor, and the problem-statement trace (which services deliver which acceptance criterion). A touched system the plan omits is drift for Gate B; put it in the plan instead.

### pipeline-stg6-implementation (the code)

Before changing a shared symbol, find every reference and visit or account for each call site. The blast radius is gathered before the edit, not discovered by the test suite. Re-check question 3 at the end of the build: the green suite proves the code does what the plan said; this proves the plan's outcome is what was asked.

### test-plan-creation (the checklist)

The touched-systems roster drives the systems-under-test table. Each named risk from the plan gets a check that would catch it. At least one check traces to the original problem statement, so the plan proves the problem is solved, not merely that new code runs.

### The gates

Not an annotation target. At Gates A, B, and C the independent reviewer re-asks all three questions from the artifacts and records alone, never seeing the author's annotations; `pipeline-stage-review` carries that procedure. This skill is the author-side half.

## Boundaries

- It checks; it owns no artifact. Route anything heavier to the owner: a missing requirement to `pipeline-stg1-requirements`, a decomposition fault to `pipeline-stg2-volatilities`, a seam change to `pipeline-stg3-architecture`, a plan fault to `pipeline-stg5-implementation-planning`, a new decision to `adr-creation`.
- A side-effect fork with no grounded resolution is a question for the developer, not a guess.
- An impact finding never justifies a speculative seam; route real new volatility through the pipeline.

## References

- Invoked by: the pipeline stages, `pipeline-stage-review`, `test-plan-creation`, and the loops `architecture-design-pipeline`, `design-autopilot`, `deliver-change`, `pair-programming`.
- Grounding: `system-map` (dependency edges).
- Sibling lens: `design-patterns`.
