---
name: audit-and-critique
description: >
  Run a periodic adversarial audit of the agent meta-system (skills, instruction files, agents,
  hub files) against five fixed goals: token economy, writing voice, plan fidelity, project big
  picture, and spec-and-built consistency. Manual only: "run audit-and-critique", "audit the
  harness", "review the skills and rules", "adversarially review the project against its
  design", "session retrospective". A hand-run baseline checklist, bounded read-only lanes, one
  findings report to docs/reviews/{date}-audit.md. Proposes only, edits nothing. Complements
  architecture-conformance and system-review.
tags: [critique, process, skill]
---

# Audit and Critique (meta-system health)

Structural checks catch broken files. They miss the slow decay: standing token cost, voice backlog, stale hand-written claims, dead machinery, and the gap between scattered records and a clearly stated project. This skill is the recurring counterweight.

## Invocation and cadence

- Manual only. The developer asks by name or asks to audit the skills, rules, agents, or instruction system. No other skill invokes it.
- Sensible cadence: before closing a milestone, after roughly ten delivered increments, or when sessions feel heavy.
- Before launching lanes, state the expected scale (lane count, rough cost). Prefer the leanest run that answers.

## The five fixed goals

Every run judges the same five lenses so results compare across runs.

1. **Token economy.** Standing per-session overhead (hub files, always-on instruction files, the skill menu), per-consult cost of indexes and pipeline skills, prose duplicated across skills.
2. **Writing voice.** Empirical compliance of recent agent-authored prose with `concise-documentation` (em dashes, buzzwords, bottom line up front), and whether any mechanical check enforces it.
3. **Plan fidelity.** Built code matches each design doc's `## Implementation Plan` point by point, deviations are recorded in `## Built log`, and index status vocabulary holds.
4. **Project big picture.** Whether the curated records alone state the project: purpose, users, core workflows, guiding principles, scope boundary. Whether superseded ideas get reconciled and open tensions get resolved.
5. **Spec-and-built consistency.** The built system against the records that specify it: `## Requirements` and `## Architecture` sections, ADRs, business rules, and any synthesis overview doc, in both directions (claims without code, code without claims). Each inconsistency names what diverged, which side is authoritative, and where the fix routes.

## Phase 0: baseline checklist

Run by hand or with `rg`; read-only. Each failure seeds a lane.

- **Mirror parity.** Every file under `.github/skills/` has a byte-identical twin under `.claude/skills/`; every `.github/instructions/*.instructions.md` has a `.claude/rules/` counterpart with the same body. Compare with `diff -r` or file hashes.
- **Frontmatter name equals folder.** `rg -n '^name:' .github/skills/*/SKILL.md` and compare each value to its folder name.
- **Every referenced skill exists.** Collect backticked skill names cited in skills, instruction files, agents, and hub files; each must have a folder under `.github/skills/`.
- **Every referenced agent exists.** Each agent a skill spawns has a `.claude/agents/` and a `.github/agents/*.agent.md` definition.
- **Hub parity.** `CLAUDE.md` and `.github/copilot-instructions.md` agree where the project says they must.
- **Sizes.** Byte totals of the always-on files (hub files, `applyTo: "**"` instruction files) and the largest skills.
- **Voice counts.** Em-dash count across recent docs and skills (`rg -c '\x{2014}'`, U+2014).

## Phase 1: bounded lanes

At most six read-only lanes; three or four when the baseline is mostly green (merge A+D, B+C, E+F).

- **Can spawn subagents (Claude Code):** each lane is one `audit-reader` agent spawn with its charter and scope. Raw file contents stay in the lane.
- **Cannot spawn subagents (Copilot chat, terminal):** run the lanes inline, one at a time, and say so in the report.

Fixed charters:

- **A. Pipeline and fidelity.** Duplicated orchestration, redundant re-grounding, gate coverage, the newest two or three implementation plans diffed against git for silent deviations, status enums.
- **B. Records and knowledge capture.** Idea lifecycle, tension count and age, template drift, dead machinery in scripts.
- **C. Indexing and navigation.** Index cost per row and staleness both ways (rows without files, files without rows), consistency of the navigation guidance across instruction files.
- **D. Instructions and voice.** Always-on footprint, rule/skill duplication, an empirical voice sample of the newest 10 to 15 docs, enforcement gaps.
- **E. Project big picture.** The blunt test: from the curated records alone, write a five-sentence project statement (purpose, users, core workflows, principles, scope) and list every hole. Find standing contradictions between curated docs.
- **F. Spec-and-built consistency.** Verify each specified claim against source and each built behavior against a spec. Name the authoritative side and the owning skill: the design pipeline for spec drift, `tech-debt` for deferred code, the developer for a synthesis doc.

Every lane returns ranked findings: severity (high/med/low), evidence (paths, numbers, quotes), a disposition (keep / tune / refactor / add / remove), and what it verified as healthy. Counter-evidence is mandatory; an audit that only finds faults is not trusted.

## Phase 2: the report

Write `docs/reviews/{date}-audit.md`, under `concise-documentation`, in this order:

1. Prior audit reconciliation (see below).
2. Verdict, bottom line first.
3. What is healthy.
4. Findings by goal.
5. Disposition table over documents and systems.
6. Prioritized roadmap with effort (S/M/L). Flag anything touching `.github/instructions/`, `.claude/rules/`, or the hub files as needing developer approval (`agent-guardrails`).
7. Step back: what is missing, and do the layers still work together.
8. Method and cost: lanes run, inline or spawned.

Deferred findings become rows through `tech-debt`, proposed, not written.

## Revise a prior audit

- Before writing, find the newest prior `docs/reviews/*-audit.md` and read it. Mark each prior roadmap item landed, in-flight, stale, or superseded in the new report's first section.
- Never overwrite an existing report without the developer's confirmation. A same-day rerun appends a suffix (`-2`) rather than clobbering.
- Correcting a factual error in a saved report: read it, change only the error, preserve the rest, confirm, same path.

## Boundaries

- Writes its own report only. Never commits; suggests a commit subject and stops.
- Mechanical layering (naming, dependency direction, purity) belongs to `architecture-conformance`; lane F consumes its latest report rather than redoing it.
- Per-increment review belongs to `pipeline-stage-review`; harness setup correctness to `system-review`.
