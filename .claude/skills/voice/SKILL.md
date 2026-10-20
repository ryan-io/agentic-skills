---
name: voice
description: >
  Swap, inspect, or add the agent's conversational voice (tone register). Use on "/voice",
  "/voice <name>", "switch to the jarvis voice", "be more terse", "tone it down", "teach me as
  you go", "what voices are there", or "add a voice". Lists the library under
  .github/docs/voices/, adopts the chosen register for the rest of the session immediately, and
  persists it by regenerating voice.instructions.md in both rule trees through
  its own set-voice.sh. Never changes the concision standard; formal records stay neutral.
tags: [process, skill, writing]
---

# Voice (swap the register)

The tone an agent speaks in is one generated rule file, `voice.instructions.md`, built from a library file under `.github/docs/voices/`. This skill swaps which library file is active, adopts it now, and keeps the swap for future sessions. Everything else about how the agent writes (the Concise Technical Writing standard, neutral formal records) stays fixed.

## Commands

- **`/voice`** (no argument): print the active voice and the library table (name, summary). Nothing changes.
- **`/voice <name>`**: swap to that voice.
- **`/voice new <name>`**: draft a new library file, confirm, then swap to it.

## Swap

1. Confirm the file exists: `.github/docs/voices/<name>.md`. If not, list the library and stop.
2. Persist: run `sh .github/skills/voice/set-voice.sh <name>` from the repo root. This works in the harness repo and in a consuming project. The sync ships the skill and the library, and never overwrites a consumer's generated rule. It regenerates `.github/instructions/voice.instructions.md` and `.claude/rules/voice.instructions.md` identically. Where no shell is available (Copilot chat in an IDE), say so and copy the file body under the generated header by hand into both paths, matching an existing generated file.
3. Adopt now: read `.github/docs/voices/<name>.md` and speak in that register for the rest of this session. The rule file loads on its own in the next session.
4. Confirm in one line, in the new voice.

## Add a voice

1. Read `.github/docs/voices/README.md` for the file contract and the invariants.
2. Draft `.github/docs/voices/<name>.md` from the developer's description: frontmatter `name` and `summary`, then `# Voice: <Name>`, one-paragraph intent, `## Register`, `## Sounds like` (bad news, disagreement, done), `## Never`. Five bullets or fewer per section. No `---` in the body.
3. Show the draft and confirm before saving. Add its row to the README table, then swap to it.

## Revise a voice

Read the saved file first, apply the requested change, keep the rest and the contract, confirm before overwriting, then re-run `sh .github/skills/voice/set-voice.sh <name>` if it is the active voice.

## Boundaries

- A voice changes tone only. The invariants every voice obeys live in `.github/docs/voices/README.md`.
- `voice.instructions.md` is generated. This skill and `.github/skills/voice/set-voice.sh` are the only sanctioned writers; hand edits go to the library file (`agent-guardrails`, Instruction File Integrity).
- Never commit. Suggest `chore(voice): set active voice to <name>` and stop.
