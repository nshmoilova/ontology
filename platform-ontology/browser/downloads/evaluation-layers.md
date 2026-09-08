# Request path boundaries

*Platform entitlements at ingress, application authorization inside the boundary*

**Audience.** Platform and application security architects

Coarse-grained platform authorization protects the right to enter an application and deployment boundary; resource authorization protects the right to perform an operation on an application resource. This walkthrough covers where that line sits, what sits on each side, and how the model stops the line from moving quietly.

## 1. The three layers

![The three layers](https://nshmoilova.github.io/ontology/downloads/diagrams/layers.svg)

Coarse-grained platform authorization protects the right to enter an application and deployment boundary. Resource authorization protects the right to perform an operation on an application resource. Everything below follows from holding those two apart.

The symmetry is exact and worth reading twice: both are authorization, both have a subject, both end in a decision. What differs is the object being protected — a boundary in one case, a resource in the other — and that difference is what makes one platform-owned and the other application-owned. A boundary is the platform's to define because the platform put it there; a resource belongs to whoever built the application behind it.

One enforcement stack serves many independently developed applications, and that only works if the vocabulary ingress evaluates stays small and stable, and if nothing application-specific can enter it. The control plane defines entitlements; ingress enforces them; applications own everything past the boundary.

**Principles:** [P1 — The boundary, not the resource](https://nshmoilova.github.io/ontology/#/principles#P1)  
**Decisions:** [D21 — Five entitlement dimensions in a closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D21), [D25 — The flagship reachability question](https://nshmoilova.github.io/ontology/#/decisions#D25), [D48 — A route serving an application is the application access endpoint](https://nshmoilova.github.io/ontology/#/decisions#D48)  
**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)  
**Terms:** [`authz:Action`](https://nshmoilova.github.io/ontology/#/term/authz%3AAction), [`authz:IngressAdmissionDecision`](https://nshmoilova.github.io/ontology/#/term/authz%3AIngressAdmissionDecision), [`core:Application`](https://nshmoilova.github.io/ontology/#/term/core%3AApplication)

## 2. A request, resolved

Take a concrete request:

POST https://api.company.com/digital-bank/transactions/12345

Before any entitlement is evaluated, ingress resolves it to a platform endpoint. The route registry matches the domain and path, and everything the platform needs falls out of governed configuration — none of it asserted by the caller.

What ingress then knows is that a request is attempting to enter the digital bank's transactions boundary, in prod, in us-west-2. What it does not know, and never needs to, is that /12345 identifies an order. That is the line: the endpoint is registered platform configuration, the object behind it is application data.

With that resolved, the authorization request is the XACML tuple — subject Alice, action ACCESS, resource the application access endpoint — with the tenant, environment, region, channel, session and assurance as context. The decision point answers one question: may Alice, acting for this tenant, cross this boundary. Permit or Deny.

| Resolved | From | Ontology term |
| --- | --- | --- |
| Application | the route's servesApplication binding | core:Application |
| Endpoint | the matched domain and path | ingress:Route — "application access endpoint" |
| Tenant | the route's boundToTenant binding | core:Tenant |
| Environment, Region | which ingress deployment received it | scope facets: inEnvironment, inRegion |
| Channel | the session's device class | core:DeliveryChannel — web, mobile, api, agent |
| Session, Assurance | the session and its journey execution | session:Session, authn:AssuranceLevel |
| Subject | the token's sub, via a subject identifier | core:Principal |
| Action | the admission action, always | authz:action-access |
| Outcome | the decision | Permit / Deny (XACML) |

**Decisions:** [D24 — The ingress token contract](https://nshmoilova.github.io/ontology/#/decisions#D24), [D43 — Route-to-tenant binding is governed desired state](https://nshmoilova.github.io/ontology/#/decisions#D43), [D44 — Sessions are sender-constrained, DPoP-style](https://nshmoilova.github.io/ontology/#/decisions#D44), [D46 — Sessions are per user per device; channel comes from device class](https://nshmoilova.github.io/ontology/#/decisions#D46), [D51 — The journey definition establishes the channel, for every channel](https://nshmoilova.github.io/ontology/#/decisions#D51)  
**Questions:** [CQ-2 — For every route, which upstream does it reach and which policy enforcement point mediates it?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-2), [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)  
**Terms:** [`ingress:Route`](https://nshmoilova.github.io/ontology/#/term/ingress%3ARoute), [`ingress:servesApplication`](https://nshmoilova.github.io/ontology/#/term/ingress%3AservesApplication), [`core:Application`](https://nshmoilova.github.io/ontology/#/term/core%3AApplication), [`authz:IngressAdmissionDecision`](https://nshmoilova.github.io/ontology/#/term/authz%3AIngressAdmissionDecision), [`authz:decidedBy`](https://nshmoilova.github.io/ontology/#/term/authz%3AdecidedBy)

**Enforced by:**

- `RouteApplicationOwnershipShape` on `ingress:Route`
  - Violation: Route serves an application its bound tenant does not own — a cross-tenant endpoint.
- `RouteEnablementScopeShape` on `ingress:Route`
  - Violation: Route serves an application at a scope outside that application's enablement — reachable where it is not enabled.

## 3. One request, three checkpoints

![One request, three checkpoints](https://nshmoilova.github.io/ontology/downloads/diagrams/request-flow.svg)

The three layers become three checkpoints on a single request, and the first distinction to make is between the first two — because it is the one people collapse.

Ingress is the enforcement point. It resolves and it enforces, but it does not decide: the domain and path give it the tenant, the application and the endpoint; the token gives it the principal; the cookie handle with its proof gives it the session; the journey definition gives it the channel and the assurance. None of that is a decision. It is the context a decision needs.

The platform PDP decides one thing — may this request cross into the application boundary — and answers Permit or Deny. Every check it makes is answerable with the application as an opaque identifier: membership, the five dimensions, enablement in scope, coverage, assurance. Nothing about what the application does.

Past the boundary, the application PDP decides what the subject may do, and the ontology does not model it. That is a decision rather than an omission, and it is enforced: an application verb cannot enter the platform action scheme, and an entitlement outside the platform dimensions cannot be evaluated at ingress. The request path ends at /12345, which is an order — the platform never learns that, and must not.

| Checkpoint | Asks | Answers with |
| --- | --- | --- |
| Platform ingress (PEP) | What is this request? | Route bindings, subject identifier, session handle, journey definition — resolution only |
| Platform PDP | May it cross the boundary? | Membership, the five dimensions, enablement scope, subscription and offering coverage, assurance |
| Application PDP | What may the subject do? | Roles, business rules, record-level access, limits — application-owned, out of scope |

**Decisions:** [D32 — Admission decisions evaluate the platform admission policy](https://nshmoilova.github.io/ontology/#/decisions#D32), [D49 — Decisions name the point that made them; XACML is the settled vocabulary](https://nshmoilova.github.io/ontology/#/decisions#D49), [D52 — Decision point and enforcement point are disjoint](https://nshmoilova.github.io/ontology/#/decisions#D52), [D55 — Executor and requesting principal are mandatory](https://nshmoilova.github.io/ontology/#/decisions#D55)  
**Questions:** [CQ-2 — For every route, which upstream does it reach and which policy enforcement point mediates it?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-2), [CQ-5 — For each Permit decision, what is the full assurance chain (decision → session → authentication → method/AAL)?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-5), [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)  
**Terms:** [`core:PolicyEnforcementPoint`](https://nshmoilova.github.io/ontology/#/term/core%3APolicyEnforcementPoint), [`core:PolicyDecisionPoint`](https://nshmoilova.github.io/ontology/#/term/core%3APolicyDecisionPoint), [`authz:IngressAdmissionDecision`](https://nshmoilova.github.io/ontology/#/term/authz%3AIngressAdmissionDecision), [`authz:decidedBy`](https://nshmoilova.github.io/ontology/#/term/authz%3AdecidedBy), [`core:Application`](https://nshmoilova.github.io/ontology/#/term/core%3AApplication)

**Enforced by:**

- `AdmissionRequiresMembershipShape` on `authz:IngressAdmissionDecision`
  - Violation: Admission decision evaluated a tenant's grants for a principal holding no active membership in that tenant.
- `PermitMeetsRequiredAssuranceShape` on `authz:PolicyDecision`
  - Violation: Permit decision violates policy assurance requirement: the session's authentication AAL is below the policy's required AAL.
- `ActionVocabularyShape` on `authz:PolicyDecision`
  - Violation: Decision evaluates an action outside the platform-owned action vocabulary — application verbs are Level-3 and must not reach platform decisions.

## 4. The check that joins the two halves

Before any dimension is evaluated, one thing must hold that is easy to overlook: the principal must be entitled to act for the tenant at all.

The two halves of a request are resolved independently — the route resolves the tenant, the token resolves the principal — and every entitlement grant is held by the tenant, not the principal. So without a membership record, a valid token for anyone would satisfy every tenant-level check at any tenant's address. Membership is the join, and it is deliberately a governed record with a lifecycle and an approver rather than a bare link, because the access-review question is not whether the link exists but when it was granted and by whom.

One principal may hold memberships in several tenants. Consultants, dual-capacity staff and the employee who is also a customer are ordinary cases, not exceptions to design around.

**Decisions:** [D19 — The enablement gate](https://nshmoilova.github.io/ontology/#/decisions#D19), [D45 — Tenant membership connects the principal to the tenant](https://nshmoilova.github.io/ontology/#/decisions#D45), [D48 — A route serving an application is the application access endpoint](https://nshmoilova.github.io/ontology/#/decisions#D48)  
**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)  
**Terms:** [`cp:TenantMembership`](https://nshmoilova.github.io/ontology/#/term/cp%3ATenantMembership), [`cp:memberPrincipal`](https://nshmoilova.github.io/ontology/#/term/cp%3AmemberPrincipal), [`cp:memberOfTenant`](https://nshmoilova.github.io/ontology/#/term/cp%3AmemberOfTenant), [`cp:memberCapacity`](https://nshmoilova.github.io/ontology/#/term/cp%3AmemberCapacity)

**Enforced by:**

- `AdmissionRequiresMembershipShape` on `authz:IngressAdmissionDecision`
  - Violation: Admission decision evaluated a tenant's grants for a principal holding no active membership in that tenant.
- `MembershipApprovalShape` on `cp:TenantMembership`
  - Violation: Active tenant membership lacks approval by a human principal — admitting a principal to act for a tenant is a meta-authorization boundary.

## 5. Level 1 — platform entitlements

Five dimensions, and only five. They are members of a closed SKOS scheme, so the set cannot grow by accident: adding a sixth is a deliberate, versioned change to a module that already requires security-architecture review.

Each answers a question ingress can settle without asking the application anything, and each is determinable from evidence the platform controls rather than from anything the caller asserts.

Note how little of this comes from the token. Tenant is resolved from the route's domain and path binding; environment and region from which ingress deployment received the request; channel from the session's device class. The token contributes identity and assurance — not one of the five dimensions is a claim.

| Dimension | Governs | Resolved from |
| --- | --- | --- |
| platform.access | May this tenant use the platform at all? | Tenant registration |
| tenant.access | Is this subject acting for a tenant that exists and is active? | The route's domain/path binding — not a token claim |
| environment.access | May this tenant operate in prod / uat / dev? | Which ingress deployment received the request |
| region.access | May this tenant operate in this region? | Where the request landed |
| channel.access | May this tenant be served over web / mobile / api / agent? | The session's device class — the session manager knows what it authenticated |

**Decisions:** [D21 — Five entitlement dimensions in a closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D21), [D22 — Grants are projections, never hand-authored](https://nshmoilova.github.io/ontology/#/decisions#D22), [D24 — The ingress token contract](https://nshmoilova.github.io/ontology/#/decisions#D24), [D36 — Grant derivation corrected; tenant onboarding named as a gap](https://nshmoilova.github.io/ontology/#/decisions#D36)  
**Questions:** [CQ-4 — Which attribute assertions back decisions about a principal, and which authoritative source issued each?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-4), [CQ-10 — Which tenants hold region-access grants for exactly one region, and in which other regions are their capabilities offered — who is refused, not served out of jurisdiction, during failover?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-10)  
**Terms:** [`authz:EntitlementDimension`](https://nshmoilova.github.io/ontology/#/term/authz%3AEntitlementDimension), [`authz:EntitlementGrant`](https://nshmoilova.github.io/ontology/#/term/authz%3AEntitlementGrant), [`core:DeliveryChannel`](https://nshmoilova.github.io/ontology/#/term/core%3ADeliveryChannel)

## 6. Level 2 — application admission

Still enforced by ingress, but defined by the control plane rather than hard-coded. Ingress does not know what any application does; it enforces a generic model — subject, action, target, decision — against governed configuration.

An application is reachable when four things hold together: the tenant owns it, a current approved enablement covers the scope, the owner holds active subscriptions for the application's confirmed capability requirements, and offerings cover that scope. The last one matters because no parity is assumed across regions and environments — a capability exists where an offering says it does.

Underneath all of it sits the route binding: the domain and path that resolved the tenant in the first place. That binding is itself a governed declaration, so the chain from address to admitted request is approvable end to end.

**Decisions:** [D17 — Applications are owned, distinct from capabilities](https://nshmoilova.github.io/ontology/#/decisions#D17), [D18 — Requirements: observed, then human-confirmed](https://nshmoilova.github.io/ontology/#/decisions#D18), [D19 — The enablement gate](https://nshmoilova.github.io/ontology/#/decisions#D19), [D35 — The enablement gate had forgotten offerings](https://nshmoilova.github.io/ontology/#/decisions#D35), [D65 — An offering is a declaration with a lifecycle state; only an available offering covers enablement](https://nshmoilova.github.io/ontology/#/decisions#D65)  
**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7), [CQ-14 — Which offerings are in which state in each scope, and does each available one carry a published contract and a committed commitment?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-14)  
**Terms:** [`core:Application`](https://nshmoilova.github.io/ontology/#/term/core%3AApplication), [`cp:ApplicationEnablement`](https://nshmoilova.github.io/ontology/#/term/cp%3AApplicationEnablement), [`cp:Subscription`](https://nshmoilova.github.io/ontology/#/term/cp%3ASubscription), [`cp:CapabilityOffering`](https://nshmoilova.github.io/ontology/#/term/cp%3ACapabilityOffering), [`cp:CapabilityRequirement`](https://nshmoilova.github.io/ontology/#/term/cp%3ACapabilityRequirement), [`ingress:boundToTenant`](https://nshmoilova.github.io/ontology/#/term/ingress%3AboundToTenant), [`cp:RouteBindingChange`](https://nshmoilova.github.io/ontology/#/term/cp%3ARouteBindingChange)

**Enforced by:**

- `EnablementGateShape` on `cp:ApplicationEnablement`
  - Violation: Application enablement exceeds its owner's active subscriptions: a confirmed capability requirement has no active subscription covering it.
- `EnablementOfferingCoverageShape` on `cp:ApplicationEnablement`
  - Violation: Application enablement's scope is not covered by any available offering of a confirmed required capability — enabled where the capability is not available.
- `GovernedRouteBindingShape` on `ingress:Route`
  - Violation: Route binds a tenant with no route-binding declaration behind it — tenant resolution must be governed, not configured out of band.

## 7. Level 3 — inside the application

Roles, scopes, record-level rules, transactional limits, four-eyes checks on a payment — none of it is modelled here, and that is a decision rather than an omission.

The moment ingress starts interpreting an application's verbs, the small-vocabulary property is gone and every application team acquires a lever on the shared enforcement stack. So the ontology refuses the question: `core:Application` says explicitly that what a subject may do inside is application-owned and out of scope.

**Decisions:** [D31 — Actions on decisions — the AuthZEN tuple completed](https://nshmoilova.github.io/ontology/#/decisions#D31), [D60 — The platform depends on no application — the dependency edges are typed](https://nshmoilova.github.io/ontology/#/decisions#D60)  
**Terms:** [`core:Application`](https://nshmoilova.github.io/ontology/#/term/core%3AApplication)

## 8. How the boundary is enforced, not just described

Two closure invariants keep the line where it is. Both are expected to return nothing, and both have a deliberately broken instance in the negative test corpus — an invariant that cannot demonstrably fire does not count.

The first stops a foreign entitlement dimension being evaluated at ingress. The second stops an application verb reaching a platform decision: an action like "approve payment" typed into the platform action class is caught even though it is structurally valid RDF.

**Principles:** [P1 — The boundary, not the resource](https://nshmoilova.github.io/ontology/#/principles#P1), [P7 — Vocabularies are closed schemes of individuals](https://nshmoilova.github.io/ontology/#/principles#P7)  
**Decisions:** [D21 — Five entitlement dimensions in a closed scheme](https://nshmoilova.github.io/ontology/#/decisions#D21), [D31 — Actions on decisions — the AuthZEN tuple completed](https://nshmoilova.github.io/ontology/#/decisions#D31), [D48 — A route serving an application is the application access endpoint](https://nshmoilova.github.io/ontology/#/decisions#D48)  
**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7)

**Enforced by:**

- `ActionVocabularyShape` on `authz:PolicyDecision`
  - Violation: Decision evaluates an action outside the platform-owned action vocabulary — application verbs are Level-3 and must not reach platform decisions.
- `PolicyDecisionShape` on `authz:PolicyDecision`
  - Violation: A policy decision must have exactly one outcome.
  - Violation: A policy decision must reference the policy it evaluated.
  - Violation: A policy decision must evaluate exactly one action — the AuthZEN tuple is incomplete without it.
  - Violation: A policy decision must name exactly one policy decision point — a decision nobody can be shown to have made is unattributable.
  - Violation: A policy decision must name the requesting principal — a decision with no subject cannot be traced to anyone (P17).
- `IngressAdmissionDecisionShape` on `authz:IngressAdmissionDecision`
  - Violation: An admission decision must arrive via exactly one channel, derived from the presenting registration.
  - Violation: An admission decision must evaluate at least one entitlement grant — admission without grants is admission without authority.

## 9. The test to apply to a candidate entitlement

When someone proposes a new coarse-grained entitlement, four questions decide whether it belongs at Level 1:

1. Can ingress determine it without trusting the application or the caller? Region, environment and channel pass; "is this user a supervisor" does not.
2. Is it about crossing a boundary, or about what happens past it? Crossing is Level 1 or 2; anything else is Level 3.
3. Is it stable? The vocabulary's value is that it changes rarely — a dimension that needs new members per product is an application concern.
4. Is it platform-owned? If an application team would maintain its values, it does not belong in the platform scheme.

A proposal that fails any of these is usually an attribute assertion feeding application policy, not a platform dimension.

**Principles:** [P1 — The boundary, not the resource](https://nshmoilova.github.io/ontology/#/principles#P1), [P9 — Questions before terms](https://nshmoilova.github.io/ontology/#/principles#P9)  
**Decisions:** [D25 — The flagship reachability question](https://nshmoilova.github.io/ontology/#/decisions#D25)  
**Questions:** [CQ-7 — Does this subject's tenant have the right to enter this application through this platform-controlled endpoint and deployment scope?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-7), [CQ-8 — Which tenants' data planes are reachable from a given desired-state declaration (blast radius)?](https://nshmoilova.github.io/ontology/#/questions?q=CQ-8)

## Open questions

1. Do environment and region belong as entitlement dimensions at all, given they are resolved from where the request landed rather than from tenant configuration — or are they properly deployment facts that policy reads, with the grant a redundant assertion? The same question now applies to tenant.access, since tenancy comes from the request URL rather than from anything the tenant presents.
2. If tenant context comes from host and path, is tenant.access enforcing anything the routing has not already decided? Put sharply: does a request that reaches a tenant's hostname ever fail tenant.access, and if not, is the dimension real or ceremonial — now that membership carries the principal-to-tenant check that actually bites?
3. Is tenant membership a sixth entitlement dimension, or identity data that sits beside the dimensions? It is currently modelled as governed control-plane state rather than a grant, on the grounds that a grant says what a tenant may do while membership says who may act as it — but the boundary is worth testing.
4. Application admission currently answers reachability of the application boundary. Do we also need a coarse 'capability class' notion at Level 2 — for example admitting a tenant to a read-only view of an application — or does that immediately become Level 3?
5. The agent channel is a dimension today, but delegation is deliberately unmodelled. For an agent acting on a human's behalf, is channel.access on the tenant sufficient, or does admission need the delegation chain before we can allow it in production?
6. Which side of the line does step-up assurance sit on? The AAL guard runs at the platform layer today, but the trigger for step-up is nearly always an application-level action.

---

Generated from `docs/explainers.json` by `ci/build_index.py`. Web version: https://nshmoilova.github.io/ontology/#/explain/evaluation-layers
