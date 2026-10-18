---
name: idea-crucible
description: >
  Invoke implicitly when the developer floats a half-formed idea, asks "what if", or weighs a
  feature, product change, or approach that is not yet a decision. Explicitly on "I have an
  idea", "let's brainstorm X", "let's whiteboard this", "round-table this", "poke holes in this",
  "talk me out of this". Facilitates a round-table: whiteboards unknowns, widens the idea
  (SCAMPER, brainwriting, analogues from real systems and products), then challenges it
  (pre-mortem, dialectical inquiry, feedback-loop check) on cited evidence. Saves a dated note to
  docs/ideas/{date}-{slug}.md with a pursue / park / drop verdict.
tags: [brainstorming, critique, ideas, skill]
---

# Idea Crucible

A facilitated round-table that takes a raw or fuzzy idea, maps the space around it, makes it stronger, then puts it under pressure. The whiteboard fills before the arguing starts. The point is not to agree: every idea is challenged on evidence and real-world analogues, its unknowns surfaced, and the session saved as a note so it survives.

A major goal is emergence: options and cross-system interactions no single lens would propose alone. A session that only validates the idea it walked in with has underdelivered. When a crossover appears (two existing capabilities combining into something neither offers), name it on the board.

## When it applies

- The developer brings an idea to explore, build on, or stress-test: a feature, a workflow change, an architecture direction, a scope change, a UX tweak, or an open question not yet an idea.
- Cues: "I have an idea", "let's brainstorm", "let's whiteboard", "round-table this", "help me think through X", "what if", "talk me out of this", "poke holes in this".
- Not for plain capture or retrieval ("note this", "where did we write down X"). The difference is the work done on the idea: this skill grows it and argues with it.

## Posture

Get this wrong and the session is either a yes-machine or a troll.

- **Set the dial by maturity.** Three energies: discovery (map the space), brainstorm (build on it as a participant), crucible (challenge on evidence). A fuzzy idea earns a long whiteboard and a short crucible; a near-decision earns the reverse. Never end at zero challenge; never open with it.
- **Steelman first.** Restate the idea at its strongest and name the outcome it chases before critiquing. Attack the strongest version, not a weak paraphrase.
- **Every challenge carries evidence.** A real system or product, a research finding, a named framework, or a concrete failure mode. Ungroundable? Say so and downgrade it to an open question.
- **Offer, do not only attack.** Pair each challenge with a direction: an analogue, a reframing, a knob to turn.
- **Pace it like a room.** One thread per message: one question, one offer, or one small batch of variants, then wait. Never deliver a framework's whole output at once. When the developer thinks out loud, mirror it back and ask the next question.
- **Participate.** Contribute variants of your own, marked as yours; "yes, and" before "yes, but". A contribution is an offer, never a decision.
- **Surface, do not decide.** Ask, do not guess (`agent-guardrails`). Do not resolve open questions or confirm design.

## Session shape

A crucible run deserves its own session, with context spent on the idea rather than a delivery run's residue. An idea sparking mid-task? Note the one-liner and offer a dedicated session. Depth is the deliverable: be expansive in-session and tighten only the saved note. Large retrieval sweeps in step 1 can go to the `grounding-scout` agent in Claude Code; where subagents are unavailable (Copilot chat, terminal), run them inline and say so. The conversation itself is never delegated.

## The table

A small recurring team, voiced by the agent and marked as offers (O#):

- **Product designer:** flows, incentives, emergence.
- **User advocate:** the experience, the person it serves or burdens.
- **Producer:** scope, cost, fit with the project's stated goal.
- **Technical seat:** what the current architecture makes cheap or dear.

Voice at most two seats per turn, only when a lens sees something. Seats disagree when lenses diverge; surfacing that is the point. The developer holds the deciding seat.

## Referenceable output

Give each item a short stable ID at first appearance: K# knowns, A# assumptions, U# open questions, O# agent offers, D# developer calls, P# prototype candidates, T# tensions. Never renumber within a session; later turns cite the ID. Number section headings (§1, §2) when a message carries more than two. Carry the IDs into the saved note.

## The session loop

Loose, not a script. Weight steps by maturity. Never skip the steelman or end without a challenge.

1. **Catch the idea and surface prior thinking.** Retrieve before reacting, index-first: `docs/ideas/` (prior notes), `docs/adr/adr-index.md`, `docs/research/research-index.md` (`system-context`), `docs/systems/systems-index.md` (`system-map`), and `docs/design/`. Ground the challenge in what the project already decided.
2. **Whiteboard the space.** For a fuzzy idea, discover before generating: knowns, assumptions, unknowns, and the question behind the question. Question-storm it (who/what/where/when/why/how) before answers. Reframe the itch as "how might we" statements. Let the developer add before you move.
3. **Steelman it.** Restate it at its strongest. Reason from the target outcome backward: does the proposed mechanism produce it? Confirm before you push.
4. **Widen before you narrow.** Generate, do not judge:
   - SCAMPER: substitute, combine, adapt, modify, put to another use, eliminate, reverse.
   - Brainwriting: three to five divergent variants fast, including one you expect to be wrong.
   - Role-storming: a variant from another stakeholder's seat (the new user, the power user, the operator, the integrator).
   - Analogues: real systems and products that did this, the loved executions and the hated ones.
5. **Put it in the crucible.** At least one structured critique, more if load-bearing:
   - Pre-mortem: a year on, this shipped and failed. Why? Causes, then mitigations.
   - Dialectical inquiry or devil's advocacy: argue the opposing design in good faith; surface the hidden assumption. Re-converge afterward.
   - Feedback-loop check: if it touches usage, cost, load, or incentives, trace the positive and negative loops. Does it run away, stall, or trivialize a resource?
   - User-fit: who is it for, who does it burden or alienate?
   - Domain lenses: any lens framework the project names (a UX heuristic set, a threat model, an operability checklist), two or three as question sets.
6. **Ground the analogues.** Local corpus first, live-cited second, knowledge last. A claim that users loved or hated something cites a postmortem, a conference talk, a changelog, an incident report, or documented reception. Prefer primary sources and date anything that can change. Thin search or low stakes? Fall back to knowledge and say so. Cite in passing; full links go in the note.
7. **Converge and name the unknowns.** Do not force a decision. Note what looks promising, what is unresolved, and what would settle it: a prototype, a measured number, a user test. A light New / Useful / Feasible read sorts the pile. Offer a verdict for the developer's call: pursue, park, or drop.
8. **Save the note.** Write `docs/ideas/{YYYY-MM-DD}-{slug}.md` (format below). Confirm before saving.
9. **Record hard conflicts as tensions.** A challenge exposing a genuine collision with an Active ADR or confirmed design is a tension, not a critique. Add an `open tension` line to the note's frontmatter, both sides stated fairly, no winner picked. A critique improves the idea; a tension needs a developer call.
10. **Propagate a coined term.** A session that coins a named concept reaching beyond this note routes it through `concept-propagation`.

## Note format

```markdown
---
title: <idea name>
date: YYYY-MM-DD
status: raw
verdict: pursue | park | drop | undecided
tags: [<sorted>]
open tension: <side A> vs <side B> (<governing record>)   # one line per tension; omit if none
---

## Steelman
## Widenings        (variants and analogues, each analogue with source and date)
## Critiques        (technique, finding, mitigation)
## Open questions   (U# items and what would settle each)
## Verdict          (the developer's call and its reason, or "undecided")
```

Status stays `raw` until the developer confirms direction. A verdict is the developer's, never the agent's.

## Revise an existing note

- Read the saved note first; work from its contents, not memory.
- Apply the change (a follow-up session, a new critique, a changed verdict). Preserve the rest and the existing IDs; append new IDs.
- Confirm before overwriting; save to the same path unless the developer renames it.

## Techniques toolbox

- **Discovery:** starbursting, How-Might-We reframing, affinity mapping (cluster a messy dump into themes), knowns/assumptions/unknowns board.
- **Generative:** SCAMPER, 6-3-5 brainwriting adapted for solo-plus-agent, nominal-group (generate, then sort), analogue mining, role-storming, "yes, and" passes.
- **Critical:** pre-mortem, dialectical inquiry and devil's advocacy, steelman, five whys (root cause behind a request), inversion (design the worst version, then flip it).
- **Systems:** feedback loops (growth, friction, escalation, stability), plus domain lens frameworks the project names.

The toolbox grows. Keep additions grounded: a named technique, a source, a clear "use it when".

## Boundaries

- It does not confirm design or build. A pursue verdict routes forward into `pipeline-stg1-requirements` (or `design-autopilot` for design-and-build), which finds the note under `docs/ideas/`.
- It does not resolve open questions or invent requirements.
- It never commits; at most it suggests a commit subject and stops.

## References

Verified 2026-06-13 unless dated otherwise or marked knowledge-sourced.

- Pre-mortem: Gary Klein, "Performing a Project Premortem," HBR, 2007 (https://hbr.org/2007/09/performing-a-project-premortem).
- Dialectical inquiry and devil's advocacy: Schweiger, Sandberg, Ragan, Academy of Management Journal (https://journals.aom.org/doi/10.5465/255859); Schwenk meta-analysis (https://www.sciencedirect.com/science/article/abs/pii/074959789090051A).
- Steelmanning and the principle of charity: https://forum.effectivealtruism.org/posts/K85qGvjqnJbznNgiY/strawmen-steelmen-and-mithrilmen-getting-the-principle-of.
- 6-3-5 brainwriting (Rohrbach, 1968): https://en.wikipedia.org/wiki/6-3-5_Brainwriting.
- Starbursting: https://en.wikipedia.org/wiki/Starbursting (2026-07-16).
- How-Might-We: IDEO Design Kit, https://www.designkit.org/methods/how-might-we (2026-07-16).
- Affinity diagram / KJ method: https://en.wikipedia.org/wiki/Affinity_diagram (2026-07-16).
- "Yes, and": Keith Johnstone, *Impro*, 1979; https://en.wikipedia.org/wiki/Yes,_and... (2026-07-16).
- Feedback loops: Donella Meadows, *Thinking in Systems*, 2008 (knowledge-sourced).
- Role-storming: Rick Griggs, 1980s (knowledge-sourced, no stable primary link).
