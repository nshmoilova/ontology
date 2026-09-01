# Competency Questions — v0.1.0

Each question is an acceptance test: it exists as a SPARQL query in
`queries/competency/` and is executed by CI against seed data. Add new
questions *before* adding new terms; a term with no question behind it is
scope creep.

| ID | Question | Query | Modules exercised |
|----|----------|-------|-------------------|
| CQ-1 | Which active sessions were established from an authentication event below AAL2, and for which principals? | `cq1-sessions-below-aal2.rq` | session, authn |
| CQ-2 | For every route, which upstream does it reach and which policy enforcement point mediates it? | `cq2-routes-and-peps.rq` | ingress, core |
| CQ-3 | Who executed and who approved each policy change, and was any approver human? | `cq3-policy-change-approvers.rq` | control-plane, core |
| CQ-4 | Which attribute assertions back decisions about a principal, and which authoritative source issued each? | `cq4-attribute-provenance.rq` | authz |
| CQ-5 | For each Permit decision, what is the full assurance chain (decision → session → authentication → method/AAL)? | `cq5-permits-with-assurance-chain.rq` | authz, session, authn |
| CQ-6 | Which workload principals exist, what are their SPIFFE identities, and which changes have they executed? | `cq6-workload-principals.rq` | core, control-plane |

## Backlog (draft, not yet modelled)

- Which resources are reachable through a route whose listener does not terminate TLS before the enforcement point?
- Which policies grant access based on attribute assertions that have expired?
- Which administrative scopes allow a workload principal to mutate the policy that governs its own access (self-authorization loop)?
- Which sessions outlived the revocation of the credential that established them?

### Platform vs. application authorization (layered-ingress design)

Ingress answers "can this subject cross this platform/application boundary?";
applications answer "what can this subject do inside it?". The control plane
defines entitlements; ingress only enforces them, against a small, stable,
platform-owned vocabulary. One question per principle; the last two are
invariants and must return zero rows.

- Which platform entitlements does each principal hold, and which access
  dimension (platform, tenant, environment, region, channel) does each
  entitlement govern?
- Which applications does each tenant own, which of them are enabled and in
  which scopes, and which principals can therefore reach each application
  boundary through ingress?
- For each admission decision at ingress, which subject, target, and action
  were evaluated, and what was the outcome? *(originally phrased "capability";
  reworded — that word now names platform offerings)*
- For each entitlement enforced at ingress, which control-plane configuration
  is its authoritative source, and when was that configuration last distributed
  to the enforcement point?
- Which entitlements evaluated at ingress are not drawn from the platform-owned
  entitlement vocabulary? *(invariant — expected empty)*
- Which policy decisions evaluate actions outside the platform-owned action
  vocabulary? *(invariant — expected empty; the Level-3 boundary enforced at
  the decision layer)*
- Which ingress decisions concern capabilities inside an application boundary
  rather than admission across it? *(invariant — expected empty)*

### Management vs. capability control planes

The management control plane owns the governance layer: it is where desired
state is declared and approved. Capability control planes are the designated
writers that actuate that desired state into capability/tenant data planes.
Governance and actuation are separated: the management plane never writes
into a data plane, and every data-plane write traces to a governed intent.

Descriptive:

- Which capability does each capability control plane govern, which data
  planes does it actuate, and which tenants does each data plane serve?
- For each data-plane mutation, which principal executed it and which
  desired-state declaration does it realize?
- Which tenants' data planes are reachable from a given management-plane
  desired-state declaration (blast radius)?

Invariants *(each expected empty)*:

- Which data-plane mutations were executed by a principal that is not the
  acting identity of that data plane's designated writer? *(sole-writer)*
- Which data-plane mutations realize no governed desired-state declaration?
  *(orphan write)*
- Which data planes does the management control plane actuate directly?
  *(tier skipping)*
- Which capability control planes administer a scope containing the
  desired-state declarations that govern their own data planes?
  *(self-governance loop)*

### Reachability (flagship)

- For a given token — or principal-session pair — which resources are
  reachable, and through which chain of grants, enablements, subscriptions,
  offerings, token audience, and effective assurance level? The explanation
  form (return the chain, not just the set) is the access-review deliverable.

### Scoped governance (one logical management plane)

Declarations carry a mandatory scope from a single-parent scope tree;
approval rigor and locality derive from it.

- Which data-plane mutations realize declarations whose scope does not
  contain the mutated data plane? *(locality — expected empty)*
- Which declarations in scopes requiring human approval lack one?
  *(expected empty)*
- Which scopes carry no approval-rigor setting on any ancestor?
- Which mutations realize superseded declarations? *(warning-level)*
- Which declarations' scopes contradict their data planes' environment or
  region facets?

### Tenant membership (which principals may act for a tenant)

Entitlement grants are held by tenants; membership is the separate fact that
a principal may act for one. Without it, nothing connects the principal a
token resolves to with the tenant a route resolves to.

- Which principals may act for each tenant, in what capacity, since when,
  and who approved it?
- Which admission decisions were made for a principal that is not an active
  member of the tenant whose grants were evaluated? *(expected empty — the
  check that connects principal to tenant)*
- Which memberships are active without a human approval behind them?
  *(expected empty)*
- Which principals hold active memberships in more than one tenant?
  *(the consultant and dual-capacity cases — descriptive, not a violation)*
- Which memberships remain active for principals whose credentials have all
  been revoked? *(needs the credential lifecycle work)*

### Subscriptions, bundles, and dependencies

Subscriptions are first-class, capability-targeted, scope-free; reach is
computed by intersection. Bundles expand at subscription time.

- Which subscriptions does each tenant hold, in which lifecycle state, and
  who approved each activation?
- Which active subscriptions lack an active subscription for a hard
  dependency of their capability? *(closure — expected empty)*
- Which capabilities participate in a circular dependency?
  *(acyclicity — expected empty)*
- Which provisioning declarations lack a justifying subscription?
  *(expected empty; teardown declarations reference the terminated one)*
- Which active subscriptions were never activated with human approval?
  *(expected empty)*

### Capability offerings (no cross-scope parity)

Offerings are governed intent: a capability is offered per scope.

- In which scopes is each capability offered, and which tenants can
  therefore reach it there?
- Which offerings sit in scopes where a hard dependency lacks a covering
  offering? *(supply closure — expected empty)*
- Which offerings have no deployed data plane in a covered scope?
  *(launch tracking — warning-level)*
- Which data planes realize a capability in a scope no offering covers?
  *(expected empty)*

### Applications, requirements, and portals

Applications are tenant-owned (the platform is a distinguished tenant);
capability requirements are observed, then human-confirmed.

- Which capabilities has each application been observed using, per window,
  and which of those requirements are confirmed?
- Which applications used capabilities outside their confirmed requirements?
  *(drift up)*
- Which confirmed requirements show no observed usage within the review
  window? *(drift down)*
- Which enabled applications' confirmed requirements exceed their owner's
  active subscriptions or the offerings covering the enablement scope?
  *(enablement gate — expected empty)*
- Which portals of the same tenant on different channels have diverging
  application sets? *(stewardship review)*

### Ingress token contract and channels

The token is evidence; grants are authority, distributed from the control
plane. Channels: web, mobile, api, agent.

- For each admission decision, which token claims supplied the evidence for
  each evaluated dimension?
- For each admission decision, which session and device class supplied the
  channel evidence?
- Which pairwise subject identifiers exist, and per which OAuth audience are
  they scoped? *(pairwise scoping is not yet modelled — named gap)*
- Which entitlement grants lack a derivation link to their governing source?
  *(hand-authored grants — expected empty)*
- Which registrations may be minted which token audiences, and from which
  governance source is each minting rule derived?
- Which tenant onboarding record does each platform- or tenant-dimension
  grant derive from? *(tenant onboarding not yet modelled — named gap)*
- Which tokens carry an audience outside their principal's reachable set at
  issuance time? *(expected empty)*
- Which domain and path binds to which tenant, on which route, and which
  governed declaration established that binding?
- Which domain and path combinations bind to more than one tenant?
  *(collision — expected empty; two tenants on one address is a
  tenant-resolution breach)*
- Which tenant-bound routes have no approved route-binding declaration
  behind them? *(ungoverned binding — expected empty)*
- Which route bindings changed without a human approval in a scope that
  requires one? *(inherited from the declaration machinery)*
- For each session, which handle resolves to it, and to which
  proof-of-possession key is the session sender-constrained?
- Which sessions are not sender-constrained — bound to no confirmation key,
  and therefore replayable from a stolen handle alone? *(expected empty)*
- Which tokens issued within a sender-constrained session are bound to a
  different key than the session, or to no key at all? *(constraint
  laundering — expected empty)*
- Which confirmation keys are shared across sessions belonging to different
  principals? *(key confusion — expected empty)*
- Which handles resolve to more than one session? *(session fixation —
  expected empty)*
- Which sessions outlived the rotation or revocation of their confirmation
  key? *(needs the key lifecycle work; sibling of the credential-revocation
  question)*

### Subject identifiers (RFC 9493 / OIDC sub)

External systems name principals with issuer-scoped subjects; the mapping
"at issuer Y, subject X denotes principal P" is a first-class naming fact,
possibly pairwise per authorized party.

- Which subject identifiers denote each principal, at which issuers, in
  which formats, and scoped to which authorized parties?
- Which (issuer, subject value, party scope) combinations identify more
  than one principal? *(collision — expected empty)*
- Which principals authenticate through issuers where they hold no
  registered subject identifier?
- Which subject-identifier mappings are past their validity window yet
  still resolve? *(issuer subject recycling — the classic CAEP hazard)*
- Which tokens or security events reference subjects with no mapped
  principal? *(needs token subject links and in-graph CAEP events)*

### The two clients

"Client" names two unrelated things and the model keeps them apart: the
OAuth client registration is protocol bookkeeping; the business client is a
party with a relationship to the firm, whose identity is in a session.

- Which OAuth client registrations exist, at which issuer, for which
  audience, and what is each one's client_id?
- Which principals act for which business clients, and since when?
- Which sessions carry a business-client identity, and which carry an
  internal staff or workload identity?
- Which business clients have no principal able to act for them?
  *(a relationship nobody can exercise — stewardship review)*
- Is a business client ever also a tenant, and if so does membership or the
  client relationship govern admission? *(open — the two are modelled
  separately until the answer is settled)*

### Devices and session concurrency

The platform issues one session per user per device; concurrent session
limits are configured per device class.

- Which devices does each principal hold active sessions on, of which
  device class, and since when?
- Which principals hold more than one active session on the same device?
  *(expected empty — one session per user per device)*
- Which principals exceed the configured concurrent-session limit for a
  device class? *(expected empty)*
- Which tenants have no concurrent-session policy configured for a device
  class their principals actually use? *(unbounded concurrency by omission)*
- Should concurrent-session policy be governed desired state, as route
  bindings now are, rather than plain configuration? *(open — it is a
  security control with no approver today)*
- Which sessions have no device at all, and is that legitimate for the
  api and agent channels? *(non-interactive sessions have no device)*

### Authentication journeys

Sessions are established by journey executions; step-up is an elevation
execution on the same session; effective AAL is the latest successful
execution's.

- Which journey definitions serve which channels, and what assurance does
  each achieve?
- Which sessions were established by executions that deviate from their
  definitions? *(expected empty — needs step-level definition modelling)*
- Which journey definitions serve channels whose governing policies require
  an AAL above what the definition achieves?
- Which Permit decisions relied on an elevation older than the policy's
  freshness requirement?
- Which journey definitions changed without a governed journey-definition
  declaration behind them? *(expected empty once definition-change events
  are observable)*

### Agent channel (terms deliberately deferred)

- For each request admitted on the agent channel, which principal's
  authority was it exercising, and under what delegation?
- Which agent-channel grants permit autonomous action versus delegated-only
  action?
