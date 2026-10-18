---
name: refactor-ledger
description: >
  Own the refactor ledger (docs/refactor/refactor-ledger.md): capture candidates spotted during
  code work, investigate cheap ones, write the RF-NNN row, advise what to refactor next, prune
  resolved rows. Invoke implicitly when work surfaces a restructuring opportunity outside the
  current change's scope: log it instead of widening the diff. Explicitly on "note this
  refactor", "what should we refactor next", or an RF-NNN reference. Feeds deliver-change's
  refactor track; complements tech-debt.
tags: [process, refactoring, skill]
---

# Refactor Ledger (capture and lifecycle)

A refactor candidate spotted mid-change has two bad exits: it widens the diff of the change that surfaced it, or it evaporates when the session ends. This skill is the third exit: a bounded triage at the moment of sighting, then one concise row a later session acts on. The code-handling skills (`deliver-change`, `pair-programming`, `pipeline-stg6-implementation`) invoke it whenever their work surfaces one.

## The ledger contract

`docs/refactor/refactor-ledger.md` is the single home; resolved rows move to `docs/refactor/refactor-ledger-archive.md`, same columns. The table, one row per line:

```
| ID | Refactor | Solves | Evidence | Disposition | Status |
|----|----------|--------|----------|-------------|--------|
| RF-001 | Extract the shared retry policy | Two HTTP clients diverge on backoff | `OrderClient.cs`, `BillingClient.cs`; 6 call sites | investigated | open |
```

- **ID** `RF-NNN`: stable, never reused across ledger and archive.
- **Refactor**: what moves, merges, splits, or renames, in one line.
- **Solves**: the concrete problem the refactor removes, never "cleanup".
- **Evidence**: the files, symbols, and reference counts that ground it.
- **Disposition** `investigated` or `needs-review`.
- **Status** `open` / `in-flight` / `blocked` / `resolved`. A `blocked` row is parked by developer direction until the condition it names arrives.
- Cells hold no `|`; one line each, plain and concrete, no em dashes.

## The tool

Row mechanics run through `refactor.py` (stdlib Python; `.claude/skills/refactor-ledger/` carries an identical copy). Without Python, edit the table by hand in the format above. Run from the repo root:

```
python .github/skills/refactor-ledger/refactor.py next-id                    # next free RF id (ledger + archive)
python .github/skills/refactor-ledger/refactor.py get RF-008                 # one row in full
python .github/skills/refactor-ledger/refactor.py list [--status open] [--filter Solves=duplication] [--full]
python .github/skills/refactor-ledger/refactor.py add --refactor "..." --solves "..." --evidence "..."
```

- `--status` is a prefix match, so it finds cells carrying trailing prose.
- `list` truncates long cells; `get` prints one row whole; `list --full` prints every column of the filtered set (unfiltered it costs about a full read).
- An unparseable table line warns on stderr rather than being skipped silently.
- `add` creates the ledger with its header when absent. The tool never moves a row; archival stays with the pruning pass.
- Tests: `python -m unittest discover -s .github/skills/refactor-ledger/tests -p "test_*.py"`.

## Capture: the sighting triage

A three-way gate, decided when a candidate surfaces:

1. **In scope and trivial.** The refactor serves the current change and lands green inside its scope: do it now in small green steps. No row; the diff carries it.
2. **Out of scope, investigation quick.** A few targeted lookups (definition, references, outline) settle the shape in minutes: run them, then write the row as `investigated` with the evidence they returned.
3. **Out of scope, investigation heavy.** Settling the shape needs a broad sweep, a behavior contract no test pins, or judgment across several systems: write the row as `needs-review`, naming the question the focused review must answer. Do not run the sweep mid-change.

Route before logging:

- A deferral or shortcut of the current work is debt (`tech-debt`), not a row here. A missing test is `testing` debt.
- A restructure that moves a layer boundary, reshapes a `Contracts` interface, or introduces a new pattern, cross-cutting concern, or dependency is design work wearing a refactor's name. `deliver-change`'s routing gate owns that line: take it to the design pipeline and, where required, an ADR.

## Delegation

Judgment stays with the session: whether a sighting is a candidate, its triage branch, its disposition, and every row's wording. A two-lookup investigation runs inline; never spawn an agent for it. In Claude Code, a genuinely large sweep delegates to `grounding-scout`, which returns compact pointers. Where subagents are unavailable (Copilot chat, terminal), run the sweep inline and say so. The refactor itself lands through `deliver-change` (`refactor` track), never here.

## Consume: early and often

- **Ride-along.** Delivery grounding scans the ledger for `open` rows touching the files or systems the change already visits. A row that fits the change's scope is folded in and flipped `resolved` with evidence; one that does not stays put. Scope discipline outranks paydown.
- **Advisory.** For "what should we refactor next": rank `open` rows by proximity to active work and by what the refactor unblocks, then hand the chosen `RF-NNN` to `deliver-change`'s `refactor` track. A `needs-review` row's next step is its focused read-only review (its own session, or `architecture-conformance` when the question is structural), which rewrites the row as `investigated` or surfaces it to the developer as not worth doing.

## The pruning pass

Run on demand or when resolved rows accumulate:

1. Each `resolved` row: confirm the resolving commit or record is named, then move it to the archive.
2. Each `open` row: confirm the evidence still holds. A row whose anchor symbol is gone gets re-verified or removed with the developer's agreement.
3. Report counts before and after. Never remove an unresolved row silently; dropping a candidate as not worth it is the developer's call.

## Revise the ledger

- Read the ledger first. Preserve the header, the column set, and every row the change does not name.
- For a bulk rewrite, show before and after counts and confirm before saving to the same path.

## Boundaries

- This skill does not perform refactors (`deliver-change` does), track deferred work (`tech-debt` does), or gate a change (`pipeline-stage-review` does).
- Capture never justifies widening a running change's diff, and a candidate never justifies a speculative seam.
- Never commit. Suggest a commit subject (`docs(refactor): ...`) and stop.
