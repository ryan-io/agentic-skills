---
name: discover
description: >
  Print a one-screen catalog of everything the agentic-skills harness can do: front doors,
  pipeline stages, skills by purpose, agents, rules, stack profiles, voices, and the ground rules.
  Use on "/discover", "what can you do", "what skills are there", "how do I start", "list the
  harness", or at the start of a session in an unfamiliar project. "/discover <name>" prints one
  skill's full trigger description. Self-checks the catalog against disk and flags anything unlisted.
tags: [index, navigation, skill]
---

# Discover (one-screen catalog)

Print the catalog below verbatim, then run the freshness check and append its findings. No preamble, no commentary; the catalog is the whole answer.

## `/discover <name>`

Print that one entry's full `description` from `.github/skills/<name>/SKILL.md` (or `.github/agents/<name>.agent.md`), unchanged, plus the line "Invoke: `/<name>` or describe the situation." Unknown name: list the nearest three names and stop.

## Catalog

```
agentic-skills: what this harness does

FRONT DOORS (name one before touching code)
  design-autopilot              design a new system end to end on its own; `post-impl` builds it too
  architecture-design-pipeline  the same design flow, interactive, stage by stage to Gate A
  deliver-change                fix / refactor / debt TD-NNN on existing code, with Gate C
  pair-programming              ungoverned live session; routes to a door above when it grows

DESIGN PIPELINE (one doc: docs/design/{slug}-design.md)
  pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture ->
  pipeline-stg4-validation -> pipeline-stg5-implementation-planning -> pipeline-stg6-implementation
  pipeline-stage-review         Gate A (design), B (plan), C (built code); findings verified before acted on
  pipeline-final-validation     whole-picture check after Gate C: requirements to tested code
  design-patterns               which classic pattern fits, per stage
  sequence-diagram-creation     Mermaid flow inline in the design doc
  impact-analysis               blast radius and problem fit before any artifact closes

RECORDS (fire on their own when the situation appears)
  adr-creation                  a pattern, concern, or dependency lands -> docs/adr/
  business-rule-creation        a domain constraint is stated -> docs/business-rules/
  concept-propagation           a term is coined -> docs/glossary.md, then every record that should carry it
  doc-reconcile                 a decision lands that an overview or README summarizes
  future-system                 a design is settled but the build is deferred -> docs/future-systems/

LEDGERS (one row each, stdlib Python scripts)
  tech-debt TD-NNN              something deferred incomplete
  refactor-ledger RF-NNN        a restructuring out of scope
  to-do TODO-NNN                "later", "remind me"
  scribble-triage               routes each line of a root scribble.md to its owner

KNOWLEDGE
  system-context                dated primary-source note when work leans on a library or external fact
  system-map                    docs/systems/ index and one node per backend system
  reverse-engineering           recover the design of code you did not write into a dated dossier
  idea-crucible                 steelman, widen, then challenge a half-formed idea; pursue / park / drop

QUALITY AND AUDITS (on request)
  unit-test-creation            tests for existing code, one unit at a time
  test-plan-creation            dated manual checklist a human runs end to end
  lua-best-practices            Lua standards, review, and toolchain setup
  architecture-conformance      has the code drifted from the layering it claims
  audit-and-critique            adversarial audit of the harness itself
  system-review                 setup health plus the engineering big picture
  house-keeping                 indexes vs disk, dead links, stale docs

WRITING AND SESSION
  concise-documentation         tighten a doc without losing a fact
  voice                         /voice <name> swaps the tone: jarvis (default), neutral, terse, mentor
  session-handoff               resume-ready handoff at a boundary
  discover                      this catalog; /discover <name> for one entry

AGENTS (spawned with a fresh context; the seat keeps judgment)
  impl-worker (builds a gated plan)  records-worker (decided record edits)  grounding-scout  docs-scout
  concise-editor  audit-reader  gate-a/b/c-reviewer  design-review-verifier  plan-review-verifier
  pipeline-validator

RULES
  always on:   agent-guardrails, code-standards, design-principles, navigation, pattern-fidelity,
               research, voice
  path-scoped: testing, pr-review, csharp-code-standards, xml-documentation, lua-code-standards,
               adr-template, adr-pr-review, br-review
  stack profile: csharp | lua | generic, named in research.instructions.md Repo Signals

GROUND RULES
  ask, do not guess   options before answers   ADRs bind   never commits   edit .github/, mirror to .claude/
```

## Freshness check

After printing, compare the catalog against disk from the harness root (the folder holding `CLAUDE.md` and `.github/skills/`; in a consuming project, the synced copies):

1. `ls .github/skills` vs the skill names above.
2. `ls .github/agents` (strip `.agent.md`) vs the AGENTS line.
3. `ls .github/instructions` (strip `.instructions.md`) vs the RULES lines.
4. `ls .github/docs/voices` (strip `.md`, skip README) vs the voices on the `voice` line.

Anything on disk and not in the catalog goes under one closing line, `Unlisted (add to discover): ...`. Anything in the catalog and not on disk goes under `Stale (remove from discover): ...`. Print nothing when both are empty. Fix the catalog in the same session only if the developer asks; the catalog is hand-curated so each line stays under about 110 characters.

## Boundaries

- Read-only. Edits the catalog only on request, then runs `sh hooks/mirror-trees.sh`.
- Never commit. Suggest `docs(discover): refresh catalog` and stop.
