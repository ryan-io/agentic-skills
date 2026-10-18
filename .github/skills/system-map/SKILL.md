---
name: system-map
description: >
  Invoke implicitly at the start of any task that must understand, locate, or change a backend
  system, before opening source. Explicitly on "what systems exist", "where does X live", "what
  depends on X", "add a system to the map", "expand this stub". Resolves through
  docs/systems/systems-index.md, opens only the one node (docs/systems/<slug>.md), then follows
  its depends_on / used_by edges. Maintains the map as systems land; a row with no node link is a
  stub to expand from its governing record.
tags: [code-map, navigation, skill]
---

# System Map

A two-tier map of the project's backend systems, so an agent learns the codebase from structured text instead of scraping source. Tier 0 is the index (`docs/systems/systems-index.md`); tier 1 is one node per system (`docs/systems/<slug>.md`) carrying the detail and the edges.

## When it applies

- **Implicitly**, before backend code work: deciding which files to open, a task naming or implying a system, a change that might ripple through dependents.
- **Explicitly**, when the developer asks what exists, where something lives, what depends on it, or asks to add or expand a system.

Prefer the map over opening source blind; that is the point of it.

## Index first

Read `docs/systems/systems-index.md` first. Match the question to one row, read the synopsis, then open only that node. A typical answer needs one node, sometimes the nodes one edge away. Row format (edit by hand, one row per system):

```markdown
| System | Layer | Status | Node | Synopsis |
|--------|-------|--------|------|----------|
| <name> | <Client / Manager / Engine / ResourceAccess / Utility> | planned / scaffolded / implemented | [<slug>](<slug>.md) or blank | <one line> |
```

## Reading a node

A node's frontmatter is the machine layer; the body holds purpose and notes:

```markdown
---
system: <name>
slug: <kebab-case>
layer: <Client / Manager / Engine / ResourceAccess / Utility>
status: planned | scaffolded | implemented
synopsis: <one line, matches the index row>
depends_on: [<slug>, ...]        # what this needs
used_by: [<slug>, ...]           # who needs this
governing_records: [<ADR or design-doc section>, ...]
research: [<docs/research note>, ...]
project: <assembly or project path once code exists, else "">
entry_points: [<type or file>, ...]
updated: YYYY-MM-DD
---

## Purpose
```

Follow `depends_on` and `used_by` to traverse. The union of edges is the graph.

## Materializing a stub

A row with no node link is a stub. Expand it on demand:

1. Read the system's governing record (`docs/adr/adr-index.md`, `docs/design/{slug}-design.md`) and research evidence (`system-context`).
2. Write `docs/systems/<slug>.md` in the schema above.
3. Set reciprocal edges: if this `depends_on` X, add this to X's `used_by`.
4. Link the node and update Status in the index row.

Boundaries not decided in a record? Ask before writing. Never invent a system no record defines. A touched system with no row at all is a gap: surface it and add the row.

## From design to code

A system seeded from a design doc starts `planned` with `project` and `entry_points` empty. When code lands, fill them in, flip Status to `scaffolded` or `implemented`, and treat the code as the source of truth over the design doc.

## Revise an existing node or the index

- Read the node first; apply only the requested change; preserve all other frontmatter, prose, and the schema.
- Confirm before overwriting; save to the same path.
- Keep edges reciprocal and reconcile the index row. In the index, append or edit one row; never rewrite the table.

## Constraints

- Read the map first; open source only after it points there.
- Do not duplicate research evidence; link the note and let `system-context` carry the external facts.
- The map is derived: the records and source are the truth. A wrong node is fixed from them.
- It never commits; at most it suggests a commit subject and stops.
