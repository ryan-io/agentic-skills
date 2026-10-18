---
name: architecture-design-pipeline
description: >
  Run the volatility-based design method interactively, stage by stage: capture required behavior,
  decompose by volatility, layer into an architecture, validate by composition, then Gate A. Use
  for the full design flow rather than one stage, e.g. "design this system", "run the whole
  pipeline", "walk me through the design", or "requirements to architecture". A thin orchestrator
  over pipeline-stg1-requirements, pipeline-stg2-volatilities, pipeline-stg3-architecture, and
  pipeline-stg4-validation, pausing for confirmation between stages. For a hands-off run, use
  design-autopilot.
tags: [design-pipeline, skill]
---

# Architecture Design Pipeline

A conductor, not a new method. It runs four stage skills in order over one artifact, `docs/design/{slug}-design.md`, and ends at Gate A. All design substance lives in the stage skills.

Pipeline: `pipeline-stg1-requirements` -> `pipeline-stg2-volatilities` -> `pipeline-stg3-architecture` -> `pipeline-stg4-validation` -> Gate A.

## Setup

- Ask what system, feature, or problem to design. Derive a kebab-case `{slug}` and confirm it.
- Check for `docs/design/{slug}-design.md`. Sections already present? Offer to resume from the first missing stage rather than redo finished work.
- Tell the developer the stages and that they can stop after any one.

## Step 0: Ground

Before stage 1, ground index-first: open the corpus indexes (`docs/adr/adr-index.md`, the business-rule index, `docs/design/`, the system map where the project keeps one), then only the records that bear on the target. A library or framework capability the design assumes goes through `system-context`; whether an API affords something can decide where a seam goes.

## The stages

Run each, then confirm the developer wants to continue.

1. **`pipeline-stg1-requirements`** writes `## Requirements`.
2. **`pipeline-stg2-volatilities`** reads it and writes `## Volatilities`.
3. **`pipeline-stg3-architecture`** reads it and writes `## Architecture`, with each service's layer, project, folder, and namespace. SOLID informs the shape as heuristics, not gates; add no service or interface just to satisfy one.
4. **`pipeline-stg4-validation`** composes the core use cases as call chains and writes `## Validation`, drawing load-bearing flows through `sequence-diagram-creation`. A composition failure routes back to the owning stage before the gate.

The stage skills run their own lenses (`impact-analysis`, `design-patterns`). Confirm each fired; do not re-apply them. Every section follows the project's writing standard; route a verbose one through `concise-documentation` before the gate reads it.

## Gate A

Invoke `pipeline-stage-review` at Gate A. It carries the mechanics: an independent reviewer given the design doc and governing records only, never the author's rationale. Close every must-fix through the owning stage and re-run the gate; carry the rest as tracked debt. The design does not move to planning with an open must-fix. A clean gate is valid.

## Business rule check

Re-read the sections for derived rules: "always", "never", "must", "at most", "is rejected when". Ground each against the business-rule index so an existing rule is extended, not duplicated. Offer each survivor through `business-rule-creation`; never auto-create. Flag, do not author, a candidate that contradicts an Active record. A clean check is valid; say so.

## Step back

Run `impact-analysis` in its whole-design form, from the records:

1. Did I design what was asked? Re-read the originating ask cold against `## Requirements`.
2. What does this design touch that the doc does not say?
3. Is it more complicated than the problem?

Correct through the owning stage; re-run Gate A if a must-fix-shaped fault moved a section. A clean pass is valid; note it in one line.

## Close

- Summarize the sections written, the doc path, and any business rules captured or flagged.
- Next is `pipeline-stg5-implementation-planning`, which writes `## Implementation Plan` and invokes Gate B as its own final step. Then `pipeline-stg6-implementation` builds from the plan.
- Parked design (settled shape, deferred build)? Capture it through `future-system` so it stays findable.
- For a hands-off run of the whole chain, `design-autopilot` drives it to a plan (`post-stop`) or into reviewed code (`post-impl`).

## Running stages independently

Each stage skill runs standalone off whatever upstream sections exist. A developer with requirements can start at stage 2; one with volatilities can start at stage 3.
