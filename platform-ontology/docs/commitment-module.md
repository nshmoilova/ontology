# The commitment module

A sibling of the identity modules. It imports `core` and `control-plane`;
nothing imports it. It holds what the platform promised for an offering and
whether that promise is measured — never the measurements themselves.

## What a commitment is

One node per promise, attached to a capability offering, which carries the
scope. It states exactly one metric from a closed scheme, a target with a
QUDT unit and a comparator, the window it is judged over, at least one
measurement source, at least one validation reference, and a lifecycle state.

A commitment missing its source or its validation is a **violation**: an
unmeasured claim is aspirational, not a guarantee. That sentence was
evaluated as a principle and not promoted; here it is a shape.

## What an observation is

A windowed aggregate of one metric for one commitment — a SOSA observation
with a result and a window. Per-request measurements never enter the graph;
they belong to the observability platform.

## How to add a commitment

1. Name the offering it is for. If the offering does not exist, that is a
   control-plane change first.
2. Pick the metric from `cmt:MetricScheme`. A new metric is a decision, not
   a string.
3. State target, unit (QUDT IRI), comparator, window.
4. Name the measurement source and the validation reference — a query in
   `queries/competency/` or an external check, as an `xsd:anyURI`.
5. Run `ci/validate.py`. CQ-9 lists every commitment with its latest
   observation.

## Vocabulary

SOSA/SSN for observable properties and observations; QUDT for units; the
repository's own closed schemes for metric, comparator and state. No product
names in terms; instances may name the real monitoring system.

## What is deliberately not here yet

- Commitments as declarations (scope, approval rigor, supersession).
- An offering readiness state gated on validated commitments.
- The service catalogue (contracts, versions, consumers).
- A JSON-LD projection for agents beyond the browser index.

Each is in the competency backlog under *Non-functional commitments*.
