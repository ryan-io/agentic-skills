---
name: concept-propagation
description: >
  Invoke implicitly the moment the developer coins or confirms a named term (a domain concept, a
  named capability, a cross-cutting phrase) that reaches into more than one doc corpus.
  Explicitly on "we coined X", "propagate this concept", "where else should this live", or "use
  this term everywhere". Registers the term in docs/glossary.md, enumerates candidate records
  with rg over docs/ and the skills trees, classifies each hit (adopt / rephrase / leave), and
  routes edits through the owning skills. Fan-out inverse of doc-reconcile. A router, not an
  owner: it edits no corpus except the glossary.
tags: [concept-propagation, documentation, glossary, skill]
---

# Concept Propagation

A coined term lands in the record where it was born, and the sibling corpora go silently stale: the design doc says the new term while the ADR, the business rule, and the skill prose still speak the old vocabulary. This skill owns the write side: "a new term just landed; which records must absorb it?" Placement beyond the birth record is found mechanically, by search, never by intuition.

## When it runs

- **Implicitly**, the moment a named term with cross-corpus reach is coined or confirmed: in conversation, at an `idea-crucible` close, or when a landing record uses a term the glossary lacks. Surface it ("X reads as a new cross-cutting term; propagate it?") and run once the developer confirms the term is real.
- **Explicitly**, on request, or routed from `doc-reconcile` when a delta fans out wider than one synthesis doc.
- **Scope gate:** a term reaching more than one corpus. A single-corpus fact routes straight to its owning skill; skip the sweep.

## Procedure

1. **Register the term.** Add or update its row in `docs/glossary.md` (create the file if absent) before anything cites it. Row format, kept alphabetical:

   ```markdown
   | Term | Definition | Coined | Source record | Supersedes |
   |------|------------|--------|---------------|------------|
   | <term> | <one sentence> | YYYY-MM-DD | <path to the dated record that defines it> | <old phrasing, or -> |
   ```

   The source record must be a dated file (a design doc, ADR, or `docs/ideas/` note). Propagation never cites a conversation: an unrecorded definition is captured into its owning record first.
2. **Enumerate candidates by search.** The sweep is command output the agent classifies, never a memory exercise. From repo root, search the term, its old phrasing, and close variants:

   ```bash
   rg -n -i "<term>|<old phrasing>" docs/ .github/skills/ .claude/skills/
   rg -l -i "<related concept>" docs/ .github/skills/
   ```

   Group hits into: records already using the term (verify they mean what the glossary now says), records using the old phrasing (strongest candidates), and records on the related concept without either (check whether they should name it). Where `rg` is unavailable, use `grep -rniE`. A large sweep can go to the `grounding-scout` agent in Claude Code, which returns pointers, not file dumps; where subagents are unavailable (Copilot chat, terminal), run it inline and say so.
3. **Classify each hit.** The judgment stays with the orchestrator.
   - **Adopt:** the record's claim is wrong or incomplete without the term; it must take the term and cite the source record.
   - **Rephrase:** the record stands but uses the old phrasing or a near-synonym; align the wording.
   - **Leave:** unaffected, or below the record's altitude. When unsure, prefer leave and note it.
4. **Route edits to owners.** Per the routing table. This skill makes none of the edits beyond the glossary. A batch of already-decided mechanical edits can go to the `records-worker` agent, or run inline where subagents are unavailable.
5. **Verify.** Re-run the step 2 search: every adopt and rephrase hit now carries the term, and the old phrasing survives only where classified leave. Report the hit list with its classification.

## Routing table

| Corpus | The term lands here when | Owner |
|--------|--------------------------|-------|
| `docs/glossary.md` | Always, first. | this skill |
| `docs/ideas/` | The idea is still tentative. | `idea-crucible` |
| `docs/design/{slug}-design.md` | A design section's claim changes. | the owning `pipeline-stg*` skill |
| Overview docs, READMEs, architecture summaries | A synthesis-level claim changes. | `doc-reconcile` |
| `docs/business-rules/` | The term constrains runtime behavior. | `business-rule-creation` |
| `docs/adr/` | The term changes an architectural or process decision. | `adr-creation` |
| `docs/systems/` | A system embodies it. | `system-map` |
| `docs/research/` | External evidence grounds it. | `system-context` |
| `.github/skills/`, `.github/instructions/` | Skill or rule prose should speak the term. | Propose to the developer; instruction files need sign-off (`agent-guardrails`) |
| Follow-up work | The term spawns a task. | `to-do` / `tech-debt` |

## Revise a glossary entry

- Read `docs/glossary.md` first; edit one row, never rewrite the table.
- Preserve every other row and the column order. Confirm before overwriting.
- A changed definition re-runs steps 2 to 5 for the records that cite it.

## Boundaries

- A router, not an owner: every edit beyond the glossary goes through the owning skill.
- It never invents or expands design while propagating. The term means what its source record says, nothing more.
- `doc-reconcile` is the pull inverse (one synthesis doc sweeps many deltas in; this skill fans one delta out). A hit on a synthesis doc routes there.
- Over-propagation is the failure mode. The scope gate and the leave default bound it.
- It never commits; at most it suggests a commit subject and stops.
