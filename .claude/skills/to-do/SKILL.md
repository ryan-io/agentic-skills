---
name: to-do
description: >
  Capture and surface small to-dos: one-line reminders too small for a debt row, a refactor
  row, or a design. Owns docs/todo/todo-ledger.md through todo.py (add, list, done, surface).
  Invoke implicitly on "later", "remind me", "don't let me forget", "we should eventually";
  explicitly on "add a to-do", "what's on the to-do list", "mark TODO-NNN done", or a TODO-NNN
  reference. Surfaces open rows when asked or at the start of a planning conversation.
  Complements tech-debt and refactor-ledger.
tags: [process, skill]
---

# To-Do (capture and lifecycle)

A small follow-up named mid-session evaporates when the session ends unless something holds it. This skill holds it: one line in `docs/todo/todo-ledger.md`, no rationale, no ceremony.

## The ledger contract

The table, one row per line:

```
| ID | To-do | Tags | Added |
|----|-------|------|-------|
| TODO-001 | re-run the load test after the cache change | perf | 2026-10-18 |
```

- **ID** `TODO-NNN`, never recycled; frontmatter `high-water: N` holds the highest id issued.
- **To-do** one imperative line, no `|`. **Tags** optional free text, sorted. **Added** `YYYY-MM-DD`.
- Done rows are removed; git history keeps the account.

## Route before logging

Anything with an owner goes there first: deferred work to `tech-debt`, a refactor candidate to `refactor-ledger`, a parked design to `future-system`, a half-formed idea to `idea-crucible`. A small action nobody else tracks earns a row.

## Commands

Stdlib Python, run from the repo root (`.claude/skills/to-do/` holds an identical copy). Without Python, hand-edit the table and bump `high-water`.

```
python .github/skills/to-do/todo.py add "re-run the load test after the cache change" --tags perf
python .github/skills/to-do/todo.py list [--tag <tag>]
python .github/skills/to-do/todo.py done TODO-001
python .github/skills/to-do/todo.py surface
```

`add` creates the ledger when absent; `done` removes a row once the action lands; `surface` prints open rows compactly, nothing when empty. Tests: `python -m unittest discover -s .github/skills/to-do/tests -p "test_*.py"`.

## Surfacing

- Run `surface` when asked or at the start of a planning conversation.
- When work touches a concern, check `list --tag <concern>` and offer matches. One that fits the session's scope is done and marked `done`; the rest stay.
- A to-do whose action has its own skill (`idea-crucible`, `deliver-change`) runs that skill, then `done`.

## Boundaries

- Records and reminds only: never acts on capture, never widens a running change to drain the ledger, never deletes an open row without the action landing or developer direction.
- Never commit. Suggest a commit subject (`chore(todo): ...`) and stop.
