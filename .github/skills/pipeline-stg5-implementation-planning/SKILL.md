---
name: pipeline-stg5-implementation-planning
description: >
  Stage 5 of the design pipeline: produce a grounded implementation plan before code is written,
  so the build honors every decision and rule already binding it. Use on "plan the
  implementation", "scope this before coding", or when handed an architecture and wanting a plan,
  not code. Reads the design doc and governing records, surfaces conflicts before coding, and
  writes the ## Implementation Plan section of docs/design/{slug}-design.md for
  pipeline-stg6-implementation to build from: the gate stage after pipeline-stg3-architecture
  and pipeline-stg4-validation.
tags: [design-pipeline, planning, skill]
---

# Pipeline Stage 5: Implementation Planning (the pre-build gate)

The gate between a design and its code. It produces one thing, the implementation plan, and nothing else: no production code, no scaffolding.

The plan exists so that when `pipeline-stg6-implementation` starts pairing, every service has already been checked against the ADRs and prior thinking that bind it. Coding first and discovering the binding later is the failure this gate prevents.

## When to use

- Before implementing anything that touches architecture: a new system, a new service, a cross-cutting concern, a change that ripples across the layers.
- After `pipeline-stg3-architecture` and its `pipeline-stg4-validation` proof; before `pipeline-stg6-implementation`.
- Confirm Gate A ran clean on the design (`pipeline-stg4-validation` invokes it). A design that never crossed Gate A gets that gate first.
- Skip only for a small, local change with a single clear governing record. Even then, say you're skipping the gate and why.
- Asked to "implement X" with no plan? Run this skill first, then hand off. A plan already exists? Revise it; don't start over.

## Input

Confirm the `{slug}` and the target: the system, feature, or change to plan.

- `docs/design/{slug}-design.md` is the design pipeline output: `## Architecture` is the service backlog, `## Volatilities` the change boundary behind each service, `## Requirements` the required behavior, `## Validation` the composition proof.
- No design sections and the change is architectural? Stop and recommend running the design pipeline first. Do not invent an architecture to plan against.

## The grounding pass

The substance of the skill: gather everything that binds the build before writing the plan. Read what governs the change; don't scrape whole corpora when a targeted read answers the question.

- **Source.** Survey the area's code: the seams the change plugs into, the call sites it ripples into. Build order and risk notes must match the code as it is.
- **Decisions.** Every ADR that binds the change, and what it constrains. ADRs are always obeyed: a checkable constraint an ADR imposes becomes an acceptance criterion in the plan, not a footnote. An undecided or proposed ADR the plan depends on is a developer question, not an assumption.
- **Prior design work.** The other design docs this plan extends or must not contradict.
- **External evidence.** When the change leans on a library or framework, verify the API surface against documentation for the installed version. Confirm a package's presence and version before leaning on it; an already-present "new" dependency is a version check, not a decision.
- **Diagrams.** Any sequence diagram in the design doc whose flow this build implements. Read it into the backlog and build order; link it. A flow worth a picture with no diagram is a `sequence-diagram-creation` handoff.
- **Patterns.** Apply `design-patterns` per its planning-stage section: write the named patterns into the plan as the shape each service takes.
- **Composition proof.** Read the design doc's `## Validation` section: the core use cases and their call chains are the interaction spec the backlog must serve. Missing? Run `pipeline-stg4-validation` before planning past it.

## The plan

Write the plan as the `## Implementation Plan` section of `docs/design/{slug}-design.md`. The same section is `pipeline-stg6-implementation`'s backlog note: this skill creates it, the build keeps it current and fills `## Built log`. Standalone runs included: check for the doc first; if present, touch only this section; if absent, create it with only this section. Short, plain, concrete prose.

The plan holds:

- **Scope.** What is being built, one paragraph, and explicitly what is out of scope. Each deferral that is real debt is listed with the record that governs it, so it stays visible.
- **Governing records.** The ADRs and design documents the build must honor, each with one line on what it constrains. The output of the grounding pass, not a generic list.
- **Impact.** What the build touches and what depends on each touched piece. Each side-effect risk stated as a checkable condition. The problem-statement trace: which backlog services deliver which acceptance criterion. A touched component the plan doesn't mention is drift for Gate B to catch; put it here instead.
- **Constraints to honor.** The hard boundaries from the records, stated as checkable conditions. Default C#/WPF stack baseline: the pure tier never references WPF assemblies (`PresentationFramework`, `WindowsBase`, `System.Windows.*`); every service registers in the composition root against its Contracts interface; no service locators or static globals; UI-thread marshaling (`Dispatcher`) only at the WPF edge; pure tier thread-agnostic (`ConfigureAwait(false)`); no static mutable state. Plus any system-specific rule the records impose.
- **Service backlog and build order.** The services from `## Architecture`, each tagged with its layer and the volatility it encapsulates. Ordered least-volatile-first: ResourceAccess, Engines, Managers, Client edge. Each carries its target project, folder, and namespace, so the build lands in the right place from the first file.
- **Tuning surface.** The knob table from `## Architecture` (name, unit, expected range, owning configuration seam), completed with a default value per row. Knobs land as authored configuration, never hardcoded constants. A knob the architecture named that the plan drops is drift for Gate B.
- **Referenced diagrams.** Sequence diagrams in the design doc that map flows this build implements, linked by their `### seq-` subsections. A flow that warrants one but lacks it: note a `sequence-diagram-creation` handoff.
- **Tests that would add value.** Per service: the behaviors and ADR-imposed constraints worth pinning with the project's test framework (NUnit on the default stack), and what deliberately isn't worth testing (Humble Object forwarders, trivial getters). Coverage percentage is explicitly not a goal.
- **Open questions and conflicts.** Every undecided decision depended on; every place the design and a record disagree. Each is a question for the developer.
- **Built log.** A `## Built log` section, append-only, one dated entry per build session: services completed, deviations with reasons, skipped or deferred tests with reasons. Empty at plan time; the build fills it; Gate C reads it (an unexplained skipped test is a Gate C finding).

## The gate

The plan is a gate, not a rubber stamp.

- Grounding surfaced an unresolved conflict, a dependency on an undecided ADR, a missing decision, or a contradiction? Stop and put it in front of the developer before the plan is called done. Surface; don't resolve by guessing.
- A new pattern, cross-cutting concern, or third-party dependency the plan would introduce is a developer decision first. Propose it, don't assume it.
- When the plan is grounded and open questions are answered or accepted as risks: invoke `pipeline-stage-review` at Gate B as this skill's final step, and note in the plan that it ran. A gate with no owner never fires.
- Hand off to `pipeline-stg6-implementation` only after Gate B is clean.

## Revise an existing plan

- Read the current plan first; work from its contents, not memory.
- Apply the change. Re-run the parts of the grounding pass the change touches. Preserve the rest. Confirm before overwriting.
- Replacing a plan wholesale? Mark the old one superseded at the top and say what replaced it.
- A record the plan rests on changed since it was written? Reconcile with the developer; don't let the plan drift from the decision.

## Boundaries

- This skill plans; it does not build. It writes the `## Implementation Plan` section and touches no code and no other record.
- It does not edit ADRs or design sections. When grounding shows one is wrong or missing, route to the owner (`pipeline-stg2-volatilities`, `pipeline-stg3-architecture`) or the developer.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
