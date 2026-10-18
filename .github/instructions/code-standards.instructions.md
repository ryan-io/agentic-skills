---
applyTo: "**"
---

# Code Standards (Universal)
Apply to all source files regardless of language. Stack-specific rules live in `{language}-code-standards.instructions.md`. A stack file may supersede specific rules within its glob; supersessions are stated explicitly in that file.

## Null Safety
- Prefer explicit null handling over implicit assumptions.
- Use the language's null-safety features (nullable annotations, optional types, nil checks).
- Document intentional force-unwrap or null-suppression with a comment explaining why.

## Async Discipline
- Never block on async code from synchronous contexts.
- Name async functions distinctly from sync counterparts (follow language idiom).
- Propagate cancellation or timeout mechanisms where the runtime supports them.

## Decoupling & Dependency Management
Dependency Inversion as a design principle lives in `design-principles`. The hard rules here:
- Prefer constructor/initializer injection over service locators or global state.
- Resolve dependencies through a DI container or equivalent.

## Separation of Concerns
Single Responsibility as a design principle lives in `design-principles`. The hard rules here:
- UI code must not contain business logic. Business logic belongs in service/module layers.
- Follow the project's architectural pattern; do not mix patterns within a module.

## Naming Conventions
- Follow the language idiom (PascalCase, camelCase, snake_case, etc.).
- Names must be descriptive and unambiguous.
- Document project-specific naming rules in the stack-specific standards file.

## Comments
- An inline comment must warrant its existence; the default for a new one is not to write it. Before writing one, try a better name or an extracted method/class that makes it unnecessary.
- Comment to explain why non-obvious code exists, not to narrate what each line does.
- Keep a comment to one or two lines: a reason, a caveat, a pointer to a rule or ADR. Paragraph-length narration in the code body is the failure to avoid; if it needs a paragraph, it belongs in the design docs, not the source.
- Prefer a self-explaining name over a comment that restates the code; delete a comment that just repeats the identifier above it.
- Doc-comment conventions are stack-specific: for C# `///` docs, keep the `<summary>` to one sentence and push any essential extra context or governing id into a short `<remarks>` (`xml-documentation.instructions.md`), never a paragraph; for Lua, LuaCATS annotations with a one-sentence summary (`lua-code-standards.instructions.md`).

## Error Handling
- Never swallow errors silently.
- Use structured logging; avoid raw print/console output in production code.
- Validate inputs at public API boundaries and fail early with clear messages.

## Testing
- All new logic must have corresponding tests.
- Tests go in a dedicated test directory, not alongside production code (unless language convention dictates otherwise).
- Test names describe the scenario and expected outcome.
- Mock external dependencies; tests must not rely on network, filesystem, or database unless explicitly integration tests.
