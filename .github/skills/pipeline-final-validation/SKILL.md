---
name: pipeline-final-validation
description: >
  Validate a finished pipeline run end to end, after Gate C closes: requirements satisfied by
  built, tested behavior; built services matching ## Architecture and ## Validation; the build
  following ## Implementation Plan with deviations logged; gate must-fixes closed. Invoke
  implicitly when Gate C closes on a design-pipeline run (design-autopilot post-impl,
  pipeline-stg6-implementation close, a multi-layer deliver-change). Explicitly on "validate the
  whole pipeline", "did the build satisfy the requirements", or "end-to-end check". Spawns the
  pipeline-validator agent where subagents exist; otherwise runs inline. Routes findings to the
  owning stage; edits no code or design.
tags: [design-pipeline, skill, validation]
---

# Pipeline Final Validation

Each gate judges one stage. This check judges the whole run: did the built, tested code deliver the requirements the design started from, by the architecture and plan the gates passed? It returns PASS or FAIL with a traceability matrix and routes every finding. It edits no code or design.

## When it runs

- After Gate C closes on a pipeline run, before the close step. `design-autopilot` (`post-impl`) and `pipeline-stg6-implementation` invoke it.
- From `deliver-change` when a change touched more than one layer or any design doc section, scoped to the touched system.
- On request, over any design doc whose `## Built log` has entries.

## Step 1: Assemble the inputs

Hand the validator these and nothing else; never the author's rationale or session narration:

- the design doc path, `docs/design/{slug}-design.md` (all sections, `## Built log` included);
- the built-code entry points and the diff for the increment;
- the gate verdicts and verifier reports from Gates A, B, and C;
- the governing records: the ADRs and business rules that bind the system, found index-first (`docs/adr/adr-index.md`, `docs/business-rules/br-index.md`);
- the project's build and test commands (default `dotnet build` / `dotnet test`).

A missing input is a finding, not a reason to skip. A run with no Gate C verdict gets Gate C first, through `pipeline-stage-review`.

## Step 2: Run the validator

- **Can spawn subagents (Claude Code):** spawn `pipeline-validator` with the Step 1 inputs. Its fresh context is the independence.
- **Cannot spawn (Copilot chat, terminal):** run the check inline and say so. Inline validation is weaker than an independent context; offer a standalone handoff holding the brief and the Step 1 inputs for a fresh chat with `@pipeline-validator`. A standalone verdict supersedes the inline one.

The validator checks:

- every requirement and use case is satisfied by built behavior a passing test exercises;
- the built services match `## Architecture` (layer, placement, seams) and the call chains in `## Validation`;
- the build followed `## Implementation Plan`, each deviation logged in `## Built log` with a reason;
- the sections agree with each other (no service, knob, or use case present in one and missing from the next);
- every must-fix from Gates A, B, and C is closed.

It returns PASS or FAIL, a traceability matrix (requirement -> service -> plan item -> code -> test), and findings with evidence.

## Step 3: Save the report

Write the validator's report to `docs/reviews/{date}-{slug}-pipeline-validation.md` (date `YYYY-MM-DD`): verdict, inputs used, the matrix, findings with owner, and whether it ran inline or independent.

## Step 4: Act on the verdict

**FAIL.** Route each finding to its owner; this skill fixes nothing:

- requirements gap: `pipeline-stg1-requirements`, or the developer when the gap is a scope call;
- architecture drift: `pipeline-stg3-architecture`, then rebuild through `pipeline-stg6-implementation`;
- plan deviation: `pipeline-stg5-implementation-planning`, then `pipeline-stg6-implementation`;
- code fault: `pipeline-stg6-implementation`, then Gate C again through `pipeline-stage-review`.

After the fixes, re-run the validator once and update the report. A second FAIL goes to the developer with the open findings; no third loop.

**PASS.** Append a dated "Validated" entry to `## Built log` naming the report path. Preserve every other section. The close step proceeds.

## Revise an existing report

When a report already exists for the slug (a re-run, or a correction):

1. Read the saved report first.
2. Apply the change: the new verdict, closed or new findings, the updated matrix.
3. Preserve the rest, keeping the original run's date and findings under a dated re-run heading.
4. Confirm with the developer before overwriting; save to the same path unless renamed.

## Boundaries

- It validates and routes. It writes only the report and the `## Built log` entry.
- It invents no requirement, constraint, or fix the design doc and records do not contain.
- It never commits; the developer does.

## References

- The gates it follows: `pipeline-stage-review`. The agent: `pipeline-validator`.
- The stages it routes to: `pipeline-stg1-requirements`, `pipeline-stg3-architecture`, `pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`.
- Callers: `design-autopilot`, `pipeline-stg6-implementation`, `deliver-change`.
