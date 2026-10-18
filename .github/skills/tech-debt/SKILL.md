---
name: tech-debt
description: >
  Own the lifecycle of the technical-debt registry at docs/debt/debt-index.md: capture a TD
  row, triage severity and trigger, advise what to pay down next, prune resolved rows. Invoke
  implicitly when work defers something incomplete: a shortcut, a skipped test, a known gap left
  behind by a change. Explicitly on "log this as debt", "what should I pay down next", "prune
  resolved debt", or a TD-NNN reference. Feeds deliver-change's debt track; complements
  refactor-ledger (optional improvement) and to-do (small reminders).
tags: [process, skill, tech-debt]
---

# Tech Debt (registry lifecycle)

Several skills append debt rows (`pipeline-stg5-implementation-planning`, `pipeline-stg6-implementation`, `pipeline-stage-review`, `deliver-change`). This skill owns what happens after a row lands: id assignment, triage, the pay-down advisory, and the pruning pass. Capture stays cheap for the writers; consistency is enforced here.

## The registry contract

`docs/debt/debt-index.md` is a pointer index. Resolved and accepted rows move to `docs/debt/tech-debt-archive.md`, same columns. The table, one row per line:

```
| ID | Sev | Category | System | Item | Owning record | Trigger / condition | Status |
|----|-----|----------|--------|------|---------------|---------------------|--------|
| TD-001 | Med | testing | OrderManager | No regression test on retry ordering | [plan](../design/orders-design.md) | before the next retry change | open |
```

- **ID** `TD-NNN`: stable, assigned once, never reused across ledger and archive. New debt takes the next free number.
- **Sev** `High` / `Med` / `Low`, by what breaks and when.
- **Category**: reuse the vocabulary already in the table (`testing`, `docs`, `dependency-risk`, `tooling`).
- **System**: the system from `docs/systems/systems-index.md` where the project keeps one (`+Name` for a secondary; `(no node)` when none exists).
- **Item**: one line naming the gap and its blast radius.
- **Owning record**: link to the ADR, design doc, or review that holds the detail. It is the single source of truth. A debt with no owning record gets one first (`adr-creation` for a decision consequence, the design doc's plan for a deferral, the review file for a finding).
- **Trigger / condition**: the checkable condition that pulls the item into active work ("before the first public release", not "someday"); `none` means latent.
- **Status** `open` / `accepted` / `watch` / `resolved`. `accepted` marks a limitation with a named revisit trigger. A limitation with no revisit trigger is `closed (will not address)` and archived. The live ledger holds `open` and `watch` rows only.
- Cells hold no `|`; keep each to one line, plain prose, no em dashes.

Debt is work already built or decided that was left incomplete, deferred, or shortcut. Forward roadmap and open design questions belong to the design docs; do not let either leak in.

## The tool

Row mechanics run through `debt.py` (stdlib Python; `.claude/skills/tech-debt/` carries an identical copy). Without Python, edit the table by hand in the format above. Run from the repo root:

```
python .github/skills/tech-debt/debt.py next-id                          # next free TD id (ledger + archive)
python .github/skills/tech-debt/debt.py get TD-005                       # one row in full
python .github/skills/tech-debt/debt.py list [--status watch] [--filter System=SaveAccess] [--full]
python .github/skills/tech-debt/debt.py verify [--status open] [--id TD-005] [--strict] [--scan-root src]
python .github/skills/tech-debt/debt.py add --sev Med --category testing \
    --system OrderManager --item "..." --record "..." --trigger "..."
```

- `--status` is a prefix match, so it finds cells carrying trailing prose.
- `list` truncates long cells; `get` prints one row whole; `list --full` prints every column of the filtered set (unfiltered it costs about a full read).
- An unparseable table line warns on stderr rather than being skipped silently.
- `verify` is a report-only anchor-existence sweep over non-resolved rows: whether each row's named identifiers and paths still exist, never whether the row still matters. Identifiers are scanned across the repo minus `docs/` unless `--scan-root` narrows it. `--strict` exits 1 when a row has lost every anchor.
- `add` creates the ledger with its header when absent. The tool never moves a row; archival stays with the pruning pass.
- Tests: `python -m unittest discover -s .github/skills/tech-debt/tests -p "test_*.py"`.

## Capture

Logging is the fallback, not the first move.

1. Confirm it is debt by the definition above.
2. Run the pay-now gate: a gap small enough to fix now without widening scope or breaking the build (a missing test, a rename, a doc fix, a local cleanup) gets fixed and logs nothing.
3. A row is earned only when the fix cannot land now: it needs its own design or ADR, a gated event, a developer decision, or more scope than the session holds. State that reason in the row.
4. Ask the roadmap question: was this in scope of the change that logged it? A feature never in scope is roadmap, not debt.
5. For what survives: assign the next `TD-NNN` and write every cell per the contract.

## Triage and advise

For "what should I pay down next":

- Rank `open` and `watch` rows by Severity and trigger proximity. A `watch` row whose gated event is near outranks an older `open` row with `none`.
- A trigger that has already fired is active work, not debt: surface it.
- Hand the chosen `TD-NNN` to `deliver-change` on its `debt` track. This skill never starts the fix.

## The pruning pass

Delivery loops flip Status to `resolved` and defer removal to this pass. Run it on demand or when resolved rows accumulate:

1. Each `resolved` row: confirm the resolving commit or record is named in the Status cell, then move it to the archive.
2. Each `open` and `accepted` row: confirm the owning record exists and the row states the remainder accurately. A half-resolved row is re-scoped, not deleted. `verify` gives the cheap existence floor.
3. Each `watch` row: surface it if its gated event is approaching.
4. Each `accepted` row: archive it with status intact, or `closed` when no revisit trigger exists.
5. Re-check every named trigger; a fired trigger is surfaced as active work.
6. Report counts before and after. Never remove an unresolved row; never delete silently.

## Revise the registry

- Read the ledger first. Preserve the header, the column set, and every row the change does not name.
- For a bulk rewrite, show before and after counts and confirm before saving to the same path.

## Boundaries

- This skill does not fix debt (`deliver-change` does) or own the detail (the owning records do).
- It does not decide a limitation is `accepted`; the developer does. Record the decision, do not make it.
- Never commit. Suggest a commit subject (`docs(debt): ...`) and stop.
