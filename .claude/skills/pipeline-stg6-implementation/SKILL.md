---
name: pipeline-stg6-implementation
description: >
  Stage 6 of the design pipeline: pair-program a grounded plan into working code (default stack
  C#/WPF). The agent drives, the developer navigates. Consumes the plan from
  pipeline-stg5-implementation-planning (or the design doc directly), building named services one
  at a time, test first, against the design and governing records. Use on "implement this",
  "pair program", or "turn the design into code" once a plan or architecture exists. If no plan
  exists, run pipeline-stg5-implementation-planning first.
tags: [design-pipeline, implementation, skill]
---

# Pipeline Stage 6: Implementation (pair-programming)

A pairing session, not a batch generator.

- The agent drives: writes code in small steps, thinks aloud.
- The developer navigates: steers, reviews, makes the calls.
- Work moves one service at a time, staying green, with the plan, the design doc, and the ADRs as the source of truth.

Default stack: WPF client tier; business logic in pure C# class libraries under volatility decomposition; dependencies wired in one composition root against Contracts interfaces; `async`/`await` throughout with UI-thread marshaling only at the WPF edge; NUnit tests. A project that pins a different stack in its records overrides these defaults; the loop is stack-independent.

## Input

- Expect the plan in the `## Implementation Plan` section of `docs/design/{slug}-design.md`: backlog, build order, governing records, tuning surface, tests worth writing. Read it first.
- Confirm the plan passed Gate B (the plan notes it ran). A plan that never crossed Gate B gets the gate first, through `pipeline-stage-review`.
- No plan? Read whatever sections exist in the design doc: `## Architecture` (the backlog: services, layers, encapsulated volatilities), `## Volatilities` (change boundaries), `## Requirements` (behavior each Manager orchestrates). This is file-handoff coupling: the skill depends on the artifact's shape, not on an upstream skill having run.
- Change touches architecture and neither plan nor architecture exists? Stop; run `pipeline-stg5-implementation-planning` first. Do not invent a plan to code against.
- Small local change with a clear governing record: you may pair directly, but state you're skipping the planning gate and why.

## Ground before you build

Do not code from the plan alone. Confirm the records the plan names are still in force; code that contradicts a decision is worse than no code.

- Re-read the plan's Governing records and Constraints: that's what the code must satisfy.
- Read the adjacent code: the seams a service plugs into and every call site a change ripples into. Know a shared symbol's blast radius before changing it.
- Build each seam as the pattern the plan named (`design-patterns` carries the catalog).
- Read any referenced sequence diagram (inline in the design doc) as the interaction spec. Code and diagram disagree? Reconcile out loud; update the diagram through `sequence-diagram-creation`.
- Conflict surfaced (plan contradicts a decision, a depended-on ADR undecided, a constraint unmet)? Stop and resolve with the developer before writing code.
- SOLID guides each service's shape as heuristics, not gates. When a principle and a simple local change conflict, prefer simplicity and say why.

## Durable trace

- Keep the `## Implementation Plan` section current: service list, build order, done vs pending.
- Close each session by appending to `## Built log`: services completed, deviations with reasons, skipped or deferred tests with reasons.
- Touch only the `## Implementation Plan` and `## Built log` sections; create the design doc with only those sections if it does not exist.
- This is a working aid for resuming, not a gated record. The real output is the code and its tests.

## Setup

- Confirm the `{slug}`. Load the plan and summarize the architecture back: services, layers, what each encapsulates. That summary is the backlog.
- Check the codebase; work from what's on disk. Layout follows the decomposition: `Contracts` holds the interfaces and DTOs every arrow terminates on; pure-tier projects (Managers, Engines, ResourceAccess) reference only Contracts, never a UI-framework assembly (`PresentationFramework`, `WindowsBase`, `System.Windows.*` on the default stack); `Adapters` implements Contracts interfaces with UI and framework types.
- A needed project doesn't exist? Propose its name and reference set; confirm before creating. The project reference graph enforces the boundary.
- Build order follows the volatility gradient in reverse (least volatile first, because everything above depends on it):
  1. ResourceAccess (atomic business verbs: config, content, persistence, settings)
  2. Engines (activity logic)
  3. Managers (orchestration)
  4. Client edge (Views and code-behind as Humble Objects, ViewModels, input wiring)
- Utilities (logging, pub/sub, security) come in when the first service needs them, registered in the composition root.

## The pairing loop

Repeat per service, smallest useful increment at a time. Under an orchestrator that can spawn agents, the loop runs inside the `impl-worker` agent (Opus 5.5, fresh context) and the orchestrator navigates from the build report; a Fable or Opus seat never types the code itself (`agent-guardrails` Coding Delegation). Inline only where subagents are unavailable, and say so.

### 1. Pick the next unit

Take the next service off the backlog. State what it encapsulates, its layer, its project. Confirm before writing anything.

### 2. Restate the contract

- Name the interface before implementing it.
- The detail that bites: a ResourceAccess contract speaks atomic business verbs (`Credit`, `Save`, `AcquireContent`), never CRUD or IO verbs that leak the resource type (`Insert`, `Open`, `ReadFile`).
- The contract is a Contracts interface when it crosses the pure/UI boundary.
- Confirm with the developer. This is the cheapest place to catch a decomposition error.

### 3. Drive

- Small steps: Contracts interface, implementation, test. Narrate intent briefly; pause at decision points.
- Follow the project's code standards (`csharp-code-standards.instructions.md`, in `.github/instructions/` mirrored at `.claude/rules/`). Doc comments follow `xml-documentation.instructions.md`: one-sentence verb-first `<summary>`, governing record id in a short `<remarks>` where one applies, never a paragraph.
- Verify any framework or package API against documentation for the installed version; confirm a package's presence and version before coding against it.
- Hold the constraints: pure tier never references a UI-framework assembly; every service registers in the composition root against its Contracts interface; no service locators or global state; UI-thread marshaling only at the UI edge; pure tier thread-agnostic (`ConfigureAwait(false)`) with a `CancellationToken` threaded through; no `static` mutable state.
- Never hand-edit generated files; regenerate from source.

### 4. Go green

- Build, run the test, show the result. Red to green before moving on.
- Pure-tier tests run headless (`dotnet test`, NUnit on the default stack). Prefer the pure tier: deterministic, fast, and the decomposition exists so logic is testable without the UI.

### 5. Test for value, not coverage

Every unit that carries logic gets a test, but the test must earn its place. Coverage percentage is not a goal.

- A test adds value when it pins a behavior, a contract, an ADR constraint, or a known bug. It adds nothing restating the implementation or asserting a trivial getter.
- Test the pure tier hard: Engine computations and state transitions, ResourceAccess verbs, Manager orchestration, every ADR-imposed constraint bound to the service.
- Don't test Humble Object Views or code-behind that only forwards; test the implementation behind the interface instead.
- Mock only at owned boundaries (NUnit + Moq, Arrange-Act-Assert). Verify outcomes over interactions; over-mocking produces suites that pass while the app breaks.
- Choosing not to test something? Say so and say why. That sentence is part of the increment.

### 6. Reflect on fidelity

Watch for the smells the layering stage named:

- A ResourceAccess contract leaking `Select`/`Insert`/`Open`/`Read`: the resource type is bleeding through. Rephrase in business verbs.
- A Manager accreting domain logic: a god service forming. Push logic into an Engine, or question the use-case boundary.
- A pure-tier project reaching for a UI-framework assembly: broken boundary. The reference belongs in Adapters behind a Contracts interface.
- An Engine calling a Manager: forbidden. Dependencies run one way, downward.
- A `<summary>` running to a paragraph or restating the name: the doc comment drifted from label to essay.
- A shared symbol changed without visiting its call sites, or a touched component's recorded invariant (an ADR's guarantee, a pinned diagram) shifting silently: the blast radius is escaping the diff.

Drift is a signal. When code and architecture disagree, resolve it out loud: fix the code, revise the design through `pipeline-stg2-volatilities` or `pipeline-stg3-architecture`, or record a new ADR when it is one. When the plan no longer holds, re-plan through `pipeline-stg5-implementation-planning`. Never diverge silently.

### 7. Keep the design record current

- A service landed somewhere new? Update the `## Architecture` placement table.
- A flow changed that a diagram maps? Update the diagram through `sequence-diagram-creation`.
- Stale records force the next agent to reverse-engineer source; that's the failure the record exists to prevent.

### 8. Suggest a small commit

- One conventional commit per unit (`feat`, `test`, `refactor`); imperative, present tense; scope encouraged.
- Suggest the subject and stop. The developer owns the commit. Take the next unit.

## Layer-to-project mapping (default C#/WPF stack)

- **Client** -> the WPF app project (Humble Object Views, ViewModels, input wiring) plus `Adapters` (Contracts implementations using WPF/framework types).
- **Managers and Engines** -> pure C# class libraries referencing only `Contracts`.
- **ResourceAccess** -> pure C# class libraries exposing business verbs; the mechanism (file, DB, HTTP, serializer) stays behind the interface in `Adapters`.
- **Resource** -> external systems: databases, filesystem, queues, third-party services.
- **Contracts** -> the interfaces and DTOs every arrow terminates on.
- **Utilities** -> cross-cutting services (logging, pub/sub, security, configuration) in the composition root.
- The layer fixes the project. Within a project, a new type lands in a per-feature folder; the namespace follows the folder path. A folder segment must not collide with a type name or a common framework type.

## Close

- Once the increment is green, invoke `pipeline-stage-review` at Gate C; a gate with no owner never fires. Close must-fix findings through the owning skill and re-run the gate before the increment closes. Once Gate C closes, `pipeline-final-validation` checks the whole run against the design doc before the increment is called done.
- Summarize: what was implemented, what's left, any drift flagged into the design or a new ADR.
- Update the plan section; append the `## Built log` entry. Record deferred or shortcut work in the plan's open items, pointing at the governing record.
- Keep referenced diagrams current where their flows changed. Offer to continue next session.

## Resuming a session

- Re-read the plan, the design doc, and the current code. Work from disk, not memory.
- Recompute the backlog: compare the architecture's services against what the code implements; continue from the first unimplemented unit.
- Never regenerate existing code; read it, then extend it.
- Architecture or a decision changed since last session? Reconcile with the developer before writing more code.

## Related skills

- `pipeline-stg5-implementation-planning`: produces and owns the `## Implementation Plan` section. Start there when no plan exists; re-plan there when the architecture shifts mid-build.
- `pipeline-stage-review`: Gate B before this skill starts; Gate C when the build is green.
- `design-patterns`: the catalog and the implementation-stage lens; build each seam as the named pattern in its language-native form.
- `sequence-diagram-creation`: draws and revises the inline diagrams; read a referenced one before building its flow, update it when the flow changes.
- `unit-test-creation`: tests over code that already exists, outside this skill's test-first loop.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
