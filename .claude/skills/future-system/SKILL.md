---
name: future-system
description: >
  Capture, index, and graduate a system that is designed but not yet built, in the
  future-system registry (docs/future-systems/). Invoke implicitly when a conversation settles a
  system's design (port, layer, data, trade-offs) but the build is deferred: "for later", "not
  now", "eventually", or the developer moves on without scheduling it. Offer the capture; never
  capture silently. Explicitly on "document this as a future-system", "park this design", "save
  this for later". Sits between a raw note and a system-map node; also finds a parked design
  and graduates it into docs/systems/ once built.
tags: [future-system, process, skill]
---

# Future-System

Maintain the registry of designed-but-unbuilt systems in `docs/future-systems/`. A future-system is past a raw note (its design is settled: port, layer, data, trade-offs named) but before a system-map node (no code exists, the build is deferred). Capture the design so it survives the conversation, index it so the next agent finds it, and graduate it into the system map when it is built.

## When this triggers

- **Explicit:** "document this as a future-system", "park this", "save this design for later", "add to the future-systems registry".
- **Implicit:** a settled system design (a named port, a layer, the data it carries, the lifecycle and cost analysis) and a signal that the build is deferred. Offer to capture; confirm first (Ask, Do Not Guess).
- **Route elsewhere when the fit is wrong:**
  - A tentative one-line idea: a raw note, `to-do`, or `idea-crucible` to challenge it.
  - A system about to be built: the design pipeline (`docs/design/{slug}-design.md`, then `pipeline-stg5-implementation-planning`).
  - A system that already has code: a `system-map` node.

The line is "settled design, no code, deferred build."

## Ground first

Index-first; never scrape a directory. Open a full record only when its row bears on the system.

- `docs/future-systems/future-systems-index.md`: already captured?
- `docs/systems/systems-index.md`: already a built system, so not a future-system?
- `docs/adr/adr-index.md` and `docs/business-rules/br-index.md`: governing or related decisions and rules.
- `docs/design/`: a design doc the parked design came from; cite it rather than re-derive it.

Capture the design as reasoned. Never expand it into decisions the developer has not made; name open questions as open.

## Step 1: Capture

1. Choose a slug and create `docs/future-systems/<slug>.md`.
2. Frontmatter:

   ```yaml
   ---
   status: planned            # planned | graduated | dropped
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   layer: Engine              # Client | Manager | Engine | ResourceAccess | Utility | spans
   governing_adr: ""          # ADR slug if one exists
   graduated_to: []           # system-map slug(s) once built
   tags: [future-system, ...] # free-text keywords, lowercase, sorted
   ---
   ```

3. Body, high-level design: the problem it solves; the port and layer; the data it carries; the architectural fit (purity of the business tier, static or lifecycle state, threading, testability); efficiency and lifecycle concerns; open questions. Write it so a future agent can start a design doc or implementation plan from the node alone.

The node holds design, not decisions. A decision the system needs is an ADR (`adr-creation`); the node points to it.

## Step 2: Index

Append a row to `docs/future-systems/future-systems-index.md`. Absent? Create it with a title and this header:

```
| System | Status | Layer | Governing ADR | Summary | Doc | Tags |
|--------|--------|-------|---------------|---------|-----|------|
```

Governing ADR carries its status in parentheses if Proposed. A node missing from the index is invisible to the next agent. The index is hand-maintained; there is no generator.

## Step 3: Retrieve

To find a parked design, scan `future-systems-index.md`. Surface a relevant future-system before designing or planning a system it touches, so the prior design informs the new work instead of being re-derived.

## Step 4: Graduate

When the system is built or scaffolded, graduate it. This is the one controlled path out of the registry:

1. Create the system node through `system-map` (the index row plus the node with `depends_on` / `used_by` edges).
2. Promote the governing ADR from Proposed to Active, or create one (`adr-creation`) if the build introduced a decision.
3. Set the node's `status: graduated` and `graduated_to` to the new system slug. Leave the node in place as the record of the original design.
4. Update the index row's status to `graduated`.

An abandoned design gets `status: dropped` and a one-line reason, so it is not re-derived. Leave the node and its row in place.

## Revise an existing entry

- Read the saved node first. Apply the requested change; preserve all other content and the frontmatter schema.
- Bump `updated` to today. Confirm before overwriting. Save to the same path unless the developer renames it.
- Update the index row to match.

## Boundaries

- The registry holds design: not decisions (ADRs), not raw ideas, not built systems (`system-map`).
- Do not pre-capture a design nobody has settled, and do not invent design to fill a node.
- Never commit. Suggest a commit subject (`docs(future-systems): ...`) and stop.
