---
name: doc-reconcile
description: >
  Invoke implicitly when a landed decision, design, or code change is summarized by a synthesis
  doc (an overview, README, architecture summary) that now drifts from it. Explicitly on "update
  the overview", "reconcile this doc", "this doc is dated", "the README is stale". Reconciles the
  synthesis against the confirmed record: classifies each dated delta (superseding, adding,
  resolving, implementation-only) and keeps every claim's dated citation. Unrecorded developer
  direction is captured into the record first. Edits the synthesis, never the sources.
tags: [documentation, process, skill]
---

# Reconcile Synthesis Docs with the Record

A synthesis doc restates confirmed records in one place; it drifts the moment new records land. An architecture overview citing ADRs, a README describing the system's capabilities, a summary of the design docs: each new decision silently invalidates a line. This skill closes that gap. It updates the synthesis, never the sources, and adds no design of its own.

## When it runs

- **Implicitly**, when a decision, design section, or increment lands and a synthesis doc summarizes the area it touched.
- **Explicitly**, on request, or routed from a review that found drift but does not edit.
- **Owned set:** a doc that declares its sources (a Sources or Maintenance section naming the records it restates). A doc without declared sources is not a synthesis doc: ask the developer whether to declare them, or route it to its owning skill.

## Procedure

1. **Fix the window.** Read the target doc. Its `updated:` stamp and newest dated citation set the staleness window; everything after that date is a candidate delta.
2. **Sweep the deltas index-first.** For the window: new or amended rows in `docs/adr/adr-index.md`, `docs/business-rules/` index, `docs/design/` docs, `docs/systems/systems-index.md`, `docs/research/research-index.md`, and `git log --since=<date>` for landed increments. A sweep spanning several corpora can go to the `grounding-scout` agent in Claude Code, which returns dated pointers; where subagents are unavailable (Copilot chat, terminal), run it inline and say so.
3. **Classify each delta.**
   - **Superseding:** replaces an existing claim. Replace the claim and its citation.
   - **Adding:** a claim the doc's scope requires. Insert it with its citation.
   - **Resolving:** closes an open item. Move it out of the open list.
   - **Implementation-only:** no synthesis-level claim. Skip.
   - Unsure whether a delta rises to the doc's altitude? Prefer skip and note it in the report.
4. **Capture before citing.** A confirmed developer statement with no dated record goes into its owning record first (an ADR through `adr-creation`, a design section through its `pipeline-stg*` skill), dated and marked with its source. The synthesis then cites that record. It never cites a conversation, and never states what the developer has not confirmed.
5. **Edit.** Replace superseded claims; do not annotate around them. Open items stay marked open with their source. Every claim keeps a dated citation (`<record path>, YYYY-MM-DD`). Bump `updated:`. Run `concise-documentation` before saving. Keep the doc's own structural rules (length cap, cited claims only). Confirm before overwriting.
6. **Verify.** Every claim in the window has a citation that resolves to an existing record. A contradiction found in a source during the sweep is fixed on the spot when verifiable (through its owner), or reported when not.

## Report

List each delta with its classification, the claim it touched, and its citation. Name skipped deltas and why.

## Delegation

The sweep is `grounding-scout` work; a large batch of already-decided edits can go to `records-worker`. The classify and capture judgment stays with the orchestrator. Where subagents are unavailable, run both inline.

## Boundaries

- Edits synthesis docs only. Never touches sources to make them agree with the synthesis.
- Never invents or expands design.
- `concise-documentation` owns pure style retrofits; `system-map` owns `docs/systems/` nodes.
- `concept-propagation` owns the inverse: a delta that coins a term needing fan-out beyond this doc routes there, and its hits on a synthesis doc route back here.
- It never commits; at most it suggests a commit subject and stops.
