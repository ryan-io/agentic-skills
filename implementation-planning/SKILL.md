---
name: implementation-planning
description: >
  Produce a grounded implementation plan before code is written, so the build honors every
  decision and rule already binding it. Use on "plan the implementation", "scope this before
  coding", or when handed an architecture and wanting a plan, not code. Reads the design
  artifacts and governing records, surfaces conflicts before coding, and writes the plan to
  docs/{system-slug}/implementation-planning.md for implementation to build from: the gate stage
  after architecture-layering. For the build, use implementation.
---

# Implementation Planning (the Pre-Build Gate)

This skill is the gate between a design and its code. It produces one artifact, an implementation plan, and it produces nothing else: no production code, no scaffolding. The plan exists so that when `implementation` starts pairing, every service has already been checked against the decisions, rules, and prior thinking that bind it. Coding first and discovering the binding later is the failure this gate prevents.

## When to use

Use it before implementing anything that touches architecture: a new system, a new service, a cross-cutting concern, or a change that ripples across the Löwy layers. Run it after `architecture-layering` and before `implementation`. Skip it only for a small, local change with a single clear governing record, and even then say you are skipping the gate and why.

If the user asks to "implement X" and no plan exists, run this skill first, then hand off. If a plan already exists for the `{system-slug}`, read it and revise it rather than starting over (see the revise step).

## Input

Confirm the `{system-slug}` and the target: the system, feature, or change to plan. The plan draws on whatever exists; none of these are required, but each one that exists must be consulted:

- `docs/{system-slug}/architecture-layering.md`, `docs/{system-slug}/volatility-decomposition.md`, `docs/{system-slug}/behavioral-requirements.md`: the design pipeline output. `architecture-layering.md` is the service backlog; `volatility-decomposition.md` is the change boundary behind each service; `behavioral-requirements.md` is the required behavior.

If the target has no design artifacts and the change is architectural, stop and recommend running the design pipeline first. Do not invent an architecture to plan against.

## The grounding pass

This is the substance of the skill: gather everything that binds the build before writing the plan. Read what governs the change; do not scrape whole corpora when a targeted read answers the question.

- **Source.** Survey the area's existing code: the seams a change plugs into and the call sites it ripples into, so the build order and risk notes match the code as it is.
- **Decisions.** Every architecture decision record (or equivalent design decision the project keeps) that binds the change, with what it constrains. Flag any undecided or proposed decision the plan would depend on as a developer question, not an assumption.
- **Rules.** Every business rule the change touches becomes an acceptance test in the plan, not a footnote.
- **Prior design work.** The other `docs/{system-slug}/` artifact sets this plan extends or must not contradict.
- **External evidence.** When the change leans on a library or framework subsystem, verify the API surface against documentation for the installed version rather than recalling it, and confirm a package's presence and version before the plan leans on its API or proposes a new dependency: an already-present "new" dependency is a version check, not a decision.
- **Diagrams.** Any sequence diagram in `docs/{system-slug}/sequence-diagram.md` whose flow this build implements. Read it into the service backlog and build order and link it in the plan; a flow worth a picture with no diagram is a `sequence-diagram` handoff.
- **Patterns.** Apply `design-patterns` per its planning-stage section: write the named patterns into the plan as the shape each service takes.
- **Composition proof.** Read `architecture-layering.md`'s `## Validation` section (`composable-design`): the core use cases and their call chains are the interaction spec the service backlog must serve. If the architecture arrives without one, run `composable-design` before planning past it.

## The plan

Write the plan to `docs/{system-slug}/implementation-planning.md`. This is the same path `implementation` reads as its backlog note, so the two skills share one artifact: this skill creates it, `implementation` keeps it current. Write in short, plain, concrete prose.

The plan holds:

- **Scope.** What is being built, in one paragraph, and explicitly what is out of scope. Each out-of-scope deferral that is real debt (a piece left for later, not merely unrelated) is listed here with the record that governs it, so the deferral is visible rather than buried.
- **Governing records.** The decisions, business rules, and design documents the build must honor, each with the one line of what it constrains. This is the output of the grounding pass, not a generic list.
- **Impact.** The systems and components the build touches, with what depends on each (what the change can ripple into), each side-effect risk stated as a checkable condition, and the problem-statement trace: which backlog services deliver which acceptance criterion. A component the build touches that the plan does not mention is drift for Gate B to catch; put it here instead.
- **Constraints to honor.** The hard boundaries pulled from the records, stated as checkable conditions. The stack baseline: the pure business-logic tier never references WPF assemblies (`PresentationFramework`, `WindowsBase`, `System.Windows.*`); every service registers in the composition root against its Contracts interface, no service locators or static globals; UI-thread marshaling (the `Dispatcher`) happens only at the WPF edge, and the pure tier stays thread-agnostic (`ConfigureAwait(false)`); no static mutable state. Plus any system-specific rule the records impose.
- **Service backlog and build order.** The services from `architecture-layering.md`, each tagged with its Löwy layer and the volatility it encapsulates, ordered least-volatile-first (ResourceAccess, then Engines, then Managers, then Client edge), and each carrying its target project, folder, and namespace, so `implementation` builds each service into the right place instead of deciding placement mid-build.
- **Tuning surface.** The knob table: name, unit, expected range, and owning configuration seam carried from `architecture-layering.md`; the plan completes each row with a default value. Knobs land as authored configuration on their seams, never hardcoded constants. A knob the architecture named that the plan drops is drift for Gate B to catch.
- **Referenced diagrams.** Any sequence diagram from `docs/{system-slug}/sequence-diagram.md` that maps a flow this build implements, linked by section, so `implementation` follows the same interaction spec rather than re-deriving it. If a flow that warrants one has no diagram, note it as a `sequence-diagram` handoff.
- **Tests that would add value.** Per service, the behaviors and business rules worth pinning with NUnit, and what is deliberately not worth testing (Humble Object forwarders, trivial getters). Coverage percentage is explicitly not a goal. This sets up `implementation` to test for value, not for a number.
- **Open questions and conflicts.** Every undecided decision depended on, every place the design and a governing record disagree. Each is a question for the developer.
- **Built log.** A `## Built log` section, append-only, one dated entry per build session: the services completed, deviations from the plan with reasons, and any skipped or deferred test with its reason. `implementation` updates it as the build advances, and Gate C reads it (a skipped test whose reason is not recorded here is a Gate C finding). Empty at plan time; the build fills it.

## The gate

The plan is a gate, not a rubber stamp. If the grounding pass surfaced an unresolved conflict, a dependency on an undecided design decision, a missing decision, or a contradiction between the design and a governing record, stop and put it in front of the developer before the plan is called done. Surface it; do not resolve it by guessing. A new architectural pattern, cross-cutting concern, or third-party dependency the plan would introduce is a decision for the developer first; propose it, do not assume it.

When the plan is grounded and the open questions are answered or explicitly accepted as risks, it is ready for Gate B. Before `implementation` builds from it, `gate-review` runs Gate B: it checks plan-vs-design fidelity over the plan plus the design artifacts plus the governing records, not the author's rationale. Invoke `gate-review` at Gate B as the final step of this skill and note in the plan that it ran; a gate with no owner never fires. Hand off to `implementation` only after Gate B is clean.

## Revise an existing plan

When a plan already exists for the `{system-slug}`, read it first and work from its current contents, not memory. Apply the requested change, re-run the parts of the grounding pass the change touches (a new decision, a changed rule, a resolved conflict), preserve the rest of the plan and its structure, confirm before overwriting, and save to the same path. When a change replaces a plan wholesale rather than revising it, mark the old plan superseded at the top and say what replaced it. If a record the plan rests on has changed since the plan was written, reconcile it with the developer rather than letting the plan drift from the decision.

## Boundaries

This skill plans; it does not build. It writes the plan at `docs/{system-slug}/implementation-planning.md` and touches no code and no other record. It does not edit decision records, business rules, or design artifacts; when grounding shows one of those is wrong or missing, it routes to the stage that owns it (`volatility-decomposition`, `architecture-layering`) or to the developer.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
