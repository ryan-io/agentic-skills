---
name: session-handoff
description: >
  Write a session-level handoff so the next agentic session resumes at the exact point this one
  stopped: what was done this session, what worked, what did not, gotchas, decisions, in-flight
  work, verification state, and a paste-ready resume prompt. Use on "hand off", "wrap up",
  "end session", "write a handoff", at a boundary (gate passed, increment closed, awaiting the
  human), when context is long or compacted, or before a risky long run. Also covers resuming.
tags: [process, handoff, session, retrospective, skill]
---

# Session handoff

One file per session. It freezes the exact point the session stopped and tells the next session what this one learned, so it starts working instead of re-discovering. The chat is not the record; the files are.

## When

- On request: "hand off", "wrap up", "end session".
- At a boundary inside a session: a gate passed, an increment or build closed, work is waiting on the human. Write or refresh the session file then, even if the session continues; a restart after that point loses nothing.
- The context is long or has been compacted. Before a long or risky run whose worker could be lost.

## Where it lives

- Project attached: `claude/handoffs/<YYYY-MM-DD>-<n>.md` (n counts sessions that day), plus `claude/handoffs/README.md` as the index.
- The index is a queue, not a history. `## Open` lists handoffs no session has picked up yet (normally one row: the latest). When a session picks one up it removes the row and appends one line to `## Consumed` (date consumed, which handoff, one phrase on what it continued). The handoff file itself stays on disk for reference.
- No Project: `docs/process/handoffs/<YYYY-MM-DD>-<n>.md` in the repo, same index.
- Refresh the same session file within a session; never start a second file for the same session.
- Never only in chat. Not in memory (memory holds durable facts about the user, not work state).

## Rules

1. **Read before writing.** The tracker, every design doc's `## Built log` touched this session, worker progress notes, the task list, and `git status` of each repo. Then the session's own trail: tool results, agent reports, the user's answers. Write from these, not from recollection.
2. **Verify now.** Every claim about test or build state comes from re-running the command in this session, quoted verbatim with date and machine. A result not re-run is written as "last seen <date>, not re-run".
3. **Resume point is a coordinate, not a summary.** The step in the plan, the file, the scenario or line, the agent that was running and its brief's location, the result not yet consumed. A new session must be able to start the next tool call from it.
4. **Retrospective is evidence, not opinion.** "What worked" names the technique and the result it produced. "What did not" names the dead end, the cost, and the fix or workaround. Gotchas name the trap, how it showed up, and how to avoid it. Each with a path or a quoted error.
5. **Promote, do not repeat.** A gotcha or technique seen in two sessions moves into the tracker's `## Gotchas` section or into the governing skill, and the handoff links it. Handoffs stay session-specific; cross-session knowledge lives in one place.
6. **Link decisions, do not restate them.** ADRs, design doc sections, tracker lines, by path. Decisions made this session are listed with where they were recorded; a decision recorded nowhere but chat gets recorded first, then linked.
7. **Name what is uncommitted** per repo, with the suggested first commit subject.
8. **Two pages at most.** Headers and bullets. The resume prompt is the first thing on the page.

## Structure

```
# Session handoff: <effort> (<YYYY-MM-DD>, session <n>)

## Resume prompt
One paragraph to paste into the new session: "Continue <effort>. Read <this file>, then <tracker>, then <design doc>. Re-run <verification command>. The next action is <...>."

## Resume point
- Plan step: <doc path> § <step or increment>, item <k>
- Last completed: <file or scenario>, evidence <path or run line>
- Next action: <one concrete tool-level step>
- In flight at stop: <agent, its brief location, progress note path, what is lost if it never reports> or "none"
- Unconsumed results: <report or output not yet acted on> or "none"

## Done this session
- <item> -> <evidence path>
(one bullet per unit of work: a plan written, a gate run and its verdict, a build landed, a review closed, a decision taken)

## Decisions this session
- <decision> -> recorded at <path § section>

## What worked
- <technique or brief shape> -> <result it produced, with evidence>

## What did not
- <dead end or failure> -> <cost> -> <fix or workaround applied>

## Gotchas
- <trap> -> <how it showed up (quoted error or symptom)> -> <avoidance>
(promote any repeat to the tracker's Gotchas or the governing skill, and link it)

## Verification
- <command> -> <verbatim last line> (<date>, <machine>)

## Uncommitted
- <repo>: <summary of untracked/modified> -> suggested subject: <conventional commit>

## Open questions for the human
- <question> -> waiting record: <path>

## Environment
- Links and folders the session depends on; tools and installs (e.g. shell on the machine, lupa.lua51); things that must be re-enabled; known instabilities (restarts, lost agent reports)

## Pointers
- Tracker, design docs, ADRs, governing skills, progress notes. Paths only.
```

## Resume procedure (new session)

1. Read the handoff named in the prompt (or the top `## Open` row of the index when none is named), then its Pointers in order. Do not re-derive the plan from source.
2. Consume it: remove its row from `## Open` and append the `## Consumed` line. Do this before any other work so a second session cannot pick up the same handoff.
3. Re-run the Verification commands; the handoff's lines are claims, the runs are facts.
4. `git status` each repo against Uncommitted; a difference means work happened in between, read it before continuing.
5. Confirm Environment facts (link to the machine, tools present).
6. Act on Resume point > Next action. If In flight names an agent that never reported, treat its scope as not done unless disk proves otherwise.
7. At this session's first boundary, create this session's own handoff file and add it to `## Open`.

## Boundaries

- Writes the handoff and its index row; consumes the row on resume. Does not commit, does not change design records, does not decide open questions.
- A handoff past two pages means the tracker or a design doc is missing content; put it there and link it.
