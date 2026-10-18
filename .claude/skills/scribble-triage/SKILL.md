---
name: scribble-triage
description: >
  Invoke implicitly when a non-empty scribble.md at the repo root is noticed during a session:
  offer to triage it. Explicit triggers: "process my scribbles", "triage scribble.md", "go through
  my notes". Splits raw notes into items, classifies each against a routing table, confirms the
  routing, dispatches each through the owning skill, and clears only routed lines. A router, not
  an owner.
tags: [process, skill]
---

# Scribble Triage (inbox to owned records)

The inbox is `scribble.md` at the repo root: ideas, reminders, links, and fragments jotted between sessions. Unprocessed, they rot. This skill drains each note into the record that owns it, through the owning skill, and removes only routed lines.

It contains no record-writing logic. Every capture goes through the destination skill, so this file never drifts when those skills change.

## The inbox contract

- The inbox is `scribble.md` at the repo root. Any other notes file the developer names is treated the same way; say so in the report.
- Missing or empty file: report an empty inbox and stop.
- A tracked `scribble.md` means clearing lines is a working-tree change the developer commits.
- One session triages at a time. If another session is mid-triage, do not touch the file.

## The steps

1. **Read.** Read the whole inbox. Expect prose, fragments, pasted content, and mixed topics.
2. **Itemize.** Split into discrete notes. Blank lines and bullets are the usual boundaries; a multi-line block on one topic is one note. Never split a thought mid-idea.
3. **Classify.** Match each note to the routing table. No match, or an ambiguous one, is marked "ask"; never guess a destination.
4. **Confirm.** Present the full routing as one table: the note (verbatim or tightly summarized), the destination skill, the one-line capture it would produce. Get sign-off before dispatching. The developer can reroute, drop, or defer any row.
5. **Dispatch.** Invoke each destination skill with the confirmed capture. Never write a destination corpus directly; the owner assigns ids and index rows.
6. **Clear.** Remove only routed lines. Skipped, deferred, and "ask" notes stay, so a rerun is idempotent. Report: routed (with the ids the owners assigned), left in place, and why.

## Routing table

| The note is | Destination |
|---|---|
| A fuzzy idea to challenge, not just keep | `to-do` row naming an `idea-crucible` run (not run during triage) |
| A small one-line follow-up | `to-do` |
| Deferred or shortcut work on existing code | `tech-debt` |
| A restructuring candidate in existing code | `refactor-ledger` |
| A bug or small change to existing code | `to-do` row naming a `deliver-change` run |
| A new system or feature to design | `to-do` row naming a `design-autopilot` or `architecture-design-pipeline` run |
| A settled-but-unbuilt system design | `future-system` |
| A decision to record | `adr-creation` |
| A domain constraint or invariant | `business-rule-creation` |
| A correction to a doc, verifiable now | Fix on the spot; `doc-reconcile` if it spans a synthesis doc |
| A newly coined cross-cutting term | `to-do` row naming a `concept-propagation` run (not run during triage) |
| An external link or library fact worth keeping | `system-context`, or the record it supports; ask if none exists |
| A system-map gap or stale entry | `system-map` |
| A flow worth diagramming | `sequence-diagram-creation` |
| A test plan or test gap | `test-plan-creation` or `unit-test-creation` |
| A review or audit request | `to-do` row naming `system-review`, `architecture-conformance`, `audit-and-critique`, or `house-keeping` |
| Unrelated to the project (a pasted how-to, machine setup) | Flag to the developer; never route; delete only on their say-so |

## Boundaries

- It routes; it does not act. It never runs the routed work (a crucible session, a build, a fix beyond the on-the-spot doc correction).
- It never writes a destination corpus directly and never deletes an unrouted note.
- A note too big for its destination: the owning skill says so, the note stays, and the report names the finding.
