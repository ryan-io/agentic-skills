---
name: gate-review
description: >
  Run an independent adversarial critique at the gates a design crosses toward code: Gate A
  over design artifacts, Gate B over the implementation plan, Gate C over built code (design
  fidelity plus plan-completeness). Use on "critique this design", "review the plan before we
  build", or "poke holes in the decomposition". Spawns a fresh reviewer agent with only
  the artifacts and governing records, never the author's rationale. Writes no design or code;
  returns a verdict the pipeline acts on.
---

# Design Critique (the adversarial gates)

A design reaches code through the pipeline: behavioral-requirements, volatility-decomposition, architecture-layering, implementation-planning, implementation. An independent adversary judges the work at two points.

Pre-implementation, once `behavioral-requirements.md`, `volatility-decomposition.md`, and `architecture-layering.md` are in place (Gate A judges the design, Gate B the plan that concretes it): a fault here is a markdown edit, the same fault found in code is a refactor, so this point prevents the expensive failure of a wrong decomposition, a misplaced seam, or a plan that drifts from its architecture. Post-implementation, once the build is done (Gate C judges the code against the design it claims to build): a fault here is a same-session fix before the increment closes, catching code that drifted, a purity-boundary leak, or a lifecycle fault the design forbade.

The gate does not stop the workflow. It returns findings; the originating pipeline agent implements the corrections through the owning stage skill, then continues. The block is local: close the must-fix, re-run the gate, proceed. This skill adds no design or code substance; it carries the gate invocation and routing.

## The independence rule (read this first)

A reviewer that shares the author's mental model is not an adversary: the pipeline agent that wrote the design will confirm it if asked to critique it. So the critique runs as a fresh reviewer agent with a deliberately starved context: spawn a subagent per gate (a Gate A, Gate B, or Gate C reviewer). Its tool access is read-only for Gates A and B; Gate C adds the ability to build and run the tests (`dotnet build`, `dotnet test`).

Give the reviewer exactly two things: the work under review (per gate, below) and the governing records it must hold the work against. Do not give it the author's rationale, session narration, chat history, or the conclusion the design argued for. The reviewer re-derives what the design is trying to do from the artifacts, then judges whether it does it. Being led to the author's conclusion is the failure mode the gate exists to break.

## Ground first

Before any gate, gather what binds the design: the project's decision records, business rules, style guides, and any prior design artifacts that govern the work, opening only what applies. This is the record set the reviewer is given. The gate's delta over the author's own grounding: the reviewer grounds independently, never from the author's narration or rationale, and the critique invents no constraint the records do not contain.

## Gate A: after architecture, before planning

Fires once the three design stages have produced `docs/{system-slug}/behavioral-requirements.md`, `docs/{system-slug}/volatility-decomposition.md`, and `docs/{system-slug}/architecture-layering.md`, before planning. Hand the Gate A reviewer the three artifact paths (`architecture-layering.md` including its `## Validation` composition proof from `composable-design`), the relevant sequence diagrams in `docs/{system-slug}/sequence-diagram.md`, and the governing-record list. Its brief weights volatility fidelity above the other lenses (use-case fidelity, layering and seam soundness, simplicity and proportion, lifecycle soundness, impact and problem fit). Verdict vocabulary: READY or REVISE.

## Gate B: after the plan, before implementation

Fires once `implementation-planning` has written `docs/{system-slug}/implementation-planning.md`. Hand the Gate B reviewer the plan path, the design artifact paths, and the record list. It checks plan-vs-design fidelity: every service in the architecture appears in the backlog with the right layer and placement, every named knob survives into the tuning surface, every governing record is honored as a checkable constraint, and nothing in the plan contradicts the design it concretes. A design sound at Gate A does not always survive its concretion into a plan; that is why the gate runs twice. Verdict vocabulary: READY or REVISE.

## Gate C: after implementation, the post-build review

Fires once the build is green (`dotnet build` clean, the NUnit suite passing via `dotnet test`). Hand the Gate C reviewer the diff, the built-code entry points, the design artifacts, the plan (including its `## Built log`), and the record list. Its lenses cover correctness, design fidelity, plan completeness, the purity boundary (no pure-tier reference to a WPF assembly), static-lifecycle safety (no static mutable state), robustness and test gaps, the tuning surface (no knob hardcoded that the plan put on a config seam), impact and problem fit, and simplicity. Verdict vocabulary: CONFIRMED or REFUTED; the reviewer never fixes.

## The verdict

The reviewer returns findings, not edits. The originating pipeline agent acts on them; the gate itself changes nothing. Sort them:

- **Must-fix:** the work is wrong against a use case, a volatility, a layer boundary, a governing record, or, at Gate C, the design it was built from. The originating agent implements the correction through the owning skill, then re-runs the gate. Faults route to: `volatility-decomposition` for a decomposition fault, `architecture-layering` for a layering or seam fault, `composable-design` for a composition-proof fault (a chain that breaks a call rule, a use case the proof omits), `implementation-planning` for a plan fault, `implementation` for a code fault (with a regression test where the gap was a missing test). Do not proceed past the gate with an open must-fix. This is a local fix-and-continue loop, not a halt of the workflow.
- **Tracked debt:** a real weakness not worth blocking on. Record it in the reviewed artifact or the plan's open items, pointing at the governing record, so the item stays visible.
- **Question:** the reviewer cannot tell from the work whether it is right. Surface it to the developer; a question the artifacts cannot answer is a gap in the artifacts.

Every line the verdict leaves in a record (a review-log note, a tracked-debt row, a finding carried into an artifact) states the defect, the evidence, and the owner, in short plain sentences.

A clean gate, no must-fix surviving the pass, is a valid and common result. Note in the artifact or the plan's review log that it ran, and proceed.

## Boundaries

This skill critiques; it owns no artifact or code and writes none of its own. It returns a verdict and routes every change to the owner (the fault-routing map is in The verdict above). It invents no requirement, volatility, constraint, or fix the records do not contain; inventing the answer is the same failure as the author confirming their own design. It complements, not replaces, the author's own composition proof (`composable-design`), which runs before Gate A so the gate checks a proof instead of supplying one. The GoF catalog (`design-patterns`) doubles as a critique checklist at every gate: a hand-rolled mechanism that is an unnamed instance of a known pattern, or a seam whose named pattern does not match what the code does, is a fidelity finding routed to the owning stage.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
- The pipeline it gates: `behavioral-requirements`, `volatility-decomposition`, `architecture-layering`, `composable-design`, `implementation-planning`, `implementation`.
