---
name: pair-programming
description: >
  Run a live, informal pairing session: quick fixes, small refactors, parameter tuning,
  whiteboarding, without delivery-loop ceremony. Use on "let's pair on X", "pair with me", "let's
  tune this", "whiteboard this with me", or any live back-and-forth over named code. Keeps light
  index-first grounding, small green steps, and a routing gate: governed changes route to
  deliver-change, new systems to design-autopilot. Never commits.
tags: [pairing, process, skill]
---

# Pair Programming (the Live Session)

The informal front door: the developer and the agent working one problem in real time. Three modes interleave in one conversation: whiteboarding an approach, tuning parameters, and landing small fixes or refactors.

- It drops the delivery-loop ceremony: no phases, no gates, no Definition of Done.
- It keeps the rails that make informal work safe: light index-first grounding, small green steps, the routing gate, and Ask-Do-Not-Guess.
- `deliver-change` is the governed maintenance loop. This session often precedes it, or replaces it when the change is too small to need a gate.

## Role

The session runs in-seat: pairing is live judgment, and judgment does not delegate. Delegate only errands: `grounding-scout` for a genuinely large grounding sweep, `docs-scout` for an API lookup, `impl-worker` for a self-contained batch build the session scopes. Where subagents are unavailable (Copilot chat, terminal), run the errand inline and say so.

## Invocation

The developer opens with a topic, the systems it touches, and ideally the code (paths, symbols, or an editor selection). Topic or target missing? Ask once and wait; do not guess a scope. A vague opener ("this feels slow") is a valid start: the first minutes narrow it together.

## Setup: ground light, then restate

Grounding is proportionate: minutes, not phases.

- Open the corpus indexes (`docs/adr/adr-index.md`, `docs/design/`, `docs/debt/debt-index.md`) and only a record that clearly governs the target.
- For each named system, read its system-map entry (`system-map`) or design doc; follow dependency edges only as far as the session's blast radius.
- Navigate code by symbol (`rg`, the editor's go-to-definition), not whole-file reads. Finding every reference to a symbol before touching it is the one non-negotiable step: those call sites are the blast radius.

Then restate the scope in two or three sentences (what we are working, what we are not) and confirm. That restatement is the session's contract.

## The session loop

The developer steers which mode is active.

### Whiteboard

- Sketch options out loud: tradeoffs, call chains through existing services, failure modes. Name two or three viable options before recommending one.
- Ground claims in the records and the code, not memory. Quote the governing ADR or business rule when one binds the choice.
- The output is the conversation; author no design documents here. Route what is worth keeping at close.

### Tune

- Tuning moves configured parameters, not constants. Every knob lives as configuration on its owning seam (the tuning-surface convention from `pipeline-stg5-implementation-planning`).
- A hardcoded value you want to move? Lifting it onto its configuration seam is the first edit. Refuse a hardcoded tweak that skips the lift.
- The loop: change the value, validate, repeat. Logic-visible effects validate in the test suite; perceived behavior validates in the running app, with the developer's own judgment as the instrument.
- Final values land in configuration. A tuning outcome worth remembering (why this value, what was wrong at the old one) goes in the system's design doc `## Built log`, with the developer's agreement.

### Edit

- Fixes and small refactors follow the `pipeline-stg6-implementation` pairing discipline without its plan machinery: small steps, narrate intent, pause at decision points, stay green.
- The stack constraints hold at full strength: the pure tier never references a UI-framework assembly; constructor injection against `Contracts` interfaces in the composition root; no service locators; no static mutable state; never hand-edit generated files.
- Pin changed logic with a cheap test where one fits. Skipping a test? Say so and why.
- Run the project's build and test commands (named in Repo Signals, `research.instructions.md`) before calling an edit done.

## The routing gate

Same boundary as `deliver-change`, checked continuously: the session must not quietly become a redesign. Route out, ideally to a fresh session, when the work would:

- introduce a new architectural pattern, cross-cutting concern, or third-party dependency (an ADR first, through `adr-creation`);
- move a layer boundary or a volatility seam, or need new requirements, volatilities, or architecture (`design-autopilot` or the pipeline stages);
- reshape a `Contracts` interface so a consumer can assume something new;
- grow into work worth a behavior-pinning test and a Gate C review (`deliver-change`).

Whiteboarding about architecture is fine and often the session's value; authoring architecture is what routes out. Name the trip, capture where the session got to, and hand off.

## Close

- Summarize what landed (files, values, tests), what was discussed but not built, and what routed out.
- Keep touched records true: fix a small verifiable stale fact on the spot; update a system-map entry through `system-map` only if an edit changed entry points or edges.
- Route captures to their owners: a deferral to `tech-debt`, a refactor spotted but not landed to `refactor-ledger`, a flow worth a picture to `sequence-diagram-creation`, a half-formed idea to `idea-crucible`, a parked design to `future-system`, a small follow-up to `to-do`.
- Suggest one conventional commit subject per coherent change and stop. The developer runs every commit.

## What this skill does not do

- It does not author requirements, volatilities, architecture, ADRs, or implementation plans; the routing gate sends that work to the pipeline.
- It does not replace `deliver-change` for a change that needs a pinning test and Gate C, and it does not relax the stack constraints because the session is informal.
- It does not commit, and it does not guess scope, root causes, or design intent to keep momentum.

## References

- The loops it defers to: `deliver-change` (governed maintenance), `design-autopilot` (new systems).
- The discipline it borrows: `pipeline-stg6-implementation`, `unit-test-creation`, `impact-analysis`.
