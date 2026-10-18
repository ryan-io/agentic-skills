---
name: architecture-conformance
description: >
  Audit the live codebase against the layered architecture it claims: *Manager/*Engine/*Access
  naming, layer dependency direction and closed call rules, the purity boundary (no UI-framework
  reference in the business tier), no static mutable state, and code-to-systems-map
  correspondence. Use for "audit the architecture", "check the layering", "has the code
  drifted", "are we still following the design", or before closing a milestone; Gate C judges
  one increment, this skill the accumulated whole. Reads the project-reference graph and source
  via rg, writes a dated report to docs/reviews/, and changes no code.
tags: [architecture, critique, skill]
---

# Architecture Conformance (the cumulative audit)

Gate C proves each increment against its own design; nothing re-proves the sum. Every increment can pass its gate while the whole drifts one small liberty at a time. This skill is the periodic sweep that catches the drift.

## Ground first

- Open `docs/systems/` (its index first, where one exists) for the canonical layer per system.
- Open `docs/adr/adr-index.md`, then only the ADRs that bind layering, seams, and the purity boundary.
- Read the `## Architecture` section of each landed `docs/design/{slug}-design.md`: what the code claims to implement.
- Build the project-reference graph from the `.csproj` files (`rg -n '<ProjectReference' -g '*.csproj'`), never from memory. Each project's layer comes from its name or the systems map.
- Read source with `rg` and targeted reads, not whole-directory scrapes.

**Fan-out.** A full sweep splits into lanes, one check family each, read-only.

- **Can spawn subagents (Claude Code):** spawn one `audit-reader` per lane; the session synthesizes their findings.
- **Cannot spawn subagents (Copilot chat, terminal):** run the lanes inline, one at a time, and say so in the report.

## The checks

1. **Naming.** Every public service type suffixed `Manager`, `Engine`, or `Access` sits in the layer its suffix claims (`rg -n 'class \w+(Manager|Engine|Access)\b' -g '*.cs'`; the containing project fixes the layer). Gerund (-ing) prefixes appear only on Engines. A service named for a business function rather than the volatility it encapsulates is a finding even when it compiles and passes tests.
2. **Dependency direction.** All project references point inward. `Contracts` references nothing project-owned. A reversed or sideways reference is a High finding.
3. **Purity boundary.** No business-tier project (Contracts, Managers, Engines, ResourceAccess) references a UI-framework assembly or package. Default C#/WPF stack: `PresentationFramework`, `PresentationCore`, `WindowsBase`, `System.Windows.*`, `UseWPF` in the csproj. Check both the csproj and `using` lines; the project's own ADRs name its UI framework.
4. **Call rules (closed architecture).** Trace each Manager, Engine, and ResourceAccess interface's call sites with `rg`:
   - Clients call only Managers, one Manager per use case.
   - A Manager reaches a peer Manager only as a queued handoff, never synchronously mid-use-case.
   - Engines call only ResourceAccess; never Managers, never each other.
   - ResourceAccess calls nothing above it and never another ResourceAccess.
   - ResourceAccess exposes business verbs (`GetCustomer`, `SaveOrder`), not CRUD or I/O verbs leaking the resource (`ExecuteSql`, `ReadFile`).
   - Only Managers publish events; only Clients and Managers subscribe. Utilities are open to all.
5. **Contracts termination.** Cross-layer dependencies go through `Contracts` interfaces. A concrete type from one layer in another layer's signatures is a leak, even where the reference graph allows it. Constructor injection only; a service locator or static accessor in business logic is a finding.
6. **Static mutable state.** Candidates: `rg -n --pcre2 '\bstatic\s+(?!readonly|class|void|async|extern|partial)[\w<>\[\],?. ]+\s+\w+\s*(=[^>]|;|\{\s*get;\s*set)' -g '*.cs'`. Judge each hit: a mutable static field or settable static property in the business tier is a finding; constants and immutable caches are not.
7. **Map correspondence.** Every business-tier project has its row in the systems map with its path recorded. Every service named in a landed `## Architecture` section exists in code, or is carried explicitly as debt or a future system. Route gaps to `system-map`.

## The report

Write `docs/reviews/{date}-architecture-conformance.md`, under `concise-documentation`:

- One row per finding: check, location (`file:line` or project), severity, routed owner, one plain sentence.
- Routing: code faults to `deliver-change`; layering faults that need redesign to the design pipeline (with an ADR where the fix changes a decision); deliberate deferrals to `tech-debt`; map gaps to `system-map`.
- A clean sweep is a valid result. Record that it ran and against which commit (`git rev-parse --short HEAD`).

## Revise a past report

Reruns write a new dated report. A past report changes only to correct a factual error: read it, change only the error, preserve the rest, confirm before overwriting, same path.

## Cadence

- On demand, not a commit gate. Worth running after any batch of increments since the last report and before a milestone closes.
- A check that stabilizes into something purely mechanical: propose promoting it into a script or CI check rather than growing this skill. That promotion is an ADR-worthy process change, not a silent addition.

## Boundaries

- Reads and reports; changes no code and no records. Never commits.
- Distinct from `pipeline-stage-review` (per-increment gates) and `system-review` (harness setup and engineering big picture).
- Ask, do not guess: a suspected violation the records cannot adjudicate is a question, not a finding.

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019 (the layered taxonomy and call rules).
