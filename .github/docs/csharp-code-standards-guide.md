# C# Code Standards Guide

Companion to `csharp-code-standards.instructions.md` (mirror `.claude/rules/csharp-code-standards.instructions.md`). Carries rationale too long for the rule file.

## Class vs Struct vs Record

Small immutable value with value semantics: `readonly record struct`, struct performance with record ergonomics. Larger object, polymorphic, or heavily shared: `record class`, and let the GC do its job. Gen 0 allocation in .NET is a pointer bump and very cheap, so do not contort a design to avoid it without a benchmark. A runtime with a non-generational GC makes allocation costlier; the benchmark-first rule still holds, but profile on the shipping runtime.

Availability by LangVersion: `record` (class) needs C# 9. `record struct` needs C# 10; below that, fill the role with a `readonly struct` implementing `IEquatable<T>`.

### Caveats that flip the answer

- **Copy cost.** Structs copy by value on every assignment, argument pass, and return. The Microsoft guideline is roughly 16 bytes or smaller; beyond that, pass with `in` (or `ref readonly` parameters from C# 12) or reconsider. A large struct copied in a hot loop can lose to a single heap reference.
- **Boxing kills it.** Store a struct in `object`, a non-generic collection, or use it through an interface without a generic constraint, and you get a heap allocation anyway, worse than the record class because it happens repeatedly.
- **Not always on the stack.** A struct that is a field of a class lives on the heap inside that class. Same if it is captured by a lambda, or lives across an `await` in an async state machine or a `yield` in an iterator.
- **Equality performance.** Default struct equality falls back to a slow reflection-based `ValueType.Equals` path when the struct contains reference types or has padding. `record struct` generates field-by-field equality at compile time, materially faster than a hand-rolled struct with no `IEquatable<T>` implementation.
- **Mutability.** `record struct` is mutable by default, unlike `record class`. Use `readonly record struct` unless there is a reason not to.

Reference: .NET "Choosing between class, record, and struct" and the framework struct design guidelines.

## Allocation Discipline

Why a hot path is held to a stricter bar than "Gen 0 is cheap" above: the two rules meet at the GC, not in contradiction. A single allocation is cheap; an allocation per iteration per item is a steady garbage stream, and that stream turns into collection pauses a user feels as latency spikes. So the hot path budgets allocations (reuse, pooling, `Span<T>`), while cold paths keep the benchmark-first rule and allocate freely for clarity.

Availability: `Span<T>`, `ReadOnlySpan<T>`, `Memory<T>`, `ArrayPool<T>.Shared`, `stackalloc` into `Span<T>`, `string.Create`, and `MemoryMarshal` all work from `netstandard2.1` and .NET Core 2.1 up. `Span<T>` is stack-only (`ref struct`): it cannot be a class field, cross an `await`/`yield`, or be captured; use `Memory<T>` where the buffer must persist, slicing to `Span<T>` at the point of work.

## Stack profile (pipeline constraints)

The C# profile's checkable conditions. Pipeline skills and agents state the neutral rule and point here. A project selects this profile as `csharp` in Repo Signals (`research.instructions.md`).

### Layers and projects

- Client: a WPF app project (Humble Object Views, ViewModels, input wiring) plus an `Adapters` project that implements Contracts interfaces with WPF and framework types.
- Managers, Engines, ResourceAccess: pure C# class libraries referencing only `Contracts`.
- Project-reference graph: `rg -n '<ProjectReference' -g '*.csproj'`.

### Purity boundary

- The pure business tier (Contracts, Managers, Engines, ResourceAccess) never references WPF assemblies: `PresentationFramework`, `PresentationCore`, `WindowsBase`, `System.Windows.*`.
- No business-tier csproj sets `UseWPF`.
- Check both the csproj references and the `using` lines.

### Composition and state

- Every service registers in the composition root against its Contracts interface.
- No service locators or static globals.
- No static mutable state: no mutable static field or settable static property in the business tier. Constants and immutable caches are fine.

### Threading

- `async`/`await` throughout.
- UI-thread marshaling (`Dispatcher`) only at the WPF edge.
- Pure tier thread-agnostic: `ConfigureAwait(false)` on its awaits, with a `CancellationToken` threaded through.

### Documentation

- `///` XML doc comments per `xml-documentation.instructions.md`.
- One-sentence verb-first `<summary>`; the governing record id in a short `<remarks>`; hard cap two sentences per tag.
- All declaration-level documentation sits inside the XML tags, never in `//` comments.

### Tests

- NUnit 4 constraint model (`Assert.That`) with Moq, default Loose.
- Test projects named `{Project}.Tests`; test names `Method_State_ExpectedBehavior`.
- Full detail: `unit-test-creation` § C# profile.

### Build and test

- Repo Signals commands: `dotnet build` and `dotnet test`.
- Green means both commands exit 0.
