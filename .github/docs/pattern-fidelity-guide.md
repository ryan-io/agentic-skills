# Pattern Fidelity Guide

The deep companion to `../instructions/pattern-fidelity.instructions.md`. The thin rule carries the grounding order, the confirm-first step, and the resist-generic directive. This guide carries the fuller examples and the mechanics of how a confirmed pattern becomes precedent. Read it when introducing or proposing a new pattern.

## Resist generic solutions, in detail

The failure mode is reaching for a textbook abstraction the project never asked for. Examples: a generic repository layer over a codebase that queries directly, an event bus where a function call suffices, a config framework for three constants, premature interfaces with one implementation. Industry-standard is not the same as right-for-here. Solve the problem the project actually has, at the scale it actually has it.

Match the domain's vocabulary too. Name types and functions after the project's terms, not generic ones (`Invoice`, not `DataRecord`). Mirror the existing layering, error-handling, and dependency style rather than importing a foreign one.

## How patterns become precedent

Confirmed patterns get captured, not left implicit:

- A convention that governs how code is written earns a line in the owning instruction file, edited at its source in `.github/instructions/` under developer approval.
- A deliberate, reusable decision earns an ADR.

When the developer confirms a new pattern, propose codifying it through one of these channels. The next agent then inherits it as precedent instead of rediscovering or contradicting it. A pattern adopted on a hunch becomes the precedent everyone copies next. That is why the thin rule's confirm-first step matters most in greenfield work, where no precedent yet exists.
