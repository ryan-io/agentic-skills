---
name: unit-test-creation
description: >
  Write unit tests for code that already exists, one unit at a time, applying the project's
  testing standards where they exist. Use when the developer wants to "write tests", "add unit
  tests", "cover this with tests", "test this class", or hands over a class and asks for tests.
  Default stack produces NUnit 4 tests with Moq for C#. Enumerates behaviors and edge cases
  first, writes Arrange-Act-Assert, mocks only at owned boundaries, and runs the suite green.
  For test-first pairing on a new design, use pipeline-stg6-implementation instead.
tags: [testing, skill]
---

# Unit Test Creation

Turn a unit of code into a focused test suite. This skill is a procedure, not a standard.

- The standards live in `testing.instructions.md` (universal) and `csharp-code-standards.instructions.md` (stack), in `.github/instructions/` mirrored at `.claude/rules/`. Read them first and follow them. Where absent, the defaults below apply.
- Default stack: C# with NUnit 4 and Moq.

## When to use

- The developer wants tests for code that exists, or that is being written next to the tests.
- For test-first pairing that builds a new design service by service, use `pipeline-stg6-implementation` instead.

## Input

- Point at the unit under test: a class, a method, a file. Read it and its collaborators.
- Target ambiguous or spanning many types? Ask the developer to name one unit. Ask; don't guess.

## Workflow

Work one unit at a time.

1. **Understand the contract.** Read the code and its public surface: what it returns, what state it changes, what it throws, which collaborators it calls. Test the contract, not the implementation.
2. **Enumerate cases before writing.** Happy path, boundaries (empty, null, zero, max, off-by-one), error paths, every branch. One behavior per test. Long list? Show the developer first.
3. **Arrange-Act-Assert.** Small Arrange, single Act, focused Assert. Name `Method_State_ExpectedBehavior` so it reads as a sentence. Simplest inputs that prove the behavior.
4. **Mock only at owned boundaries.** Substitute external dependencies (clock, network, filesystem, database, other services) through the abstraction the code already uses. Never mock the type under test, types you don't own, or private detail. A test that needs private state is a design signal, not a mocking problem. Prefer a fake when the dependency has real behavior. Over-mocking is the top failure mode for generated tests: suites that pass while production breaks.
5. **Verify outcomes, not interactions.** Assert the observable result: return value, changed state, thrown exception. Verify a collaborator call only when the call is the behavior ("sends the email"). Don't assert every interaction or call order.
6. **Run the suite.** Green and fast. A test needing real network, filesystem, or wall clock is not a unit test; isolate the dependency or move it to the integration tier.
7. **Cover the fix.** Testing a bug fix? Add a test that fails without the fix and passes with it.

## C#: NUnit 4 and Moq (default stack)

- NUnit 4 uses the constraint model: `Assert.That(actual, Is.EqualTo(expected))`, not classic `Assert.AreEqual`. The classic asserts moved to `NUnit.Framework.Legacy.ClassicAssert`; don't use them in new tests.
- `[Test]` for a case, `[TestCase(...)]` for parametrized inputs, `[TestCaseSource]` for complex data, `[SetUp]` for shared arrange.
- Expected exceptions: `Assert.That(() => sut.Do(), Throws.TypeOf<ArgumentException>())`.
- Moq defaults to Loose; that's right. Set up only what the test needs; verify the one or two calls that are the behavior. Avoid `MockBehavior.Strict` and blanket `VerifyAll`: they couple tests to call order and incidental setup.
- Layout: a `{ProjectName}.Tests` project, one test class per type (`FooServiceTests`), factory methods for test data.
- Moq's 4.20.0 SponsorLink component was removed in 4.20.2; current 4.x is clean. If supply-chain policy comes up, note NSubstitute as the common MIT alternative and confirm before switching frameworks. A framework switch is a developer decision.

## Revising existing tests

- Read the file first. Match its patterns: framework version, naming, fixture and `[SetUp]` style, helpers.
- Apply only the requested change. Preserve every other test and the file's conventions. Confirm before overwriting. Same path unless renamed.

## Done

- Every behavior and edge case has a test; names read as sentences; mocks sit only at owned boundaries; assertions check outcomes; the suite runs green.
- Summarize what was covered. Name anything you chose not to test, and why.
