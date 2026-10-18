---
name: test-plan-creation
description: >
  Generate a dated manual test plan: a checklist a human runs end to end against the running
  app, service, or CLI, one checkbox per action with its expected result. Use on "generate a
  test plan", "write a manual test plan", "QA checklist for this feature / batch / release",
  "how do I verify this by hand", or after an increment with a user-facing surface lands.
  Grounds every check in the design doc's ## Requirements, business rules, ADR invariants, and
  deferred gaps; writes docs/test-plans/{date}-{slug}-test-plan.md and updates
  docs/test-plans/test-plans-index.md. Complements unit-test-creation.
tags: [process, skill, testing]
---

# Test Plan Creation

Produce a manual test plan a human executes top to bottom, checking boxes as they go. A test plan is a checklist, not documentation: every line is performable and falsifiable.

## Scope the plan

- Name what is under test: a design doc's system, a commit batch (a `git log` window since the last plan), a release, or named systems. If the target is ambiguous, ask once.
- Exclude landed work with no observable surface (docs, internal refactors covered by unit tests). Say so in one line, so a tester knows the omission is deliberate.

## Ground first

Gather what defines "passes" before writing any check. Index-first: open the corpus index, then one record; never scrape a directory.

- **Requirements.** Each use case and acceptance criterion in `docs/design/{slug}-design.md` `## Requirements` maps to a check, usually one to one.
- **Business rules.** Every Active rule the increment touches becomes a check citing the rule inline, e.g. `(br-order-total-never-negative)`.
- **ADRs.** An Active ADR invariant the increment touches (persistence format, idempotency, error contract) becomes a check citing the ADR by id, not a generic assertion.
- **Debt.** Known deferred gaps in `docs/debt/debt-index.md` become a stated "known deferred" line so a tester does not re-file them.
- **Prior plans.** Reuse the Common setup from earlier plans in `docs/test-plans/` that already works, instead of re-deriving it.
- **Impact.** The `## Implementation Plan` Impact section (or the systems map's edges) drives the systems-under-test table. Each named side-effect risk gets a cross-system check. At least one check traces to the original requirement, so the plan proves the problem is solved, not merely that new code runs.

## Write the plan

Save to `docs/test-plans/{date}-{slug}-test-plan.md` with frontmatter `title`, `status: active`, `created`, `updated`, and sorted `tags`. The body, in order:

1. One-line intro: what landed, what is out of scope and why.
2. Systems-under-test table: #, system, governing record, entry point (screen, endpoint, or command).
3. Common setup checklist: how to build and start the app or service to a testable state, test data and accounts, configuration, and the diagnostic handles (logs, health endpoints, verbose flags).
4. One section per system: one terse Configuration line (settings with expected values, no prose), a short Setup checklist, then the checks.
5. Cross-system checks last: the highest-value integration behaviors, including one check per side-effect risk from the Impact section.

Checklist discipline:

- Every check is one `- [ ]` line: one action, one observable expected result. Bold the discriminating action or outcome.
- Under each check, an indented numbered sub-list of terse steps (which screen, command, or request; what to enter; what to watch). The check line keeps the expected result. A tester never reverse-engineers the procedure from the check line.
- A check must be performable by a human against the running system. Anything only assertable in code routes to `unit-test-creation`.
- No narrative between checks. Cut any sentence that does not change what the tester does or expects.
- Where the records demand it, include the recurring invariants: state survives a restart, a retried operation does not duplicate its effect, invalid input fails with the documented error, and a clean shutdown leaves no orphaned state.

## Index and status

- Keep `docs/test-plans/test-plans-index.md` true, in the same change. Create it if absent with one table: `| Date | Plan | Scope | Status |`, one row per plan, `Plan` a relative link.
- A plan stays `status: active` until every box is checked. Then flip it to `complete`, bump `updated`, move the file to `docs/test-plans/completed/`, and update the row's path and Status.
- A failed check is a finding, not an editing problem. Route a bug to `deliver-change` (fix track) and a deliberate gap to `tech-debt`. Never soften an expectation so the box can be checked.

## Revise an existing plan

If the plan file already exists, this is a revision. Read it first, apply the requested change, preserve all other content, checked boxes, and the conventions above, confirm before overwriting, and save to the same path unless the developer renames it.

## Boundaries

- Writes the checklist and its index row. Does not run the system and does not write automated tests (`unit-test-creation` does).
- This is the human regression pass over what landed, not in-delivery validation.
- Every plan follows `concise-documentation`. Ask, do not guess: an unverifiable expectation is a question for the developer.
- Never commits; suggests a commit subject and stops.
