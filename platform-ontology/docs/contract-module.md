# The contract module

A sibling of the identity modules. It imports `core` and `control-plane`;
nothing imports it. It holds the published interfaces of capabilities, their
versions, and the governed changes that publish, deprecate and retire them.

## The scoping decision (D62)

The catalogue contracts **capabilities, not services**. A contract is the
published interface of exactly one capability. A consumer is an application,
which already declares what it requires through a capability requirement;
the requirement now pins a contract version. "Service" stays out of the
vocabulary.

## What a version is

A version string (MAJOR.MINOR.PATCH), a lifecycle state from a closed scheme
(draft, published, deprecated, retired), a compatibility with its predecessor
(compatible, breaking), a reference to the interface artifact — an OpenAPI or
AsyncAPI document — and the version it supersedes.

## The published change process

Publication, deprecation and retirement are **contract changes**: desired-
state declarations with a management plane, a scope, an approval where the
scope requires one, and supersession. A version that is published, deprecated
or retired with no change declaration behind it is a violation.

## What is enforced

- A contract belongs to exactly one capability; a version to exactly one contract.
- No publication without a change declaration.
- A requirement pinning a retired version is a violation — a consumer on a dead contract.
- An offering whose capability has no published version is a violation — deployed without a contract.
- A breaking version that deprecates its predecessor with no tolerance window is a warning to stewardship.

## What is deliberately not here yet

- Consumers other than applications (a platform capability consuming another's contract).
- Contract-level commitments (the latency a consumer reserves against a version).
- The principle — "consumers depend on contracts, never on implementations; a
  contract changes only through a published, approved version" — waits on two
  decisions made because of it.
