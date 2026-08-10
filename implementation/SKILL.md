---
name: implementation
description: >
  Pair-program a grounded plan into working C#/WPF code: the agent drives, the developer
  navigates. Consumes the plan from implementation-planning (or the design pipeline's artifacts
  directly), building named services one at a time, test first, against the design and
  governing records. Use on "implement this", "pair program", or "turn the design into code"
  once a plan or architecture exists. Build stage after implementation-planning; if no plan
  exists, run that first.
---

# Implementation (Pair-Programming)

This skill runs as a pairing session, not a batch generator. The agent drives: it writes the code in small steps and thinks aloud. The developer navigates: they steer, review, and make the calls. The work moves one service at a time through the architecture, staying green, with the implementation plan, the design artifacts, and the governing records as the source of truth.

This is the build stage of the design pipeline. It turns an implementation plan (or `architecture-layering.md`) into running C#/WPF code. The stack: WPF is the Client tier, business logic lives in pure C# class-library projects under Löwy volatility decomposition, dependencies are wired in a single composition root against Contracts interfaces, async is `async`/`await` throughout with UI-thread marshaling only at the WPF edge, and tests are NUnit.

## Input

This skill expects the plan that `implementation-planning` produces at `docs/{system-slug}/implementation-planning.md`: the grounded service backlog, the build order, the governing records each service must honor, the tuning surface (every knob in that table lands as authored configuration on its owning seam, never a hardcoded constant), and the tests that would add value. Read it first. Confirm the plan passed Gate B (the plan notes the gate ran); a plan that never crossed Gate B gets the gate first, through `gate-review`, before any code is written.

If no plan exists, read whatever design artifacts exist under `docs/{system-slug}/`, in any combination:

- `architecture-layering.md`: the named services, their Löwy layer, and the volatility each encapsulates. This is the backlog.
- `volatility-decomposition.md`: the change boundaries behind each service.
- `behavioral-requirements.md`: the required behavior each Manager orchestrates.

This is file-handoff coupling: the skill depends on the shape of the artifacts, not on an upstream skill having run. If the change touches architecture and neither a plan nor an architecture exists, stop and run `implementation-planning` first; do not invent a plan to code against. For a small, local change with a clear governing record, you may pair directly, but state that you are skipping the planning gate and why.

## Ground before you build

Do not code from the plan alone. Confirm the records the plan names are still in force before the first unit; code that contradicts a decision is worse than no code.

- Re-read the plan's **Governing records** and **Constraints** sections: those are the plan's distilled grounding, and they are what the code must satisfy.
- Read the code the change is adjacent to: the seams a service plugs into and every call site a change ripples into. Gather a shared symbol's blast radius before changing it.
- Build each seam as the GoF pattern the plan named (`design-patterns` carries the catalog and the implementation-stage lens), and re-check the original problem statement at the end.
- Read any sequence diagram the plan references (in `docs/{system-slug}/sequence-diagram.md`) as the interaction spec for its flow; when code and diagram disagree, reconcile out loud and update the diagram through `sequence-diagram`.

If grounding surfaces a conflict (the plan contradicts a governing decision, a decision it depends on is undecided, or a business rule is unmet), stop and resolve it with the developer before writing code. Let SOLID guide each service's shape as heuristics, not gates; when a principle and a simple local change conflict, prefer simplicity and say why.

## Durable trace

The session keeps the plan note at `docs/{system-slug}/implementation-planning.md` current: the service list, the build order, and what is done versus pending. Closing a build session means appending its entry to the plan's `## Built log`: services completed, deviations from the plan with reasons, and any skipped or deferred test with its reason. It is a working aid for resuming across sessions, not a gated record; the real output is the code and its tests.

## Setup

Confirm the `{system-slug}`. Load the plan and the artifacts that exist and summarize the architecture back to the developer: the services, their Löwy layer, and what each encapsulates. That summary is the backlog.

Check the codebase. Projects arrive as systems land; work from what is on disk. The solution layout follows the decomposition: a `Contracts` project holds the interfaces and DTOs that terminate every arrow; pure-tier projects (Managers, Engines, ResourceAccess) reference only Contracts and never a WPF assembly (`PresentationFramework`, `WindowsBase`, `System.Windows.*`); an `Adapters` project implements the Contracts interfaces with WPF and framework types. If a needed project does not exist yet, propose its name and reference set and confirm before creating it; the project reference graph is what enforces the boundary.

Agree on the build order. Follow the architecture's volatility gradient in reverse: implement the least volatile, most reusable parts first, because the things above depend on them.

1. ResourceAccess (atomic business verbs over the resources: config, content, persistence, settings).
2. Engines (the activity logic).
3. Managers (orchestration over the Engines and ResourceAccess).
4. Client edge last (WPF Views and code-behind as Humble Objects, ViewModels, input wiring).

Utilities (logging, pub/sub, security) come in when the first service needs them, registered in the composition root.

## The Pairing Loop

Repeat per service, smallest useful increment at a time.

### 1. Pick the next unit

Take the next service off the backlog. State what it encapsulates, which Löwy layer it lives in, and which project it belongs to. Confirm it is the right next step before writing anything.

### 2. Restate the contract

Name the interface before implementing it, in the layer's contract idiom. The one detail that bites: a ResourceAccess contract speaks atomic business verbs (`Credit`, `Save`, `AcquireContent`), never CRUD or IO verbs that leak the resource type (`Insert`, `Open`, `ReadFile`). The contract is an interface in the Contracts project when it crosses the pure/UI boundary. Confirm it with the developer; this is the cheapest place to catch a decomposition error.

### 3. Drive

Write in small steps: the Contracts interface, then the implementation, then a test. Narrate intent briefly and pause at decision points for the navigator. Follow the project's code standards where they exist. Keep `///` doc comments to the contract: a one-sentence verb-first `<summary>` of what the member does, a governing record id in a short `<remarks>` where one applies, never a paragraph in either.

For any framework or package API the code calls into, verify it against the documentation for the installed version rather than coding from memory, and confirm a package's presence and version before coding against it.

Hold the architectural constraints as you write: the pure tier never references a WPF assembly; every service registers in the composition root against its Contracts interface, no service locators or global state; UI-thread marshaling (the `Dispatcher`) happens only at the WPF edge, the pure tier stays thread-agnostic (`ConfigureAwait(false)`) with a `CancellationToken` threaded through the chain; no `static` mutable state.

Never hand-edit generated files; regenerate them from their source.

### 4. Go green

Build and run the test. Show the result. Red to green before moving on. Pure-tier tests run headless through `dotnet test` with NUnit. Prefer the pure tier: it is deterministic and fast, and the decomposition exists precisely so the logic is testable without the UI.

### 5. Test for value, not for coverage

Every unit that carries logic gets a test, but the test must earn its place. Coverage percentage is not a goal. A test adds value when it pins a behavior, a contract, a business rule, or a known bug. It adds nothing when it restates the implementation, asserts a trivial getter, or exists to move a number.

- Test the pure tier hard: the Engines' computations and state transitions, the ResourceAccess verbs, the Managers' orchestration, and every business rule bound to the service. These are where regressions hurt and where tests pay back.
- Do not write tests for Humble Object Views or code-behind that only forward to an interface; there is no logic to pin. Test the interface's implementation instead.
- Mock only at owned boundaries (NUnit plus a mocking library such as Moq, Arrange-Act-Assert), and verify outcomes over interactions. Over-mocking produces suites that pass while the application breaks.

When you choose not to test something, say so and say why. That sentence is part of the increment.

### 6. Reflect on fidelity

Ask whether the code still matches the design and the records. Watch for the smells the layering skill named:

- A ResourceAccess contract leaking `Select`/`Insert`/`Open`/`Read`: the resource type is bleeding through. Rephrase in business verbs.
- A Manager accreting domain logic: it is becoming a god service. Push the logic into an Engine, or question the use-case boundary.
- A pure-tier project reaching for a WPF assembly: the boundary is broken. The reference belongs in the Adapters project behind a Contracts interface.
- An Engine calling a Manager: forbidden. The dependency runs one way, downward.
- A `<summary>` that runs to a paragraph, narrates mechanism, or restates the name: the doc comment has drifted from a contract label into an essay.
- A shared symbol changed without visiting its call sites, or a touched component's recorded invariant (a decision's guarantee, a business rule, a pinned diagram) shifting silently: the blast radius is escaping the diff.

Drift is a signal, not a nuisance. When the code and the architecture disagree, resolve it out loud: fix the code, or revise the artifact through `volatility-decomposition` or `architecture-layering`, or record the change as a new decision when it is one. When the architecture shifts enough that the plan no longer holds, re-plan through `implementation-planning` rather than improvising past it. Never diverge silently.

### 7. Keep the design record current

When this unit lands a project or changes a flow a diagram maps, update the affected design artifacts before moving on: the architecture document's placement table if a service landed somewhere new, and any sequence diagram in `docs/{system-slug}/sequence-diagram.md` whose flow changed (through `sequence-diagram`). Code that changes the design and leaves the record stale forces the next agent to reverse-engineer source, the failure the record exists to prevent.

### 8. Suggest a small increment

One conventional commit per unit (`feat`, `test`, `refactor`), imperative, present tense, scope encouraged. Suggest the subject and stop; the developer owns the commit. Then take the next unit.

## Layer-to-Project Mapping (WPF)

- **Client** -> the WPF application project: Views and code-behind as Humble Objects, ViewModels, input wiring; plus the `Adapters` project that implements Contracts interfaces with WPF and framework types.
- **Managers and Engines** -> pure C# class libraries that reference only `Contracts`.
- **ResourceAccess** -> pure C# class libraries exposing business verbs; the mechanism (file, database, HTTP, serializer) stays behind the interface in `Adapters`.
- **Resource** -> external systems: databases, the filesystem, message queues, third-party services.
- **Contracts** -> the interfaces and DTOs every arrow terminates on.
- **Utilities** -> cross-cutting services (logging, pub/sub, security, configuration), registered in the composition root.

The layer fixes the project; within a project, a new type lands in a per-feature folder and the namespace follows the folder path. A folder segment must not collide with a type name or a common framework type.

## Close

Summarize what was implemented this session, what is left on the backlog, and any drift flagged back into the design or up into a new decision. Update the plan note and append the session's `## Built log` entry. Record any work deferred or shortcut this session in the plan's open items, pointing at the governing record, so the deferral is carried where the next agent will see it. Keep any sequence diagram the plan referenced current when the flow it maps changed this session. Offer to continue next session.

## Resuming a Session

Use this when returning to a build already in progress.

Re-read the plan, the design artifacts, and the current code first. Work from what is on disk, not from memory. Recompute the backlog: compare the services the architecture lists against what the code already implements, and continue from the first unimplemented unit. Do not regenerate code that exists; read it, then extend it. If the architecture or a governing decision changed since the last session, reconcile it with the developer before writing more code.

## Related skills and handoffs

- `implementation-planning` produces the plan this skill builds from and owns it at `docs/{system-slug}/implementation-planning.md`. Start there when a build touches architecture and no plan exists, and re-plan there when the architecture shifts mid-build.
- `gate-review` runs Gate B over the plan before this skill starts, and Gate C over the built code once the build is green.
- `design-patterns` carries the pattern catalog and the implementation-stage lens: build each seam as the pattern the plan named, in its C#-native form.
- `sequence-diagram` draws and revises the interaction diagrams in `docs/{system-slug}/sequence-diagram.md`; read a referenced one as the flow's spec before building it, and update it through that skill when the flow changes.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
