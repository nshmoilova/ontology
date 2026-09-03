# Competency Questions

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
| CQ-7 | Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope? | `cq7-application-entry-rights.rq` | core, ingress, control-plane |
| CQ-8 | Which tenants' data planes are reachable from a given desired-state declaration (blast radius)? | `cq8-blast-radius.rq` | control-plane, core |
| CQ-9 | Which commitments does each offering carry — metric, target, source, validation — and what is the latest observation of each? | `cq9-commitments-and-evidence.rq` | commitment, control-plane |
| CQ-10 | Which tenants hold region-access grants for exactly one region, and in which other regions are their capabilities offered — who is refused, not served out of jurisdiction, during failover? | `cq10-region-bound-tenants.rq` | authz, control-plane |
| CQ-11 | Which capabilities are offered in exactly one region, so no failover target exists? | `cq11-single-region-offerings.rq` | control-plane |

## Backlog and realised invariants

A bullet ending in `[realised: ShapeName]` is answered by its absence of
violations: the shape exists and a negative instance fires it in CI (P10);
the build fails on a name that does not exist (P15). Unmarked bullets are
open.

- Which application boundaries are reachable through a route whose listener does not terminate TLS before the enforcement point? [realised: PlaintextListenerWarningShape]
- Which policies grant access based on attribute assertions that have expired?
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
  entitlement vocabulary? *(invariant — expected empty)* [realised: EntitlementGrantShape]
- Which policy decisions evaluate actions outside the platform-owned action
  vocabulary? *(invariant — expected empty; the Level-3 boundary enforced at
  the decision layer)* [realised: ActionVocabularyShape]
- Which ingress decisions concern operations inside an application boundary
  rather than admission across it? *(invariant — expected empty)* [realised: ActionVocabularyShape]

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

Invariants *(each expected empty)*:

- Which data-plane mutations were executed by a principal that is not the
  acting identity of that data plane's designated writer? *(sole-writer)* [realised: SoleWriterShape]
- Which data-plane mutations realize no governed desired-state declaration?
  *(orphan write)* [realised: DataPlaneMutationShape]
- Which data planes does the management control plane actuate directly?
  *(tier skipping)* [realised: ManagementPlaneNoActuationShape]
- Which capability control planes administer a scope containing the
  desired-state declarations that govern their own data planes?
  *(self-governance loop)* [realised: SelfGovernanceLoopShape]

### Which decision point decided

The platform and each application run their own PDP. Only platform decisions
belong in this graph, and every decision must name the point that made it.

- Which policy decision point rendered each decision, and over what period?
- Which decisions record no deciding policy decision point?
  *(expected empty — an unattributable decision)* [realised: PolicyDecisionShape]
- Which decision points have rendered admission decisions, and are any of
  them not the platform PDP? *(the check that would catch an application
  decision misfiled as a platform one)*

### Reachability (flagship)

- For a given token — or principal-session pair — which application
  boundaries are reachable, and through which chain of grants, enablements, subscriptions,
  offerings, token audience, and effective assurance level? The explanation
  form (return the chain, not just the set) is the access-review deliverable.

### Scoped governance (one logical management plane)

Declarations carry a mandatory scope from a single-parent scope tree;
approval rigor and locality derive from it.

- Which data-plane mutations realize declarations whose scope does not
  contain the mutated data plane? *(locality — expected empty)* [realised: ScopeLocalityShape]
- Which declarations in scopes requiring human approval lack one?
  *(expected empty)* [realised: ScopeRigorShape]
- Which scopes carry no approval-rigor setting on any ancestor?
- Which mutations realize superseded declarations? *(warning-level)* [realised: SupersededRealizationShape]
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
  check that connects principal to tenant)* [realised: AdmissionRequiresMembershipShape]
- Which memberships are active without a human approval behind them?
  *(expected empty)* [realised: MembershipApprovalShape]
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
  dependency of their capability? *(closure — expected empty)* [realised: SubscriptionClosureShape]
- Which capabilities participate in a circular dependency?
  *(acyclicity — expected empty)* [realised: AcyclicDependencyShape]
- Which provisioning declarations lack a justifying subscription?
  *(expected empty; teardown declarations reference the terminated one)* [realised: ProvisioningJustificationShape]
- Which active subscriptions were never activated with human approval?
  *(expected empty)* [realised: SubscriptionActivationApprovalShape]

### Capability offerings (no cross-scope parity)

Offerings are governed intent: a capability is offered per scope.

- In which scopes is each capability offered, and which tenants can
  therefore reach it there?
- Which offerings sit in scopes where a hard dependency lacks a covering
  offering? *(supply closure — expected empty)* [realised: OfferingSupplyClosureShape]
- Which offerings have no deployed data plane in a covered scope?
  *(launch tracking — warning-level)*
- Which data planes realize a capability in a scope no offering covers?
  *(expected empty)* [realised: DataPlaneOfferedShape]

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
  *(enablement gate — expected empty)* [realised: EnablementGateShape, EnablementOfferingCoverageShape]
- Which portals of the same tenant on different channels have diverging
  application sets? *(stewardship review)* [realised: PortalShape]

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
  *(hand-authored grants — expected empty)* [realised: EntitlementGrantShape]
- From which governance source is each registration's audience derived?
  *(a registration serves exactly one audience — OAuthClientRegistrationShape;
  the derivation itself has no term)*
- Which tenant onboarding record does each platform- or tenant-dimension
  grant derive from? *(tenant onboarding not yet modelled — named gap)*
- Which tokens carry an audience outside their principal's reachable set at
  issuance time? *(expected empty)*
- Which domain and path binds to which tenant, on which route, and which
  governed declaration established that binding?
- Which domain and path combinations bind to more than one tenant?
  *(collision — expected empty; two tenants on one address is a
  tenant-resolution breach)* [realised: RouteBindingCollisionShape]
- Which tenant-bound routes have no approved route-binding declaration
  behind them? *(ungoverned binding — expected empty)* [realised: GovernedRouteBindingShape]
- Which route bindings changed without a human approval in a scope that
  requires one? *(inherited from the declaration machinery)* [realised: ScopeRigorShape]
- Which routes serve an application their bound tenant does not own?
  *(cross-tenant endpoint — expected empty)* [realised: RouteApplicationOwnershipShape]
- Which routes serve an application at a scope outside that application's
  enablement scope? *(endpoint reachable where the application is not
  enabled — expected empty)* [realised: RouteEnablementScopeShape]
- For each session, which handle resolves to it, and to which
  proof-of-possession key is the session sender-constrained?
- Which sessions are not sender-constrained — bound to no confirmation key,
  and therefore replayable from a stolen handle alone? *(expected empty)* [realised: SenderConstrainedSessionShape]
- Which tokens issued within a sender-constrained session are bound to a
  different key than the session, or to no key at all? *(constraint
  laundering — expected empty)* [realised: TokenInheritsConfirmationShape]
- Which confirmation keys are shared across sessions belonging to different
  principals? *(key confusion — expected empty)* [realised: KeyConfusionShape]
- Which handles resolve to more than one session? *(session fixation —
  expected empty)* [realised: SessionHandleShape]
- Which sessions outlived the rotation or revocation of their confirmation
  key? *(needs the key lifecycle work; sibling of the credential-revocation
  question)*

### Subject identifiers (RFC 9493 / OIDC sub)

External systems name principals with issuer-scoped subjects; the mapping
"at issuer Y, subject X denotes principal P" is a first-class naming fact,
possibly pairwise per audience (D47).

- Which subject identifiers denote each principal, at which issuers, in
  which formats, and — where pairwise — for which audience?
- Which (issuer, subject value, format) combinations identify more
  than one principal? *(collision — expected empty)* [realised: SubjectIdentifierCollisionShape]
- Which principals authenticate through issuers where they hold no
  registered subject identifier?
- Which subject-identifier mappings are past their validity window yet
  still resolve? *(issuer subject recycling — the classic CAEP hazard)*
- Which tokens or security events reference subjects with no mapped
  principal? *(needs token subject links and in-graph CAEP events)*
- Which principals' subject identifiers are bound to a given issuer, and what
  would re-issuance under another issuer require? *(an identifier is scoped to
  exactly one issuer, so substituting the identity provider is a migration
  with re-issuance, never an active substitution)*

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

- Which devices does each principal hold active sessions on, identified how,
  of which device class, and since when?
- Which principals hold more than one active session on the same device?
  *(expected empty — one session per user per device)* [realised: OneSessionPerDeviceShape]
- Which principals exceed the configured concurrent-session limit for a
  device class? *(expected empty)* [realised: ConcurrentSessionLimitShape]
- Which tenants have no concurrent-session policy configured for a device
  class their principals actually use? *(unbounded concurrency by omission)*
- Should concurrent-session policy be governed desired state, as route
  bindings now are, rather than plain configuration? *(open — cp:ConcurrentSessionPolicy lives in control-plane but is not
  a declaration; a security control with no approver today)*
- Which sessions have no device at all, and is that legitimate for the
  api and agent channels? *(non-interactive sessions have no device)*
- Which journey definition established each session's channel, and does the
  session's device class agree with it? *(disagreement — expected empty)* [realised: ChannelDeviceAgreementShape]
- Which journey executions follow no governed definition? *(expected empty —
  an ungoverned authentication path, and a session whose channel cannot be
  established)* [realised: JourneyExecutionShape]

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
- Which journey definitions changed without a governed journey-definition
  declaration behind them? *(the JourneyDefinitionChange declaration exists — D37; no shape or
  seed instance yet)*

### Agent channel (terms deliberately deferred)

- For each request admitted on the agent channel, which principal's
  authority was it exercising, and under what delegation?
- Which agent-channel grants permit autonomous action versus delegated-only
  action?

### Trust zones (terms deliberately deferred)

Zone here means a network trust zone — internet-facing, DMZ, internal,
restricted — the meaning a zone crossing gives an enforcement point. P16
records that zone is not modelled. These two questions are the trigger for
adding it; until one is needed, the term stays out (P9).

- Which routes cross a trust-zone boundary, and which policy enforcement
  point mediates each crossing?
- Which restricted-zone data planes are reachable from an internet-facing
  route? *(blast radius across zones — an extension of CQ-8)*

When zone enters: it is a placement fact on upstream services and data
planes with an allowed-crossing invariant tied to routes — not a facet on the
scope tree (a zone spans tenants and a scope spans zones) and not a sixth
entitlement dimension (subjects hold no zone grants). Environment and region,
already stated as facets with no rejecting invariant, come first.

### Privilege drift (least privilege as reconciliation)

The model holds no statement of need for principals, so least privilege is
not a default it can enforce; it is a reconciliation the graph can support
(P18, D18). These questions make the over-privilege direction answerable.

- Which entitlement grants, tenant memberships or subscriptions show no
  observed use across a given window? *(standing privilege — descriptive,
  routed to stewardship)*
- Which confirmed capability requirements have no capability-use observation
  in the window, and which observed uses have no confirmed requirement?
  *(requirement drift in both directions — D18)*
- Which grants outlived the governance fact they derive from — a terminated
  subscription, an inactive membership, a superseded enablement?
  *(expected empty — P18's contingency clause)*

### Temporal validation (recorded bounds with no validator)

Every time bound the model records — expiry, validity windows, distribution
time, observation windows, elevation time — is a source nothing checks; only
assurance rank and session count are validated. P15 carries the family as
its known exception. Existing questions stay in their own sections: expired
attribute assertions behind a permit (*Platform vs. application
authorization*), subject-identifier mappings past their validity window
(*Subject identifiers*), sessions outliving a rotated confirmation key
(*Ingress token contract*), grants outliving their governing fact
(*Privilege drift*), and the grant-staleness threshold (open, in the
'Request path boundaries' explainer). The first below was missing; the second moves here from Authentication
journeys, its home under P15's exception.

- Which sessions or tokens are in an active state past their expiry?
  *(expected empty — presence of an expiry is enforced, its passing is not)*
- Which permits relied on an elevation older than the policy's freshness
  requirement? *(assurance decay — D28 deferred it; needs a per-policy
  freshness bound before it is answerable)*

### Non-functional commitments (module `commitment`, scaffolded — D58)

A sibling module, outside the identity set: commitments are governed intent
attached to an offering; observations are windowed evidence. A commitment
with no measurement source or no validation mechanism is a violation — the
'every guarantee is measured' rule as a shape, not a principle.

- Which committed commitments have no observation inside their current
  window? *(a promise nobody is watching — expected empty)*
- Which observations fall outside their commitment's target, by comparator?
  *(needs a comparator-aware query; the data is there)*
- Which tenants are subscribed in a scope whose offering carries a weaker
  commitment than the tenant's contract requires? *(needs the contract
  side — see the published-contracts scoping decision)*
- Who is accountable for each commitment, and was its change approved?
  *(commitments are declarations — D59; CQ-9 lists scope and approver, and
  a commitment declared where rigor requires approval must carry one)* [realised: ScopeRigorShape, CommitmentScopeShape]

## The four platform questions

Four questions asked of the platform, each broken into competency questions
and judged by four tests: asked of the graph rather than a dashboard; in scope
for this ontology or the commitment module; not already asked; decidable.
Verdicts: **now** — answerable with existing terms and data; **sibling** — the
commitment module, needing seeds or one metric; **terms** — valid, needs a
modelling decision first; **invalid** — recorded so it is not re-asked.

Two term decisions recur across the themes and are the next modelling steps:
the platform's own request-path components (ingress, decision point, session
manager, authentication) as platform-owned offerings, so they can carry
commitments; and plane placement with an operational role (active, standby,
draining) for data planes and control planes alike.

### Availability

- Will users lose requests when failure occurs? → which offerings carry a
  commitment on request loss during failover? *(sibling; new metric by
  decision — successful-request ratio during failover. On control-plane
  failure ingress refuses by design, P15: refused, not dropped)*
- Can recovery happen automatically without human intervention? → which
  data-plane mutations were executed by a workload under a standing,
  approved declaration, and which needed a fresh approval? *(now — recovery
  is actuation, not a grant of authority; P3 requires the declaration's
  approval, not one per event)*
- How long will users be impacted if an entire region fails? → which
  offerings carry a recovery-time commitment per region *(sibling)*; which
  capabilities are offered in only one region *(now — CQ-11)*
- How quickly can we switch providers when a vendor fails? *(invalid here —
  no vendor concept, P8; the only in-scope seam is the identity provider,
  see Subject identifiers)*
- How fast can we recover and how much data could we lose? → which
  offerings carry recovery-time and recovery-point commitments per scope
  *(sibling; both metrics exist)*
- Can we deploy and evolve the platform without disrupting users? → which
  declarations took effect in production scopes, under whose approval, and
  which were followed by a commitment breach in the next window? *(sibling
  + control-plane — the first cross-module question; needs the breach query
  and a change-failure metric)*

### Multi-region resiliency

- Can we survive losing a region? → single-region capabilities *(now —
  CQ-11)*; hard dependencies offered in fewer regions than their dependents
  *(now; partly enforced by OfferingSupplyClosureShape)*; recovery-time
  commitments per region *(sibling)*
- Are we truly running across regions or keeping standby infrastructure? →
  data planes per region, in what operational role? *(terms — data planes
  have no operational state; one closed scheme, P7)*
- How much state or data is at risk if a region fails right now? → which
  tenants' data planes exist in a single region *(now)*; recovery-point
  commitments per region *(sibling)*
- Can we safely take a region out of service for maintenance? → which
  tenants and applications would lose their only data plane or route if the
  region's scope were drained, under which declaration and approval? *(now
  — CQ-8 by region facet; draining as a state needs the same term as above)*
- After losing a region, how quickly do we regain operational safety
  margin? → commitment on time to restore redundancy *(sibling; new metric
  by decision. Capacity headroom itself is not a graph fact)*
- Will regulated traffic remain compliant during failover? → which tenants
  hold region-access grants for one region only, so failover elsewhere
  refuses them rather than serving them out of jurisdiction? *(now — CQ-10)*
- Can the platform still be managed when a region is lost? → which data
  planes become unmanageable if a control plane is lost *(now — sole-writer
  edges)*; where does each control plane run *(terms — control planes are
  logical, D01/D02, with no placement; same decision as operational role)*.
  Behaviour during the loss is implied: intent persists so state persists
  (P18); management stalls, serving continues, declarations queue.

### Ingress and traffic management

- Can we safely roll out changes using canaries, blue-green and weighted
  routing? → which routes forward to more than one upstream, with what
  split, changed under which declaration and approval; which tenants sit
  behind a canary now? *(terms — a weighted forwarding edge and a
  traffic-split change as a declaration subclass; governance then comes
  free via D43. "Who is behind it" is answerable now. Rollback-on-failure is
  the change-failure commitment, sibling)*
- What happens when demand exceeds capacity? → which tenants share a data
  plane *(now — the noisy-neighbour blast radius via the isolation model)*;
  throughput commitments per offering *(sibling; new metric)*; is there any
  path under load where a request reaches an application without admission
  *(P12/P15 asserted — the model states no bypass and cannot observe it)*.
  Capacity is not a graph fact. Load-shedding order would need a priority
  term that only this question asks for — deferred.

### Performance

- How much delay does the platform itself add to every request? → which
  request-path offerings carry a latency commitment at which percentile
  *(sibling, after the request-path-as-offerings decision)*; which checks
  sit on the path for a given route *(now)*
- How much latency should consumers reserve for the platform? → the same
  commitment read from the consumer's side: the target is the budget
  *(sibling — the one contract-shaped question that needs no catalogue)*
- How long does a user take to sign in? → per journey definition and
  channel, execution duration from first to last event *(now — executions
  and events are in-graph under P17, with timestamps)*; a duration
  commitment *(sibling)*
- How long does additional authentication take when required? → the same
  over elevation executions *(now — D28)*; and which permits required an
  elevation at all *(now)*
- How quickly can the platform decide whether a request is allowed? →
  decision-latency commitment on the decision point *(sibling only —
  requests are not reified, D31, so duration is not derivable; the design
  answer is structural: authority is projected to ingress, P4)*
- What is the 99th-percentile latency now? / Is the platform up right now?
  *(invalid — dashboard questions)*

