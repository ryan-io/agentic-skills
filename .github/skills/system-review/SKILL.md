---
name: system-review
description: >
  Principal-staff review of the whole project: harness setup health (file existence,
  cross-references, frontmatter, mirror parity, size limits) plus the bigger picture (tech-debt
  pertinence, system cohesion and infrastructure reuse, dependency integration quality,
  per-system overview docs, trajectory and risk). Use when asked to "review the system", "audit
  the setup", "check for gaps", "is the harness healthy", or for a big-picture engineering
  review of the project. Reports findings; changes nothing but its own report.
tags: [critique, process, skill]
---

# System Review

Review the project the way a principal staff engineer would. Part A verifies the agent machinery is correct. Part B steps back and judges whether the systems, their seams, their debt, and their documentation still form a coherent whole. Prose follows `concise-documentation`.

## Orchestrator pattern

The session plans the lanes, synthesizes findings, and renders every verdict. Raw file contents stay inside lanes so only findings enter the synthesizing context.

- **Can spawn subagents (Claude Code):** each lane is one `audit-reader` spawn (read-only) with a named scope, the lane's question, and a findings-with-`file:line`-evidence return.
- **Cannot spawn subagents (Copilot chat, terminal):** run the lanes inline, one at a time, and say so in the report.
- **Budget.** At most three lanes concurrently, eight per run. Announce the planned lane count first. When Part A is green, merge or skip overlapping Part B lanes. A narrow request ("just check mirror parity") gets zero lanes.

## Part A: setup audit

Run the project's validation scripts first, where any exist. A script FAIL is a finding, never re-derived by hand. Spend the manual pass on what no script checks.

1. **File existence.** Every skill, agent, instruction file, and template the hub files (`CLAUDE.md`, `.github/copilot-instructions.md`) and `README.md` name exists on disk.
2. **Environment compatibility.**
   - `.github/instructions/*.instructions.md` carry `applyTo:`; path-scoped ones also carry `paths:` for Claude Code.
   - `.github/copilot-instructions.md` has no frontmatter (always-on hub).
   - `CLAUDE.md` has no `@` imports; rules load via `.claude/rules/`.
   - Skills: frontmatter `name` equals the folder name; `description` present.
   - Agents: every role a skill spawns has both `.claude/agents/<name>.md` and `.github/agents/<name>.agent.md`.
3. **Mirror parity.** `.claude/rules/` mirrors `.github/instructions/` (same body, same glob) and `.claude/skills/` mirrors `.github/skills/` byte for byte. Every source file has its copy; no orphan copies. Compare with `diff -r` or file hashes.
4. **Size limits.** Instruction files stay within the project's cap (default 4,000 characters). Skills and READMEs are exempt.
5. **Content consistency** (manual; no script judges meaning).
   - Stack-agnostic files carry no stack-specific references.
   - Stack-specific files name the general file they extend.
   - Every cross-reference resolves to a real file; templates carry no leftover placeholders.
   - Skill steps, docstrings, and READMEs describe what the code does today. Stale guidance is a finding even when every check passes.
6. **Hub accuracy.** Both hub files list every current skill and instruction file, with no stale references to renamed or deleted files. Where the project requires them identical, a divergence is a FAIL; fix the source and re-sync, never edit the copy.

## Part B: big-picture lanes

Every lane grounds index-first (`docs/systems/`, `docs/debt/debt-index.md`, `docs/adr/adr-index.md`, then one record), reports counter-evidence (what it verified healthy) alongside findings, and judges against the project's named standards, not generic best practice.

### Lane 1: tech-debt pertinence

Classify every `open`, `watch`, and `accepted` row in `docs/debt/debt-index.md`:

- **Still pertinent:** the gap is real and the trigger still makes sense.
- **Resolved in code:** name the evidence (commit, symbol, test).
- **No longer debt:** the context is gone (feature cut, decision superseded).

Also flag rows whose trigger has silently fired. Propose dispositions only; row edits run through `tech-debt`.

### Lane 2: cohesion and infrastructure reuse

Do systems consume shared Utilities (logging, messaging, DI hosting) and the `Contracts` interfaces, or quietly reinvent them? Findings: duplicated helpers solving one problem in two systems, parallel idioms for one concern (two error-handling styles, two config-access patterns), infrastructure that exists but is bypassed, a reusable piece trapped inside one system.

### Lane 3: dependency integration

Walk each system's dependencies in `docs/systems/` and judge each integration, not just its direction. Good: a constructor-injected interface with a narrow surface. Findings: a side channel, a wide interface, a layer skip, or duplicated knowledge of a dependency's internals.

### Lane 4: per-system overview docs

Every code-bearing project or system folder carries a `README.md` that:

- states what the system does, its layer, and its key seams in a few short paragraphs, no implementation detail;
- holds a shallow Mermaid ERD: entities and relationships, no attributes;
- gives an engineer new to the system a working mental model in a few minutes.

Missing, stale, or bloated READMEs are findings. Writing one is follow-up work for the developer, never an inline lane edit.

### Lane 5: trajectory and risk

Does work in flight serve the project's stated goal, where one is recorded, or has scope drifted? Are `watch` risks aging safely? Do new systems land with tests; are tests skipped or quarantined? Does the systems map still match the code (a built system with no row, a row whose system was absorbed)? Findings are directional: name the drift and its cost, not a fix.

## Synthesis and output

- Mark each check **PASS**, **FAIL** (what and where), or **WARN** (not broken, worth attention).
- Open with a verdict, bottom line first. Then Part A in checklist order, then Part B by lane, most severe first, each with evidence and counter-evidence. End with counts: passes, fails, warnings.
- A session-sized review answers inline. When the developer asks for the record, or the run is large, save `docs/reviews/{date}-system-review.md`.
- Debt dispositions route through `tech-debt`; doc and code gaps become scoped work, not silent edits.

## Revise a saved review

Reruns write a new dated report. Correcting a saved one: read it first, change only what was asked, preserve the rest, confirm before overwriting, same path.

## Boundaries

- Changes nothing but its own report. Never commits; suggests a commit subject and stops.
- `architecture-conformance` owns the mechanical layering audit (naming, dependency direction, purity); this skill judges seam quality above that floor.
- `audit-and-critique` owns meta-system health (token economy, voice, plan fidelity); this skill owns setup correctness and the engineering big picture.
- `pipeline-stage-review` judges one increment; this skill judges the accumulated whole.
