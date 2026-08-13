---
applyTo: "**/*.cs"
paths:
  - "**/*.cs"
---

# C# Code Standards (stub)

Placeholder: the stack-specific C# code standards land here; the file exists so pointers from `unit-test-creation`, `pipeline-stg6-implementation`, and `xml-documentation.instructions.md` resolve. Until the real content arrives, those skills fall back to their inline defaults: pure business-logic tier never references a UI-framework assembly, composition-root DI against `Contracts` interfaces, no service locators or static mutable state, `async`/`await` with `ConfigureAwait(false)` in the pure tier, UI-thread marshaling only at the UI edge. Central file: fill it in the agentic-skills repo; the sync overwrites project-local edits.
