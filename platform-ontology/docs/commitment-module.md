# The commitment module

A sibling of the identity modules. It imports `core` and `control-plane`;
nothing imports it. It holds what the platform promised for an offering and
whether that promise is measured — never the measurements themselves.

## What a commitment is

One node per promise, attached to a capability offering. A commitment is a
desired-state declaration (D59): declared through the management plane, bound
to a scope that contains the offering's, approved where that scope requires
it, superseded rather than edited. It states exactly one metric from a closed scheme, a target with a
QUDT unit and a comparator, the window it is judged over, at least one
measurement source, at least one validation reference, and a lifecycle state.

A commitment missing its source or its validation is a **violation**: an
unmeasured claim is aspirational, not a guarantee. That sentence was
evaluated as a principle and not promoted; here it is a shape.

A committed commitment also records its **rationale** (D72): the reason for
its target, as text citing the decisions it rests on by identifier. A
committed commitment without one is a warning routed to stewardship — the
promise still binds; what is missing is reviewability.

## What a floor is

A baseline (D66) is a floor declared at a scope: one metric, comparator,
target, unit and window that every offering beneath the scope must meet with
a committed commitment at least as strong, in the floor's unit (D69). It is a
requirement, not a promise, so it needs no measurement source — but it
records its rationale like a commitment does. The production floors are D69;
CQ-15 and CQ-17 show coverage and margins.

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
4. Declare it: management plane, scope (at or above the offering's), and an
   approval if the scope requires one.
5. Name the measurement source and the validation reference — a query in
   `queries/competency/` or an external check, as an `xsd:anyURI`.
6. State why: `cmt:rationale`, citing the decision that set the target.
7. Run `ci/validate.py`. CQ-9 lists every commitment with its latest
   observation; CQ-18 lists every current promise with its reason.

## Vocabulary

SOSA/SSN for observable properties and observations; QUDT for units; the
repository's own closed schemes for metric, comparator and state. No product
names in terms; instances may name the real monitoring system.

## When a metric applies

Each metric in the scheme states one applicability condition (D74): always;
when a realising data plane holds a data category; when the capability is
offered in more than one region. CQ-19 derives, for every offering, the
metrics that apply and which carry no committed promise. That is advice to
the owner; only a floor obliges.

## What a consumer needs

A capability requirement may state needs (D75): one per metric, each a
comparator, target and unit in the unit the offering promises in, approved
with the requirement. `NeedMetShape` rejects an enablement whose covering
available offering promises less than a need; CQ-20 lists needs against
promises as met, unmet or no promise.

## What is deliberately not here yet

- The kind of evidence behind a measurement source (production telemetry or
  isolated benchmark).
- Enforced composition along a request path. The browser composes promises
  for a consumer, but the conventions are advisory (D73).
- Tiers, only if asked for.

Each is in the competency backlog under *Non-functional commitments*.
