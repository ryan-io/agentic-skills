---
name: design-autopilot
description: >
  Drive the design pipeline to completion autonomously, halting only on genuine uncertainty. Use
  for "run the pipeline autonomously", "take this from requirements to a plan on your own",
  "autopilot the architecture", "design and build this system", or a mode flag (`post-stop`,
  `post-impl`). Runs pipeline-stg1 through pipeline-stg4 with Gate A, then
  pipeline-stg5-implementation-planning with Gate B; `post-impl` continues into
  pipeline-stg6-implementation (delegated to `impl-worker` where subagents exist), the Gate C
  review, and pipeline-final-validation. The design-and-build front door for new systems. Always manually invoked, bounded by
  Ask-Do-Not-Guess, never commits. For an interactive stage-by-stage run, use
  architecture-design-pipeline.
tags: [design-pipeline, process, skill]
---

# Design Autopilot

Carries a design from requirements to a gated plan, or on into reviewed code, with minimal developer input. It adds no design logic: it runs the pipeline stage skills in order, grounded in the project's records, until it reaches the chosen stopping point or hits something it cannot decide alone.

It is the autonomous counterpart to `architecture-design-pipeline`, which pauses between stages. This one runs the stages back to back and replaces "confirm before continuing" with one sharper rule: proceed when grounded, stop and ask when not.

## Roles

- The orchestrating session runs Steps 0 to 2 and holds all judgment in one context.
- Gate reviews spawn the role-bound reviewers through `pipeline-stage-review` (`gate-a-reviewer`, `gate-b-reviewer`, `gate-c-reviewer`).
- In `post-impl`, Step 3 spawns the `impl-worker` agent so compile-and-test churn stays out of this context. A large grounding sweep may delegate to `grounding-scout`.
- Where subagents are unavailable (Copilot chat, terminal), run the step inline and say so. Inline gates follow `pipeline-stage-review`'s inline procedure, including the optional standalone handoff.

## Invocation and modes

Invoked manually with a target and a mode.

- **Target:** the system or feature as the developer states it, plus a kebab-case `{slug}`. Derive the slug and confirm it. The run writes one artifact, `docs/design/{slug}-design.md`.
- `post-stop` (the conservative default): run stages 1 to 5 with Gates A and B, end at a gated `## Implementation Plan`, write no production code.
- `post-impl`: everything `post-stop` does, then build the plan (Step 3) and close with Gate C and the step back.

Mode missing? Ask once, recommending `post-stop`. Target missing or ambiguous? Ask. Do not guess either.

## The prime directive: ask, do not guess

The run proceeds without check-ins while every decision is grounded in the records. It has two equal and opposite failure modes: asking questions the records already answer, and inventing an answer the records do not contain.

Stop and ask when, and only when, you are blocked:

- a requirement or scope boundary is ambiguous and no record resolves it;
- a design choice is a real fork with no grounded basis to prefer one branch;
- the work contradicts an Active ADR or business rule, or depends on a Proposed (undecided) ADR;
- the work would introduce a new architectural pattern, cross-cutting concern, or third-party dependency (an ADR first, through `adr-creation`).

Ask one tight question at the moment of the block: the fork, the options with tradeoffs, a recommendation. Resume from the answer. Do not stockpile questions, and do not lower the bar for "grounded" to avoid asking.

## Step 0: Take the project context (index-first)

Before any stage, ground the target index-first: open the corpus indexes (`docs/adr/adr-index.md`, the business-rule index, `docs/design/`, `docs/debt/debt-index.md`, the system map where the project keeps one), then only the records that bear on the target. Never scrape a directory.

- Read any existing `docs/design/{slug}-design.md`, and the other design docs this one extends or must not contradict.
- The developer's statement of the task is the problem statement. Quote it into `## Requirements` (stage 1 does this); its stated boundary is a hard scope limit. A needed addition beyond it is a block to raise, never a silent inclusion.
- When the target leans on a library, framework, or external fact, route it through `system-context` rather than designing from memory.

## Step 1: Stages 1 to 3, back to back

Invoke in order over `docs/design/{slug}-design.md`, suppressing the inter-stage confirmation pauses:

1. `pipeline-stg1-requirements` writes `## Requirements`.
2. `pipeline-stg2-volatilities` writes `## Volatilities`.
3. `pipeline-stg3-architecture` writes `## Architecture`, including each service's layer, project, folder, and namespace, so the build lands in the right place from the first file.

A stage that cannot proceed on grounded requirements is a block. The stage skills invoke their own lenses (`impact-analysis` at every stage; `design-patterns` at decomposition and layering, where a pattern that would be new cross-cutting structure needs an ADR first). Confirm each lens fired.

No navigator reviews an autonomous run's prose, so verbosity accretes silently. Hold every section to the project's writing standard as it is written.

## Step 1a: Stage 4, validate by composition

Invoke `pipeline-stg4-validation`: designate the core use cases, compose each as a call chain through the named services, and write `## Validation`. A use case that breaks a call rule, or a service no chain touches, routes back to the owning stage. A core-use-case designation with no grounded basis is a block.

Lean on `sequence-diagram-creation` more than an interactive run would. A Mermaid diagram captures a complex flow in little text that the next stage reads directly. Draw one for any flow with branching, loops, retries, parallelism, or three or more participants, inline in the section the flow belongs to. A flow you cannot diagram without guessing is a block.

## Step 1b: Gate A

Invoke `pipeline-stage-review` at Gate A over the design doc and the governing-record list only, never this run's rationale. Route a grounded must-fix to the owning stage (`pipeline-stg2-volatilities`, `pipeline-stg3-architecture`, `pipeline-stg4-validation`), apply it, re-run the gate. A must-fix whose resolution is an ungrounded fork is a block. Carry tracked debt into the doc. Never pass with an open must-fix.

## Step 1c: Derived business rules

A design derives rules, not just architecture. Re-read `## Requirements`, `## Volatilities`, and `## Architecture` for statements of the form "always", "never", "must", "at most", "is rejected when". Ground each against the business-rule index and `docs/adr/adr-index.md`, so an existing rule is extended, not duplicated.

- Never author a rule unprompted; that invents a domain commitment.
- Surface each surviving candidate with the line it came from, and offer to capture it through `business-rule-creation`.
- A candidate that contradicts an Active rule or ADR is a block. A clean check is valid; record it and continue.

## Step 2: Stage 5, the implementation plan

Invoke `pipeline-stg5-implementation-planning`. It re-grounds against the full record and writes `## Implementation Plan` plus an empty `## Built log`. Let it run its grounding pass rather than duplicating it here. An unresolved conflict, an undecided ADR, or a contradiction with an Active record is a block.

## Step 2a: Gate B

Invoke `pipeline-stage-review` at Gate B over the design doc and the record list only. It checks the plan still honors the design: every service traced, layers and build order right, every governing record a checkable constraint. Route a grounded must-fix to `pipeline-stg5-implementation-planning` (or the upstream stage), re-run, and never enter implementation with an open must-fix.

Once Gate B is READY, run `concise-documentation` over the design doc: zero em dashes, no buzzwords, every fact kept.

In `post-stop` this is the end. Summarize the design doc's sections and path, name the plan as the handoff point, and stop. If the developer parks the plan rather than building soon, offer `future-system` so the designed-but-unbuilt system stays findable.

## Step 3 (post-impl): Stage 6, implementation

Spawn `impl-worker` with the design doc path and the increment scope. It builds through `pipeline-stg6-implementation` service by service, test first, under the plan's constraints, keeps `## Implementation Plan` and `## Built log` current, and returns a compact report: files added and changed, test counts, deviations from the plan. Where subagents are unavailable, run `pipeline-stg6-implementation` inline and say so.

Handle the report under the prime directive. Reconcile a grounded deviation into the doc; an ungrounded fork is a block. Drift routes back to the owning stage or up into a new ADR, never diverges silently. The worker never commits.

## Step 3a (post-impl): Gate C

Once the project's build and test commands are green (default `dotnet build` / `dotnet test`), invoke `pipeline-stage-review` at Gate C over the diff, the built-code entry points, the design doc (plan and Built log included), and the record list, never this run's rationale. Implement each must-fix through `pipeline-stg6-implementation` (a regression test where the gap was a missing test), re-run the gate, and never pass with an open must-fix. Tracked debt becomes a row through `tech-debt`.

- Once Gate C closes, invoke `pipeline-final-validation` (it spawns `pipeline-validator` where subagents exist). A FAIL routes each finding to its owning stage and re-validates once.

## Step 3b (post-impl): Step back

After the Gate C fixes, run `impact-analysis` in its post-build form, from the records, not memory:

1. Did I build the stated value? Re-read the problem statement in `## Requirements` cold.
2. What changed beyond the diff? Call sites of changed symbols, dependency edges of touched systems, records now stale.
3. Is any of it more complicated than the problem?

Apply small corrections through `pipeline-stg6-implementation` and re-run the suite. Carry larger ones as `tech-debt` rows. Put a suspected misinterpretation in front of the developer. A clean pass is valid; state it in one line.

## Close (post-impl)

- Requires a PASS from `pipeline-final-validation`, logged in `## Built log`. A standing FAIL goes to the developer, not to the close.
- Summarize what was built, test results with output, and any deviation recorded in `## Built log`.
- Name the records still to complete and offer each through its owner: a new decision through `adr-creation`, a derived rule through `business-rule-creation`, a system-map entry through `system-map`, deferrals through `tech-debt`, out-of-scope restructuring through `refactor-ledger`.
- Suggest one conventional commit subject per increment and stop. The developer commits.

## What the autopilot does not do

- It does not commit.
- It does not invent requirements, decisions, or architecture to avoid asking.
- It does not author business rules unprompted.
- It does not skip stage 5, Gate A, Gate B, or (wherever it produces code) Gate C and the step back.
- It writes no production code in `post-stop`; in `post-impl` the orchestrating context writes none either when `impl-worker` is available.
- It adds no design logic; the substance lives in the stage skills.

## Resuming a run

Re-read `docs/design/{slug}-design.md` and the current code; continue from the first missing section or unbuilt service. Work from disk, not memory. A record the work rests on changed since the last run? Reconcile it first; an unreconcilable change is a block.

## References

- The stages it runs: `pipeline-stg1-requirements`, `pipeline-stg2-volatilities`, `pipeline-stg3-architecture`, `pipeline-stg4-validation`, `pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`, and the gates in `pipeline-stage-review`.
- Supporting skills: `impact-analysis`, `design-patterns`, `sequence-diagram-creation`, `system-context`, `business-rule-creation`, `tech-debt`, `future-system`, `concise-documentation`.
- The interactive counterpart: `architecture-design-pipeline`. The maintenance counterpart: `deliver-change`.
