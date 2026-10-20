---
name: deliver-change
description: >
  Deliver a change to existing code: a bugfix, a behavior-preserving refactor, or a tech-debt
  paydown. Use on "fix this bug", "refactor this module", "pay down TD-NNN", "work RF-NNN", or by
  name with a track (`fix`, `refactor`, `debt`). The maintenance counterpart to `design-autopilot`:
  it skips the design stages and Gates A/B, keeps index-first grounding, a behavior-pinning test,
  the Gate C review, and a lighter Definition of Done; anything architectural routes to
  `design-autopilot` or the pipeline stages. Manually invoked, never commits. For a new system,
  use `design-autopilot post-impl`.
tags: [process, skill, tech-debt, testing]
---

# Deliver Change (the Maintenance Loop)

The direct delivery loop for code that already exists: a bugfix, a refactor, or a tech-debt item.

- It skips stages 1 to 5 of the design pipeline and Gates A and B. A bug deviates from specified behavior, a refactor preserves behavior by definition, and a debt item is already decided: none has a new design or plan to gate.
- It keeps what still earns its place: index-first grounding, a test that pins behavior before the change, the smallest correct change, the Gate C review, and a lighter Definition of Done.
- It adds no design logic. The substance lives in the skills it sequences: `pipeline-stg6-implementation`, `pipeline-stage-review` (Gate C only), `unit-test-creation`, and the record skills.

## Roles

- The coding step (Phase 3 and its tests) is delegated to the `impl-worker` agent, an Opus 5.5 worker with a fresh context, whatever the orchestrator's own model (`agent-guardrails` Coding Delegation); the orchestrator grounds, pins the behavior, reviews the build report, and runs the gate. Record edits past a row or two can delegate to `records-worker`. Where subagents are unavailable (Copilot chat, terminal), run the step inline and say so.
- Gate C always runs as an independent review per `pipeline-stage-review`, whatever built the change: independence is the point of the gate.

## Invocation and tracks

Invoked manually, with a track and a target.

- `fix`: a bug. The target is a reproduction or a report of wrong behavior.
- `refactor`: a behavior-preserving restructure. The target is the module, type, or smell, or an `RF-NNN` row in `docs/refactor/refactor-ledger.md`; for a row, flipping it `resolved` joins the Definition of Done.
- `debt`: a `TD-NNN` row in `docs/debt/debt-index.md`. It routes to `fix` or `refactor` by the row's nature; closing the row is its Definition of Done.

Track missing? Infer it from the target and confirm once. Target missing or ambiguous? Ask. Do not guess either.

Flags:

- `--test-plan` (`True` | `False`, default `True`): whether Phase 6 revises affected test plans. `False` skips the `test-plan-creation` step entirely.
- `--list`: print the roster below verbatim and stop. Run no phase, read no file.

```
deliver-change flags:
  --test-plan <True|False>   default: True   Phase 6 test-plan revision; False skips test-plan-creation entirely.
  --list                     (no value)      Print this roster verbatim and stop; no phase, no file, no target.
```

## The routing gate (read this first)

A change belongs here when it works inside the existing architecture and records. Route it to `design-autopilot` or the pipeline stages, with an ADR first through `adr-creation`, when it:

- introduces a new architectural pattern, cross-cutting concern, or third-party dependency;
- moves or creates a layer boundary or a volatility seam (decomposition, not refactoring);
- changes a `Contracts` interface's shape so a consumer can assume something new;
- contradicts or supersedes an Active ADR or business rule.

A refactor inside one service that preserves its contract is this loop. A "refactor" that reshapes the seam between services is a redesign wearing a refactor's name; route it. Unsure? Treat it as a pipeline item and ask. This gate keeps the direct loop from becoming a backdoor around Gates A and B.

## The prime directive: ask, do not guess

Proceed while every decision is grounded in the records; stop and ask the moment one is not. Block when:

- the routing gate trips;
- a bug's root cause is a real fork with no grounded basis to prefer a branch;
- a refactor cannot stay behavior-preserving without a decision;
- the change would need a new pattern, cross-cutting concern, or dependency (an ADR first).

Ask one tight question at the block: the fork, the options, a recommendation. Then resume from the answer.

## Phase 0: Pre-flight

Read-only warm-up. Confirm the project's build and test commands run (named in Repo Signals, `research.instructions.md`). Close with a one-line readiness statement.

## Phase 1: Select and ground

State the target in one line. Ground it index-first, never by scraping a directory:

- Open the corpus indexes and only the rows that bear on the change: `docs/adr/adr-index.md`, the business-rule index, `docs/debt/debt-index.md`, `docs/refactor/refactor-ledger.md`, and the system map (`system-map`) where the project keeps one.
- Read the design doc for the touched system (`docs/design/{slug}-design.md`) where one exists. Its `## Architecture`, `## Implementation Plan`, and `## Built log` describe the code the change lands in. A sequence diagram there maps a flow across services; read it before re-deriving the flow from prose.
- Navigate the source by symbol (`rg`, or the editor's go-to-definition and find-references), not whole-file reads. Gather every call site of each symbol the change touches before editing: that is the blast radius the change must respect.
- An open `RF-NNN` row touching the same files folds into this change when it fits the scope; otherwise it stays put.

For a `debt` run, the `TD-NNN` row and its owning record are ground truth. Read them first; the row's trigger, severity, and category decide the track.

## Phase 2: Pin the behavior (test first)

The phase that makes a direct loop safe. Do not skip it.

- **`fix`.** Write a failing test that reproduces the bug at the tightest layer that shows it, the pure tier where the logic lives. It stays as the regression guard. Not yet isolated? Localize systematically, not by guessing: a hypothesis-trial-refine loop (Zeller), `git bisect` for the failure-inducing commit, binary search over the call graph. Fix the root cause the test pins, not the symptom.
- **`refactor`.** Write characterization tests (Feathers) that pin current observable behavior before touching anything, so "behavior-preserving" is enforced by a test. Code unreachable by a test? Break the dependency through a seam with the smallest safe edit, then characterize. Refactor only on green (Fowler).
- **`debt`.** Run the step for the track the row implies.

## Phase 3: Make the change (smallest correct step)

Build through `pipeline-stg6-implementation`, test first, under its constraints: the pure tier never references a UI-framework assembly; constructor injection against `Contracts` interfaces in the composition root; no service locators; no static mutable state. The change is scoped: no new services, layers, or interfaces. Reaching for a new abstraction trips the routing gate. A refactor candidate outside scope is not license to widen the diff: log it through `refactor-ledger` and keep building.

- **`fix`.** The minimal change that turns the red test green without breaking the suite.
- **`refactor`.** Small behavior-preserving steps, tests after each (Fowler). On red, revert to the last green state and record the failed step's prerequisite (the Mikado Method). A change rippling across the Phase 1 call sites uses parallel change (expand, migrate, contract), green at each step.

## Phase 4: Validate the build

Run the project's build and test commands. The suite must include the Phase 2 test: now passing for a `fix`, still passing for a `refactor`. A red build is a block, not a finding to defer.

## Phase 5: Gate C review

Invoke `pipeline-stage-review` at Gate C over the diff, the touched design doc (if any), and the governing-record list, never this run's rationale. Add the track's lens to the reviewer's brief:

- **`fix`:** the regression test reproduces the original bug (fails without the fix, passes with it); the fix addresses the root cause.
- **`refactor`:** behavior is preserved; the characterization tests still pass and were not weakened, deleted, or edited to fit.

Act on the verdict: must-fix through `pipeline-stg6-implementation` (with a regression test where the gap was a missing test); tracked debt as a row through `tech-debt`. Re-run the suite. Fix and continue; not a halt. A change that touched more than one layer or any design doc section also runs `pipeline-final-validation` scoped to the touched system.

## Phase 5b: Step back

After the Gate C fixes, run `impact-analysis` in its post-build form, from the records, not memory:

1. Did I change what was asked? Re-read the report or `TD-NNN` row cold. A symptom patch beside the root cause, or a refactor that changed behavior the characterization suite missed, is a finding.
2. What changed beyond the diff? Re-check the call sites of every changed symbol and the records now stale.
3. Is the fix more complicated than the problem? If so, the routing gate may have tripped late; re-check it.

Apply small corrections now and re-run the suite. Route larger findings to `tech-debt` or `refactor-ledger`. Put a suspected misread of intent in front of the developer. A clean pass is valid; state it in one line.

## Phase 6: Definition of Done

Decide each record's content in-seat; execute through `records-worker` where available and more than a row or two needs editing. Touch only what the change changed.

- **Tests green.** The full suite, including the Phase 2 test, passing on the project's test command. Show the output.
- **Debt registry.** Flip the `TD-NNN` row to `resolved` with the resolving evidence through `tech-debt`. For any new shortcut, close it now if it fits; otherwise add a `TD` row.
- **Refactor ledger.** Flip any `RF-NNN` row this change resolved to `resolved` with evidence, and land rows the Phase 3 sightings produced, through `refactor-ledger`.
- **Built log.** If the touched system has a design doc, append a dated `## Built log` entry: track, what changed, the guarding test, deviations, skipped tests with reasons. Preserve every other section.
- **ADR.** Usually none. If the change needed a new pattern, cross-cutting concern, or dependency, the routing gate tripped late: stop and take it to `adr-creation` and the pipeline.
- **Business rules.** Only if the fix codifies an invariant the code must now enforce, through `business-rule-creation`. Do not manufacture one.
- **System map.** Update through `system-map` only if the change altered a system's entry points or dependency edges.
- **Test plans.** If the change altered behavior an active plan checks, revise it through `test-plan-creation`. Skip under `--test-plan False` and say so.
- **Conciseness.** Run `concise-documentation` over every document this change created or edited.

## Phase 7: Hand off

Summarize what landed: the change, the evidence (the regression test or the characterization suite), the records touched, any tracked debt. Name any step skipped and why. Suggest one conventional-commit subject (`fix:`, `refactor:`, the debt id in the body) and stop. The developer runs every commit.

## Resuming a partial run

Re-read the tests, the code, and the records on disk; continue from the first incomplete phase.

## What this skill does not do

- It does not design new systems or decompose new volatility; the routing gate sends that to the pipeline, with an ADR.
- It does not skip the pinning test, Gate C, or the step back.
- It does not run Gate A or Gate B.
- It does not commit, and it does not invent an ADR decision, a business rule, or a root cause to keep moving.

## References

- The front door for new systems: `design-autopilot`.
- The skills it sequences: `pipeline-stg6-implementation`, `pipeline-stage-review` (Gate C), `impact-analysis`, `unit-test-creation`, `adr-creation`, `business-rule-creation`, `system-map`, `tech-debt`, `refactor-ledger`, `test-plan-creation`, `concise-documentation`.
- Zeller, Andreas. *Why Programs Fail* (scientific and delta debugging). Feathers, Michael. *Working Effectively with Legacy Code* (characterization tests, seams). Fowler, Martin. *Refactoring* (small steps, refactor on green, parallel change). Ellnestam and Brolund. *The Mikado Method*.
