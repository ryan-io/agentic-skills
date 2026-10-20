---
applyTo: "**"
---

# Research Practice
How the agent gathers context and cites sources. Use it when a task is documentation-heavy, source-sensitive, or needs broad repository context. The writing standard (`concise-documentation`, `.github/docs/writing-voice-guide.md`) governs how findings are written; this file governs how they are gathered and supported.

## Defaults
- Prefer primary documentation and direct source links over secondary summaries.
- Date any fact that can change over time, so a reader knows when it was true.
- Keep a short evidence trail for every recommendation or conclusion: the file, command, or link it rests on.

## Suggested Flow
1. Inspect local code and docs first. The repository is the primary source.
2. Browse only for facts that are external or unstable, not for what the repository already answers.
3. Summarize findings with file paths, commands, or links, so each claim can be checked.

## Repo Signals
Stable facts about this repository that research should assume rather than rediscover.
Fill per project: primary language and version, framework, build and test commands, architecture style, where local docs live.
Stack profile: name it here (`csharp`, `lua`, or `generic`); skills read the matching profile. `generic` means only `code-standards.instructions.md` applies.
