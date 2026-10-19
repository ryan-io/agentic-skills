# Reverse Engineering Guide: Running Black Box

Companion to the `reverse-engineering` skill for targets with no code in hand: a service, a device, a protocol, a host API observed only from outside. The work is experimental: hypothesize, probe, record. Facts dated 2026-10-18 unless marked.

## What changes with no code

There is no static pass. Every row in the hypothesis ledger moves only by an experiment, and the dossier's Model is a behavioral model (inputs, outputs, states, timing), not a component map. Keep the question narrow; a black box answers one question per experiment and never volunteers the rest.

## Permission first

Observe only what you are entitled to observe: your own traffic, your own account, a system you are authorized to test. Capturing other people's traffic, probing a service past its terms, or evading rate limits or detection is a stop. Record the authorization in the dossier's `license` field.

## First contact

- Use it as a user for one time-boxed session. Write each visible behavior as an assumed row.
- Collect the public surface: documentation, API references, status pages, error messages, version strings, client libraries. A client library is often the real specification.
- Capture one complete session end to end before designing any experiment. Forshaw's order: capture, then analyze structure, then probe.

## Experiments that move rows

- **Differential probing.** Change one input, observe the one output that changes. A row moves to known when the same change produces the same effect three times.
- **Boundary probing.** Empty, maximum, malformed, out of order. The error path reveals the validation model and often the internal naming.
- **State inference.** Sequence operations and note which orders are accepted. Draw the state machine; each transition is a row with its triggering experiment as evidence.
- **Timing and ordering.** Latency and response order reveal caches, queues, and batching. Record measurements in a table with their conditions, never as prose.
- **Protocol structure.** From captures, recover framing, length fields, type tags, and encoding. Forshaw's method is to write a parser and let its failures locate the next unknown field.

## Recording a black box

- **Inventory.** Endpoints, message types, observable states, the tooling used to observe (proxy, capture, logs).
- **Model.** A state diagram and a protocol or message grammar, each element tied to a row.
- **Flows.** One sequence diagram per experiment family, with the probe as the first message.
- **Hypotheses.** Rows stay inferred when an experiment is impossible or unauthorized, and say so. Unobservable internals are never guessed into the Model.

## When the box opens

A binary, a client library, or a leaked source tree turns the job into the artifact or source case. Hand on to that guide, keep the behavioral rows as the characterization tests the next pass must satisfy, and continue the same dossier.

## Sources

All accessed 2026-10-18.

- Forshaw, Attacking Network Protocols, No Starch Press, Jan 2018.
- Chikofsky and Cross, "Reverse Engineering and Design Recovery: A Taxonomy," IEEE Software 7(1), 1990.
- Feathers, Working Effectively with Legacy Code, Prentice Hall 2004 (characterization tests).
