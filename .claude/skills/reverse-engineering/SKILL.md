---
name: reverse-engineering
description: >
  Recover the design of code or a system you did not write: a third-party addon, a decompiled
  assembly, a service with no source. Invoke implicitly when work must understand a foreign
  codebase or black box before building on, porting, auditing, or interoperating with it.
  Explicitly on "reverse engineer X", "how does this addon work", "recover the design of",
  "figure out what this does", "map this dependency's internals". Classifies the target by what
  is in hand (source, compiled artifact, running black box), opens the matching guide under
  .github/docs/, runs one hypothesis-driven loop (first contact, inventory, static pass, dynamic
  pass, model), and writes a dated dossier to docs/reverse-engineering/{slug}.md with its index
  row. Findings are evidence labeled known, inferred, or assumed; adopted facts flow on to
  system-context, system-map, and ADRs.
tags: [analysis, research, skill]
---

# Reverse Engineering

Recover what a target does and how, from whatever is in hand, into a dossier other work can cite. One method, three guides. The method is this file; the depth per input kind lives in `.github/docs/`:

| In hand | Guide | Typical target |
|---|---|---|
| Readable source | `reverse-engineering-source-guide.md` | a WoW addon, a vendored library, a legacy module |
| Compiled artifact | `reverse-engineering-artifact-guide.md` | a .NET assembly, Lua bytecode, a native binary |
| Running black box | `reverse-engineering-blackbox-guide.md` | a service, a device, a protocol with no code |

An artifact becomes source once decompiled, and a black box becomes an artifact once its binary is obtained. Guides hand off forward; the loop below runs once over the whole job.

## Method basis

- **Vocabulary and the abstraction ladder** from Chikofsky and Cross (IEEE Software, 1990): reverse engineering produces representations at a higher level of abstraction; design recovery adds domain knowledge and deduction; redocumentation only re-renders what exists. The dossier is a design-recovery artifact.
- **The loop's phases** from Demeyer, Ducasse, and Nierstrasz, Object-Oriented Reengineering Patterns (2003, CC BY-SA at https://scg.unibe.ch/oorp/): First Contact, Initial Understanding, Detailed Model Capture. Their patterns name the steps below.
- **Seams and characterization tests** from Feathers, Working Effectively with Legacy Code (2004): pin observed behavior with a test before trusting a reading of it.
- **Artifact and protocol technique** from Eilam (Reversing, 2005), Dang et al. (Practical Reverse Engineering, 2014), Eagle and Nance (The Ghidra Book, 2020), and Forshaw (Attacking Network Protocols, 2018), summarized in the artifact and black-box guides.

## When to use

- Work depends on a codebase or system the repo does not document: a dependency's internals, a host's addon model, a service to interoperate with.
- The developer asks how a foreign thing works, or wants it ported, audited, or extended.
- Skip it when `docs/research/` or `docs/systems/` already answers; those are checked first (`navigation`).

## Procedure

1. **Scope and permission.** Write down the target (name, version, commit, or build), the question the dossier must answer, and what is out of scope. Confirm the license and the host's terms allow the study and the intended use. Classify the input kind and name the guide you are opening. Stop and ask when the question is vague; a dossier without a question becomes a transcript of the code.
2. **Index first.** Open `docs/reverse-engineering/re-index.md` when it exists. An existing dossier is revised (step 9), never duplicated. Check `docs/research/research-index.md` and `docs/systems/systems-index.md` for facts already recorded.
3. **First contact** (OORP: Read All the Code in One Hour, Skim the Documentation, Interview During Demo). Time-box one pass over the manifest, entry points, directory shape, docs, and changelog. Run the thing once if it runs. Write the Inventory section: entry points, dependencies, size, build or load mechanism. Breadth, not depth; no file is read in full here.
4. **Hypothesis ledger.** Turn the question into claims, each with a status: assumed (not yet checked), inferred (consistent with evidence, not confirmed), known (confirmed by evidence named in the row), refuted. Every later step moves rows, never prose alone. Label per `research.instructions.md`.
5. **Static pass** (OORP: Speculate about Design, Analyze the Persistent Data, Study the Exceptional Entities). Follow each entry point inward with symbol search, not full reads (`navigation`). Persistent data (saved state, config, schema) is read first; it is the most stable part and names the domain. Oversized or oddly shaped units get a look; they usually hold the interesting logic. Delegate a large sweep to a sonnet-bound explorer and keep the hypothesis judgment in the session.
6. **Dynamic pass** (OORP: Step Through the Execution; Feathers: characterization tests). Instrument, trace, or test the running target to confirm the inferred rows. A characterization test pins what the target does today, correct or not. A row no experiment can move stays inferred and says why.
7. **Model** (OORP: Detailed Model Capture, Look for the Contracts). Name the components by responsibility, draw the dependency edges, and diagram the core flows with `sequence-diagram-creation`. Use the harness layer vocabulary (Client, Manager, Engine, ResourceAccess, Utilities) where it fits the target; force nothing. The model is the highest rung the evidence supports, and lower rungs stay in the ledger.
8. **Record.** Write `docs/reverse-engineering/{slug}.md` (format below) and its index row. Route what belongs elsewhere: a host or library fact with a shelf life goes to `docs/research/` through `system-context`; a component the project adopts becomes a `system-map` node; a pattern the project adopts from the target gets an ADR (`adr-creation`). Run `impact-analysis` before closing.
9. **Revise an existing dossier.** Read it first. Apply the requested change, keep every other section and its hypothesis rows, bump `verified`, confirm before overwriting, and save to the same path unless the developer renames it. Fix the index row in the same change.

## Dossier format

```markdown
---
title: <target and version>
kind: source | artifact | blackbox
question: <what this dossier answers>
verified: YYYY-MM-DD
license: <license or terms, with URL>
tags: [<sorted>]
---

## Summary          (three lines: what it is, how it works, what we rely on)
## Scope            (target, question, out of scope)
## Inventory        (entry points, manifest, dependencies, size)
## Model            (components, responsibilities, edges; one Mermaid diagram)
## Flows            (sequence diagrams for the core use cases)
## Hypotheses       (ledger: H-n | claim | status | evidence)
## Open questions
## Sources          (file:line, command, URL; date accessed)
```

Index row in `docs/reverse-engineering/re-index.md` (one table, edit by hand):

```markdown
| Dossier | Target | Kind | Verified | Synopsis |
|---------|--------|------|----------|----------|
| [<slug>](<slug>.md) | <name and version> | source / artifact / blackbox | YYYY-MM-DD | <one line> |
```

## Guardrails

- Respect the target's license and the host's terms of use. Studying code to interoperate, extend, port, or audit it is the job; circumventing a protection, a license check, or an anti-tamper measure is not, and the skill stops there and says so.
- Secrets found in a target (keys, tokens, credentials) are reported as a finding, never copied into the dossier or elsewhere.
- Evidence labels are not optional. A claim with no evidence column is assumed, however plausible.
- A dossier describes the target as it is; it decides nothing. Decisions go to ADRs and design docs.
- Never commit. Suggest one conventional commit subject (for example `docs(re): add dossier for <target>`) and stop.

## Done

- The question is stated and the Summary answers it in three lines.
- Every hypothesis row carries a status and, for inferred and known, its evidence.
- The Model and Flows match the ledger; nothing in the diagram outranks its evidence.
- Facts with a shelf life are in `docs/research/`, adopted components in `docs/systems/`, and the index row matches the dossier.
