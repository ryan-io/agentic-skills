---
name: pipeline-stg2-volatilities
description: >
  Stage 2 of the design pipeline: interactively decompose a problem, feature, or system by
  volatility. Identify what is likely to change, encapsulate it behind stable interfaces, and
  structure components around change boundaries rather than business functions. Use when the user
  mentions "volatility decomposition", "axes of volatility", "service boundaries", "how should I
  decompose this", "what's likely to change", or presents a system to break down. Reads the
  design doc's Requirements section when present; writes its Volatilities section
  (docs/design/{slug}-design.md).
tags: [decomposition, design-pipeline, skill]
---

# Pipeline Stage 2: Volatility-Based Decomposition

Interactive session. The developer brings a problem, feature, or system. Help them discover what changes, what doesn't, and where the boundaries belong. Ask; don't lecture.

The approach, in order:

1. Observe the system aspect by aspect, asking what changes.
2. Apply the two axes of volatility.
3. Scrub away solutions masquerading as requirements.
4. Confirm the volatilities list.
5. Define boundaries. Design comes last and goes fast; finding the right volatilities is the slow, valuable work.

Second stage of the pipeline: pipeline-stg1-requirements -> pipeline-stg2-volatilities -> pipeline-stg3-architecture. Also runs standalone.

## Ground first

- Read the project's ADRs and design documents for the area, so a proposed boundary doesn't cut against a settled seam.
- Read the code a boundary would split, including the call sites that depend on the types being separated.
- An unresolved conflict in the records is a blocker to raise, not a seam to design past.
- Keep claimed volatilities grounded in evidence. For external facts (a library's surface, a framework's limits, a format's stability), verify against documentation, not memory.
- Where an axis of change matches a known pattern (Strategy, Factory, Memento), invoke `design-patterns` to name the candidate. Only where the axis is real.

## Input and output

- Input: the `## Requirements` section of `docs/design/{slug}-design.md` when it exists, including its "Solutions to scrub" list. Otherwise, work from what the user describes.
- Output: the `## Volatilities` section of the same doc: confirmed volatilities, items set aside as variable or nature-of-the-business, and proposed boundaries.
- Standalone runs included: check for the doc first. If it exists, modify only this section. If not, create it with only this section.
- If the section already exists, this is a revision: read it first, apply the change, preserve everything else, confirm before overwriting.

## The central question

**"Is this volatile, or just variable?"**

- **Volatile:** open-ended change that ripples across the system unless encapsulated at the architecture level. Deserves its own component behind a stable interface.
- **Variable:** bounded change handled with a conditional, configuration, or a code-level abstraction. Not an architectural concern.

Call out the clearly variable immediately. Collect the ambiguous as candidates and decide in Phase 4.

## Starting the session

- Opening question: "What is the system (or feature, or problem) you want to decompose?"
- Derive a kebab-case `{slug}` and confirm it. If the design doc already has a `## Requirements` section, read it and confirm you're continuing the same work.
- Then: "Describe the system at a high level. What are its major aspects or concerns? Don't think in components yet."
- Goal: get the system on the table. Do not propose components yet.

## Phase 1: Observe and walk through

Walk the system aspect by aspect, like walking through a house.

- "Consider [aspect]. Does it change over time? Has it before? Do you expect it to?"
- "What specifically changes? The technology? The rules? The format? The provider?" Pin the dimension of change.
- Keep a running candidate list. Observations, not architecture.
- Clearly variable? Say so: "That sounds like something you'd handle in code, not an architectural boundary. Does that match your read?" Set it aside.

## Phase 2: Apply the axes of volatility

### Axis 1: same customer over time

- "If one customer used this for the next five years, what would need to change as their situation evolves?"
- Key distinction: you wouldn't change how you send email based on connectivity type. The transport (dial-up, fiber) is volatile; the capability (send email) is stable. Encapsulate the volatility behind the stable interface.

### Axis 2: across customers right now

- "If you deployed this to a second customer today, what would be different?"
- "Different protocols? Rules? Integrations? Workflows? Where does usage diverge?"

### Iterate: A -> B -> C

Treat the system as one monolith (A) and peel it:

1. "Could you use this with one customer forever?" If no, encapsulate what changes over time (B).
2. "Could you use B across all customers right now?" If no, encapsulate what differs across customers (C).
3. Repeat until every point on both axes is encapsulated.

Axis assignment is a discovery aid. A volatility may surface on both axes; once found, one component handles it.

### Design for your competitors

- "If you built this for a competitor or another division, what would have to change?" Those deltas are volatilities.
- Heuristic: two ways of doing something implies many more. That's a signal to encapsulate.

### The "what if?" stress test

For aspects that surfaced nothing, ask targeted questions:

- "What if you switched the database?"
- "What if a new regulation changed the validation rules?"
- "What if you added a mobile client?"
- "What if a third-party API changed its contract?"

"We'd have to change a lot" marks a candidate volatility.

## Phase 3: Scrub solutions masquerading as requirements

Most requirement lists are full of solutions in disguise. Scrubbing them is how you find the true volatilities.

- For each candidate: "Is [candidate] the only way to satisfy this need, or are there alternatives?"
- Alternatives exist? It's a solution, not the requirement. Drill: "What is the actual need it satisfies?" Check whether that answer is itself a solution. Keep drilling until no further abstraction exists.
- Watch for mutually exclusive requirements at any level (e.g. "feeding" vs "dieting"). That means you haven't reached the true need yet.

Example flow:

- Candidate: "Cooking support."
- "Is cooking the only way to satisfy this need?" -- "No, they could order food or eat out."
- "So the need is feeding the occupants. Is feeding the real requirement? What if they're dieting?" -- "Support both."
- Feeding and dieting conflict, so feeding is still a solution. The real requirement is occupant wellbeing: caloric intake, temperature, humidity, and more.

Encapsulate the underlying need (wellbeing) and the design survives when solutions change.

## Phase 4: Confirm the volatilities list

The list is an open-ended discovery artifact, not a scope document. Some volatilities will be out of scope; designating a component costs almost nothing, so name them anyway.

- Present the full picture: confirmed volatilities, items filtered as variable, remaining ambiguous candidates.
- For each ambiguous one: "If [X] changed, would you restructure components and interfaces, or just update code inside one component?" The former is volatile, the latter variable.
- Validate each volatility: is addressing it a requirement? Not every volatility earns a boundary.

### Worked example (condensed): trading system

Several entries began as solutions in disguise:

- **Users** (traders, read-only customers, admins) and the **client apps** their differences drive (web, desktop, mobile).
- **Security:** domain accounts in-house vs federated SSO for internet customers.
- **Notification:** "send an email" is a solution; the volatility is notify (transport, recipients, publisher).
- **Storage:** "local database" is a solution; the volatility is "do not lose data" (local DB through distributed cache).
- **Connection and synchronization:** synchronous lock-step vs async queued calls.
- **Trade item** (stocks today; bonds, currencies, futures later) and the **workflow** each drives.
- **Locale and regulations**; **market feed** (source, format, rate, protocol).

The list's value is the mindset, not the scope. Several of these won't ship in v1.

### Functional vs volatile: the house example

Use this when the user struggles with the distinction.

- A functionally decomposed house has `Kitchen`, `Bedroom`, `Bathroom`: named for what the house *does*. Those are behaviors, not areas of change.
- Volatility-based decomposition asks what actually changes:
  - Axis 1 (same customer over time): Furniture, Appliances (CRT to OLED), Occupants, Appearance, Utilities (dial-up to fiber).
  - Axis 2 (different customers now): Structure, Location Context (neighbors, regulations, building codes, taxes).
- There is no `Cooking` component. Cooking is behavior that emerges from Occupants, Appliances, and Utilities interacting.
- A component named after a behavior instead of an area of change is functional decomposition.

Close the phase: "Here are the confirmed volatilities: [list]. Each would break the architecture if uncontained. Does this look right?"

## What not to encapsulate

Record these decisions in the output; they are part of the analysis.

- **The nature of the business.** The core business tends to be constant. FedEx has always been shipment and delivery; designing for a pivot into healthcare is out of scope. Two signs a change is nature-of-the-business: it is rare, and any attempt to encapsulate it comes out poorly no matter the investment.
- **Longevity beats recency.** The longer something has been done the same way, the less volatile it is. Weight stability over recency.
- **Speculative design.** Once volatility thinking clicks, it's easy to see volatility everywhere. A design with a building block for every imagined change is bad design. Encapsulate real, validated requirements, not imagined ones.

## Phase 5: Define boundaries

Propose components. Each encapsulates one coherent area of change behind a stable interface.

- Mapping is rarely one-to-one: a component can hold several related volatilities. One volatility does not mean one service.
- For each boundary: "Does [component] own one coherent area of change, or is it mixing concerns?"
- **Naming matters.** Name components for what they encapsulate, not what the system does. `BillingService` and `CookingModule` name business functions. The Manager/Engine/ResourceAccess taxonomy is applied next stage (`pipeline-stg3-architecture`); here, keep names pointed at the change.

### Validate independence

- For each pair: "Can [A] change without forcing [B] to change?" If not, they belong together or one is functionally decomposed.
- The axes should be independent. A component spanning both axes signals functional decomposition in disguise.

### Check for missing boundaries

- "Is there a component here that maps to neither axis?"
- A component that exists because the system "does" something, not because something "changes," is functional decomposition. Remove it or reframe it.

## Phase 6: Note interactions and hand off

- Behavior emerges from the encapsulated volatilities interacting. There are no dedicated behavior services. Capture the insight; don't design the structure here.
- Flag one thing: if the client stitches components together (A -> B -> C), the architecture is flat and the client will bloat into the system. Coordination belongs in an intermediary layer. Note where it's needed; placing it is stage 3's job.
- Save the volatilities and boundaries as the `## Volatilities` section, in short plain prose.
- Offer the handoff: "The volatilities and boundaries are ready. Want me to run pipeline-stg3-architecture to classify these into a layered architecture?"

## Reviewing an existing design

Same approach, framed around what exists. The prize: catching what the user treats as volatile that is only variable, and what they treat as fixed that is volatile.

- Open: "Walk me through your current services and what each is responsible for."
- Per service: "Does this encapsulate something that changes, or something the system does?" If it changes: "Would the change break the architecture, or could you handle it inside the component?"
- Build the axis table as you go:

| Service | Axis 1 (changes over time?) | Axis 2 (differs across customers?) | Volatile? |
|---|---|---|---|

- Check for solutions in disguise: "Is [service] the real need, or a specific solution to a deeper need?"
- Probe for functional decomposition by asking, not asserting: "Is the client doing orchestration that doesn't belong in a presentation layer?" "If [requirement X] changed, how many services would you touch?" "Can you integration-test [service] without wiring up the whole system?"
- Services that fail the check: ask what volatility they should encapsulate. Services that pass: verify scope ("one axis of change, or has it absorbed variable concerns?").

## Key principles (for reference, not lecturing)

- Functional decomposition is valid for requirements discovery, never for system design. There is no direct mapping from requirements to components.
- Domain decomposition (by business domain) is functional decomposition in disguise.
- The design prime directive: never design against the requirements. Encapsulate the volatilities and let behavior emerge from composing them (`pipeline-stg4-validation` proves this).

## References

- Löwy, Juval. *Righting Software*. Addison-Wesley, 2019.
- Parnas, David L. "On the Criteria to Be Used in Decomposing Systems into Modules." *Communications of the ACM*, 15(12), 1972.
- Nygard, Michael. *Release It!*
