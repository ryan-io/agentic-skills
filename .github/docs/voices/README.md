# Voice library

One file per conversational register. The active one is generated into `voice.instructions.md` in both rule trees by `.github/skills/voice/set-voice.sh`; the `voice` skill does the same from inside a session (`/voice <name>`).

| Voice | Summary |
|---|---|
| `jarvis` (default) | Short, dry status lines. The number that matters, the next move, wit in the margins. |
| `neutral` | Plain professional register. No persona, no wit, the facts in order. |
| `terse` | Minimum words. Fragments allowed. Status, cause, next. |
| `mentor` | Patient senior engineer. Explains the why, names the tradeoff, teaches while working. |

## File contract

- Frontmatter: `name` (equals the filename slug) and a one-line `summary`.
- Body: `# Voice: <Name>`, one-paragraph intent, then `## Register`, `## Sounds like`, `## Never`. Keep each to five bullets or fewer.
- No `---` lines in the body; the generator reads the frontmatter by them.

## Invariants no voice may override

The generator writes these into every `voice.instructions.md` header, so a voice file never has to repeat them:

- The Concise Technical Writing rules in the entry points still bind. A voice changes tone, never the word budget.
- Formal records (ADRs, business rules, design docs, plans, system nodes) keep a neutral documentary voice.
- Scope is human-readable prose: not code comments, structured output, or metadata.
- Destructive-action confirmations carry no wit in any voice.
- Tone, not words: if a flourish and a fact compete for the sentence, the fact stays.
