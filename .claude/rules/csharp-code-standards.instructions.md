---
applyTo: "**/*.cs"
paths:
  - "**/*.cs"
---

# C# Code Standards

> **Full guidance:** `.github/docs/csharp-code-standards-guide.md`

Extends `code-standards.instructions.md`. Sources: ktaranov/naming-convention, the .NET runtime style guide.

## Language Version

Pin the LangVersion the project's csproj declares; do not use a feature above it; no preview features without an ADR.

## Verify, Don't Recall

- Not 100% sure a pattern, API, or syntax shorthand behaves as remembered, exists under the pinned LangVersion and target framework, or is actually faster? Research it first (the local doc corpora or the vendor docs), then write it.
- A "more performant" API or clever shorthand claimed without evidence is a guess; back it with the doc or measurement before it lands.

## Naming

| Identifier | Convention | Example |
|---|---|---|
| Class, struct, record | PascalCase | `ClientActivity` |
| Interface | `I` + PascalCase | `IGroupable` |
| Method, property, public field, constant | PascalCase | `CalculateStatistics` |
| Private field | `_camelCase` | `_registrationDate` |
| Parameter, local | camelCase | `itemCount` |
| Type parameter | `T` + PascalCase | `TResult` |
| Namespace | `Company.Product.Module` | |

No Hungarian, `SCREAMING_CAPS`, or underscores except the private field prefix. Abbreviations 3+ chars PascalCase (`XmlDocument`); two-char stay uppercase (`UI`, `IO`).

## Null Safety

Enable nullable project-wide (`<Nullable>enable</Nullable>`); warnings as errors. Null-forgiving `!` only when the compiler cannot prove safety, with a comment saying why. Prefer `is not null` / `is null` over `!=` / `==`.

## Async

Suffix async methods with `Async`. Return `Task` or `ValueTask`, never `async void` except event handlers. Pass `CancellationToken` through every async chain. `ConfigureAwait(false)` in library code.

## Dependency Injection

Register services in a composition root. Constructor injection only. Do not resolve from `IServiceProvider` inside business logic. Scoped services must not be injected into singletons.

## Error Handling

Throw specific types, not bare `Exception`; custom exceptions use the `Exception` suffix (`BarcodeReadException`). Exception filters (`when`) avoid catching what you cannot handle. `ILogger<T>` for structured logging.

## Type Usage

C# aliases (`int`, `string`, `bool`) for declarations; framework names (`Int32.TryParse`) for static member access. `var` when the type is obvious from the right side; explicit types for primitives.

## Class vs Struct vs Record

Small immutable value with value semantics: `readonly record struct`; larger, polymorphic, or shared: `record class` (Gen 0 allocation is cheap; benchmark before avoiding it). Below C# 10, `record struct` is unavailable: use `readonly struct` + `IEquatable<T>`. Flip caveats (copy cost past ~16 bytes, boxing, heap capture, default equality, mutability): the guide.

## LINQ

Method syntax for simple queries; query syntax for multiple `from`/`let`/`join`. No LINQ in allocation-sensitive hot paths. Materialize (`.ToList()`, `.ToArray()`) at the boundary, not inside loops.

## Allocation Discipline

Where a hot path exists (a per-frame, per-request, or per-message loop), it allocates only what its work strictly requires. Each new hot-path allocation is a cost to justify.

- Reuse across iterations: preallocated buffers and collections, `ArrayPool<T>` for transient ones; clear, don't reallocate.
- Prefer `Span<T>`/`ReadOnlySpan<T>`/`Memory<T>` over copying slices; `stackalloc` for small short-lived buffers.
- Hot-path bans: capturing closures, iterator methods, `params` arrays, boxing (struct-through-interface, `object` storage), string building, LINQ (above).
- Cold paths (setup, config load, tooling) keep clarity first; do not contort them to save a Gen 0 allocation (benchmark-first note: the guide).

## Collections

Return `IReadOnlyList<T>`, `IReadOnlyCollection<T>`, or `IEnumerable<T>` when mutation is not intended; concrete types internally. Collection expressions where supported.

## Enums

Singular names for standard enums, plural for `[Flags]`; no `Enum` or `Flags` suffix. No underlying type or explicit values unless required (bit fields).

## Events

Event args suffix with `EventArgs`, delegate types with `EventHandler`. Handlers take `object sender` and typed `e`.

## Code Organization

One type per file, name matches type. Allman braces. Members top-down: static fields, instance fields, constructors, properties, public then private methods.

Extract a cohesive block of logic into its own class when it makes the host easier to read; another file is a fair price. Place it in the owning module's feature folder or a Utilities home per the project's folder conventions. Keep the extraction as simple as the requirement demands (KISS/YAGNI, `design-principles`).

## Testing

NUnit 4 constraint model (`Assert.That`; legacy asserts in `NUnit.Framework.Legacy`). Projects `{ProjectName}.Tests`, one class per type (`FooServiceTests`). Names `Method_State_ExpectedBehavior` per `testing.instructions.md`. Moq, default Loose: verify outcomes, not call order. Factory methods for data. Author via the `unit-test-creation` skill.

## Stack profile

This file is the standards file for the `csharp` stack profile, selected in Repo Signals (`research.instructions.md`). The pipeline's checkable C# constraints (purity boundary, threading, tests, build commands) live in `.github/docs/csharp-code-standards-guide.md` § Stack profile.
